import time
import sys
from pathlib import Path
import pytest

# Ensure project root is on sys.path so tests can import package
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from strategy_pattern_rate_limiters.sliding_window_strategy import SlidingWindowStrategy


def test_sliding_window_allows_and_blocks():
    limiter = SlidingWindowStrategy(default_max_requests=2, default_window_seconds=1.0)
    key = "test_user"

    assert limiter.allow_request(key) is True
    assert limiter.allow_request(key) is True
    # third request should be blocked
    assert limiter.allow_request(key) is False

    # simulate expiration by moving the oldest timestamp back
    store = limiter.store[key]
    assert len(store) == 2
    store[0] = store[0] - 2.0  # make it older than window

    # now one slot should be available
    assert limiter.allow_request(key) is True


def test_get_usage_returns_count_and_ttl():
    limiter = SlidingWindowStrategy(default_max_requests=3, default_window_seconds=2.0)
    key = "usage_user"

    assert limiter.get_usage(key) == (0, 0.0)
    assert limiter.allow_request(key) is True
    count, ttl = limiter.get_usage(key)
    assert count == 1
    assert ttl > 0.0
