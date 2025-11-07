"""Pytest configuration and shared fixtures for Paint by Numbers Generator tests."""

import pytest
from pathlib import Path
from typing import Generator
import numpy as np
from PIL import Image


@pytest.fixture
def test_data_dir() -> Path:
    """Return path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create and return a temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir(exist_ok=True)
    yield output_dir


@pytest.fixture
def simple_test_image() -> np.ndarray:
    """Create a simple test image with a few colors."""
    # Create a 10x10 image with 3 colors
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    img[0:5, :] = [255, 0, 0]      # Top half red
    img[5:8, :] = [0, 255, 0]      # Middle green
    img[8:10, :] = [0, 0, 255]     # Bottom blue
    return img


@pytest.fixture
def simple_pil_image(simple_test_image: np.ndarray) -> Image.Image:
    """Create a simple PIL test image."""
    return Image.fromarray(simple_test_image, mode="RGB")


@pytest.fixture
def checkerboard_image() -> np.ndarray:
    """Create a checkerboard pattern image."""
    img = np.zeros((20, 20, 3), dtype=np.uint8)
    # Create 2x2 pixel checkerboard
    for i in range(0, 20, 4):
        for j in range(0, 20, 4):
            img[i:i+2, j:j+2] = [255, 255, 255]
            img[i+2:i+4, j+2:j+4] = [255, 255, 255]
    return img


@pytest.fixture
def gradient_image() -> np.ndarray:
    """Create a gradient image."""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    for i in range(100):
        img[i, :] = [int(i * 2.55), int(i * 2.55), int(i * 2.55)]
    return img


# Pytest configuration
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "comparison: mark test as comparison with TypeScript")
    config.addinivalue_line("markers", "benchmark: mark test as benchmark")
