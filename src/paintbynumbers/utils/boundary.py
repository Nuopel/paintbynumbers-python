"""Boundary checking and validation utilities.

This module provides reusable functions for checking if points are within
image boundaries, clamping values, and getting neighbors. These utilities
eliminate duplicated boundary checking logic throughout the codebase.
"""

from __future__ import annotations
from enum import IntFlag
from typing import List
from paintbynumbers.structs.point import Point


class EdgeType(IntFlag):
    """Edge type flags for identifying which edge(s) a point is on.

    Can be combined using bitwise OR for corners.
    """
    NONE = 0
    LEFT = 1
    RIGHT = 2
    TOP = 4
    BOTTOM = 8


def is_in_bounds(x: int, y: int, width: int, height: int) -> bool:
    """Check if a point is within image boundaries.

    Args:
        x: X coordinate to check
        y: Y coordinate to check
        width: Image width (exclusive upper bound)
        height: Image height (exclusive upper bound)

    Returns:
        True if point is within bounds [0, width) × [0, height)

    Example:
        >>> if is_in_bounds(x, y, image.width, image.height):
        ...     pixel = image_data[y * width + x]
    """
    return 0 <= x < width and 0 <= y < height


def clamp(value: int, min_val: int, max_val: int) -> int:
    """Clamp a value to a range [min, max].

    Args:
        value: Value to clamp
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)

    Returns:
        Clamped value within [min, max]

    Example:
        >>> clamp(-5, 0, 10)
        0
        >>> clamp(15, 0, 10)
        10
        >>> clamp(5, 0, 10)
        5
    """
    return max(min_val, min(value, max_val))


def clamp_point(point: Point, width: int, height: int) -> Point:
    """Clamp a point to image boundaries.

    Args:
        point: Point to clamp
        width: Image width
        height: Image height

    Returns:
        New point with coordinates clamped to [0, width-1] × [0, height-1]

    Example:
        >>> clamped = clamp_point(Point(-5, 100), 50, 50)
        Point(x=0, y=49)
    """
    return Point(
        clamp(point.x, 0, width - 1),
        clamp(point.y, 0, height - 1)
    )


def get_neighbors_4(x: int, y: int, width: int, height: int) -> List[Point]:
    """Get 4-connected neighbors (up, down, left, right).

    Only returns neighbors that are within image boundaries.

    Args:
        x: X coordinate of center point
        y: Y coordinate of center point
        width: Image width
        height: Image height

    Returns:
        List of valid neighbor points (2-4 neighbors depending on position)

    Example:
        >>> # Center point returns 4 neighbors
        >>> neighbors = get_neighbors_4(5, 5, 10, 10)
        >>> len(neighbors)
        4
        >>> # Corner returns 2 neighbors
        >>> corner = get_neighbors_4(0, 0, 10, 10)
        >>> len(corner)
        2
    """
    neighbors: List[Point] = []

    # Up
    if y > 0:
        neighbors.append(Point(x, y - 1))
    # Down
    if y < height - 1:
        neighbors.append(Point(x, y + 1))
    # Left
    if x > 0:
        neighbors.append(Point(x - 1, y))
    # Right
    if x < width - 1:
        neighbors.append(Point(x + 1, y))

    return neighbors


def get_neighbors_8(x: int, y: int, width: int, height: int) -> List[Point]:
    """Get 8-connected neighbors (includes diagonals).

    Only returns neighbors that are within image boundaries.

    Args:
        x: X coordinate of center point
        y: Y coordinate of center point
        width: Image width
        height: Image height

    Returns:
        List of valid neighbor points (3-8 neighbors depending on position)

    Example:
        >>> # Center point returns 8 neighbors
        >>> neighbors = get_neighbors_8(5, 5, 10, 10)
        >>> len(neighbors)
        8
        >>> # Corner returns 3 neighbors
        >>> corner = get_neighbors_8(0, 0, 10, 10)
        >>> len(corner)
        3
    """
    neighbors: List[Point] = []

    for dy in range(-1, 2):
        for dx in range(-1, 2):
            if dx == 0 and dy == 0:
                continue  # Skip center point

            nx = x + dx
            ny = y + dy

            if is_in_bounds(nx, ny, width, height):
                neighbors.append(Point(nx, ny))

    return neighbors


def is_on_edge(x: int, y: int, width: int, height: int) -> bool:
    """Check if a point is on any edge of the image.

    Args:
        x: X coordinate to check
        y: Y coordinate to check
        width: Image width
        height: Image height

    Returns:
        True if point is on left, right, top, or bottom edge

    Example:
        >>> is_on_edge(0, 5, 10, 10)    # Left edge
        True
        >>> is_on_edge(9, 5, 10, 10)    # Right edge
        True
        >>> is_on_edge(5, 5, 10, 10)    # Center
        False
        >>> is_on_edge(0, 0, 10, 10)    # Corner
        True
    """
    return x == 0 or x == width - 1 or y == 0 or y == height - 1


def get_edge_type(x: int, y: int, width: int, height: int) -> EdgeType:
    """Get which edge(s) a point is on.

    Returns a bitmask that can be tested with bitwise AND.
    Points on corners will have multiple flags set.

    Args:
        x: X coordinate to check
        y: Y coordinate to check
        width: Image width
        height: Image height

    Returns:
        EdgeType bitmask indicating which edge(s) the point is on

    Example:
        >>> edge = get_edge_type(0, 0, 10, 10)
        >>> bool(edge & EdgeType.LEFT)
        True
        >>> bool(edge & EdgeType.TOP)
        True
        >>> center = get_edge_type(5, 5, 10, 10)
        >>> center == EdgeType.NONE
        True
    """
    edge = EdgeType.NONE

    if x == 0:
        edge |= EdgeType.LEFT
    if x == width - 1:
        edge |= EdgeType.RIGHT
    if y == 0:
        edge |= EdgeType.TOP
    if y == height - 1:
        edge |= EdgeType.BOTTOM

    return edge
