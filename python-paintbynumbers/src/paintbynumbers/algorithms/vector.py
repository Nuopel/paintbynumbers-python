"""Vector class for K-means clustering.

This module provides a Vector class representing points in n-dimensional space
with optional weight and metadata. Used primarily for color clustering in
RGB/HSL/LAB color spaces.
"""

from __future__ import annotations
from typing import List, Any, Optional
import math


class Vector:
    """A vector in n-dimensional space with weight and optional metadata.

    Represents a point in n-dimensional space. The weight is used for weighted
    averaging during K-means clustering (e.g., color frequency).

    Attributes:
        values: List of dimensional values
        weight: Weight for weighted operations (default: 1.0)
        tag: Optional metadata (e.g., original RGB color)
    """

    def __init__(self, values: List[float], weight: float = 1.0, tag: Optional[Any] = None) -> None:
        """Create a new vector.

        Args:
            values: List of dimensional values
            weight: Weight for weighted operations (default: 1.0)
            tag: Optional metadata tag

        Example:
            >>> # Create RGB color vector
            >>> color_vec = Vector([255, 128, 0], 1, {"r": 255, "g": 128, "b": 0})
            >>> # Create weighted point
            >>> weighted_vec = Vector([1, 2, 3], 5)
        """
        self.values = values
        self.weight = weight
        self.tag = tag

    def distance_to(self, other: Vector) -> float:
        """Calculate Euclidean distance to another vector.

        Args:
            other: Vector to calculate distance to

        Returns:
            Euclidean distance between vectors

        Example:
            >>> v1 = Vector([0, 0])
            >>> v2 = Vector([3, 4])
            >>> v1.distance_to(v2)
            5.0
        """
        sum_squares = 0.0
        for i in range(len(self.values)):
            diff = other.values[i] - self.values[i]
            sum_squares += diff * diff
        return math.sqrt(sum_squares)

    @staticmethod
    def average(vectors: List[Vector]) -> Vector:
        """Calculate weighted average of multiple vectors.

        Computes the centroid of a set of vectors, taking their weights into account.
        The resulting vector's weight is the sum of all input weights.

        Args:
            vectors: List of vectors to average

        Returns:
            New vector representing the weighted average

        Raises:
            ValueError: If vectors list is empty

        Example:
            >>> v1 = Vector([0, 0], 1)
            >>> v2 = Vector([10, 10], 2)
            >>> avg = Vector.average([v1, v2])
            >>> avg.values
            [6.666..., 6.666...]
            >>> avg.weight
            3.0
        """
        if len(vectors) == 0:
            raise ValueError("Cannot average empty array of vectors")

        dims = len(vectors[0].values)
        values: List[float] = [0.0] * dims

        weight_sum = 0.0
        for vec in vectors:
            weight_sum += vec.weight
            for i in range(dims):
                values[i] += vec.weight * vec.values[i]

        # Normalize by total weight
        for i in range(len(values)):
            values[i] /= weight_sum

        return Vector(values, weight_sum)

    def clone(self) -> Vector:
        """Create a deep clone of this vector.

        Returns:
            New vector with copied values

        Example:
            >>> original = Vector([1, 2, 3], 5, {"data": "test"})
            >>> copy = original.clone()
            >>> copy.values[0] = 999
            >>> original.values[0]
            1
        """
        return Vector(self.values.copy(), self.weight, self.tag)

    @property
    def dimensions(self) -> int:
        """Get the dimensionality of this vector.

        Returns:
            Number of dimensions
        """
        return len(self.values)

    def magnitude_squared(self) -> float:
        """Get the squared magnitude of this vector.

        Returns:
            Sum of squared values

        Example:
            >>> v = Vector([3, 4])
            >>> v.magnitude_squared()
            25.0
        """
        sum_val = 0.0
        for i in range(len(self.values)):
            sum_val += self.values[i] * self.values[i]
        return sum_val

    def magnitude(self) -> float:
        """Get the magnitude (length) of this vector.

        Returns:
            Euclidean length of the vector

        Example:
            >>> v = Vector([3, 4])
            >>> v.magnitude()
            5.0
        """
        return math.sqrt(self.magnitude_squared())

    def __repr__(self) -> str:
        """String representation of vector."""
        return f"Vector(values={self.values}, weight={self.weight})"

    def __eq__(self, other: object) -> bool:
        """Check equality with another vector."""
        if not isinstance(other, Vector):
            return NotImplemented
        return (
            self.values == other.values
            and self.weight == other.weight
        )
