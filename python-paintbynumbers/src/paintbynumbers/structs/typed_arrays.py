"""TypedArray wrappers for 2D arrays using NumPy.

These classes provide a TypeScript-like API for 2D arrays,
wrapping NumPy arrays with get/set methods that use (x, y) coordinates.
"""

from __future__ import annotations
import numpy as np
from numpy.typing import NDArray


class Uint32Array2D:
    """2D array of 32-bit unsigned integers.

    Wraps a NumPy uint32 array with row-major storage (y * width + x).

    Attributes:
        width: Width of the array
        height: Height of the array
    """

    def __init__(self, width: int, height: int) -> None:
        """Initialize a 2D uint32 array.

        Args:
            width: Width of the array
            height: Height of the array
        """
        self.width = width
        self.height = height
        self._arr: NDArray[np.uint32] = np.zeros(width * height, dtype=np.uint32)

    def get(self, x: int, y: int) -> int:
        """Get value at (x, y).

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Value at (x, y)
        """
        return int(self._arr[y * self.width + x])

    def set(self, x: int, y: int, value: int) -> None:
        """Set value at (x, y).

        Args:
            x: X coordinate
            y: Y coordinate
            value: Value to set
        """
        self._arr[y * self.width + x] = value

    @property
    def shape(self) -> tuple[int, int]:
        """Get shape as (width, height)."""
        return (self.width, self.height)

    def __repr__(self) -> str:
        """String representation."""
        return f"Uint32Array2D(width={self.width}, height={self.height})"


class Uint8Array2D:
    """2D array of 8-bit unsigned integers.

    Wraps a NumPy uint8 array with row-major storage (y * width + x).

    Attributes:
        width: Width of the array
        height: Height of the array
    """

    def __init__(self, width: int, height: int) -> None:
        """Initialize a 2D uint8 array.

        Args:
            width: Width of the array
            height: Height of the array
        """
        self.width = width
        self.height = height
        self._arr: NDArray[np.uint8] = np.zeros(width * height, dtype=np.uint8)

    def get(self, x: int, y: int) -> int:
        """Get value at (x, y).

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Value at (x, y)
        """
        return int(self._arr[y * self.width + x])

    def set(self, x: int, y: int, value: int) -> None:
        """Set value at (x, y).

        Args:
            x: X coordinate
            y: Y coordinate
            value: Value to set
        """
        self._arr[y * self.width + x] = value

    def match_all_around(self, x: int, y: int, value: int) -> bool:
        """Check if all 4 orthogonal neighbors match a value.

        This checks if the pixels to the left, top, right, and bottom
        all have the specified value.

        Args:
            x: X coordinate
            y: Y coordinate
            value: Value to match

        Returns:
            True if all 4 neighbors exist and match the value
        """
        idx = y * self.width + x

        # Check left neighbor
        if x - 1 < 0 or self._arr[idx - 1] != value:
            return False

        # Check top neighbor
        if y - 1 < 0 or self._arr[idx - self.width] != value:
            return False

        # Check right neighbor
        if x + 1 >= self.width or self._arr[idx + 1] != value:
            return False

        # Check bottom neighbor
        if y + 1 >= self.height or self._arr[idx + self.width] != value:
            return False

        return True

    @property
    def shape(self) -> tuple[int, int]:
        """Get shape as (width, height)."""
        return (self.width, self.height)

    def __repr__(self) -> str:
        """String representation."""
        return f"Uint8Array2D(width={self.width}, height={self.height})"


class BooleanArray2D:
    """2D array of booleans.

    Wraps a NumPy uint8 array (0 or 1) with row-major storage (y * width + x).
    Provides boolean get/set interface.

    Attributes:
        width: Width of the array
        height: Height of the array
    """

    def __init__(self, width: int, height: int) -> None:
        """Initialize a 2D boolean array.

        Args:
            width: Width of the array
            height: Height of the array
        """
        self.width = width
        self.height = height
        self._arr: NDArray[np.uint8] = np.zeros(width * height, dtype=np.uint8)

    def get(self, x: int, y: int) -> bool:
        """Get boolean value at (x, y).

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if non-zero, False if zero
        """
        return self._arr[y * self.width + x] != 0

    def set(self, x: int, y: int, value: bool) -> None:
        """Set boolean value at (x, y).

        Args:
            x: X coordinate
            y: Y coordinate
            value: Boolean value to set
        """
        self._arr[y * self.width + x] = 1 if value else 0

    @property
    def shape(self) -> tuple[int, int]:
        """Get shape as (width, height)."""
        return (self.width, self.height)

    def __repr__(self) -> str:
        """String representation."""
        return f"BooleanArray2D(width={self.width}, height={self.height})"
