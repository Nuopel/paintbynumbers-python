"""Tests for flood fill algorithm."""

import pytest
from paintbynumbers.algorithms.flood_fill import FloodFillAlgorithm
from paintbynumbers.structs.point import Point


class TestFloodFillBasic:
    """Test basic flood fill functionality."""

    def test_create_flood_fill(self) -> None:
        """Test creating FloodFillAlgorithm instance."""
        flood_fill = FloodFillAlgorithm()
        assert flood_fill is not None

    def test_fill_single_pixel(self) -> None:
        """Test filling a single pixel region."""
        flood_fill = FloodFillAlgorithm()

        # Create a 3x3 grid where only center is fillable
        filled = flood_fill.fill(
            Point(1, 1),
            3,
            3,
            lambda x, y: x == 1 and y == 1
        )

        assert len(filled) == 1
        assert Point(1, 1) in filled

    def test_fill_line_horizontal(self) -> None:
        """Test filling a horizontal line."""
        flood_fill = FloodFillAlgorithm()

        # Fill a horizontal line at y=1
        filled = flood_fill.fill(
            Point(2, 1),
            5,
            3,
            lambda x, y: y == 1
        )

        assert len(filled) == 5
        for x in range(5):
            assert Point(x, 1) in filled

    def test_fill_line_vertical(self) -> None:
        """Test filling a vertical line."""
        flood_fill = FloodFillAlgorithm()

        # Fill a vertical line at x=2
        filled = flood_fill.fill(
            Point(2, 1),
            5,
            5,
            lambda x, y: x == 2
        )

        assert len(filled) == 5
        for y in range(5):
            assert Point(2, y) in filled

    def test_fill_rectangle(self) -> None:
        """Test filling a rectangular region."""
        flood_fill = FloodFillAlgorithm()

        # Fill a 3x3 square in the center of 5x5 grid
        filled = flood_fill.fill(
            Point(2, 2),
            5,
            5,
            lambda x, y: 1 <= x <= 3 and 1 <= y <= 3
        )

        assert len(filled) == 9
        for x in range(1, 4):
            for y in range(1, 4):
                assert Point(x, y) in filled

    def test_fill_entire_area(self) -> None:
        """Test filling entire area."""
        flood_fill = FloodFillAlgorithm()

        filled = flood_fill.fill(
            Point(0, 0),
            10,
            10,
            lambda x, y: True
        )

        assert len(filled) == 100


class TestFloodFillConnectivity:
    """Test flood fill connectivity rules."""

    def test_4_connectivity(self) -> None:
        """Test that flood fill uses 4-connectivity (not 8)."""
        flood_fill = FloodFillAlgorithm()

        # Create a pattern where diagonal is blocked
        # X.X
        # ...
        # X.X
        def predicate(x: int, y: int) -> bool:
            if x == 1 and y == 1:  # Center
                return True
            if x == 0 and y == 0:  # Top-left
                return True
            if x == 2 and y == 0:  # Top-right
                return True
            if x == 0 and y == 2:  # Bottom-left
                return True
            if x == 2 and y == 2:  # Bottom-right
                return True
            return False

        # Start from center - should only fill center (diagonals not connected)
        filled = flood_fill.fill(Point(1, 1), 3, 3, predicate)

        assert len(filled) == 1
        assert Point(1, 1) in filled

    def test_no_diagonal_connections(self) -> None:
        """Test that diagonal pixels are not connected."""
        flood_fill = FloodFillAlgorithm()

        # Create L-shape that requires going around diagonal
        # XX
        # X.
        def predicate(x: int, y: int) -> bool:
            return (x == 0 and y == 0) or (x == 1 and y == 0) or (x == 0 and y == 1)

        filled = flood_fill.fill(Point(0, 0), 2, 2, predicate)

        assert len(filled) == 3
        assert Point(0, 0) in filled
        assert Point(1, 0) in filled
        assert Point(0, 1) in filled
        assert Point(1, 1) not in filled


class TestFloodFillBoundary:
    """Test flood fill boundary handling."""

    def test_fill_from_corner(self) -> None:
        """Test filling from corner of area."""
        flood_fill = FloodFillAlgorithm()

        filled = flood_fill.fill(
            Point(0, 0),
            5,
            5,
            lambda x, y: x + y < 3
        )

        # Should fill upper-left triangle
        assert Point(0, 0) in filled
        assert Point(1, 0) in filled
        assert Point(2, 0) in filled
        assert Point(0, 1) in filled
        assert Point(1, 1) in filled
        assert Point(0, 2) in filled

    def test_respects_bounds(self) -> None:
        """Test that fill respects width/height bounds."""
        flood_fill = FloodFillAlgorithm()

        # Predicate allows everything, but area is limited
        filled = flood_fill.fill(
            Point(2, 2),
            5,
            5,
            lambda x, y: True
        )

        # Should only fill within 5x5 area
        assert len(filled) == 25
        for pt in filled:
            assert 0 <= pt.x < 5
            assert 0 <= pt.y < 5

    def test_out_of_bounds_start(self) -> None:
        """Test starting from out of bounds point."""
        flood_fill = FloodFillAlgorithm()

        filled = flood_fill.fill(
            Point(-1, -1),
            5,
            5,
            lambda x, y: True
        )

        # Should fill nothing (start is out of bounds)
        assert len(filled) == 0

    def test_out_of_bounds_start_positive(self) -> None:
        """Test starting from out of bounds (beyond max)."""
        flood_fill = FloodFillAlgorithm()

        filled = flood_fill.fill(
            Point(10, 10),
            5,
            5,
            lambda x, y: True
        )

        assert len(filled) == 0


