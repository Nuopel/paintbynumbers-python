"""Example usage of the Paint-by-Numbers Explorer programmatically."""

from pathlib import Path
from paintbynumbers.explorer import (
    ExplorerConfig,
    ExplorationEngine,
    ExplorationStrategy,
    HTMLReportGenerator,
    get_preset,
)


def example_basic_usage():
    """Basic usage with preset configuration."""
    print("=" * 60)
    print("Example 1: Basic usage with preset")
    print("=" * 60)

    # Use a preset configuration
    config = get_preset('quick_test')

    # Run exploration
    engine = ExplorationEngine(
        config=config,
        input_image=Path("path/to/your/image.jpg"),
        output_dir=Path("results/example1"),
    )

    results = engine.run()

    # Generate HTML report
    report_generator = HTMLReportGenerator(results, engine.output_dir)
    report_generator.generate(engine.output_dir / "report.html")

    print(f"\nResults saved to: {engine.output_dir}")


def example_custom_config():
    """Custom exploration configuration."""
    print("\n" + "=" * 60)
    print("Example 2: Custom configuration")
    print("=" * 60)

    # Create custom configuration
    config = ExplorerConfig(
        strategy=ExplorationStrategy.STAR,
        baseline={
            "kMeansNrOfClusters": 16,
            "kMeansClusteringColorSpace": "RGB",
            "removeFacetsSmallerThanNrOfPoints": 20,
        },
        vary={
            "kMeansNrOfClusters": [8, 12, 16, 20, 24],
            "kMeansClusteringColorSpace": ["RGB", "LAB", "HSL"],
        },
        parallel_processing=True,
        save_intermediate=True,
    )

    print(f"Total variations: {config.get_total_combinations()}")
    print(f"Strategy: {config.strategy.value}")

    # Save configuration for later use
    config.to_json("my_explorer_config.json")
    print("Configuration saved to: my_explorer_config.json")


def example_grid_exploration():
    """Grid exploration for thorough testing."""
    print("\n" + "=" * 60)
    print("Example 3: Grid exploration (all combinations)")
    print("=" * 60)

    config = ExplorerConfig(
        strategy=ExplorationStrategy.GRID,
        baseline={
            "kMeansNrOfClusters": 16,
            "kMeansClusteringColorSpace": "RGB",
        },
        vary={
            "kMeansNrOfClusters": [12, 16, 20],
            "kMeansClusteringColorSpace": ["RGB", "LAB"],
            "removeFacetsSmallerThanNrOfPoints": [10, 20],
        },
    )

    total = config.get_total_combinations()
    print(f"Total variations: {total} (3 × 2 × 2)")
    print("This will test ALL combinations")


def example_random_sampling():
    """Random sampling for large parameter spaces."""
    print("\n" + "=" * 60)
    print("Example 4: Random sampling")
    print("=" * 60)

    config = ExplorerConfig(
        strategy=ExplorationStrategy.RANDOM,
        random_samples=20,  # Generate 20 random variations
        baseline={
            "kMeansNrOfClusters": 16,
        },
        vary={
            "kMeansNrOfClusters": [6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 32],
            "kMeansClusteringColorSpace": ["RGB", "LAB", "HSL"],
            "removeFacetsSmallerThanNrOfPoints": [10, 15, 20, 25, 30, 40, 50],
            "nrOfTimesToHalveBorderSegments": [0, 1, 2, 3],
        },
    )

    total_possible = 11 * 3 * 7 * 4  # 924 combinations
    print(f"Total possible combinations: {total_possible}")
    print(f"Will randomly sample: {config.random_samples}")
    print("This is useful when grid search would be too expensive")


def example_color_space_comparison():
    """Compare different color spaces."""
    print("\n" + "=" * 60)
    print("Example 5: Color space comparison")
    print("=" * 60)

    config = get_preset('color_space_comparison')

    print(f"Strategy: {config.strategy.value}")
    print(f"Varying: {list(config.vary.keys())}")
    print("This helps determine which color space works best for your image")


def example_progressive_refinement():
    """Progressive refinement: coarse grid then fine-tuning."""
    print("\n" + "=" * 60)
    print("Example 6: Progressive refinement strategy")
    print("=" * 60)

    # Step 1: Coarse exploration
    coarse_config = ExplorerConfig(
        strategy=ExplorationStrategy.GRID,
        baseline={"kMeansNrOfClusters": 16},
        vary={"kMeansNrOfClusters": [8, 16, 24, 32]},
    )

    print("Step 1 - Coarse grid:")
    print(f"  Testing clusters: {coarse_config.vary['kMeansNrOfClusters']}")
    print(f"  Variations: {coarse_config.get_total_combinations()}")

    # After reviewing results, suppose 16 clusters looked best
    # Step 2: Fine-tuning around best value
    fine_config = ExplorerConfig(
        strategy=ExplorationStrategy.GRID,
        baseline={"kMeansNrOfClusters": 16},
        vary={
            "kMeansNrOfClusters": [14, 16, 18],
            "removeFacetsSmallerThanNrOfPoints": [15, 20, 25],
            "nrOfTimesToHalveBorderSegments": [1, 2, 3],
        },
    )

    print("\nStep 2 - Fine-tuning around cluster=16:")
    print(f"  Variations: {fine_config.get_total_combinations()}")
    print("  Tests nearby cluster values with other parameters")


def example_with_progress_callback():
    """Using a custom progress callback."""
    print("\n" + "=" * 60)
    print("Example 7: Custom progress callback")
    print("=" * 60)

    def my_progress_callback(current, total, message):
        percent = (current / total) * 100
        print(f"[{percent:5.1f}%] {current}/{total} - {message}")

    config = get_preset('quick_test')

    engine = ExplorationEngine(
        config=config,
        input_image=Path("path/to/your/image.jpg"),
        progress_callback=my_progress_callback,
    )

    print("Progress callback will be called for each variation")


def main():
    """Run all examples (informational only, doesn't process images)."""
    print("\nPaint-by-Numbers Explorer - Usage Examples")
    print("=" * 60)

    example_basic_usage()
    example_custom_config()
    example_grid_exploration()
    example_random_sampling()
    example_color_space_comparison()
    example_progressive_refinement()
    example_with_progress_callback()

    print("\n" + "=" * 60)
    print("To actually run exploration, replace 'path/to/your/image.jpg'")
    print("with a real image path and uncomment the engine.run() calls.")
    print("=" * 60)


if __name__ == "__main__":
    # Show examples without actually running (no real image paths)
    # To run for real, provide actual image paths
    main()
