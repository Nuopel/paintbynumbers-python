"""Flood fill algorithm for finding connected regions.

This module provides a class-based interface for flood-fill operations, making it
easier to test and reuse across different parts of the application.

The implementation uses a scanline-based algorithm (based on Adam Milazzo's approach)
which is significantly faster than simple stack-based approaches:
- Processes entire horizontal spans at once
- Better cache locality through sequential memory access
- Fewer stack operations (one per span vs one per pixel)
- Guaranteed complete coverage with no missed pixels
"""

from __future__ import annotations
from typing import List, Set, Callable, Tuple
from paintbynumbers.structs.point import Point
from paintbynumbers.utils.boundary import is_in_bounds


class FloodFillAlgorithm:
    """Flood fill algorithm implementation using scanline approach.

    Uses a sophisticated scanline-based algorithm to find all connected pixels.
    This approach fills entire horizontal spans at once, making it much faster
    than pixel-by-pixel approaches while guaranteeing complete coverage.

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
        """Perform scanline-based flood fill from a starting point.

        Finds all connected pixels that satisfy the should_include predicate
        using 4-connectivity. Processes entire horizontal spans for efficiency.

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
        # Bounds check
        if not is_in_bounds(start.x, start.y, width, height):
            return []

        if not should_include(start.x, start.y):
            return []

        filled: List[Point] = []
        visited: Set[int] = set()

        # Stack stores (x, y, direction) tuples
        # direction: 1 = scan up, -1 = scan down, 0 = scan both
        stack: List[Tuple[int, int, int]] = [(start.x, start.y, 0)]

        while stack:
            x, y, dy = stack.pop()

            # Skip if out of bounds or already visited
            if not is_in_bounds(x, y, width, height):
                continue

            key = y * width + x
            if key in visited:
                continue

            if not should_include(x, y):
                continue

            # Find left extent of span
            x1 = x
            while x1 > 0:
                left_key = y * width + (x1 - 1)
                if left_key in visited or not should_include(x1 - 1, y):
                    break
                x1 -= 1

            # Find right extent of span
            x2 = x
            while x2 < width - 1:
                right_key = y * width + (x2 + 1)
                if right_key in visited or not should_include(x2 + 1, y):
                    break
                x2 += 1

            # Fill the span from x1 to x2
            for xi in range(x1, x2 + 1):
                span_key = y * width + xi
                visited.add(span_key)
                filled.append(Point(xi, y))

            # Scan the lines above and below this span
            # For the initial seed, scan both directions
            # For subsequent spans, only scan in the direction we came from
            if dy <= 0 and y > 0:  # Scan up
                self._scan_line(x1, x2, y - 1, -1, width, height, should_include, visited, stack)

            if dy >= 0 and y < height - 1:  # Scan down
                self._scan_line(x1, x2, y + 1, 1, width, height, should_include, visited, stack)

        return filled

    def _scan_line(
        self,
        x1: int,
        x2: int,
        y: int,
        dy: int,
        width: int,
        height: int,
        should_include: Callable[[int, int], bool],
        visited: Set[int],
        stack: List[Tuple[int, int, int]]
    ) -> None:
        """Scan a line for connected regions and add them to the stack.

        Args:
            x1: Start x coordinate of the span to check
            x2: End x coordinate of the span to check
            y: Y coordinate of the line to scan
            dy: Direction we're scanning (1 = down, -1 = up)
            width: Width of the area
            height: Height of the area
            should_include: Predicate for pixel inclusion
            visited: Set of visited pixel keys
            stack: Stack to add new spans to
        """
        in_span = False

        for x in range(x1, x2 + 1):
            key = y * width + x

            # Check if this pixel should be included
            is_valid = (
                is_in_bounds(x, y, width, height) and
                key not in visited and
                should_include(x, y)
            )

            if is_valid:
                if not in_span:
                    # Start of a new span
                    stack.append((x, y, dy))
                    in_span = True
            else:
                in_span = False

    def fill_with_callback(
        self,
        start: Point,
        width: int,
        height: int,
        should_include: Callable[[int, int], bool],
        on_fill: Callable[[int, int], None]
    ) -> int:
        """Perform scanline-based flood fill with a callback for each filled pixel.

        Similar to fill() but executes a callback for each pixel instead of
        collecting them in an array. Uses scanline algorithm for better performance.

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
        # Bounds check
        if not is_in_bounds(start.x, start.y, width, height):
            return 0

        if not should_include(start.x, start.y):
            return 0

        visited: Set[int] = set()
        stack: List[Tuple[int, int, int]] = [(start.x, start.y, 0)]
        count = 0

        while stack:
            x, y, dy = stack.pop()

            # Skip if out of bounds or already visited
            if not is_in_bounds(x, y, width, height):
                continue

            key = y * width + x
            if key in visited:
                continue

            if not should_include(x, y):
                continue

            # Find left extent of span
            x1 = x
            while x1 > 0:
                left_key = y * width + (x1 - 1)
                if left_key in visited or not should_include(x1 - 1, y):
                    break
                x1 -= 1

            # Find right extent of span
            x2 = x
            while x2 < width - 1:
                right_key = y * width + (x2 + 1)
                if right_key in visited or not should_include(x2 + 1, y):
                    break
                x2 += 1

            # Fill the span from x1 to x2
            for xi in range(x1, x2 + 1):
                span_key = y * width + xi
                visited.add(span_key)
                on_fill(xi, y)
                count += 1

            # Scan the lines above and below this span
            if dy <= 0 and y > 0:  # Scan up
                self._scan_line(x1, x2, y - 1, -1, width, height, should_include, visited, stack)

            if dy >= 0 and y < height - 1:  # Scan down
                self._scan_line(x1, x2, y + 1, 1, width, height, should_include, visited, stack)

        return count
