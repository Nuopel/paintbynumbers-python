"""Tests for polylabel algorithm."""

import pytest
import math
from paintbynumbers.algorithms.polylabel import polylabel, PolylabelResult


class TestPolylabelBasic:
    """Test basic polylabel functionality."""

    def test_square(self) -> None:
        """Test pole of inaccessibility for a square."""
        # 10x10 square
        polygon = [[(0, 0), (10, 0), (10, 10), (0, 10)]]

        result = polylabel(polygon, precision=1.0)

        # Center should be at (5, 5)
        assert abs(result.pt[0] - 5.0) < 1.0
        assert abs(result.pt[1] - 5.0) < 1.0
        # Distance to edge should be ~5
        assert abs(result.distance - 5.0) < 1.0

    def test_rectangle(self) -> None:
        """Test pole of inaccessibility for a rectangle."""
        # 20x10 rectangle
        polygon = [[(0, 0), (20, 0), (20, 10), (0, 10)]]

        result = polylabel(polygon, precision=1.0)

        # Center should be at (10, 5)
        assert abs(result.pt[0] - 10.0) < 1.0
        assert abs(result.pt[1] - 5.0) < 1.0
        # Distance to nearest edge should be ~5 (half the smaller dimension)
        assert abs(result.distance - 5.0) < 1.0

    def test_triangle(self) -> None:
        """Test pole of inaccessibility for a triangle."""
        # Equilateral-ish triangle
        polygon = [[(0, 0), (10, 0), (5, 10)]]

        result = polylabel(polygon, precision=0.5)

        # Should be somewhere near center
        assert 2.0 < result.pt[0] < 8.0
        assert 2.0 < result.pt[1] < 8.0
        assert result.distance > 0

    def test_small_square(self) -> None:
        """Test with a small square."""
        polygon = [[(0, 0), (2, 0), (2, 2), (0, 2)]]

        result = polylabel(polygon, precision=0.1)

        # Center at (1, 1)
        assert abs(result.pt[0] - 1.0) < 0.5
        assert abs(result.pt[1] - 1.0) < 0.5
        assert abs(result.distance - 1.0) < 0.5


class TestPolylabelHoles:
    """Test polylabel with polygons containing holes."""

    def test_square_with_hole(self) -> None:
        """Test square with square hole in center."""
        # Outer square 10x10, inner hole 4x4 centered
        polygon = [
            [(0, 0), (10, 0), (10, 10), (0, 10)],  # Outer ring
            [(3, 3), (7, 3), (7, 7), (3, 7)]       # Hole
        ]

        result = polylabel(polygon, precision=0.5)

        # Should be between outer edge and hole
        # Not in the hole (3-7, 3-7)
        assert result.distance > 0
        # Should not be in the center (which is the hole)
        center_dist = math.sqrt((result.pt[0] - 5) ** 2 + (result.pt[1] - 5) ** 2)
        assert center_dist > 1.0  # Should be away from center

    def test_ring_shape(self) -> None:
        """Test ring-shaped polygon (large outer, small inner)."""
        # Outer 10x10, inner 2x2 centered
        polygon = [
            [(0, 0), (10, 0), (10, 10), (0, 10)],
            [(4, 4), (6, 4), (6, 6), (4, 6)]
        ]

        result = polylabel(polygon, precision=0.5)

        # Should find a point in the ring
        assert result.distance > 0
        # Should be a reasonable distance from edge
        assert result.distance > 1.0


class TestPolylabelPrecision:
    """Test polylabel precision parameter."""

    def test_high_precision(self) -> None:
        """Test with high precision (small tolerance)."""
        polygon = [[(0, 0), (10, 0), (10, 10), (0, 10)]]

        result = polylabel(polygon, precision=0.01)

        # Should be very close to (5, 5)
        assert abs(result.pt[0] - 5.0) < 0.1
        assert abs(result.pt[1] - 5.0) < 0.1

    def test_low_precision(self) -> None:
        """Test with low precision (large tolerance)."""
        polygon = [[(0, 0), (10, 0), (10, 10), (0, 10)]]

        result = polylabel(polygon, precision=2.0)

        # Should still find a reasonable point
        assert 2.0 < result.pt[0] < 8.0
        assert 2.0 < result.pt[1] < 8.0

    def test_precision_affects_accuracy(self) -> None:
        """Test that higher precision gives better results."""
        polygon = [[(0, 0), (10, 0), (10, 10), (0, 10)]]

        result_low = polylabel(polygon, precision=1.0)
        result_high = polylabel(polygon, precision=0.1)

        # High precision should be closer to true center
        error_low = abs(result_low.pt[0] - 5.0) + abs(result_low.pt[1] - 5.0)
        error_high = abs(result_high.pt[0] - 5.0) + abs(result_high.pt[1] - 5.0)

        # High precision should have less error (or equal in best case)
        assert error_high <= error_low + 0.1  # Small tolerance for variability


