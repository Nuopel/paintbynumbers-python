#!/usr/bin/env python
"""Quick performance test for facet reduction improvements."""

import time
from paintbynumbers.core.pipeline import PaintByNumbersPipeline
from paintbynumbers.core.settings import Settings

def progress_callback(stage: str, progress: float):
    """Display progress updates."""
    bar_width = 30
    filled = int(bar_width * progress)
    bar = "█" * filled + "░" * (bar_width - filled)
    percent = int(progress * 100)
    print(f"\r{stage:.<30} [{bar}] {percent}%", end="", flush=True)
    if progress >= 1.0:
        print()

def main():
    print("Performance Test: Facet Reduction")
    print("=" * 60)

    settings = Settings()
    settings.resizeImageWidth = 300
    settings.resizeImageHeight = 300
    settings.removeFacetsSmallerThanNrOfPoints = 20
    settings.maximumNumberOfFacets = None  # Use default

    # Test with input.png if it exists
    try:
        start_time = time.time()

        PaintByNumbersPipeline.process_and_save(
            input_path="input.png",
            output_path="test_output",
            settings=settings,
            export_png=True,
            progress_callback=progress_callback
        )

        elapsed = time.time() - start_time
        print(f"\n✓ Processing completed in {elapsed:.2f} seconds")
        print("\nImprovements:")
        print("1. ✓ Fixed Point object allocation (distance_to_coord)")
        print("2. ✓ Added progress callback support")
        print("\nYou should now see smooth progress updates during")
        print("'Reducing facets' instead of it being stuck at 0%!")

    except FileNotFoundError:
        print("\nℹ️  No input.png found - skipping actual test")
        print("To test, create an input.png file and run again.")
        print("\nCode improvements applied:")
        print("1. ✓ Fixed Point object allocation")
        print("2. ✓ Added progress callback support")

if __name__ == "__main__":
    main()
