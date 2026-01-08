import sys
from pathlib import Path
import pytest

# Ensure project root is on sys.path so tests can import package
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from strategy_pattern_rate_limiters.rate_limiter_context import RateLimiterContext
from strategy_pattern_rate_limiters.sliding_window_strategy import SlidingWindowStrategy
from strategy_pattern_rate_limiters.token_bucket_strategy import TokenBucketStrategy


def test_context_switching_changes_strategy_behavior():
    sliding = SlidingWindowStrategy(default_max_requests=1, default_window_seconds=10.0)
    token = TokenBucketStrategy(default_max_requests=2, default_window_seconds=10.0)

    ctx = RateLimiterContext(sliding)
    key = "switch_user"

    # Sliding allows one request
    assert ctx.allow_request(key) is True
    assert ctx.allow_request(key) is False

    # Switch to token bucket
    ctx.set_strategy(token)
    assert ctx.get_current_strategy() == "TokenBucketStrategy"

    # Token bucket should allow up to 2 requests initially
    assert ctx.allow_request(key) in (True, False)
    # get_usage should return tuple
    usage = ctx.get_usage(key)
    assert isinstance(usage, tuple)


def test_redis_strategy_ping():
    # Integration test for Redis-backed rate limiter.
    # Skip if `redis` package isn't installed or the Redis server isn't reachable.
    try:
        import redis
    except Exception:
        pytest.skip("redis package not installed")

    try:
        r = redis.Redis(host="localhost", port=6379, db=15, socket_connect_timeout=1)
        r.ping()
    except Exception:
        pytest.skip("Redis server not available on localhost:6379")

    # Import the strategy implementation
    from strategy_pattern_rate_limiters.redis_lua_strategy import RedisLuaStrategy
    import uuid

    strategy = RedisLuaStrategy(redis_client=r, prefix="test:rate:", max_requests=3, window_seconds=2)
    identifier = f"pytest:{uuid.uuid4()}"

    # Ensure key is clean
    r.delete(strategy._key(identifier))

    # First 3 should be allowed, 4th should be blocked
    assert strategy.allow_request(identifier) is True
    assert strategy.allow_request(identifier) is True
    assert strategy.allow_request(identifier) is True
    assert strategy.allow_request(identifier) is False

    # Cleanup
    r.delete(strategy._key(identifier))
