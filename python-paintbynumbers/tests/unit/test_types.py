"""Tests for core types."""

import pytest
from paintbynumbers.core.types import (
    RGB,
    OrientationEnum,
    PathPoint,
)
from paintbynumbers.structs.point import Point


class TestRGB:
    """Test RGB type."""

    def test_rgb_tuple(self) -> None:
        """Test RGB as tuple of 3 ints."""
        color: RGB = (255, 128, 0)
        assert len(color) == 3
        assert color[0] == 255
        assert color[1] == 128
        assert color[2] == 0


class TestOrientationEnum:
    """Test OrientationEnum."""

    def test_orientation_values(self) -> None:
        """Test orientation enum values."""
        assert OrientationEnum.Left == 0
        assert OrientationEnum.Top == 1
        assert OrientationEnum.Right == 2
        assert OrientationEnum.Bottom == 3

    def test_orientation_names(self) -> None:
        """Test orientation enum names."""
        assert OrientationEnum.Left.name == "Left"
        assert OrientationEnum.Top.name == "Top"
        assert OrientationEnum.Right.name == "Right"
        assert OrientationEnum.Bottom.name == "Bottom"

    def test_orientation_from_value(self) -> None:
        """Test creating orientation from value."""
        assert OrientationEnum(0) == OrientationEnum.Left
        assert OrientationEnum(1) == OrientationEnum.Top
        assert OrientationEnum(2) == OrientationEnum.Right
        assert OrientationEnum(3) == OrientationEnum.Bottom


class TestPathPoint:
    """Test PathPoint class."""

    def test_create_pathpoint(self) -> None:
        """Test creating a PathPoint."""
        pp = PathPoint(10, 20, OrientationEnum.Left)
        assert pp.x == 10
        assert pp.y == 20
        assert pp.orientation == OrientationEnum.Left

    def test_from_point(self) -> None:
        """Test creating PathPoint from Point."""
        p = Point(5, 15)
        pp = PathPoint.from_point(p, OrientationEnum.Top)
        assert pp.x == 5
        assert pp.y == 15
        assert pp.orientation == OrientationEnum.Top

    def test_get_wall_x_left(self) -> None:
        """Test get_wall_x for left orientation."""
        pp = PathPoint(10, 20, OrientationEnum.Left)
        assert pp.get_wall_x() == 9.5  # 10 - 0.5

    def test_get_wall_x_right(self) -> None:
        """Test get_wall_x for right orientation."""
        pp = PathPoint(10, 20, OrientationEnum.Right)
        assert pp.get_wall_x() == 10.5  # 10 + 0.5

    def test_get_wall_x_vertical(self) -> None:
        """Test get_wall_x for top/bottom (no change)."""
        pp_top = PathPoint(10, 20, OrientationEnum.Top)
        pp_bottom = PathPoint(10, 20, OrientationEnum.Bottom)
        assert pp_top.get_wall_x() == 10.0
        assert pp_bottom.get_wall_x() == 10.0

    def test_get_wall_y_top(self) -> None:
        """Test get_wall_y for top orientation."""
        pp = PathPoint(10, 20, OrientationEnum.Top)
        assert pp.get_wall_y() == 19.5  # 20 - 0.5

    def test_get_wall_y_bottom(self) -> None:
        """Test get_wall_y for bottom orientation."""
        pp = PathPoint(10, 20, OrientationEnum.Bottom)
        assert pp.get_wall_y() == 20.5  # 20 + 0.5

    def test_get_wall_y_horizontal(self) -> None:
        """Test get_wall_y for left/right (no change)."""
        pp_left = PathPoint(10, 20, OrientationEnum.Left)
        pp_right = PathPoint(10, 20, OrientationEnum.Right)
        assert pp_left.get_wall_y() == 20.0
        assert pp_right.get_wall_y() == 20.0

    def test_wall_coordinates_example(self) -> None:
        """Test wall coordinates with specific example."""
        # Pixel at (5, 5) with left wall
        pp = PathPoint(5, 5, OrientationEnum.Left)
        assert pp.get_wall_x() == 4.5
        assert pp.get_wall_y() == 5.0

    def test_pathpoint_equality(self) -> None:
        """Test PathPoint equality."""
        pp1 = PathPoint(10, 20, OrientationEnum.Left)
        pp2 = PathPoint(10, 20, OrientationEnum.Left)
        pp3 = PathPoint(10, 20, OrientationEnum.Right)
        pp4 = PathPoint(11, 20, OrientationEnum.Left)

        assert pp1 == pp2
        assert pp1 != pp3  # Different orientation
        assert pp1 != pp4  # Different position

    def test_pathpoint_hashable(self) -> None:
        """Test that PathPoints can be used in sets and dicts."""
        pp1 = PathPoint(10, 20, OrientationEnum.Left)
        pp2 = PathPoint(10, 20, OrientationEnum.Left)
        pp3 = PathPoint(10, 20, OrientationEnum.Right)

        # Can use in set
        point_set = {pp1, pp2, pp3}
        assert len(point_set) == 2  # pp1 and pp2 are same

        # Can use as dict key
        point_dict = {pp1: "left", pp3: "right"}
        assert point_dict[pp2] == "left"

    def test_pathpoint_repr(self) -> None:
        """Test string representation."""
        pp = PathPoint(10, 20, OrientationEnum.Top)
        assert repr(pp) == "PathPoint(x=10, y=20, orientation=Top)"

    def test_pathpoint_inherits_distance(self) -> None:
        """Test that PathPoint inherits distance methods from Point."""
        pp1 = PathPoint(0, 0, OrientationEnum.Left)
        pp2 = PathPoint(3, 4, OrientationEnum.Right)

        # Should inherit distance_to from Point
        assert pp1.distance_to(pp2) == 7  # Manhattan distance

    def test_different_orientations_all_corners(self) -> None:
        """Test PathPoint at same location with all orientations."""
        pp_left = PathPoint(5, 5, OrientationEnum.Left)
        pp_top = PathPoint(5, 5, OrientationEnum.Top)
        pp_right = PathPoint(5, 5, OrientationEnum.Right)
        pp_bottom = PathPoint(5, 5, OrientationEnum.Bottom)

        # All have same base coordinates
        assert pp_left.x == pp_top.x == pp_right.x == pp_bottom.x == 5
        assert pp_left.y == pp_top.y == pp_right.y == pp_bottom.y == 5

        # But different wall coordinates
        assert pp_left.get_wall_x() == 4.5
        assert pp_right.get_wall_x() == 5.5
        assert pp_top.get_wall_y() == 4.5
        assert pp_bottom.get_wall_y() == 5.5

        # All are different PathPoints
        assert pp_left != pp_top
        assert pp_left != pp_right
        assert pp_left != pp_bottom
