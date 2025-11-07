"""Flood fill algorithm for finding connected regions.

This module provides a class-based interface for flood-fill operations, making it
easier to test and reuse across different parts of the application.
"""

from __future__ import annotations
from typing import List, Set, Callable
from paintbynumbers.structs.point import Point
from paintbynumbers.utils.boundary import is_in_bounds


class FloodFillAlgorithm:
    """Flood fill algorithm implementation.

    Uses a stack-based approach to find all connected pixels matching a predicate.
    The algorithm starts from a seed point and expands to all reachable neighbors
    that satisfy the given condition.

    Example:
        >>> flood_fill = FloodFillAlgorithm()
        >>> start = Point(10, 10)
        >>> region = flood_fill.fill(
        ...     start,
        ...     width,
        ...     height,
        ...     lambda x, y: color_map[y * width + x] == target_color
        ... )
        >>> print(f"Found region with {len(region)} pixels")
    """

    def fill(
        self,
        start: Point,
        width: int,
        height: int,
        should_include: Callable[[int, int], bool]
    ) -> List[Point]:
        """Perform flood fill from a starting point.

        Finds all connected pixels that satisfy the should_include predicate
        using 4-connectivity (up, down, left, right neighbors).

        Args:
            start: Starting point for the flood fill
            width: Width of the area to fill
            height: Height of the area to fill
            should_include: Predicate function that returns true if a pixel should be included

        Returns:
            Array of all points in the filled region

        Example:
            >>> flood_fill = FloodFillAlgorithm()
            >>> filled = flood_fill.fill(
            ...     Point(5, 5),
            ...     100,
            ...     100,
            ...     lambda x, y: not visited[y * 100 + x] and color_map[y * 100 + x] == target_color
            ... )
        """
        filled: List[Point] = []
        visited: Set[int] = set()
        stack: List[Point] = [start]

        while len(stack) > 0:
            point = stack.pop()
            key = point.y * width + point.x

            # Skip if already visited
            if key in visited:
                continue

            # Skip if out of bounds
            if not is_in_bounds(point.x, point.y, width, height):
                continue

            # Skip if doesn't match predicate
            if not should_include(point.x, point.y):
                continue

            # Mark as visited and add to result
            visited.add(key)
            filled.append(point)

            # Add 4-connected neighbors to stack
            # Note: We don't use get_neighbors_4 here to avoid extra allocations
            # Instead, we push points directly and rely on bounds checking above
            if point.y > 0:
                stack.append(Point(point.x, point.y - 1))  # Up
            if point.y < height - 1:
                stack.append(Point(point.x, point.y + 1))  # Down
            if point.x > 0:
                stack.append(Point(point.x - 1, point.y))  # Left
            if point.x < width - 1:
                stack.append(Point(point.x + 1, point.y))  # Right

        return filled

    def fill_with_callback(
        self,
        start: Point,
        width: int,
        height: int,
        should_include: Callable[[int, int], bool],
        on_fill: Callable[[int, int], None]
    ) -> int:
        """Perform flood fill with a custom callback for each filled pixel.

        Similar to fill() but executes a callback for each pixel instead of
        collecting them in an array. This is more memory-efficient for large regions.

        Args:
            start: Starting point for the flood fill
            width: Width of the area to fill
            height: Height of the area to fill
            should_include: Predicate function that returns true if a pixel should be included
            on_fill: Callback function executed for each filled pixel

        Returns:
            Number of pixels filled

        Example:
            >>> flood_fill = FloodFillAlgorithm()
            >>> count = flood_fill.fill_with_callback(
            ...     Point(5, 5),
            ...     100,
            ...     100,
            ...     lambda x, y: not visited[y * 100 + x],
            ...     lambda x, y: (
            ...         visited.__setitem__(y * 100 + x, True),
            ...         color_map.__setitem__(y * 100 + x, new_color)
            ...     )
            ... )
        """
        visited: Set[int] = set()
        stack: List[Point] = [start]
        count = 0

        while len(stack) > 0:
            point = stack.pop()
            key = point.y * width + point.x

            if key in visited:
                continue

            if not is_in_bounds(point.x, point.y, width, height):
                continue

            if not should_include(point.x, point.y):
                continue

            visited.add(key)
            on_fill(point.x, point.y)
            count += 1

            # Add 4-connected neighbors
            if point.y > 0:
                stack.append(Point(point.x, point.y - 1))
            if point.y < height - 1:
                stack.append(Point(point.x, point.y + 1))
            if point.x > 0:
                stack.append(Point(point.x - 1, point.y))
            if point.x < width - 1:
                stack.append(Point(point.x + 1, point.y))

        return count
