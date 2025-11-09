"""Facet reduction with BATCH PROCESSING + HOLE FILLING.

This version prevents holes by:
1. Tracking orphaned pixels (those whose neighbors are all being removed)
2. Expanding search radius to find valid neighbors
3. Filling holes with nearest valid facets
"""

from __future__ import annotations
from typing import List, Set, Dict, Optional, Callable, Tuple
import time
import numpy as np
from paintbynumbers.core.types import RGB
from paintbynumbers.structs.point import Point
from paintbynumbers.structs.typed_arrays import BooleanArray2D, Uint8Array2D
from paintbynumbers.processing.facetmanagement import Facet, FacetResult
from paintbynumbers.processing.facetbuilder import FacetBuilder

RGB = Tuple[int, int, int]


class FacetReducer:
    """Batch-optimized facet reduction with hole prevention."""

    @staticmethod
    def reduce_facets(
            smaller_than: int,
            remove_facets_from_large_to_small: bool,
            maximum_number_of_facets: Optional[int],
            colors_by_index: List[RGB],
            facet_result: FacetResult,
            img_color_indices: Uint8Array2D,
            on_update: Optional[Callable[[float], None]] = None
    ) -> None:
        """Remove facets using batch processing with hole prevention."""
        if smaller_than <= 0 and maximum_number_of_facets is None:
            if on_update is not None:
                on_update(1.0)
            return

        width, height = facet_result.width, facet_result.height
        facets = facet_result.facets

        visited_cache = BooleanArray2D(width, height)
        color_distances = FacetReducer._build_color_distance_matrix(colors_by_index)

        # Progress throttling
        last_progress_time = time.time()

        def _maybe_update(progress: float) -> None:
            nonlocal last_progress_time
            if on_update is None:
                return
            now = time.time()
            if now - last_progress_time >= 0.5:
                last_progress_time = now
                on_update(max(0.0, min(1.0, progress)))

        # PHASE 1: Identify all facets to remove (20%)
        _maybe_update(0.0)
        facets_to_remove = FacetReducer._identify_facets_to_remove(
            facets,
            smaller_than,
            maximum_number_of_facets,
            remove_facets_from_large_to_small
        )

        if not facets_to_remove:
            if on_update is not None:
                on_update(1.0)
            return

        _maybe_update(0.2)

        # PHASE 2: Batch reassign pixels with hole tracking (50%)
        affected_facets, orphaned_pixels = FacetReducer._batch_reassign_pixels(
            facets_to_remove,
            facet_result,
            img_color_indices,
            color_distances,
            lambda p: _maybe_update(0.2 + 0.5 * p)
        )

        _maybe_update(0.7)

        # PHASE 2.5: Fill holes - critical step! (10%)
        if orphaned_pixels:
            additional_affected = FacetReducer._fill_holes(
                orphaned_pixels,
                facets_to_remove,
                facet_result,
                img_color_indices,
                color_distances
            )
            affected_facets.update(additional_affected)

        _maybe_update(0.8)

        # PHASE 3: Single rebuild pass (15%)
        FacetReducer._batch_rebuild_affected_facets(
            affected_facets,
            facets_to_remove,
            facet_result,
            img_color_indices,
            visited_cache
        )

        _maybe_update(0.95)

        # PHASE 4: Mark removed facets as None (5%)
        for fid in facets_to_remove:
            facets[fid] = None

        if on_update is not None:
            on_update(1.0)

    @staticmethod
    def _identify_facets_to_remove(
            facets: List[Optional[Facet]],
            smaller_than: int,
            maximum_number_of_facets: Optional[int],
            remove_from_large_to_small: bool
    ) -> Set[int]:
        """Identify all facets that need to be removed upfront."""
        to_remove = set()

        valid_facets = [(f.id, f.pointCount) for f in facets if f is not None]

        if not valid_facets:
            return to_remove

        # Phase 1: Mark facets below size threshold
        if smaller_than > 0:
            for fid, count in valid_facets:
                if count < smaller_than:
                    to_remove.add(fid)

        # Phase 2: Enforce maximum facet count
        if maximum_number_of_facets is not None:
            remaining_facets = [(fid, count) for fid, count in valid_facets
                                if fid not in to_remove]

            if len(remaining_facets) > maximum_number_of_facets:
                remaining_facets.sort(key=lambda x: x[1])
                to_remove_count = len(remaining_facets) - maximum_number_of_facets

                for i in range(to_remove_count):
                    to_remove.add(remaining_facets[i][0])

        return to_remove

    @staticmethod
    def _batch_reassign_pixels(
            facets_to_remove: Set[int],
            facet_result: FacetResult,
            img_color_indices: Uint8Array2D,
            color_distances: np.ndarray,
            on_progress: Optional[Callable[[float], None]] = None
    ) -> Tuple[Set[int], List[Tuple[int, int]]]:
        """
        Reassign pixels and track orphaned ones.
        Returns (affected_facets, orphaned_pixels).
        """
        facets = facet_result.facets
        facet_map = facet_result.facetMap
        affected_facets = set()
        orphaned_pixels = []  # List of (x, y) that couldn't find valid neighbors

        # Build neighbor information
        builder = FacetBuilder()
        for fid in facets_to_remove:
            facet = facets[fid]
            if facet is None:
                continue
            if facet.neighbourFacetsIsDirty:
                builder.build_facet_neighbour(facet, facet_result)

        # Collect pixels and find assignments
        total_pixels = 0
        pixel_assignments = []

        for fid in facets_to_remove:
            facet = facets[fid]
            if facet is None:
                continue

            min_x, max_x = facet.bbox.minX, facet.bbox.maxX
            min_y, max_y = facet.bbox.minY, facet.bbox.maxY

            for y in range(min_y, max_y + 1):
                for x in range(min_x, max_x + 1):
                    if facet_map.get(x, y) == fid:
                        total_pixels += 1

                        closest_neigh_id = FacetReducer._get_closest_valid_neighbour(
                            facet,
                            facets_to_remove,
                            facet_result,
                            x,
                            y,
                            color_distances
                        )

                        if closest_neigh_id != -1:
                            neigh = facets[closest_neigh_id]
                            if neigh is not None:
                                pixel_assignments.append((x, y, neigh.color))
                                affected_facets.add(closest_neigh_id)
                        else:
                            # No valid neighbor found - mark as orphaned
                            orphaned_pixels.append((x, y))

        # Apply assignments
        processed = 0
        for x, y, new_color in pixel_assignments:
            img_color_indices.set(x, y, new_color)
            processed += 1

            if on_progress is not None and processed % 1000 == 0:
                on_progress(processed / max(1, total_pixels))

        if on_progress is not None:
            on_progress(1.0)

        return affected_facets, orphaned_pixels

    @staticmethod
    def _fill_holes(
            orphaned_pixels: List[Tuple[int, int]],
            facets_being_removed: Set[int],
            facet_result: FacetResult,
            img_color_indices: Uint8Array2D,
            color_distances: np.ndarray
    ) -> Set[int]:
        """
        Fill holes by finding nearest valid facet with expanded search radius.
        Returns set of newly affected facets.
        """
        if not orphaned_pixels:
            return set()

        facets = facet_result.facets
        facet_map = facet_result.facetMap
        width, height = facet_result.width, facet_result.height
        newly_affected = set()

        # For each orphaned pixel, do a spiral search for nearest valid facet
        for x, y in orphaned_pixels:
            found_neighbor = False

            # Spiral search with increasing radius
            for radius in range(1, min(width, height)):
                if found_neighbor:
                    break

                # Check all pixels at this radius
                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        # Only check pixels on the perimeter of the square
                        if abs(dx) != radius and abs(dy) != radius:
                            continue

                        nx, ny = x + dx, y + dy

                        # Boundary check
                        if nx < 0 or nx >= width or ny < 0 or ny >= height:
                            continue

                        # Get facet at this location
                        neighbor_id = facet_map.get(nx, ny)

                        # Check if it's a valid facet (not being removed)
                        if neighbor_id is not None and neighbor_id not in facets_being_removed:
                            neighbor_facet = facets[neighbor_id]
                            if neighbor_facet is not None:
                                # Assign this pixel to the found neighbor
                                img_color_indices.set(x, y, neighbor_facet.color)
                                newly_affected.add(neighbor_id)
                                found_neighbor = True
                                break

            # If still no neighbor found after max search, try direct adjacency fallback
            if not found_neighbor:
                # Check immediate 4-connected neighbors as last resort
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        neighbor_id = facet_map.get(nx, ny)
                        if neighbor_id is not None:
                            neighbor_facet = facets[neighbor_id]
                            if neighbor_facet is not None:
                                img_color_indices.set(x, y, neighbor_facet.color)
                                newly_affected.add(neighbor_id)
                                break

        return newly_affected

    @staticmethod
    def _get_closest_valid_neighbour(
            facet_to_remove: Facet,
            facets_being_removed: Set[int],
            facet_result: FacetResult,
            x: int,
            y: int,
            color_distances: np.ndarray
    ) -> int:
        """Find closest neighbor that is NOT being removed."""
        closest_neighbour = -1
        min_distance = 10 ** 9
        min_color_distance = float('inf')

        neigh_idxs = facet_to_remove.neighbourFacets
        if not neigh_idxs:
            return -1

        facets = facet_result.facets
        facet_color = facet_to_remove.color

        if isinstance(color_distances, np.ndarray):
            color_row = color_distances[facet_color]
        else:
            color_row = color_distances[facet_color]

        for n_idx in neigh_idxs:
            # Skip if this neighbor is also being removed
            if n_idx in facets_being_removed:
                continue

            neigh = facets[n_idx]
            if neigh is None or not neigh.borderPoints:
                continue

            # Bbox pruning
            bx_min, bx_max = neigh.bbox.minX, neigh.bbox.maxX
            by_min, by_max = neigh.bbox.minY, neigh.bbox.maxY

            dx = max(0, bx_min - x, x - bx_max)
            dy = max(0, by_min - y, y - by_max)
            bbox_lower_bound = dx + dy

            if bbox_lower_bound > min_distance:
                continue

            # Vectorized distance
            border_array = np.array([(p.x, p.y) for p in neigh.borderPoints], dtype=np.int32)
            distances = np.abs(border_array[:, 0] - x) + np.abs(border_array[:, 1] - y)
            min_d = int(distances.min())

            if min_d < min_distance:
                min_distance = min_d
                closest_neighbour = n_idx
                min_color_distance = float('inf')

                if min_d == 1:
                    return closest_neighbour

            elif min_d == min_distance:
                neigh_color = neigh.color
                cd = float(color_row[neigh_color])
                if cd < min_color_distance:
                    min_color_distance = cd
                    closest_neighbour = n_idx

        return closest_neighbour

    @staticmethod
    def _batch_rebuild_affected_facets(
            affected_facets: Set[int],
            removed_facets: Set[int],
            facet_result: FacetResult,
            img_color_indices: Uint8Array2D,
            visited_cache: BooleanArray2D
    ) -> None:
        """Rebuild all affected facets in a single pass."""
        facets = facet_result.facets
        builder = FacetBuilder()

        # Expand to include neighbors of affected facets
        all_affected = set(affected_facets)
        for fid in affected_facets:
            facet = facets[fid]
            if facet is None:
                continue

            if facet.neighbourFacetsIsDirty:
                builder.build_facet_neighbour(facet, facet_result)

            if facet.neighbourFacets:
                for n_id in facet.neighbourFacets:
                    if n_id not in removed_facets:
                        all_affected.add(n_id)

        # Rebuild each affected facet once
        for fid in all_affected:
            facet = facets[fid]
            if facet is None or not facet.borderPoints:
                continue

            # Reset visited array
            min_x, max_x = facet.bbox.minX, facet.bbox.maxX
            min_y, max_y = facet.bbox.minY, facet.bbox.maxY

            for y in range(min_y, max_y + 1):
                for x in range(min_x, max_x + 1):
                    if facet_result.facetMap.get(x, y) == fid:
                        visited_cache.set(x, y, False)

            # Rebuild
            bp = facet.borderPoints[0]
            new_facet = builder.build_facet(
                fid,
                facet.color,
                bp.x,
                bp.y,
                visited_cache,
                img_color_indices,
                facet_result
            )

            facets[fid] = new_facet

            if new_facet is not None and new_facet.pointCount == 0:
                facets[fid] = None

        # Mark neighbor lists as dirty
        for fid in all_affected:
            facet = facets[fid]
            if facet is not None:
                facet.neighbourFacets = None
                facet.neighbourFacetsIsDirty = True

    @staticmethod
    def _build_color_distance_matrix(colors_by_index: List[RGB]) -> np.ndarray:
        """Vectorized Euclidean distance matrix."""
        if not colors_by_index:
            return np.array([])

        arr = np.asarray(colors_by_index, dtype=np.float64)
        diff = arr[:, None, :] - arr[None, :, :]
        dist = np.sqrt(np.einsum('ijk,ijk->ij', diff, diff))
        return dist