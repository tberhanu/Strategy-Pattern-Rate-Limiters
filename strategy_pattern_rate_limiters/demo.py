"""
Rate Limiter Strategy Pattern - Demonstration

This script demonstrates how to use the strategy pattern to switch between
different rate limiting algorithms at runtime.
"""

import time
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from rate_limiter_context import RateLimiterContext
from sliding_window_strategy import SlidingWindowStrategy
from token_bucket_strategy import TokenBucketStrategy


def demo_strategy_switching():
    """
    Demonstrate switching between different rate limiting strategies.
    """
    print("=" * 70)
    print("RATE LIMITER STRATEGY PATTERN DEMO")
    print("=" * 70)

    # Configuration: 5 requests per 10 seconds
    max_requests = 5
    window_seconds = 10.0
    
    # ========== DEMO 1: Sliding Window Strategy ==========
    print("\n1. SLIDING WINDOW STRATEGY (5 requests per 10 seconds)")
    print("-" * 70)
    
    sliding_strategy = SlidingWindowStrategy(max_requests, window_seconds)
    limiter = RateLimiterContext(sliding_strategy)
    
    user_id = "user_123"
    print(f"Using strategy: {limiter.get_current_strategy()}")
    print(f"Sending 8 requests quickly for {user_id}:\n")
    
    for i in range(8):
        allowed = limiter.allow_request(user_id)
        current_count, ttl = limiter.get_usage(user_id)
        status = "✓ ALLOWED" if allowed else "✗ REJECTED"
        print(f"  Request {i+1}: {status} | Current: {current_count:.0f}/5 | TTL: {ttl:.2f}s")
    
    print(f"\nWaiting 6 seconds for window to reset...")
    time.sleep(6)
    
    print(f"After 6 seconds, sending 3 more requests:")
    for i in range(3):
        allowed = limiter.allow_request(user_id)
        current_count, ttl = limiter.get_usage(user_id)
        status = "✓ ALLOWED" if allowed else "✗ REJECTED"
        print(f"  Request {i+1}: {status} | Current: {current_count:.0f}/5 | TTL: {ttl:.2f}s")
    
    # ========== DEMO 2: Token Bucket Strategy ==========
    print("\n\n2. TOKEN BUCKET STRATEGY (5 requests per 10 seconds)")
    print("-" * 70)
    
    token_strategy = TokenBucketStrategy(max_requests, window_seconds)
    
    # Switch to token bucket strategy
    limiter.set_strategy(token_strategy)
    print(f"Switched to strategy: {limiter.get_current_strategy()}")
    print(f"Sending 8 requests quickly for {user_id}:\n")
    
    for i in range(8):
        allowed = limiter.allow_request(user_id)
        current_tokens, ttl = limiter.get_usage(user_id)
        status = "✓ ALLOWED" if allowed else "✗ REJECTED"
        print(f"  Request {i+1}: {status} | Tokens: {current_tokens:.2f}/5 | TTL: {ttl:.2f}s")
    
    print(f"\nWaiting 3 seconds for token refill...")
    time.sleep(3)
    
    print(f"After 3 seconds, sending 3 more requests:")
    for i in range(3):
        allowed = limiter.allow_request(user_id)
        current_tokens, ttl = limiter.get_usage(user_id)
        status = "✓ ALLOWED" if allowed else "✗ REJECTED"
        print(f"  Request {i+1}: {status} | Tokens: {current_tokens:.2f}/5 | TTL: {ttl:.2f}s")
    
    # ========== DEMO 3: Per-Key Custom Limits ==========
    print("\n\n3. CUSTOM LIMITS FOR DIFFERENT USERS")
    print("-" * 70)
    
    sliding_strategy2 = SlidingWindowStrategy(default_max_requests=3, default_window_seconds=5.0)
    limiter2 = RateLimiterContext(sliding_strategy2)
    
    print(f"Using strategy: {limiter2.get_current_strategy()}")
    print(f"Default limits: 3 requests per 5 seconds")
    print(f"Custom limit for premium_user: 10 requests per 5 seconds\n")
    
    # Set custom limit for premium user
    limiter2.set_limit("premium_user", 10, 5.0)
    
    regular_user = "regular_user"
    premium_user = "premium_user"
    
    print("Sending 5 requests for regular_user (default limits):")
    for i in range(5):
        allowed = limiter2.allow_request(regular_user)
        status = "✓" if allowed else "✗"
        print(f"  Request {i+1}: {status}")
    
    print("\nSending 5 requests for premium_user (custom limits):")
    for i in range(5):
        allowed = limiter2.allow_request(premium_user)
        status = "✓" if allowed else "✗"
        print(f"  Request {i+1}: {status}")
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    demo_strategy_switching()
