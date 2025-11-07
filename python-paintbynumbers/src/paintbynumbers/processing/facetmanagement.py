"""Facet management for paint-by-numbers generation.

This module provides data structures for managing facets (connected regions
of pixels with the same color) throughout the processing pipeline.
"""

from __future__ import annotations
from typing import List, Optional
from paintbynumbers.structs.point import Point
from paintbynumbers.structs.boundingbox import BoundingBox
from paintbynumbers.structs.typed_arrays import Uint32Array2D
from paintbynumbers.core.types import PathPoint


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
        borderPath: Ordered list of PathPoints tracing the facet border
        borderSegments: List of FacetBoundarySegments for border
        labelBounds: Bounding box for label placement

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
        self.borderPath: List[PathPoint] = []
        self.borderSegments: List['FacetBoundarySegment'] = []
        self.labelBounds: BoundingBox = BoundingBox()

    def get_full_path_from_border_segments(self, use_walls: bool = False) -> List[Point]:
        """Get the full path from border segments.

        Reconstructs the complete border path by concatenating all border segments
        in order. Handles segments that need to be traversed in reverse order and
        adds transition points between segments for continuity.

        Args:
            use_walls: If True, use wall coordinates (±0.5). If False, use pixel centers.

        Returns:
            List of Points forming the complete border path

        Example:
            >>> facet = Facet()
            >>> # ... setup facet with border segments ...
            >>> path = facet.get_full_path_from_border_segments(use_walls=True)
            >>> print(len(path))
            100
        """
        newpath: List[Point] = []

        def add_point(pt: PathPoint) -> None:
            if use_walls:
                newpath.append(Point(pt.get_wall_x(), pt.get_wall_y()))
            else:
                newpath.append(Point(pt.x, pt.y))

        last_segment: Optional[FacetBoundarySegment] = None

        for seg in self.borderSegments:
            # Fix for continuity: repeat transition points between segments
            # to prevent holes when rendered
            if last_segment is not None:
                if last_segment.reverseOrder:
                    add_point(last_segment.originalSegment.points[0])
                else:
                    add_point(last_segment.originalSegment.points[-1])

            # Add all points from this segment (in correct order)
            for i in range(len(seg.originalSegment.points)):
                if seg.reverseOrder:
                    idx = len(seg.originalSegment.points) - 1 - i
                else:
                    idx = i
                add_point(seg.originalSegment.points[idx])

            last_segment = seg

        return newpath

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


class PathSegment:
    """A segment of a border path that is adjacent to a specific neighbour facet.

    Path segments are created by splitting a border path where the neighboring
    facet changes. This allows matching segments between adjacent facets.

    Attributes:
        points: Ordered list of PathPoints forming the segment
        neighbour: Facet ID of the neighbor this segment borders (-1 for image edge)

    Example:
        >>> from paintbynumbers.core.types import PathPoint, OrientationEnum
        >>> points = [PathPoint(1, 1, OrientationEnum.Left), PathPoint(1, 2, OrientationEnum.Left)]
        >>> segment = PathSegment(points, neighbour=5)
        >>> print(len(segment.points))
        2
    """

    def __init__(self, points: List[PathPoint], neighbour: int) -> None:
        """Create a new path segment.

        Args:
            points: Ordered list of PathPoints
            neighbour: Facet ID of neighboring facet
        """
        self.points: List[PathPoint] = points
        self.neighbour: int = neighbour

    def __repr__(self) -> str:
        """Return string representation of path segment."""
        return f"PathSegment(points={len(self.points)}, neighbour={self.neighbour})"


class FacetBoundarySegment:
    """Describes a matched segment shared between 2 facets.

    When two segments are matched, one becomes the original segment and
    the other references it. This ensures that adjacent facets share the
    exact same segment, but sometimes in reverse order to maintain path continuity.

    Attributes:
        originalSegment: The canonical PathSegment instance
        neighbour: Facet ID of the neighbor this segment borders
        reverseOrder: If True, traverse segment points in reverse

    Example:
        >>> from paintbynumbers.core.types import PathPoint, OrientationEnum
        >>> points = [PathPoint(1, 1, OrientationEnum.Left)]
        >>> orig_segment = PathSegment(points, 5)
        >>> boundary = FacetBoundarySegment(orig_segment, neighbour=3, reverseOrder=False)
        >>> print(boundary.neighbour)
        3
    """

    def __init__(
        self,
        originalSegment: PathSegment,
        neighbour: int,
        reverseOrder: bool
    ) -> None:
        """Create a new facet boundary segment.

        Args:
            originalSegment: The canonical PathSegment instance
            neighbour: Facet ID of the neighbor
            reverseOrder: Whether to traverse points in reverse
        """
        self.originalSegment: PathSegment = originalSegment
        self.neighbour: int = neighbour
        self.reverseOrder: bool = reverseOrder

    def __repr__(self) -> str:
        """Return string representation of facet boundary segment."""
        return (f"FacetBoundarySegment(points={len(self.originalSegment.points)}, "
                f"neighbour={self.neighbour}, reverse={self.reverseOrder})")
