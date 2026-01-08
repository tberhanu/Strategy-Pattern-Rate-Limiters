# Strategy Pattern Architecture

## Overview

This implementation demonstrates the **Strategy Pattern**, a behavioral design pattern that enables selecting an algorithm's behavior at runtime.

## Pattern Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    RateLimiterContext                        │
│  (Client code uses this interface)                           │
│  - Holds a RateLimiterStrategy reference                     │
│  - Delegates all operations to the strategy                  │
│  - Can switch strategies at runtime                          │
└─────────────────────────────────────────────────────────────┘
                            △
                            │
                            │ uses
                            │
        ┌───────────────────┴────────────────────┐
        │                                         │
        │  <<interface>>                          │
        │  RateLimiterStrategy                    │
        │  ────────────────────────────────       │
        │  + allow_request(key): bool             │
        │  + get_usage(key): (count, ttl)        │
        │  + set_limit(key, max, window)         │
        │                                         │
        └───────────────────┬────────────────────┘
                            △
                  ┌─────────┼─────────┐
                  │         │         │
        ┌─────────┴────┐ ┌──┴─────┬──┐ ┌──┴──────────────┐
        │              │ │        │  │ │                 │
        │ SlidingWindow │ │ Token  │  │ │   Redis Lua    │
        │  Strategy    │ │ Bucket │  │ │   Strategy     │
        │              │ │Strategy│  │ │                 │
        └──────────────┘ └────────┘  └──────────────────┘
```

## Key Components

### 1. **RateLimiterStrategy** (Abstract Base Class)
Defines the contract that all concrete strategies must implement:

```python
class RateLimiterStrategy(ABC):
    @abstractmethod
    def allow_request(self, key: str) -> bool:
        """Determine if request is allowed"""
    
    @abstractmethod
    def get_usage(self, key: str) -> Tuple[float, float]:
        """Get current usage metrics"""
    
    @abstractmethod
    def set_limit(self, key: str, max_requests: int, window_seconds: float):
        """Configure limits"""
```

**Benefits:**
- Guarantees all strategies implement required methods
- Provides clear interface for new implementations
- Enables polymorphism

### 2. **Concrete Strategies**

#### SlidingWindowStrategy
- **Algorithm**: Deque-based timestamp tracking
- **Thread Safety**: Per-key locks
- **Memory**: Medium (stores timestamps)
- **Accuracy**: Precise
- **Use Case**: Single server, strict enforcement

#### TokenBucketStrategy
- **Algorithm**: Continuous token refill
- **Thread Safety**: Built-in token bucket locks
- **Memory**: Low (only stores token count)
- **Accuracy**: Approximate (continuous refill)
- **Use Case**: High-frequency, smooth distribution

#### RedisLuaStrategy
- **Algorithm**: Redis sorted sets with atomic Lua script
- **Thread Safety**: Redis atomic operations
- **Memory**: External (Redis)
- **Accuracy**: Precise
- **Use Case**: Distributed systems, multiple servers

### 3. **RateLimiterContext** (Context Class)
Encapsulates strategy and allows runtime switching:

```python
class RateLimiterContext:
    def __init__(self, strategy: RateLimiterStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: RateLimiterStrategy):
        """Switch to different strategy"""
        self._strategy = strategy
    
    def allow_request(self, key: str) -> bool:
        return self._strategy.allow_request(key)
```

**Benefits:**
- Single point of interaction for clients
- Hides strategy details from users
- Easy to switch strategies without affecting client code

## Design Pattern Benefits

### 1. **Open/Closed Principle**
- Open for extension (add new strategies)
- Closed for modification (existing code unchanged)

### 2. **Single Responsibility**
- Each strategy handles one algorithm
- Context only delegates operations

### 3. **Dependency Inversion**
- Context depends on abstraction (RateLimiterStrategy)
- Not on concrete implementations

### 4. **Runtime Flexibility**
```python
# Switch strategies without changing client code
limiter = RateLimiterContext(SlidingWindowStrategy(...))
limiter.allow_request("user_1")

