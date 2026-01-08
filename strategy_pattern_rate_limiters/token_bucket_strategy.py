"""
Token Bucket Rate Limiter Strategy

Uses a token bucket algorithm where tokens are refilled at a constant rate.
Requests consume 1 token.
"""

import threading
import time

try:
    from .rate_limiter_strategy import RateLimiterStrategy
except ImportError:
    from rate_limiter_strategy import RateLimiterStrategy


class TokenBucket:
    """
    Token bucket rate limiter.
    
    Tokens are refilled at a constant rate (refill_rate tokens/sec).
    Each request consumes 1 token. Requests are allowed if tokens >= 1.
    """

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize a token bucket.
        
        Args:
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second
        """
        self.capacity = float(capacity)
        self.tokens = float(capacity)
        self.refill_rate = float(refill_rate)
        self.last_refill = time.monotonic()
        self.lock = threading.Lock()

    def _refill(self):
        """Recalculate tokens based on elapsed time since last refill."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        added = elapsed * self.refill_rate
        # Only update tokens and `last_refill` when we actually gained tokens.
        if added > 0:
            self.tokens = min(self.capacity, self.tokens + added)
            self.last_refill = now

    def allow(self) -> bool:
        """
        Check if a request is allowed (consume 1 token).
        Returns True if allowed, False otherwise.
        """
        with self.lock:
            self._refill()

            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False

    def get_usage(self) -> tuple[float, float]:
        """
        Returns (tokens_available, time_until_next_token).
        tokens_available: current token count
        time_until_next_token: seconds until next token available (if empty)
        """
        with self.lock:
            self._refill()

            if self.tokens >= 1:
                return (self.tokens, 0.0)

            missing = 1 - self.tokens
            ttl = missing / self.refill_rate
            return (self.tokens, ttl)


class TokenBucketStrategy(RateLimiterStrategy):
    """
    Token bucket rate limiter that manages per-key buckets.
    """

    def __init__(self, default_max_requests: int, default_window_seconds: float):
        """
        Initialize the token bucket strategy.
        
        Args:
            default_max_requests: Requests allowed per window
            default_window_seconds: Time window in seconds (used to calculate refill rate)
        """
        self.default_max = int(default_max_requests)
        self.default_window = float(default_window_seconds)

        # Per-key token buckets
        self.token_buckets = {}

        # Per-key limits (optional override of defaults)
        self.limits = {}

    def set_limit(self, key: str, max_requests: int, window_seconds: float):
        """
        Set custom limits for a key and create its token bucket.
        """
        self.limits[key] = (int(max_requests), float(window_seconds))
        refill_rate = max_requests / window_seconds
        self.token_buckets[key] = TokenBucket(max_requests, refill_rate)

    def _get_limit(self, key: str):
        """Get limit for key, falling back to defaults."""
        return self.limits.get(key, (self.default_max, self.default_window))

    def allow_request(self, key: str) -> bool:
        """
        Check if request is allowed for the given key.
        Returns True if allowed, False if rate limit exceeded.
        """
        if key not in self.token_buckets:
            max_requests, window_seconds = self._get_limit(key)
            refill_rate = max_requests / window_seconds
            self.token_buckets[key] = TokenBucket(max_requests, refill_rate)

        return self.token_buckets[key].allow()

    def get_usage(self, key: str) -> tuple[float, float]:
        """
        Returns (tokens_available, time_until_next_token).
        """
        if key not in self.token_buckets:
            max_requests, window_seconds = self._get_limit(key)
            refill_rate = max_requests / window_seconds
            self.token_buckets[key] = TokenBucket(max_requests, refill_rate)

        return self.token_buckets[key].get_usage()
