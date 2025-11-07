"""Tests for KMeans clustering algorithm."""

import pytest
from paintbynumbers.algorithms.kmeans import KMeans
from paintbynumbers.algorithms.vector import Vector
from paintbynumbers.utils.random import Random


class TestKMeansInit:
    """Test KMeans initialization."""

    def test_create_kmeans(self) -> None:
        """Test creating KMeans instance."""
        random = Random(42)
        points = [Vector([1, 2]), Vector([3, 4])]

        kmeans = KMeans(points, 2, random)

        assert kmeans.k == 2
        assert kmeans.current_iteration == 0
        assert len(kmeans.centroids) == 2
        assert len(kmeans.points_per_category) == 2

    def test_random_initialization(self) -> None:
        """Test that centroids are initialized randomly."""
        random = Random(42)
        points = [
            Vector([1, 1]),
            Vector([2, 2]),
            Vector([3, 3]),
            Vector([4, 4]),
        ]

        kmeans = KMeans(points, 2, random)

        # Centroids should be from the dataset
        assert len(kmeans.centroids) == 2
        for centroid in kmeans.centroids:
            # Each centroid should match one of the points
            assert any(centroid.values == p.values for p in points)

    def test_deterministic_initialization(self) -> None:
        """Test that same seed produces same initialization."""
        points = [
            Vector([1, 1]),
            Vector([2, 2]),
            Vector([3, 3]),
            Vector([4, 4]),
        ]

        kmeans1 = KMeans(points, 2, Random(42))
        kmeans2 = KMeans(points, 2, Random(42))

        # Same seed should give same initial centroids
        assert kmeans1.centroids[0].values == kmeans2.centroids[0].values
        assert kmeans1.centroids[1].values == kmeans2.centroids[1].values

    def test_custom_centroids(self) -> None:
        """Test initializing with custom centroids."""
        random = Random(42)
        points = [Vector([1, 1]), Vector([9, 9])]

        custom_centroids = [
            Vector([0, 0]),
            Vector([10, 10]),
        ]

        kmeans = KMeans(points, 2, random, custom_centroids)

        assert kmeans.centroids[0].values == [0, 0]
        assert kmeans.centroids[1].values == [10, 10]


class TestKMeansStep:
    """Test KMeans step() method."""

    def test_single_step(self) -> None:
        """Test performing a single step."""
        random = Random(42)
        points = [
            Vector([1, 1]),
            Vector([2, 2]),
            Vector([9, 9]),
            Vector([10, 10]),
        ]

        # Use sub-optimal centroids that will need to move
        centroids = [Vector([0, 0]), Vector([10, 10])]
        kmeans = KMeans(points, 2, random, centroids)

        kmeans.step()

        assert kmeans.current_iteration == 1
        # Should have moved centroids (they were sub-optimal)
        assert kmeans.current_delta_distance_difference > 0

    def test_assignment_step(self) -> None:
        """Test that points are assigned to nearest centroid."""
        random = Random(42)
        points = [
            Vector([1, 1]),
            Vector([2, 2]),
            Vector([9, 9]),
            Vector([10, 10]),
        ]

        centroids = [Vector([1.5, 1.5]), Vector([9.5, 9.5])]
        kmeans = KMeans(points, 2, random, centroids)

        kmeans.step()

        # First two points should be in cluster 0
        assert len(kmeans.points_per_category[0]) == 2
        # Last two points should be in cluster 1
        assert len(kmeans.points_per_category[1]) == 2

    def test_update_step(self) -> None:
        """Test that centroids are updated correctly."""
        random = Random(42)
        points = [
            Vector([0, 0]),
            Vector([2, 2]),
        ]

        centroids = [Vector([0, 0]), Vector([10, 10])]
        kmeans = KMeans(points, 2, random, centroids)

        kmeans.step()

        # Both points should be assigned to first centroid (closer)
        # New centroid should be their average
        new_centroid = kmeans.centroids[0]
        assert new_centroid.values == [1.0, 1.0]

    def test_convergence(self) -> None:
        """Test that algorithm converges."""
        random = Random(42)
        points = [
            Vector([1, 1]),
            Vector([2, 2]),
            Vector([9, 9]),
            Vector([10, 10]),
        ]

        kmeans = KMeans(points, 2, random)

        # Run until convergence
        max_iterations = 100
        for _ in range(max_iterations):
            kmeans.step()
            if kmeans.has_converged(0.01):
                break

        # Should converge quickly for this simple case
        assert kmeans.current_iteration < 20
        assert kmeans.has_converged(0.01)

    def test_multiple_steps_decrease_movement(self) -> None:
        """Test that centroid movement decreases over iterations."""
        random = Random(42)
        points = [
            Vector([1, 1]),
            Vector([2, 2]),
            Vector([9, 9]),
            Vector([10, 10]),
        ]

        kmeans = KMeans(points, 2, random)

        # First step
        kmeans.step()
        first_movement = kmeans.current_delta_distance_difference

        # Continue stepping
        for _ in range(5):
            kmeans.step()

        last_movement = kmeans.current_delta_distance_difference

        # Movement should decrease as it converges
        # (May not be strictly monotonic, but final should be less)
        assert last_movement < first_movement or last_movement < 0.01


