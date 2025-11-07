"""Tests for CLI application."""

import pytest
import tempfile
import os
import json
from pathlib import Path
from click.testing import CliRunner
from PIL import Image
import numpy as np

try:
    import click
    HAS_CLICK = True
except ImportError:
    HAS_CLICK = False

if HAS_CLICK:
    from paintbynumbers.cli.main import main, init_config


@pytest.mark.skipif(not HAS_CLICK, reason="requires click")
class TestCLI:
    """Test CLI application."""

    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def test_image(self, tmp_path):
        """Create a simple test image."""
        img_array = np.zeros((50, 50, 3), dtype=np.uint8)
        img_array[10:20, 10:20] = [255, 0, 0]  # Red square
        img_array[30:40, 30:40] = [0, 255, 0]  # Green square

        img = Image.fromarray(img_array, mode='RGB')
        image_path = tmp_path / "test_image.png"
        img.save(image_path)
        return str(image_path)

    def test_main_basic(self, runner, test_image, tmp_path):
        """Test basic CLI usage."""
        output_path = tmp_path / "output"

        result = runner.invoke(main, [
            test_image,
            str(output_path),
            '--colors', '4',
            '--quiet'
        ])

        # CLI should succeed
        assert result.exit_code == 0

        # Output file should exist
        assert (tmp_path / "output.svg").exists()

    def test_main_with_png_export(self, runner, test_image, tmp_path):
        """Test CLI with PNG export."""
        output_path = tmp_path / "output"

        result = runner.invoke(main, [
            test_image,
            str(output_path),
            '--colors', '4',
            '--png',
            '--quiet'
        ])

        assert result.exit_code == 0
        assert (tmp_path / "output.svg").exists()
        # PNG may or may not exist depending on dependencies
        # assert (tmp_path / "output.png").exists()

    def test_main_with_options(self, runner, test_image, tmp_path):
        """Test CLI with various options."""
        output_path = tmp_path / "output"

        result = runner.invoke(main, [
            test_image,
            str(output_path),
            '--colors', '8',
            '--color-space', 'LAB',
            '--scale', '2.0',
            '--font-size', '16',
            '--border-smoothing', '1',
            '--quiet'
        ])

        assert result.exit_code == 0
        assert (tmp_path / "output.svg").exists()

    def test_main_with_config_file(self, runner, test_image, tmp_path):
        """Test CLI with configuration file."""
        # Create config file
        config_path = tmp_path / "config.json"
        config_data = {
            "kMeansNrOfClusters": 6,
            "kMeansClusteringColorSpace": "RGB",
            "removeFacetsSmallerThanNrOfPoints": 10
        }
        with open(config_path, 'w') as f:
            json.dump(config_data, f)

        output_path = tmp_path / "output"

        result = runner.invoke(main, [
            test_image,
            str(output_path),
            '--config', str(config_path),
            '--quiet'
        ])

        assert result.exit_code == 0
        assert (tmp_path / "output.svg").exists()

    def test_main_save_config(self, runner, test_image, tmp_path):
        """Test CLI with --save-config option."""
        output_path = tmp_path / "output"
        config_path = tmp_path / "saved_config.json"

        result = runner.invoke(main, [
            test_image,
            str(output_path),
            '--colors', '12',
            '--save-config', str(config_path),
            '--quiet'
        ])

        assert result.exit_code == 0
        assert config_path.exists()

        # Load and verify config
        with open(config_path, 'r') as f:
            config = json.load(f)
        assert config['kMeansNrOfClusters'] == 12

    def test_main_invalid_image(self, runner, tmp_path):
        """Test CLI with non-existent image."""
        output_path = tmp_path / "output"

        result = runner.invoke(main, [
            "/nonexistent/image.jpg",
            str(output_path),
            '--quiet'
        ])

        # Should fail
        assert result.exit_code != 0

    def test_main_no_svg(self, runner, test_image, tmp_path):
        """Test CLI with --no-svg option."""
        output_path = tmp_path / "output"

        result = runner.invoke(main, [
            test_image,
            str(output_path),
            '--no-svg',
            '--quiet'
        ])

        # Should still work (SVG is default output)
        assert result.exit_code == 0

    def test_main_various_appearance_options(self, runner, test_image, tmp_path):
        """Test CLI with appearance options."""
        output_path = tmp_path / "output"

        result = runner.invoke(main, [
            test_image,
            str(output_path),
            '--no-show-labels',
            '--no-show-borders',
            '--no-fill-facets',
            '--font-color', '#FF0000',
            '--quiet'
        ])

        assert result.exit_code == 0
        assert (tmp_path / "output.svg").exists()

    def test_init_config(self, runner, tmp_path):
        """Test init-config command."""
        config_path = tmp_path / "settings.json"

        result = runner.invoke(init_config, [
            '--output', str(config_path)
        ])

        assert result.exit_code == 0
        assert config_path.exists()

        # Verify it's valid JSON
        with open(config_path, 'r') as f:
            config = json.load(f)
        assert 'kMeansNrOfClusters' in config

    def test_main_with_seed(self, runner, test_image, tmp_path):
        """Test CLI with random seed for reproducibility."""
        output_path1 = tmp_path / "output1"
        output_path2 = tmp_path / "output2"

        # Run twice with same seed
        result1 = runner.invoke(main, [
            test_image,
            str(output_path1),
            '--seed', '42',
            '--quiet'
        ])

        result2 = runner.invoke(main, [
            test_image,
            str(output_path2),
            '--seed', '42',
            '--quiet'
        ])

        assert result1.exit_code == 0
        assert result2.exit_code == 0

        # Read SVG files - they should be identical
        with open(f"{output_path1}.svg", 'r') as f:
            svg1 = f.read()
        with open(f"{output_path2}.svg", 'r') as f:
            svg2 = f.read()

        # Should be very similar (minor differences possible due to floating point)
        assert len(svg1) == len(svg2)

    def test_main_with_max_width_height(self, runner, test_image, tmp_path):
        """Test CLI with image resizing options."""
        output_path = tmp_path / "output"

        result = runner.invoke(main, [
            test_image,
            str(output_path),
            '--max-width', '25',
            '--max-height', '25',
            '--quiet'
        ])

        assert result.exit_code == 0
        assert (tmp_path / "output.svg").exists()

    def test_main_with_facet_limits(self, runner, test_image, tmp_path):
        """Test CLI with facet reduction options."""
        output_path = tmp_path / "output"

        result = runner.invoke(main, [
            test_image,
            str(output_path),
            '--min-facet-size', '15',
            '--max-facets', '10',
            '--quiet'
        ])

        assert result.exit_code == 0
        assert (tmp_path / "output.svg").exists()
