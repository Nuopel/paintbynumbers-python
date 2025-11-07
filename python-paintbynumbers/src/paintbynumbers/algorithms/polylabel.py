"""Polylabel algorithm for finding pole of inaccessibility.

This is a Python port of https://github.com/mapbox/polylabel to calculate
the pole of inaccessibility quickly. The pole of inaccessibility is the most
distant internal point from the polygon outline (not to be confused with centroid).

This is useful for optimal label placement in paint-by-numbers generation.
"""

from __future__ import annotations
from typing import List, Tuple
import heapq
import math


Point = Tuple[float, float]
PolygonRing = List[Point]
Polygon = List[PolygonRing]


class PolylabelResult:
    """Result of polylabel algorithm.

    Attributes:
        pt: The optimal point (x, y) for label placement
        distance: Distance from the point to the nearest polygon edge
    """

    def __init__(self, pt: Point, distance: float) -> None:
        """Create a polylabel result.

        Args:
            pt: The optimal point (x, y)
            distance: Distance to nearest edge
        """
        self.pt = pt
        self.distance = distance


class _Cell:
    """Cell in the grid search for pole of inaccessibility.

    Represents a square cell in the recursive grid subdivision algorithm.
    """

    def __init__(self, x: float, y: float, h: float, polygon: Polygon) -> None:
        """Create a cell.

        Args:
            x: Cell center x coordinate
            y: Cell center y coordinate
            h: Half the cell size
            polygon: The polygon to calculate distance to
        """
        self.x = x
        self.y = y
        self.h = h
        self.d = _point_to_polygon_dist(x, y, polygon)
        self.max = self.d + self.h * math.sqrt(2)

    def __lt__(self, other: _Cell) -> bool:
        """Compare cells by their max potential distance (for heap).

        Args:
            other: Other cell to compare to

        Returns:
            True if this cell has higher potential than other
        """
        # Reversed for max-heap behavior (higher max = higher priority)
        return self.max > other.max


def polylabel(polygon: Polygon, precision: float = 1.0) -> PolylabelResult:
    """Find pole of inaccessibility for a polygon.

    The pole of inaccessibility is the most distant internal point from the
    polygon outline. This is useful for optimal label placement.

    Args:
        polygon: List of rings (first ring is outer boundary, rest are holes)
        precision: Stop when cell size is below this threshold

    Returns:
        PolylabelResult with optimal point and distance to edge

    Example:
        >>> polygon = [[(0, 0), (10, 0), (10, 10), (0, 10)]]
        >>> result = polylabel(polygon, precision=1.0)
        >>> print(f"Optimal point: {result.pt}, distance: {result.distance}")
    """
    # Find the bounding box of the outer ring
    min_x = float('inf')
    min_y = float('inf')
    max_x = float('-inf')
    max_y = float('-inf')

    for x, y in polygon[0]:
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x)
        max_y = max(max_y, y)

    width = max_x - min_x
    height = max_y - min_y
    cell_size = min(width, height)
    h = cell_size / 2

    if cell_size == 0:
        return PolylabelResult((min_x, min_y), 0)

    # Priority queue of cells in order of their "potential" (max distance to polygon)
    # Using negative max for max-heap behavior
    cell_queue: List[_Cell] = []

    # Cover polygon with initial cells
    y = min_y
    while y < max_y:
        x = min_x
        while x < max_x:
            cell = _Cell(x + h, y + h, h, polygon)
            heapq.heappush(cell_queue, cell)
            x += cell_size
        y += cell_size

    # Take centroid as the first best guess
    best_cell = _get_centroid_cell(polygon)

    # Special case for rectangular polygons
    bbox_cell = _Cell(min_x + width / 2, min_y + height / 2, 0, polygon)
    if bbox_cell.d > best_cell.d:
        best_cell = bbox_cell

    num_probes = len(cell_queue)

    while len(cell_queue) > 0:
        # Pick the most promising cell from the queue
        cell = heapq.heappop(cell_queue)

        # Update the best cell if we found a better one
        if cell.d > best_cell.d:
            best_cell = cell

        # Do not drill down further if there's no chance of a better solution
        if cell.max - best_cell.d <= precision:
            continue

        # Split the cell into four cells
        h = cell.h / 2
        heapq.heappush(cell_queue, _Cell(cell.x - h, cell.y - h, h, polygon))
        heapq.heappush(cell_queue, _Cell(cell.x + h, cell.y - h, h, polygon))
        heapq.heappush(cell_queue, _Cell(cell.x - h, cell.y + h, h, polygon))
        heapq.heappush(cell_queue, _Cell(cell.x + h, cell.y + h, h, polygon))
        num_probes += 4

    return PolylabelResult((best_cell.x, best_cell.y), best_cell.d)


def _get_seg_dist_sq(px: float, py: float, a: Point, b: Point) -> float:
    """Get squared distance from a point to a segment.

    Args:
        px: Point x coordinate
        py: Point y coordinate
        a: Segment start point
        b: Segment end point

    Returns:
        Squared distance from point to segment
    """
    x = a[0]
    y = a[1]
    dx = b[0] - x
    dy = b[1] - y

    if dx != 0 or dy != 0:
        t = ((px - x) * dx + (py - y) * dy) / (dx * dx + dy * dy)

        if t > 1:
            x = b[0]
            y = b[1]
        elif t > 0:
            x += dx * t
            y += dy * t

    dx = px - x
    dy = py - y

    return dx * dx + dy * dy


def _point_to_polygon_dist(x: float, y: float, polygon: Polygon) -> float:
    """Calculate signed distance from point to polygon outline.

    Distance is negative if point is outside polygon.

    Args:
        x: Point x coordinate
        y: Point y coordinate
        polygon: The polygon (list of rings)

    Returns:
        Signed distance (negative if outside)
    """
    inside = False
    min_dist_sq = float('inf')

    for ring in polygon:
        ring_len = len(ring)
        j = ring_len - 1
        for i in range(ring_len):
            a = ring[i]
            b = ring[j]

            # Ray casting for inside/outside test
            if ((a[1] > y) != (b[1] > y)) and \
               (x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]):
                inside = not inside

            # Distance to segment
            min_dist_sq = min(min_dist_sq, _get_seg_dist_sq(x, y, a, b))

            j = i

    return (1 if inside else -1) * math.sqrt(min_dist_sq)


def _get_centroid_cell(polygon: Polygon) -> _Cell:
    """Calculate centroid of polygon as initial guess.

    Args:
        polygon: The polygon

    Returns:
        Cell at the centroid
    """
    area = 0.0
    x = 0.0
    y = 0.0
    points = polygon[0]

    j = len(points) - 1
    for i in range(len(points)):
        a = points[i]
        b = points[j]
        f = a[0] * b[1] - b[0] * a[1]
        x += (a[0] + b[0]) * f
        y += (a[1] + b[1]) * f
        area += f * 3
        j = i

    if area == 0:
        return _Cell(points[0][0], points[0][1], 0, polygon)

    return _Cell(x / area, y / area, 0, polygon)
