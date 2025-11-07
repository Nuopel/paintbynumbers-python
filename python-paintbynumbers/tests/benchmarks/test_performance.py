"""Performance benchmarks for paint-by-numbers processing."""

import pytest
import numpy as np
import time
from paintbynumbers.core.settings import Settings, ClusteringColorSpace
from paintbynumbers.processing.colorreduction import ColorReducer
from paintbynumbers.processing.facetbuilder import FacetBuilder
from paintbynumbers.processing.facetmanagement import FacetResult
from paintbynumbers.algorithms.kmeans import KMeans
from paintbynumbers.algorithms.vector import Vector
from paintbynumbers.algorithms.flood_fill import FloodFillAlgorithm
from paintbynumbers.structs.point import Point
from paintbynumbers.structs.typed_arrays import Uint8Array2D, BooleanArray2D, Uint32Array2D


@pytest.fixture
def small_image():
    """Create a small test image (100x100)."""
    return np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)


@pytest.fixture
def medium_image():
    """Create a medium test image (500x500)."""
    return np.random.randint(0, 256, (500, 500, 3), dtype=np.uint8)


@pytest.fixture
def large_image():
    """Create a large test image (1000x1000)."""
    return np.random.randint(0, 256, (1000, 1000, 3), dtype=np.uint8)


class TestKMeansPerformance:
    """Performance benchmarks for K-means clustering."""

    def test_kmeans_small_dataset(self, benchmark):
        """Benchmark K-means on small dataset."""
        # 1000 vectors with 3 dimensions
        vectors = [Vector([np.random.randint(0, 256) for _ in range(3)], weight=1.0)
                   for _ in range(1000)]

        def run_kmeans():
            kmeans = KMeans(vectors, nr_of_clusters=16)
            return kmeans.get_clusters()

        result = benchmark(run_kmeans)
        assert len(result.clusters) == 16

    def test_kmeans_medium_dataset(self, benchmark):
        """Benchmark K-means on medium dataset."""
        # 10000 vectors
        vectors = [Vector([np.random.randint(0, 256) for _ in range(3)], weight=1.0)
                   for _ in range(10000)]

        def run_kmeans():
            kmeans = KMeans(vectors, nr_of_clusters=16)
            return kmeans.get_clusters()

        result = benchmark(run_kmeans)
        assert len(result.clusters) == 16

    def test_kmeans_different_cluster_counts(self):
        """Test K-means performance with different cluster counts."""
        vectors = [Vector([np.random.randint(0, 256) for _ in range(3)], weight=1.0)
                   for _ in range(5000)]

        results = {}
        for k in [4, 8, 16, 32]:
            start = time.time()
            kmeans = KMeans(vectors, nr_of_clusters=k)
            result = kmeans.get_clusters()
            elapsed = time.time() - start
            results[k] = elapsed

            assert len(result.clusters) == k

        # More clusters should generally take longer (but not guaranteed)
        print(f"\nK-means timing: {results}")


class TestColorReductionPerformance:
    """Performance benchmarks for color reduction."""

    def test_color_reduction_small(self, benchmark, small_image):
        """Benchmark color reduction on small image."""
        settings = Settings()
        settings.kMeansNrOfClusters = 16

        def run_reduction():
            return ColorReducer.apply_kmeans_clustering(
                small_image, 100, 100, settings
            )

        clustered_data, kmeans = benchmark(run_reduction)
        assert clustered_data.shape == (100, 100, 3)

    def test_color_reduction_medium(self, benchmark, medium_image):
        """Benchmark color reduction on medium image."""
        settings = Settings()
        settings.kMeansNrOfClusters = 16

        def run_reduction():
            return ColorReducer.apply_kmeans_clustering(
                medium_image, 500, 500, settings
            )

        clustered_data, kmeans = benchmark(run_reduction)
        assert clustered_data.shape == (500, 500, 3)

    def test_create_color_map_small(self, benchmark, small_image):
        """Benchmark color map creation on small image."""
        def run_color_map():
            return ColorReducer.create_color_map(small_image, 100, 100)

        result = benchmark(run_color_map)
        assert result.width == 100
        assert result.height == 100


class TestFloodFillPerformance:
    """Performance benchmarks for flood fill."""

    def test_flood_fill_small_region(self, benchmark):
        """Benchmark flood fill on small region."""
        # Create a 100x100 grid with one color
        grid = BooleanArray2D(100, 100)

        flood_fill = FloodFillAlgorithm()

        def should_fill(x, y):
            return not grid.get(x, y)

        def on_fill(x, y):
            grid.set(x, y, True)

        def run_fill():
            flood_fill.fill_with_callback(
                Point(0, 0),
                100, 100,
                should_fill,
                on_fill
            )

        benchmark(run_fill)

        # Should have filled entire grid
        assert grid.get(99, 99)

    def test_flood_fill_large_region(self, benchmark):
        """Benchmark flood fill on large region."""
        grid = BooleanArray2D(500, 500)

        flood_fill = FloodFillAlgorithm()

        def should_fill(x, y):
            return not grid.get(x, y)

        def on_fill(x, y):
            grid.set(x, y, True)

        def run_fill():
            flood_fill.fill_with_callback(
                Point(0, 0),
                500, 500,
                should_fill,
                on_fill
            )

        benchmark(run_fill)


