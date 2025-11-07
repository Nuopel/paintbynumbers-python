"""Tests for BoundingBox class."""

import pytest
import sys
from paintbynumbers.structs.boundingbox import BoundingBox
from paintbynumbers.structs.point import Point


class TestBoundingBox:
    """Test BoundingBox class."""

    def test_create_default_boundingbox(self) -> None:
        """Test creating a bounding box with default values."""
        bb = BoundingBox()
        assert bb.minX == sys.maxsize
        assert bb.minY == sys.maxsize
        assert bb.maxX == -sys.maxsize - 1
        assert bb.maxY == -sys.maxsize - 1
        assert not bb.is_valid()

    def test_create_custom_boundingbox(self) -> None:
        """Test creating a bounding box with custom values."""
        bb = BoundingBox(minX=10, minY=20, maxX=100, maxY=200)
        assert bb.minX == 10
        assert bb.minY == 20
        assert bb.maxX == 100
        assert bb.maxY == 200
        assert bb.is_valid()

    def test_width_calculation(self) -> None:
        """Test width calculation (maxX - minX + 1)."""
        bb = BoundingBox(minX=10, minY=20, maxX=19, maxY=29)
        # Width = 19 - 10 + 1 = 10
        assert bb.width == 10

    def test_height_calculation(self) -> None:
        """Test height calculation (maxY - minY + 1)."""
        bb = BoundingBox(minX=10, minY=20, maxX=19, maxY=29)
        # Height = 29 - 20 + 1 = 10
        assert bb.height == 10

    def test_single_point_dimensions(self) -> None:
        """Test that a single point has width and height of 1."""
        bb = BoundingBox(minX=5, minY=10, maxX=5, maxY=10)
        assert bb.width == 1
        assert bb.height == 1

    def test_expand_with_coordinates(self) -> None:
        """Test expanding bounding box with coordinates."""
        bb = BoundingBox()

        bb.expand(10, 20)
        assert bb.minX == 10
        assert bb.minY == 20
        assert bb.maxX == 10
        assert bb.maxY == 20

        bb.expand(5, 15)
        assert bb.minX == 5
        assert bb.minY == 15

        bb.expand(15, 25)
        assert bb.maxX == 15
        assert bb.maxY == 25

    def test_expand_with_point(self) -> None:
        """Test expanding bounding box with Point objects."""
        bb = BoundingBox()

        bb.expand_point(Point(10, 20))
        assert bb.minX == 10
        assert bb.minY == 20

        bb.expand_point(Point(5, 25))
        assert bb.minX == 5
        assert bb.maxY == 25

    def test_expand_multiple_points(self) -> None:
        """Test expanding with multiple points."""
        bb = BoundingBox()

        points = [
            Point(10, 20),
            Point(5, 15),
            Point(20, 30),
            Point(8, 25),
        ]

        for point in points:
            bb.expand_point(point)

        assert bb.minX == 5
        assert bb.minY == 15
        assert bb.maxX == 20
        assert bb.maxY == 30
        assert bb.width == 16  # 20 - 5 + 1
        assert bb.height == 16  # 30 - 15 + 1

    def test_contains_coordinates(self) -> None:
        """Test checking if coordinates are contained."""
        bb = BoundingBox(minX=10, minY=20, maxX=100, maxY=200)

        # Inside
        assert bb.contains(50, 100)
        assert bb.contains(10, 20)  # Boundaries included
        assert bb.contains(100, 200)  # Boundaries included

        # Outside
        assert not bb.contains(5, 100)
        assert not bb.contains(150, 100)
        assert not bb.contains(50, 10)
        assert not bb.contains(50, 250)

    def test_contains_point(self) -> None:
        """Test checking if Point objects are contained."""
        bb = BoundingBox(minX=10, minY=20, maxX=100, maxY=200)

        assert bb.contains_point(Point(50, 100))
        assert bb.contains_point(Point(10, 20))
        assert not bb.contains_point(Point(5, 100))
        assert not bb.contains_point(Point(150, 250))

    def test_is_valid(self) -> None:
        """Test validity checking."""
        # Default (invalid)
        bb = BoundingBox()
        assert not bb.is_valid()

        # After expansion (valid)
        bb.expand(10, 20)
        assert bb.is_valid()

        # Created with valid bounds
        bb2 = BoundingBox(minX=0, minY=0, maxX=10, maxY=10)
        assert bb2.is_valid()

    def test_equality(self) -> None:
        """Test bounding box equality."""
        bb1 = BoundingBox(minX=10, minY=20, maxX=100, maxY=200)
        bb2 = BoundingBox(minX=10, minY=20, maxX=100, maxY=200)
        bb3 = BoundingBox(minX=0, minY=0, maxX=50, maxY=50)

        assert bb1 == bb2
        assert bb1 != bb3

    def test_repr(self) -> None:
        """Test string representation."""
        bb = BoundingBox(minX=10, minY=20, maxX=100, maxY=200)
        expected = "BoundingBox(minX=10, minY=20, maxX=100, maxY=200)"
        assert repr(bb) == expected

    def test_zero_based_bounds(self) -> None:
        """Test bounding box starting at (0, 0)."""
        bb = BoundingBox()
        bb.expand(0, 0)
        bb.expand(9, 9)

        assert bb.minX == 0
        assert bb.minY == 0
        assert bb.maxX == 9
        assert bb.maxY == 9
        assert bb.width == 10
        assert bb.height == 10

    def test_negative_coordinates(self) -> None:
        """Test bounding box with negative coordinates."""
        bb = BoundingBox()
        bb.expand(-10, -20)
        bb.expand(10, 20)

        assert bb.minX == -10
        assert bb.minY == -20
        assert bb.maxX == 10
        assert bb.maxY == 20
        assert bb.width == 21  # 10 - (-10) + 1
        assert bb.height == 41  # 20 - (-20) + 1
