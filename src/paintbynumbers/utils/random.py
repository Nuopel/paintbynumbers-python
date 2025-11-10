"""Seeded random number generator for reproducible results.

This module provides a deterministic random number generator that produces
the same sequence of values given the same seed. This is critical for
ensuring reproducible output in the paint-by-numbers generation.
"""

import math
import time


class Random:
    """Seeded random number generator using sin-based algorithm.

    This implementation matches the TypeScript version exactly to ensure
    identical clustering results when using the same seed.

    Attributes:
        seed: Current seed value (incremented on each call)
    """

    def __init__(self, seed: int | None = None) -> None:
        """Initialize random generator with optional seed.

        Args:
            seed: Initial seed value. If None, uses current timestamp.
        """
        if seed is None:
            self.seed = int(time.time() * 1000)  # Milliseconds like JS
        else:
            self.seed = seed

    def next(self) -> float:
        """Generate next random number in range [0, 1).

        Returns:
            Random float in range [0, 1)
        """
        # Match TypeScript: Math.sin(seed++) * 10000
        x = math.sin(self.seed) * 10000
        self.seed += 1
        return x - math.floor(x)

    def randint(self, min_val: int, max_val: int) -> int:
        """Generate random integer in range [min_val, max_val].

        Args:
            min_val: Minimum value (inclusive)
            max_val: Maximum value (inclusive)

        Returns:
            Random integer in range
        """
        return int(self.next() * (max_val - min_val + 1)) + min_val

    def choice(self, items: list) -> any:
        """Choose random item from list.

        Args:
            items: List to choose from

        Returns:
            Random item from list
        """
        return items[self.randint(0, len(items) - 1)]
