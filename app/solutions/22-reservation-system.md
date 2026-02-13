# Design a Hotel/Restaurant Reservation System

> **Companies**: Airbnb, Booking.com, Uber (Eats), DoorDash, OpenTable, Expedia, Google (Travel) | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Distributed locking for double-booking prevention, exactly-once reservation semantics, optimistic vs pessimistic concurrency control, how to handle inventory that's shared across multiple channels, idempotency in payment flows

---

## The First 5 Minutes — Scoping & Technical Clarifications

1. **What type of inventory?** Hotel rooms (date-range booking, one guest at a time) vs restaurant tables (time-slot booking, same table reusable across slots). This fundamentally changes the data model.
2. **Booking flow steps?** Search -> select -> hold -> confirm -> pay. Where are the race conditions? The hold-to-confirm window is where double-booking happens.
3. **Concurrency level?** How many simultaneous attempts to book the same room/table? Flash sales (thousands) vs normal traffic (tens).
4. **Multi-channel inventory?** Is the same room listed on Booking.com, Expedia, AND the hotel's own site? How do we prevent cross-channel overbooking?
5. **Cancellation and modification?** What's the cancellation policy? Do we need to handle overbooking (like airlines) intentionally?
6. **Payment integration?** Two-phase (authorize then capture) or single-phase? What if payment fails after reservation is confirmed?
7. **Consistency vs availability trade-off?** Is it acceptable to occasionally show rooms as available that aren't (eventual consistency), or must we always be accurate (strong consistency)?
8. **Scale?** How many properties, rooms per property, bookings per day?

### Working Assumptions

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Properties (hotels) | 1,000,000 | Global hotel platform |
| Rooms per property | 100 avg | 100M total rooms |
| Bookings per day | 5,000,000 | ~58 bookings/sec |
| Search QPS | 500,000 | 100:1 search:booking ratio |
| Peak concurrent booking attempts on same room | 100 | Flash sales, popular properties |
| Booking flow duration | 10 minutes | Search -> select -> pay |
| Hold timeout | 10 minutes | Soft lock on inventory |
| p99 booking confirmation latency | <500 ms | Including payment auth |
| Availability target | 99.99% | Revenue-critical system |

