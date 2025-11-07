"""Tests for common utilities."""

import pytest
import asyncio
import time
from paintbynumbers.core.common import delay, CancellationToken


class TestDelay:
    """Test delay function."""

    @pytest.mark.asyncio
    async def test_delay_basic(self) -> None:
        """Test basic delay functionality."""
        start = time.time()
        await delay(100)  # 100ms
        elapsed = (time.time() - start) * 1000

        # Should be approximately 100ms (allow 50ms tolerance)
        assert 50 < elapsed < 200

    @pytest.mark.asyncio
    async def test_delay_zero(self) -> None:
        """Test delay with zero milliseconds."""
        start = time.time()
        await delay(0)
        elapsed = (time.time() - start) * 1000

        # Should complete very quickly
        assert elapsed < 50


class TestCancellationToken:
    """Test CancellationToken class."""

    def test_create_token(self) -> None:
        """Test creating a cancellation token."""
        token = CancellationToken()
        assert not token.is_cancelled

    def test_cancel_token(self) -> None:
        """Test canceling a token."""
        token = CancellationToken()
        assert not token.is_cancelled

        token.cancel()
        assert token.is_cancelled

    def test_reset_token(self) -> None:
        """Test resetting a cancelled token."""
        token = CancellationToken()

        token.cancel()
        assert token.is_cancelled

        token.reset()
        assert not token.is_cancelled

    def test_multiple_cancel(self) -> None:
        """Test calling cancel multiple times."""
        token = CancellationToken()

        token.cancel()
        token.cancel()
        token.cancel()

        assert token.is_cancelled

    def test_token_in_loop(self) -> None:
        """Test using token to cancel a loop."""
        token = CancellationToken()
        iterations = 0

        for i in range(1000):
            if token.is_cancelled:
                break
            iterations += 1
            if i == 10:
                token.cancel()

        assert iterations == 11  # 0-10 inclusive
        assert token.is_cancelled
