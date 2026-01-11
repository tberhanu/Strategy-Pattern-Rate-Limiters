🚦 Rate Limiter
Why Use a Rate Limiter?

Prevent DoS (Denial of Service) attacks

Reduce costs (especially for paid 3rd-party APIs)

Reduce server load

Basics

Client Side or Server Side?
→ Server Side

Implemented on Server or Gateway?
→ Design decision (depends on architecture)

Throttling Based On?

User ID

IP Address

API Key

Other identifiers

Scaling Considerations?

Startup-scale systems

Large companies with massive user bases

Distributed Environment Support?
→ Yes

Inform Throttled Users? (Exception Handling)
→ Yes

Algorithms

Common rate-limiting algorithms:

Fixed Window

Sliding Window

Token Bucket

High-Level Design (HLD)

Rate Limiter adds an extra layer on top of the existing system, so it must be extremely fast

Basic model:

User

Counter (tracks requests per user)

Where to Store the Counter?

❌ Database → Too slow

✅ In-Memory Cache → Fast and supports time-based expiry

Example (Redis):

INCR

EXPIRE

Rule Management

Where are rules created and stored?

Cache + Original DB (recommended)

Rules are usually:

Stored in configuration files

Persisted on disk

Handling Rate-Limited Users

Return HTTP 429 (Too Many Requests)

Include useful headers in successful (200 OK) responses:

Requests already used

Requests remaining

Reset time

Handling Rejected Requests

Two approaches:

Drop the request

Push to a Queue

Useful for critical operations like ordering or payments

Distributed Environment Challenges
Single Server

Easy to implement

Multiple Servers & Concurrent Threads

Additional challenges:

Race Conditions

Synchronization Issues

Race Condition

Occurs when:

Multiple threads access and modify shared resources simultaneously

Synchronization Issues

Example:

A user (e.g., with a shopping cart) hits different servers

No cookies or sticky sessions

Load Balancer does not route user to the same server

Why Cookies & Sticky Sessions Are Often Avoided?

They:

Break scalability

Reduce flexibility

Hurt resilience

Sticky sessions:

Tie users to specific servers

Make scaling, deployments, and traffic rerouting harder

Better Solution

Centralized data stores (e.g., Redis)

Store session/state data centrally instead of on individual servers

Race Condition Solutions
Option 1: Locks

Works but slows down the system

Option 2: Redis-Based Solutions
1. Sorted Sets (ZSETs)

Redis is single-threaded

Single commands are atomic

2. Lua Scripts

Handle multiple commands atomically

Acts as an implicit lock

No overhead of distributed locks

⚠️ Note: Redis has a memory limit (≈128GB), so sharded Redis may be required.

Distributed System Summary

Multiple Rate Limiter Servers (Leader + Followers)

Each Rate Limiter:

Connects to a Redis replica via Load Balancer

Connects to API Servers via Load Balancer

Monitoring & Observability

Each Rate Limiter pushes metrics to a Monitoring Tool

Useful for:

Traffic analysis

Alerting

Capacity planning
