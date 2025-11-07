"""Core type definitions."""

from __future__ import annotations
from typing import TypeVar, Dict, Tuple
from enum import IntEnum
from paintbynumbers.structs.point import Point

# RGB color type - tuple of (R, G, B) values (0-255)
RGB = Tuple[int, int, int]

# Generic map type
T = TypeVar('T')
IMap = Dict[str, T]


class OrientationEnum(IntEnum):
    """Orientation of a border wall relative to a pixel.

    Used in border tracing to indicate which edge of a pixel
    the path is following.
    """
    Left = 0
    Top = 1
    Right = 2
    Bottom = 3


class PathPoint(Point):
    """A Point with an orientation indicating which wall border is set.

    Used in border tracing to represent points along facet boundaries.
    The orientation indicates which edge of the pixel this point is on.

    Attributes:
        x: X coordinate (inherited from Point)
        y: Y coordinate (inherited from Point)
        orientation: Which wall border this point represents
    """

    def __init__(self, x: int, y: int, orientation: OrientationEnum) -> None:
        """Initialize a PathPoint.

        Args:
            x: X coordinate
            y: Y coordinate
            orientation: Wall border orientation
        """
        super().__init__(x, y)
        self.orientation = orientation

    @classmethod
    def from_point(cls, pt: Point, orientation: OrientationEnum) -> PathPoint:
        """Create PathPoint from existing Point.

        Args:
            pt: Source point
            orientation: Wall border orientation

        Returns:
            New PathPoint with same coordinates
        """
        return cls(pt.x, pt.y, orientation)

    def get_wall_x(self) -> float:
        """Get X coordinate adjusted for wall position.

        Walls are positioned at pixel edges:
        - Left wall: x - 0.5
        - Right wall: x + 0.5
        - Top/Bottom wall: x (unchanged)

        Returns:
            Adjusted X coordinate
        """
        x = float(self.x)
        if self.orientation == OrientationEnum.Left:
            x -= 0.5
        elif self.orientation == OrientationEnum.Right:
            x += 0.5
        return x

    def get_wall_y(self) -> float:
        """Get Y coordinate adjusted for wall position.

        Walls are positioned at pixel edges:
        - Top wall: y - 0.5
        - Bottom wall: y + 0.5
        - Left/Right wall: y (unchanged)

        Returns:
            Adjusted Y coordinate
        """
        y = float(self.y)
        if self.orientation == OrientationEnum.Top:
            y -= 0.5
        elif self.orientation == OrientationEnum.Bottom:
            y += 0.5
        return y

    def __repr__(self) -> str:
        """String representation."""
        return f"PathPoint(x={self.x}, y={self.y}, orientation={self.orientation.name})"

    def __eq__(self, other: object) -> bool:
        """Check equality including orientation."""
        if not isinstance(other, PathPoint):
            return NotImplemented
        return (
            self.x == other.x
            and self.y == other.y
            and self.orientation == other.orientation
        )

    def __hash__(self) -> int:
        """Hash including orientation."""
        return hash((self.x, self.y, self.orientation))
