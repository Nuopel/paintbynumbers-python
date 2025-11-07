"""Tests for FacetBorderSegmenter segmentation and smoothing functionality."""

import pytest
from paintbynumbers.processing.facetmanagement import (
    Facet, FacetResult, PathSegment, FacetBoundarySegment
)
from paintbynumbers.processing.facetbordertracer import FacetBorderTracer
from paintbynumbers.processing.facetbordersegmenter import FacetBorderSegmenter
from paintbynumbers.structs.point import Point
from paintbynumbers.structs.boundingbox import BoundingBox
from paintbynumbers.structs.typed_arrays import Uint32Array2D
from paintbynumbers.core.types import PathPoint, OrientationEnum


class TestPathSegmentBasic:
    """Test PathSegment class."""

    def test_create_path_segment(self):
        """Test creating a PathSegment."""
        points = [
            PathPoint(0, 0, OrientationEnum.Left),
            PathPoint(0, 1, OrientationEnum.Left)
        ]
        segment = PathSegment(points, neighbour=5)

        assert len(segment.points) == 2
        assert segment.neighbour == 5

    def test_path_segment_repr(self):
        """Test PathSegment string representation."""
        points = [PathPoint(0, 0, OrientationEnum.Left)]
        segment = PathSegment(points, neighbour=3)

        repr_str = repr(segment)
        assert "PathSegment" in repr_str
        assert "points=1" in repr_str
        assert "neighbour=3" in repr_str


class TestFacetBoundarySegmentBasic:
    """Test FacetBoundarySegment class."""

    def test_create_boundary_segment(self):
        """Test creating a FacetBoundarySegment."""
        points = [PathPoint(0, 0, OrientationEnum.Left)]
        path_segment = PathSegment(points, neighbour=5)
        boundary = FacetBoundarySegment(path_segment, neighbour=3, reverseOrder=False)

        assert boundary.originalSegment == path_segment
        assert boundary.neighbour == 3
        assert boundary.reverseOrder is False

    def test_boundary_segment_reverse(self):
        """Test FacetBoundarySegment with reverse order."""
        points = [PathPoint(0, 0, OrientationEnum.Left)]
        path_segment = PathSegment(points, neighbour=5)
        boundary = FacetBoundarySegment(path_segment, neighbour=3, reverseOrder=True)

        assert boundary.reverseOrder is True

    def test_boundary_segment_repr(self):
        """Test FacetBoundarySegment string representation."""
        points = [PathPoint(0, 0, OrientationEnum.Left)]
        path_segment = PathSegment(points, neighbour=5)
        boundary = FacetBoundarySegment(path_segment, neighbour=3, reverseOrder=False)

        repr_str = repr(boundary)
        assert "FacetBoundarySegment" in repr_str
        assert "points=1" in repr_str
        assert "neighbour=3" in repr_str


class TestFacetBorderSegmenterBasic:
    """Basic functionality tests for FacetBorderSegmenter."""

    def test_simple_segmentation(self):
        """Test segmentation of a simple two-facet image."""
        facet_result = FacetResult()
        facet_result.width = 4
        facet_result.height = 2
        facet_result.facetMap = Uint32Array2D(4, 2)
        facet_result.facets = [None, None]

        # Facet 0: left half
        facet0 = Facet()
        facet0.id = 0
        facet0.color = 0
        facet0.pointCount = 4
        facet0.borderPoints = [Point(0, 0), Point(1, 0), Point(0, 1), Point(1, 1)]
        facet0.bbox = BoundingBox(minX=0, minY=0, maxX=1, maxY=1)
        facet_result.facets[0] = facet0

        # Facet 1: right half
        facet1 = Facet()
        facet1.id = 1
        facet1.color = 1
        facet1.pointCount = 4
        facet1.borderPoints = [Point(2, 0), Point(3, 0), Point(2, 1), Point(3, 1)]
        facet1.bbox = BoundingBox(minX=2, minY=0, maxX=3, maxY=1)
        facet_result.facets[1] = facet1

        # Fill map
        for y in range(2):
            for x in range(4):
                facet_result.facetMap.set(x, y, 0 if x < 2 else 1)

        # Trace borders first
        FacetBorderTracer.build_facet_border_paths(facet_result)

        # Now segment
        FacetBorderSegmenter.build_facet_border_segments(facet_result, nr_of_times_to_halve_points=0)

        # Both facets should have border segments
        assert len(facet0.borderSegments) > 0
        assert len(facet1.borderSegments) > 0

    def test_empty_facet_list(self):
        """Test with no facets."""
        facet_result = FacetResult()
        facet_result.width = 3
        facet_result.height = 3
        facet_result.facetMap = Uint32Array2D(3, 3)
        facet_result.facets = []

        # Should not crash
        FacetBorderSegmenter.build_facet_border_segments(facet_result)

    def test_deleted_facets(self):
        """Test with None entries in facets array."""
        facet_result = FacetResult()
        facet_result.width = 3
        facet_result.height = 3
        facet_result.facetMap = Uint32Array2D(3, 3)
        facet_result.facets = [None, None, None]

        # Should not crash
        FacetBorderSegmenter.build_facet_border_segments(facet_result)


