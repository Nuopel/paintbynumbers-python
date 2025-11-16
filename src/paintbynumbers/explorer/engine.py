"""Main exploration engine for parameter testing."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
import traceback

from ..core.pipeline import PaintByNumbersPipeline
from ..core.settings import Settings
from .config import ExplorerConfig
from .variations import VariationGenerator
from .metrics import MetricsCollector, VariationMetrics


@dataclass
class VariationResult:
    """Result of processing a single variation."""

    variation_id: str
    variation_index: int
    parameters: Dict[str, Any]
    metrics: VariationMetrics
    output_paths: Dict[str, Path]  # svg, png, etc.
    error: Optional[str] = None
    success: bool = True


class ExplorationEngine:
    """Engine for running parameter exploration."""

    def __init__(
        self,
        config: ExplorerConfig,
        input_image: Path,
        output_dir: Optional[Path] = None,
        progress_callback: Optional[callable] = None,
    ):
        """Initialize exploration engine.

        Args:
            config: Explorer configuration
            input_image: Path to input image
            output_dir: Output directory (default: results/{image_name}/{timestamp})
            progress_callback: Optional callback(current, total, message)
        """
        self.config = config
        self.input_image = Path(input_image)
        self.progress_callback = progress_callback

        # Setup output directory
        if output_dir:
            self.output_dir = Path(output_dir)
        elif config.output_dir:
            self.output_dir = config.output_dir
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            self.output_dir = (
                Path("results") / self.input_image.stem / timestamp
            )

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Variation generator
        self.variation_generator = VariationGenerator(config)
        self.variations = self.variation_generator.generate_variations()

        # Check for warnings
        total = len(self.variations)
        if total > config.warn_threshold:
            print(
                f"Warning: Generating {total} variations! "
                f"Consider using star exploration or reducing parameter ranges."
            )

    def run(self) -> List[VariationResult]:
        """Run exploration and return all results.

        Returns:
            List of VariationResult objects
        """
        start_time = time.time()

        # Save exploration configuration
        self._save_exploration_config()

        # Generate all variations
        print(f"Generating {len(self.variations)} variations...")
        print(f"Strategy: {self.config.strategy.value}")
        print(f"Output directory: {self.output_dir}")

        # Process variations (parallel or sequential)
        if self.config.parallel_processing and len(self.variations) > 1:
            results = self._process_parallel()
        else:
            results = self._process_sequential()

        # Calculate total time
        total_time = time.time() - start_time

        # Print summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        print(f"\nExploration complete!")
        print(f"Total time: {total_time:.1f}s")
        print(f"Successful: {successful}/{len(results)}")
        if failed > 0:
            print(f"Failed: {failed}")

        # Save results summary
        self._save_results_summary(results, total_time)

        return results

    def _process_sequential(self) -> List[VariationResult]:
        """Process variations sequentially."""
        results = []

        for i, variation in enumerate(self.variations, 1):
            if self.progress_callback:
                self.progress_callback(i, len(self.variations), f"Processing variation {i}")

            print(f"\n[{i}/{len(self.variations)}] Processing variation...")
            result = self._process_single_variation(variation, i)
            results.append(result)

            if result.success:
                print(f"  ✓ Success ({result.metrics.processing_time:.2f}s)")
            else:
                print(f"  ✗ Failed: {result.error}")

        return results

    def _process_parallel(self) -> List[VariationResult]:
        """Process variations in parallel."""
        max_workers = self.config.max_workers or cpu_count()
        print(f"Using {max_workers} parallel workers...")

        results = []
        completed = 0

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_idx = {
                executor.submit(
                    _process_variation_worker,
                    variation,
                    i,
                    self.input_image,
                    self.output_dir,
                    self.variation_generator,
                    self.config.save_intermediate,
                ): i
                for i, variation in enumerate(self.variations, 1)
            }

            # Collect results as they complete
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                completed += 1

                try:
                    result = future.result()
                    results.append(result)

                    if self.progress_callback:
                        self.progress_callback(
                            completed,
                            len(self.variations),
                            f"Completed variation {idx}",
                        )

                    status = "✓" if result.success else "✗"
                    print(f"[{completed}/{len(self.variations)}] {status} Variation {idx}")

                except Exception as e:
                    print(f"[{completed}/{len(self.variations)}] ✗ Variation {idx} - Exception: {e}")
                    # Create error result
                    error_result = VariationResult(
                        variation_id=f"var_{idx:03d}",
                        variation_index=idx,
                        parameters=self.variations[idx - 1],
                        metrics=None,
                        output_paths={},
                        error=str(e),
                        success=False,
                    )
                    results.append(error_result)

        # Sort results by index to maintain order
        results.sort(key=lambda r: r.variation_index)

        return results

    def _process_single_variation(
        self, variation: Dict[str, Any], index: int
    ) -> VariationResult:
        """Process a single variation.

        Args:
            variation: Parameter dictionary
            index: Variation index (1-based)

        Returns:
            VariationResult
        """
        variation_id = self.variation_generator.get_variation_label(variation, index)

        try:
            # Create variation directory
            if self.config.save_intermediate:
                var_dir = self.output_dir / "variations" / variation_id
                var_dir.mkdir(parents=True, exist_ok=True)
            else:
                var_dir = None

            # Create settings from variation parameters
            settings = Settings(**variation)

            # Add output profile for SVG (minimal for speed)
            from ..core.settings import OutputProfile
            settings.outputProfiles = [
                OutputProfile(
                    name="explorer_output",
                    filetype="svg",
                    svgShowLabels=True,
                    svgShowBorders=True,
                    svgFillFacets=True,
                )
            ]

            # Process with pipeline
            start_time = time.time()
            result = PaintByNumbersPipeline.process(
                str(self.input_image),
                settings,
                progress_callback=None
            )
            processing_time = time.time() - start_time

            # Collect metrics
            img_width = result.width
            img_height = result.height

            metrics = MetricsCollector.collect_metrics(
                result.facet_result,
                result.colors_by_index,
                processing_time,
                img_width,
                img_height,
            )

            # Save outputs if requested
            output_paths = {}
            if var_dir:
                # Save SVG
                svg_path = var_dir / "output.svg"
                with open(svg_path, 'w') as f:
                    f.write(result.svg_content)
                output_paths['svg'] = svg_path

                # Save PNG preview (small)
                png_path = var_dir / "preview.png"
                self._save_png_preview(result.svg_content, png_path)
                output_paths['png'] = png_path

                # Save metadata
                metadata_path = var_dir / "metadata.json"
                self._save_metadata(
                    metadata_path, variation, metrics, variation_id
                )
                output_paths['metadata'] = metadata_path

            return VariationResult(
                variation_id=variation_id,
                variation_index=index,
                parameters=variation,
                metrics=metrics,
                output_paths=output_paths,
                success=True,
            )

        except Exception as e:
            return VariationResult(
                variation_id=variation_id,
                variation_index=index,
                parameters=variation,
                metrics=None,
                output_paths={},
                error=f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}",
                success=False,
            )

    def _save_exploration_config(self) -> None:
        """Save exploration configuration to output directory."""
        config_path = self.output_dir / "exploration_config.json"
        self.config.to_json(config_path)

    def _save_results_summary(
        self, results: List[VariationResult], total_time: float
    ) -> None:
        """Save summary of all results."""
        summary = {
            "input_image": str(self.input_image),
            "strategy": self.config.strategy.value,
            "total_variations": len(results),
            "successful": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "total_time": total_time,
            "timestamp": datetime.now().isoformat(),
            "variations": [
                {
                    "id": r.variation_id,
                    "index": r.variation_index,
                    "success": r.success,
                    "error": r.error,
                    "parameters": r.parameters,
                    "metrics": r.metrics.to_dict() if r.metrics else None,
                }
                for r in results
            ],
        }

        summary_path = self.output_dir / "results_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

    def _save_metadata(
        self,
        path: Path,
        parameters: Dict[str, Any],
        metrics: VariationMetrics,
        variation_id: str,
    ) -> None:
        """Save variation metadata."""
        metadata = {
            "variation_id": variation_id,
            "parameters": parameters,
            "metrics": metrics.to_dict(),
        }

        with open(path, 'w') as f:
            json.dump(metadata, f, indent=2)

    def _save_png_preview(self, svg_content: str, output_path: Path) -> None:
        """Save PNG preview from SVG."""
        try:
            import cairosvg
            cairosvg.svg2png(
                bytestring=svg_content.encode('utf-8'),
                write_to=str(output_path),
                output_width=400,  # Small preview
            )
        except ImportError:
            # cairosvg not available, skip PNG generation
            pass
        except Exception:
            # Ignore errors in preview generation
            pass


# Worker function for parallel processing (must be at module level)
def _process_variation_worker(
    variation: Dict[str, Any],
    index: int,
    input_image: Path,
    output_dir: Path,
    variation_generator: VariationGenerator,
    save_intermediate: bool,
) -> VariationResult:
    """Worker function for parallel processing."""
    variation_id = variation_generator.get_variation_label(variation, index)

    try:
        # Create variation directory
        if save_intermediate:
            var_dir = output_dir / "variations" / variation_id
            var_dir.mkdir(parents=True, exist_ok=True)
        else:
            var_dir = None

        # Create settings from variation parameters
        settings = Settings(**variation)

        # Add output profile for SVG
        from ..core.settings import OutputProfile
        settings.outputProfiles = [
            OutputProfile(
                name="explorer_output",
                filetype="svg",
                svgShowLabels=True,
                svgShowBorders=True,
                svgFillFacets=True,
            )
        ]

        # Process with pipeline
        start_time = time.time()
        result = PaintByNumbersPipeline.process(
            str(input_image),
            settings,
            progress_callback=None
        )
        processing_time = time.time() - start_time

        # Collect metrics
        img_width = result.width
        img_height = result.height

        metrics = MetricsCollector.collect_metrics(
            result.facet_result,
            result.colors_by_index,
            processing_time,
            img_width,
            img_height,
        )

        # Save outputs if requested
        output_paths = {}
        if var_dir:
            # Save SVG
            svg_path = var_dir / "output.svg"
            with open(svg_path, 'w') as f:
                f.write(result.svg_content)
            output_paths['svg'] = svg_path

            # Save PNG preview
            png_path = var_dir / "preview.png"
            try:
                import cairosvg
                cairosvg.svg2png(
                    bytestring=result.svg_content.encode('utf-8'),
                    write_to=str(png_path),
                    output_width=400,
                )
                output_paths['png'] = png_path
            except:
                pass

            # Save metadata
            metadata = {
                "variation_id": variation_id,
                "parameters": variation,
                "metrics": metrics.to_dict(),
            }
            metadata_path = var_dir / "metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            output_paths['metadata'] = metadata_path

        return VariationResult(
            variation_id=variation_id,
            variation_index=index,
            parameters=variation,
            metrics=metrics,
            output_paths=output_paths,
            success=True,
        )

    except Exception as e:
        return VariationResult(
            variation_id=variation_id,
            variation_index=index,
            parameters=variation,
            metrics=None,
            output_paths={},
            error=f"{type(e).__name__}: {str(e)}",
            success=False,
        )
