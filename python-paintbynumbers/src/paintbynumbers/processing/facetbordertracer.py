"""Border tracing for facets using wall-following algorithm.

This module implements border tracing that traces the outer edge of each facet
by following walls placed around border pixels. The algorithm uses a state machine
to track orientation and handles complex cases like corners, diagonals, and holes.
"""

from __future__ import annotations
from typing import List, Optional, Callable
from paintbynumbers.core.types import PathPoint, OrientationEnum
from paintbynumbers.structs.point import Point
from paintbynumbers.structs.typed_arrays import BooleanArray2D
from paintbynumbers.processing.facetmanagement import Facet, FacetResult
from paintbynumbers.utils.boundary import is_in_bounds


class FacetBorderTracer:
    """Traces border paths of facets using wall-following algorithm.

    The algorithm imagines placing walls around the outer side of border points
    and follows these walls to create an ordered path of PathPoints with orientations.
    """

    @staticmethod
    def build_facet_border_paths(
        facet_result: FacetResult,
        on_update: Optional[Callable[[float], None]] = None
    ) -> None:
        """Build border paths for all facets in the result.

        Processes facets from largest to smallest to ensure consistent results.
        Each facet's borderPath will be populated with an ordered list of PathPoints.

        Args:
            facet_result: FacetResult containing facets to process
            on_update: Optional callback for progress updates (0.0 to 1.0)

        Example:
            >>> from paintbynumbers.processing.facetmanagement import FacetResult
            >>> facet_result = FacetResult()
            >>> # ... setup facets ...
            >>> FacetBorderTracer.build_facet_border_paths(facet_result)
            >>> # Now facet_result.facets[i].borderPath contains the traced path
        """
        count = 0
        border_mask = BooleanArray2D(facet_result.width, facet_result.height)

        # Sort by biggest facets first
        facet_processing_order = [
            f.id for f in facet_result.facets
            if f is not None
        ]
        facet_processing_order.sort(
            key=lambda fid: facet_result.facets[fid].pointCount,
            reverse=True
        )

        for fidx, facet_id in enumerate(facet_processing_order):
            f = facet_result.facets[facet_id]
            if f is None:
                continue

            # Set border mask
            for bp in f.borderPoints:
                border_mask.set(bp.x, bp.y, True)

            # Keep track of which walls are already set on each pixel
            # xWall.get(x, y) is the left wall of point x,y
            # The right wall of x,y can be set with xWall.set(x+1, y)
            # Analogous for horizontal walls in yWall
            x_wall = BooleanArray2D(facet_result.width + 1, facet_result.height + 1)
            y_wall = BooleanArray2D(facet_result.width + 1, facet_result.height + 1)

            # Skip facets with no border points
            if len(f.borderPoints) == 0:
                f.borderPath = []
                continue

            # Find a border point that edges with the bounding box
            # This is definitely on the outer side
            border_start_index = -1
            for i, bp in enumerate(f.borderPoints):
                if ((bp.x == f.bbox.minX or bp.x == f.bbox.maxX) or
                    (bp.y == f.bbox.minY or bp.y == f.bbox.maxY)):
                    border_start_index = i
                    break

            if border_start_index == -1:
                # Shouldn't happen, but use first point as fallback
                border_start_index = 0

            # Determine the starting point orientation (the outside of facet)
            start_point = f.borderPoints[border_start_index]
            pt = PathPoint(start_point.x, start_point.y, OrientationEnum.Left)

            # Check L T R B to find which side is outside
            if (not is_in_bounds(pt.x - 1, pt.y, facet_result.width, facet_result.height) or
                facet_result.facetMap.get(pt.x - 1, pt.y) != f.id):
                pt.orientation = OrientationEnum.Left
            elif (not is_in_bounds(pt.x, pt.y - 1, facet_result.width, facet_result.height) or
                  facet_result.facetMap.get(pt.x, pt.y - 1) != f.id):
                pt.orientation = OrientationEnum.Top
            elif (not is_in_bounds(pt.x + 1, pt.y, facet_result.width, facet_result.height) or
                  facet_result.facetMap.get(pt.x + 1, pt.y) != f.id):
                pt.orientation = OrientationEnum.Right
            elif (not is_in_bounds(pt.x, pt.y + 1, facet_result.width, facet_result.height) or
                  facet_result.facetMap.get(pt.x, pt.y + 1) != f.id):
                pt.orientation = OrientationEnum.Bottom

            # Build the border path from that point
            path = FacetBorderTracer._get_path(pt, facet_result, f, border_mask, x_wall, y_wall)
            f.borderPath = path

            count += 1
            if count % 100 == 0 and on_update is not None:
                on_update(fidx / len(facet_processing_order))

        if on_update is not None:
            on_update(1.0)

    @staticmethod
    def _get_path(
        pt: PathPoint,
        facet_result: FacetResult,
        f: Facet,
        border_mask: BooleanArray2D,
        x_wall: BooleanArray2D,
        y_wall: BooleanArray2D
    ) -> List[PathPoint]:
        """Return a border path starting from the given point.

        Uses a wall-following algorithm with a state machine. The algorithm
        checks rotations first, then straight movement, then diagonal movement
        to ensure tight turns are always taken.

        Args:
            pt: Starting PathPoint with orientation
            facet_result: FacetResult containing facet map
            f: Facet being traced
            border_mask: Boolean mask of border points
            x_wall: Boolean array tracking set vertical walls
            y_wall: Boolean array tracking set horizontal walls

        Returns:
            List of PathPoints forming a closed border loop
        """
        finished = False
        path: List[PathPoint] = []
        FacetBorderTracer._add_point_to_path(path, pt, x_wall, y_wall)

        while not finished:
            possible_next_points: List[PathPoint] = []

            # Process based on current orientation
            if pt.orientation == OrientationEnum.Left:
                FacetBorderTracer._check_left_orientation(
                    pt, f, facet_result, border_mask, x_wall, y_wall, possible_next_points
                )
            elif pt.orientation == OrientationEnum.Top:
                FacetBorderTracer._check_top_orientation(
                    pt, f, facet_result, border_mask, x_wall, y_wall, possible_next_points
                )
            elif pt.orientation == OrientationEnum.Right:
                FacetBorderTracer._check_right_orientation(
                    pt, f, facet_result, border_mask, x_wall, y_wall, possible_next_points
                )
            elif pt.orientation == OrientationEnum.Bottom:
                FacetBorderTracer._check_bottom_orientation(
                    pt, f, facet_result, border_mask, x_wall, y_wall, possible_next_points
                )

            if len(possible_next_points) > 0:
                pt = possible_next_points[0]
                FacetBorderTracer._add_point_to_path(path, pt, x_wall, y_wall)
            else:
                finished = True

        # Clear the walls for reuse
        for path_point in path:
            if path_point.orientation == OrientationEnum.Left:
                x_wall.set(path_point.x, path_point.y, False)
            elif path_point.orientation == OrientationEnum.Top:
                y_wall.set(path_point.x, path_point.y, False)
            elif path_point.orientation == OrientationEnum.Right:
                x_wall.set(path_point.x + 1, path_point.y, False)
            elif path_point.orientation == OrientationEnum.Bottom:
                y_wall.set(path_point.x, path_point.y + 1, False)

        return path

    @staticmethod
    def _add_point_to_path(
        path: List[PathPoint],
        pt: PathPoint,
        x_wall: BooleanArray2D,
        y_wall: BooleanArray2D
    ) -> None:
        """Add a point to the border path and set the corresponding wall.

        Args:
            path: Path list to append to
            pt: PathPoint to add
            x_wall: Vertical wall tracker
            y_wall: Horizontal wall tracker
        """
        path.append(pt)

        if pt.orientation == OrientationEnum.Left:
            x_wall.set(pt.x, pt.y, True)
        elif pt.orientation == OrientationEnum.Top:
            y_wall.set(pt.x, pt.y, True)
        elif pt.orientation == OrientationEnum.Right:
            x_wall.set(pt.x + 1, pt.y, True)
        elif pt.orientation == OrientationEnum.Bottom:
            y_wall.set(pt.x, pt.y + 1, True)

    @staticmethod
    def _check_left_orientation(
        pt: PathPoint,
        f: Facet,
        facet_result: FacetResult,
        border_mask: BooleanArray2D,
        x_wall: BooleanArray2D,
        y_wall: BooleanArray2D,
        possible_next_points: List[PathPoint]
    ) -> None:
        """Check possible next points when facing left."""
        # Check rotate to top
        if (((pt.y - 1 >= 0 and facet_result.facetMap.get(pt.x, pt.y - 1) != f.id) or pt.y - 1 < 0)
            and not y_wall.get(pt.x, pt.y)):
            possible_next_points.append(PathPoint(pt.x, pt.y, OrientationEnum.Top))

        # Check rotate to bottom
        if (((pt.y + 1 < facet_result.height and facet_result.facetMap.get(pt.x, pt.y + 1) != f.id)
             or pt.y + 1 >= facet_result.height)
            and not y_wall.get(pt.x, pt.y + 1)):
            possible_next_points.append(PathPoint(pt.x, pt.y, OrientationEnum.Bottom))

        # Check upwards
        if (pt.y - 1 >= 0
            and facet_result.facetMap.get(pt.x, pt.y - 1) == f.id
            and (pt.x - 1 < 0 or facet_result.facetMap.get(pt.x - 1, pt.y - 1) != f.id)
            and border_mask.get(pt.x, pt.y - 1)
            and not x_wall.get(pt.x, pt.y - 1)):
            possible_next_points.append(PathPoint(pt.x, pt.y - 1, OrientationEnum.Left))

        # Check downwards
        if (pt.y + 1 < facet_result.height
            and facet_result.facetMap.get(pt.x, pt.y + 1) == f.id
            and (pt.x - 1 < 0 or facet_result.facetMap.get(pt.x - 1, pt.y + 1) != f.id)
            and border_mask.get(pt.x, pt.y + 1)
            and not x_wall.get(pt.x, pt.y + 1)):
            possible_next_points.append(PathPoint(pt.x, pt.y + 1, OrientationEnum.Left))

        # Check left upwards (diagonal)
        if (pt.y - 1 >= 0 and pt.x - 1 >= 0
            and facet_result.facetMap.get(pt.x - 1, pt.y - 1) == f.id
            and border_mask.get(pt.x - 1, pt.y - 1)
            and not y_wall.get(pt.x - 1, pt.y - 1 + 1)
            and not y_wall.get(pt.x, pt.y)):
            possible_next_points.append(PathPoint(pt.x - 1, pt.y - 1, OrientationEnum.Bottom))

        # Check left downwards (diagonal)
        if (pt.y + 1 < facet_result.height and pt.x - 1 >= 0
            and facet_result.facetMap.get(pt.x - 1, pt.y + 1) == f.id
            and border_mask.get(pt.x - 1, pt.y + 1)
            and not y_wall.get(pt.x - 1, pt.y + 1)
            and not y_wall.get(pt.x, pt.y + 1)):
            possible_next_points.append(PathPoint(pt.x - 1, pt.y + 1, OrientationEnum.Top))

    @staticmethod
    def _check_top_orientation(
        pt: PathPoint,
        f: Facet,
        facet_result: FacetResult,
        border_mask: BooleanArray2D,
        x_wall: BooleanArray2D,
        y_wall: BooleanArray2D,
        possible_next_points: List[PathPoint]
    ) -> None:
        """Check possible next points when facing top."""
        # Check rotate to left
        if (((pt.x - 1 >= 0 and facet_result.facetMap.get(pt.x - 1, pt.y) != f.id) or pt.x - 1 < 0)
            and not x_wall.get(pt.x, pt.y)):
            possible_next_points.append(PathPoint(pt.x, pt.y, OrientationEnum.Left))

        # Check rotate to right
        if (((pt.x + 1 < facet_result.width and facet_result.facetMap.get(pt.x + 1, pt.y) != f.id)
             or pt.x + 1 >= facet_result.width)
            and not x_wall.get(pt.x + 1, pt.y)):
            possible_next_points.append(PathPoint(pt.x, pt.y, OrientationEnum.Right))

        # Check leftwards
        if (pt.x - 1 >= 0
            and facet_result.facetMap.get(pt.x - 1, pt.y) == f.id
            and (pt.y - 1 < 0 or facet_result.facetMap.get(pt.x - 1, pt.y - 1) != f.id)
            and border_mask.get(pt.x - 1, pt.y)
            and not y_wall.get(pt.x - 1, pt.y)):
            possible_next_points.append(PathPoint(pt.x - 1, pt.y, OrientationEnum.Top))

        # Check rightwards
        if (pt.x + 1 < facet_result.width
            and facet_result.facetMap.get(pt.x + 1, pt.y) == f.id
            and (pt.y - 1 < 0 or facet_result.facetMap.get(pt.x + 1, pt.y - 1) != f.id)
            and border_mask.get(pt.x + 1, pt.y)
            and not y_wall.get(pt.x + 1, pt.y)):
            possible_next_points.append(PathPoint(pt.x + 1, pt.y, OrientationEnum.Top))

        # Check left upwards (diagonal)
        if (pt.y - 1 >= 0 and pt.x - 1 >= 0
            and facet_result.facetMap.get(pt.x - 1, pt.y - 1) == f.id
            and border_mask.get(pt.x - 1, pt.y - 1)
            and not x_wall.get(pt.x - 1 + 1, pt.y - 1)
            and not x_wall.get(pt.x, pt.y)):
            possible_next_points.append(PathPoint(pt.x - 1, pt.y - 1, OrientationEnum.Right))

        # Check right upwards (diagonal)
        if (pt.y - 1 >= 0 and pt.x + 1 < facet_result.width
            and facet_result.facetMap.get(pt.x + 1, pt.y - 1) == f.id
            and border_mask.get(pt.x + 1, pt.y - 1)
            and not x_wall.get(pt.x + 1, pt.y - 1)
            and not x_wall.get(pt.x + 1, pt.y)):
            possible_next_points.append(PathPoint(pt.x + 1, pt.y - 1, OrientationEnum.Left))

    @staticmethod
    def _check_right_orientation(
        pt: PathPoint,
        f: Facet,
        facet_result: FacetResult,
        border_mask: BooleanArray2D,
        x_wall: BooleanArray2D,
        y_wall: BooleanArray2D,
        possible_next_points: List[PathPoint]
    ) -> None:
        """Check possible next points when facing right."""
        # Check rotate to top
        if (((pt.y - 1 >= 0 and facet_result.facetMap.get(pt.x, pt.y - 1) != f.id) or pt.y - 1 < 0)
            and not y_wall.get(pt.x, pt.y)):
            possible_next_points.append(PathPoint(pt.x, pt.y, OrientationEnum.Top))

        # Check rotate to bottom
        if (((pt.y + 1 < facet_result.height and facet_result.facetMap.get(pt.x, pt.y + 1) != f.id)
             or pt.y + 1 >= facet_result.height)
            and not y_wall.get(pt.x, pt.y + 1)):
            possible_next_points.append(PathPoint(pt.x, pt.y, OrientationEnum.Bottom))

        # Check upwards
        if (pt.y - 1 >= 0
            and facet_result.facetMap.get(pt.x, pt.y - 1) == f.id
            and (pt.x + 1 >= facet_result.width or facet_result.facetMap.get(pt.x + 1, pt.y - 1) != f.id)
            and border_mask.get(pt.x, pt.y - 1)
            and not x_wall.get(pt.x + 1, pt.y - 1)):
            possible_next_points.append(PathPoint(pt.x, pt.y - 1, OrientationEnum.Right))

        # Check downwards
        if (pt.y + 1 < facet_result.height
            and facet_result.facetMap.get(pt.x, pt.y + 1) == f.id
            and (pt.x + 1 >= facet_result.width or facet_result.facetMap.get(pt.x + 1, pt.y + 1) != f.id)
            and border_mask.get(pt.x, pt.y + 1)
            and not x_wall.get(pt.x + 1, pt.y + 1)):
            possible_next_points.append(PathPoint(pt.x, pt.y + 1, OrientationEnum.Right))

        # Check right upwards (diagonal)
        if (pt.y - 1 >= 0 and pt.x + 1 < facet_result.width
            and facet_result.facetMap.get(pt.x + 1, pt.y - 1) == f.id
            and border_mask.get(pt.x + 1, pt.y - 1)
            and not y_wall.get(pt.x + 1, pt.y - 1 + 1)
            and not y_wall.get(pt.x, pt.y)):
            possible_next_points.append(PathPoint(pt.x + 1, pt.y - 1, OrientationEnum.Bottom))

        # Check right downwards (diagonal)
        if (pt.y + 1 < facet_result.height and pt.x + 1 < facet_result.width
            and facet_result.facetMap.get(pt.x + 1, pt.y + 1) == f.id
            and border_mask.get(pt.x + 1, pt.y + 1)
            and not y_wall.get(pt.x + 1, pt.y + 1)
            and not y_wall.get(pt.x, pt.y + 1)):
            possible_next_points.append(PathPoint(pt.x + 1, pt.y + 1, OrientationEnum.Top))

    @staticmethod
    def _check_bottom_orientation(
        pt: PathPoint,
        f: Facet,
        facet_result: FacetResult,
        border_mask: BooleanArray2D,
        x_wall: BooleanArray2D,
        y_wall: BooleanArray2D,
        possible_next_points: List[PathPoint]
    ) -> None:
        """Check possible next points when facing bottom."""
        # Check rotate to left
        if (((pt.x - 1 >= 0 and facet_result.facetMap.get(pt.x - 1, pt.y) != f.id) or pt.x - 1 < 0)
            and not x_wall.get(pt.x, pt.y)):
            possible_next_points.append(PathPoint(pt.x, pt.y, OrientationEnum.Left))

        # Check rotate to right
        if (((pt.x + 1 < facet_result.width and facet_result.facetMap.get(pt.x + 1, pt.y) != f.id)
             or pt.x + 1 >= facet_result.width)
            and not x_wall.get(pt.x + 1, pt.y)):
            possible_next_points.append(PathPoint(pt.x, pt.y, OrientationEnum.Right))

        # Check leftwards
        if (pt.x - 1 >= 0
            and facet_result.facetMap.get(pt.x - 1, pt.y) == f.id
            and (pt.y + 1 >= facet_result.height or facet_result.facetMap.get(pt.x - 1, pt.y + 1) != f.id)
            and border_mask.get(pt.x - 1, pt.y)
            and not y_wall.get(pt.x - 1, pt.y + 1)):
            possible_next_points.append(PathPoint(pt.x - 1, pt.y, OrientationEnum.Bottom))

        # Check rightwards
        if (pt.x + 1 < facet_result.width
            and facet_result.facetMap.get(pt.x + 1, pt.y) == f.id
            and (pt.y + 1 >= facet_result.height or facet_result.facetMap.get(pt.x + 1, pt.y + 1) != f.id)
            and border_mask.get(pt.x + 1, pt.y)
            and not y_wall.get(pt.x + 1, pt.y + 1)):
            possible_next_points.append(PathPoint(pt.x + 1, pt.y, OrientationEnum.Bottom))

        # Check left downwards (diagonal)
        if (pt.y + 1 < facet_result.height and pt.x - 1 >= 0
            and facet_result.facetMap.get(pt.x - 1, pt.y + 1) == f.id
            and border_mask.get(pt.x - 1, pt.y + 1)
            and not x_wall.get(pt.x - 1 + 1, pt.y + 1)
            and not x_wall.get(pt.x, pt.y)):
            possible_next_points.append(PathPoint(pt.x - 1, pt.y + 1, OrientationEnum.Right))

        # Check right downwards (diagonal)
        if (pt.y + 1 < facet_result.height and pt.x + 1 < facet_result.width
            and facet_result.facetMap.get(pt.x + 1, pt.y + 1) == f.id
            and border_mask.get(pt.x + 1, pt.y + 1)
            and not x_wall.get(pt.x + 1, pt.y + 1)
            and not x_wall.get(pt.x + 1, pt.y)):
            possible_next_points.append(PathPoint(pt.x + 1, pt.y + 1, OrientationEnum.Left))
