# Quick Start Guide

Get up and running with the Strategy Pattern Rate Limiter in 5 minutes!

## Installation

The package is self-contained. No external dependencies required for the core strategies.

For Redis strategy, install redis client:
```bash
pip install redis
```

## Basic Usage (30 seconds)

```python
from strategy_pattern_rate_limiters import RateLimiterContext, SlidingWindowStrategy

# Create rate limiter: 5 requests per 10 seconds
limiter = RateLimiterContext(SlidingWindowStrategy(5, 10.0))

# Check if request is allowed
if limiter.allow_request("user_123"):
    print("Request allowed!")
else:
    print("Rate limit exceeded")
```

## Choose Your Strategy

### Option 1: Sliding Window (Precise)
```python
from strategy_pattern_rate_limiters import SlidingWindowStrategy

strategy = SlidingWindowStrategy(default_max_requests=5, default_window_seconds=10.0)
limiter = RateLimiterContext(strategy)
```
**Best for**: Single server, exact enforcement

### Option 2: Token Bucket (Efficient)
```python
from strategy_pattern_rate_limiters import TokenBucketStrategy

strategy = TokenBucketStrategy(default_max_requests=5, default_window_seconds=10.0)
limiter = RateLimiterContext(strategy)
```
**Best for**: High-frequency requests, smooth distribution

### Option 3: Redis Lua (Distributed)
```python
import redis
from strategy_pattern_rate_limiters import RedisLuaStrategy

redis_client = redis.Redis(host='localhost', port=6379, db=0)
strategy = RedisLuaStrategy(redis_client, prefix="rate:", max_requests=5, window_seconds=10)
limiter = RateLimiterContext(strategy)
```
**Best for**: Multiple servers, shared limits

## Common Tasks

### Check Usage
```python
count, time_until_reset = limiter.get_usage("user_123")
print(f"Used {count}/5 requests, reset in {time_until_reset:.1f}s")
```

### Set Custom Limit for Specific User
```python
# Premium user: 20 requests per 10 seconds
limiter.set_limit("premium_user", 20, 10.0)

# Regular user uses default (5 per 10s)
limiter.allow_request("regular_user")
```

### Switch Strategy at Runtime
```python
# Start with sliding window
limiter.set_strategy(SlidingWindowStrategy(5, 10.0))
limiter.allow_request("user_123")

# Switch to token bucket
limiter.set_strategy(TokenBucketStrategy(5, 10.0))
limiter.allow_request("user_123")  # Uses new strategy
```

### Get Current Strategy Name
```python
print(limiter.get_current_strategy())  # "SlidingWindowStrategy"
```

## Real-World Examples

### API Gateway
```python
limiter = RateLimiterContext(TokenBucketStrategy(100, 60.0))  # 100 req/min

@app.route('/api/endpoint')
def api_endpoint():
    if not limiter.allow_request(request.remote_addr):
        return {"error": "Rate limit exceeded"}, 429
    
    # Process request
    return {"data": "..."}
```

### Multi-Tier Service
```python
limiter = RateLimiterContext(SlidingWindowStrategy(10, 60.0))

# Set custom limits
limiter.set_limit("premium_user", 1000, 60.0)
limiter.set_limit("vip_user", 10000, 60.0)

def handle_request(user_id):
    if limiter.allow_request(user_id):
        # Process
        pass
    else:
        # Reject
        pass
```

### Load Balancing
```python
# Share rate limiter across multiple servers
redis_client = redis.Redis(host='redis.server', port=6379)
limiter = RateLimiterContext(
    RedisLuaStrategy(redis_client, prefix="api:", max_requests=1000, window_seconds=60)
)

# All servers enforce same limit
if limiter.allow_request(f"client:{client_id}"):
    # Process
    pass
```

## Running Examples

```bash
# Quick demo (2 minutes)
python demo.py

# Comprehensive examples (5 minutes)
python examples.py
```

## Troubleshooting

### "ImportError: No module named redis"
- Install redis: `pip install redis`
- Or skip Redis strategy if not needed

### Rate limit too strict?
```python
# Increase limit
limiter = RateLimiterContext(TokenBucketStrategy(100, 10.0))

# Or switch to token bucket for smoother distribution
limiter.set_strategy(TokenBucketStrategy(50, 10.0))
```

### Not limiting as expected?
```python
# Check usage
count, ttl = limiter.get_usage("user_123")
print(f"Current usage: {count}, TTL: {ttl}")

# Verify you're using same key consistently
limiter.allow_request("user_123")  # Good: consistent key
limiter.allow_request("different_key")  # Different: separate limit
```

## Performance Tips

1. **For APIs**: Use TokenBucketStrategy (better for bursts)
2. **For strict limits**: Use SlidingWindowStrategy (more precise)
3. **For microservices**: Use RedisLuaStrategy (shared state)

## Next Steps

1. **Try the demo**: `python demo.py`
2. **Run examples**: `python examples.py`
3. **Read documentation**: `README.md`
4. **Explore architecture**: `ARCHITECTURE.md`
5. **Implement custom strategy**: See ARCHITECTURE.md for guide

## API Reference

```python
# Context class
context = RateLimiterContext(strategy)
context.allow_request(key: str) -> bool
context.get_usage(key: str) -> Tuple[float, float]
context.set_limit(key: str, max_requests: int, window_seconds: float)
context.set_strategy(strategy: RateLimiterStrategy)
context.get_current_strategy() -> str

# Strategy interface (implement for custom strategies)
strategy.allow_request(key: str) -> bool
strategy.get_usage(key: str) -> Tuple[float, float]
strategy.set_limit(key: str, max_requests: int, window_seconds: float)
```

## Strategy Defaults

All strategies follow the same convention:
- `allow_request(key)`: Returns True if allowed, False if limit exceeded
- `get_usage(key)`: Returns (current_count, time_until_reset_seconds)
- `set_limit(key, max_requests, window_seconds)`: Override default limits

## Best Practices

✓ Use same key consistently for same entity
✓ Check usage before responding to user
✓ Choose strategy based on your use case
✓ Test with realistic load
✓ Monitor rate limit rejections
✓ Document your rate limit policy
✓ Allow gradual backoff/retry

✗ Mix keys for same entity
✗ Create new limiter per request
✗ Ignore the strategy choice
✗ Trust without testing
