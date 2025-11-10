"""Tests for Vector class."""

import pytest
import math
from paintbynumbers.algorithms.vector import Vector


class TestVector:
    """Test Vector class."""

    def test_create_vector(self) -> None:
        """Test creating a vector."""
        v = Vector([1, 2, 3])
        assert v.values == [1, 2, 3]
        assert v.weight == 1.0
        assert v.tag is None

    def test_create_weighted_vector(self) -> None:
        """Test creating a weighted vector."""
        v = Vector([1, 2, 3], 5.0)
        assert v.values == [1, 2, 3]
        assert v.weight == 5.0

    def test_create_vector_with_tag(self) -> None:
        """Test creating a vector with tag."""
        tag_data = {"color": "red"}
        v = Vector([255, 0, 0], 1.0, tag_data)
        assert v.tag == tag_data

    def test_dimensions_property(self) -> None:
        """Test dimensions property."""
        v2d = Vector([1, 2])
        assert v2d.dimensions == 2

        v3d = Vector([1, 2, 3])
        assert v3d.dimensions == 3

        v10d = Vector([0] * 10)
        assert v10d.dimensions == 10

    def test_distance_to(self) -> None:
        """Test Euclidean distance calculation."""
        v1 = Vector([0, 0])
        v2 = Vector([3, 4])

        distance = v1.distance_to(v2)
        assert abs(distance - 5.0) < 1e-10

    def test_distance_to_same_point(self) -> None:
        """Test distance to same point is zero."""
        v = Vector([1, 2, 3])
        assert v.distance_to(v) == 0.0

    def test_distance_3d(self) -> None:
        """Test distance in 3D space."""
        v1 = Vector([0, 0, 0])
        v2 = Vector([1, 1, 1])

        distance = v1.distance_to(v2)
        expected = math.sqrt(3)
        assert abs(distance - expected) < 1e-10

    def test_distance_symmetric(self) -> None:
        """Test that distance is symmetric."""
        v1 = Vector([1, 2, 3])
        v2 = Vector([4, 5, 6])

        assert v1.distance_to(v2) == v2.distance_to(v1)

    def test_magnitude(self) -> None:
        """Test magnitude calculation."""
        v = Vector([3, 4])
        assert abs(v.magnitude() - 5.0) < 1e-10

    def test_magnitude_squared(self) -> None:
        """Test squared magnitude calculation."""
        v = Vector([3, 4])
        assert abs(v.magnitude_squared() - 25.0) < 1e-10

    def test_magnitude_3d(self) -> None:
        """Test magnitude in 3D."""
        v = Vector([1, 2, 2])
        expected = math.sqrt(1 + 4 + 4)
        assert abs(v.magnitude() - expected) < 1e-10

    def test_clone(self) -> None:
        """Test cloning a vector."""
        original = Vector([1, 2, 3], 5.0, {"data": "test"})
        clone = original.clone()

        assert clone.values == original.values
        assert clone.weight == original.weight
        assert clone.tag == original.tag

        # Modify clone shouldn't affect original
        clone.values[0] = 999
        assert original.values[0] == 1

    def test_equality(self) -> None:
        """Test vector equality."""
        v1 = Vector([1, 2, 3], 2.0)
        v2 = Vector([1, 2, 3], 2.0)
        v3 = Vector([1, 2, 4], 2.0)
        v4 = Vector([1, 2, 3], 3.0)

        assert v1 == v2
        assert v1 != v3  # Different values
        assert v1 != v4  # Different weight

    def test_repr(self) -> None:
        """Test string representation."""
        v = Vector([1, 2, 3], 5.0)
        repr_str = repr(v)
        assert "Vector" in repr_str
        assert "[1, 2, 3]" in repr_str
        assert "5.0" in repr_str


class TestVectorAverage:
    """Test Vector.average() method."""

    def test_average_single_vector(self) -> None:
        """Test averaging a single vector."""
        v = Vector([1, 2, 3], 5.0)
        avg = Vector.average([v])

        assert avg.values == [1, 2, 3]
        assert avg.weight == 5.0

    def test_average_equal_weights(self) -> None:
        """Test averaging vectors with equal weights."""
        v1 = Vector([0, 0], 1.0)
        v2 = Vector([10, 10], 1.0)

        avg = Vector.average([v1, v2])

        assert avg.values == [5.0, 5.0]
        assert avg.weight == 2.0

    def test_average_different_weights(self) -> None:
        """Test weighted averaging."""
        v1 = Vector([0, 0], 1.0)
        v2 = Vector([10, 10], 2.0)

        avg = Vector.average([v1, v2])

        # Weighted average: (1*0 + 2*10) / (1+2) = 20/3
        expected = 20.0 / 3.0
        assert abs(avg.values[0] - expected) < 1e-10
        assert abs(avg.values[1] - expected) < 1e-10
        assert avg.weight == 3.0

    def test_average_three_vectors(self) -> None:
        """Test averaging three vectors."""
        v1 = Vector([0, 0], 1.0)
        v2 = Vector([3, 3], 1.0)
        v3 = Vector([6, 6], 1.0)

        avg = Vector.average([v1, v2, v3])

        assert avg.values == [3.0, 3.0]
        assert avg.weight == 3.0

    def test_average_heavily_weighted(self) -> None:
        """Test that heavy weight dominates average."""
        v1 = Vector([0, 0], 1.0)
        v2 = Vector([10, 10], 99.0)

        avg = Vector.average([v1, v2])

        # Should be very close to v2
        assert abs(avg.values[0] - 9.9) < 1e-10
        assert abs(avg.values[1] - 9.9) < 1e-10
        assert avg.weight == 100.0

    def test_average_3d_vectors(self) -> None:
        """Test averaging 3D vectors."""
        v1 = Vector([1, 2, 3], 1.0)
        v2 = Vector([4, 5, 6], 1.0)

        avg = Vector.average([v1, v2])

        assert avg.values == [2.5, 3.5, 4.5]
        assert avg.weight == 2.0

    def test_average_empty_list(self) -> None:
        """Test that averaging empty list raises error."""
        with pytest.raises(ValueError):
            Vector.average([])

    def test_average_rgb_colors(self) -> None:
        """Test averaging RGB color vectors."""
        red = Vector([255, 0, 0], 1.0)
        green = Vector([0, 255, 0], 1.0)

        avg = Vector.average([red, green])

        # Should be yellowish
        assert avg.values == [127.5, 127.5, 0]
        assert avg.weight == 2.0

    def test_average_preserves_centroid_property(self) -> None:
        """Test that average is the centroid."""
        vectors = [
            Vector([1, 1], 1.0),
            Vector([3, 1], 1.0),
            Vector([3, 3], 1.0),
            Vector([1, 3], 1.0),
        ]

        avg = Vector.average(vectors)

        # Centroid of square should be at center
        assert avg.values == [2.0, 2.0]