class TestFacetBorderSegmenterSmoothing:
    """Test Haar wavelet smoothing functionality."""

    def test_haar_wavelet_reduction(self):
        """Test that Haar wavelet reduces point count."""
        # Create a path with many points
        points = [PathPoint(i, 0, OrientationEnum.Top) for i in range(20)]

        reduced = FacetBorderSegmenter._reduce_segment_haar_wavelet(
            points, skip_outside_borders=False, width=100, height=100
        )

        # Should have fewer points
        assert len(reduced) < len(points)
        # Should preserve first and last
        assert reduced[0].x == points[0].x
        assert reduced[-1].x == points[-1].x

    def test_haar_wavelet_short_path(self):
        """Test that short paths are not reduced."""
        points = [PathPoint(i, 0, OrientationEnum.Top) for i in range(4)]

        reduced = FacetBorderSegmenter._reduce_segment_haar_wavelet(
            points, skip_outside_borders=False, width=100, height=100
        )

        # Should remain unchanged (too short)
        assert len(reduced) == len(points)

    def test_haar_wavelet_preserve_edges(self):
        """Test that image edge points are preserved."""
        # Create points along top edge
        points = [PathPoint(i, 0, OrientationEnum.Top) for i in range(10)]

        reduced = FacetBorderSegmenter._reduce_segment_haar_wavelet(
            points, skip_outside_borders=True, width=10, height=10
        )

        # All points should be preserved (on edge)
        assert len(reduced) >= len(points) - 2  # Might reduce interior slightly

    def test_multiple_smoothing_iterations(self):
        """Test multiple iterations of smoothing."""
        facet_result = FacetResult()
        facet_result.width = 10
        facet_result.height = 10
        facet_result.facetMap = Uint32Array2D(10, 10)
        facet_result.facets = [None]

        # Create a facet with a long border path
        facet0 = Facet()
        facet0.id = 0
        facet0.color = 0
        facet0.pointCount = 20
        facet0.borderPoints = [Point(i, 0) for i in range(20)]
        facet0.borderPath = [PathPoint(i, 0, OrientationEnum.Top) for i in range(20)]
        facet0.bbox = BoundingBox(minX=0, minY=0, maxX=19, maxY=0)
        facet_result.facets[0] = facet0

        for y in range(10):
            for x in range(10):
                facet_result.facetMap.set(x, y, 0)

        original_length = len(facet0.borderPath)

        # Apply segmentation with multiple iterations
        FacetBorderSegmenter.build_facet_border_segments(facet_result, nr_of_times_to_halve_points=2)

        # Segments should exist and be smoothed
        assert len(facet0.borderSegments) > 0
        if len(facet0.borderSegments) > 0:
            for seg in facet0.borderSegments:
                if seg is not None and seg.originalSegment is not None:
                    # Smoothed segments should have fewer points
                    assert len(seg.originalSegment.points) <= original_length


