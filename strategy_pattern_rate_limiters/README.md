# Strategy Pattern Rate Limiters

A flexible rate limiting implementation using the **Strategy Pattern** that allows you to switch between different rate limiting algorithms at runtime.

## Overview

This package provides three different rate limiting strategies:

1. **Sliding Window Strategy** - Tracks request timestamps in a sliding window
2. **Token Bucket Strategy** - Maintains a bucket of tokens that refill at a constant rate
3. **Redis Lua Strategy** - Uses Redis sorted sets with Lua scripts for distributed rate limiting

## Architecture

### Core Components

#### 1. `RateLimiterStrategy` (Abstract Base Class)
Defines the interface that all rate limiting strategies must implement:

```python
class RateLimiterStrategy(ABC):
    def allow_request(self, key: str) -> bool:
        """Check if a request is allowed"""
        pass
    
    def get_usage(self, key: str) -> Tuple[float, float]:
        """Get current usage (count, time_until_reset)"""
        pass
    
    def set_limit(self, key: str, max_requests: int, window_seconds: float):
        """Set custom limits for a key"""
        pass
```

#### 2. `RateLimiterContext` (Context Class)
Uses a strategy implementation and allows switching strategies at runtime:

```python
limiter = RateLimiterContext(sliding_strategy)
limiter.allow_request("user_123")          # Uses sliding strategy
limiter.set_strategy(token_bucket_strategy) # Switch to token bucket
limiter.allow_request("user_123")          # Now uses token bucket
```

#### 3. Strategy Implementations

**SlidingWindowStrategy**
- Per-key request timestamp tracking with deques
- Thread-safe with per-key locks
- Removes expired timestamps automatically
- Memory usage depends on request volume

**TokenBucketStrategy**
- Token bucket per key
- Constant token refill rate
- Smooth request distribution
- Lower memory overhead

**RedisLuaStrategy**
- Distributed rate limiting using Redis
- Atomic Lua script execution
- Suitable for multi-server deployments
- Requires Redis connection

## Usage

### Basic Usage - Sliding Window

```python
from strategy_pattern_rate_limiters import RateLimiterContext, SlidingWindowStrategy

# Create strategy: 5 requests per 10 seconds
strategy = SlidingWindowStrategy(max_requests=5, default_window_seconds=10.0)

# Create context with strategy
limiter = RateLimiterContext(strategy)

# Use rate limiter
user_id = "user_123"
if limiter.allow_request(user_id):
    print("Request allowed")
else:
    print("Rate limit exceeded")

# Check usage
count, ttl = limiter.get_usage(user_id)
print(f"Requests: {count}/5, Reset in: {ttl:.2f}s")
```

### Switching Strategies at Runtime

```python
from strategy_pattern_rate_limiters import (
    RateLimiterContext, 
    SlidingWindowStrategy,
    TokenBucketStrategy
)

# Start with sliding window
limiter = RateLimiterContext(SlidingWindowStrategy(5, 10.0))
limiter.allow_request("user_123")

# Switch to token bucket
limiter.set_strategy(TokenBucketStrategy(5, 10.0))
limiter.allow_request("user_123")  # Now uses token bucket

# Get current strategy name
print(limiter.get_current_strategy())  # "TokenBucketStrategy"
```

### Custom Per-Key Limits

```python
limiter = RateLimiterContext(SlidingWindowStrategy(5, 10.0))

# Default: 5 requests per 10 seconds
limiter.allow_request("regular_user")

# Premium user: 20 requests per 10 seconds
limiter.set_limit("premium_user", 20, 10.0)
limiter.allow_request("premium_user")
```

### Using Redis Strategy (Distributed)

```python
import redis
from strategy_pattern_rate_limiters import RateLimiterContext, RedisLuaStrategy

redis_client = redis.Redis(host='localhost', port=6379, db=0)
strategy = RedisLuaStrategy(
    redis_client=redis_client,
    prefix="rate:",
    max_requests=5,
    window_seconds=10
)

limiter = RateLimiterContext(strategy)
if limiter.allow_request("user_123"):
    print("Request allowed")
```

## File Structure

```
strategy_pattern_rate_limiters/
├── __init__.py                      # Package exports
├── rate_limiter_strategy.py         # Abstract base class
├── rate_limiter_context.py          # Context class
├── sliding_window_strategy.py       # Sliding window implementation
├── token_bucket_strategy.py         # Token bucket implementation
├── redis_lua_strategy.py            # Redis Lua implementation
└── demo.py                          # Demonstration script
```

## Running the Demo

```bash
python demo.py
```

The demo shows:
1. Sliding window strategy in action
2. Token bucket strategy in action
3. Switching between strategies
4. Custom per-key limits

## Strategy Comparison

| Feature | Sliding Window | Token Bucket | Redis Lua |
|---------|---|---|---|
| **Memory** | Medium (tracks timestamps) | Low (token counter) | N/A (Redis) |
| **Accuracy** | Precise | Approximate | Precise |
| **Thread-safe** | Yes (per-key locks) | Yes (built-in) | Yes (Redis atomic) |
| **Distributed** | No | No | Yes |
| **Complexity** | Low | Low | Medium |
| **Best For** | Single server, precise limits | Smooth distribution | Multiple servers |

## Design Pattern Benefits

The **Strategy Pattern** provides:

1. **Flexibility** - Choose different algorithms at runtime
2. **Extensibility** - Add new strategies without modifying existing code
3. **Testability** - Easy to test each strategy independently
4. **Maintainability** - Each strategy is isolated and focused
5. **Reusability** - Strategies can be used in different contexts

## Example: Adding a New Strategy

To add a new rate limiting algorithm, simply create a new class implementing `RateLimiterStrategy`:

```python
from strategy_pattern_rate_limiters import RateLimiterStrategy

class CustomStrategy(RateLimiterStrategy):
    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Your implementation
    
    def allow_request(self, key: str) -> bool:
        # Your logic
        pass
    
    def get_usage(self, key: str) -> tuple[float, float]:
        # Your logic
        pass
    
    def set_limit(self, key: str, max_requests: int, window_seconds: float):
        # Your logic
        pass

# Use it
limiter = RateLimiterContext(CustomStrategy(5, 10.0))
```

## Thread Safety

- **SlidingWindowStrategy**: Thread-safe with per-key locks
- **TokenBucketStrategy**: Thread-safe with lock in TokenBucket
- **RedisLuaStrategy**: Thread-safe (Redis handles concurrency)

All strategies are safe to use in multi-threaded environments.

## Performance Considerations

- **SlidingWindowStrategy**: O(n) complexity in window cleanup, good for low-frequency requests
- **TokenBucketStrategy**: O(1) complexity, better for high-frequency requests
- **RedisLuaStrategy**: Network latency + Redis performance, best for distributed systems
