"""Tests for FacetBuilder."""

import pytest
from paintbynumbers.processing.facetbuilder import FacetBuilder
from paintbynumbers.processing.facetmanagement import Facet, FacetResult
from paintbynumbers.structs.point import Point
from paintbynumbers.structs.boundingbox import BoundingBox
from paintbynumbers.structs.typed_arrays import BooleanArray2D, Uint8Array2D, Uint32Array2D


class TestFacetBuilderBasic:
    """Test basic FacetBuilder functionality."""

    def test_create_facet_builder(self) -> None:
        """Test creating a FacetBuilder."""
        builder = FacetBuilder()
        assert builder is not None

    def test_build_single_pixel_facet(self) -> None:
        """Test building a single pixel facet."""
        builder = FacetBuilder()

        # Create 3x3 color map with single color at center
        color_map = Uint8Array2D(3, 3)
        for y in range(3):
            for x in range(3):
                color_map.set(x, y, 0)
        color_map.set(1, 1, 1)  # Center is different color

        visited = BooleanArray2D(3, 3)
        result = FacetResult()
        result.width = 3
        result.height = 3
        result.facetMap = Uint32Array2D(3, 3)
        result.facets = []

        facet = builder.build_facet(0, 1, 1, 1, visited, color_map, result)

        assert facet.id == 0
        assert facet.color == 1
        assert facet.pointCount == 1
        assert len(facet.borderPoints) == 1
        assert Point(1, 1) in facet.borderPoints

    def test_build_horizontal_line_facet(self) -> None:
        """Test building a horizontal line facet."""
        builder = FacetBuilder()

        # Create 5x3 color map with horizontal line
        color_map = Uint8Array2D(5, 3)
        for y in range(3):
            for x in range(5):
                color_map.set(x, y, 0)
        # Horizontal line at y=1
        for x in range(5):
            color_map.set(x, 1, 1)

        visited = BooleanArray2D(5, 3)
        result = FacetResult()
        result.width = 5
        result.height = 3
        result.facetMap = Uint32Array2D(5, 3)
        result.facets = []

        facet = builder.build_facet(0, 1, 2, 1, visited, color_map, result)

        assert facet.id == 0
        assert facet.color == 1
        assert facet.pointCount == 5
        # All 5 pixels are border pixels (top and bottom neighbors different)
        assert len(facet.borderPoints) == 5

    def test_build_rectangle_facet(self) -> None:
        """Test building a rectangular facet."""
        builder = FacetBuilder()

        # Create 5x5 color map with 3x3 rectangle
        color_map = Uint8Array2D(5, 5)
        for y in range(5):
            for x in range(5):
                color_map.set(x, y, 0)

        # 3x3 rectangle in center
        for y in range(1, 4):
            for x in range(1, 4):
                color_map.set(x, y, 1)

        visited = BooleanArray2D(5, 5)
        result = FacetResult()
        result.width = 5
        result.height = 5
        result.facetMap = Uint32Array2D(5, 5)
        result.facets = []

        facet = builder.build_facet(0, 1, 2, 2, visited, color_map, result)

        assert facet.id == 0
        assert facet.color == 1
        assert facet.pointCount == 9  # 3x3
        # Border is outer ring: 8 pixels (center pixel is not border)
        assert len(facet.borderPoints) == 8

    def test_build_facet_bounding_box(self) -> None:
        """Test that bounding box is calculated correctly."""
        builder = FacetBuilder()

        color_map = Uint8Array2D(10, 10)
        for y in range(10):
            for x in range(10):
                color_map.set(x, y, 0)

        # Rectangle from (2,3) to (5,7)
        for y in range(3, 8):
            for x in range(2, 6):
                color_map.set(x, y, 1)

        visited = BooleanArray2D(10, 10)
        result = FacetResult()
        result.width = 10
        result.height = 10
        result.facetMap = Uint32Array2D(10, 10)
        result.facets = []

        facet = builder.build_facet(0, 1, 4, 5, visited, color_map, result)

        assert facet.bbox.minX == 2
        assert facet.bbox.maxX == 5
        assert facet.bbox.minY == 3
        assert facet.bbox.maxY == 7


