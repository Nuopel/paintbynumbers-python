"""Tests for TypedArray wrapper classes."""

import pytest
from paintbynumbers.structs.typed_arrays import (
    Uint32Array2D,
    Uint8Array2D,
    BooleanArray2D,
)


class TestUint32Array2D:
    """Test Uint32Array2D class."""

    def test_create_array(self) -> None:
        """Test creating a Uint32Array2D."""
        arr = Uint32Array2D(10, 20)
        assert arr.width == 10
        assert arr.height == 20
        assert arr.shape == (10, 20)

    def test_default_values_zero(self) -> None:
        """Test that default values are zero."""
        arr = Uint32Array2D(5, 5)
        for y in range(5):
            for x in range(5):
                assert arr.get(x, y) == 0

    def test_set_and_get(self) -> None:
        """Test setting and getting values."""
        arr = Uint32Array2D(10, 10)

        arr.set(5, 3, 42)
        assert arr.get(5, 3) == 42

        arr.set(0, 0, 100)
        assert arr.get(0, 0) == 100

        arr.set(9, 9, 999)
        assert arr.get(9, 9) == 999

    def test_large_values(self) -> None:
        """Test storing large uint32 values."""
        arr = Uint32Array2D(5, 5)

        # Max uint32 value
        max_val = 2**32 - 1
        arr.set(2, 2, max_val)
        assert arr.get(2, 2) == max_val

    def test_multiple_values(self) -> None:
        """Test setting multiple values."""
        arr = Uint32Array2D(3, 3)

        values = [
            (0, 0, 1),
            (1, 0, 2),
            (2, 0, 3),
            (0, 1, 4),
            (1, 1, 5),
            (2, 1, 6),
        ]

        for x, y, val in values:
            arr.set(x, y, val)

        for x, y, expected in values:
            assert arr.get(x, y) == expected

    def test_repr(self) -> None:
        """Test string representation."""
        arr = Uint32Array2D(10, 20)
        assert repr(arr) == "Uint32Array2D(width=10, height=20)"


class TestUint8Array2D:
    """Test Uint8Array2D class."""

    def test_create_array(self) -> None:
        """Test creating a Uint8Array2D."""
        arr = Uint8Array2D(10, 20)
        assert arr.width == 10
        assert arr.height == 20
        assert arr.shape == (10, 20)

    def test_default_values_zero(self) -> None:
        """Test that default values are zero."""
        arr = Uint8Array2D(5, 5)
        for y in range(5):
            for x in range(5):
                assert arr.get(x, y) == 0

    def test_set_and_get(self) -> None:
        """Test setting and getting values."""
        arr = Uint8Array2D(10, 10)

        arr.set(5, 3, 42)
        assert arr.get(5, 3) == 42

        arr.set(0, 0, 100)
        assert arr.get(0, 0) == 100

        arr.set(9, 9, 255)
        assert arr.get(9, 9) == 255

    def test_uint8_range(self) -> None:
        """Test uint8 value range (0-255)."""
        arr = Uint8Array2D(5, 5)

        arr.set(0, 0, 0)
        assert arr.get(0, 0) == 0

        arr.set(1, 1, 255)
        assert arr.get(1, 1) == 255

    def test_match_all_around_true(self) -> None:
        """Test match_all_around when all neighbors match."""
        arr = Uint8Array2D(5, 5)

        # Fill with value 10
        for y in range(5):
            for x in range(5):
                arr.set(x, y, 10)

        # Center point should match all around
        assert arr.match_all_around(2, 2, 10)

    def test_match_all_around_false(self) -> None:
        """Test match_all_around when neighbors don't match."""
        arr = Uint8Array2D(5, 5)

        # Fill with value 10
        for y in range(5):
            for x in range(5):
                arr.set(x, y, 10)

        # Change one neighbor
        arr.set(2, 1, 20)  # Top of (2, 2)

        # Should not match
        assert not arr.match_all_around(2, 2, 10)

    def test_match_all_around_edge_cases(self) -> None:
        """Test match_all_around at edges and corners."""
        arr = Uint8Array2D(5, 5)

        # Fill with value 10
        for y in range(5):
            for x in range(5):
                arr.set(x, y, 10)

        # Corner (0, 0) - missing left and top neighbors
        assert not arr.match_all_around(0, 0, 10)

        # Edge (0, 2) - missing left neighbor
        assert not arr.match_all_around(0, 2, 10)

        # Edge (2, 0) - missing top neighbor
        assert not arr.match_all_around(2, 0, 10)

    def test_match_all_around_pattern(self) -> None:
        """Test match_all_around with specific pattern."""
        arr = Uint8Array2D(5, 5)

        # Create a cross pattern with value 1
        arr.set(2, 2, 1)  # Center
        arr.set(1, 2, 1)  # Left
        arr.set(3, 2, 1)  # Right
        arr.set(2, 1, 1)  # Top
        arr.set(2, 3, 1)  # Bottom

        # Center should match all around
        assert arr.match_all_around(2, 2, 1)

        # Change one neighbor to different value
        arr.set(1, 2, 2)  # Change left neighbor
        # Now not all neighbors match
        assert not arr.match_all_around(2, 2, 1)

    def test_repr(self) -> None:
        """Test string representation."""
        arr = Uint8Array2D(10, 20)
        assert repr(arr) == "Uint8Array2D(width=10, height=20)"


