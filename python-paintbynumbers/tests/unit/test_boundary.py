"""Tests for boundary utilities."""

import pytest
from paintbynumbers.utils.boundary import (
    is_in_bounds,
    clamp,
    clamp_point,
    get_neighbors_4,
    get_neighbors_8,
    is_on_edge,
    get_edge_type,
    EdgeType,
)
from paintbynumbers.structs.point import Point


class TestIsInBounds:
    """Test is_in_bounds function."""

    def test_point_inside(self) -> None:
        """Test point inside boundaries."""
        assert is_in_bounds(5, 5, 10, 10)
        assert is_in_bounds(0, 0, 10, 10)
        assert is_in_bounds(9, 9, 10, 10)

    def test_point_outside(self) -> None:
        """Test point outside boundaries."""
        assert not is_in_bounds(-1, 5, 10, 10)
        assert not is_in_bounds(5, -1, 10, 10)
        assert not is_in_bounds(10, 5, 10, 10)
        assert not is_in_bounds(5, 10, 10, 10)

    def test_edge_cases(self) -> None:
        """Test edge coordinates."""
        # (0, 0) is in bounds
        assert is_in_bounds(0, 0, 10, 10)
        # (9, 9) is in bounds for 10x10
        assert is_in_bounds(9, 9, 10, 10)
        # (10, 10) is out of bounds
        assert not is_in_bounds(10, 10, 10, 10)


class TestClamp:
    """Test clamp function."""

    def test_clamp_below_min(self) -> None:
        """Test clamping value below minimum."""
        assert clamp(-5, 0, 10) == 0
        assert clamp(-100, 0, 10) == 0

    def test_clamp_above_max(self) -> None:
        """Test clamping value above maximum."""
        assert clamp(15, 0, 10) == 10
        assert clamp(100, 0, 10) == 10

    def test_clamp_within_range(self) -> None:
        """Test value already within range."""
        assert clamp(5, 0, 10) == 5
        assert clamp(0, 0, 10) == 0
        assert clamp(10, 0, 10) == 10

    def test_clamp_single_value_range(self) -> None:
        """Test clamping when min == max."""
        assert clamp(-5, 5, 5) == 5
        assert clamp(5, 5, 5) == 5
        assert clamp(10, 5, 5) == 5


class TestClampPoint:
    """Test clamp_point function."""

    def test_clamp_point_inside(self) -> None:
        """Test point already inside bounds."""
        p = Point(5, 5)
        clamped = clamp_point(p, 10, 10)
        assert clamped == Point(5, 5)

    def test_clamp_point_negative(self) -> None:
        """Test clamping negative coordinates."""
        p = Point(-5, -10)
        clamped = clamp_point(p, 10, 10)
        assert clamped == Point(0, 0)

    def test_clamp_point_too_large(self) -> None:
        """Test clamping coordinates beyond bounds."""
        p = Point(15, 20)
        clamped = clamp_point(p, 10, 10)
        assert clamped == Point(9, 9)

    def test_clamp_point_mixed(self) -> None:
        """Test clamping with mixed coordinates."""
        p = Point(-5, 100)
        clamped = clamp_point(p, 50, 50)
        assert clamped == Point(0, 49)


class TestGetNeighbors4:
    """Test get_neighbors_4 function."""

    def test_center_point(self) -> None:
        """Test 4-neighbors of center point."""
        neighbors = get_neighbors_4(5, 5, 10, 10)
        assert len(neighbors) == 4
        assert Point(5, 4) in neighbors  # Up
        assert Point(5, 6) in neighbors  # Down
        assert Point(4, 5) in neighbors  # Left
        assert Point(6, 5) in neighbors  # Right

    def test_corner_top_left(self) -> None:
        """Test 4-neighbors of top-left corner."""
        neighbors = get_neighbors_4(0, 0, 10, 10)
        assert len(neighbors) == 2
        assert Point(1, 0) in neighbors  # Right
        assert Point(0, 1) in neighbors  # Down

    def test_corner_bottom_right(self) -> None:
        """Test 4-neighbors of bottom-right corner."""
        neighbors = get_neighbors_4(9, 9, 10, 10)
        assert len(neighbors) == 2
        assert Point(8, 9) in neighbors  # Left
        assert Point(9, 8) in neighbors  # Up

    def test_edge_left(self) -> None:
        """Test 4-neighbors of left edge."""
        neighbors = get_neighbors_4(0, 5, 10, 10)
        assert len(neighbors) == 3
        assert Point(0, 4) in neighbors  # Up
        assert Point(0, 6) in neighbors  # Down
        assert Point(1, 5) in neighbors  # Right

    def test_edge_right(self) -> None:
        """Test 4-neighbors of right edge."""
        neighbors = get_neighbors_4(9, 5, 10, 10)
        assert len(neighbors) == 3
        assert Point(9, 4) in neighbors  # Up
        assert Point(9, 6) in neighbors  # Down
        assert Point(8, 5) in neighbors  # Left


