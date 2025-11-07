"""Paint by Numbers Generator - Convert images to paint-by-numbers format.

This package provides tools to convert any image into a paint-by-numbers style
image with numbered regions, vectorized as SVG.

Example:
    >>> from paintbynumbers import Settings, process_image_from_file
    >>> settings = Settings(kMeansNrOfClusters=16)
    >>> result = process_image_from_file("input.jpg", settings)
    >>> result.save_svg("output.svg")
"""

__version__ = "1.0.0"
__author__ = "Paint by Numbers Generator Contributors"

# Import main public API
from paintbynumbers.core.settings import Settings, ClusteringColorSpace

__all__ = [
    "__version__",
    "Settings",
    "ClusteringColorSpace",
]