class TestBooleanArray2D:
    """Test BooleanArray2D class."""

    def test_create_array(self) -> None:
        """Test creating a BooleanArray2D."""
        arr = BooleanArray2D(10, 20)
        assert arr.width == 10
        assert arr.height == 20
        assert arr.shape == (10, 20)

    def test_default_values_false(self) -> None:
        """Test that default values are False."""
        arr = BooleanArray2D(5, 5)
        for y in range(5):
            for x in range(5):
                assert arr.get(x, y) == False

    def test_set_and_get_true(self) -> None:
        """Test setting and getting True values."""
        arr = BooleanArray2D(10, 10)

        arr.set(5, 3, True)
        assert arr.get(5, 3) == True

        arr.set(0, 0, True)
        assert arr.get(0, 0) == True

    def test_set_and_get_false(self) -> None:
        """Test setting and getting False values."""
        arr = BooleanArray2D(10, 10)

        # Set to True first
        arr.set(5, 3, True)
        assert arr.get(5, 3) == True

        # Set to False
        arr.set(5, 3, False)
        assert arr.get(5, 3) == False

    def test_boolean_pattern(self) -> None:
        """Test setting a boolean pattern."""
        arr = BooleanArray2D(4, 4)

        # Set checkerboard pattern
        for y in range(4):
            for x in range(4):
                arr.set(x, y, (x + y) % 2 == 0)

        # Verify pattern
        assert arr.get(0, 0) == True
        assert arr.get(1, 0) == False
        assert arr.get(0, 1) == False
        assert arr.get(1, 1) == True

    def test_multiple_toggle(self) -> None:
        """Test toggling values multiple times."""
        arr = BooleanArray2D(5, 5)

        arr.set(2, 2, True)
        assert arr.get(2, 2) == True

        arr.set(2, 2, False)
        assert arr.get(2, 2) == False

        arr.set(2, 2, True)
        assert arr.get(2, 2) == True

    def test_repr(self) -> None:
        """Test string representation."""
        arr = BooleanArray2D(10, 20)
        assert repr(arr) == "BooleanArray2D(width=10, height=20)"


class TestArrayIndexing:
    """Test array indexing consistency across all types."""

    def test_row_major_order(self) -> None:
        """Test that all arrays use row-major order (y * width + x)."""
        width, height = 3, 3

        arr32 = Uint32Array2D(width, height)
        arr8 = Uint8Array2D(width, height)
        arr_bool = BooleanArray2D(width, height)

        # Set diagonal values
        for i in range(3):
            arr32.set(i, i, i + 1)
            arr8.set(i, i, i + 1)
            arr_bool.set(i, i, True)

        # Verify diagonal
        for i in range(3):
            assert arr32.get(i, i) == i + 1
            assert arr8.get(i, i) == i + 1
            assert arr_bool.get(i, i) == True

        # Verify non-diagonal are default
        assert arr32.get(0, 1) == 0
        assert arr8.get(0, 1) == 0
        assert arr_bool.get(0, 1) == False
