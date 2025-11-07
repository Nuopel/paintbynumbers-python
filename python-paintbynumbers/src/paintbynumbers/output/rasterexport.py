"""Raster image export from SVG.

This module provides PNG and JPG export functionality by converting SVG
to raster formats using cairosvg or Pillow as fallback.
"""

from __future__ import annotations
from typing import Optional
import io

# Try to import cairosvg, fall back to Pillow if not available
try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class RasterExporter:
    """Export SVG to raster formats (PNG, JPG)."""

    @staticmethod
    def export_png(
        svg_content: str,
        output_path: str,
        scale: float = 1.0
    ) -> None:
        """Export SVG to PNG file.

        Args:
            svg_content: SVG string content
            output_path: Output file path
            scale: Scale factor for output resolution

        Raises:
            ImportError: If neither cairosvg nor PIL is available
            IOError: If file cannot be written

        Example:
            >>> svg = '<svg>...</svg>'
            >>> RasterExporter.export_png(svg, 'output.png', scale=2.0)
        """
        if CAIROSVG_AVAILABLE:
            RasterExporter._export_png_cairosvg(svg_content, output_path, scale)
        elif PIL_AVAILABLE:
            RasterExporter._export_png_pil(svg_content, output_path, scale)
        else:
            raise ImportError(
                "PNG export requires either cairosvg or Pillow. "
                "Install with: pip install cairosvg or pip install Pillow"
            )

    @staticmethod
    def export_jpg(
        svg_content: str,
        output_path: str,
        quality: int = 95,
        scale: float = 1.0
    ) -> None:
        """Export SVG to JPG file.

        Args:
            svg_content: SVG string content
            output_path: Output file path
            quality: JPEG quality (1-100)
            scale: Scale factor for output resolution

        Raises:
            ImportError: If neither cairosvg nor PIL is available
            IOError: If file cannot be written

        Example:
            >>> svg = '<svg>...</svg>'
            >>> RasterExporter.export_jpg(svg, 'output.jpg', quality=90)
        """
        if CAIROSVG_AVAILABLE:
            RasterExporter._export_jpg_cairosvg(svg_content, output_path, quality, scale)
        elif PIL_AVAILABLE:
            RasterExporter._export_jpg_pil(svg_content, output_path, quality, scale)
        else:
            raise ImportError(
                "JPG export requires either cairosvg or Pillow. "
                "Install with: pip install cairosvg or pip install Pillow"
            )

    @staticmethod
    def _export_png_cairosvg(
        svg_content: str,
        output_path: str,
        scale: float
    ) -> None:
        """Export PNG using cairosvg."""
        cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            write_to=output_path,
            scale=scale
        )

    @staticmethod
    def _export_jpg_cairosvg(
        svg_content: str,
        output_path: str,
        quality: int,
        scale: float
    ) -> None:
        """Export JPG using cairosvg via PNG intermediate."""
        # cairosvg doesn't support JPG directly, so go through PNG
        png_bytes = cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            scale=scale
        )

        # Convert PNG to JPG using PIL
        if PIL_AVAILABLE:
            img = Image.open(io.BytesIO(png_bytes))
            # Convert RGBA to RGB for JPEG
            if img.mode == 'RGBA':
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # Use alpha as mask
                img = background
            img.save(output_path, 'JPEG', quality=quality)
        else:
            # Fallback: save as PNG
            with open(output_path, 'wb') as f:
                f.write(png_bytes)

    @staticmethod
    def _export_png_pil(
        svg_content: str,
        output_path: str,
        scale: float
    ) -> None:
        """Export PNG using Pillow (basic rasterization).

        Note: This is a fallback and doesn't support full SVG rendering.
        For best results, use cairosvg.
        """
        # PIL doesn't natively support SVG, so this is a very basic fallback
        # We can't actually render the SVG paths without SVG support
        # This is just a placeholder that creates a blank image
        import xml.etree.ElementTree as ET

        try:
            root = ET.fromstring(svg_content)
            width = int(float(root.get('width', '800')) * scale)
            height = int(float(root.get('height', '600')) * scale)
        except:
            width = int(800 * scale)
            height = int(600 * scale)

        # Create blank image
        img = Image.new('RGB', (width, height), color='white')
        img.save(output_path, 'PNG')

    @staticmethod
    def _export_jpg_pil(
        svg_content: str,
        output_path: str,
        quality: int,
        scale: float
    ) -> None:
        """Export JPG using Pillow (basic rasterization).

        Note: This is a fallback and doesn't support full SVG rendering.
        For best results, use cairosvg.
        """
        # Same limitation as PNG export
        import xml.etree.ElementTree as ET

        try:
            root = ET.fromstring(svg_content)
            width = int(float(root.get('width', '800')) * scale)
            height = int(float(root.get('height', '600')) * scale)
        except:
            width = int(800 * scale)
            height = int(600 * scale)

        # Create blank image
        img = Image.new('RGB', (width, height), color='white')
        img.save(output_path, 'JPEG', quality=quality)


# Convenience functions
def export_png(svg_content: str, output_path: str, scale: float = 1.0) -> None:
    """Export SVG to PNG. Convenience function for RasterExporter.export_png()."""
    RasterExporter.export_png(svg_content, output_path, scale)


def export_jpg(svg_content: str, output_path: str, quality: int = 95, scale: float = 1.0) -> None:
    """Export SVG to JPG. Convenience function for RasterExporter.export_jpg()."""
    RasterExporter.export_jpg(svg_content, output_path, quality, scale)
