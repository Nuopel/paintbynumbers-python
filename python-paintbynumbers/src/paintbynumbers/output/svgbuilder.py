"""SVG generation for paint-by-numbers output.

This module generates SVG files from processed facets, with support for
fills, strokes, labels, and smooth curves using quadratic Bezier paths.
"""

from __future__ import annotations
from typing import List, Tuple, Optional
from xml.etree import ElementTree as ET
from paintbynumbers.processing.facetmanagement import FacetResult
from paintbynumbers.structs.point import Point
from paintbynumbers.core.types import RGB

# SVG constants
DEFAULT_FONT_SIZE = 50
DEFAULT_FONT_COLOR = "black"
DEFAULT_STROKE_WIDTH = 1


class SVGBuilder:
    """Builds SVG output from facet results.

    Generates SVG files with smooth paths using quadratic Bezier curves,
    optional fills and strokes, and color labels positioned at optimal locations.
    """

    @staticmethod
    def create_svg(
        facet_result: FacetResult,
        colors_by_index: List[RGB],
        size_multiplier: float = 1.0,
        fill: bool = True,
        stroke: bool = True,
        add_color_labels: bool = True,
        font_size: int = DEFAULT_FONT_SIZE,
        font_color: str = DEFAULT_FONT_COLOR
    ) -> str:
        """Create SVG string from facet result.

        Args:
            facet_result: FacetResult with traced borders and segments
            colors_by_index: List of RGB colors indexed by color ID
            size_multiplier: Scale factor for output size
            fill: Whether to fill facets with color
            stroke: Whether to draw black border strokes
            add_color_labels: Whether to add color number labels
            font_size: Font size for labels
            font_color: Color for label text

        Returns:
            SVG string content

        Example:
            >>> from paintbynumbers.processing.facetmanagement import FacetResult
            >>> facet_result = FacetResult()
            >>> colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            >>> svg_content = SVGBuilder.create_svg(facet_result, colors)
            >>> with open('output.svg', 'w') as f:
            ...     f.write(svg_content)
        """
        # Create root SVG element
        svg = ET.Element('svg')
        svg.set('xmlns', 'http://www.w3.org/2000/svg')
        svg.set('width', str(int(size_multiplier * facet_result.width)))
        svg.set('height', str(int(size_multiplier * facet_result.height)))
        svg.set('viewBox', f'0 0 {facet_result.width} {facet_result.height}')

        # Process each facet
        for f in facet_result.facets:
            if f is None or len(f.borderSegments) == 0:
                continue

            # Get full path from border segments
            newpath = f.get_full_path_from_border_segments(use_walls=False)

            if len(newpath) == 0:
                continue

            # Close loop if necessary
            if (newpath[0].x != newpath[-1].x or
                newpath[0].y != newpath[-1].y):
                newpath.append(Point(newpath[0].x, newpath[0].y))

            # Create SVG path with quadratic Bezier curves for smoothness
            path_data = SVGBuilder._create_path_data(newpath, size_multiplier)

            # Create path element
            path = ET.SubElement(svg, 'path')
            path.set('data-facet-id', str(f.id))
            path.set('d', path_data)

            # Set stroke
            if stroke:
                path.set('stroke', '#000')
            elif fill:
                # Make border same color as fill to prevent gaps
                rgb = colors_by_index[f.color]
                path.set('stroke', f'rgb({rgb[0]},{rgb[1]},{rgb[2]})')
            else:
                path.set('stroke', 'none')

            path.set('stroke-width', str(DEFAULT_STROKE_WIDTH))

            # Set fill
            if fill:
                rgb = colors_by_index[f.color]
                path.set('fill', f'rgb({rgb[0]},{rgb[1]},{rgb[2]})')
            else:
                path.set('fill', 'none')

            # Add label if requested
            if add_color_labels:
                SVGBuilder._add_label(svg, f, font_size, font_color, size_multiplier)

        # Convert to string
        return SVGBuilder._element_to_string(svg)

    @staticmethod
    def _create_path_data(path: List[Point], size_multiplier: float) -> str:
        """Create SVG path data with quadratic Bezier curves.

        Uses quadratic curves (Q command) for smooth, natural-looking paths
        by placing control points at midpoints between consecutive points.

        Args:
            path: List of points forming the path
            size_multiplier: Scale factor

        Returns:
            SVG path data string
        """
        if len(path) == 0:
            return ""

        # Start with Move command
        data = f"M {path[0].x * size_multiplier} {path[0].y * size_multiplier} "

        # Add quadratic Bezier curves
        for i in range(1, len(path)):
            # Control point is at midpoint between consecutive points
            midpoint_x = (path[i].x + path[i - 1].x) / 2
            midpoint_y = (path[i].y + path[i - 1].y) / 2

            # Q control_x control_y end_x end_y
            data += f"Q {midpoint_x * size_multiplier} {midpoint_y * size_multiplier} "
            data += f"{path[i].x * size_multiplier} {path[i].y * size_multiplier} "

        # Close path
        data += "Z"

        return data

    @staticmethod
    def _add_label(
        svg: ET.Element,
        facet,
        font_size: int,
        font_color: str,
        size_multiplier: float
    ) -> None:
        """Add color label to SVG.

        Args:
            svg: Parent SVG element
            facet: Facet to add label for
            font_size: Font size
            font_color: Font color
            size_multiplier: Scale factor
        """
        # Calculate label position (center of label bounds)
        label_x = (facet.labelBounds.minX + facet.labelBounds.maxX) / 2
        label_y = (facet.labelBounds.minY + facet.labelBounds.maxY) / 2

        # Adjust font size based on number of digits
        label_text = str(facet.color)
        nr_of_digits = len(label_text)
        adjusted_font_size = font_size / nr_of_digits

        # Create text element
        text = ET.SubElement(svg, 'text')
        text.set('x', str(label_x * size_multiplier))
        text.set('y', str(label_y * size_multiplier))
        text.set('font-family', 'Tahoma')
        text.set('font-size', str(adjusted_font_size))
        text.set('dominant-baseline', 'middle')
        text.set('text-anchor', 'middle')
        text.set('fill', font_color)
        text.text = label_text

    @staticmethod
    def _element_to_string(element: ET.Element) -> str:
        """Convert ElementTree element to string.

        Args:
            element: XML element

        Returns:
            XML string with declaration
        """
        # Create tree and convert to string
        tree = ET.ElementTree(element)

        # Write to string with XML declaration
        import io
        output = io.BytesIO()
        tree.write(output, encoding='utf-8', xml_declaration=True)
        return output.getvalue().decode('utf-8')