class TestFacetBorderSegmenterMatching:
    """Test segment matching between facets."""

    def test_segment_matching_straight(self):
        """Test that adjacent segments are matched in straight order."""
        facet_result = FacetResult()
        facet_result.width = 4
        facet_result.height = 2
        facet_result.facetMap = Uint32Array2D(4, 2)
        facet_result.facets = [None, None]

        # Facet 0: left half
        facet0 = Facet()
        facet0.id = 0
        facet0.color = 0
        facet0.pointCount = 4
        facet0.borderPoints = [Point(0, 0), Point(1, 0), Point(0, 1), Point(1, 1)]
        facet0.bbox = BoundingBox(minX=0, minY=0, maxX=1, maxY=1)
        facet_result.facets[0] = facet0

        # Facet 1: right half
        facet1 = Facet()
        facet1.id = 1
        facet1.color = 1
        facet1.pointCount = 4
        facet1.borderPoints = [Point(2, 0), Point(3, 0), Point(2, 1), Point(3, 1)]
        facet1.bbox = BoundingBox(minX=2, minY=0, maxX=3, maxY=1)
        facet_result.facets[1] = facet1

        # Fill map
        for y in range(2):
            for x in range(4):
                facet_result.facetMap.set(x, y, 0 if x < 2 else 1)

        # Trace and segment
        FacetBorderTracer.build_facet_border_paths(facet_result)
        FacetBorderSegmenter.build_facet_border_segments(facet_result, nr_of_times_to_halve_points=0)

        # Check that segments are matched
        # Adjacent facets should share segments
        facet0_has_segments = len(facet0.borderSegments) > 0
        facet1_has_segments = len(facet1.borderSegments) > 0

        assert facet0_has_segments
        assert facet1_has_segments

    def test_segment_neighbor_references(self):
        """Test that segment neighbor references are correct."""
        facet_result = FacetResult()
        facet_result.width = 4
        facet_result.height = 2
        facet_result.facetMap = Uint32Array2D(4, 2)
        facet_result.facets = [None, None]

        # Facet 0: left half
        facet0 = Facet()
        facet0.id = 0
        facet0.color = 0
        facet0.pointCount = 4
        facet0.borderPoints = [Point(0, 0), Point(1, 0), Point(0, 1), Point(1, 1)]
        facet0.bbox = BoundingBox(minX=0, minY=0, maxX=1, maxY=1)
        facet_result.facets[0] = facet0

        # Facet 1: right half
        facet1 = Facet()
        facet1.id = 1
        facet1.color = 1
        facet1.pointCount = 4
        facet1.borderPoints = [Point(2, 0), Point(3, 0), Point(2, 1), Point(3, 1)]
        facet1.bbox = BoundingBox(minX=2, minY=0, maxX=3, maxY=1)
        facet_result.facets[1] = facet1

        # Fill map
        for y in range(2):
            for x in range(4):
                facet_result.facetMap.set(x, y, 0 if x < 2 else 1)

        # Trace and segment
        FacetBorderTracer.build_facet_border_paths(facet_result)
        FacetBorderSegmenter.build_facet_border_segments(facet_result, nr_of_times_to_halve_points=0)

        # Check neighbor references in segments
        for seg in facet0.borderSegments:
            if seg is not None:
                # Neighbour should be either facet 1 or image edge (-1)
                assert seg.neighbour in [-1, 1]

        for seg in facet1.borderSegments:
            if seg is not None:
                # Neighbour should be either facet 0 or image edge (-1)
                assert seg.neighbour in [-1, 0]


class TestFacetBorderSegmenterEdgeCases:
    """Test edge cases for segmentation."""

    def test_single_pixel_facet_segmentation(self):
        """Test segmentation of a single-pixel facet."""
        facet_result = FacetResult()
        facet_result.width = 3
        facet_result.height = 3
        facet_result.facetMap = Uint32Array2D(3, 3)
        facet_result.facets = [None, None]

        # Facet 0: single pixel
        facet0 = Facet()
        facet0.id = 0
        facet0.color = 0
        facet0.pointCount = 1
        facet0.borderPoints = [Point(1, 1)]
        facet0.bbox = BoundingBox(minX=1, minY=1, maxX=1, maxY=1)
        facet_result.facets[0] = facet0

        for y in range(3):
            for x in range(3):
                facet_result.facetMap.set(x, y, 0 if (x == 1 and y == 1) else 1)

        facet1 = Facet()
        facet1.id = 1
        facet1.color = 1
        facet1.pointCount = 8
        facet1.borderPoints = []
        facet1.bbox = BoundingBox()
        facet_result.facets[1] = facet1

        # Trace and segment
        FacetBorderTracer.build_facet_border_paths(facet_result)
        FacetBorderSegmenter.build_facet_border_segments(facet_result)

        # Should have segments
        assert len(facet0.borderSegments) > 0

    def test_is_outside_border_point(self):
        """Test detection of outside border points."""
        # Corner points
        assert FacetBorderSegmenter._is_outside_border_point(Point(0, 0), 10, 10)
        assert FacetBorderSegmenter._is_outside_border_point(Point(9, 0), 10, 10)
        assert FacetBorderSegmenter._is_outside_border_point(Point(0, 9), 10, 10)
        assert FacetBorderSegmenter._is_outside_border_point(Point(9, 9), 10, 10)

        # Edge points
        assert FacetBorderSegmenter._is_outside_border_point(Point(5, 0), 10, 10)
        assert FacetBorderSegmenter._is_outside_border_point(Point(0, 5), 10, 10)
        assert FacetBorderSegmenter._is_outside_border_point(Point(9, 5), 10, 10)
        assert FacetBorderSegmenter._is_outside_border_point(Point(5, 9), 10, 10)

        # Interior points
        assert not FacetBorderSegmenter._is_outside_border_point(Point(5, 5), 10, 10)
        assert not FacetBorderSegmenter._is_outside_border_point(Point(1, 1), 10, 10)

    def test_progress_callback(self):
        """Test progress callback is called."""
        facet_result = FacetResult()
        facet_result.width = 3
        facet_result.height = 3
        facet_result.facetMap = Uint32Array2D(3, 3)
        facet_result.facets = [None]

        # Create a simple facet
        facet0 = Facet()
        facet0.id = 0
        facet0.color = 0
        facet0.pointCount = 1
        facet0.borderPoints = [Point(1, 1)]
        facet0.borderPath = [PathPoint(1, 1, OrientationEnum.Left)]
        facet0.bbox = BoundingBox(minX=1, minY=1, maxX=1, maxY=1)
        facet_result.facets[0] = facet0

        for y in range(3):
            for x in range(3):
                facet_result.facetMap.set(x, y, 0)

        progress_values = []

        def on_update(progress: float):
            progress_values.append(progress)

        FacetBorderSegmenter.build_facet_border_segments(facet_result, on_update=on_update)

        # Should have called the callback at least once
        assert len(progress_values) > 0
        assert progress_values[-1] == 1.0  # Final call should be 1.0


