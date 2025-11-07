"""Edge case tests for paint-by-numbers generation."""

import pytest
import numpy as np
from paintbynumbers.core.settings import Settings
from paintbynumbers.structs.typed_arrays import Uint8Array2D, Uint32Array2D, BooleanArray2D
from paintbynumbers.processing.colorreduction import ColorReducer, ColorMapResult
from paintbynumbers.processing.facetbuilder import FacetBuilder
from paintbynumbers.processing.facetmanagement import Facet, FacetResult
from paintbynumbers.algorithms.kmeans import KMeans
from paintbynumbers.algorithms.vector import Vector
from paintbynumbers.utils.random import Random


class TestEdgeCasesColorReduction:
    """Test edge cases in color reduction."""

    def test_single_color_image(self):
        """Test image with only one color."""
        # Create image with single color
        img_data = np.full((10, 10, 3), [128, 128, 128], dtype=np.uint8)

        settings = Settings()
        settings.kMeansNrOfClusters = 4

        # Should handle gracefully
        clustered_data, kmeans = ColorReducer.apply_kmeans_clustering(
            img_data, 10, 10, settings
        )

        assert clustered_data.shape == (10, 10, 3)

        # Create color map
        color_map = ColorReducer.create_color_map(clustered_data, 10, 10)

        # Should have only one color
        assert len(color_map.colorsByIndex) == 1

    def test_very_small_image(self):
        """Test with very small image."""
        # 3x3 image
        img_data = np.random.randint(0, 256, (3, 3, 3), dtype=np.uint8)

        settings = Settings()
        settings.kMeansNrOfClusters = 2

        clustered_data, kmeans = ColorReducer.apply_kmeans_clustering(
            img_data, 3, 3, settings
        )

        assert clustered_data.shape == (3, 3, 3)

    def test_more_clusters_than_pixels(self):
        """Test with more clusters than available pixels."""
        # 5x5 image (25 pixels)
        img_data = np.random.randint(0, 256, (5, 5, 3), dtype=np.uint8)

        settings = Settings()
        settings.kMeansNrOfClusters = 50  # More than pixels

        # Should handle gracefully (k-means will use fewer clusters)
        clustered_data, kmeans = ColorReducer.apply_kmeans_clustering(
            img_data, 5, 5, settings
        )

        assert clustered_data is not None


class TestEdgeCasesFacetBuilding:
    """Test edge cases in facet building."""

    def test_empty_facet_result(self):
        """Test with empty facet result."""
        facet_result = FacetResult()
        facet_result.width = 10
        facet_result.height = 10
        facet_result.facetMap = Uint32Array2D(10, 10)
        facet_result.facets = []

        # Should handle empty facet list
        assert len(facet_result.facets) == 0

    def test_single_pixel_facet(self):
        """Test facet with single pixel."""
        facet = Facet()
        facet.id = 0
        facet.color = 0
        facet.pointCount = 1

        assert facet.pointCount == 1
        assert len(facet.borderPoints) == 0

    def test_all_same_color(self):
        """Test image where all pixels are same color."""
        # Create color map with all same color
        color_indices = Uint8Array2D(10, 10)
        for y in range(10):
            for x in range(10):
                color_indices.set(x, y, 0)  # All color 0

        facet_result = FacetResult()
        facet_result.width = 10
        facet_result.height = 10
        facet_result.facetMap = Uint32Array2D(10, 10)

        facet_builder = FacetBuilder()
        facets = facet_builder.build_all_facets(color_indices, 10, 10, facet_result)

        # Should create one facet covering entire image
        assert len(facets) == 1
        assert facets[0].pointCount == 100


class TestEdgeCasesKMeans:
    """Test edge cases in K-means clustering."""

    def test_single_vector(self):
        """Test clustering with single vector."""
        vectors = [Vector([128, 128, 128], weight=1.0)]

        random = Random()
        kmeans = KMeans(vectors, 1, random)
        result = kmeans.get_clusters()

        assert len(result.clusters) == 1

    def test_zero_weight_vectors(self):
        """Test vectors with zero weight."""
        vectors = [
            Vector([255, 0, 0], weight=0.0),
            Vector([0, 255, 0], weight=1.0),
            Vector([0, 0, 255], weight=1.0)
        ]

        random = Random()
        kmeans = KMeans(vectors, 2, random)
        result = kmeans.get_clusters()

        # Should handle zero-weight vectors
        assert len(result.clusters) == 2

    def test_duplicate_vectors(self):
        """Test with duplicate vectors."""
        # All same values
        vectors = [
            Vector([100, 100, 100], weight=1.0),
            Vector([100, 100, 100], weight=1.0),
            Vector([100, 100, 100], weight=1.0)
        ]

        random = Random()
        kmeans = KMeans(vectors, 2, random)
        result = kmeans.get_clusters()

        # Should converge even with duplicates
        assert len(result.clusters) <= 2


