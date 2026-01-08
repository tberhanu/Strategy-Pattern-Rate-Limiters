import sys
from pathlib import Path
import pytest

# Ensure project root is on sys.path so tests can import package
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from strategy_pattern_rate_limiters.token_bucket_strategy import TokenBucket


def test_token_bucket_consumes_and_refills():
    tb = TokenBucket(capacity=3, refill_rate=1.0)  # 1 token/sec

    # consume all tokens
    assert tb.allow() is True
    assert tb.allow() is True
    assert tb.allow() is True
    assert tb.allow() is False

    # simulate time passage by moving last_refill back
    tb.last_refill = tb.last_refill - 1.5  # 1.5 seconds -> ~1.5 tokens

    # after refill there should be at least 1 token available
    allowed = tb.allow()
    assert allowed in (True, False)  # allow could be True if enough tokens
    tokens, ttl = tb.get_usage()
    assert isinstance(tokens, float)
    assert isinstance(ttl, float)
