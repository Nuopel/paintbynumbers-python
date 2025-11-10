"""Label placement for facets using pole of inaccessibility algorithm.

This module determines optimal label positions for facets by finding the point
furthest from all edges (pole of inaccessibility) where labels have maximum room.
"""

from __future__ import annotations
from typing import List, Optional, Callable
from paintbynumbers.structs.point import Point
from paintbynumbers.structs.boundingbox import BoundingBox
from paintbynumbers.processing.facetmanagement import Facet, FacetResult
from paintbynumbers.processing.facetbuilder import FacetBuilder
from paintbynumbers.algorithms.polylabel import polylabel, _point_to_polygon_dist
import math


class FacetLabelPlacer:
    """Determines optimal label positions for facets.

    Uses the polylabel algorithm to find the pole of inaccessibility (the point
    furthest from all edges) where labels have the most room. Handles inner facets
    by treating neighbor facets that fall completely inside as holes.
    """

    @staticmethod
    def build_facet_label_bounds(
        facet_result: FacetResult,
        on_update: Optional[Callable[[float], None]] = None
    ) -> None:
        """Build label bounds for all facets.

        For each facet, finds the optimal label position using the pole of
        inaccessibility algorithm. Accounts for neighbor facets that fall inside
        the current facet as exclusion zones.

        Args:
            facet_result: FacetResult containing facets with border segments
            on_update: Optional callback for progress updates (0.0 to 1.0)

        Example:
            >>> from paintbynumbers.processing.facetmanagement import FacetResult
            >>> facet_result = FacetResult()
            >>> # ... setup facets with border segments ...
            >>> FacetLabelPlacer.build_facet_label_bounds(facet_result)
            >>> # Now facet_result.facets[i].labelBounds contains the label area
        """
        count = 0

        for f in facet_result.facets:
            if f is None:
                count += 1
                continue

            poly_rings: List[List[tuple]] = []

            # Get border path from segments (may be smoothed)
            border_path = f.get_full_path_from_border_segments(use_walls=True)

            # Convert Points to tuples for polylabel
            border_path_tuples = [(p.x, p.y) for p in border_path]

            # Outer path must be first ring
            poly_rings.append(border_path_tuples)
            only_outer_ring = [border_path_tuples]

            # Add all neighbors that fall completely inside as inner rings
            # These are exclusion zones where labels cannot be placed
            if f.neighbourFacetsIsDirty:
                builder = FacetBuilder()
                builder.build_facet_neighbour(f, facet_result)

            if f.neighbourFacets is not None:
                for neighbour_idx in f.neighbourFacets:
                    if facet_result.facets[neighbour_idx] is None:
                        continue

                    neighbour_path = facet_result.facets[neighbour_idx].get_full_path_from_border_segments(use_walls=True)
                    # Convert to tuples
                    neighbour_path_tuples = [(p.x, p.y) for p in neighbour_path]

                    falls_inside = FacetLabelPlacer._does_neighbour_fall_inside_current_facet(
                        neighbour_path, f, only_outer_ring
                    )

                    if falls_inside:
                        poly_rings.append(neighbour_path_tuples)

            # Find pole of inaccessibility
            result = polylabel(poly_rings)

            # Create label bounds as inner square within the circle
            # The circle has radius = result.distance
            # Inner square has side length = 2 * sqrt(2) * radius
            f.labelBounds = BoundingBox()
            inner_padding = 2 * math.sqrt(2 * result.distance)
            # result.pt is a tuple (x, y)
            pt_x, pt_y = result.pt
            f.labelBounds.minX = int(pt_x - inner_padding)
            f.labelBounds.maxX = int(pt_x + inner_padding)
            f.labelBounds.minY = int(pt_y - inner_padding)
            f.labelBounds.maxY = int(pt_y + inner_padding)

            count += 1
            if count % 100 == 0 and on_update is not None:
                on_update(count / len(facet_result.facets))

        if on_update is not None:
            on_update(1.0)

    @staticmethod
    def _does_neighbour_fall_inside_current_facet(
        neighbour_path: List[Point],
        f: Facet,
        only_outer_ring: List[List[Point]]
    ) -> bool:
        """Check if a neighbor's border path falls completely inside current facet.

        Args:
            neighbour_path: Border path of the neighbor facet
            f: Current facet
            only_outer_ring: List containing only the outer border ring

        Returns:
            True if all points of neighbor path are inside current facet
        """
        falls_inside = True

        # Fast bbox test first
        for pt in neighbour_path:
            if not (f.bbox.minX <= pt.x <= f.bbox.maxX and
                    f.bbox.minY <= pt.y <= f.bbox.maxY):
                falls_inside = False
                break

        # If bbox test passed, do more expensive point-in-polygon test
        if falls_inside:
            for pt in neighbour_path:
                distance = _point_to_polygon_dist(pt.x, pt.y, only_outer_ring)
                if distance < 0:
                    # Point falls outside
                    falls_inside = False
                    break

        return falls_inside
