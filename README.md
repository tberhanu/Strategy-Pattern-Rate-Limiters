# Rate Limiter

## Why
- Prevent DoS (Denial of Service) attacks
- Reduce cost (especially for paid 3rd‑party APIs)
- Reduce server load

## Basics
- **Client Side or Server Side?** → Server Side  
- **Implemented on Server Side or in a Gateway?** → Design decision  
- **Throttling based on what?** → user id, IP address, …  
- **Scaling System?** → startup vs. large user base  
- **Distributed environment?** → Yes  
- **Inform throttled user?** → Yes  

## Algorithms
- Fixed window  
- Sliding window  
- Token bucket  

## High-Level Design (HLD)

### Performance
Rate limiter adds an extra layer on top of the existing system, so it must be **fast**.

### System Overview
We have:
- **USER**
- **COUNTER** (tracks per-user usage)

### Counter Storage
- DB is too slow  
- Use **in-memory cache** (fast + TTL support)  
- Example Redis commands:
  - `INCR`
  - `EXPIRE`

### Rules
- Stored in **cache + original DB**
- Often saved in configuration files on disk

### Handling Rate-Limited Users
- Return **HTTP 429**
- For successful requests, include headers:
  - hits already used
  - hits remaining

### Handling Rejected Requests
- Drop the request  
- Or push to a **queue** for later processing (important for ordering/purchasing flows)

## Distributed Environment

### Challenges
- **Race conditions**
- **Synchronization issues**

### Race Condition
Occurs when multiple threads access/modify shared resources simultaneously.

### Synchronization Issues
Example:  
A user hits different servers without cookies or sticky sessions, so the load balancer does not route them consistently.

## Why Cookies & Sticky Sessions Are Avoided
They:
- Break scalability  
- Reduce flexibility  
- Reduce resilience  
- Tie users to a specific server  

Better approach:  
Use **centralized data stores** (e.g., Redis) for session-like data.

## Race Condition Solutions

### 1. Locks
Work but slow down the system.

### 2. Redis-Based Solutions
#### Sorted Sets (ZSETs)
- Good for single commands  
- Redis is single-threaded → atomic operations

#### Lua Scripts
- Useful when multiple commands must run atomically  
- Acts like an implicit lock without overhead  
- Note: Redis < 128GB may require **sharding**

## Distributed System Summary
- Multiple rate limiter servers (leader + followers)  
- Each rate limiter connects to a Redis replica via load balancer  
- Each rate limiter connects to API servers via load balancer  

## Monitoring & Observability
- Each rate limiter pushes data to the monitoring tool
