"""Point class for 2D coordinates."""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    """Represents a 2D point with integer coordinates.

    This class is immutable (frozen) to allow use as dictionary keys and in sets.

    Attributes:
        x: X coordinate
        y: Y coordinate
    """

    x: int
    y: int

    def distance_to(self, pt: Point) -> int:
        """Calculate Manhattan distance to another point.

        Uses Manhattan distance (L1 norm) instead of Euclidean distance.
        This is important for maintaining 4-connectivity in the algorithm,
        since sqrt(2) < 2, diagonal neighbors would be considered closer
        than orthogonal neighbors with Euclidean distance.

        Args:
            pt: Target point

        Returns:
            Manhattan distance (sum of absolute differences)
        """
        return abs(pt.x - self.x) + abs(pt.y - self.y)

    def distance_to_coord(self, x: int, y: int) -> int:
        """Calculate Manhattan distance to coordinates.

        Uses Manhattan distance (L1 norm) instead of Euclidean distance.

        Args:
            x: Target X coordinate
            y: Target Y coordinate

        Returns:
            Manhattan distance (sum of absolute differences)
        """
        return abs(x - self.x) + abs(y - self.y)

    def __repr__(self) -> str:
        """String representation of the point."""
        return f"Point(x={self.x}, y={self.y})"