class TestKMeansClassify:
    """Test KMeans classify() method."""

    def test_classify_point(self) -> None:
        """Test classifying a point to nearest cluster."""
        random = Random(42)
        points = [Vector([1, 1]), Vector([9, 9])]

        centroids = [Vector([0, 0]), Vector([10, 10])]
        kmeans = KMeans(points, 2, random, centroids)

        # Point close to first centroid
        cluster = kmeans.classify(Vector([1, 1]))
        assert cluster == 0

        # Point close to second centroid
        cluster = kmeans.classify(Vector([9, 9]))
        assert cluster == 1

    def test_classify_midpoint(self) -> None:
        """Test classifying midpoint."""
        random = Random(42)
        points = [Vector([0, 0]), Vector([10, 10])]

        centroids = [Vector([0, 0]), Vector([10, 10])]
        kmeans = KMeans(points, 2, random, centroids)

        # Midpoint - should go to one of them
        cluster = kmeans.classify(Vector([5, 5]))
        assert cluster in [0, 1]


class TestKMeansConvergence:
    """Test KMeans convergence detection."""

    def test_has_converged_true(self) -> None:
        """Test has_converged returns True when below threshold."""
        random = Random(42)
        points = [Vector([1, 1]), Vector([2, 2])]

        kmeans = KMeans(points, 1, random)
        kmeans.current_delta_distance_difference = 0.5

        assert kmeans.has_converged(1.0)
        assert kmeans.has_converged(0.5)

    def test_has_converged_false(self) -> None:
        """Test has_converged returns False when above threshold."""
        random = Random(42)
        points = [Vector([1, 1]), Vector([2, 2])]

        kmeans = KMeans(points, 1, random)
        kmeans.current_delta_distance_difference = 2.0

        assert not kmeans.has_converged(1.0)

    def test_has_converged_exact(self) -> None:
        """Test has_converged at exact threshold."""
        random = Random(42)
        points = [Vector([1, 1]), Vector([2, 2])]

        kmeans = KMeans(points, 1, random)
        kmeans.current_delta_distance_difference = 1.0

        assert kmeans.has_converged(1.0)


class TestKMeansWeighted:
    """Test KMeans with weighted vectors."""

    def test_weighted_averaging(self) -> None:
        """Test that weights affect centroid calculation."""
        random = Random(42)

        # One point with weight 1, another with weight 9
        points = [
            Vector([0, 0], 1.0),
            Vector([10, 10], 9.0),
        ]

        centroids = [Vector([5, 5])]
        kmeans = KMeans(points, 1, random, centroids)

        kmeans.step()

        # Weighted average should be (1*0 + 9*10) / (1+9) = 9
        new_centroid = kmeans.centroids[0]
        assert abs(new_centroid.values[0] - 9.0) < 1e-10
        assert abs(new_centroid.values[1] - 9.0) < 1e-10

    def test_weighted_color_clustering(self) -> None:
        """Test weighted clustering for color quantization."""
        random = Random(42)

        # Simulate color frequencies
        # 10 pixels of red, 1 pixel of green
        red = Vector([255, 0, 0], 10.0)
        green = Vector([0, 255, 0], 1.0)

        points = [red, green]
        centroids = [Vector([127, 127, 0])]

        kmeans = KMeans(points, 1, random, centroids)
        kmeans.step()

        # Centroid should be much closer to red due to weight
        centroid = kmeans.centroids[0]
        # Weighted avg: (10*255 + 1*0) / 11 = 231.8...
        assert centroid.values[0] > 230  # Mostly red
        assert centroid.values[1] < 25   # Little green


class TestKMeansDeterminism:
    """Test that KMeans is deterministic with same seed."""

    def test_deterministic_clustering(self) -> None:
        """Test that same seed produces same results."""
        points = [
            Vector([1, 1]),
            Vector([2, 2]),
            Vector([8, 8]),
            Vector([9, 9]),
        ]

        # Run twice with same seed
        kmeans1 = KMeans(points, 2, Random(42))
        kmeans2 = KMeans(points, 2, Random(42))

        # Run same number of steps
        for _ in range(10):
            kmeans1.step()
            kmeans2.step()

        # Should produce identical results
        assert kmeans1.current_iteration == kmeans2.current_iteration
        for i in range(2):
            for j in range(len(kmeans1.centroids[i].values)):
                assert kmeans1.centroids[i].values[j] == kmeans2.centroids[i].values[j]

    def test_different_seeds_differ(self) -> None:
        """Test that different seeds produce different results."""
        points = [
            Vector([1, 1]),
            Vector([2, 2]),
            Vector([8, 8]),
            Vector([9, 9]),
        ]

        kmeans1 = KMeans(points, 2, Random(42))
        kmeans2 = KMeans(points, 2, Random(100))

        # Initial centroids should likely differ
        # (Small chance they could be same by random chance)
        different = False
        for i in range(2):
            if kmeans1.centroids[i].values != kmeans2.centroids[i].values:
                different = True
                break

        # With high probability they should be different
        # If not initially, they will be after steps
        if not different:
            kmeans1.step()
            kmeans2.step()
            for i in range(2):
                if kmeans1.centroids[i].values != kmeans2.centroids[i].values:
                    different = True
                    break

        assert different


class TestKMeans3D:
    """Test KMeans in 3D space (like RGB colors)."""

    def test_rgb_clustering(self) -> None:
        """Test clustering RGB colors."""
        random = Random(42)

        # Primary colors
        red = Vector([255, 0, 0])
        green = Vector([0, 255, 0])
        blue = Vector([0, 0, 255])

        # Near-red colors
        red1 = Vector([250, 5, 5])
        red2 = Vector([245, 10, 10])

        points = [red, red1, red2, green, blue]

        kmeans = KMeans(points, 3, random)

        # Run to convergence
        for _ in range(50):
            kmeans.step()
            if kmeans.has_converged(1.0):
                break

        # Should converge to 3 clusters
        assert kmeans.has_converged(1.0)

        # Each cluster should have at least one point
        for category in kmeans.points_per_category:
            assert len(category) > 0