class TestPolylabelEdgeCases:
    """Test edge cases and special scenarios."""

    def test_very_small_polygon(self) -> None:
        """Test with very small polygon."""
        polygon = [[(0, 0), (1, 0), (1, 1), (0, 1)]]

        result = polylabel(polygon, precision=0.1)

        assert result.pt is not None
        assert result.distance > 0

    def test_narrow_rectangle(self) -> None:
        """Test with very narrow rectangle."""
        polygon = [[(0, 0), (10, 0), (10, 1), (0, 1)]]

        result = polylabel(polygon, precision=0.1)

        # Should be near center
        assert abs(result.pt[0] - 5.0) < 1.0
        # Distance should be limited by narrow dimension
        assert result.distance < 1.0

    def test_l_shape(self) -> None:
        """Test with L-shaped polygon."""
        # L-shape
        polygon = [
            [(0, 0), (5, 0), (5, 5), (10, 5), (10, 10), (0, 10)]
        ]

        result = polylabel(polygon, precision=0.5)

        # Should find a reasonable point
        assert result.distance > 0
        assert 0 <= result.pt[0] <= 10
        assert 0 <= result.pt[1] <= 10

    def test_concave_polygon(self) -> None:
        """Test with concave polygon."""
        # Star-like shape (simplified)
        polygon = [
            [(5, 0), (6, 4), (10, 5), (6, 6), (5, 10), (4, 6), (0, 5), (4, 4)]
        ]

        result = polylabel(polygon, precision=0.5)

        # Should find point inside
        assert result.distance > 0

    def test_zero_area_polygon(self) -> None:
        """Test with degenerate polygon (line)."""
        # Degenerate case: line segment
        polygon = [[(0, 0), (10, 0), (10, 0), (0, 0)]]

        result = polylabel(polygon, precision=0.1)

        # Should return a point (even if degenerate)
        assert result.pt is not None
        assert result.distance == 0  # No interior


class TestPolylabelResult:
    """Test PolylabelResult class."""

    def test_result_structure(self) -> None:
        """Test that result has expected structure."""
        polygon = [[(0, 0), (10, 0), (10, 10), (0, 10)]]

        result = polylabel(polygon, precision=1.0)

        assert isinstance(result, PolylabelResult)
        assert isinstance(result.pt, tuple)
        assert len(result.pt) == 2
        assert isinstance(result.pt[0], float)
        assert isinstance(result.pt[1], float)
        assert isinstance(result.distance, float)

    def test_result_distance_positive(self) -> None:
        """Test that distance is positive for valid polygons."""
        polygon = [[(0, 0), (10, 0), (10, 10), (0, 10)]]

        result = polylabel(polygon, precision=1.0)

        assert result.distance > 0

    def test_result_point_inside(self) -> None:
        """Test that result point is inside polygon."""
        polygon = [[(0, 0), (10, 0), (10, 10), (0, 10)]]

        result = polylabel(polygon, precision=1.0)

        # Point should be inside bounds
        assert 0 <= result.pt[0] <= 10
        assert 0 <= result.pt[1] <= 10


class TestPolylabelComplex:
    """Test complex polygon scenarios."""

    def test_hexagon(self) -> None:
        """Test with regular hexagon."""
        # Approximate regular hexagon
        polygon = [
            [(5, 0), (10, 2.5), (10, 7.5), (5, 10), (0, 7.5), (0, 2.5)]
        ]

        result = polylabel(polygon, precision=0.5)

        # Should be near center
        assert abs(result.pt[0] - 5.0) < 2.0
        assert abs(result.pt[1] - 5.0) < 2.0
        assert result.distance > 0

    def test_c_shape(self) -> None:
        """Test with C-shaped polygon."""
        # C-shape (rectangle with rectangular notch)
        polygon = [
            [(0, 0), (10, 0), (10, 3), (3, 3), (3, 7), (10, 7), (10, 10), (0, 10)]
        ]

        result = polylabel(polygon, precision=0.5)

        assert result.distance > 0
        # Should avoid the notch area
        assert result.pt[0] < 3 or result.pt[1] < 3 or result.pt[1] > 7

    def test_multiple_holes(self) -> None:
        """Test polygon with multiple holes."""
        # Outer square with two holes
        polygon = [
            [(0, 0), (10, 0), (10, 10), (0, 10)],
            [(1, 1), (3, 1), (3, 3), (1, 3)],  # Hole 1
            [(7, 7), (9, 7), (9, 9), (7, 9)]   # Hole 2
        ]

        result = polylabel(polygon, precision=0.5)

        assert result.distance > 0
        # Should not be in either hole
        assert not (1 <= result.pt[0] <= 3 and 1 <= result.pt[1] <= 3)
        assert not (7 <= result.pt[0] <= 9 and 7 <= result.pt[1] <= 9)

    def test_real_world_facet(self) -> None:
        """Test with a more realistic irregular facet shape."""
        # Irregular quadrilateral (like a facet in paint-by-numbers)
        polygon = [
            [(10, 5), (25, 8), (30, 25), (15, 30), (5, 20)]
        ]

        result = polylabel(polygon, precision=0.5)

        assert result.distance > 0
        assert result.pt is not None
        # Should be somewhere inside the polygon bounds
        assert 5 <= result.pt[0] <= 30
        assert 5 <= result.pt[1] <= 30
