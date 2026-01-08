"""
Rate Limiter Context

The context class that holds a rate limiter strategy and delegates
rate limiting operations to it. Allows switching strategies at runtime.
"""

from typing import Optional

try:
    from .rate_limiter_strategy import RateLimiterStrategy
except ImportError:
    from rate_limiter_strategy import RateLimiterStrategy


class RateLimiterContext:
    """
    Context class that uses a rate limiter strategy.
    
    Provides a simple interface to switch between different rate limiting
    algorithms at runtime. Delegates all rate limiting operations to the
    underlying strategy.
    """

    def __init__(self, strategy: RateLimiterStrategy):
        """
        Initialize the context with a rate limiter strategy.
        
        Args:
            strategy: An instance of a RateLimiterStrategy implementation
        """
        self._strategy = strategy

    def set_strategy(self, strategy: RateLimiterStrategy):
        """
        Switch to a different rate limiter strategy.
        
        Args:
            strategy: An instance of a RateLimiterStrategy implementation
        """
        self._strategy = strategy

    def allow_request(self, key: str) -> bool:
        """
        Check if a request is allowed for the given key.
        
        Args:
            key: Unique identifier (e.g., user ID, IP address)
            
        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        return self._strategy.allow_request(key)

    def get_usage(self, key: str) -> tuple[float, float]:
        """
        Get current usage information for the given key.
        
        Args:
            key: Unique identifier
            
        Returns:
            Tuple of (current_count, time_until_reset)
        """
        return self._strategy.get_usage(key)

    def set_limit(self, key: str, max_requests: int, window_seconds: float):
        """
        Set custom limits for a specific key.
        
        Args:
            key: Unique identifier
            max_requests: Number of requests allowed per window
            window_seconds: Time window in seconds
        """
        self._strategy.set_limit(key, max_requests, window_seconds)

    def get_current_strategy(self) -> str:
        """
        Get the name of the current strategy.
        
        Returns:
            Name of the current strategy class
        """
        return self._strategy.__class__.__name__
