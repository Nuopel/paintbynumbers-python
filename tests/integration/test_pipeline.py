"""Integration tests for the complete processing pipeline."""

import pytest
import tempfile
import os
from pathlib import Path
import numpy as np
from PIL import Image

from paintbynumbers.core.pipeline import PaintByNumbersPipeline, PipelineResult
from paintbynumbers.core.settings import Settings, ClusteringColorSpace, OutputProfile


@pytest.fixture
def test_image_path(tmp_path):
    """Create a simple test image."""
    # Create a simple 100x100 test image with a few distinct colors
    img_array = np.zeros((100, 100, 3), dtype=np.uint8)

    # Red square
    img_array[10:40, 10:40] = [255, 0, 0]

    # Green square
    img_array[10:40, 60:90] = [0, 255, 0]

    # Blue square
    img_array[60:90, 10:40] = [0, 0, 255]

    # Yellow square
    img_array[60:90, 60:90] = [255, 255, 0]

    # White center
    img_array[40:60, 40:60] = [255, 255, 255]

    # Save as PNG
    img = Image.fromarray(img_array, mode='RGB')
    image_path = tmp_path / "test_image.png"
    img.save(image_path)

    return str(image_path)


@pytest.fixture
def basic_settings():
    """Create basic settings for testing."""
    settings = Settings()
    settings.kMeansNrOfClusters = 8  # Small number for testing
    settings.removeFacetsSmallerThanNrOfPoints = 5
    settings.narrowPixelStripCleanupRuns = 1
    settings.nrOfTimesToHalveBorderSegments = 1
    settings.resizeImageIfTooLarge = False  # Don't resize test image
    return settings


