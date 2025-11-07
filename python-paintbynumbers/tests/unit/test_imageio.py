"""Tests for image I/O utilities."""

import pytest
import tempfile
import os
import numpy as np
from PIL import Image

try:
    from paintbynumbers.utils.imageio import (
        load_image,
        image_to_array,
        array_to_image,
        get_image_info
    )
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


@pytest.mark.skipif(not HAS_PIL, reason="requires PIL/Pillow")
class TestImageIO:
    """Test image I/O functions."""

    @pytest.fixture
    def test_image_path(self, tmp_path):
        """Create a test image file."""
        img_array = np.zeros((100, 100, 3), dtype=np.uint8)
        img_array[20:40, 20:40] = [255, 0, 0]  # Red square
        img_array[60:80, 60:80] = [0, 255, 0]  # Green square

        img = Image.fromarray(img_array, mode='RGB')
        image_path = tmp_path / "test.png"
        img.save(image_path)
        return str(image_path)

    @pytest.fixture
    def large_image_path(self, tmp_path):
        """Create a large test image."""
        img_array = np.random.randint(0, 256, (2000, 2000, 3), dtype=np.uint8)

        img = Image.fromarray(img_array, mode='RGB')
        image_path = tmp_path / "large.png"
        img.save(image_path)
        return str(image_path)

    @pytest.fixture
    def grayscale_image_path(self, tmp_path):
        """Create a grayscale test image."""
        img_array = np.random.randint(0, 256, (100, 100), dtype=np.uint8)

        img = Image.fromarray(img_array, mode='L')
        image_path = tmp_path / "gray.png"
        img.save(image_path)
        return str(image_path)

    @pytest.fixture
    def rgba_image_path(self, tmp_path):
        """Create an RGBA test image."""
        img_array = np.random.randint(0, 256, (100, 100, 4), dtype=np.uint8)

        img = Image.fromarray(img_array, mode='RGBA')
        image_path = tmp_path / "rgba.png"
        img.save(image_path)
        return str(image_path)

    def test_load_image_basic(self, test_image_path):
        """Test basic image loading."""
        img_data, width, height = load_image(test_image_path)

        assert img_data.shape == (100, 100, 3)
        assert width == 100
        assert height == 100
        assert img_data.dtype == np.uint8

    def test_load_image_with_resize(self, large_image_path):
        """Test image loading with resizing."""
        img_data, width, height = load_image(
            large_image_path,
            max_width=500,
            max_height=500
        )

        # Should be resized to fit within 500x500
        assert width <= 500
        assert height <= 500
        assert img_data.shape[0] == height
        assert img_data.shape[1] == width

    def test_load_image_grayscale_converts_to_rgb(self, grayscale_image_path):
        """Test that grayscale images are converted to RGB."""
        img_data, width, height = load_image(grayscale_image_path)

        # Should have 3 channels even though input was grayscale
        assert img_data.shape == (100, 100, 3)
        assert img_data.dtype == np.uint8

    def test_load_image_rgba_converts_to_rgb(self, rgba_image_path):
        """Test that RGBA images are converted to RGB."""
        img_data, width, height = load_image(rgba_image_path)

        # Should have 3 channels (alpha removed)
        assert img_data.shape == (100, 100, 3)
        assert img_data.dtype == np.uint8

    def test_load_image_nonexistent_raises_error(self):
        """Test that loading non-existent file raises error."""
        with pytest.raises(Exception):  # FileNotFoundError or similar
            load_image("/nonexistent/file.png")

    def test_image_to_array(self):
        """Test PIL Image to numpy array conversion."""
        # Create a PIL Image
        img_array = np.array([[[255, 0, 0], [0, 255, 0]],
                              [[0, 0, 255], [255, 255, 0]]], dtype=np.uint8)
        img = Image.fromarray(img_array, mode='RGB')

        # Convert to array
        result = image_to_array(img)

        assert result.shape == (2, 2, 3)
        assert result.dtype == np.uint8
        np.testing.assert_array_equal(result, img_array)

    def test_array_to_image(self):
        """Test numpy array to PIL Image conversion."""
        # Create array
        img_array = np.array([[[255, 0, 0], [0, 255, 0]],
                              [[0, 0, 255], [255, 255, 0]]], dtype=np.uint8)

        # Convert to image
        img = array_to_image(img_array)

        assert img.mode == 'RGB'
        assert img.size == (2, 2)  # PIL uses (width, height)

        # Convert back to verify
        result = np.array(img)
        np.testing.assert_array_equal(result, img_array)

    def test_get_image_info(self, test_image_path):
        """Test getting image information."""
        info = get_image_info(test_image_path)

        assert info['width'] == 100
        assert info['height'] == 100
        assert info['mode'] == 'RGB'
        assert info['format'] in ['PNG', 'JPEG', None]  # Varies by implementation

    def test_round_trip_conversion(self):
        """Test round-trip array -> image -> array."""
        # Create array
        original = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)

        # Convert to image and back
        img = array_to_image(original)
        result = image_to_array(img)

        # Should be identical
        np.testing.assert_array_equal(result, original)

    def test_load_image_preserves_colors(self, test_image_path):
        """Test that image loading preserves color values."""
        img_data, width, height = load_image(test_image_path)

        # Check red square
        red_pixel = img_data[30, 30]  # In the red square
        assert red_pixel[0] == 255  # R
        assert red_pixel[1] == 0    # G
        assert red_pixel[2] == 0    # B

        # Check green square
        green_pixel = img_data[70, 70]  # In the green square
        assert green_pixel[0] == 0    # R
        assert green_pixel[1] == 255  # G
        assert green_pixel[2] == 0    # B

    def test_load_image_aspect_ratio_preserved(self, tmp_path):
        """Test that aspect ratio is preserved when resizing."""
        # Create a 200x100 image (2:1 aspect ratio)
        img_array = np.random.randint(0, 256, (100, 200, 3), dtype=np.uint8)
        img = Image.fromarray(img_array, mode='RGB')
        image_path = tmp_path / "rect.png"
        img.save(image_path)

        # Load with max dimensions
        img_data, width, height = load_image(
            str(image_path),
            max_width=100,
            max_height=100
        )

        # Should maintain 2:1 aspect ratio, so width should be 100 and height 50
        assert width == 100
        assert height == 50

    def test_load_jpeg_image(self, tmp_path):
        """Test loading JPEG images."""
        # Create a JPEG image
        img_array = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        img = Image.fromarray(img_array, mode='RGB')
        image_path = tmp_path / "test.jpg"
        img.save(image_path, 'JPEG')

        # Load it
        img_data, width, height = load_image(str(image_path))

        assert img_data.shape == (100, 100, 3)
        assert width == 100
        assert height == 100
