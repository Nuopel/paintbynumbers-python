"""Border segmentation for facets with Haar wavelet smoothing.

This module segments facet borders into shared edges between neighbors,
applies Haar wavelet smoothing for curves, and matches segments between
adjacent facets to ensure continuity.
"""

from __future__ import annotations
from typing import List, Optional, Callable
from paintbynumbers.core.types import PathPoint, OrientationEnum
from paintbynumbers.structs.point import Point
from paintbynumbers.processing.facetmanagement import (
    Facet, FacetResult, PathSegment, FacetBoundarySegment
)

# Constants
DEFAULT_HALVE_ITERATIONS = 2
MAX_SEGMENT_MATCH_DISTANCE = 4
MIN_PATH_LENGTH_FOR_REDUCTION = 5
BATCH_UPDATE_FREQUENCY = 100


class FacetBorderSegmenter:
    """Builds border segments that are shared between facets.

    Border paths are nice but not linked to neighbour facets. Segments ensure
    that adjacent facets share the exact same boundary, preventing gaps when
    the paths are smoothed or modified.
    """

    @staticmethod
    def build_facet_border_segments(
        facet_result: FacetResult,
        nr_of_times_to_halve_points: int = DEFAULT_HALVE_ITERATIONS,
        on_update: Optional[Callable[[float], None]] = None
    ) -> None:
        """Build border segments for all facets and match them with neighbors.

        This process:
        1. Chops border paths into segments where the neighbor changes
        2. Reduces segment complexity with Haar wavelet smoothing
        3. Matches segments between adjacent facets

        Args:
            facet_result: FacetResult containing facets with border paths
            nr_of_times_to_halve_points: Number of Haar wavelet iterations
            on_update: Optional callback for progress updates (0.0 to 1.0)

        Example:
            >>> from paintbynumbers.processing.facetmanagement import FacetResult
            >>> facet_result = FacetResult()
            >>> # ... setup facets with border paths ...
            >>> FacetBorderSegmenter.build_facet_border_segments(facet_result)
            >>> # Now facets have matched border segments
        """
        # First chop up the border path into segments each time the neighbor changes
        segments_per_facet = FacetBorderSegmenter._prepare_segments_per_facet(facet_result)

        # Reduce segment complexity with Haar wavelet smoothing
        FacetBorderSegmenter._reduce_segment_complexity(
            facet_result, segments_per_facet, nr_of_times_to_halve_points
        )

        # Match segments with neighbours
        FacetBorderSegmenter._match_segments_with_neighbours(
            facet_result, segments_per_facet, on_update
        )

    @staticmethod
    def _prepare_segments_per_facet(facet_result: FacetResult) -> List[List[Optional[PathSegment]]]:
        """Chop up border paths into segments adjacent to the same neighbour.

        Segments are split when:
        - The neighbor on the other side of the wall changes
        - A diagonal turn introduces a different neighbor

        Args:
            facet_result: FacetResult containing facets with border paths

        Returns:
            List of segment lists per facet (indexed by facet ID)
        """
        segments_per_facet: List[List[Optional[PathSegment]]] = [[] for _ in range(len(facet_result.facets))]

        for f in facet_result.facets:
            if f is None:
                continue

            segments: List[PathSegment] = []

            if len(f.borderPath) > 1:
                current_points: List[PathPoint] = [f.borderPath[0]]

                for i in range(1, len(f.borderPath)):
                    prev_border_point = f.borderPath[i - 1]
                    cur_border_point = f.borderPath[i]

                    old_neighbour = prev_border_point.get_neighbour(facet_result)
                    cur_neighbour = cur_border_point.get_neighbour(facet_result)

                    is_transition_point = False

                    if old_neighbour != cur_neighbour:
                        is_transition_point = True
                    elif old_neighbour != -1:
                        # Check for tight rotations with different diagonal neighbors
                        if (prev_border_point.x == cur_border_point.x and
                            prev_border_point.y == cur_border_point.y):
                            # Rotation turn - check diagonal neighbor
                            diag_neighbour = -1

                            if ((prev_border_point.orientation == OrientationEnum.Top and
                                 cur_border_point.orientation == OrientationEnum.Left) or
                                (prev_border_point.orientation == OrientationEnum.Left and
                                 cur_border_point.orientation == OrientationEnum.Top)):
                                diag_neighbour = facet_result.facetMap.get(cur_border_point.x - 1, cur_border_point.y - 1)
                            elif ((prev_border_point.orientation == OrientationEnum.Top and
                                   cur_border_point.orientation == OrientationEnum.Right) or
                                  (prev_border_point.orientation == OrientationEnum.Right and
                                   cur_border_point.orientation == OrientationEnum.Top)):
                                diag_neighbour = facet_result.facetMap.get(cur_border_point.x + 1, cur_border_point.y - 1)
                            elif ((prev_border_point.orientation == OrientationEnum.Bottom and
                                   cur_border_point.orientation == OrientationEnum.Left) or
                                  (prev_border_point.orientation == OrientationEnum.Left and
                                   cur_border_point.orientation == OrientationEnum.Bottom)):
                                diag_neighbour = facet_result.facetMap.get(cur_border_point.x - 1, cur_border_point.y + 1)
                            elif ((prev_border_point.orientation == OrientationEnum.Bottom and
                                   cur_border_point.orientation == OrientationEnum.Right) or
                                  (prev_border_point.orientation == OrientationEnum.Right and
                                   cur_border_point.orientation == OrientationEnum.Bottom)):
                                diag_neighbour = facet_result.facetMap.get(cur_border_point.x + 1, cur_border_point.y + 1)

                            if diag_neighbour != old_neighbour:
                                is_transition_point = True

                    current_points.append(cur_border_point)

                    if is_transition_point:
                        # Create segment and start new list
                        if len(current_points) > 1:
                            segment = PathSegment(current_points, old_neighbour)
                            segments.append(segment)
                            current_points = [cur_border_point]

                # Handle remainder
                if len(current_points) > 1:
                    old_neighbour = f.borderPath[-1].get_neighbour(facet_result)

                    if len(segments) > 0 and segments[0].neighbour == old_neighbour:
                        # Merge with first segment
                        merged_points = current_points + segments[0].points
                        segments[0].points = merged_points
                    else:
                        # Add as final segment
                        segment = PathSegment(current_points, old_neighbour)
                        segments.append(segment)

            segments_per_facet[f.id] = segments

        return segments_per_facet

    @staticmethod
    def _reduce_segment_complexity(
        facet_result: FacetResult,
        segments_per_facet: List[List[Optional[PathSegment]]],
        nr_of_times_to_halve_points: int
    ) -> None:
        """Reduce each segment's border path points using Haar wavelet smoothing.

        Args:
            facet_result: FacetResult for dimensions
            segments_per_facet: List of segments per facet
            nr_of_times_to_halve_points: Number of iterations
        """
        for f in facet_result.facets:
            if f is None:
                continue

            for segment in segments_per_facet[f.id]:
                if segment is None:
                    continue

                for _ in range(nr_of_times_to_halve_points):
                    segment.points = FacetBorderSegmenter._reduce_segment_haar_wavelet(
                        segment.points, True, facet_result.width, facet_result.height
                    )

    @staticmethod
    def _reduce_segment_haar_wavelet(
        newpath: List[PathPoint],
        skip_outside_borders: bool,
        width: int,
        height: int
    ) -> List[PathPoint]:
        """Remove points by averaging pairs (Haar wavelet reduction).

        Takes the average of each pair of points as a new point. Delta values
        that create the Haar wavelet are not tracked because they're unneeded.

        Args:
            newpath: Input path points
            skip_outside_borders: If True, preserve image edge points
            width: Image width
            height: Image height

        Returns:
            Reduced path with approximately half the points
        """
        if len(newpath) <= MIN_PATH_LENGTH_FOR_REDUCTION:
            return newpath

        reduced_path: List[PathPoint] = [newpath[0]]

        for i in range(1, len(newpath) - 2, 2):
            if (not skip_outside_borders or
                (skip_outside_borders and
                 not FacetBorderSegmenter._is_outside_border_point(newpath[i], width, height))):
                # Average the pair
                cx = (newpath[i].x + newpath[i + 1].x) / 2.0
                cy = (newpath[i].y + newpath[i + 1].y) / 2.0
                reduced_path.append(PathPoint(int(cx), int(cy), OrientationEnum.Left))
            else:
                # Keep both points (on image edge)
                reduced_path.append(newpath[i])
                reduced_path.append(newpath[i + 1])

        # Close the loop
        reduced_path.append(newpath[-1])

        return reduced_path

    @staticmethod
    def _is_outside_border_point(point: Point, width: int, height: int) -> bool:
        """Check if a point is on the outside border of the image.

        Args:
            point: Point to check
            width: Image width
            height: Image height

        Returns:
            True if point is on image edge
        """
        return point.x == 0 or point.y == 0 or point.x == width - 1 or point.y == height - 1

    @staticmethod
    def _match_segments_with_neighbours(
        facet_result: FacetResult,
        segments_per_facet: List[List[Optional[PathSegment]]],
        on_update: Optional[Callable[[float], None]] = None
    ) -> None:
        """Match all segments between facets and their neighbours.

        A segment matches when start/end points match within MAX_DISTANCE.
        Segments can match in normal or reverse order.

        Args:
            facet_result: FacetResult containing facets
            segments_per_facet: List of segments per facet
            on_update: Optional progress callback
        """
        max_distance = MAX_SEGMENT_MATCH_DISTANCE

        # Reserve room for border segments
        for f in facet_result.facets:
            if f is not None:
                f.borderSegments = [None] * len(segments_per_facet[f.id])  # type: ignore

        count = 0

        for f in facet_result.facets:
            if f is None:
                continue

            for s in range(len(segments_per_facet[f.id])):
                segment = segments_per_facet[f.id][s]

                if segment is not None and f.borderSegments[s] is None:
                    # Set this facet's segment
                    f.borderSegments[s] = FacetBoundarySegment(segment, segment.neighbour, False)

                    if segment.neighbour != -1:
                        neighbour_facet = facet_result.facets[segment.neighbour]
                        match_found = False

                        if neighbour_facet is not None:
                            neighbour_segments = segments_per_facet[segment.neighbour]

                            for ns in range(len(neighbour_segments)):
                                neighbour_segment = neighbour_segments[ns]

                                # Only match unprocessed segments adjacent to current facet
                                if (neighbour_segment is not None and
                                    neighbour_segment.neighbour == f.id):

                                    seg_start = segment.points[0]
                                    seg_end = segment.points[-1]
                                    nseg_start = neighbour_segment.points[0]
                                    nseg_end = neighbour_segment.points[-1]

                                    matches_straight = (
                                        seg_start.distance_to(nseg_start) <= max_distance and
                                        seg_end.distance_to(nseg_end) <= max_distance
                                    )
                                    matches_reverse = (
                                        seg_start.distance_to(nseg_end) <= max_distance and
                                        seg_end.distance_to(nseg_start) <= max_distance
                                    )

                                    # Both match - choose closest
                                    if matches_straight and matches_reverse:
                                        straight_dist = (seg_start.distance_to(nseg_start) +
                                                       seg_end.distance_to(nseg_end))
                                        reverse_dist = (seg_start.distance_to(nseg_end) +
                                                      seg_end.distance_to(nseg_start))

                                        if straight_dist < reverse_dist:
                                            matches_reverse = False
                                        else:
                                            matches_straight = False

                                    if matches_straight:
                                        # Start & end points match
                                        neighbour_facet.borderSegments[ns] = FacetBoundarySegment(
                                            segment, f.id, False
                                        )
                                        segments_per_facet[neighbour_facet.id][ns] = None
                                        match_found = True
                                        break
                                    elif matches_reverse:
                                        # Start & end points match in reverse order
                                        neighbour_facet.borderSegments[ns] = FacetBoundarySegment(
                                            segment, f.id, True
                                        )
                                        segments_per_facet[neighbour_facet.id][ns] = None
                                        match_found = True
                                        break

                    # Clear segment so it can't be processed again
                    segments_per_facet[f.id][s] = None

            count += 1
            if count % BATCH_UPDATE_FREQUENCY == 0 and on_update is not None:
                on_update(f.id / len(facet_result.facets))

        if on_update is not None:
            on_update(1.0)
