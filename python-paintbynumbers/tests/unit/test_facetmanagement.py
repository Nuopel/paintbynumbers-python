"""Tests for facet management."""

import pytest
from paintbynumbers.processing.facetmanagement import Facet, FacetResult
from paintbynumbers.structs.point import Point
from paintbynumbers.structs.boundingbox import BoundingBox
from paintbynumbers.structs.typed_arrays import Uint32Array2D


class TestFacet:
    """Test Facet class."""

    def test_create_facet(self) -> None:
        """Test creating a facet."""
        facet = Facet()
        assert facet is not None
        assert facet.id == -1
        assert facet.color == -1
        assert facet.pointCount == 0
        assert facet.borderPoints == []
        assert facet.neighbourFacets is None
        assert facet.neighbourFacetsIsDirty is False

    def test_facet_id(self) -> None:
        """Test setting facet ID."""
        facet = Facet()
        facet.id = 5
        assert facet.id == 5

    def test_facet_color(self) -> None:
        """Test setting facet color."""
        facet = Facet()
        facet.color = 10
        assert facet.color == 10

    def test_facet_point_count(self) -> None:
        """Test facet point count."""
        facet = Facet()
        facet.pointCount = 100
        assert facet.pointCount == 100

    def test_facet_border_points(self) -> None:
        """Test facet border points."""
        facet = Facet()
        facet.borderPoints = [Point(0, 0), Point(1, 0), Point(2, 0)]
        assert len(facet.borderPoints) == 3
        assert Point(1, 0) in facet.borderPoints

    def test_facet_bounding_box(self) -> None:
        """Test facet bounding box."""
        facet = Facet()
        facet.bbox = BoundingBox()
        facet.bbox.minX = 5
        facet.bbox.maxX = 10
        assert facet.bbox.minX == 5
        assert facet.bbox.maxX == 10

    def test_facet_neighbours(self) -> None:
        """Test facet neighbours."""
        facet = Facet()
        facet.neighbourFacets = [1, 2, 3]
        assert len(facet.neighbourFacets) == 3
        assert 2 in facet.neighbourFacets

    def test_facet_neighbours_dirty_flag(self) -> None:
        """Test neighbour dirty flag."""
        facet = Facet()
        assert facet.neighbourFacetsIsDirty is False
        facet.neighbourFacetsIsDirty = True
        assert facet.neighbourFacetsIsDirty is True

    def test_facet_repr(self) -> None:
        """Test facet string representation."""
        facet = Facet()
        facet.id = 5
        facet.color = 10
        facet.pointCount = 100
        facet.borderPoints = [Point(0, 0), Point(1, 0)]

        repr_str = repr(facet)
        assert "Facet" in repr_str
        assert "id=5" in repr_str
        assert "color=10" in repr_str
        assert "pointCount=100" in repr_str
        assert "borderPoints=2" in repr_str


class TestFacetResult:
    """Test FacetResult class."""

    def test_create_facet_result(self) -> None:
        """Test creating a facet result."""
        result = FacetResult()
        assert result is not None
        assert result.facetMap is None
        assert result.facets == []
        assert result.width == 0
        assert result.height == 0

    def test_facet_result_dimensions(self) -> None:
        """Test setting dimensions."""
        result = FacetResult()
        result.width = 100
        result.height = 100
        assert result.width == 100
        assert result.height == 100

    def test_facet_result_facet_map(self) -> None:
        """Test facet map."""
        result = FacetResult()
        result.width = 10
        result.height = 10
        result.facetMap = Uint32Array2D(10, 10)

        result.facetMap.set(5, 5, 3)
        assert result.facetMap.get(5, 5) == 3

    def test_facet_result_facets_list(self) -> None:
        """Test facets list."""
        result = FacetResult()

        facet1 = Facet()
        facet1.id = 0
        facet2 = Facet()
        facet2.id = 1

        result.facets = [facet1, facet2]
        assert len(result.facets) == 2
        assert result.facets[0].id == 0
        assert result.facets[1].id == 1

    def test_facet_result_with_none(self) -> None:
        """Test facets list with None (deleted facets)."""
        result = FacetResult()

        facet1 = Facet()
        facet1.id = 0

        result.facets = [facet1, None, Facet()]
        assert len(result.facets) == 3
        assert result.facets[0] is not None
        assert result.facets[1] is None
        assert result.facets[2] is not None

    def test_get_facet_count_empty(self) -> None:
        """Test get_facet_count with empty list."""
        result = FacetResult()
        assert result.get_facet_count() == 0

    def test_get_facet_count_all_facets(self) -> None:
        """Test get_facet_count with all valid facets."""
        result = FacetResult()
        result.facets = [Facet(), Facet(), Facet()]
        assert result.get_facet_count() == 3

    def test_get_facet_count_with_none(self) -> None:
        """Test get_facet_count with deleted facets."""
        result = FacetResult()
        result.facets = [Facet(), None, Facet(), None, Facet()]
        assert result.get_facet_count() == 3

    def test_get_facet_count_all_none(self) -> None:
        """Test get_facet_count with all deleted."""
        result = FacetResult()
        result.facets = [None, None, None]
        assert result.get_facet_count() == 0

    def test_facet_result_repr(self) -> None:
        """Test facet result string representation."""
        result = FacetResult()
        result.width = 100
        result.height = 100
        result.facets = [Facet(), None, Facet()]

        repr_str = repr(result)
        assert "FacetResult" in repr_str
        assert "width=100" in repr_str
        assert "height=100" in repr_str
        assert "facets=2/3" in repr_str  # 2 non-None out of 3 total

    def test_facet_result_integration(self) -> None:
        """Test full facet result integration."""
        result = FacetResult()
        result.width = 5
        result.height = 5
        result.facetMap = Uint32Array2D(5, 5)

        # Create 2 facets
        facet1 = Facet()
        facet1.id = 0
        facet1.color = 1
        facet1.pointCount = 10

        facet2 = Facet()
        facet2.id = 1
        facet2.color = 2
        facet2.pointCount = 15

        result.facets = [facet1, facet2]

        # Set some pixels
        result.facetMap.set(0, 0, 0)
        result.facetMap.set(1, 1, 1)

        assert result.get_facet_count() == 2
        assert result.facetMap.get(0, 0) == 0
        assert result.facetMap.get(1, 1) == 1
