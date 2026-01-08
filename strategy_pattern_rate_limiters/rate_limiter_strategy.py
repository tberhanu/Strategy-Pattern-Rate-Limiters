"""
Rate Limiter Strategy Pattern

This module defines the interface and various strategies for rate limiting.
Strategies can be switched at runtime to use different rate limiting algorithms.
"""

from abc import ABC, abstractmethod
from typing import Tuple


class RateLimiterStrategy(ABC):
    """
    Abstract base class defining the interface for all rate limiting strategies.
    """

    @abstractmethod
    def allow_request(self, key: str) -> bool:
        """
        Check if a request is allowed for the given key.
        
        Args:
            key: Unique identifier (e.g., user ID, IP address)
            
        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        pass

    @abstractmethod
    def get_usage(self, key: str) -> Tuple[float, float]:
        """
        Get current usage information for the given key.
        
        Args:
            key: Unique identifier
            
        Returns:
            Tuple of (current_count, time_until_reset) in seconds
        """
        pass

    @abstractmethod
    def set_limit(self, key: str, max_requests: int, window_seconds: float):
        """
        Set custom limits for a specific key.
        
        Args:
            key: Unique identifier
            max_requests: Number of requests allowed per window
            window_seconds: Time window in seconds
        """
        pass