class TestFacetBuilderAllFacets:
    """Test building all facets from image."""

    def test_build_all_facets_single_color(self) -> None:
        """Test building facets from single color image."""
        builder = FacetBuilder()

        color_map = Uint8Array2D(10, 10)
        for y in range(10):
            for x in range(10):
                color_map.set(x, y, 0)

        result = FacetResult()
        result.width = 10
        result.height = 10
        result.facetMap = Uint32Array2D(10, 10)
        result.facets = []

        facets = builder.build_all_facets(color_map, 10, 10, result)

        assert len(facets) == 1
        assert facets[0].color == 0
        assert facets[0].pointCount == 100

    def test_build_all_facets_two_colors(self) -> None:
        """Test building facets from two color image."""
        builder = FacetBuilder()

        # Half and half
        color_map = Uint8Array2D(10, 10)
        for y in range(10):
            for x in range(10):
                if x < 5:
                    color_map.set(x, y, 0)
                else:
                    color_map.set(x, y, 1)

        result = FacetResult()
        result.width = 10
        result.height = 10
        result.facetMap = Uint32Array2D(10, 10)
        result.facets = []

        facets = builder.build_all_facets(color_map, 10, 10, result)

        assert len(facets) == 2
        assert facets[0].pointCount == 50
        assert facets[1].pointCount == 50

    def test_build_all_facets_checkerboard(self) -> None:
        """Test building facets from checkerboard."""
        builder = FacetBuilder()

        # 4x4 checkerboard
        color_map = Uint8Array2D(4, 4)
        for y in range(4):
            for x in range(4):
                color_map.set(x, y, (x + y) % 2)

        result = FacetResult()
        result.width = 4
        result.height = 4
        result.facetMap = Uint32Array2D(4, 4)
        result.facets = []

        facets = builder.build_all_facets(color_map, 4, 4, result)

        # Each square is separate facet (no 4-connectivity)
        assert len(facets) == 16
        for facet in facets:
            assert facet.pointCount == 1


class TestFacetBuilderNeighbours:
    """Test finding facet neighbours."""

    def test_build_facet_neighbour_two_facets(self) -> None:
        """Test finding neighbours between two facets."""
        builder = FacetBuilder()

        # Two facets side by side
        color_map = Uint8Array2D(10, 5)
        for y in range(5):
            for x in range(10):
                if x < 5:
                    color_map.set(x, y, 0)
                else:
                    color_map.set(x, y, 1)

        result = FacetResult()
        result.width = 10
        result.height = 5
        result.facetMap = Uint32Array2D(10, 5)
        result.facets = []

        facets = builder.build_all_facets(color_map, 10, 5, result)
        result.facets = facets

        builder.build_facet_neighbour(facets[0], result)
        builder.build_facet_neighbour(facets[1], result)

        assert facets[0].neighbourFacets == [1]
        assert facets[1].neighbourFacets == [0]
        assert facets[0].neighbourFacetsIsDirty is False
        assert facets[1].neighbourFacetsIsDirty is False

    def test_build_facet_neighbour_four_facets(self) -> None:
        """Test finding neighbours in 2x2 grid."""
        builder = FacetBuilder()

        # 2x2 grid of colors
        color_map = Uint8Array2D(10, 10)
        for y in range(10):
            for x in range(10):
                if y < 5:
                    color = 0 if x < 5 else 1
                else:
                    color = 2 if x < 5 else 3
                color_map.set(x, y, color)

        result = FacetResult()
        result.width = 10
        result.height = 10
        result.facetMap = Uint32Array2D(10, 10)
        result.facets = []

        facets = builder.build_all_facets(color_map, 10, 10, result)
        result.facets = facets

        for facet in facets:
            builder.build_facet_neighbour(facet, result)

        # Top-left (0) neighbours: top-right(1), bottom-left(2)
        assert len(facets[0].neighbourFacets) == 2
        assert 1 in facets[0].neighbourFacets
        assert 2 in facets[0].neighbourFacets

        # Center facets have 3 neighbours
        # But since each facet is connected, all should have 2-3 neighbours

    def test_build_facet_neighbour_isolated(self) -> None:
        """Test facet with no neighbours (single color image)."""
        builder = FacetBuilder()

        color_map = Uint8Array2D(5, 5)
        for y in range(5):
            for x in range(5):
                color_map.set(x, y, 0)

        result = FacetResult()
        result.width = 5
        result.height = 5
        result.facetMap = Uint32Array2D(5, 5)
        result.facets = []

        facets = builder.build_all_facets(color_map, 5, 5, result)
        result.facets = facets

        builder.build_facet_neighbour(facets[0], result)

        assert facets[0].neighbourFacets == []


