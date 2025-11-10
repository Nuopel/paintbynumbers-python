"""Image I/O utilities for loading and saving images.

This module provides functions to load images from various formats,
convert them to NumPy arrays, and handle image resizing.
"""

from __future__ import annotations
from typing import Tuple, Optional
import numpy as np
from numpy.typing import NDArray

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def load_image(file_path: str, max_width: Optional[int] = None, max_height: Optional[int] = None) -> Tuple[NDArray[np.uint8], int, int]:
    """Load an image from a file and convert to RGB NumPy array.

    Args:
        file_path: Path to image file
        max_width: Maximum width (will resize if larger)
        max_height: Maximum height (will resize if larger)

    Returns:
        Tuple of (image_data, width, height)
        image_data: NumPy array of shape (height, width, 3) with RGB values

    Raises:
        ImportError: If PIL is not available
        FileNotFoundError: If file doesn't exist
        IOError: If file cannot be read

    Example:
        >>> img_data, width, height = load_image('photo.jpg', max_width=800)
        >>> print(img_data.shape)
        (600, 800, 3)
    """
    if not PIL_AVAILABLE:
        raise ImportError("PIL (Pillow) is required for image loading. Install with: pip install Pillow")

    # Load image
    img = Image.open(file_path)

    # Convert to RGB (handles RGBA, grayscale, etc.)
    img = img.convert('RGB')

    # Resize if necessary
    if max_width is not None or max_height is not None:
        width, height = img.size
        new_width, new_height = width, height

        if max_width is not None and width > max_width:
            new_width = max_width
            new_height = int(height * (max_width / width))

        if max_height is not None and new_height > max_height:
            new_height = max_height
            new_width = int(new_width * (max_height / new_height))

        if (new_width, new_height) != (width, height):
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Convert to NumPy array
    img_array = np.array(img, dtype=np.uint8)

    height, width = img_array.shape[:2]

    return img_array, width, height


def image_to_flat_array(img_array: NDArray[np.uint8]) -> NDArray[np.uint8]:
    """Convert image array to flat 1D array of RGB values.

    Args:
        img_array: NumPy array of shape (height, width, 3)

    Returns:
        Flat NumPy array of shape (height * width * 3,)

    Example:
        >>> img = np.zeros((100, 100, 3), dtype=np.uint8)
        >>> flat = image_to_flat_array(img)
        >>> flat.shape
        (30000,)
    """
    return img_array.flatten()


def flat_array_to_image(flat_array: NDArray[np.uint8], width: int, height: int) -> NDArray[np.uint8]:
    """Convert flat 1D array back to image array.

    Args:
        flat_array: Flat NumPy array of shape (height * width * 3,)
        width: Image width
        height: Image height

    Returns:
        NumPy array of shape (height, width, 3)

    Example:
        >>> flat = np.zeros(30000, dtype=np.uint8)
        >>> img = flat_array_to_image(flat, 100, 100)
        >>> img.shape
        (100, 100, 3)
    """
    return flat_array.reshape((height, width, 3))


def save_image(img_array: NDArray[np.uint8], file_path: str) -> None:
    """Save NumPy array as an image file.

    Args:
        img_array: NumPy array of shape (height, width, 3)
        file_path: Output file path

    Raises:
        ImportError: If PIL is not available
        IOError: If file cannot be written

    Example:
        >>> img = np.zeros((100, 100, 3), dtype=np.uint8)
        >>> save_image(img, 'output.png')
    """
    if not PIL_AVAILABLE:
        raise ImportError("PIL (Pillow) is required for image saving. Install with: pip install Pillow")

    img = Image.fromarray(img_array, mode='RGB')
    img.save(file_path)


def get_image_info(file_path: str) -> Tuple[int, int, str]:
    """Get basic information about an image file.

    Args:
        file_path: Path to image file

    Returns:
        Tuple of (width, height, format)

    Example:
        >>> width, height, fmt = get_image_info('photo.jpg')
        >>> print(f"{width}x{height} {fmt}")
        800x600 JPEG
    """
    if not PIL_AVAILABLE:
        raise ImportError("PIL (Pillow) is required. Install with: pip install Pillow")

    with Image.open(file_path) as img:
        return img.size[0], img.size[1], img.format or 'UNKNOWN'
