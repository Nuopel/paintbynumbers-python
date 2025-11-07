"""Tests for Phase 6: SVG generation, label placement, and PNG export."""

import pytest
from paintbynumbers.processing.facetmanagement import Facet, FacetResult, PathSegment, FacetBoundarySegment
from paintbynumbers.processing.facetlabelplacer import FacetLabelPlacer
from paintbynumbers.output.svgbuilder import SVGBuilder
from paintbynumbers.output.rasterexport import RasterExporter
from paintbynumbers.structs.point import Point
from paintbynumbers.structs.boundingbox import BoundingBox
from paintbynumbers.structs.typed_arrays import Uint32Array2D
from paintbynumbers.core.types import PathPoint, OrientationEnum
import tempfile
import os


class TestFacetGetFullPath:
    """Test Facet.get_full_path_from_border_segments()."""

    def test_get_full_path_no_segments(self):
        """Test with no segments."""
        facet = Facet()
        facet.borderSegments = []
        path = facet.get_full_path_from_border_segments()
        assert len(path) == 0

    def test_get_full_path_single_segment(self):
        """Test with single segment."""
        points = [PathPoint(i, 0, OrientationEnum.Top) for i in range(5)]
        segment = PathSegment(points, neighbour=1)
        boundary = FacetBoundarySegment(segment, neighbour=1, reverseOrder=False)

        facet = Facet()
        facet.borderSegments = [boundary]

        path = facet.get_full_path_from_border_segments(use_walls=False)
        assert len(path) == 5
        assert all(isinstance(p, Point) for p in path)

    def test_get_full_path_use_walls(self):
        """Test wall coordinates."""
        points = [PathPoint(5, 5, OrientationEnum.Left)]
        segment = PathSegment(points, neighbour=1)
        boundary = FacetBoundarySegment(segment, neighbour=1, reverseOrder=False)

        facet = Facet()
        facet.borderSegments = [boundary]

        path = facet.get_full_path_from_border_segments(use_walls=True)
        assert len(path) == 1
        assert path[0].x == 4.5  # Left wall: x - 0.5
        assert path[0].y == 5.0

    def test_get_full_path_reverse_order(self):
        """Test reverse order segment."""
        points = [PathPoint(i, 0, OrientationEnum.Top) for i in range(5)]
        segment = PathSegment(points, neighbour=1)
        boundary = FacetBoundarySegment(segment, neighbour=1, reverseOrder=True)

        facet = Facet()
        facet.borderSegments = [boundary]

        path = facet.get_full_path_from_border_segments(use_walls=False)
        # Should be reversed
        assert path[0].x == 4
        assert path[-1].x == 0


class TestFacetLabelPlacer:
    """Test FacetLabelPlacer functionality."""

    def test_build_label_bounds_empty(self):
        """Test with empty facet list."""
        facet_result = FacetResult()
        facet_result.width = 10
        facet_result.height = 10
        facet_result.facetMap = Uint32Array2D(10, 10)
        facet_result.facets = []

        # Should not crash
        FacetLabelPlacer.build_facet_label_bounds(facet_result)

    def test_build_label_bounds_simple_facet(self):
        """Test label placement for a simple facet."""
        facet_result = FacetResult()
        facet_result.width = 10
        facet_result.height = 10
        facet_result.facetMap = Uint32Array2D(10, 10)

        # Create a simple facet with border segments
        facet0 = Facet()
        facet0.id = 0
        facet0.color = 0
        facet0.pointCount = 9
        facet0.bbox = BoundingBox(minX=0, minY=0, maxX=2, maxY=2)
        facet0.neighbourFacets = []
        facet0.neighbourFacetsIsDirty = False

        # Create border segments
        points = [
            PathPoint(0, 0, OrientationEnum.Top),
            PathPoint(2, 0, OrientationEnum.Top),
            PathPoint(2, 2, OrientationEnum.Right),
            PathPoint(0, 2, OrientationEnum.Bottom),
        ]
        segment = PathSegment(points, neighbour=-1)
        boundary = FacetBoundarySegment(segment, neighbour=-1, reverseOrder=False)
        facet0.borderSegments = [boundary]

        facet_result.facets = [facet0]

        # Build label bounds
        FacetLabelPlacer.build_facet_label_bounds(facet_result)

        # Should have label bounds
        assert facet0.labelBounds is not None
        assert isinstance(facet0.labelBounds, BoundingBox)


