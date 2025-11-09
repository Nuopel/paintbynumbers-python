#!/usr/bin/env python3
"""Basic usage examples for Paint by Numbers Generator.

This script demonstrates how to use the library programmatically.
"""

from pathlib import Path
from paintbynumbers.core.pipeline import PaintByNumbersPipeline
from paintbynumbers.core.settings import Settings, ClusteringColorSpace, OutputProfile


def example_basic():
    """Basic example - process an image with default settings."""
    print("Example 1: Basic usage with defaults")
    print("-" * 50)

    # Create default settings
    settings = Settings()

    # Process and save
    PaintByNumbersPipeline.process_and_save(
        input_path="input.jpg",
        output_path="output_basic",
        settings=settings,
        export_png=True
    )

    print("✓ Generated: output_basic.svg, output_basic.png\n")


def example_custom_colors():
    """Example with custom color settings."""
    print("Example 2: Custom color settings")
    print("-" * 50)

    # Create settings with custom colors
    settings = Settings()
    settings.kMeansNrOfClusters = 24  # Use 24 colors instead of default 16
    settings.kMeansClusteringColorSpace = ClusteringColorSpace.LAB  # Use LAB color space

    PaintByNumbersPipeline.process_and_save(
        input_path="input.jpg",
        output_path="output_24colors",
        settings=settings,
        export_png=True
    )

    print("✓ Generated: output_24colors.svg with 24 colors in LAB space\n")


def example_output_profiles():
    """Example with custom output profiles."""
    print("Example 3: Custom output profile")
    print("-" * 50)

    # Create settings with custom output profile
    settings = Settings()

    # Create a custom profile with larger labels and different appearance
    profile = OutputProfile(
        name="large_labels",
        filetype="svg",
        svgShowLabels=True,
        svgShowBorders=True,
        svgFillFacets=False,  # Outline only
        svgSizeMultiplier=4.0,  # Larger output
        svgFontSize=28,  # Larger font
        svgFontColor="#FF0000"  # Red labels
    )
    settings.outputProfiles = [profile]

    PaintByNumbersPipeline.process_and_save(
        input_path="input.jpg",
        output_path="output_outline",
        settings=settings
    )

    print("✓ Generated: output_outline.svg with red labels and no fill\n")


def example_high_quality():
    """Example for high-quality output with many colors and fine details."""
    print("Example 4: High-quality output")
    print("-" * 50)

    settings = Settings()

    # High color count
    settings.kMeansNrOfClusters = 32

    # Keep more detail
    settings.removeFacetsSmallerThanNrOfPoints = 10  # Keep smaller facets
    settings.narrowPixelStripCleanupRuns = 5  # More cleanup passes

    # Smoother borders
    settings.nrOfTimesToHalveBorderSegments = 3  # More smoothing

    # High resolution output
    profile = OutputProfile(
        name="high_quality",
        svgSizeMultiplier=5.0,
        svgFontSize=16,
        svgShowLabels=True,
        svgShowBorders=True,
        svgFillFacets=True
    )
    settings.outputProfiles = [profile]

    PaintByNumbersPipeline.process_and_save(
        input_path="input.jpg",
        output_path="output_hq",
        settings=settings,
        export_png=True,
        export_jpg=True
    )

    print("✓ Generated: output_hq.svg, output_hq.png, output_hq.jpg with high quality\n")


def example_with_progress():
    """Example with progress callback."""
    print("Example 5: Processing with progress updates")
    print("-" * 50)

    def progress_callback(stage: str, progress: float):
        """Display progress updates."""
        bar_width = 30
        filled = int(bar_width * progress)
        bar = "█" * filled + "░" * (bar_width - filled)
        percent = int(progress * 100)
        print(f"\r{stage:.<30} [{bar}] {percent}%", end="", flush=True)
        if progress >= 1.0:
            print()

    settings = Settings()
    settings.resizeImageWidth = 1000
    settings.resizeImageHeight = 1000
    settings.kMeansNrOfClusters = 16

    PaintByNumbersPipeline.process_and_save(
        input_path="input2.png",
        output_path="output_progress",
        settings=settings,
        export_png=True,
        progress_callback=progress_callback
    )

    print("\n✓ Completed with progress tracking\n")


def example_programmatic_access():
    """Example showing programmatic access to results."""
    print("Example 6: Programmatic access to results")
    print("-" * 50)

    settings = Settings()
    settings.kMeansNrOfClusters = 12

    # Process and get results
    result = PaintByNumbersPipeline.process(
        input_path="input.jpg",
        settings=settings
    )

    # Access the results
    print(f"Image dimensions: {result.width}x{result.height}")
    print(f"Number of colors: {len(result.colors_by_index)}")
    print(f"Number of facets: {len([f for f in result.facet_result.facets if f is not None])}")

    # Print color palette
    print("\nColor palette:")
    for i, color in enumerate(result.colors_by_index):
        print(f"  Color {i+1}: RGB{color}")

    # Save SVG manually
    with open("output_programmatic.svg", 'w') as f:
        f.write(result.svg_content)

    print("\n✓ Results accessed and saved programmatically\n")


def example_config_file():
    """Example loading and saving configuration."""
    print("Example 7: Configuration file usage")
    print("-" * 50)

    import json

    # Create and save a configuration
    settings = Settings()
    settings.kMeansNrOfClusters = 20
    settings.kMeansClusteringColorSpace = ClusteringColorSpace.LAB
    settings.removeFacetsSmallerThanNrOfPoints = 15

    # Save to JSON
    config_path = "my_config.json"
    with open(config_path, 'w') as f:
        json.dump(settings.to_json(), f, indent=2)
    print(f"✓ Configuration saved to {config_path}")

    # Load from JSON
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    loaded_settings = Settings.from_json(config_data)
    print(f"✓ Configuration loaded from {config_path}")

    # Use loaded settings
    PaintByNumbersPipeline.process_and_save(
        input_path="input.jpg",
        output_path="output_from_config",
        settings=loaded_settings
    )

    print("✓ Image processed with loaded configuration\n")


def main():
    """Run all examples (commented out - uncomment as needed)."""
    print("Paint by Numbers Generator - Usage Examples")
    print("=" * 50)
    print()

    # Note: You'll need to provide an actual input.jpg file to run these examples
    print("To run these examples:")
    print("1. Place an image file named 'input.jpg' in the current directory")
    print("2. Uncomment the example functions you want to run")
    print("3. Run this script: python examples/basic_usage.py")
    print()

    # Uncomment the examples you want to run:

    # example_basic()
    # example_custom_colors()
    # example_output_profiles()
    # example_high_quality()
    example_with_progress()
    # example_programmatic_access()
    # example_config_file()


if __name__ == "__main__":
    main()
