"""Tests for random number generator."""

import pytest
from paintbynumbers.utils.random import Random


class TestRandom:
    """Test Random class."""

    def test_create_with_seed(self) -> None:
        """Test creating random with specific seed."""
        rng = Random(seed=42)
        assert rng.seed == 42

    def test_create_without_seed(self) -> None:
        """Test creating random without seed uses timestamp."""
        rng = Random()
        assert rng.seed > 0

    def test_next_deterministic(self) -> None:
        """Test that same seed produces same sequence."""
        rng1 = Random(seed=42)
        rng2 = Random(seed=42)

        # First 10 values should match
        for _ in range(10):
            assert rng1.next() == rng2.next()

    def test_next_in_range(self) -> None:
        """Test that next() returns values in [0, 1)."""
        rng = Random(seed=42)

        for _ in range(100):
            val = rng.next()
            assert 0.0 <= val < 1.0

    def test_next_increments_seed(self) -> None:
        """Test that next() increments the seed."""
        rng = Random(seed=42)
        initial_seed = rng.seed

        rng.next()
        assert rng.seed == initial_seed + 1

        rng.next()
        assert rng.seed == initial_seed + 2

    def test_next_different_seeds(self) -> None:
        """Test that different seeds produce different sequences."""
        rng1 = Random(seed=42)
        rng2 = Random(seed=100)

        # Should produce different sequences
        sequence1 = [rng1.next() for _ in range(10)]
        sequence2 = [rng2.next() for _ in range(10)]

        assert sequence1 != sequence2

    def test_randint_range(self) -> None:
        """Test randint produces values in specified range."""
        rng = Random(seed=42)

        for _ in range(100):
            val = rng.randint(0, 10)
            assert 0 <= val <= 10
            assert isinstance(val, int)

    def test_randint_single_value(self) -> None:
        """Test randint with min == max."""
        rng = Random(seed=42)

        for _ in range(10):
            val = rng.randint(5, 5)
            assert val == 5

    def test_randint_deterministic(self) -> None:
        """Test randint is deterministic with same seed."""
        rng1 = Random(seed=42)
        rng2 = Random(seed=42)

        for _ in range(10):
            assert rng1.randint(0, 100) == rng2.randint(0, 100)

    def test_choice_from_list(self) -> None:
        """Test choice selects from list."""
        rng = Random(seed=42)
        items = ['a', 'b', 'c', 'd', 'e']

        for _ in range(20):
            choice = rng.choice(items)
            assert choice in items

    def test_choice_deterministic(self) -> None:
        """Test choice is deterministic."""
        rng1 = Random(seed=42)
        rng2 = Random(seed=42)
        items = [1, 2, 3, 4, 5]

        for _ in range(10):
            assert rng1.choice(items) == rng2.choice(items)

    def test_reproducible_sequence(self) -> None:
        """Test complete reproducibility of sequence."""
        # Generate sequence with seed 123
        rng = Random(seed=123)
        sequence1 = [rng.next() for _ in range(20)]

        # Generate again with same seed
        rng = Random(seed=123)
        sequence2 = [rng.next() for _ in range(20)]

        # Should be exactly the same
        for val1, val2 in zip(sequence1, sequence2):
            assert val1 == val2

    def test_long_sequence(self) -> None:
        """Test that long sequences remain deterministic."""
        rng1 = Random(seed=999)
        rng2 = Random(seed=999)

        # Test 1000 values
        for _ in range(1000):
            assert abs(rng1.next() - rng2.next()) < 1e-10
