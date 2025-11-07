"""Facet reduction for merging small or similar facets.

This module handles the merging of small facets into their neighbors to
reduce the total number of facets and create cleaner paint-by-numbers output.
"""

from __future__ import annotations
from typing import List, Set, Dict, Optional
from paintbynumbers.core.types import RGB
from paintbynumbers.structs.point import Point
from paintbynumbers.structs.typed_arrays import BooleanArray2D, Uint8Array2D
from paintbynumbers.processing.facetmanagement import Facet, FacetResult
from paintbynumbers.processing.facetbuilder import FacetBuilder


class FacetReducer:
    """Facet reduction utilities for merging small facets.

    Provides methods to remove facets below a size threshold by merging
    them with neighboring facets. Uses Voronoi-like distance-based
    allocation to distribute pixels to neighbors.
    """

    @staticmethod
    def reduce_facets(
        smaller_than: int,
        remove_facets_from_large_to_small: bool,
        maximum_number_of_facets: Optional[int],
        colors_by_index: List[RGB],
        facet_result: FacetResult,
        img_color_indices: Uint8Array2D
    ) -> None:
        """Remove all facets with pointCount smaller than the given threshold.

        Process facets from large to small for better consistency with the
        original image. Small facets act as boundaries for large merges,
        keeping them in place.

        Args:
            smaller_than: Remove facets with fewer pixels than this
            remove_facets_from_large_to_small: Process order (True = large first)
            maximum_number_of_facets: Hard limit on facet count
            colors_by_index: Array of RGB colors
            facet_result: Facet result to modify
            img_color_indices: Color index map to update

        Example:
            >>> FacetReducer.reduce_facets(
            ...     smaller_than=10,
            ...     remove_facets_from_large_to_small=True,
            ...     maximum_number_of_facets=100,
            ...     colors_by_index=colors,
            ...     facet_result=result,
            ...     img_color_indices=color_map
            ... )
        """
        visited_cache = BooleanArray2D(facet_result.width, facet_result.height)

        # Build color distance matrix
        color_distances = FacetReducer._build_color_distance_matrix(colors_by_index)

        # Process facets from large to small
        facet_processing_order = [
            f.id for f in facet_result.facets if f is not None
        ]
        facet_processing_order.sort(
            key=lambda fid: facet_result.facets[fid].pointCount,  # type: ignore
            reverse=True
        )

        if not remove_facets_from_large_to_small:
            facet_processing_order.reverse()

        # First pass: remove facets below threshold
        for fidx in facet_processing_order:
            f = facet_result.facets[fidx]
            if f is not None and f.pointCount < smaller_than:
                FacetReducer._delete_facet(
                    f.id,
                    facet_result,
                    img_color_indices,
                    color_distances,
                    visited_cache
                )

        # Second pass: enforce maximum facet count
        facet_count = sum(1 for f in facet_result.facets if f is not None)
        while maximum_number_of_facets is not None and facet_count > maximum_number_of_facets:
            # Re-evaluate order to remove smallest
            facet_processing_order = [
                f.id for f in facet_result.facets if f is not None
            ]
            facet_processing_order.sort(
                key=lambda fid: facet_result.facets[fid].pointCount,  # type: ignore
                reverse=False  # Smallest first
            )

            facet_to_remove = facet_result.facets[facet_processing_order[0]]
            if facet_to_remove is not None:
                FacetReducer._delete_facet(
                    facet_to_remove.id,
                    facet_result,
                    img_color_indices,
                    color_distances,
                    visited_cache
                )

            facet_count = sum(1 for f in facet_result.facets if f is not None)

    @staticmethod
    def _delete_facet(
        facet_id_to_remove: int,
        facet_result: FacetResult,
        img_color_indices: Uint8Array2D,
        color_distances: List[List[float]],
        visited_array_cache: BooleanArray2D
    ) -> None:
        """Delete a facet by moving its pixels to nearest neighbors.

        All points belonging to the facet are moved to the nearest neighbor
        facet based on distance to border points. This results in Voronoi-like
        filling of the void.

        Args:
            facet_id_to_remove: ID of facet to remove
            facet_result: Facet result container
            img_color_indices: Color index map
            color_distances: Color distance matrix
            visited_array_cache: Reusable visited array
        """
        facet_to_remove = facet_result.facets[facet_id_to_remove]
        if facet_to_remove is None:
            return  # Already removed

        # Ensure neighbor list is up to date
        if facet_to_remove.neighbourFacetsIsDirty:
            builder = FacetBuilder()
            builder.build_facet_neighbour(facet_to_remove, facet_result)

        if facet_to_remove.neighbourFacets and len(facet_to_remove.neighbourFacets) > 0:
            # Iterate over bounding box and reallocate pixels
            for j in range(facet_to_remove.bbox.minY, facet_to_remove.bbox.maxY + 1):
                for i in range(facet_to_remove.bbox.minX, facet_to_remove.bbox.maxX + 1):
                    if facet_result.facetMap.get(i, j) == facet_to_remove.id:  # type: ignore
                        closest_neighbour = FacetReducer._get_closest_neighbour_for_pixel(
                            facet_to_remove,
                            facet_result,
                            i,
                            j,
                            color_distances
                        )
                        if closest_neighbour != -1:
                            # Copy color of closest neighbor
                            img_color_indices.set(
                                i, j,
                                facet_result.facets[closest_neighbour].color  # type: ignore
                            )

        # Rebuild all affected neighbor facets
        FacetReducer._rebuild_for_facet_change(
            visited_array_cache,
            facet_to_remove,
            img_color_indices,
            facet_result
        )

        # Mark facet as deleted
        facet_result.facets[facet_to_remove.id] = None

    @staticmethod
    def _get_closest_neighbour_for_pixel(
        facet_to_remove: Facet,
        facet_result: FacetResult,
        x: int,
        y: int,
        color_distances: List[List[float]]
    ) -> int:
        """Determine closest neighbor for a pixel.

        Based on distance to neighbor border points, and when tied,
        closest color distance.

        Args:
            facet_to_remove: Facet being removed
            facet_result: Facet result container
            x: Pixel x coordinate
            y: Pixel y coordinate
            color_distances: Color distance matrix

        Returns:
            Facet ID of closest neighbor, or -1 if none found
        """
        closest_neighbour = -1
        min_distance = float('inf')
        min_color_distance = float('inf')

        # Ensure neighbor list is up to date
        if facet_to_remove.neighbourFacetsIsDirty:
            builder = FacetBuilder()
            builder.build_facet_neighbour(facet_to_remove, facet_result)

        if not facet_to_remove.neighbourFacets:
            return -1

        # Check each neighbor
        for neighbour_idx in facet_to_remove.neighbourFacets:
            neighbour = facet_result.facets[neighbour_idx]
            if neighbour is not None:
                for bpt in neighbour.borderPoints:
                    distance = bpt.distance_to(Point(x, y))

                    if distance < min_distance:
                        min_distance = distance
                        closest_neighbour = neighbour_idx
                        min_color_distance = float('inf')  # Reset color distance
                    elif distance == min_distance:
                        # Tie: use color distance
                        color_distance = color_distances[facet_to_remove.color][neighbour.color]
                        if color_distance < min_color_distance:
                            min_color_distance = color_distance
                            closest_neighbour = neighbour_idx

        return closest_neighbour

    @staticmethod
    def _rebuild_for_facet_change(
        visited_array_cache: BooleanArray2D,
        facet_to_remove: Facet,
        img_color_indices: Uint8Array2D,
        facet_result: FacetResult
    ) -> None:
        """Rebuild neighbor facets after a facet change.

        Args:
            visited_array_cache: Reusable visited array
            facet_to_remove: Facet that was removed/changed
            img_color_indices: Color index map
            facet_result: Facet result container
        """
        FacetReducer._rebuild_changed_neighbour_facets(
            visited_array_cache,
            facet_to_remove,
            img_color_indices,
            facet_result
        )

        # Sanity check: ensure all points were reallocated
        needs_to_rebuild = False
        for y in range(facet_to_remove.bbox.minY, facet_to_remove.bbox.maxY + 1):
            for x in range(facet_to_remove.bbox.minX, facet_to_remove.bbox.maxX + 1):
                if facet_result.facetMap.get(x, y) == facet_to_remove.id:  # type: ignore
                    needs_to_rebuild = True
                    # Try to merge with any direct neighbor
                    if (x - 1 >= 0 and
                        facet_result.facetMap.get(x - 1, y) != facet_to_remove.id and  # type: ignore
                        facet_result.facets[facet_result.facetMap.get(x - 1, y)] is not None):  # type: ignore
                        img_color_indices.set(
                            x, y,
                            facet_result.facets[facet_result.facetMap.get(x - 1, y)].color  # type: ignore
                        )
                    elif (y - 1 >= 0 and
                          facet_result.facetMap.get(x, y - 1) != facet_to_remove.id and  # type: ignore
                          facet_result.facets[facet_result.facetMap.get(x, y - 1)] is not None):  # type: ignore
                        img_color_indices.set(
                            x, y,
                            facet_result.facets[facet_result.facetMap.get(x, y - 1)].color  # type: ignore
                        )
                    elif (x + 1 < facet_result.width and
                          facet_result.facetMap.get(x + 1, y) != facet_to_remove.id and  # type: ignore
                          facet_result.facets[facet_result.facetMap.get(x + 1, y)] is not None):  # type: ignore
                        img_color_indices.set(
                            x, y,
                            facet_result.facets[facet_result.facetMap.get(x + 1, y)].color  # type: ignore
                        )
                    elif (y + 1 < facet_result.height and
                          facet_result.facetMap.get(x, y + 1) != facet_to_remove.id and  # type: ignore
                          facet_result.facets[facet_result.facetMap.get(x, y + 1)] is not None):  # type: ignore
                        img_color_indices.set(
                            x, y,
                            facet_result.facets[facet_result.facetMap.get(x, y + 1)].color  # type: ignore
                        )

        # Rebuild again if needed
        if needs_to_rebuild:
            FacetReducer._rebuild_changed_neighbour_facets(
                visited_array_cache,
                facet_to_remove,
                img_color_indices,
                facet_result
            )

    @staticmethod
    def _rebuild_changed_neighbour_facets(
        visited_array_cache: BooleanArray2D,
        facet_to_remove: Facet,
        img_color_indices: Uint8Array2D,
        facet_result: FacetResult
    ) -> None:
        """Rebuild the changed neighbor facets.

        Args:
            visited_array_cache: Reusable visited array
            facet_to_remove: Facet that triggered the rebuild
            img_color_indices: Color index map
            facet_result: Facet result container
        """
        changed_neighbours_set: Set[int] = set()
        builder = FacetBuilder()

        if facet_to_remove.neighbourFacetsIsDirty:
            builder.build_facet_neighbour(facet_to_remove, facet_result)

        if not facet_to_remove.neighbourFacets:
            return

        # Track all facets that need neighbour list updates
        for neighbour_idx in facet_to_remove.neighbourFacets:
            neighbour = facet_result.facets[neighbour_idx]
            if neighbour is not None:
                changed_neighbours_set.add(neighbour_idx)

                if neighbour.neighbourFacetsIsDirty:
                    builder.build_facet_neighbour(neighbour, facet_result)

                if neighbour.neighbourFacets:
                    for n in neighbour.neighbourFacets:
                        changed_neighbours_set.add(n)

                # Rebuild the neighbor facet
                if len(neighbour.borderPoints) > 0:
                    new_facet = builder.build_facet(
                        neighbour_idx,
                        neighbour.color,
                        neighbour.borderPoints[0].x,
                        neighbour.borderPoints[0].y,
                        visited_array_cache,
                        img_color_indices,
                        facet_result
                    )
                    facet_result.facets[neighbour_idx] = new_facet

                    # If facet has 0 points, it merged with another - remove it
                    if new_facet.pointCount == 0:
                        facet_result.facets[neighbour_idx] = None

        # Reset visited array for all neighbors
        for neighbour_idx in facet_to_remove.neighbourFacets:
            neighbour = facet_result.facets[neighbour_idx]
            if neighbour is not None:
                for y in range(neighbour.bbox.minY, neighbour.bbox.maxY + 1):
                    for x in range(neighbour.bbox.minX, neighbour.bbox.maxX + 1):
                        if facet_result.facetMap.get(x, y) == neighbour.id:  # type: ignore
                            visited_array_cache.set(x, y, False)

        # Mark neighbor arrays as dirty (defer rebuilding)
        for k in changed_neighbours_set:
            f = facet_result.facets[k]
            if f is not None:
                f.neighbourFacets = None
                f.neighbourFacetsIsDirty = True

    @staticmethod
    def _build_color_distance_matrix(colors_by_index: List[RGB]) -> List[List[float]]:
        """Build a distance matrix for each color to each other.

        Args:
            colors_by_index: List of RGB colors

        Returns:
            2D matrix where [i][j] is distance from color i to color j
        """
        n = len(colors_by_index)
        color_distances: List[List[float]] = [[0.0] * n for _ in range(n)]

        for j in range(n):
            for i in range(j, n):
                c1 = colors_by_index[j]
                c2 = colors_by_index[i]
                distance = ((c1[0] - c2[0]) ** 2 +
                           (c1[1] - c2[1]) ** 2 +
                           (c1[2] - c2[2]) ** 2) ** 0.5

                color_distances[i][j] = distance
                color_distances[j][i] = distance

        return color_distances