limiter.set_strategy(TokenBucketStrategy(...))
limiter.allow_request("user_1")  # Now uses different strategy
```

### 5. **Testability**
```python
# Easy to test with mock strategy
class MockStrategy(RateLimiterStrategy):
    def allow_request(self, key): return True
    
limiter = RateLimiterContext(MockStrategy())
```

## File Organization

```
strategy_pattern_rate_limiters/
│
├── rate_limiter_strategy.py      # Abstract base class (Strategy interface)
├── rate_limiter_context.py       # Context class
├── sliding_window_strategy.py    # Concrete Strategy 1
├── token_bucket_strategy.py      # Concrete Strategy 2
├── redis_lua_strategy.py         # Concrete Strategy 3
│
├── demo.py                        # Quick demonstration
├── examples.py                    # Comprehensive examples
├── __init__.py                   # Package exports
│
└── README.md                     # Documentation
```

## Usage Flow

```
1. Create a Strategy
   ├── SlidingWindowStrategy(max_requests=5, window_seconds=10)
   ├── TokenBucketStrategy(max_requests=5, window_seconds=10)
   └── RedisLuaStrategy(redis_client, prefix, max_requests, window_seconds)

2. Create Context with Strategy
   └── RateLimiterContext(strategy)

3. Use Context (operations delegated to strategy)
   ├── limiter.allow_request(key)
   ├── limiter.get_usage(key)
   └── limiter.set_limit(key, max_requests, window_seconds)

4. (Optional) Switch Strategy at Runtime
   └── limiter.set_strategy(new_strategy)
```

## Extending the Pattern

To add a new rate limiting algorithm:

1. Create new class inheriting from `RateLimiterStrategy`
2. Implement three required methods
3. Use with existing `RateLimiterContext`

```python
from rate_limiter_strategy import RateLimiterStrategy

class MyCustomStrategy(RateLimiterStrategy):
    def __init__(self, ...):
        # Initialize
        pass
    
    def allow_request(self, key: str) -> bool:
        # Your algorithm
        pass
    
    def get_usage(self, key: str) -> tuple[float, float]:
        # Your metrics
        pass
    
    def set_limit(self, key: str, max_requests: int, window_seconds: float):
        # Your configuration
        pass

# Use it immediately
limiter = RateLimiterContext(MyCustomStrategy(...))
```

## Comparison with Other Patterns

### Strategy vs Factory Pattern
- **Strategy**: Choose implementation at runtime
- **Factory**: Create objects of different types

### Strategy vs Decorator Pattern
- **Strategy**: Replace entire behavior
- **Decorator**: Add behavior to existing

### Strategy vs State Pattern
- **Strategy**: Client chooses behavior
- **State**: Object state determines behavior

## Performance Characteristics

| Strategy | Time Complexity | Space Complexity | Best Case |
|----------|-----------------|-----------------|-----------|
| Sliding Window | O(n) cleanup | O(n) requests | Few requests |
| Token Bucket | O(1) | O(1) | High frequency |
| Redis Lua | O(log n) | External | Distributed |

## When to Use Strategy Pattern

✓ Multiple algorithms for a task
✓ Need to switch algorithms at runtime
✓ Avoid large conditional statements
✓ Each algorithm is independent
✓ Clients don't care which algorithm is used

✗ Few algorithms (use factory pattern instead)
✗ Algorithms rarely change (use polymorphism directly)
✗ Simple conditional logic (use if/else)

## Real-World Applications

1. **API Rate Limiting** - Choose based on use case
2. **Payment Processing** - Different payment methods
3. **Sorting** - QuickSort, MergeSort, HeapSort
4. **Compression** - GZIP, LZ4, BROTLI
5. **Authentication** - JWT, OAuth, Session-based
6. **Caching** - LRU, LFU, FIFO strategies
