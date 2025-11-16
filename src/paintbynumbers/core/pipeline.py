"""Complete processing pipeline for paint-by-numbers generation.

This module orchestrates all processing steps from input image to final output.
"""

from __future__ import annotations
from typing import Optional, Callable, List
from dataclasses import dataclass
import numpy as np

from paintbynumbers.utils.imageio import load_image
from paintbynumbers.processing.colorreduction import ColorReducer
from paintbynumbers.processing.facetbuilder import FacetBuilder
from paintbynumbers.processing.facetreduction import FacetReducer
from paintbynumbers.processing.facetbordertracer import FacetBorderTracer
from paintbynumbers.processing.facetbordersegmenter import FacetBorderSegmenter
from paintbynumbers.processing.facetlabelplacer import FacetLabelPlacer
from paintbynumbers.processing.facetmanagement import FacetResult
from paintbynumbers.output.svgbuilder import SVGBuilder
from paintbynumbers.output.rasterexport import RasterExporter
from paintbynumbers.core.settings import Settings
from paintbynumbers.core.types import RGB


@dataclass
class PipelineResult:
    """Result of the complete pipeline."""
    facet_result: FacetResult
    colors_by_index: List[RGB]
    svg_content: str
    width: int
    height: int


class PaintByNumbersPipeline:
    """Complete paint-by-numbers processing pipeline.

    Orchestrates all steps from image loading to final output generation.
    """

    @staticmethod
    def process(
        input_path: str,
        settings: Settings,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> PipelineResult:
        """Process an image through the complete pipeline.

        Args:
            input_path: Path to input image
            settings: Processing settings
            progress_callback: Optional callback(stage_name, progress) for updates

        Returns:
            PipelineResult with facets, colors, and SVG

        Example:
            >>> from paintbynumbers.core.settings import Settings
            >>> settings = Settings()
            >>> result = PaintByNumbersPipeline.process('input.jpg', settings)
            >>> with open('output.svg', 'w') as f:
            ...     f.write(result.svg_content)
        """
        def update(stage: str, progress: float):
            if progress_callback:
                progress_callback(stage, progress)

        # Stage 1: Load image
        update("Loading image", 0.0)
        img_data, width, height = load_image(
            input_path,
            max_width=settings.resizeImageWidth if settings.resizeImageIfTooLarge else None,
            max_height=settings.resizeImageHeight if settings.resizeImageIfTooLarge else None
        )
        update("Loading image", 1.0)

        # Stage 2: K-means clustering
        update("K-means clustering", 0.0)
        clustered_data, kmeans = ColorReducer.apply_kmeans_clustering(
            img_data,
            width,
            height,
            settings
        )
        update("K-means clustering", 1.0)

        # Stage 3: Create color map
        update("Creating color map", 0.0)
        color_map_result = ColorReducer.create_color_map(clustered_data, width, height)
        update("Creating color map", 1.0)

        # Stages 4-7: Facet building and reduction
        # Important: If narrow pixel strip cleanup is enabled, we need to rebuild facets
        # after each cleanup run because facet reduction updates the color indices
        facet_builder = FacetBuilder()
        facet_result = FacetResult()
        facet_result.width = width
        facet_result.height = height
        from paintbynumbers.structs.typed_arrays import Uint32Array2D

        if settings.narrowPixelStripCleanupRuns == 0:
            # No cleanup runs - just build facets once
            update("Building facets", 0.0)
            facet_result.facetMap = Uint32Array2D(width, height)
            facet_result.facets = facet_builder.build_all_facets(
                color_map_result.imgColorIndices,
                width,
                height,
                facet_result
            )
            update("Building facets", 1.0)

            # Build facet neighbors
            update("Building neighbors", 0.0)
            for i, facet in enumerate(facet_result.facets):
                if facet is not None:
                    facet_builder.build_facet_neighbour(facet, facet_result)
                if (i + 1) % 100 == 0:
                    update("Building neighbors", (i + 1) / len(facet_result.facets))
            update("Building neighbors", 1.0)

            # Reduce facets
            if settings.removeFacetsSmallerThanNrOfPoints > 0 or (settings.maximumNumberOfFacets is not None and settings.maximumNumberOfFacets < len(facet_result.facets)):
                update("Reducing facets", 0.0)
                FacetReducer.reduce_facets(
                    settings.removeFacetsSmallerThanNrOfPoints,
                    settings.removeFacetsFromLargeToSmall,
                    settings.maximumNumberOfFacets,
                    color_map_result.colorsByIndex,
                    facet_result,
                    color_map_result.imgColorIndices,
                    on_update=lambda p: update("Reducing facets", p)
                )
        else:
            # Multiple cleanup runs - rebuild facets after each cleanup
            # The color indices get updated during facet reduction, so we need to
            # rebuild facets in each iteration to handle the updated color map
            for run in range(settings.narrowPixelStripCleanupRuns):
                # Stage 4: Narrow pixel strip cleanup
                update("Cleaning narrow strips", 0.0)
                ColorReducer.process_narrow_pixel_strip_cleanup(color_map_result)
                update("Cleaning narrow strips", (run + 1) / settings.narrowPixelStripCleanupRuns)

                # Stage 5: Build facets (rebuild each time)
                update("Building facets", 0.0)
                facet_result.facetMap = Uint32Array2D(width, height)
                facet_result.facets = facet_builder.build_all_facets(
                    color_map_result.imgColorIndices,
                    width,
                    height,
                    facet_result
                )
                update("Building facets", 1.0)

                # Stage 6: Build facet neighbors
                update("Building neighbors", 0.0)
                for i, facet in enumerate(facet_result.facets):
                    if facet is not None:
                        facet_builder.build_facet_neighbour(facet, facet_result)
                    if (i + 1) % 100 == 0:
                        update("Building neighbors", (i + 1) / len(facet_result.facets))
                update("Building neighbors", 1.0)

                # Stage 7: Reduce facets (updates color indices for next iteration)
                if settings.removeFacetsSmallerThanNrOfPoints > 0 or (settings.maximumNumberOfFacets is not None and settings.maximumNumberOfFacets < len(facet_result.facets)):
                    update("Reducing facets", 0.0)
                    FacetReducer.reduce_facets(
                        settings.removeFacetsSmallerThanNrOfPoints,
                        settings.removeFacetsFromLargeToSmall,
                        settings.maximumNumberOfFacets,
                        color_map_result.colorsByIndex,
                        facet_result,
                        color_map_result.imgColorIndices,
                        on_update=lambda p: update("Reducing facets", p)
                    )

        # Stage 8: Trace borders
        update("Tracing borders", 0.0)
        FacetBorderTracer.build_facet_border_paths(
            facet_result,
            on_update=lambda p: update("Tracing borders", p)
        )
        update("Tracing borders", 1.0)

        # Stage 9: Segment borders
        update("Segmenting borders", 0.0)
        FacetBorderSegmenter.build_facet_border_segments(
            facet_result,
            nr_of_times_to_halve_points=settings.nrOfTimesToHalveBorderSegments,
            on_update=lambda p: update("Segmenting borders", p)
        )
        update("Segmenting borders", 1.0)

        # Stage 10: Place labels
        update("Placing labels", 0.0)
        FacetLabelPlacer.build_facet_label_bounds(
            facet_result,
            on_update=lambda p: update("Placing labels", p)
        )
        update("Placing labels", 1.0)

        # Stage 11: Generate SVG
        update("Generating SVG", 0.0)
        # Use first output profile for default SVG generation
        profile = settings.outputProfiles[0] if settings.outputProfiles else None
        if profile is None:
            # Create default profile if none exists
            from paintbynumbers.core.settings import OutputProfile
            profile = OutputProfile(name="default")

        svg_content = SVGBuilder.create_svg(
            facet_result,
            color_map_result.colorsByIndex,
            size_multiplier=profile.svgSizeMultiplier,
            fill=profile.svgFillFacets,
            stroke=profile.svgShowBorders,
            add_color_labels=profile.svgShowLabels,
            font_size=profile.svgFontSize,
            font_color=profile.svgFontColor,
            border_width=profile.svgBorderWidth,
            label_start_number=profile.svgLabelStartNumber
        )
        update("Generating SVG", 1.0)

        return PipelineResult(
            facet_result=facet_result,
            colors_by_index=color_map_result.colorsByIndex,
            svg_content=svg_content,
            width=width,
            height=height
        )

    @staticmethod
    def process_and_save(
        input_path: str,
        output_path: str,
        settings: Settings,
        export_png: bool = False,
        export_jpg: bool = False,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> None:
        """Process an image and save output files.

        Args:
            input_path: Path to input image
            output_path: Base path for output files (without extension)
            settings: Processing settings
            export_png: If True, also export PNG
            export_jpg: If True, also export JPG
            progress_callback: Optional callback(stage_name, progress) for updates

        Example:
            >>> settings = Settings()
            >>> PaintByNumbersPipeline.process_and_save(
            ...     'input.jpg',
            ...     'output',
            ...     settings,
            ...     export_png=True
            ... )
            # Creates: output.svg, output.png
        """
        # Process the image
        result = PaintByNumbersPipeline.process(input_path, settings, progress_callback)

        # Save SVG
        svg_path = f"{output_path}.svg"
        with open(svg_path, 'w') as f:
            f.write(result.svg_content)

        # Get output profile for export settings
        profile = settings.outputProfiles[0] if settings.outputProfiles else None
        if profile is None:
            from paintbynumbers.core.settings import OutputProfile
            profile = OutputProfile(name="default")

        # Export PNG if requested
        if export_png:
            png_path = f"{output_path}.png"
            RasterExporter.export_png(result.svg_content, png_path, scale=profile.svgSizeMultiplier)

        # Export JPG if requested
        if export_jpg:
            jpg_path = f"{output_path}.jpg"
            quality = int(profile.filetypeQuality * 100)
            RasterExporter.export_jpg(result.svg_content, jpg_path, quality=quality, scale=profile.svgSizeMultiplier)

        return result