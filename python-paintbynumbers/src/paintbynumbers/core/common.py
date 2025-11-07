"""Common utilities and types."""

from __future__ import annotations
import asyncio
from typing import Callable, Optional, Awaitable


async def delay(ms: float) -> None:
    """Async delay/sleep for specified milliseconds.

    Args:
        ms: Milliseconds to sleep
    """
    await asyncio.sleep(ms / 1000.0)


class CancellationToken:
    """Token for canceling long-running operations.

    Attributes:
        is_cancelled: Whether the operation has been cancelled
    """

    def __init__(self) -> None:
        """Initialize cancellation token."""
        self.is_cancelled: bool = False

    def cancel(self) -> None:
        """Cancel the operation."""
        self.is_cancelled = True

    def reset(self) -> None:
        """Reset the cancellation state."""
        self.is_cancelled = False


# Type alias for progress callbacks
ProgressCallback = Callable[[float], None]
AsyncProgressCallback = Callable[[float], Awaitable[None]]