class TestFacetBuildingPerformance:
    """Performance benchmarks for facet building."""

    def test_facet_building_small(self, benchmark):
        """Benchmark facet building on small image."""
        # Create color indices (checkerboard pattern)
        color_indices = Uint8Array2D(100, 100)
        for y in range(100):
            for x in range(100):
                color_indices.set(x, y, (x // 10 + y // 10) % 4)

        facet_result = FacetResult()
        facet_result.width = 100
        facet_result.height = 100
        facet_result.facetMap = Uint32Array2D(100, 100)

        def run_facet_building():
            facet_builder = FacetBuilder()
            return facet_builder.build_all_facets(
                color_indices, 100, 100, facet_result
            )

        facets = benchmark(run_facet_building)
        assert len(facets) > 0

    def test_facet_neighbor_building(self, benchmark):
        """Benchmark neighbor relationship building."""
        # Create simple facet structure
        color_indices = Uint8Array2D(50, 50)
        for y in range(50):
            for x in range(50):
                color_indices.set(x, y, (x // 10) % 3)

        facet_result = FacetResult()
        facet_result.width = 50
        facet_result.height = 50
        facet_result.facetMap = Uint32Array2D(50, 50)

        facet_builder = FacetBuilder()
        facets = facet_builder.build_all_facets(
            color_indices, 50, 50, facet_result
        )
        facet_result.facets = facets

        def run_neighbor_building():
            for facet in facets:
                if facet is not None:
                    facet_builder.build_facet_neighbour(facet, facet_result)

        benchmark(run_neighbor_building)


class TestTypedArrayPerformance:
    """Performance benchmarks for typed arrays."""

    def test_array_creation(self, benchmark):
        """Benchmark array creation."""
        def create_array():
            return Uint8Array2D(1000, 1000)

        arr = benchmark(create_array)
        assert arr.shape == (1000, 1000)

    def test_array_sequential_access(self, benchmark):
        """Benchmark sequential array access."""
        arr = Uint8Array2D(100, 100)

        def sequential_access():
            total = 0
            for y in range(100):
                for x in range(100):
                    arr.set(x, y, (x + y) % 256)
                    total += arr.get(x, y)
            return total

        result = benchmark(sequential_access)
        assert result > 0

    def test_array_random_access(self, benchmark):
        """Benchmark random array access."""
        arr = Uint8Array2D(100, 100)

        # Pre-generate random coordinates
        coords = [(np.random.randint(0, 100), np.random.randint(0, 100))
                  for _ in range(1000)]

        def random_access():
            total = 0
            for x, y in coords:
                arr.set(x, y, (x + y) % 256)
                total += arr.get(x, y)
            return total

        result = benchmark(random_access)
        assert result > 0


class TestIntegrationPerformance:
    """End-to-end performance benchmarks."""

    def test_full_pipeline_small_image(self):
        """Benchmark full pipeline on small image."""
        img_data = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        settings = Settings()
        settings.kMeansNrOfClusters = 8
        settings.removeFacetsSmallerThanNrOfPoints = 10

        start = time.time()

        # Color reduction
        clustered_data, kmeans = ColorReducer.apply_kmeans_clustering(
            img_data, 100, 100, settings
        )
        color_map = ColorReducer.create_color_map(clustered_data, 100, 100)

        # Facet building
        facet_result = FacetResult()
        facet_result.width = 100
        facet_result.height = 100
        facet_result.facetMap = Uint32Array2D(100, 100)

        facet_builder = FacetBuilder()
        facets = facet_builder.build_all_facets(
            color_map.imgColorIndices, 100, 100, facet_result
        )

        elapsed = time.time() - start

        print(f"\nFull pipeline (100x100): {elapsed:.3f}s")
        assert elapsed < 10.0  # Should complete in reasonable time

    def test_different_color_spaces_performance(self):
        """Compare performance of different color spaces."""
        img_data = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)

        results = {}
        for color_space in [ClusteringColorSpace.RGB,
                           ClusteringColorSpace.HSL,
                           ClusteringColorSpace.LAB]:
            settings = Settings()
            settings.kMeansNrOfClusters = 16
            settings.kMeansClusteringColorSpace = color_space

            start = time.time()
            ColorReducer.apply_kmeans_clustering(img_data, 200, 200, settings)
            elapsed = time.time() - start

            results[color_space.value] = elapsed

        print(f"\nColor space timing: {results}")

        # All should complete in reasonable time
        for elapsed in results.values():
            assert elapsed < 30.0
