"""Tests for Point class."""

import pytest
from paintbynumbers.structs.point import Point


class TestPoint:
    """Test Point class."""

    def test_create_point(self) -> None:
        """Test creating a point."""
        p = Point(10, 20)
        assert p.x == 10
        assert p.y == 20

    def test_point_equality(self) -> None:
        """Test point equality."""
        p1 = Point(5, 10)
        p2 = Point(5, 10)
        p3 = Point(10, 5)

        assert p1 == p2
        assert p1 != p3

    def test_point_hashable(self) -> None:
        """Test that points can be used in sets and as dict keys."""
        p1 = Point(1, 2)
        p2 = Point(1, 2)
        p3 = Point(3, 4)

        # Can use in set
        point_set = {p1, p2, p3}
        assert len(point_set) == 2  # p1 and p2 are same

        # Can use as dict key
        point_dict = {p1: "first", p3: "second"}
        assert point_dict[p2] == "first"  # p2 equals p1

    def test_distance_to_point(self) -> None:
        """Test Manhattan distance calculation between points."""
        p1 = Point(0, 0)
        p2 = Point(3, 4)

        # Manhattan distance = |3-0| + |4-0| = 7
        assert p1.distance_to(p2) == 7
        assert p2.distance_to(p1) == 7

    def test_distance_to_same_point(self) -> None:
        """Test distance to same point is 0."""
        p = Point(5, 10)
        assert p.distance_to(p) == 0

    def test_distance_to_orthogonal_neighbor(self) -> None:
        """Test distance to orthogonal neighbors is 1."""
        p = Point(5, 5)

        # Orthogonal neighbors (4-connected)
        assert p.distance_to(Point(5, 4)) == 1  # Up
        assert p.distance_to(Point(5, 6)) == 1  # Down
        assert p.distance_to(Point(4, 5)) == 1  # Left
        assert p.distance_to(Point(6, 5)) == 1  # Right

    def test_distance_to_diagonal_neighbor(self) -> None:
        """Test distance to diagonal neighbors is 2 (Manhattan)."""
        p = Point(5, 5)

        # Diagonal neighbors (8-connected)
        # Manhattan distance is 2, not sqrt(2) ≈ 1.41
        assert p.distance_to(Point(4, 4)) == 2
        assert p.distance_to(Point(6, 6)) == 2
        assert p.distance_to(Point(4, 6)) == 2
        assert p.distance_to(Point(6, 4)) == 2

    def test_distance_to_coord(self) -> None:
        """Test Manhattan distance calculation to coordinates."""
        p = Point(0, 0)

        assert p.distance_to_coord(3, 4) == 7
        assert p.distance_to_coord(0, 0) == 0
        assert p.distance_to_coord(-2, -3) == 5

    def test_distance_with_negative_coords(self) -> None:
        """Test distance calculation with negative coordinates."""
        p1 = Point(-5, -10)
        p2 = Point(5, 10)

        # |-5-5| + |-10-10| = 10 + 20 = 30
        assert p1.distance_to(p2) == 30

    def test_point_repr(self) -> None:
        """Test string representation."""
        p = Point(10, 20)
        assert repr(p) == "Point(x=10, y=20)"

    def test_point_immutable(self) -> None:
        """Test that point is immutable (frozen)."""
        p = Point(5, 10)

        with pytest.raises(AttributeError):
            p.x = 15  # type: ignore

        with pytest.raises(AttributeError):
            p.y = 20  # type: ignore