class TestPipelineIntegration:
    """Integration tests for complete pipeline."""

    def test_process_basic(self, test_image_path, basic_settings):
        """Test basic pipeline processing."""
        result = PaintByNumbersPipeline.process(
            input_path=test_image_path,
            settings=basic_settings
        )

        # Check result structure
        assert isinstance(result, PipelineResult)
        assert result.facet_result is not None
        assert len(result.colors_by_index) > 0
        assert result.svg_content is not None
        assert len(result.svg_content) > 0
        assert result.width == 100
        assert result.height == 100

        # Check that we have facets
        facet_count = len([f for f in result.facet_result.facets if f is not None])
        assert facet_count > 0

        # Check that colors are RGB tuples
        for color in result.colors_by_index:
            assert len(color) == 3
            assert all(0 <= c <= 255 for c in color)

        # Check SVG content
        assert '<svg' in result.svg_content
        assert '</svg>' in result.svg_content

    def test_process_and_save_svg(self, test_image_path, basic_settings, tmp_path):
        """Test pipeline with SVG output."""
        output_path = tmp_path / "output"

        PaintByNumbersPipeline.process_and_save(
            input_path=test_image_path,
            output_path=str(output_path),
            settings=basic_settings,
            export_png=False,
            export_jpg=False
        )

        # Check that SVG was created
        svg_path = Path(f"{output_path}.svg")
        assert svg_path.exists()
        assert svg_path.stat().st_size > 0

        # Read and validate SVG content
        svg_content = svg_path.read_text()
        assert '<svg' in svg_content
        assert '</svg>' in svg_content

    def test_process_and_save_all_formats(self, test_image_path, basic_settings, tmp_path):
        """Test pipeline with all output formats."""
        output_path = tmp_path / "output_all"

        # Note: PNG/JPG export may fail if cairosvg/PIL is not available
        # We'll handle that gracefully
        try:
            PaintByNumbersPipeline.process_and_save(
                input_path=test_image_path,
                output_path=str(output_path),
                settings=basic_settings,
                export_png=True,
                export_jpg=True
            )

            # Check that SVG was created
            svg_path = Path(f"{output_path}.svg")
            assert svg_path.exists()

            # PNG and JPG may or may not exist depending on dependencies
            # We'll just check if they were created when possible
            png_path = Path(f"{output_path}.png")
            jpg_path = Path(f"{output_path}.jpg")

            if png_path.exists():
                assert png_path.stat().st_size > 0

            if jpg_path.exists():
                assert jpg_path.stat().st_size > 0

        except ImportError:
            # If cairosvg/PIL not available, just test SVG
            pytest.skip("PNG/JPG export not available")

    def test_process_with_progress_callback(self, test_image_path, basic_settings):
        """Test pipeline with progress callback."""
        progress_updates = []

        def progress_callback(stage: str, progress: float):
            progress_updates.append((stage, progress))

        result = PaintByNumbersPipeline.process(
            input_path=test_image_path,
            settings=basic_settings,
            progress_callback=progress_callback
        )

        # Check that progress was reported
        assert len(progress_updates) > 0

        # Check that we got updates from multiple stages
        stages = set(stage for stage, _ in progress_updates)
        assert len(stages) > 3  # Should have at least several stages

        # Check that progress values are reasonable
        for stage, progress in progress_updates:
            assert 0.0 <= progress <= 1.0

    def test_process_different_color_spaces(self, test_image_path, basic_settings):
        """Test processing with different color spaces."""
        for color_space in [ClusteringColorSpace.RGB,
                           ClusteringColorSpace.HSL,
                           ClusteringColorSpace.LAB]:
            settings = basic_settings
            settings.kMeansClusteringColorSpace = color_space

            result = PaintByNumbersPipeline.process(
                input_path=test_image_path,
                settings=settings
            )

            assert isinstance(result, PipelineResult)
            assert len(result.colors_by_index) > 0

    def test_process_with_custom_output_profile(self, test_image_path, basic_settings):
        """Test processing with custom output profile."""
        profile = OutputProfile(
            name="test_profile",
            svgShowLabels=True,
            svgShowBorders=True,
            svgFillFacets=False,
            svgSizeMultiplier=2.0,
            svgFontSize=24,
            svgFontColor="#FF0000"
        )
        basic_settings.outputProfiles = [profile]

        result = PaintByNumbersPipeline.process(
            input_path=test_image_path,
            settings=basic_settings
        )

        # Check SVG was generated
        assert result.svg_content is not None
        assert len(result.svg_content) > 0

    def test_process_with_facet_reduction(self, test_image_path, basic_settings):
        """Test processing with facet size and count limits."""
        basic_settings.removeFacetsSmallerThanNrOfPoints = 20
        basic_settings.maximumNumberOfFacets = 10

        result = PaintByNumbersPipeline.process(
            input_path=test_image_path,
            settings=basic_settings
        )

        # Check that facet reduction was applied
        facet_count = len([f for f in result.facet_result.facets if f is not None])
        assert facet_count <= 10

    def test_process_with_image_resize(self, test_image_path, basic_settings):
        """Test processing with image resizing."""
        basic_settings.resizeImageIfTooLarge = True
        basic_settings.resizeImageWidth = 50
        basic_settings.resizeImageHeight = 50

        result = PaintByNumbersPipeline.process(
            input_path=test_image_path,
            settings=basic_settings
        )

        # Image should be resized to 50x50
        assert result.width <= 50
        assert result.height <= 50

    def test_process_with_smoothing_settings(self, test_image_path, basic_settings):
        """Test processing with different smoothing settings."""
        # Test with no smoothing
        basic_settings.nrOfTimesToHalveBorderSegments = 0
        result1 = PaintByNumbersPipeline.process(
            input_path=test_image_path,
            settings=basic_settings
        )

        # Test with more smoothing
        basic_settings.nrOfTimesToHalveBorderSegments = 3
        result2 = PaintByNumbersPipeline.process(
            input_path=test_image_path,
            settings=basic_settings
        )

        # Both should succeed
        assert result1.svg_content is not None
        assert result2.svg_content is not None

    def test_process_nonexistent_file(self, basic_settings):
        """Test processing with nonexistent file."""
        with pytest.raises(Exception):  # Could be FileNotFoundError or IOError
            PaintByNumbersPipeline.process(
                input_path="/nonexistent/file.jpg",
                settings=basic_settings
            )

    def test_settings_to_json_and_back(self, basic_settings):
        """Test settings serialization."""
        # Convert to JSON
        json_data = basic_settings.to_json()
        assert isinstance(json_data, dict)

        # Convert back
        settings2 = Settings.from_json(json_data)
        assert settings2.kMeansNrOfClusters == basic_settings.kMeansNrOfClusters
        assert settings2.removeFacetsSmallerThanNrOfPoints == basic_settings.removeFacetsSmallerThanNrOfPoints