**Concurrency math**: 58 bookings/sec across 100M rooms = extremely low contention on average. But popular rooms during peak (New Year's Eve, major events) might see 100+ simultaneous attempts. The system must handle both the average case efficiently and the hot-spot case correctly.

---

## High-Level Design

```
         ┌────────────────┐
         │  API Gateway   │
         │  (rate limit,  │
         │   auth)        │
         └───────┬────────┘
                 │
    ┌────────────┼────────────────┐
    │            │                │
┌───▼────┐  ┌───▼──────┐  ┌─────▼──────┐
│ Search │  │ Booking  │  │ Inventory  │
│ Service│  │ Service  │  │ Service    │
│        │  │ (saga    │  │ (source of │
│(Elastic│  │  orchestr│  │  truth for │
│ Search)│  │  ator)   │  │  avail.)   │
└────────┘  └───┬──────┘  └─────┬──────┘
                │               │
         ┌──────┼───────┐       │
         │      │       │       │
    ┌────▼──┐ ┌─▼────┐ ┌▼──────▼──────┐
    │Payment│ │Notif. │ │  Inventory   │
    │Service│ │Service│ │  Database    │
    │(Stripe│ │(email,│ │ (PostgreSQL  │
    │ etc.) │ │ push) │ │  with row    │
    └───────┘ └──────┘ │  locking)    │
                        └──────────────┘
```

**Why this architecture?** The Inventory Service with its PostgreSQL database is the single source of truth for room availability. All booking operations go through this service, which uses row-level locking to prevent double-booking. Search reads from a denormalized ElasticSearch index (eventually consistent, acceptable for search — a room might show as available for a few seconds after being booked). The Booking Service orchestrates the multi-step booking flow (hold inventory -> authorize payment -> confirm booking) using the saga pattern, with compensating actions for failures.

---

## Core Concepts Deep Dive

### Concept 1: Preventing Double-Booking — The Core Problem

**What it is**: Two users attempt to book the same room for the same dates simultaneously. Without coordination, both succeed and the hotel has a double-booking. Three approaches: (1) Pessimistic locking — lock the row before reading, hold lock through the write. (2) Optimistic concurrency — read version, write with version check, retry on conflict. (3) Serializable transactions — database enforces serial execution.

**How it applies**: For a hotel room, the inventory record is `(room_id, date)`. Booking a 3-night stay requires atomically reserving 3 records: (room_id, Jan 15), (room_id, Jan 16), (room_id, Jan 17). All three must be available, or the booking fails. With pessimistic locking (SELECT FOR UPDATE), we lock all 3 rows, check availability, insert the reservation, and release locks. With optimistic concurrency, we read version numbers for all 3 rows, insert with version check, and retry if any version changed.

**The math**: At 58 bookings/sec across 100M rooms, the probability of two concurrent bookings targeting the same room-date is extremely low under normal conditions: ~(58/100M)^2 per second ≈ 3.4 x 10^-13. But for a popular hotel during a conference, 100 concurrent attempts on 200 rooms is realistic. At that contention level, pessimistic locking serializes requests (one at a time), while optimistic concurrency retries proliferate (99 out of 100 fail and retry).

**Common misconception**: "Use Redis distributed locks for performance." Redis locks are appropriate for short-lived operations, but a booking involves multiple steps (inventory check, payment, confirmation) spanning seconds. If the process crashes holding a Redis lock, the lock must expire — during that window, the room is neither booked nor available. PostgreSQL row locks with transactions are safer: if the process crashes, the transaction rolls back and the room is immediately available again.

### Concept 2: The Booking Saga — Multi-Step Orchestration

**What it is**: A booking is not a single operation — it's a saga with multiple steps that can fail independently: (1) Hold inventory, (2) Authorize payment, (3) Confirm booking, (4) Send confirmation. If payment fails after inventory is held, we must release the hold (compensating action).

**How it applies**: Two saga patterns: orchestration (a central service coordinates steps) vs choreography (each service reacts to events). For bookings, orchestration is preferred because the flow is linear and failures need deterministic compensation. The Booking Service is the orchestrator:

```
Hold Inventory -> Auth Payment -> Confirm Booking -> Notify
     |                |                |
     | (fail)         | (fail)         | (fail)
     v                v                v
  No-op         Release Hold     Release Hold +
                                 Void Payment
```

**The math**: Payment authorization takes 200-500ms (network call to payment provider). Inventory hold takes <50ms (database operation). Total saga duration: ~500-1000ms. During this time, the inventory is held (soft-locked) — other users see the room as unavailable. If we hold too long (user abandons at payment), the room is blocked for 10 minutes (hold timeout). With 5M bookings/day and 10% abandonment, 500K holds expire daily, each blocking a room for 10 minutes. That's 500K x 10 min / (100M rooms x 1440 min) = 0.035% of inventory blocked by abandoned holds at any time — acceptable.

**Common misconception**: "Just use a 2-phase commit across inventory and payment databases." 2PC across different services (especially an external payment provider) is fragile and slow. If the payment provider is unreachable during the commit phase, the entire transaction hangs. The saga pattern with compensating actions is more resilient: if payment authorization fails, we explicitly release the inventory hold. Each step is an independent transaction that either succeeds or triggers compensation.

### Concept 3: Inventory Models — Date-Range vs Time-Slot

**What it is**: Hotels book date ranges (check-in to check-out). Restaurants book time slots (7:00 PM for 90 minutes). The data model and contention patterns are fundamentally different.

**How it applies**: For hotels, the key is `(room_id, date)` — one record per room per night. A 3-night booking creates 3 records. Availability query: "find rooms available from Jan 15-18" is a range query that checks 3 dates simultaneously. For restaurants, the key is `(table_id, slot_start)` — one record per table per time slot. A reservation at 7 PM occupies slots 7:00, 7:30 (if using 30-min slots for 90-min service). The restaurant model is higher contention: a popular restaurant with 20 tables and 30-min slots has only 20 bookable entities per slot vs a hotel with thousands of rooms per night.

**The math**: Hotel: 100 rooms x 365 nights = 36,500 inventory records per property. Restaurant: 20 tables x 48 slots/day (30-min slots for 24 hours) = 960 records per day. But restaurant contention is much higher: prime-time dinner (6-9 PM) = 6 slots x 20 tables = 120 records, with potentially 50+ concurrent attempts.

**Common misconception**: "Model room availability as a count rather than individual records." Counting ("3 rooms of type King available on Jan 15") is fine for search, but booking needs specific room assignment for operational reasons (housekeeping, maintenance, room preferences). The count model can oversell: if 3 kings are available but one is under maintenance, the count says 3 but only 2 are bookable. Individual room tracking prevents this.

### Concept 4: Idempotent Booking Operations

**What it is**: Network failures mean the client might retry a booking request. Without idempotency, a retry could create a duplicate booking and charge the customer twice.

**How it applies**: Every booking request includes an `idempotency_key` (client-generated UUID). The Booking Service checks if this key has been processed: if yes, return the previous result. If no, process the request and store the result keyed by `idempotency_key`. The check-and-process must be atomic (within a database transaction) to prevent race conditions where two retries process simultaneously.

**The math**: With a 10-minute idempotency window and 58 bookings/sec, we store ~35K idempotency keys in memory. At ~100 bytes per key, that's 3.5 MB — trivial.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: Double-Booking Prevention Under Concurrency

**Interviewer**: "Two users simultaneously try to book the same hotel room for January 15-17. Walk me through exactly how you prevent double-booking."

**You**: Both requests arrive at the Booking Service. Each initiates a transaction against the Inventory Database. The inventory table has one row per room-date:

```sql
-- User A and User B both try to book room 42 for Jan 15-17
-- User A's transaction:
BEGIN;
SELECT id, status FROM room_inventory
WHERE room_id = 42 AND date IN ('2024-01-15', '2024-01-16', '2024-01-17')
FOR UPDATE;  -- acquires row-level exclusive locks
-- Returns 3 rows, all status='available'
UPDATE room_inventory SET status='held', booking_id='A123', hold_expires=now()+interval'10 min'
WHERE room_id = 42 AND date IN ('2024-01-15', '2024-01-16', '2024-01-17');
COMMIT;

-- User B's transaction (runs concurrently):
BEGIN;
SELECT id, status FROM room_inventory
WHERE room_id = 42 AND date IN ('2024-01-15', '2024-01-16', '2024-01-17')
FOR UPDATE;  -- BLOCKS here until User A's transaction commits or rolls back
-- After User A commits, User B's SELECT returns status='held'
-- User B sees room is not available, returns "room unavailable" to client
ROLLBACK;
```

The `SELECT FOR UPDATE` acquires row-level exclusive locks. User B's transaction blocks on the lock until User A's transaction completes. PostgreSQL's MVCC ensures User B sees the committed state after the lock is released. There's no possibility of both seeing "available" and both writing "held" — the lock serializes access.

**Interviewer**: "What if User A's process crashes after acquiring the lock but before committing?"

**You**: PostgreSQL automatically detects the dead connection (via TCP keepalive or statement timeout) and rolls back the transaction. The row locks are released, and the room returns to "available" status. User B's blocked transaction then acquires the lock and proceeds. The key: PostgreSQL row locks are tied to the transaction, not the application process. Transaction rollback = lock release. We also set a `statement_timeout` (e.g., 5 seconds) to prevent indefinite lock holding, and `idle_in_transaction_session_timeout` to kill sessions that hold transactions open too long.

**Interviewer**: "This doesn't scale — what if you have 100 concurrent attempts on the same room? They all serialize."

**You**: Correct — pessimistic locking serializes access, so 100 concurrent attempts process one at a time. Each takes ~50ms (lock + update + commit), so total throughput is 20 bookings/sec on that specific room. But only 1 succeeds — the other 99 fail immediately after acquiring the lock (room already held). So the actual delay is: the first user takes 50ms, the 100th user waits 5 seconds. For normal traffic this is fine. For flash sales (popular room drops price), two optimizations: (1) Optimistic concurrency instead of pessimistic: use a version column. All 100 users read the current version, try to write with version check. One succeeds, 99 retry (and find it unavailable). This is O(1) database round-trips per user instead of serialized waits. (2) Queue the requests: put booking attempts in a queue, process sequentially, immediately notify users of success/failure. First-come-first-served, no lock contention.

**Interviewer**: "How does optimistic concurrency work here specifically? Show me the SQL."

**You**:
```sql
-- Each room_inventory row has a version column
-- User A reads:
SELECT version, status FROM room_inventory
WHERE room_id = 42 AND date = '2024-01-15';
-- Returns version=7, status='available'

-- User A writes (no FOR UPDATE, no lock):
UPDATE room_inventory
SET status='held', booking_id='A123', version=version+1,
    hold_expires=now()+interval'10 min'
WHERE room_id = 42 AND date = '2024-01-15'
  AND version = 7 AND status = 'available';

-- If 1 row updated: success
-- If 0 rows updated: someone else modified it first, retry or fail
```

The `AND version = 7` is the optimistic lock. If another transaction changed the version between our read and write, our update matches 0 rows. No blocking, no waiting. The trade-off: under high contention, many retries waste CPU. Under low contention (the 99.9% case for hotel rooms), it's faster than pessimistic locking because there's no lock acquisition overhead.

### Deep Dive Path 2: Multi-Channel Inventory Synchronization

**Interviewer**: "The same hotel room is listed on Booking.com, Expedia, and the hotel's own website. How do you prevent overbooking across channels?"

**You**: This is the channel manager problem. Three approaches: (1) **Central inventory pool**: All channels read from and write to a single inventory system (ours). We're the source of truth. Each channel is a tenant in our system. (2) **Allocated inventory**: Split available rooms across channels. Booking.com gets 30 rooms, Expedia gets 30, direct gets 40. Simple but suboptimal — if Booking.com sells out but Expedia has vacancy, rooms go unsold. (3) **Shared pool with last-room availability**: All channels share the full pool, but when availability drops below a threshold (e.g., 3 rooms left), a centralized lock coordinator serializes booking attempts across channels. This is the approach used by most modern channel managers.

**Interviewer**: "Walk me through approach 3 in detail. How does the lock coordinator work?"

**You**: The inventory service maintains a counter per room type per date. When availability is above threshold (say, 5+ rooms), channels book independently — the risk of double-booking is low because there's buffer. When availability drops below 5, the inventory service switches to "last-room mode": booking requests from any channel must acquire a global lock (distributed lock via Redis or ZooKeeper) before proceeding. The lock ensures serialized access to the scarce inventory.

Implementation: the inventory service publishes availability counts to each channel's API. When a channel receives a booking, it calls our central `POST /bookings` API. The API checks current availability: if > threshold, process normally (optimistic concurrency). If <= threshold, acquire distributed lock, re-check availability, process, release lock. The distributed lock has a 5-second TTL to prevent deadlocks if the service crashes.

The math: 1M properties with 100 rooms each. At any time, maybe 1% of room-dates are in "last-room" mode. That's 10K room-dates using the distributed lock path. At 58 bookings/sec, maybe 0.58 bookings/sec hit the locked path — easily handled by a single Redis instance.

**Interviewer**: "What about the case where a channel confirms a booking to the guest but the central system rejects it?"

**You**: This is the fundamental problem of distributed inventory. Two strategies: (1) **Synchronous**: Channel calls our API before confirming to the guest. Guest sees a loading spinner for 200-500ms. If our API rejects, the channel shows "room no longer available." No overbooking, but worse UX (added latency). (2) **Asynchronous with overbooking handling**: Channel confirms immediately based on cached availability, then sends the booking to our system. If our system rejects (sold out), the channel must notify the guest of the cancellation and offer alternatives. This is how airlines work — they intentionally overbook by 5-10% and handle conflicts at check-in. Hotels can do the same: if overbooked, offer a room upgrade or alternative property. The choice depends on business requirements: synchronous is safer but slower; asynchronous is faster but requires overbooking resolution processes.

### Deep Dive Path 3: Payment Saga and Failure Handling

**Interviewer**: "The user selects a room, you hold inventory, then call the payment provider to authorize. The payment provider times out. What do you do?"

**You**: This is the classic saga failure scenario. Our state machine is: `HOLD_INVENTORY -> AUTHORIZE_PAYMENT -> CONFIRM_BOOKING`. Payment timeout means we don't know if the authorization succeeded or not. We must handle the ambiguity. Step 1: Retry the authorization with the same `idempotency_key`. Payment providers (Stripe, Adyen) support idempotent requests — retrying with the same key returns the previous result if it already succeeded. Step 2: If retries exhaust (3 attempts over 15 seconds), check the payment provider's status API: `GET /authorizations/{id}`. Three possible states: (a) authorized — proceed to confirm, (b) failed — release inventory hold, (c) not found — the authorization was never processed, safe to release hold and ask user to retry.

**Interviewer**: "What if your service crashes between authorizing payment and confirming the booking? The hold exists, the payment is authorized, but no booking record."

**You**: This is why we need a durable saga state machine. Before each step, we write the saga state to a `booking_sagas` table:

```sql
INSERT INTO booking_sagas (booking_id, step, status, idempotency_key, created_at)
VALUES ('B123', 'AUTHORIZE_PAYMENT', 'COMPLETED', 'idem-456', now());
```

On crash recovery, a background worker scans for incomplete sagas (last step != COMPLETED or COMPENSATED) and resumes or compensates. If the saga shows `AUTHORIZE_PAYMENT = COMPLETED` but `CONFIRM_BOOKING = PENDING`, the worker retries the confirmation step. If `HOLD_INVENTORY = COMPLETED` but `AUTHORIZE_PAYMENT = FAILED`, the worker releases the hold. The saga table is the recovery log — it guarantees that every booking either completes fully or is fully compensated, even across crashes.

**Interviewer**: "How do you handle the hold timeout? If the user abandons, the hold sits for 10 minutes."

**You**: A scheduled job runs every minute, scanning for expired holds: `SELECT * FROM room_inventory WHERE status='held' AND hold_expires < now()`. For each expired hold, it releases the inventory (status -> available) and checks if there's an associated payment authorization — if so, it voids the authorization. We also proactively notify the user's session via WebSocket: "Your hold will expire in 2 minutes." The 10-minute timeout is a business decision balancing user experience (enough time to enter payment info) vs inventory lock-up (shorter timeout means more available inventory). Some systems use a two-tier approach: 5-minute soft hold (inventory appears taken in search but isn't locked) + 10-minute hard hold (after payment form loads).

**Interviewer**: "What about partial failure in a multi-room booking? User books 3 rooms but only 2 are available."

**You**: Atomic multi-item booking: either all rooms are booked or none. The inventory check and hold for all 3 rooms must happen in a single database transaction. If any room is unavailable, the entire transaction rolls back. We never partially hold inventory — that creates a confusing state where the user has some rooms but not others. The SQL:

```sql
BEGIN;
UPDATE room_inventory SET status='held', booking_id='B123'
WHERE room_id IN (42, 43, 44)
  AND date BETWEEN '2024-01-15' AND '2024-01-17'
  AND status = 'available';
-- Check that we updated exactly 9 rows (3 rooms x 3 nights)
-- If fewer, ROLLBACK and return "not all rooms available"
COMMIT;
```

If the UPDATE affects fewer than 9 rows, we know at least one room-date wasn't available. Rollback, and return the specific unavailable rooms to the user so they can choose alternatives.

---

## How Real Companies Built This

- **Airbnb**: Uses a centralized availability service backed by MySQL with sharding by listing_id. Holds implemented as time-limited reservations with background cleanup. [Airbnb Engineering — Avoiding Double Payments](https://medium.com/airbnb-engineering/avoiding-double-payments-in-a-distributed-payments-system-2981f6b070bb)
- **Booking.com**: Uses allocated + shared inventory model for channel management. Custom availability engine handling 1M+ properties. [Booking.com at Scale](https://www.youtube.com/watch?v=bY0y3CzNMn0)
- **Uber (Eats)**: Restaurant availability is real-time (kitchen capacity, wait times). Uses a combination of menu availability + order queue depth for admission control. [Uber Engineering Blog](https://www.uber.com/blog/engineering/)
- **OpenTable**: Pioneered online restaurant reservations. Uses time-slot-based inventory with party-size optimization (seat 2 people at a 2-top, not a 4-top). Real-time availability sync across channels.
- **Stripe**: Payment authorization/capture pattern used by booking platforms. Idempotency keys prevent duplicate charges. [Stripe — Idempotent Requests](https://stripe.com/docs/api/idempotent_requests)

---

## The Complete Reference Design

### API Design

```
# Search availability
GET /v1/availability?location=NYC&checkin=2024-01-15&checkout=2024-01-18&guests=2&rooms=1
# Response: list of available properties with room types, prices, availability counts

# Hold inventory (start booking flow)
POST /v1/bookings/hold
{
  "idempotency_key": "uuid-v4",
  "property_id": "prop-123",
  "room_type": "king",
  "checkin": "2024-01-15",
  "checkout": "2024-01-18",
  "guests": 2
}
# Response: { "hold_id": "hold-456", "expires_at": "2024-01-14T10:15:00Z", "price": {...} }

# Confirm booking (with payment)
POST /v1/bookings/confirm
{
  "idempotency_key": "uuid-v4",
  "hold_id": "hold-456",
  "payment_method": "pm_stripe_abc",
  "guest_info": { "name": "...", "email": "...", "phone": "..." }
}
# Response: { "booking_id": "BK-789", "status": "confirmed", "confirmation_code": "ABC123" }

# Cancel booking
POST /v1/bookings/{booking_id}/cancel
{
  "idempotency_key": "uuid-v4",
  "reason": "change_of_plans"
}
# Response: { "refund_amount": 250.00, "refund_status": "processing" }
```

### Database Schema

```sql
CREATE TABLE properties (
    id           UUID PRIMARY KEY,
    name         VARCHAR(256) NOT NULL,
    location     GEOGRAPHY(Point) NOT NULL,
    timezone     VARCHAR(64) NOT NULL,
    total_rooms  INT NOT NULL
);

CREATE TABLE room_types (
    id           UUID PRIMARY KEY,
    property_id  UUID NOT NULL REFERENCES properties(id),
    name         VARCHAR(64) NOT NULL,       -- king, queen, suite
    capacity     INT NOT NULL,
    base_price   DECIMAL(10,2) NOT NULL,
    total_count  INT NOT NULL                -- how many rooms of this type
);

-- One row per room per date — the core inventory table
CREATE TABLE room_inventory (
    room_type_id  UUID NOT NULL REFERENCES room_types(id),
    date          DATE NOT NULL,
    available     INT NOT NULL,              -- available count for this type+date
    held          INT NOT NULL DEFAULT 0,    -- currently held (soft-locked)
    booked        INT NOT NULL DEFAULT 0,    -- confirmed bookings
    version       INT NOT NULL DEFAULT 0,    -- optimistic concurrency
    PRIMARY KEY (room_type_id, date)
);

CREATE TABLE bookings (
    id               UUID PRIMARY KEY,
    property_id      UUID NOT NULL,
    room_type_id     UUID NOT NULL,
    checkin          DATE NOT NULL,
    checkout         DATE NOT NULL,
    guest_name       VARCHAR(256) NOT NULL,
    guest_email      VARCHAR(256) NOT NULL,
    status           VARCHAR(16) NOT NULL,    -- held, confirmed, cancelled, completed
    total_price      DECIMAL(10,2) NOT NULL,
    payment_intent_id VARCHAR(256),
    idempotency_key  UUID NOT NULL UNIQUE,
    hold_expires_at  TIMESTAMP,
    created_at       TIMESTAMP NOT NULL,
    updated_at       TIMESTAMP NOT NULL
);
CREATE INDEX idx_bookings_property ON bookings(property_id, checkin);
CREATE INDEX idx_bookings_status ON bookings(status) WHERE status = 'held';

-- Saga state for crash recovery
CREATE TABLE booking_sagas (
    booking_id   UUID NOT NULL REFERENCES bookings(id),
    step         VARCHAR(32) NOT NULL,
    status       VARCHAR(16) NOT NULL,    -- pending, completed, failed, compensating
    idempotency_key UUID NOT NULL,
    payload      JSONB,
    created_at   TIMESTAMP NOT NULL,
    PRIMARY KEY (booking_id, step)
);
```

### Key Algorithms — Optimistic Concurrency Booking

```python
import uuid
from datetime import date, timedelta
from typing import Optional

class BookingService:
    MAX_RETRIES = 3

    def hold_inventory(
        self,
        room_type_id: str,
        checkin: date,
        checkout: date,
        idempotency_key: str,
    ) -> Optional[str]:
        """Attempt to hold rooms with optimistic concurrency."""
        dates = [checkin + timedelta(days=i)
                 for i in range((checkout - checkin).days)]

        for attempt in range(self.MAX_RETRIES):
            # Read current state
            rows = self.db.execute(
                "SELECT date, available, held, version FROM room_inventory "
                "WHERE room_type_id = %s AND date = ANY(%s)",
                (room_type_id, dates)
            )

            if len(rows) != len(dates):
                return None  # missing dates

            # Check availability
            if any(r.available - r.held - r.booked <= 0 for r in rows):
                return None  # not available

            # Attempt optimistic update
            booking_id = str(uuid.uuid4())
            updated = 0
            for row in rows:
                result = self.db.execute(
                    "UPDATE room_inventory SET held = held + 1, version = version + 1 "
                    "WHERE room_type_id = %s AND date = %s "
                    "AND version = %s AND (available - held - booked) > 0",
                    (room_type_id, row.date, row.version)
                )
                if result.rowcount == 1:
                    updated += 1
                else:
                    # Version conflict — rollback partial updates
                    self.db.execute(
                        "UPDATE room_inventory SET held = held - 1, version = version + 1 "
                        "WHERE room_type_id = %s AND date = ANY(%s) "
                        "AND version > %s",  # only rollback rows we updated
                        (room_type_id, dates[:updated], rows[0].version)
                    )
                    break  # retry

            if updated == len(dates):
                # All dates held successfully
                self.db.execute(
                    "INSERT INTO bookings (id, room_type_id, checkin, checkout, "
                    "status, idempotency_key, hold_expires_at) "
                    "VALUES (%s, %s, %s, %s, 'held', %s, now() + interval '10 min')",
                    (booking_id, room_type_id, checkin, checkout, idempotency_key)
                )
                return booking_id

        return None  # all retries exhausted
```

### Capacity Planning

| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Inventory DB | 100M rooms x 365 days x 50B/row = 1.8 TB | PostgreSQL cluster, 3 replicas |
| Bookings DB | 5M/day x 1KB x 365 = 1.8 TB/year | Sharded by property_id |
| Search index | 1M properties x 10KB = 10 GB | ElasticSearch, 3 nodes |
| Booking QPS | 58/sec avg, 500/sec peak | 3 booking service instances |
| Search QPS | 500K/sec | 20 search service instances + ES caching |
| Hold cleanup | 500K expired holds/day / 1440 min = 347/min | 1 background worker |
| Saga recovery | ~0.1% failed sagas = 5K/day | 1 background worker |

---

## Senior vs Staff vs Principal

| Aspect | Senior (E5/L5) | Staff (E6/L6) | Principal (L66+) |
|--------|----------------|----------------|-------------------|
| **Concurrency** | Uses SELECT FOR UPDATE, prevents double-booking | Compares pessimistic vs optimistic locking with math, designs version-based concurrency | Designs multi-channel inventory with distributed coordination, handles cross-datacenter booking |
| **Payment** | Mentions payment integration | Designs the booking saga with compensating actions, handles payment timeouts | Designs idempotent payment flows with audit trails, handles split payments and refund cascades |
| **Scale** | Correct schema for single-region | Sharding strategy (by property_id), read replicas for search, cache invalidation | Designs global inventory system with regional write affinity and cross-region consistency |
| **Operations** | Mentions monitoring | Designs hold cleanup, saga recovery workers, overbooking detection alerts | Designs revenue reconciliation system, A/B tests on hold timeout duration, yield management integration |

---

## Red Flags & Common Mistakes

1. **No double-booking prevention** — "Just check availability and book." Without locking or versioning, two concurrent requests both see "available" and both book.
2. **Distributed lock for everything** — Redis locks for the normal case is over-engineering. Database row locks handle 99.9% of cases. Reserve distributed locks for cross-channel coordination.
3. **No saga for the booking flow** — Treating hold + payment + confirm as a single atomic operation. Payment providers are external — you can't wrap them in a database transaction.
4. **Ignoring idempotency** — Network retries will duplicate booking requests. Without idempotency keys, the customer gets charged twice.
5. **Eventual consistency for inventory** — Search can be eventually consistent, but the booking path MUST be strongly consistent. Showing "available" in search but rejecting at booking is acceptable; confirming two bookings for the same room is not.
6. **No hold timeout** — Holding inventory indefinitely while the user enters payment info. Users abandon carts — those rooms must become available again.
7. **Count-based inventory only** — "50 rooms available" doesn't tell you which specific rooms. You need room-level tracking for operations (housekeeping, maintenance, guest preferences).