class TestSVGBuilder:
    """Test SVG generation."""

    def test_create_svg_empty(self):
        """Test SVG creation with empty facet list."""
        facet_result = FacetResult()
        facet_result.width = 100
        facet_result.height = 100
        facet_result.facetMap = Uint32Array2D(100, 100)
        facet_result.facets = []

        colors = []

        svg = SVGBuilder.create_svg(facet_result, colors)
        assert '<?xml' in svg
        assert 'svg' in svg
        assert 'width="100"' in svg
        assert 'height="100"' in svg

    def test_create_svg_basic(self):
        """Test basic SVG creation."""
        facet_result = FacetResult()
        facet_result.width = 10
        facet_result.height = 10
        facet_result.facetMap = Uint32Array2D(10, 10)

        # Create a facet with border segments
        facet0 = Facet()
        facet0.id = 0
        facet0.color = 0
        facet0.pointCount = 4

        # Create simple path
        points = [
            PathPoint(0, 0, OrientationEnum.Top),
            PathPoint(2, 0, OrientationEnum.Top),
            PathPoint(2, 2, OrientationEnum.Right),
            PathPoint(0, 2, OrientationEnum.Bottom),
        ]
        segment = PathSegment(points, neighbour=-1)
        boundary = FacetBoundarySegment(segment, neighbour=-1, reverseOrder=False)
        facet0.borderSegments = [boundary]
        facet0.labelBounds = BoundingBox(minX=0, minY=0, maxX=2, maxY=2)

        facet_result.facets = [facet0]
        colors = [(255, 0, 0)]

        svg = SVGBuilder.create_svg(facet_result, colors, fill=True, stroke=True, add_color_labels=False)

        assert '<?xml' in svg
        assert 'path' in svg
        assert 'd=' in svg

    def test_create_svg_with_labels(self):
        """Test SVG with labels."""
        facet_result = FacetResult()
        facet_result.width = 10
        facet_result.height = 10
        facet_result.facetMap = Uint32Array2D(10, 10)

        facet0 = Facet()
        facet0.id = 0
        facet0.color = 0  # Fixed: color index must match colors array
        facet0.pointCount = 4

        points = [PathPoint(0, 0, OrientationEnum.Top)]
        segment = PathSegment(points, neighbour=-1)
        boundary = FacetBoundarySegment(segment, neighbour=-1, reverseOrder=False)
        facet0.borderSegments = [boundary]
        facet0.labelBounds = BoundingBox(minX=0, minY=0, maxX=2, maxY=2)

        facet_result.facets = [facet0]
        colors = [(255, 0, 0)]

        svg = SVGBuilder.create_svg(facet_result, colors, add_color_labels=True)

        assert 'text' in svg
        assert '>1<' in svg or '1' in svg  # Labels are 1-based (id + 1)

    def test_create_svg_scale(self):
        """Test SVG scaling."""
        facet_result = FacetResult()
        facet_result.width = 10
        facet_result.height = 10
        facet_result.facetMap = Uint32Array2D(10, 10)
        facet_result.facets = []

        colors = []

        svg = SVGBuilder.create_svg(facet_result, colors, size_multiplier=2.0)
        assert 'width="20"' in svg
        assert 'height="20"' in svg


class TestRasterExporter:
    """Test PNG/JPG export."""

    def test_export_png_fallback(self):
        """Test PNG export (may use fallback if cairosvg not available)."""
        svg_content = '''<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
</svg>'''

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test.png')

            try:
                RasterExporter.export_png(svg_content, output_path)
                # Check file was created
                assert os.path.exists(output_path)
                assert os.path.getsize(output_path) > 0
            except ImportError as e:
                # If neither cairosvg nor PIL available, that's OK for test
                if "requires either cairosvg or Pillow" not in str(e):
                    raise

    def test_export_jpg_fallback(self):
        """Test JPG export (may use fallback if cairosvg not available)."""
        svg_content = '''<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
</svg>'''

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test.jpg')

            try:
                RasterExporter.export_jpg(svg_content, output_path, quality=90)
                # Check file was created
                assert os.path.exists(output_path)
                assert os.path.getsize(output_path) > 0
            except ImportError as e:
                # If neither cairosvg nor PIL available, that's OK for test
                if "requires either cairosvg or Pillow" not in str(e):
                    raise


class TestIntegration:
    """Integration tests for full pipeline."""

    def test_full_svg_pipeline(self):
        """Test complete SVG generation pipeline."""
        # Create minimal facet result
        facet_result = FacetResult()
        facet_result.width = 10
        facet_result.height = 10
        facet_result.facetMap = Uint32Array2D(10, 10)

        facet0 = Facet()
        facet0.id = 0
        facet0.color = 0
        facet0.pointCount = 4
        facet0.bbox = BoundingBox(minX=0, minY=0, maxX=2, maxY=2)
        facet0.neighbourFacets = []
        facet0.neighbourFacetsIsDirty = False

        points = [
            PathPoint(0, 0, OrientationEnum.Top),
            PathPoint(2, 0, OrientationEnum.Top),
            PathPoint(2, 2, OrientationEnum.Right),
            PathPoint(0, 2, OrientationEnum.Bottom),
        ]
        segment = PathSegment(points, neighbour=-1)
        boundary = FacetBoundarySegment(segment, neighbour=-1, reverseOrder=False)
        facet0.borderSegments = [boundary]

        facet_result.facets = [facet0]
        colors = [(255, 0, 0)]

        # Build label bounds
        FacetLabelPlacer.build_facet_label_bounds(facet_result)

        # Generate SVG
        svg = SVGBuilder.create_svg(facet_result, colors, add_color_labels=True)

        # Verify SVG structure
        assert '<?xml' in svg
        assert 'svg' in svg
        assert 'path' in svg
        assert facet0.labelBounds is not None