class TestEdgeCasesTypedArrays:
    """Test edge cases for typed arrays."""

    def test_single_element_array(self):
        """Test 1x1 arrays."""
        arr = Uint8Array2D(1, 1)
        arr.set(0, 0, 42)

        assert arr.get(0, 0) == 42
        assert arr.shape == (1, 1)

    def test_bounds_checking(self):
        """Test that out-of-bounds access is handled."""
        arr = Uint8Array2D(5, 5)

        # Accessing out of bounds should raise IndexError
        with pytest.raises(IndexError):
            arr.get(10, 10)

        with pytest.raises(IndexError):
            arr.set(10, 10, 42)

    def test_large_out_of_bounds(self):
        """Test handling of large out-of-bounds indices."""
        arr = Uint8Array2D(5, 5)

        # Large out of bounds should raise IndexError
        with pytest.raises(IndexError):
            arr.get(100, 0)

        with pytest.raises(IndexError):
            arr.set(0, 100, 42)

    def test_boolean_array_operations(self):
        """Test boolean array specific operations."""
        arr = BooleanArray2D(3, 3)

        # All should be False initially
        for y in range(3):
            for x in range(3):
                assert arr.get(x, y) == False

        # Set to True
        arr.set(1, 1, True)
        assert arr.get(1, 1) == True

        # Others should still be False
        assert arr.get(0, 0) == False
        assert arr.get(2, 2) == False


class TestEdgeCasesSettings:
    """Test edge cases in settings."""

    def test_zero_clusters(self):
        """Test with zero clusters."""
        settings = Settings()
        settings.kMeansNrOfClusters = 0

        # Should accept 0 (though it may cause issues downstream)
        assert settings.kMeansNrOfClusters == 0

    def test_very_large_cluster_count(self):
        """Test with very large cluster count."""
        settings = Settings()
        settings.kMeansNrOfClusters = 1000

        assert settings.kMeansNrOfClusters == 1000

    def test_negative_facet_size(self):
        """Test with negative facet size threshold."""
        settings = Settings()
        settings.removeFacetsSmallerThanNrOfPoints = -1

        # Should accept negative (though illogical)
        assert settings.removeFacetsSmallerThanNrOfPoints == -1

    def test_settings_roundtrip(self):
        """Test settings JSON roundtrip with edge cases."""
        settings = Settings()
        settings.kMeansNrOfClusters = 0
        settings.removeFacetsSmallerThanNrOfPoints = 999
        settings.maximumNumberOfFacets = None

        # Convert to JSON and back
        json_data = settings.to_json()
        settings2 = Settings.from_json(json_data)

        assert settings2.kMeansNrOfClusters == 0
        assert settings2.removeFacetsSmallerThanNrOfPoints == 999
        assert settings2.maximumNumberOfFacets is None


class TestEdgeCasesVector:
    """Test edge cases in Vector class."""

    def test_zero_dimensional_vector(self):
        """Test vector with no dimensions."""
        vec = Vector([], weight=1.0)

        assert len(vec.values) == 0
        assert vec.weight == 1.0

    def test_single_dimensional_vector(self):
        """Test 1D vector."""
        vec = Vector([42], weight=1.0)

        assert vec.values == [42]

    def test_high_dimensional_vector(self):
        """Test high-dimensional vector."""
        values = list(range(100))
        vec = Vector(values, weight=1.0)

        assert len(vec.values) == 100

    def test_squared_distance_to_identical_vector(self):
        """Test squared distance between identical vectors."""
        vec1 = Vector([1, 2, 3], weight=1.0)
        vec2 = Vector([1, 2, 3], weight=1.0)

        dist = vec1.squared_distance(vec2)
        assert dist == 0.0

    def test_negative_weight(self):
        """Test vector with negative weight."""
        vec = Vector([1, 2, 3], weight=-1.0)

        assert vec.weight == -1.0

    def test_zero_weight(self):
        """Test vector with zero weight."""
        vec = Vector([1, 2, 3], weight=0.0)

        assert vec.weight == 0.0


class TestEdgeCasesBoundingBox:
    """Test edge cases for bounding box."""

    def test_point_bounding_box(self):
        """Test bounding box for a single point."""
        from paintbynumbers.structs.boundingbox import BoundingBox

        bbox = BoundingBox()
        bbox.minX = 5
        bbox.minY = 5
        bbox.maxX = 5
        bbox.maxY = 5

        # width and height are properties, not methods
        assert bbox.width == 0
        assert bbox.height == 0

    def test_contains_boundary(self):
        """Test containment at boundary."""
        from paintbynumbers.structs.boundingbox import BoundingBox

        bbox = BoundingBox()
        bbox.minX = 0
        bbox.minY = 0
        bbox.maxX = 10
        bbox.maxY = 10

        # Points on boundary
        assert bbox.contains(0, 0)
        assert bbox.contains(10, 10)
        assert bbox.contains(5, 0)
        assert bbox.contains(0, 5)

    def test_inverted_bounds(self):
        """Test with inverted bounds (min > max)."""
        from paintbynumbers.structs.boundingbox import BoundingBox

        bbox = BoundingBox()
        bbox.minX = 10
        bbox.minY = 10
        bbox.maxX = 0
        bbox.maxY = 0

        # width and height are properties, not methods
        width = bbox.width
        height = bbox.height

        # Should be negative
        assert width < 0
        assert height < 0
