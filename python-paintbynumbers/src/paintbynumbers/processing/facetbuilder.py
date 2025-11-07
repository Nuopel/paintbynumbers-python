"""Facet building utilities.

Separates facet construction from region finding, making the code
more modular and easier to test.
"""

from __future__ import annotations
from typing import List, Set
from paintbynumbers.structs.point import Point
from paintbynumbers.structs.boundingbox import BoundingBox
from paintbynumbers.structs.typed_arrays import BooleanArray2D, Uint8Array2D
from paintbynumbers.algorithms.flood_fill import FloodFillAlgorithm
from paintbynumbers.utils.boundary import get_neighbors_4
from paintbynumbers.processing.facetmanagement import Facet, FacetResult


class FacetBuilder:
    """Builder class for creating facets from color-mapped images.

    Provides a clean interface for facet creation that separates the concerns
    of region detection (flood fill) from facet object construction.

    Example:
        >>> builder = FacetBuilder()
        >>> result = FacetResult()
        >>> result.width = 100
        >>> result.height = 100
        >>> result.facetMap = Uint32Array2D(100, 100)
        >>> result.facets = []
        >>> visited = BooleanArray2D(100, 100)
        >>> facet = builder.build_facet(
        ...     0, 5, 10, 10,
        ...     visited, color_map, result
        ... )
        >>> print(f"Facet has {facet.pointCount} pixels")
    """

    def __init__(self) -> None:
        """Create a new facet builder."""
        self._flood_fill = FloodFillAlgorithm()

    def build_facet(
        self,
        facet_index: int,
        facet_color_index: int,
        x: int,
        y: int,
        visited: BooleanArray2D,
        img_color_indices: Uint8Array2D,
        facet_result: FacetResult
    ) -> Facet:
        """Build a single facet starting from a given point.

        Uses flood fill to find all connected pixels of the same color,
        then constructs a Facet object with:
        - Point count
        - Border points
        - Bounding box
        - Color index

        Args:
            facet_index: Unique index for this facet
            facet_color_index: Color index this facet represents
            x: Starting x coordinate
            y: Starting y coordinate
            visited: 2D array tracking visited pixels
            img_color_indices: 2D array of color indices
            facet_result: Result container to update

        Returns:
            Newly created facet

        Example:
            >>> builder = FacetBuilder()
            >>> visited = BooleanArray2D(width, height)
            >>> facet = builder.build_facet(
            ...     0, 5, 10, 10,
            ...     visited, color_map, result
            ... )
            >>> print(f"Facet has {facet.pointCount} pixels")
        """
        facet = Facet()
        facet.id = facet_index
        facet.color = facet_color_index
        facet.bbox = BoundingBox()
        facet.borderPoints = []
        facet.neighbourFacetsIsDirty = True
        facet.neighbourFacets = None

        def should_include(ptx: int, pty: int) -> bool:
            """Check if pixel should be included in facet."""
            if visited.get(ptx, pty):
                return False
            if img_color_indices.get(ptx, pty) != facet_color_index:
                return False
            return True

        def on_fill(ptx: int, pty: int) -> None:
            """Callback for each filled pixel."""
            # Mark as visited
            visited.set(ptx, pty, True)
            facet_result.facetMap.set(ptx, pty, facet_index)  # type: ignore
            facet.pointCount += 1

            # Determine if this is a border point
            # A point is a border point if any of its 4-neighbors has a different color
            is_inner_point = img_color_indices.match_all_around(ptx, pty, facet_color_index)
            if not is_inner_point:
                facet.borderPoints.append(Point(ptx, pty))

            # Update bounding box
            if ptx > facet.bbox.maxX:
                facet.bbox.maxX = ptx
            if pty > facet.bbox.maxY:
                facet.bbox.maxY = pty
            if ptx < facet.bbox.minX:
                facet.bbox.minX = ptx
            if pty < facet.bbox.minY:
                facet.bbox.minY = pty

        # Use optimized fill algorithm with callbacks
        self._flood_fill.fill_with_callback(
            Point(x, y),
            facet_result.width,
            facet_result.height,
            should_include,
            on_fill
        )

        return facet

    def build_all_facets(
        self,
        img_color_indices: Uint8Array2D,
        width: int,
        height: int,
        facet_result: FacetResult
    ) -> List[Facet]:
        """Build all facets from a color-mapped image.

        Scans the entire image and creates a facet for each connected region
        of pixels with the same color.

        Args:
            img_color_indices: 2D array of color indices
            width: Image width
            height: Image height
            facet_result: Result container to populate

        Returns:
            Array of created facets

        Example:
            >>> builder = FacetBuilder()
            >>> result = FacetResult()
            >>> result.width = 100
            >>> result.height = 100
            >>> result.facetMap = Uint32Array2D(100, 100)
            >>> result.facets = []
            >>> facets = builder.build_all_facets(color_map, 100, 100, result)
            >>> print(f"Created {len(facets)} facets")
        """
        visited = BooleanArray2D(width, height)
        facets: List[Facet] = []

        for j in range(height):
            for i in range(width):
                if not visited.get(i, j):
                    color_index = img_color_indices.get(i, j)
                    facet_index = len(facets)

                    facet = self.build_facet(
                        facet_index,
                        color_index,
                        i,
                        j,
                        visited,
                        img_color_indices,
                        facet_result
                    )

                    facets.append(facet)

        return facets

    def calculate_bounding_box(self, points: List[Point]) -> BoundingBox:
        """Calculate the bounding box of a set of points.

        Args:
            points: Array of points

        Returns:
            Bounding box containing all points

        Example:
            >>> builder = FacetBuilder()
            >>> points = [Point(5, 10), Point(15, 20), Point(8, 12)]
            >>> bbox = builder.calculate_bounding_box(points)
            >>> print(f"Box: ({bbox.minX}, {bbox.minY}) to ({bbox.maxX}, {bbox.maxY})")
        """
        if len(points) == 0:
            return BoundingBox()

        bbox = BoundingBox()
        bbox.minX = float('inf')
        bbox.minY = float('inf')
        bbox.maxX = float('-inf')
        bbox.maxY = float('-inf')

        for pt in points:
            if pt.x < bbox.minX:
                bbox.minX = pt.x
            if pt.x > bbox.maxX:
                bbox.maxX = pt.x
            if pt.y < bbox.minY:
                bbox.minY = pt.y
            if pt.y > bbox.maxY:
                bbox.maxY = pt.y

        return bbox

    def identify_border_points(
        self,
        points: List[Point],
        width: int,
        height: int
    ) -> List[Point]:
        """Identify border points within a set of points.

        A point is considered a border point if any of its 4-neighbors
        (up, down, left, right) is not in the point set.

        Args:
            points: Array of points in the region
            width: Width of the area
            height: Height of the area

        Returns:
            Array of border points

        Example:
            >>> builder = FacetBuilder()
            >>> region = [
            ...     Point(5, 5), Point(6, 5), Point(7, 5),
            ...     Point(5, 6), Point(6, 6), Point(7, 6),
            ... ]
            >>> border = builder.identify_border_points(region, 100, 100)
            >>> print(f"{len(border)} border points found")
        """
        # Create a set for fast lookup
        point_set: Set[int] = set()
        for pt in points:
            point_set.add(pt.y * width + pt.x)

        border_points: List[Point] = []

        for pt in points:
            is_border = False

            # Check 4-neighbors
            if pt.y > 0 and (pt.y - 1) * width + pt.x not in point_set:
                is_border = True  # Top neighbor missing
            elif pt.y < height - 1 and (pt.y + 1) * width + pt.x not in point_set:
                is_border = True  # Bottom neighbor missing
            elif pt.x > 0 and pt.y * width + (pt.x - 1) not in point_set:
                is_border = True  # Left neighbor missing
            elif pt.x < width - 1 and pt.y * width + (pt.x + 1) not in point_set:
                is_border = True  # Right neighbor missing

            # Also check if at image boundary
            if pt.x == 0 or pt.x == width - 1 or pt.y == 0 or pt.y == height - 1:
                is_border = True

            if is_border:
                border_points.append(pt)

        return border_points

    def build_facet_neighbour(
        self,
        facet: Facet,
        facet_result: FacetResult
    ) -> None:
        """Build the list of neighboring facets for a given facet.

        Checks which neighbor facets the given facet has by examining
        the neighbors at each border point.

        Args:
            facet: Facet to find neighbors for
            facet_result: Result container with facet map

        Example:
            >>> builder = FacetBuilder()
            >>> builder.build_facet_neighbour(facet, facet_result)
            >>> print(f"Facet {facet.id} has {len(facet.neighbourFacets)} neighbors")
        """
        facet.neighbourFacets = []
        unique_facets: Set[int] = set()  # Poor man's set

        for pt in facet.borderPoints:
            # Get all 4-connected neighbors within bounds
            neighbors = get_neighbors_4(pt.x, pt.y, facet_result.width, facet_result.height)
            for neighbor in neighbors:
                neighbor_facet_id = facet_result.facetMap.get(neighbor.x, neighbor.y)  # type: ignore
                if neighbor_facet_id != facet.id:
                    unique_facets.add(neighbor_facet_id)

        facet.neighbourFacets = list(unique_facets)
        # The neighbour array is updated so it's not dirty anymore
        facet.neighbourFacetsIsDirty = False