class TestFloodFillPredicate:
    """Test flood fill predicate handling."""

    def test_predicate_false_at_start(self) -> None:
        """Test when predicate is false at starting point."""
        flood_fill = FloodFillAlgorithm()

        filled = flood_fill.fill(
            Point(2, 2),
            5,
            5,
            lambda x, y: x != 2 or y != 2  # False at start
        )

        assert len(filled) == 0

    def test_predicate_with_state(self) -> None:
        """Test predicate that uses external state."""
        flood_fill = FloodFillAlgorithm()

        # Simulate a color map
        color_map = [
            [1, 1, 2],
            [1, 1, 2],
            [2, 2, 2]
        ]

        filled = flood_fill.fill(
            Point(0, 0),
            3,
            3,
            lambda x, y: color_map[y][x] == 1
        )

        assert len(filled) == 4
        assert Point(0, 0) in filled
        assert Point(1, 0) in filled
        assert Point(0, 1) in filled
        assert Point(1, 1) in filled

    def test_complex_pattern(self) -> None:
        """Test complex fill pattern with holes."""
        flood_fill = FloodFillAlgorithm()

        # Create a ring pattern (outer ring, hole in middle)
        def is_ring(x: int, y: int) -> bool:
            # Outer square minus inner square
            return (0 <= x < 5 and 0 <= y < 5) and not (1 < x < 3 and 1 < y < 3)

        filled = flood_fill.fill(Point(0, 0), 5, 5, is_ring)

        # Should fill the ring (25 - 1 center pixel = 24, but center is 1 pixel)
        # Actually the center is a single pixel at (2,2), so ring has 24 pixels
        # But actually the inner is a 1x1 at positions x=2 and y=2
        # Wait, 1 < x < 3 means x=2, and 1 < y < 3 means y=2
        # So hole is just 1 pixel at (2,2)
        assert len(filled) == 24
        assert Point(2, 2) not in filled
        assert Point(0, 0) in filled
        assert Point(4, 4) in filled


class TestFloodFillWithCallback:
    """Test fill_with_callback method."""

    def test_callback_basic(self) -> None:
        """Test basic callback functionality."""
        flood_fill = FloodFillAlgorithm()

        filled_points = []

        def callback(x: int, y: int) -> None:
            filled_points.append(Point(x, y))

        count = flood_fill.fill_with_callback(
            Point(1, 1),
            3,
            3,
            lambda x, y: True,
            callback
        )

        assert count == 9
        assert len(filled_points) == 9

    def test_callback_count(self) -> None:
        """Test that callback returns correct count."""
        flood_fill = FloodFillAlgorithm()

        count = flood_fill.fill_with_callback(
            Point(0, 0),
            10,
            10,
            lambda x, y: x < 5 and y < 5,
            lambda x, y: None
        )

        assert count == 25

    def test_callback_modifies_state(self) -> None:
        """Test callback that modifies external state."""
        flood_fill = FloodFillAlgorithm()

        visited = [[False] * 5 for _ in range(5)]

        def mark_visited(x: int, y: int) -> None:
            visited[y][x] = True

        count = flood_fill.fill_with_callback(
            Point(2, 2),
            5,
            5,
            lambda x, y: x == 2 or y == 2,  # Cross pattern
            mark_visited
        )

        assert count == 9  # 5 horizontal + 5 vertical - 1 center
        assert visited[2][2]  # Center
        assert visited[0][2]  # Top
        assert visited[2][0]  # Left

    def test_callback_vs_fill_equivalence(self) -> None:
        """Test that callback and fill produce same results."""
        flood_fill = FloodFillAlgorithm()

        predicate = lambda x, y: (x + y) % 2 == 0

        # Use fill()
        filled = flood_fill.fill(Point(0, 0), 10, 10, predicate)

        # Use fill_with_callback()
        callback_points = []
        count = flood_fill.fill_with_callback(
            Point(0, 0),
            10,
            10,
            predicate,
            lambda x, y: callback_points.append(Point(x, y))
        )

        assert count == len(filled)
        # Note: Order might differ (stack-based), so check as sets
        filled_set = set(filled)
        callback_set = set(callback_points)
        assert filled_set == callback_set

    def test_callback_memory_efficiency(self) -> None:
        """Test that callback doesn't collect points unnecessarily."""
        flood_fill = FloodFillAlgorithm()

        # This should be more memory efficient than fill()
        # Just count without storing
        count = flood_fill.fill_with_callback(
            Point(0, 0),
            100,
            100,
            lambda x, y: True,
            lambda x, y: None  # Do nothing
        )

        assert count == 10000


class TestFloodFillEdgeCases:
    """Test edge cases and special scenarios."""

    def test_single_pixel_area(self) -> None:
        """Test 1x1 area."""
        flood_fill = FloodFillAlgorithm()

        filled = flood_fill.fill(
            Point(0, 0),
            1,
            1,
            lambda x, y: True
        )

        assert len(filled) == 1
        assert Point(0, 0) in filled

    def test_narrow_area(self) -> None:
        """Test 1-pixel wide area."""
        flood_fill = FloodFillAlgorithm()

        filled = flood_fill.fill(
            Point(0, 5),
            1,
            10,
            lambda x, y: True
        )

        assert len(filled) == 10

    def test_large_area(self) -> None:
        """Test larger area to ensure no stack overflow."""
        flood_fill = FloodFillAlgorithm()

        filled = flood_fill.fill(
            Point(0, 0),
            100,
            100,
            lambda x, y: True
        )

        assert len(filled) == 10000

    def test_no_duplicate_points(self) -> None:
        """Test that no duplicate points are returned."""
        flood_fill = FloodFillAlgorithm()

        filled = flood_fill.fill(
            Point(5, 5),
            10,
            10,
            lambda x, y: True
        )

        # Check for duplicates
        unique_points = set(filled)
        assert len(filled) == len(unique_points)
