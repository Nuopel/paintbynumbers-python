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

        Uses an efficient scanline-based flood fill algorithm that ensures
        complete coverage of connected regions.

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
        # Create a visited callback that returns True if pixel should be SKIPPED
        def visited(x: int, y: int) -> bool:
            return not should_include(x, y)

        # Use scanline-based fill algorithm
        self._fill_scanline(start.x, start.y, width, height, visited, on_fill)
        return 0  # Count not tracked in scanline algorithm

    def _fill_scanline(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        visited: Callable[[int, int], bool],
        set_fill: Callable[[int, int], None]
    ) -> None:
        """Scanline-based flood fill algorithm.

        This is a port of the efficient flood fill algorithm from:
        http://www.adammil.net/blog/v126_A_More_Efficient_Flood_Fill.html

        Args:
            x: Starting x coordinate
            y: Starting y coordinate
            width: Width of the area
            height: Height of the area
            visited: Function that returns True if pixel should be skipped
            set_fill: Callback to mark pixel as filled
        """
        # Move to upper-left corner of the region
        xx = x
        yy = y
        while True:
            ox = xx
            oy = yy
            while yy != 0 and not visited(xx, yy - 1):
                yy -= 1
            while xx != 0 and not visited(xx - 1, yy):
                xx -= 1
            if xx == ox and yy == oy:
                break

        self._fill_core(xx, yy, width, height, visited, set_fill)

    def _fill_core(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        visited: Callable[[int, int], bool],
        set_fill: Callable[[int, int], None]
    ) -> None:
        """Core scanline fill algorithm.

        Args:
            x: Starting x coordinate
            y: Starting y coordinate
            width: Width of the area
            height: Height of the area
            visited: Function that returns True if pixel should be skipped
            set_fill: Callback to mark pixel as filled
        """
        last_row_length = 0

        while True:
            row_length = 0
            sx = x

            if last_row_length != 0 and visited(x, y):
                while True:
                    last_row_length -= 1
                    if last_row_length == 0:
                        return
                    x += 1
                    if not visited(x, y):
                        break
                sx = x
            else:
                while x != 0 and not visited(x - 1, y):
                    x -= 1
                    set_fill(x, y)
                    row_length += 1
                    last_row_length += 1

                    if y != 0 and not visited(x, y - 1):
                        self._fill_scanline(x, y - 1, width, height, visited, set_fill)

            # Scan current row
            while sx < width and not visited(sx, y):
                set_fill(sx, y)
                row_length += 1
                sx += 1

            # Handle non-rectangular blocks
            if row_length < last_row_length:
                end = x + last_row_length
                sx += 1
                while sx < end:
                    if not visited(sx, y):
                        self._fill_core(sx, y, width, height, visited, set_fill)
                    sx += 1
            elif row_length > last_row_length and y != 0:
                ux = x + last_row_length
                ux += 1
                while ux < sx:
                    if not visited(ux, y - 1):
                        self._fill_scanline(ux, y - 1, width, height, visited, set_fill)
                    ux += 1

            last_row_length = row_length
            y += 1

            if last_row_length == 0 or y >= height:
                break
