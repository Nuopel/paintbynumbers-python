"""BoundingBox class for rectangular regions."""

from __future__ import annotations
import sys
from paintbynumbers.structs.point import Point


class BoundingBox:
    """Represents an axis-aligned bounding box.

    The bounding box is defined by minimum and maximum X and Y coordinates.
    It can be expanded to include new points.

    Attributes:
        minX: Minimum X coordinate
        minY: Minimum Y coordinate
        maxX: Maximum X coordinate
        maxY: Maximum Y coordinate
    """

    def __init__(
        self,
        minX: int = sys.maxsize,
        minY: int = sys.maxsize,
        maxX: int = -sys.maxsize - 1,
        maxY: int = -sys.maxsize - 1,
    ) -> None:
        """Initialize a bounding box.

        By default, the bounding box is initialized with extreme values
        so that any point will expand it.

        Args:
            minX: Minimum X coordinate (default: maxsize)
            minY: Minimum Y coordinate (default: maxsize)
            maxX: Maximum X coordinate (default: -maxsize-1)
            maxY: Maximum Y coordinate (default: -maxsize-1)
        """
        self.minX = minX
        self.minY = minY
        self.maxX = maxX
        self.maxY = maxY

    @property
    def width(self) -> int:
        """Calculate the width of the bounding box.

        Returns:
            Width (maxX - minX + 1)
        """
        return self.maxX - self.minX + 1

    @property
    def height(self) -> int:
        """Calculate the height of the bounding box.

        Returns:
            Height (maxY - minY + 1)
        """
        return self.maxY - self.minY + 1

    def contains(self, x: int, y: int) -> bool:
        """Check if a point is contained within the bounding box.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if point is within bounds (inclusive), False otherwise
        """
        return self.minX <= x <= self.maxX and self.minY <= y <= self.maxY

    def contains_point(self, point: Point) -> bool:
        """Check if a Point is contained within the bounding box.

        Args:
            point: Point to check

        Returns:
            True if point is within bounds (inclusive), False otherwise
        """
        return self.contains(point.x, point.y)

    def expand(self, x: int, y: int) -> None:
        """Expand the bounding box to include a point.

        Updates minX, minY, maxX, maxY to ensure the point is contained.

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.minX = min(self.minX, x)
        self.minY = min(self.minY, y)
        self.maxX = max(self.maxX, x)
        self.maxY = max(self.maxY, y)

    def expand_point(self, point: Point) -> None:
        """Expand the bounding box to include a Point.

        Args:
            point: Point to include
        """
        self.expand(point.x, point.y)

    def is_valid(self) -> bool:
        """Check if the bounding box is valid (has been expanded at least once).

        A valid bounding box has minX <= maxX and minY <= maxY.

        Returns:
            True if valid, False if still in initial state
        """
        return self.minX <= self.maxX and self.minY <= self.maxY

    def __repr__(self) -> str:
        """String representation of the bounding box."""
        return (
            f"BoundingBox(minX={self.minX}, minY={self.minY}, "
            f"maxX={self.maxX}, maxY={self.maxY})"
        )

    def __eq__(self, other: object) -> bool:
        """Check equality with another bounding box."""
        if not isinstance(other, BoundingBox):
            return NotImplemented
        return (
            self.minX == other.minX
            and self.minY == other.minY
            and self.maxX == other.maxX
            and self.maxY == other.maxY
        )
