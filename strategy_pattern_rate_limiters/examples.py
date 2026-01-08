"""
Strategy Pattern Rate Limiter - Usage Examples

This file contains various examples of how to use the rate limiter
with different strategies.
"""

import time
from rate_limiter_context import RateLimiterContext
from sliding_window_strategy import SlidingWindowStrategy
from token_bucket_strategy import TokenBucketStrategy


# ============================================================================
# EXAMPLE 1: Basic Usage with Sliding Window
# ============================================================================
def example_basic_sliding_window():
    """Basic sliding window rate limiting."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Sliding Window Rate Limiting")
    print("=" * 70)
    
    # Create a sliding window strategy: 3 requests per 5 seconds
    strategy = SlidingWindowStrategy(default_max_requests=3, default_window_seconds=5.0)
    limiter = RateLimiterContext(strategy)
    
    user = "api_client_1"
    
    print(f"Rate limit: 3 requests per 5 seconds")
    print(f"Strategy: {limiter.get_current_strategy()}\n")
    
    for i in range(6):
        allowed = limiter.allow_request(user)
        count, ttl = limiter.get_usage(user)
        
        status = "✓ ALLOWED" if allowed else "✗ BLOCKED"
        print(f"Request {i+1}: {status} | Usage: {count}/3 | Reset in: {ttl:.1f}s")


# ============================================================================
# EXAMPLE 2: Basic Usage with Token Bucket
# ============================================================================
def example_basic_token_bucket():
    """Basic token bucket rate limiting."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Basic Token Bucket Rate Limiting")
    print("=" * 70)
    
    # Create a token bucket strategy: 4 requests per 8 seconds
    strategy = TokenBucketStrategy(default_max_requests=4, default_window_seconds=8.0)
    limiter = RateLimiterContext(strategy)
    
    user = "mobile_app"
    
    print(f"Rate limit: 4 requests per 8 seconds")
    print(f"Strategy: {limiter.get_current_strategy()}\n")
    
    print("Sending 4 requests immediately:")
    for i in range(4):
        allowed = limiter.allow_request(user)
        tokens, ttl = limiter.get_usage(user)
        status = "✓" if allowed else "✗"
        print(f"  Request {i+1}: {status} | Tokens: {tokens:.2f}/4 | TTL: {ttl:.2f}s")
    
    print("\nWaiting 2 seconds for token refill...")
    time.sleep(2)
    
    print("Sending 2 more requests after 2 seconds:")
    for i in range(2):
        allowed = limiter.allow_request(user)
        tokens, ttl = limiter.get_usage(user)
        status = "✓" if allowed else "✗"
        print(f"  Request {i+1}: {status} | Tokens: {tokens:.2f}/4 | TTL: {ttl:.2f}s")


# ============================================================================
# EXAMPLE 3: Strategy Switching
# ============================================================================
def example_strategy_switching():
    """Switch between strategies at runtime."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Runtime Strategy Switching")
    print("=" * 70)
    
    user = "user_456"
    
    # Start with sliding window
    print("\nPhase 1: Using Sliding Window Strategy")
    limiter = RateLimiterContext(SlidingWindowStrategy(2, 5.0))
    print(f"Current strategy: {limiter.get_current_strategy()}")
    
    allowed = limiter.allow_request(user)
    print(f"Request 1: {'✓ ALLOWED' if allowed else '✗ BLOCKED'}")
    
    # Switch to token bucket
    print("\nPhase 2: Switching to Token Bucket Strategy")
    limiter.set_strategy(TokenBucketStrategy(3, 5.0))
    print(f"Current strategy: {limiter.get_current_strategy()}")
    
    allowed = limiter.allow_request(user)
    print(f"Request 2: {'✓ ALLOWED' if allowed else '✗ BLOCKED'}")
    
    print("\nNote: Different strategies maintain separate state per user.")


# ============================================================================
# EXAMPLE 4: Tiered Rate Limits (Different Limits per User)
# ============================================================================
def example_tiered_limits():
    """Different rate limits for different user tiers."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Tiered Rate Limits")
    print("=" * 70)
    
    # Base strategy: free tier (5 requests per 10 seconds)
    strategy = SlidingWindowStrategy(default_max_requests=5, default_window_seconds=10.0)
    limiter = RateLimiterContext(strategy)
    
    # Premium tier: 20 requests per 10 seconds
    limiter.set_limit("premium_user", max_requests=20, window_seconds=10.0)
    
    # VIP tier: unlimited (very high limit)
    limiter.set_limit("vip_user", max_requests=1000, window_seconds=10.0)
    
    print("Free tier: 5 requests per 10 seconds")
    print("Premium tier: 20 requests per 10 seconds")
    print("VIP tier: 1000 requests per 10 seconds\n")
    
    # Test free user
    print("Free user (10 requests):")
    free_allowed = 0
    for i in range(10):
        if limiter.allow_request("free_user"):
            free_allowed += 1
    print(f"  Allowed: {free_allowed}/10")
    
    # Test premium user
    print("\nPremium user (10 requests):")
    premium_allowed = 0
    for i in range(10):
        if limiter.allow_request("premium_user"):
            premium_allowed += 1
    print(f"  Allowed: {premium_allowed}/10")
    
    # Test VIP user
    print("\nVIP user (10 requests):")
    vip_allowed = 0
    for i in range(10):
        if limiter.allow_request("vip_user"):
            vip_allowed += 1
    print(f"  Allowed: {vip_allowed}/10")