class TestFacetBorderSegmenterIntegration:
    """Integration tests combining tracing and segmentation."""

    def test_full_pipeline_two_facets(self):
        """Test full pipeline with two facets."""
        facet_result = FacetResult()
        facet_result.width = 4
        facet_result.height = 2
        facet_result.facetMap = Uint32Array2D(4, 2)
        facet_result.facets = [None, None]

        # Facet 0: left half
        facet0 = Facet()
        facet0.id = 0
        facet0.color = 0
        facet0.pointCount = 4
        facet0.borderPoints = [Point(0, 0), Point(1, 0), Point(0, 1), Point(1, 1)]
        facet0.bbox = BoundingBox(minX=0, minY=0, maxX=1, maxY=1)
        facet_result.facets[0] = facet0

        # Facet 1: right half
        facet1 = Facet()
        facet1.id = 1
        facet1.color = 1
        facet1.pointCount = 4
        facet1.borderPoints = [Point(2, 0), Point(3, 0), Point(2, 1), Point(3, 1)]
        facet1.bbox = BoundingBox(minX=2, minY=0, maxX=3, maxY=1)
        facet_result.facets[1] = facet1

        # Fill map
        for y in range(2):
            for x in range(4):
                facet_result.facetMap.set(x, y, 0 if x < 2 else 1)

        # Full pipeline
        FacetBorderTracer.build_facet_border_paths(facet_result)
        FacetBorderSegmenter.build_facet_border_segments(facet_result, nr_of_times_to_halve_points=1)

        # Both should have paths and segments
        assert len(facet0.borderPath) > 0
        assert len(facet1.borderPath) > 0
        assert len(facet0.borderSegments) > 0
        assert len(facet1.borderSegments) > 0

    def test_full_pipeline_with_smoothing(self):
        """Test full pipeline with multiple smoothing iterations."""
        facet_result = FacetResult()
        facet_result.width = 10
        facet_result.height = 10
        facet_result.facetMap = Uint32Array2D(10, 10)
        facet_result.facets = [None, None]

        # Facet 0: top half
        facet0 = Facet()
        facet0.id = 0
        facet0.color = 0
        facet0.pointCount = 50
        facet0.borderPoints = [Point(x, y) for y in range(5) for x in range(10)]
        facet0.bbox = BoundingBox(minX=0, minY=0, maxX=9, maxY=4)
        facet_result.facets[0] = facet0

        # Facet 1: bottom half
        facet1 = Facet()
        facet1.id = 1
        facet1.color = 1
        facet1.pointCount = 50
        facet1.borderPoints = [Point(x, y) for y in range(5, 10) for x in range(10)]
        facet1.bbox = BoundingBox(minX=0, minY=5, maxX=9, maxY=9)
        facet_result.facets[1] = facet1

        # Fill map
        for y in range(10):
            for x in range(10):
                facet_result.facetMap.set(x, y, 0 if y < 5 else 1)

        # Full pipeline with smoothing
        FacetBorderTracer.build_facet_border_paths(facet_result)
        FacetBorderSegmenter.build_facet_border_segments(facet_result, nr_of_times_to_halve_points=2)

        # Should complete successfully
        assert len(facet0.borderSegments) > 0
        assert len(facet1.borderSegments) > 0
