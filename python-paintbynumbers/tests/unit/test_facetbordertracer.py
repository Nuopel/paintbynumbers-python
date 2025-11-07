"""Tests for FacetBorderTracer border tracing functionality."""

import pytest
from paintbynumbers.processing.facetmanagement import Facet, FacetResult
from paintbynumbers.processing.facetbordertracer import FacetBorderTracer
from paintbynumbers.structs.point import Point
from paintbynumbers.structs.boundingbox import BoundingBox
from paintbynumbers.structs.typed_arrays import Uint32Array2D
from paintbynumbers.core.types import PathPoint, OrientationEnum


class TestFacetBorderTracerBasic:
    """Basic functionality tests for FacetBorderTracer."""

    def test_single_pixel_facet(self):
        """Test border tracing for a single-pixel facet."""
        # Create a 3x3 image with a single pixel facet in the center
        facet_result = FacetResult()
        facet_result.width = 3
        facet_result.height = 3
        facet_result.facetMap = Uint32Array2D(3, 3)
        facet_result.facets = [None, None]

        # Facet 0: single pixel at (1,1)
        facet0 = Facet()
        facet0.id = 0
        facet0.color = 0
        facet0.pointCount = 1
        facet0.borderPoints = [Point(1, 1)]
        facet0.bbox = BoundingBox(minX=1, minY=1, maxX=1, maxY=1)
        facet_result.facets[0] = facet0

        # Fill the map
        for y in range(3):
            for x in range(3):
                facet_result.facetMap.set(x, y, 1 if (x != 1 or y != 1) else 0)

        # Facet 1: surrounding pixels
        facet1 = Facet()
        facet1.id = 1
        facet1.color = 1
        facet1.pointCount = 8
        facet1.borderPoints = []
        facet1.bbox = BoundingBox(minX=0, minY=0, maxX=2, maxY=2)
        facet_result.facets[1] = facet1

        # Trace borders
        FacetBorderTracer.build_facet_border_paths(facet_result)

        # Single pixel should have a path (4 walls around it)
        assert len(facet0.borderPath) >= 4
        assert all(isinstance(pt, PathPoint) for pt in facet0.borderPath)

    def test_2x2_square_facet(self):
        """Test border tracing for a 2x2 square facet."""
        facet_result = FacetResult()
        facet_result.width = 4
        facet_result.height = 4
        facet_result.facetMap = Uint32Array2D(4, 4)
        facet_result.facets = [None, None]

        # Facet 0: 2x2 square at top-left
        facet0 = Facet()
        facet0.id = 0
        facet0.color = 0
        facet0.pointCount = 4
        facet0.borderPoints = [Point(0, 0), Point(1, 0), Point(0, 1), Point(1, 1)]
        facet0.bbox = BoundingBox(minX=0, minY=0, maxX=1, maxY=1)
        facet_result.facets[0] = facet0

        # Set the facet map
        for y in range(4):
            for x in range(4):
                if x < 2 and y < 2:
                    facet_result.facetMap.set(x, y, 0)
                else:
                    facet_result.facetMap.set(x, y, 1)

        # Facet 1: rest
        facet1 = Facet()
        facet1.id = 1
        facet1.color = 1
        facet1.pointCount = 12
        facet1.borderPoints = []
        facet1.bbox = BoundingBox(minX=0, minY=0, maxX=3, maxY=3)
        facet_result.facets[1] = facet1

        # Trace borders
        FacetBorderTracer.build_facet_border_paths(facet_result)

        # Should have a closed path
        assert len(facet0.borderPath) > 0
        # Path should form a loop (more than 4 points for corners)
        assert len(facet0.borderPath) >= 4

    def test_l_shaped_facet(self):
        """Test border tracing for an L-shaped facet."""
        facet_result = FacetResult()
        facet_result.width = 4
        facet_result.height = 4
        facet_result.facetMap = Uint32Array2D(4, 4)
        facet_result.facets = [None, None]

        # Facet 0: L-shape
        # ##__
        # ##__
        # ##__
        # ____
        facet0 = Facet()
        facet0.id = 0
        facet0.color = 0
        facet0.pointCount = 6
        facet0.borderPoints = [
            Point(0, 0), Point(1, 0),
            Point(0, 1), Point(1, 1),
            Point(0, 2), Point(1, 2)
        ]
        facet0.bbox = BoundingBox(minX=0, minY=0, maxX=1, maxY=2)
        facet_result.facets[0] = facet0

        # Set the facet map
        for y in range(4):
            for x in range(4):
                if x < 2 and y < 3:
                    facet_result.facetMap.set(x, y, 0)
                else:
                    facet_result.facetMap.set(x, y, 1)

        facet1 = Facet()
        facet1.id = 1
        facet1.color = 1
        facet1.pointCount = 10
        facet1.borderPoints = []
        facet1.bbox = BoundingBox()
        facet_result.facets[1] = facet1

        # Trace borders
        FacetBorderTracer.build_facet_border_paths(facet_result)

        # Should have a path
        assert len(facet0.borderPath) > 0
        assert all(isinstance(pt, PathPoint) for pt in facet0.borderPath)


