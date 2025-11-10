#!/usr/bin/env python3
"""Example: Batch processing multiple images.

This example demonstrates how to:
1. Process multiple images in a batch
2. Use different settings for each image
3. Track overall progress
"""

from pathlib import Path
from paintbynumbers.core.pipeline import PaintByNumbersPipeline
from paintbynumbers.core.settings import Settings, ClusteringColorSpace


def process_batch(images_and_settings):
    """Process multiple images with individual settings.

    Args:
        images_and_settings: List of (input_path, output_path, settings) tuples
    """
    total = len(images_and_settings)

    for i, (input_path, output_path, settings) in enumerate(images_and_settings, 1):
        print(f"\n[{i}/{total}] Processing: {input_path}")
        print(f"  Output: {output_path}")
        print(f"  Colors: {settings.kMeansNrOfClusters}")

        try:
            PaintByNumbersPipeline.process_and_save(
                input_path=input_path,
                output_path=output_path,
                settings=settings,
                export_png=True
            )
            print(f"  ✓ Complete")
        except Exception as e:
            print(f"  ✗ Error: {e}")


def main():
    """Batch process example images with different settings."""

    # Create different settings for different image types

    # Low detail setting (few colors, larger facets)
    low_detail = Settings()
    low_detail.kMeansNrOfClusters = 8
    low_detail.removeFacetsSmallerThanNrOfPoints = 30

    # Medium detail setting (balanced)
    medium_detail = Settings()
    medium_detail.kMeansNrOfClusters = 16
    medium_detail.removeFacetsSmallerThanNrOfPoints = 20

    # High detail setting (many colors, small facets)
    high_detail = Settings()
    high_detail.kMeansNrOfClusters = 32
    high_detail.removeFacetsSmallerThanNrOfPoints = 10
    high_detail.kMeansClusteringColorSpace = ClusteringColorSpace.LAB

    # Define batch: (input, output, settings)
    batch = [
        ('landscape.jpg', 'output/landscape_low', low_detail),
        ('portrait.jpg', 'output/portrait_medium', medium_detail),
        ('detailed.jpg', 'output/detailed_high', high_detail),
    ]

    print("=== Batch Processing ===")
    print(f"Total images: {len(batch)}")

    process_batch(batch)

    print("\n=== Batch Complete ===")


if __name__ == '__main__':
    main()
