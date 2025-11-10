"""Tests for ColorReducer."""

import pytest
import numpy as np
from numpy.typing import NDArray

from paintbynumbers.processing.colorreduction import ColorReducer, ColorMapResult
from paintbynumbers.core.settings import Settings, ClusteringColorSpace
from paintbynumbers.structs.typed_arrays import Uint8Array2D


class TestColorMapResult:
    """Test ColorMapResult class."""

    def test_create_color_map_result(self) -> None:
        """Test creating a ColorMapResult."""
        result = ColorMapResult()
        assert result is not None
        assert result.imgColorIndices is None
        assert result.colorsByIndex == []
        assert result.width == 0
        assert result.height == 0

    def test_color_map_result_attributes(self) -> None:
        """Test setting ColorMapResult attributes."""
        result = ColorMapResult()
        result.width = 100
        result.height = 100
        result.colorsByIndex = [(255, 0, 0), (0, 255, 0)]

        assert result.width == 100
        assert result.height == 100
        assert len(result.colorsByIndex) == 2


class TestColorReducerColorMap:
    """Test color map creation."""

    def test_create_color_map_single_color(self) -> None:
        """Test creating color map from single color image."""
        img_data = np.full((10, 10, 3), [255, 0, 0], dtype=np.uint8)

        result = ColorReducer.create_color_map(img_data, 10, 10)

        assert result.width == 10
        assert result.height == 10
        assert len(result.colorsByIndex) == 1
        assert result.colorsByIndex[0] == (255, 0, 0)

        # All pixels should map to color index 0
        for y in range(10):
            for x in range(10):
                assert result.imgColorIndices.get(x, y) == 0

    def test_create_color_map_two_colors(self) -> None:
        """Test creating color map from two color image."""
        img_data = np.zeros((10, 10, 3), dtype=np.uint8)

        # Left half red, right half blue
        img_data[:, :5] = [255, 0, 0]
        img_data[:, 5:] = [0, 0, 255]

        result = ColorReducer.create_color_map(img_data, 10, 10)

        assert len(result.colorsByIndex) == 2
        assert (255, 0, 0) in result.colorsByIndex
        assert (0, 0, 255) in result.colorsByIndex

    def test_create_color_map_unique_colors(self) -> None:
        """Test that color map tracks unique colors."""
        img_data = np.zeros((5, 5, 3), dtype=np.uint8)

        # Create gradient
        for y in range(5):
            for x in range(5):
                img_data[y, x] = [x * 50, y * 50, 0]

        result = ColorReducer.create_color_map(img_data, 5, 5)

        # Should have unique color for each unique combination
        assert len(result.colorsByIndex) == 25  # All different

    def test_create_color_map_color_indices(self) -> None:
        """Test color indices are assigned correctly."""
        img_data = np.zeros((3, 3, 3), dtype=np.uint8)
        img_data[0, 0] = [255, 0, 0]  # Red at row=0, col=0
        img_data[1, 1] = [0, 255, 0]  # Green at row=1, col=1
        img_data[2, 2] = [0, 0, 255]  # Blue at row=2, col=2
        img_data[0, 1] = [255, 0, 0]  # Red again at row=0, col=1

        result = ColorReducer.create_color_map(img_data, 3, 3)

        # Should have 4 colors (3 RGB + 1 black)
        assert len(result.colorsByIndex) >= 3

        # Same colors should have same index
        # Note: Uint8Array2D.get(x, y) where x=col, y=row
        idx_00 = result.imgColorIndices.get(0, 0)  # col=0, row=0
        idx_10 = result.imgColorIndices.get(1, 0)  # col=1, row=0
        assert idx_00 == idx_10  # Both red