class TestFacetBorderTracerOrientations:
    """Test orientation handling in border tracing."""

    def test_path_point_orientations(self):
        """Test that PathPoints have valid orientations."""
        facet_result = FacetResult()
        facet_result.width = 3
        facet_result.height = 3
        facet_result.facetMap = Uint32Array2D(3, 3)
        facet_result.facets = [None, None]

        # Create a simple facet
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

        # Trace borders
        FacetBorderTracer.build_facet_border_paths(facet_result)

        # Check all orientations are valid
        for pt in facet0.borderPath:
            assert pt.orientation in [
                OrientationEnum.Left,
                OrientationEnum.Top,
                OrientationEnum.Right,
                OrientationEnum.Bottom
            ]

    def test_wall_coordinates(self):
        """Test that wall coordinates are calculated correctly."""
        pt_left = PathPoint(5, 5, OrientationEnum.Left)
        assert pt_left.get_wall_x() == 4.5
        assert pt_left.get_wall_y() == 5.0

        pt_right = PathPoint(5, 5, OrientationEnum.Right)
        assert pt_right.get_wall_x() == 5.5
        assert pt_right.get_wall_y() == 5.0

        pt_top = PathPoint(5, 5, OrientationEnum.Top)
        assert pt_top.get_wall_x() == 5.0
        assert pt_top.get_wall_y() == 4.5

        pt_bottom = PathPoint(5, 5, OrientationEnum.Bottom)
        assert pt_bottom.get_wall_x() == 5.0
        assert pt_bottom.get_wall_y() == 5.5


class TestFacetBorderTracerEdgeCases:
    """Test edge cases for border tracing."""

    def test_facet_at_image_edge(self):
        """Test tracing a facet that touches the image boundary."""
        facet_result = FacetResult()
        facet_result.width = 3
        facet_result.height = 3
        facet_result.facetMap = Uint32Array2D(3, 3)
        facet_result.facets = [None, None]

        # Facet 0: top-left corner pixel
        facet0 = Facet()
        facet0.id = 0
        facet0.color = 0
        facet0.pointCount = 1
        facet0.borderPoints = [Point(0, 0)]
        facet0.bbox = BoundingBox(minX=0, minY=0, maxX=0, maxY=0)
        facet_result.facets[0] = facet0

        # Fill map
        for y in range(3):
            for x in range(3):
                facet_result.facetMap.set(x, y, 0 if (x == 0 and y == 0) else 1)

        facet1 = Facet()
        facet1.id = 1
        facet1.color = 1
        facet1.pointCount = 8
        facet1.borderPoints = []
        facet1.bbox = BoundingBox()
        facet_result.facets[1] = facet1

        # Trace borders
        FacetBorderTracer.build_facet_border_paths(facet_result)

        # Should successfully trace the border
        assert len(facet0.borderPath) > 0

    def test_empty_facet_list(self):
        """Test with no facets."""
        facet_result = FacetResult()
        facet_result.width = 3
        facet_result.height = 3
        facet_result.facetMap = Uint32Array2D(3, 3)
        facet_result.facets = []

        # Should not crash
        FacetBorderTracer.build_facet_border_paths(facet_result)

    def test_deleted_facets(self):
        """Test with None entries in facets array."""
        facet_result = FacetResult()
        facet_result.width = 3
        facet_result.height = 3
        facet_result.facetMap = Uint32Array2D(3, 3)
        facet_result.facets = [None, None, None]

        # Should not crash
        FacetBorderTracer.build_facet_border_paths(facet_result)

    def test_progress_callback(self):
        """Test progress callback is called."""
        facet_result = FacetResult()
        facet_result.width = 3
        facet_result.height = 3
        facet_result.facetMap = Uint32Array2D(3, 3)
        facet_result.facets = []

        # Create a simple facet
        facet0 = Facet()
        facet0.id = 0
        facet0.color = 0
        facet0.pointCount = 1
        facet0.borderPoints = [Point(1, 1)]
        facet0.bbox = BoundingBox(minX=1, minY=1, maxX=1, maxY=1)
        facet_result.facets.append(facet0)

        for y in range(3):
            for x in range(3):
                facet_result.facetMap.set(x, y, 0)

        progress_values = []

        def on_update(progress: float):
            progress_values.append(progress)

        FacetBorderTracer.build_facet_border_paths(facet_result, on_update=on_update)

        # Should have called the callback at least once
        assert len(progress_values) > 0
        assert progress_values[-1] == 1.0  # Final call should be 1.0


