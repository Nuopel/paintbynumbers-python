#!/usr/bin/env python3
"""Example: Simplest possible usage - just a few lines!

This is the absolute minimal example to get started.
"""

from paintbynumbers.core.pipeline import PaintByNumbersPipeline
from paintbynumbers.core.settings import Settings

# Create default settings
settings = Settings()

# Process image and save as SVG
PaintByNumbersPipeline.process_and_save(
    input_path='input.jpg',
    output_path='output',
    settings=settings
)

print("✓ Done! Check output.svg")
