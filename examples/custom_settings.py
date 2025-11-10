#!/usr/bin/env python3
"""Example: Using custom settings from JSON configuration.

This example demonstrates how to:
1. Load settings from a JSON file
2. Process an image with custom settings
3. Save output in multiple formats (SVG, PNG, JPG)
"""

import json
from paintbynumbers.core.pipeline import PaintByNumbersPipeline
from paintbynumbers.core.settings import Settings


def main():
    """Process image with custom settings from JSON."""

    # Load settings from JSON file
    with open('settings_example.json', 'r') as f:
        settings_data = json.load(f)

    settings = Settings.from_json(settings_data)

    print("Processing image with custom settings...")
    print(f"- Colors: {settings.kMeansNrOfClusters}")
    print(f"- Color space: {settings.kMeansClusteringColorSpace.value}")
    print(f"- Min facet size: {settings.removeFacetsSmallerThanNrOfPoints}")

    # Process and save in multiple formats
    PaintByNumbersPipeline.process_and_save(
        input_path='input.jpg',
        output_path='output_custom',
        settings=settings,
        export_png=True,
        export_jpg=True,
        progress_callback=lambda stage, progress: print(f"\r{stage}: {int(progress*100)}%", end='')
    )

    print("\n\n✓ Generated files:")
    print("  - output_custom.svg")
    print("  - output_custom.png")
    print("  - output_custom.jpg")


if __name__ == '__main__':
    main()