class TestFacetBorderTracerIntegration:
    """Integration tests with multiple facets."""

    def test_two_adjacent_facets(self):
        """Test tracing two adjacent facets."""
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

        # Trace borders
        FacetBorderTracer.build_facet_border_paths(facet_result)

        # Both should have paths
        assert len(facet0.borderPath) > 0
        assert len(facet1.borderPath) > 0

    def test_diagonal_connection(self):
        """Test tracing facets with diagonal connections."""
        facet_result = FacetResult()
        facet_result.width = 3
        facet_result.height = 3
        facet_result.facetMap = Uint32Array2D(3, 3)
        facet_result.facets = [None, None]

        # Facet 0: checkerboard pattern
        # #_#
        # _#_
        # #_#
        facet0 = Facet()
        facet0.id = 0
        facet0.color = 0
        facet0.pointCount = 5
        facet0.borderPoints = [
            Point(0, 0), Point(2, 0),
            Point(1, 1),
            Point(0, 2), Point(2, 2)
        ]
        facet0.bbox = BoundingBox(minX=0, minY=0, maxX=2, maxY=2)
        facet_result.facets[0] = facet0

        # Fill map
        for y in range(3):
            for x in range(3):
                if (x + y) % 2 == 0:
                    facet_result.facetMap.set(x, y, 0)
                else:
                    facet_result.facetMap.set(x, y, 1)

        facet1 = Facet()
        facet1.id = 1
        facet1.color = 1
        facet1.pointCount = 4
        facet1.borderPoints = []
        facet1.bbox = BoundingBox()
        facet_result.facets[1] = facet1

        # Trace borders
        FacetBorderTracer.build_facet_border_paths(facet_result)

        # Should have paths (might be complex due to disconnected regions)
        # Note: In real usage, disconnected regions would be separate facets
        assert len(facet0.borderPath) > 0


class TestPathPointNeighbour:
    """Test PathPoint get_neighbour functionality."""

    def test_get_neighbour_left(self):
        """Test getting left neighbour."""
        facet_result = FacetResult()
        facet_result.width = 3
        facet_result.height = 3
        facet_result.facetMap = Uint32Array2D(3, 3)

        facet_result.facetMap.set(0, 1, 5)
        facet_result.facetMap.set(1, 1, 7)

        pt = PathPoint(1, 1, OrientationEnum.Left)
        neighbour = pt.get_neighbour(facet_result)
        assert neighbour == 5

    def test_get_neighbour_right(self):
        """Test getting right neighbour."""
        facet_result = FacetResult()
        facet_result.width = 3
        facet_result.height = 3
        facet_result.facetMap = Uint32Array2D(3, 3)

        facet_result.facetMap.set(1, 1, 7)
        facet_result.facetMap.set(2, 1, 9)

        pt = PathPoint(1, 1, OrientationEnum.Right)
        neighbour = pt.get_neighbour(facet_result)
        assert neighbour == 9

    def test_get_neighbour_top(self):
        """Test getting top neighbour."""
        facet_result = FacetResult()
        facet_result.width = 3
        facet_result.height = 3
        facet_result.facetMap = Uint32Array2D(3, 3)

        facet_result.facetMap.set(1, 0, 3)
        facet_result.facetMap.set(1, 1, 7)

        pt = PathPoint(1, 1, OrientationEnum.Top)
        neighbour = pt.get_neighbour(facet_result)
        assert neighbour == 3

    def test_get_neighbour_bottom(self):
        """Test getting bottom neighbour."""
        facet_result = FacetResult()
        facet_result.width = 3
        facet_result.height = 3
        facet_result.facetMap = Uint32Array2D(3, 3)

        facet_result.facetMap.set(1, 1, 7)
        facet_result.facetMap.set(1, 2, 11)

        pt = PathPoint(1, 1, OrientationEnum.Bottom)
        neighbour = pt.get_neighbour(facet_result)
        assert neighbour == 11

    def test_get_neighbour_out_of_bounds(self):
        """Test getting neighbour when out of bounds."""
        facet_result = FacetResult()
        facet_result.width = 3
        facet_result.height = 3
        facet_result.facetMap = Uint32Array2D(3, 3)

        # Left edge
        pt = PathPoint(0, 1, OrientationEnum.Left)
        assert pt.get_neighbour(facet_result) == -1

        # Right edge
        pt = PathPoint(2, 1, OrientationEnum.Right)
        assert pt.get_neighbour(facet_result) == -1

        # Top edge
        pt = PathPoint(1, 0, OrientationEnum.Top)
        assert pt.get_neighbour(facet_result) == -1

        # Bottom edge
        pt = PathPoint(1, 2, OrientationEnum.Bottom)
        assert pt.get_neighbour(facet_result) == -1