# ============================================================================
# EXAMPLE 5: Multiple Clients with Shared Context
# ============================================================================
def example_multiple_clients():
    """Multiple clients sharing the same rate limiter."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Multiple Independent Clients")
    print("=" * 70)
    
    # Single limiter shared by multiple clients
    limiter = RateLimiterContext(SlidingWindowStrategy(2, 5.0))
    
    print("Rate limit: 2 requests per 5 seconds (per client)")
    print("Strategy: Sliding Window\n")
    
    clients = ["client_A", "client_B", "client_C"]
    
    print("Sending 3 requests from each client:")
    for i in range(3):
        print(f"\nRound {i+1}:")
        for client in clients:
            allowed = limiter.allow_request(client)
            count, ttl = limiter.get_usage(client)
            status = "✓" if allowed else "✗"
            print(f"  {client}: {status} | Usage: {count}/2 | TTL: {ttl:.1f}s")


# ============================================================================
# EXAMPLE 6: API Rate Limiting Simulation
# ============================================================================
def example_api_rate_limiting():
    """Simulate API rate limiting scenario."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: API Rate Limiting Simulation")
    print("=" * 70)
    
    # API rate limit: 100 requests per minute per user
    strategy = TokenBucketStrategy(default_max_requests=100, default_window_seconds=60.0)
    api_limiter = RateLimiterContext(strategy)
    
    print("API Rate Limit: 100 requests per minute per user")
    print("Strategy: Token Bucket\n")
    
    api_key = "sk_test_1234567890"
    
    print(f"Simulating burst of 50 requests:")
    allowed_count = 0
    blocked_count = 0
    
    for i in range(50):
        if api_limiter.allow_request(api_key):
            allowed_count += 1
        else:
            blocked_count += 1
        
        if (i + 1) % 10 == 0:
            tokens, ttl = api_limiter.get_usage(api_key)
            print(f"  After {i+1} attempts: {allowed_count} allowed, {blocked_count} blocked")
            print(f"    Remaining tokens: {tokens:.0f}/100")
    
    print(f"\nFinal result: {allowed_count} requests allowed, {blocked_count} requests blocked")


# ============================================================================
# EXAMPLE 7: Choosing the Right Strategy
# ============================================================================
def example_strategy_comparison():
    """Compare different strategies."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Strategy Selection Guide")
    print("=" * 70)
    
    guide = """
    When to use each strategy:
    
    1. SLIDING WINDOW
       ✓ Precise and accurate
       ✓ Good for strict limits
       ✗ Slightly more memory usage
       Best for: Single server, exact enforcement needed
       
    2. TOKEN BUCKET
       ✓ Efficient (O(1) operations)
       ✓ Good for handling bursts
       ✓ Better memory efficiency
       ✗ Approximate enforcement (continuous refill)
       Best for: High-frequency requests, smooth distribution
       
    3. REDIS LUA
       ✓ Distributed rate limiting
       ✓ Atomic operations
       ✗ Network latency
       ✗ Requires Redis infrastructure
       Best for: Multi-server deployments, shared limits
    """
    
    print(guide)


def main():
    """Run all examples."""
    example_basic_sliding_window()
    example_basic_token_bucket()
    example_strategy_switching()
    example_tiered_limits()
    example_multiple_clients()
    example_api_rate_limiting()
    example_strategy_comparison()
    
    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