class TestGetNeighbors8:
    """Test get_neighbors_8 function."""

    def test_center_point(self) -> None:
        """Test 8-neighbors of center point."""
        neighbors = get_neighbors_8(5, 5, 10, 10)
        assert len(neighbors) == 8

        # All 8 directions
        expected = [
            Point(4, 4), Point(5, 4), Point(6, 4),  # Top row
            Point(4, 5),              Point(6, 5),  # Middle row (no center)
            Point(4, 6), Point(5, 6), Point(6, 6),  # Bottom row
        ]
        for p in expected:
            assert p in neighbors

    def test_corner_top_left(self) -> None:
        """Test 8-neighbors of top-left corner."""
        neighbors = get_neighbors_8(0, 0, 10, 10)
        assert len(neighbors) == 3
        assert Point(1, 0) in neighbors  # Right
        assert Point(0, 1) in neighbors  # Down
        assert Point(1, 1) in neighbors  # Diagonal

    def test_corner_bottom_right(self) -> None:
        """Test 8-neighbors of bottom-right corner."""
        neighbors = get_neighbors_8(9, 9, 10, 10)
        assert len(neighbors) == 3
        assert Point(8, 9) in neighbors  # Left
        assert Point(9, 8) in neighbors  # Up
        assert Point(8, 8) in neighbors  # Diagonal

    def test_edge_top(self) -> None:
        """Test 8-neighbors of top edge."""
        neighbors = get_neighbors_8(5, 0, 10, 10)
        assert len(neighbors) == 5

        expected = [
            Point(4, 0), Point(6, 0),  # Left and right
            Point(4, 1), Point(5, 1), Point(6, 1),  # Bottom row
        ]
        for p in expected:
            assert p in neighbors

    def test_no_duplicates(self) -> None:
        """Test that no duplicate neighbors are returned."""
        neighbors = get_neighbors_8(5, 5, 10, 10)
        assert len(neighbors) == len(set(neighbors))


class TestIsOnEdge:
    """Test is_on_edge function."""

    def test_center_not_on_edge(self) -> None:
        """Test center point is not on edge."""
        assert not is_on_edge(5, 5, 10, 10)

    def test_corners_on_edge(self) -> None:
        """Test corners are on edges."""
        assert is_on_edge(0, 0, 10, 10)
        assert is_on_edge(9, 0, 10, 10)
        assert is_on_edge(0, 9, 10, 10)
        assert is_on_edge(9, 9, 10, 10)

    def test_edges(self) -> None:
        """Test edge points."""
        assert is_on_edge(0, 5, 10, 10)  # Left
        assert is_on_edge(9, 5, 10, 10)  # Right
        assert is_on_edge(5, 0, 10, 10)  # Top
        assert is_on_edge(5, 9, 10, 10)  # Bottom


class TestGetEdgeType:
    """Test get_edge_type function."""

    def test_center_no_edge(self) -> None:
        """Test center point has no edge."""
        edge = get_edge_type(5, 5, 10, 10)
        assert edge == EdgeType.NONE

    def test_left_edge(self) -> None:
        """Test left edge detection."""
        edge = get_edge_type(0, 5, 10, 10)
        assert edge & EdgeType.LEFT
        assert not (edge & EdgeType.RIGHT)
        assert not (edge & EdgeType.TOP)
        assert not (edge & EdgeType.BOTTOM)

    def test_right_edge(self) -> None:
        """Test right edge detection."""
        edge = get_edge_type(9, 5, 10, 10)
        assert edge & EdgeType.RIGHT
        assert not (edge & EdgeType.LEFT)

    def test_top_edge(self) -> None:
        """Test top edge detection."""
        edge = get_edge_type(5, 0, 10, 10)
        assert edge & EdgeType.TOP
        assert not (edge & EdgeType.BOTTOM)

    def test_bottom_edge(self) -> None:
        """Test bottom edge detection."""
        edge = get_edge_type(5, 9, 10, 10)
        assert edge & EdgeType.BOTTOM
        assert not (edge & EdgeType.TOP)

    def test_corner_top_left(self) -> None:
        """Test top-left corner has two flags."""
        edge = get_edge_type(0, 0, 10, 10)
        assert edge & EdgeType.LEFT
        assert edge & EdgeType.TOP
        assert not (edge & EdgeType.RIGHT)
        assert not (edge & EdgeType.BOTTOM)

    def test_corner_bottom_right(self) -> None:
        """Test bottom-right corner has two flags."""
        edge = get_edge_type(9, 9, 10, 10)
        assert edge & EdgeType.RIGHT
        assert edge & EdgeType.BOTTOM
        assert not (edge & EdgeType.LEFT)
        assert not (edge & EdgeType.TOP)

    def test_all_corners(self) -> None:
        """Test all four corners."""
        # Top-left
        edge = get_edge_type(0, 0, 10, 10)
        assert edge == (EdgeType.LEFT | EdgeType.TOP)

        # Top-right
        edge = get_edge_type(9, 0, 10, 10)
        assert edge == (EdgeType.RIGHT | EdgeType.TOP)

        # Bottom-left
        edge = get_edge_type(0, 9, 10, 10)
        assert edge == (EdgeType.LEFT | EdgeType.BOTTOM)

        # Bottom-right
        edge = get_edge_type(9, 9, 10, 10)
        assert edge == (EdgeType.RIGHT | EdgeType.BOTTOM)