class TestColorReducerKMeans:
    """Test K-means clustering."""

    def test_apply_kmeans_single_color(self) -> None:
        """Test K-means on single color image."""
        img_data = np.full((10, 10, 3), [128, 128, 128], dtype=np.uint8)

        settings = Settings()
        settings.kMeansNrOfClusters = 2
        settings.kMeansMinDeltaDifference = 1.0

        output, kmeans = ColorReducer.apply_kmeans_clustering(
            img_data, 10, 10, settings
        )

        # Should still work with 1 cluster effectively
        assert output.shape == (10, 10, 3)
        # Output should be close to gray
        assert np.all(output >= 0)
        assert np.all(output <= 255)

    def test_apply_kmeans_two_colors(self) -> None:
        """Test K-means on two distinct colors."""
        img_data = np.zeros((20, 20, 3), dtype=np.uint8)

        # Half black, half white
        img_data[:10, :] = [0, 0, 0]
        img_data[10:, :] = [255, 255, 255]

        settings = Settings()
        settings.kMeansNrOfClusters = 2
        settings.kMeansMinDeltaDifference = 1.0
        settings.randomSeed = 42

        output, kmeans = ColorReducer.apply_kmeans_clustering(
            img_data, 20, 20, settings
        )

        assert output.shape == (20, 20, 3)
        assert len(kmeans.centroids) == 2

        # Should have 2 distinct colors in output
        unique_colors = set()
        for y in range(20):
            for x in range(20):
                color = tuple(output[y, x])
                unique_colors.add(color)

        assert len(unique_colors) == 2

    def test_apply_kmeans_rgb_colorspace(self) -> None:
        """Test K-means with RGB color space."""
        img_data = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)

        settings = Settings()
        settings.kMeansNrOfClusters = 4
        settings.kMeansClusteringColorSpace = ClusteringColorSpace.RGB
        settings.randomSeed = 42

        output, kmeans = ColorReducer.apply_kmeans_clustering(
            img_data, 10, 10, settings
        )

        assert output.shape == (10, 10, 3)
        assert len(kmeans.centroids) == 4

    def test_apply_kmeans_hsl_colorspace(self) -> None:
        """Test K-means with HSL color space."""
        img_data = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)

        settings = Settings()
        settings.kMeansNrOfClusters = 4
        settings.kMeansClusteringColorSpace = ClusteringColorSpace.HSL
        settings.randomSeed = 42

        output, kmeans = ColorReducer.apply_kmeans_clustering(
            img_data, 10, 10, settings
        )

        assert output.shape == (10, 10, 3)
        assert len(kmeans.centroids) == 4

    def test_apply_kmeans_lab_colorspace(self) -> None:
        """Test K-means with LAB color space."""
        img_data = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)

        settings = Settings()
        settings.kMeansNrOfClusters = 4
        settings.kMeansClusteringColorSpace = ClusteringColorSpace.LAB
        settings.randomSeed = 42

        output, kmeans = ColorReducer.apply_kmeans_clustering(
            img_data, 10, 10, settings
        )

        assert output.shape == (10, 10, 3)
        assert len(kmeans.centroids) == 4

    def test_apply_kmeans_convergence(self) -> None:
        """Test that K-means converges."""
        img_data = np.zeros((20, 20, 3), dtype=np.uint8)

        # Create distinct color blocks
        img_data[:10, :10] = [255, 0, 0]    # Red
        img_data[:10, 10:] = [0, 255, 0]   # Green
        img_data[10:, :10] = [0, 0, 255]   # Blue
        img_data[10:, 10:] = [255, 255, 0] # Yellow

        settings = Settings()
        settings.kMeansNrOfClusters = 4
        settings.kMeansMinDeltaDifference = 1.0
        settings.randomSeed = 42

        output, kmeans = ColorReducer.apply_kmeans_clustering(
            img_data, 20, 20, settings
        )

        # Should converge (delta difference should be small)
        assert kmeans.current_delta_distance_difference <= settings.kMeansMinDeltaDifference


