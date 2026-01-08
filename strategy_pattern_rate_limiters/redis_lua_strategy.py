"""
Redis Lua Rate Limiter Strategy

Uses Redis sorted sets with a Lua script for atomic sliding window operations.
"""

import time
import uuid
import redis

try:
    from .rate_limiter_strategy import RateLimiterStrategy
except ImportError:
    from rate_limiter_strategy import RateLimiterStrategy


class RedisLuaStrategy(RateLimiterStrategy):
    """
    Sliding-window rate limiter using Redis sorted sets + Lua script.
    """

    LUA_SCRIPT = """
    local key = KEYS[1]
    local now = tonumber(ARGV[1])
    local window_ms = tonumber(ARGV[2])
    local limit = tonumber(ARGV[3])

    -- Remove entries outside the window
    redis.call("ZREMRANGEBYSCORE", key, 0, now - window_ms)

    -- Current count in the window
    local count = redis.call("ZCARD", key)

    if count >= limit then
        return {0, count}  -- not allowed
    end

    -- Add current request with unique member
    local member = ARGV[4]
    redis.call("ZADD", key, now, member)

    -- Optional: set TTL to avoid key buildup
    redis.call("PEXPIRE", key, window_ms)

    count = count + 1
    return {1, count}  -- allowed
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        prefix: str = "rate:",
        max_requests: int = 10,
        window_seconds: int = 60,
    ):
        """
        Initialize the Redis Lua strategy.
        
        Args:
            redis_client: Redis client instance
            prefix: Key prefix for rate limit tracking
            max_requests: Default requests allowed per window
            window_seconds: Default time window in seconds
        """
        self.redis = redis_client
        self.prefix = prefix
        self.max_requests = max_requests
        self.window_ms = window_seconds * 1000
        # Registers the Lua script with Redis.
        self._lua = self.redis.register_script(self.LUA_SCRIPT)
        self.limits = {}

    def set_limit(self, key: str, max_requests: int, window_seconds: float):
        """Override default limits for a specific key."""
        self.limits[key] = (int(max_requests), int(window_seconds * 1000))

    def _key(self, identifier: str) -> str:
        return f"{self.prefix}{identifier}"

    def _get_limit(self, identifier: str):
        """Get limit for identifier, falling back to defaults."""
        if identifier in self.limits:
            return self.limits[identifier]
        return (self.max_requests, self.window_ms)

    def allow_request(self, identifier: str) -> bool:
        """
        Check if request is allowed for the given identifier.
        Returns True if allowed, False if rate limit exceeded.
        """
        max_requests, window_ms = self._get_limit(identifier)
        now_ms = int(time.time() * 1000)
        member = f"{now_ms}-{uuid.uuid4()}"
        
        result = self._lua(
            keys=[self._key(identifier)],
            args=[now_ms, window_ms, max_requests, member],
        )
        allowed = bool(result[0])
        return allowed

    def get_usage(self, identifier: str) -> tuple[float, float]:
        """
        Returns (current_count, time_until_reset).
        current_count: number of requests in current window
        time_until_reset: seconds until oldest request expires
        """
        max_requests, window_ms = self._get_limit(identifier)
        now_ms = int(time.time() * 1000)
        key = self._key(identifier)
        
        # Remove expired entries
        self.redis.zremrangebyscore(key, 0, now_ms - window_ms)
        
        # Get current count
        count = self.redis.zcard(key)
        
        if count == 0:
            return (0.0, 0.0)
        
        # Get oldest entry's score
        oldest_entries = self.redis.zrange(key, 0, 0, withscores=True)
        if oldest_entries:
            oldest_score = oldest_entries[0][1]
            ttl_ms = max(0, (oldest_score + window_ms) - now_ms)
            return (float(count), ttl_ms / 1000.0)
        
        return (float(count), 0.0)