class TestFacetBuilderBoundingBox:
    """Test bounding box calculation."""

    def test_calculate_bounding_box_empty(self) -> None:
        """Test bounding box with empty points list."""
        builder = FacetBuilder()
        bbox = builder.calculate_bounding_box([])

        # Should return default BoundingBox
        assert isinstance(bbox, BoundingBox)

    def test_calculate_bounding_box_single_point(self) -> None:
        """Test bounding box with single point."""
        builder = FacetBuilder()
        points = [Point(5, 10)]
        bbox = builder.calculate_bounding_box(points)

        assert bbox.minX == 5
        assert bbox.maxX == 5
        assert bbox.minY == 10
        assert bbox.maxY == 10

    def test_calculate_bounding_box_multiple_points(self) -> None:
        """Test bounding box with multiple points."""
        builder = FacetBuilder()
        points = [
            Point(5, 10),
            Point(15, 20),
            Point(8, 12),
            Point(3, 25)
        ]
        bbox = builder.calculate_bounding_box(points)

        assert bbox.minX == 3
        assert bbox.maxX == 15
        assert bbox.minY == 10
        assert bbox.maxY == 25

    def test_calculate_bounding_box_line(self) -> None:
        """Test bounding box for horizontal line."""
        builder = FacetBuilder()
        points = [Point(x, 5) for x in range(10)]
        bbox = builder.calculate_bounding_box(points)

        assert bbox.minX == 0
        assert bbox.maxX == 9
        assert bbox.minY == 5
        assert bbox.maxY == 5


class TestFacetBuilderBorderPoints:
    """Test border point identification."""

    def test_identify_border_points_single_pixel(self) -> None:
        """Test border identification for single pixel."""
        builder = FacetBuilder()
        points = [Point(5, 5)]
        border = builder.identify_border_points(points, 10, 10)

        # Single pixel is always border
        assert len(border) == 1
        assert Point(5, 5) in border

    def test_identify_border_points_rectangle(self) -> None:
        """Test border identification for rectangle."""
        builder = FacetBuilder()
        # 3x3 rectangle
        points = []
        for y in range(3):
            for x in range(3):
                points.append(Point(x, y))

        border = builder.identify_border_points(points, 10, 10)

        # Border is outer ring: 8 pixels
        assert len(border) == 8
        # Center pixel should not be border
        assert Point(1, 1) not in border
        # Corner pixels should be border
        assert Point(0, 0) in border
        assert Point(2, 2) in border

    def test_identify_border_points_line(self) -> None:
        """Test border identification for line."""
        builder = FacetBuilder()
        points = [Point(x, 5) for x in range(10)]
        border = builder.identify_border_points(points, 20, 20)

        # All pixels in line are border (top/bottom neighbors missing)
        assert len(border) == 10

    def test_identify_border_points_at_image_edge(self) -> None:
        """Test border identification at image edge."""
        builder = FacetBuilder()
        # Line at top edge
        points = [Point(x, 0) for x in range(5)]
        border = builder.identify_border_points(points, 10, 10)

        # All are border (at image edge)
        assert len(border) == 5

    def test_identify_border_points_l_shape(self) -> None:
        """Test border identification for L-shape."""
        builder = FacetBuilder()
        # L-shape
        points = [
            Point(0, 0), Point(1, 0), Point(2, 0),
            Point(0, 1),
            Point(0, 2)
        ]
        border = builder.identify_border_points(points, 10, 10)

        # All L-shape pixels are border
        assert len(border) == 5
