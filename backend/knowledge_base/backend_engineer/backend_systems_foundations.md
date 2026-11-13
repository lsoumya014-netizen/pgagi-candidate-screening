# Role: Backend Engineer (Python / Distributed Systems / Cloud)
# Source Corpus: System Design & Enterprise Backend Architecture Standards

## Module 1: High-Performance API Architecture & Asynchronous I/O
Modern backend architectures rely on non-blocking event-driven frameworks for handling concurrent I/O:
- Asynchronous Python (FastAPI / ASGI / Starlette):
  - Utilizes Python's `asyncio` event loop running on top of epoll/kqueue.
  - Coroutines with `async` / `await` yield execution during network/disk I/O, allowing a single thread to handle thousands of concurrent client connections without context-switch overhead.
  - Concurrency vs Parallelism: CPU-bound tasks require multi-processing (`ProcessPoolExecutor`) to bypass Python's Global Interpreter Lock (GIL), while I/O-bound tasks leverage asynchronous coroutines or thread pools.
- API Paradigms:
  - RESTful HTTP: Stateless, standard verbs (GET, POST, PUT, PATCH, DELETE), idempotent operations, and HTTP status codes.
  - GraphQL: Client-specified queries preventing over-fetching and under-fetching, resolved via hierarchical field resolvers.
  - gRPC / Protocol Buffers: High-throughput binary serialization over HTTP/2 with bi-directional streaming and strict typed schemas.

## Module 2: Relational Databases, Indexing, and ACID Transactions
Relational databases (PostgreSQL, MySQL, SQLite) ensure ACID guarantees:
- Atomicity: All operations in a transaction succeed or all roll back (WAL - Write-Ahead Logging).
- Consistency: State transitions preserve all schema constraints, foreign keys, and triggers.
- Isolation: Multi-Version Concurrency Control (MVCC) prevents dirty reads, non-repeatable reads, and phantom reads across isolation levels (Read Committed, Repeatable Read, Serializable).
- Durability: Committed transactions persist even in power failures via fsync to disk logs.
Indexing Internals:
- B+ Trees: Balanced tree structures with high branching factors (fan-out) minimizing disk I/O. Leaf nodes form a doubly linked list enabling efficient range scans.
- Composite Indexes & Leftmost Prefix Rule: An index on `(user_id, created_at)` accelerates queries filtering by `user_id` or both, but not queries filtering only by `created_at`.
- Query Optimization: Using `EXPLAIN ANALYZE` to eliminate sequential table scans and optimize nested loop vs hash joins.

## Module 3: Distributed Caching, Rate Limiting, & Resiliency
High-scale applications protect persistent stores using caching layers:
- Redis / Memcached In-Memory Stores:
  - Cache Invalidation Strategies: Cache-Aside (Lazy Loading), Write-Through, Write-Behind (Write-Back).
  - Cache Pitfalls:
    - Cache Stampede / Thundering Herd: Handled via mutex locking or probabilistic early expiration.
    - Cache Penetration: Handled via Bloom filters or caching null results.
- Rate Limiting Algorithms:
  - Token Bucket & Leaky Bucket: Smooths bursty traffic and enforces steady departure rates.
  - Sliding Window Log & Sliding Window Counter: Prevents boundary burst abuses.
- Fault Tolerance & Distributed Resiliency:
  - Circuit Breakers (Closed, Open, Half-Open states) to prevent cascading microservice outages.
  - Idempotency Keys (UUIDs in Redis/DB) to prevent double-charging or duplicate resource creation on network retries.

## Module 4: Message Queues & Event-Driven Decoupling
Asynchronous job processing decouples client request-response cycles:
- Task Queues (Celery, RQ, ARQ): Background dispatch of heavy tasks (e.g., PDF generation, ML inference, email dispatch).
- Message Brokers (RabbitMQ vs Apache Kafka):
  - RabbitMQ: AMQP broker with topic/direct exchanges and smart routing with message acknowledgments.
  - Kafka: Distributed append-only commit log partitioned for massive parallel consumer throughput, supporting exactly-once and at-least-once processing semantics.