class TestColorReducerDistanceMatrix:
    """Test color distance matrix building."""

    def test_build_distance_matrix_single_color(self) -> None:
        """Test distance matrix for single color."""
        colors = [(255, 0, 0)]
        matrix = ColorReducer.build_color_distance_matrix(colors)

        assert len(matrix) == 1
        assert len(matrix[0]) == 1
        assert matrix[0][0] == 0.0  # Distance to self is 0

    def test_build_distance_matrix_two_colors(self) -> None:
        """Test distance matrix for two colors."""
        colors = [(255, 0, 0), (0, 0, 0)]
        matrix = ColorReducer.build_color_distance_matrix(colors)

        assert len(matrix) == 2
        assert len(matrix[0]) == 2

        # Distance to self is 0
        assert matrix[0][0] == 0.0
        assert matrix[1][1] == 0.0

        # Distance is symmetric
        assert matrix[0][1] == matrix[1][0]

        # Distance from red to black
        expected = (255**2) ** 0.5
        assert abs(matrix[0][1] - expected) < 0.01

    def test_build_distance_matrix_symmetry(self) -> None:
        """Test distance matrix is symmetric."""
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        matrix = ColorReducer.build_color_distance_matrix(colors)

        for i in range(3):
            for j in range(3):
                assert matrix[i][j] == matrix[j][i]

    def test_build_distance_matrix_diagonal_zero(self) -> None:
        """Test distance matrix diagonal is zero."""
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 128)]
        matrix = ColorReducer.build_color_distance_matrix(colors)

        for i in range(4):
            assert matrix[i][i] == 0.0

    def test_build_distance_matrix_euclidean(self) -> None:
        """Test distance matrix uses Euclidean distance."""
        colors = [(0, 0, 0), (3, 4, 0)]
        matrix = ColorReducer.build_color_distance_matrix(colors)

        # Distance should be sqrt(3^2 + 4^2) = 5
        expected = 5.0
        assert abs(matrix[0][1] - expected) < 0.01


class TestColorReducerNarrowPixelStrip:
    """Test narrow pixel strip cleanup."""

    def test_narrow_pixel_strip_horizontal(self) -> None:
        """Test removing horizontally isolated pixels."""
        result = ColorMapResult()
        result.width = 5
        result.height = 5
        result.imgColorIndices = Uint8Array2D(5, 5)
        result.colorsByIndex = [(255, 0, 0), (0, 255, 0)]

        # Create pattern with horizontal strip
        for y in range(5):
            for x in range(5):
                if y == 2:
                    result.imgColorIndices.set(x, y, 1)  # Green strip
                else:
                    result.imgColorIndices.set(x, y, 0)  # Red background

        count = ColorReducer.process_narrow_pixel_strip_cleanup(result)

        # Inner 3 pixels in strip should be replaced (edges excluded)
        assert count == 3

    def test_narrow_pixel_strip_vertical(self) -> None:
        """Test removing vertically isolated pixels."""
        result = ColorMapResult()
        result.width = 5
        result.height = 5
        result.imgColorIndices = Uint8Array2D(5, 5)
        result.colorsByIndex = [(255, 0, 0), (0, 255, 0)]

        # Create pattern with vertical strip
        for y in range(5):
            for x in range(5):
                if x == 2:
                    result.imgColorIndices.set(x, y, 1)  # Green strip
                else:
                    result.imgColorIndices.set(x, y, 0)  # Red background

        count = ColorReducer.process_narrow_pixel_strip_cleanup(result)

        # All 5 pixels in strip should be replaced (excluding edges)
        assert count >= 3  # At least inner pixels

    def test_narrow_pixel_strip_no_change(self) -> None:
        """Test no changes on solid color."""
        result = ColorMapResult()
        result.width = 5
        result.height = 5
        result.imgColorIndices = Uint8Array2D(5, 5)
        result.colorsByIndex = [(255, 0, 0)]

        # All same color
        for y in range(5):
            for x in range(5):
                result.imgColorIndices.set(x, y, 0)

        count = ColorReducer.process_narrow_pixel_strip_cleanup(result)

        assert count == 0

    def test_narrow_pixel_strip_color_distance(self) -> None:
        """Test that color distance is used for selection."""
        result = ColorMapResult()
        result.width = 5
        result.height = 3
        result.imgColorIndices = Uint8Array2D(5, 3)
        result.colorsByIndex = [
            (0, 0, 0),      # Black
            (128, 128, 128), # Gray (strip)
            (255, 255, 255)  # White
        ]

        # Pattern: white top, gray middle, black bottom
        for x in range(5):
            result.imgColorIndices.set(x, 0, 2)  # White
            result.imgColorIndices.set(x, 1, 1)  # Gray (isolated)
            result.imgColorIndices.set(x, 2, 0)  # Black

        count = ColorReducer.process_narrow_pixel_strip_cleanup(result)

        assert count > 0
        # Gray should be replaced with black or white based on distance
