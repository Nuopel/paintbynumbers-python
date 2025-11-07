"""Facet management for paint-by-numbers generation.

This module provides data structures for managing facets (connected regions
of pixels with the same color) throughout the processing pipeline.
"""

from __future__ import annotations
from typing import List, Optional
from paintbynumbers.structs.point import Point
from paintbynumbers.structs.boundingbox import BoundingBox
from paintbynumbers.structs.typed_arrays import Uint32Array2D


class Facet:
    """A facet representing an area of pixels of the same color.

    Attributes:
        id: Unique identifier (always matches index in facets array)
        color: Color index this facet represents
        pointCount: Number of pixels in this facet
        borderPoints: List of points on the border of the facet
        neighbourFacets: List of neighboring facet IDs (None if dirty)
        neighbourFacetsIsDirty: Flag indicating neighbor list needs rebuilding
        bbox: Bounding box containing all facet points

    Example:
        >>> facet = Facet()
        >>> facet.id = 0
        >>> facet.color = 5
        >>> facet.pointCount = 100
        >>> facet.bbox = BoundingBox()
    """

    def __init__(self) -> None:
        """Create a new facet."""
        self.id: int = -1
        self.color: int = -1
        self.pointCount: int = 0
        self.borderPoints: List[Point] = []
        self.neighbourFacets: Optional[List[int]] = None
        self.neighbourFacetsIsDirty: bool = False
        self.bbox: BoundingBox = BoundingBox()

    def __repr__(self) -> str:
        """Return string representation of facet."""
        return (f"Facet(id={self.id}, color={self.color}, "
                f"pointCount={self.pointCount}, "
                f"borderPoints={len(self.borderPoints)})")


class FacetResult:
    """Result of facet construction, both as a map and as an array.

    Facets in the array can be None when they've been deleted (e.g., during
    facet reduction). The facet map provides O(1) lookup of which facet owns
    each pixel.

    Attributes:
        facetMap: 2D array mapping pixels to facet IDs
        facets: Array of facets (can contain None for deleted facets)
        width: Image width
        height: Image height

    Example:
        >>> result = FacetResult()
        >>> result.width = 100
        >>> result.height = 100
        >>> result.facetMap = Uint32Array2D(100, 100)
        >>> result.facets = []
    """

    def __init__(self) -> None:
        """Create a new facet result."""
        self.facetMap: Optional[Uint32Array2D] = None
        self.facets: List[Optional[Facet]] = []
        self.width: int = 0
        self.height: int = 0

    def get_facet_count(self) -> int:
        """Get the number of non-deleted facets.

        Returns:
            Number of facets that are not None
        """
        return sum(1 for f in self.facets if f is not None)

    def __repr__(self) -> str:
        """Return string representation of facet result."""
        return (f"FacetResult(width={self.width}, height={self.height}, "
                f"facets={self.get_facet_count()}/{len(self.facets)})")
