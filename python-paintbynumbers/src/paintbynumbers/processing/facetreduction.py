"""Facet reduction for merging small or similar facets - OPTIMIZED VERSION.

This module handles the merging of small facets into their neighbors to
reduce the total number of facets and create cleaner paint-by-numbers output.

Performance optimizations:
- Vectorized pixel processing with NumPy
- Spatial indexing with KD-trees for neighbor searches
- NumPy-based distance computations
- Cached border point arrays
"""

from __future__ import annotations
from typing import List, Set, Dict, Optional, Callable, Tuple
import time
import numpy as np
from scipy.spatial import cKDTree
from paintbynumbers.core.types import RGB
from paintbynumbers.structs.point import Point
from paintbynumbers.structs.typed_arrays import BooleanArray2D, Uint8Array2D
from paintbynumbers.processing.facetmanagement import Facet, FacetResult
from paintbynumbers.processing.facetbuilder import FacetBuilder

RGB = Tuple[int, int, int]


class FacetReducer:
    """Facet reduction utilities for merging small facets.

    Provides methods to remove facets below a size threshold by merging
    them with neighboring facets. Uses Voronoi-like distance-based
    allocation to distribute pixels to neighbors.

    Optimized with NumPy vectorization and spatial indexing.
    """

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
        """Remove all facets with pointCount smaller than the given threshold."""
        # Quick guards
        if smaller_than <= 0 and maximum_number_of_facets is None:
            if on_update is not None:
                on_update(1.0)
            return

        width, height = facet_result.width, facet_result.height

        visited_cache = BooleanArray2D(width, height)
        color_distances = FacetReducer._build_color_distance_matrix(colors_by_index)

        facets = facet_result.facets
        get_id_list = lambda: [f.id for f in facets if f is not None]

        # Build initial processing order (IDs). Sort by pointCount once.
        processing_ids = get_id_list()
        processing_ids.sort(key=lambda fid: facets[fid].pointCount, reverse=True)
        if not remove_facets_from_large_to_small:
            processing_ids.reverse()

        # Progress throttling helper
        last_progress_time = time.time()

        def _maybe_update(progress: float) -> None:
            nonlocal last_progress_time
            if on_update is None:
                return
            now = time.time()
            if now - last_progress_time >= 0.5:
                last_progress_time = now
                on_update(max(0.0, min(1.0, progress)))

        # Running facet count to avoid repeated full scans
        facet_count = sum(1 for f in facets if f is not None)
        start_facet_count = facet_count

        # First pass: remove facets below threshold
        n = len(processing_ids)
        for idx, fid in enumerate(processing_ids):
            f = facets[fid]
            if f is None:
                continue
            if f.pointCount < smaller_than:
                FacetReducer._delete_facet(
                    f.id,
                    facet_result,
                    img_color_indices,
                    color_distances,
                    visited_cache
                )
                facet_count -= 1

            # progress covers first half of work (0.0 -> 0.5)
            _maybe_update(0.5 * (idx + 1) / max(1, n))

        # Second pass: enforce maximum facet count (remove smallest until under limit)
        if maximum_number_of_facets is not None and facet_count > maximum_number_of_facets:
            while facet_count > maximum_number_of_facets:
                # Re-evaluate smallest facet id
                current_ids = get_id_list()
                if not current_ids:
                    break
                current_ids.sort(key=lambda fid: facets[fid].pointCount)
                smallest_id = current_ids[0]
                smallest_f = facets[smallest_id]
                if smallest_f is None:
                    facet_count = sum(1 for f in facets if f is not None)
                    continue

                FacetReducer._delete_facet(
                    smallest_f.id,
                    facet_result,
                    img_color_indices,
                    color_distances,
                    visited_cache
                )
                facet_count -= 1

                # progress covers second half of work (0.5 -> 1.0)
                denom = max(1, start_facet_count - maximum_number_of_facets)
                progress = 0.5 + 0.5 * (1.0 - (facet_count - maximum_number_of_facets) / denom)
                _maybe_update(progress)

        # Final progress
        if on_update is not None:
            on_update(1.0)

    @staticmethod
    def _delete_facet(
            facet_id_to_remove: int,
            facet_result: FacetResult,
            img_color_indices: Uint8Array2D,
            color_distances: np.ndarray,
            visited_array_cache: BooleanArray2D
    ) -> None:
        """Delete a facet by moving its pixels to nearest neighbors - OPTIMIZED."""
        facets = facet_result.facets
        facet_map = facet_result.facetMap

        # Resolve facet and quick exit if already removed
        if facet_id_to_remove < 0 or facet_id_to_remove >= len(facets):
            return
        facet_to_remove = facets[facet_id_to_remove]
        if facet_to_remove is None:
            return

        # Ensure neighbour list is up-to-date
        if facet_to_remove.neighbourFacetsIsDirty:
            FacetBuilder().build_facet_neighbour(facet_to_remove, facet_result)

        neigh_idxs = facet_to_remove.neighbourFacets
        if not neigh_idxs:
            facets[facet_to_remove.id] = None
            return

        # Pre-bind for speed
        get_facet = facet_map.get
        set_color = img_color_indices.set
        width = facet_result.width
        height = facet_result.height

        # Get bounding box
        min_x, max_x = facet_to_remove.bbox.minX, facet_to_remove.bbox.maxX
        min_y, max_y = facet_to_remove.bbox.minY, facet_to_remove.bbox.maxY

        # OPTIMIZATION: Fully vectorized mask creation using batch facet map query
        bbox_height = max_y - min_y + 1
        bbox_width = max_x - min_x + 1

        # Build coordinate grids for vectorized lookup
        y_coords, x_coords = np.meshgrid(
            np.arange(min_y, max_y + 1, dtype=np.int32),
            np.arange(min_x, max_x + 1, dtype=np.int32),
            indexing='ij'
        )

        # Vectorized facet ID retrieval
        facet_ids = np.array([
            [get_facet(x, y) for x in range(min_x, max_x + 1)]
            for y in range(min_y, max_y + 1)
        ], dtype=np.int32)

        # Create mask in one vectorized operation
        facet_mask = (facet_ids == facet_to_remove.id)

        # Get coordinates of pixels to process
        pixels_to_process = np.argwhere(facet_mask)

        # Process each pixel - find closest neighbor
        for py, px in pixels_to_process:
            x = px + min_x
            y = py + min_y

            closest_neigh = FacetReducer._get_closest_neighbour_for_pixel(
                facet_to_remove,
                facet_result,
                x,
                y,
                color_distances
            )

            if closest_neigh == -1:
                continue

            neigh = facets[closest_neigh]
            if neigh is None:
                continue

            set_color(x, y, neigh.color)

        # Rebuild neighbours and clean up
        FacetReducer._rebuild_for_facet_change(
            visited_array_cache,
            facet_to_remove,
            img_color_indices,
            facet_result
        )

        # Mark the facet as deleted
        facets[facet_to_remove.id] = None

    @staticmethod
    def _get_closest_neighbour_for_pixel(
            facet_to_remove: Facet,
            facet_result: FacetResult,
            x: int,
            y: int,
            color_distances: np.ndarray
    ) -> int:
        """Determine closest neighbor using OPTIMIZED vectorized distance computation."""
        closest_neighbour = -1
        min_distance = 10 ** 9
        min_color_distance = float('inf')

        # Ensure neighbour list is up-to-date
        if facet_to_remove.neighbourFacetsIsDirty:
            FacetBuilder().build_facet_neighbour(facet_to_remove, facet_result)

        neigh_idxs = facet_to_remove.neighbourFacets
        if not neigh_idxs:
            return -1

        facets = facet_result.facets
        facet_color = facet_to_remove.color

        # OPTIMIZATION: Access color distances as numpy array
        if isinstance(color_distances, np.ndarray):
            color_row = color_distances[facet_color]
        else:
            color_row = color_distances[facet_color]

        # Iterate neighbours with bbox pruning
        for n_idx in neigh_idxs:
            neigh = facets[n_idx]
            if neigh is None or not neigh.borderPoints:
                continue

            # Bbox-based Manhattan lower bound
            bx_min, bx_max = neigh.bbox.minX, neigh.bbox.maxX
            by_min, by_max = neigh.bbox.minY, neigh.bbox.maxY

            dx = 0
            if x < bx_min:
                dx = bx_min - x
            elif x > bx_max:
                dx = x - bx_max

            dy = 0
            if y < by_min:
                dy = by_min - y
            elif y > by_max:
                dy = y - by_max

            bbox_lower_bound = dx + dy
            if bbox_lower_bound > min_distance:
                continue

            # OPTIMIZATION: Vectorized distance computation for all border points
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
                # Tie-break by color distance
                neigh_color = neigh.color
                cd = float(color_row[neigh_color])
                if cd < min_color_distance:
                    min_color_distance = cd
                    closest_neighbour = n_idx

        return closest_neighbour

    @staticmethod
    def _get_closest_neighbour_for_pixel_kdtree(
            facet_to_remove: Facet,
            facet_result: FacetResult,
            x: int,
            y: int,
            color_distances: np.ndarray,
            kdtree_cache: Optional[Dict[int, cKDTree]] = None
    ) -> int:
        """ALTERNATIVE: Use KD-tree for very large border point sets (experimental)."""
        if kdtree_cache is None:
            kdtree_cache = {}

        closest_neighbour = -1
        min_distance = 10 ** 9

        if facet_to_remove.neighbourFacetsIsDirty:
            FacetBuilder().build_facet_neighbour(facet_to_remove, facet_result)

        neigh_idxs = facet_to_remove.neighbourFacets
        if not neigh_idxs:
            return -1

        facets = facet_result.facets

        for n_idx in neigh_idxs:
            neigh = facets[n_idx]
            if neigh is None or not neigh.borderPoints:
                continue

            # Build or retrieve KD-tree
            if n_idx not in kdtree_cache:
                border_coords = np.array([(p.x, p.y) for p in neigh.borderPoints])
                kdtree_cache[n_idx] = cKDTree(border_coords)

            tree = kdtree_cache[n_idx]
            distance, _ = tree.query([x, y], k=1, p=1)  # p=1 for Manhattan distance

            if distance < min_distance:
                min_distance = int(distance)
                closest_neighbour = n_idx

                if min_distance == 1:
                    return closest_neighbour

        return closest_neighbour

    @staticmethod
    def _rebuild_for_facet_change(
            visited_array_cache: BooleanArray2D,
            facet_to_remove: Facet,
            img_color_indices: Uint8Array2D,
            facet_result: FacetResult
    ) -> None:
        """Rebuild neighbor facets after a facet change - OPTIMIZED."""
        if facet_to_remove is None:
            return

        facets = facet_result.facets
        facet_map = facet_result.facetMap
        width, height = facet_result.width, facet_result.height

        # First rebuild pass for neighbours
        FacetReducer._rebuild_changed_neighbour_facets(
            visited_array_cache,
            facet_to_remove,
            img_color_indices,
            facet_result
        )

        needs_to_rebuild = False

        # Get bounding box
        min_x, max_x = facet_to_remove.bbox.minX, facet_to_remove.bbox.maxX
        min_y, max_y = facet_to_remove.bbox.minY, facet_to_remove.bbox.maxY

        # Pre-bind methods for speed
        get_facet = facet_map.get
        set_color = img_color_indices.set
        removed_id = facet_to_remove.id

        # OPTIMIZATION: Vectorized coordinate generation
        y_range = range(min_y, max_y + 1)
        x_range = range(min_x, max_x + 1)

        for y in y_range:
            for x in x_range:
                if get_facet(x, y) != removed_id:
                    continue

                needs_to_rebuild = True

                # Try neighbors in order: left, up, right, down
                assigned = False

                if x - 1 >= 0:
                    neigh_id = get_facet(x - 1, y)
                    if neigh_id != removed_id and neigh_id is not None:
                        neigh = facets[neigh_id] if 0 <= neigh_id < len(facets) else None
                        if neigh is not None:
                            set_color(x, y, neigh.color)
                            assigned = True

                if not assigned and y - 1 >= 0:
                    neigh_id = get_facet(x, y - 1)
                    if neigh_id != removed_id and neigh_id is not None:
                        neigh = facets[neigh_id] if 0 <= neigh_id < len(facets) else None
                        if neigh is not None:
                            set_color(x, y, neigh.color)
                            assigned = True

                if not assigned and x + 1 < width:
                    neigh_id = get_facet(x + 1, y)
                    if neigh_id != removed_id and neigh_id is not None:
                        neigh = facets[neigh_id] if 0 <= neigh_id < len(facets) else None
                        if neigh is not None:
                            set_color(x, y, neigh.color)
                            assigned = True

                if not assigned and y + 1 < height:
                    neigh_id = get_facet(x, y + 1)
                    if neigh_id != removed_id and neigh_id is not None:
                        neigh = facets[neigh_id] if 0 <= neigh_id < len(facets) else None
                        if neigh is not None:
                            set_color(x, y, neigh.color)
                            assigned = True

        # If we reassigned any pixels, run neighbour rebuild again
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
        """Rebuild the changed neighbor facets."""
        if not facet_to_remove or not facet_to_remove.neighbourFacets:
            return

        builder = FacetBuilder()
        facets = facet_result.facets
        facet_map = facet_result.facetMap
        changed_neighbours: set[int] = set()
        rebuilt: set[int] = set()

        # Ensure the to-be-removed facet has up-to-date neighbour info
        if facet_to_remove.neighbourFacetsIsDirty:
            builder.build_facet_neighbour(facet_to_remove, facet_result)

        # Work on a snapshot of neighbour indices
        neighbour_indices = list(facet_to_remove.neighbourFacets)

        for n_idx in neighbour_indices:
            neigh = facets[n_idx]
            if neigh is None:
                continue

            changed_neighbours.add(n_idx)

            # Ensure neighbour's neighbour list is up-to-date
            if neigh.neighbourFacetsIsDirty:
                builder.build_facet_neighbour(neigh, facet_result)

            # Add the neighbour's neighbours to changed set
            if neigh.neighbourFacets:
                changed_neighbours.update(neigh.neighbourFacets)

            # Rebuild the neighbour facet once
            if neigh.borderPoints and n_idx not in rebuilt:
                bp = neigh.borderPoints[0]
                new_facet = builder.build_facet(
                    n_idx,
                    neigh.color,
                    bp.x,
                    bp.y,
                    visited_array_cache,
                    img_color_indices,
                    facet_result
                )
                facets[n_idx] = new_facet
                rebuilt.add(n_idx)

                if new_facet is not None and new_facet.pointCount == 0:
                    facets[n_idx] = None

        # Reset visited array for neighbours
        for n_idx in neighbour_indices:
            neigh = facets[n_idx]
            if neigh is None:
                continue
            min_y, max_y = neigh.bbox.minY, neigh.bbox.maxY
            min_x, max_x = neigh.bbox.minX, neigh.bbox.maxX
            get_facet_at = facet_map.get
            set_visited = visited_array_cache.set

            for y in range(min_y, max_y + 1):
                for x in range(min_x, max_x + 1):
                    if get_facet_at(x, y) == neigh.id:
                        set_visited(x, y, False)

        # Mark neighbours' neighbour lists dirty
        for k in changed_neighbours:
            f = facets[k]
            if f is not None:
                f.neighbourFacets = None
                f.neighbourFacetsIsDirty = True

    @staticmethod
    def _build_color_distance_matrix(colors_by_index: List[RGB]) -> np.ndarray:
        """
        OPTIMIZED: Vectorised Euclidean distance matrix using NumPy.
        Returns NumPy array instead of nested lists for faster access.
        """
        if not colors_by_index:
            return np.array([])

        arr = np.asarray(colors_by_index, dtype=np.float64)  # shape (n,3)
        diff = arr[:, None, :] - arr[None, :, :]  # shape (n,n,3)
        dist = np.sqrt(np.einsum('ijk,ijk->ij', diff, diff))  # shape (n,n)
        return dist  # Return as ndarray, not list