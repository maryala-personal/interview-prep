# Design a Ride-Sharing Service

> **Companies**: Uber (very common), Lyft, Google, Amazon, Microsoft, DoorDash | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you design a real-time geospatial matching system, reason about location indexing (geohashing, quad-trees), handle the concurrency challenges of ride matching (two riders can't get the same driver), and think through the end-to-end lifecycle of a ride from request to payment? This problem tests your understanding of spatial data structures, real-time systems, and state machines.

---

## The First 5 Minutes — Scoping & Technical Clarifications

**These are the questions that make the interviewer think "this person knows what they're doing."**

- "What's the core flow I should focus on? Rider requests ride → match with driver → trip in progress → payment? Or are we also designing the driver onboarding, surge pricing, etc.?"
- "What's the matching latency SLA? Time from ride request to driver assignment — under 10 seconds?"
- "How many concurrent drivers and riders? This determines the spatial indexing strategy."
- "What's the location update frequency? Drivers sending GPS every 3 seconds? That's a high-throughput write workload."
- "What's the matching radius? Look for drivers within 3 km, 5 km? Does it expand if no drivers are found?"
- "Do we need to handle ride types (UberX, UberXL, UberBlack)? This adds filtering to the matching."
- "Single city or multi-city? Do we need cross-city routing or is each city an independent partition?"
- "What's the ETA calculation strategy? Straight-line distance, road network routing, or historical data?"

### Working Assumptions

| Parameter | Value |
|-----------|-------|
| Active drivers (online) | 1M globally, 50K per major city |
| Active riders | 5M globally |
| Ride requests | 10K/sec globally |
| Driver location updates | 1M drivers x 1 update/3 sec = 333K writes/sec |
| Matching latency | p99 < 5 seconds |
| Location update size | ~100 bytes (lat, lng, heading, speed, timestamp) |
| Matching radius | 3 km initial, expand to 5 km |
| Availability | 99.99% |

**The math**:
- 333K location writes/sec — this is the dominant write workload
- 10K matching queries/sec — each queries drivers within a geospatial radius
- Storage: location data is ephemeral (only latest position matters). Trip history: 10K trips/sec x 5 KB metadata = 50 MB/sec → ~4 TB/day
- In-memory spatial index: 1M drivers x 100 bytes = 100 MB — easily fits in RAM

---

## High-Level Design (Keep it brief — 5 minutes max)

```
┌──────────┐          ┌──────────┐
│  Rider   │          │  Driver  │
│  App     │          │  App     │
└────┬─────┘          └────┬─────┘
     │                     │
     │    REST/WebSocket   │  GPS updates every 3 sec
     │                     │
┌────▼─────────────────────▼────┐
│        API Gateway            │
└────┬──────────────────┬───────┘
     │                  │
┌────▼─────┐     ┌──────▼──────┐
│  Ride    │     │  Location   │  ← Ingests 333K GPS updates/sec
│  Service │     │  Service    │
└────┬─────┘     └──────┬──────┘
     │                  │
┌────▼─────┐     ┌──────▼──────┐
│ Matching │◄────│  Spatial    │  ← In-memory geohash/quad-tree index
│ Service  │     │  Index      │
└────┬─────┘     └─────────────┘
     │
┌────▼──────────┐    ┌──────────────┐
│  Trip State   │    │  ETA/Routing │  ← Road network graph, historical data
│  Machine      │    │  Service     │
│  (DB + Kafka) │    └──────────────┘
└───────────────┘
```

**Why this architecture?** The location service is separated because it's a pure high-throughput write workload (333K writes/sec) with no transactional requirements — eventual consistency is fine for driver positions. The matching service is the brain — it queries the spatial index to find nearby available drivers and handles the race condition of assigning a single driver to a single rider. The trip state machine tracks the lifecycle of each ride with strong consistency.

---

## Core Concepts Deep Dive

### Concept 1: Geospatial Indexing — Geohash vs. Quad-Tree

**What it is**: When a rider requests a ride, we need to find all available drivers within a 3 km radius. Scanning 1M drivers for proximity is O(N) — too slow. We need a spatial index.

**How it applies here**: Two main approaches:

- **Geohash**: Encode lat/lng into a string (e.g., `9q8yyz`). Longer strings = more precision. A 6-character geohash covers ~1.2 km x 0.6 km. Drivers in the same geohash cell are nearby. To find drivers within 3 km, search the cell and its 8 neighbors.
- **Quad-tree**: Recursively divide the map into quadrants. Each leaf contains up to K drivers. Query: traverse from root, find the leaf containing the rider, then expand to nearby leaves until the radius is covered.

**The math/mechanics**:
```
Geohash precision levels:
  4 chars: ~39 km x 20 km  (too coarse)
  5 chars: ~5 km x 5 km    (good for initial radius)
  6 chars: ~1.2 km x 0.6 km (for dense areas)

For a 3 km radius search with precision 6:
  - Query the rider's cell + 8 adjacent cells = 9 cells
  - Each cell in a dense city: ~50K drivers / (city area / cell area) ≈ 50-200 drivers per cell
  - 9 cells x 100 drivers avg = 900 candidates, filter by exact distance → ~50 drivers within 3 km
```

**Common misconception**: Candidates propose a naive approach: "store lat/lng in a database and query `WHERE distance(driver, rider) < 3km`." Even with a spatial index (PostGIS), querying 1M rows for every ride request (10K/sec) will crush the database. The spatial index must be in-memory for the hot path.

### Concept 2: Ride Matching — The Concurrency Problem

**What it is**: When a ride request comes in, we find 10 nearby drivers and send the request to the "best" one. But what if two riders request at the same time and the same driver is the best match for both? We can't assign one driver to two riders.

**How it applies here**: The matching service uses optimistic locking with retry:

1. Query spatial index → get 10 nearest available drivers
2. Rank by ETA, rating, ride type match
3. Try to assign the top driver: atomic compare-and-swap on the driver's status (`available` → `assigned`). In Redis: `SET driver:d123:status assigned NX`
4. If CAS succeeds → dispatch the ride request to the driver (push notification)
5. If CAS fails → driver was just assigned to another rider. Try the next driver in the ranked list.
6. Driver has 15 seconds to accept. If declined or timeout → try the next driver.

**The math/mechanics**:
- At 10K rides/sec and 50K available drivers per city, the collision probability is low: ~10K/50K = 20% chance of two requests targeting the same driver in a given second.
- With 10 candidates per request, the retry adds < 1ms (another Redis read).
- Worst case: all 10 candidates are taken → expand the search radius and re-query.

**Common misconception**: Candidates propose a centralized matching queue (all requests go into a single queue, one matcher assigns them one-by-one). This works but creates a single-threaded bottleneck. The optimistic concurrency approach scales horizontally.

### Concept 3: Trip State Machine — Ensuring Consistency

**What it is**: A ride goes through a strict sequence of states. Each state transition must be validated and persisted atomically.

**How it applies here**:
```
REQUESTED → MATCHED → DRIVER_EN_ROUTE → ARRIVED → TRIP_IN_PROGRESS → COMPLETED → PAID
                                                                    ↘ CANCELLED
```

- State transitions are stored in a PostgreSQL table with a version column for optimistic concurrency control.
- Each transition publishes an event to Kafka for downstream consumers (analytics, billing, ETA updates, rider/driver app updates).
- Critical invariant: a ride can never be in two states simultaneously, and transitions must follow the defined paths.

**Common misconception**: Candidates store ride state as a simple `status` column and update it with `UPDATE rides SET status = 'completed' WHERE id = ?`. This has no concurrency protection — two concurrent requests could transition from different states. Use `UPDATE rides SET status = 'completed', version = version + 1 WHERE id = ? AND status = 'trip_in_progress' AND version = ?`.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: "Driver Location Updates and Spatial Indexing"

**Interviewer**: "333K location updates per second. Walk me through how a driver's GPS update flows through the system."

**You**: "The driver app sends a GPS update every 3 seconds over a persistent connection (WebSocket or MQTT). The location service receives it and does two things: (1) Update the spatial index — remove the driver from the old geohash cell and insert into the new one. This is an in-memory operation, < 0.1ms. (2) Write to a time-series store (Kafka → Cassandra) for historical tracking and analytics. The spatial index is sharded by geographic region — each city gets its own shard. A city like New York with 50K drivers has its own in-memory index on a single server (with replicas). The index is a hash map: `geohash_cell → set of driver_ids`. A driver update that moves to a new cell: `SREM geohash:old_cell driver_id; SADD geohash:new_cell driver_id` — two O(1) operations."

**Interviewer**: "What if the location service crashes? You lose the in-memory spatial index for that city."

**You**: "The index is reconstructable. On restart, the service reads the latest location for all active drivers from Redis (which is persistent): `GET driver:d123:location` for each driver. This takes a few seconds for 50K drivers. During recovery, the matching service falls back to querying Redis directly (slower but functional). For zero-downtime, I run two replicas per city shard. Both receive the same location updates (via Kafka consumer group — no, actually, both consume independently from the location update stream). If the primary dies, the replica is already hot and takes over. The load balancer health-checks the index service and routes to the healthy replica."

**Interviewer**: "Geohash has edge problems — two drivers might be 100 meters apart but in different geohash cells. How do you handle this?"

**You**: "Classic geohash boundary problem. The solution is to always search the target cell plus all 8 neighboring cells. If the rider is at the edge of cell `9q8yyz`, a driver 100 meters away in cell `9q8yyx` will be found because we search both cells. For the corner case where the rider is at the corner of 4 cells, searching 9 cells (3x3 grid) always covers the radius. The slight over-query (9 cells instead of 1) is acceptable because each cell lookup is O(1) from the hash map. After collecting candidates from all 9 cells, we compute exact Haversine distance and filter to the actual 3 km radius."

**Interviewer**: "Why not use a quad-tree instead? When would that be better?"

**You**: "Quad-trees adapt to density. In Manhattan with 500 drivers per km^2, the quad-tree subdivides more finely. In rural Kansas with 1 driver per 100 km^2, the leaves are huge. Geohash has a fixed grid — a cell in Manhattan and a cell in Kansas are the same size. With geohash, a dense Manhattan cell might have 1000 drivers, making the filter step slower. Quad-tree keeps leaf size bounded (say, max 100 drivers per leaf). The trade-off: quad-trees are harder to distribute. Geohash maps naturally to hash maps and Redis. Quad-trees need in-memory tree structures that are harder to shard. Uber's H3 (hexagonal hierarchical geospatial indexing) is a hybrid — hexagonal cells with multiple resolutions, combining the benefits of both. I'd use geohash for simplicity and switch to H3 at Uber-scale."

### Deep Dive Path 2: "Ride Matching Algorithm"

**Interviewer**: "Walk me through the matching algorithm. A rider requests a ride — what happens?"

**You**: "Step 1: The ride service publishes a 'ride requested' event. Step 2: The matching service picks it up and queries the spatial index: 'give me all available drivers within 3 km of (40.7128, -74.0060).' This returns, say, 25 drivers. Step 3: Filter by ride type (UberX only shows UberX-eligible drivers). Step 4: Rank the remaining drivers. The ranking function considers: (a) ETA — estimated time for the driver to reach the rider, based on road network distance (not straight-line). (b) Driver rating — higher-rated drivers get preference. (c) Driver's idle time — a driver waiting for 10 minutes gets boosted over one who just completed a trip. (d) Direction — a driver heading toward the rider is preferred over one heading away. Step 5: Offer the ride to the #1 ranked driver via push notification. Wait 15 seconds for acceptance."

**Interviewer**: "What if no driver is within 3 km?"

**You**: "Expand the radius. 3 km → 5 km → 8 km, querying more geohash cells each time. If still no drivers after 8 km, inform the rider that no drivers are available and offer to notify them when one becomes available. Also, this is where surge pricing kicks in — if demand exceeds supply in a geohash region, increase the price multiplier. The higher price incentivizes more drivers to that area and discourages price-sensitive riders, bringing supply and demand toward balance. The surge multiplier is calculated per geohash region based on the ratio of ride requests to available drivers, updated every 30 seconds."

**Interviewer**: "The driver has 15 seconds to accept. What if they don't? What if they accept but then cancel?"

**You**: "If the driver doesn't accept within 15 seconds (timeout) or explicitly declines, the matching service immediately offers to the #2 ranked driver. We don't re-query the spatial index unless significant time has passed (> 30 seconds, because driver positions change). The original ranked list is cached for 60 seconds. If a driver accepts but then cancels (before pickup), the trip state transitions to `CANCELLED_BY_DRIVER`. The rider is automatically re-entered into matching. The driver's cancellation rate is tracked — high cancellation rates affect their ranking in future matching and can lead to deactivation. The rider sees 'finding another driver' and the process restarts, typically faster since we already have a warm candidate list."

**Interviewer**: "How does the matching service handle 10K ride requests per second without becoming a bottleneck?"

**You**: "Partition by city. Each city has its own matching service instance (or pool of instances). New York's 10K drivers and 500 requests/sec are handled by a dedicated set of matchers. This is natural because matching is inherently local — a rider in NYC won't match with a driver in LA. Within a city, multiple matching instances can run in parallel because the optimistic locking (CAS on driver status) handles conflicts. If two matchers try to assign the same driver, one wins and the other retries with the next candidate. The spatial index for each city is replicated to all matchers in that city, so each matcher can query independently."

### Deep Dive Path 3: "Trip Lifecycle and Payment"

**Interviewer**: "Walk me through the trip from the moment the driver starts driving to payment."

**You**: "When the driver starts the trip (rider is in the car), the driver app sends a 'trip started' event. The trip state machine transitions to `TRIP_IN_PROGRESS`. During the trip, the driver app sends GPS updates every 3 seconds. The location service stores these as a trip trajectory (Kafka → Cassandra, partitioned by trip_id). This trajectory is used for route visualization, fare calculation, and dispute resolution. When the driver ends the trip, the state transitions to `COMPLETED`. The fare calculation service is triggered: it queries the trip trajectory, calculates total distance (sum of haversine distances between consecutive GPS points) and duration, applies the rate card (base fare + per-mile + per-minute + surge multiplier), and produces the final fare."

**Interviewer**: "How do you calculate the fare accurately? GPS can drift, and the driver might take a detour."

**You**: "GPS accuracy is typically 5-15 meters, which introduces noise. We apply Kalman filtering to smooth the trajectory — removing GPS jumps and interpolating gaps. For distance, we snap GPS points to the road network (map matching) using a service like OSRM or Google's Roads API. This gives us the actual road distance, not the noisy GPS distance. For detours: we compare the actual route to the optimal route (pre-calculated at ride request time). If the actual route is significantly longer (say 30%+ more), we have a policy choice: charge the optimal route distance (Uber does this) or flag for review. The pre-calculated optimal ETA and distance serve as the 'expected' fare, and the actual fare should be close."

**Interviewer**: "The payment fails after the trip is completed. How do you handle this?"

**You**: "Payment is async and retried. When the trip completes, a payment event is published to Kafka. The payment service consumes it and charges the rider's card via the payment processor (Stripe, Braintree). If the charge fails (insufficient funds, card declined), the payment service retries with exponential backoff — 1 min, 5 min, 30 min, 4 hours, 24 hours. After 3 failed attempts, the rider's account is flagged and they can't request new rides until the outstanding payment is resolved. The driver still gets paid — the platform absorbs the loss and pursues collection from the rider. This is important: driver payments are never blocked by rider payment failures. The driver payout runs on a separate payment rails (weekly direct deposit) and is calculated from completed trips regardless of rider payment status."

---

## How Real Companies Built This

- **Uber**: Uses H3 (hexagonal hierarchical spatial index) for geospatial operations. Their matching system (Marketplace) handles millions of trips/day. Key papers and blog posts: "Uber's Real-Time Marketplace" (Uber Engineering Blog), "H3: Uber's Hexagonal Hierarchical Spatial Index" (Uber Engineering Blog). Their dispatch system evolved from a simple nearest-driver model to a batched matching system that optimizes globally.
- **Lyft**: Uses a similar architecture but publicly documented their approach to ETA prediction using ML models. See: "How Lyft Predicts Your Ride's ETA" (Lyft Engineering Blog).
- **Grab (SE Asia)**: Faces unique challenges with motorcycle taxis and extreme traffic. They've published about their geospatial challenges in cities with no structured addresses.
- **Key lesson**: The matching algorithm is the competitive differentiator. A 10-second improvement in pickup ETA translates directly to user retention. Uber's matching evolved from "nearest available driver" to a global optimization that considers future demand predictions, driver earnings fairness, and rider wait time simultaneously.

---

## The Complete Reference Design

### API Design
```
POST /api/v1/rides/request
Request: {
    "rider_id": "r_12345",
    "pickup": {"lat": 40.7128, "lng": -74.0060},
    "dropoff": {"lat": 40.7580, "lng": -73.9855},
    "ride_type": "uberx",
    "payment_method_id": "pm_stripe_abc"
}
Response: {
    "ride_id": "ride_abc123",
    "status": "matching",
    "estimated_fare": {"min": 15.50, "max": 21.00, "currency": "USD"},
    "surge_multiplier": 1.2,
    "estimated_pickup_eta": 240    // seconds
}

# Driver accepts ride
POST /api/v1/rides/{ride_id}/accept
Request: {"driver_id": "d_67890"}
Response: {
    "ride_id": "ride_abc123",
    "status": "driver_en_route",
    "rider": {"name": "Alice", "rating": 4.8, "pickup": {...}},
    "eta_to_pickup": 180
}

# Driver location update (high frequency)
PUT /api/v1/drivers/{driver_id}/location
Request: {
    "lat": 40.7135,
    "lng": -74.0055,
    "heading": 45.0,
    "speed": 12.5,
    "timestamp": 1707696000123
}
Response: 204 No Content

# Trip lifecycle
POST /api/v1/rides/{ride_id}/start    // Driver starts trip
POST /api/v1/rides/{ride_id}/complete // Driver ends trip
POST /api/v1/rides/{ride_id}/cancel   // Either party cancels

GET /api/v1/rides/{ride_id}
Response: {
    "ride_id": "ride_abc123",
    "status": "completed",
    "driver": {"id": "d_67890", "name": "Bob", "rating": 4.9},
    "route": {"distance_meters": 8500, "duration_seconds": 1200},
    "fare": {"amount": 18.75, "currency": "USD", "breakdown": {
        "base": 2.50, "distance": 10.20, "time": 4.80, "surge": 1.25
    }},
    "timestamps": {
        "requested": "...", "matched": "...", "pickup": "...", "completed": "..."
    }
}
```

### Database Schema
```sql
-- PostgreSQL: Rides (trip state machine)
CREATE TABLE rides (
    ride_id         UUID PRIMARY KEY,
    rider_id        BIGINT NOT NULL,
    driver_id       BIGINT,
    status          VARCHAR(30) NOT NULL DEFAULT 'requested',
    ride_type       VARCHAR(20) NOT NULL,
    pickup_lat      DOUBLE PRECISION NOT NULL,
    pickup_lng      DOUBLE PRECISION NOT NULL,
    dropoff_lat     DOUBLE PRECISION NOT NULL,
    dropoff_lng     DOUBLE PRECISION NOT NULL,
    surge_multiplier DECIMAL(3,2) DEFAULT 1.00,
    estimated_fare  DECIMAL(10,2),
    actual_fare     DECIMAL(10,2),
    payment_method_id VARCHAR(100),
    version         INT NOT NULL DEFAULT 0,   -- Optimistic concurrency
    requested_at    TIMESTAMP NOT NULL,
    matched_at      TIMESTAMP,
    pickup_at       TIMESTAMP,
    dropoff_at      TIMESTAMP,
    cancelled_at    TIMESTAMP,
    INDEX idx_rider (rider_id, requested_at DESC),
    INDEX idx_driver (driver_id, requested_at DESC),
    INDEX idx_status (status)
);

-- Cassandra: Trip trajectory (GPS points during trip)
CREATE TABLE trip_trajectory (
    ride_id     UUID,
    recorded_at TIMESTAMP,
    lat         DOUBLE,
    lng         DOUBLE,
    heading     FLOAT,
    speed       FLOAT,
    PRIMARY KEY (ride_id, recorded_at)
) WITH CLUSTERING ORDER BY (recorded_at ASC)
  AND default_time_to_live = 7776000;  -- 90 days

-- Redis: Driver state and spatial index
-- Key: driver:{driver_id}:status  → "available" | "assigned" | "on_trip" | "offline"
-- Key: driver:{driver_id}:location → "{lat},{lng},{heading},{speed},{timestamp}"
-- Key: geohash:{cell} → Set of driver_ids in this cell
-- Key: driver:{driver_id}:geohash → current geohash cell (for removal on update)
```

### Key Algorithms
```python
from typing import List, Tuple, Optional
from dataclasses import dataclass
import math

@dataclass
class Driver:
    driver_id: str
    lat: float
    lng: float
    heading: float
    speed: float
    rating: float
    idle_since: float

@dataclass
class RideRequest:
    ride_id: str
    rider_id: str
    pickup_lat: float
    pickup_lng: float
    ride_type: str

def geohash_encode(lat: float, lng: float, precision: int = 6) -> str:
    """Encode lat/lng to geohash string."""
    BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
    lat_range, lng_range = (-90.0, 90.0), (-180.0, 180.0)
    geohash = []
    bit = 0
    ch = 0
    even = True
    while len(geohash) < precision:
        if even:
            mid = (lng_range[0] + lng_range[1]) / 2
            if lng >= mid:
                ch |= (1 << (4 - bit))
                lng_range = (mid, lng_range[1])
            else:
                lng_range = (lng_range[0], mid)
        else:
            mid = (lat_range[0] + lat_range[1]) / 2
            if lat >= mid:
                ch |= (1 << (4 - bit))
                lat_range = (mid, lat_range[1])
            else:
                lat_range = (lat_range[0], mid)
        even = not even
        bit += 1
        if bit == 5:
            geohash.append(BASE32[ch])
            bit = 0
            ch = 0
    return "".join(geohash)

def get_neighbors(geohash: str) -> List[str]:
    """Return the 8 neighboring geohash cells."""
    # Implementation uses geohash arithmetic to find N, NE, E, SE, S, SW, W, NW neighbors
    # Each neighbor is computed by adjusting lat/lng at the cell boundary
    pass  # Standard geohash neighbor algorithm

def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distance between two points in meters."""
    R = 6371000  # Earth's radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

async def find_nearby_drivers(
    lat: float, lng: float, radius_m: float, ride_type: str, limit: int = 20
) -> List[Driver]:
    """Find available drivers within radius using geohash spatial index."""
    cell = geohash_encode(lat, lng, precision=6)
    cells_to_search = [cell] + get_neighbors(cell)

    candidates = []
    for c in cells_to_search:
        driver_ids = await redis.smembers(f"geohash:{c}")
        for did in driver_ids:
            status = await redis.get(f"driver:{did}:status")
            if status != "available":
                continue
            loc = await redis.get(f"driver:{did}:location")
            dlat, dlng, heading, speed, ts = parse_location(loc)
            dist = haversine_distance(lat, lng, dlat, dlng)
            if dist <= radius_m:
                candidates.append(Driver(
                    driver_id=did, lat=dlat, lng=dlng,
                    heading=heading, speed=speed,
                    rating=await get_driver_rating(did),
                    idle_since=ts
                ))

    # Sort by composite score: ETA (40%), rating (30%), idle time (30%)
    candidates.sort(key=lambda d: match_score(d, lat, lng), reverse=True)
    return candidates[:limit]

async def match_ride(request: RideRequest) -> Optional[str]:
    """Match a ride request to a driver. Returns driver_id or None."""
    radius = 3000  # Start with 3 km
    max_radius = 8000

    while radius <= max_radius:
        drivers = await find_nearby_drivers(
            request.pickup_lat, request.pickup_lng, radius, request.ride_type
        )
        for driver in drivers:
            # Optimistic lock: try to assign this driver
            acquired = await redis.set(
                f"driver:{driver.driver_id}:status", "assigned",
                nx=False,  # We need CAS, not SETNX
                # Use Lua for atomic compare-and-swap:
            )
            # Lua CAS: if status == "available" then set "assigned" return 1 else return 0
            success = await redis.eval(
                "if redis.call('get', KEYS[1]) == 'available' "
                "then redis.call('set', KEYS[1], 'assigned') return 1 "
                "else return 0 end",
                1, f"driver:{driver.driver_id}:status"
            )
            if success:
                return driver.driver_id
            # Driver was taken by another request, try next

        radius += 2000  # Expand radius

    return None  # No drivers available
```

### Capacity Planning

| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Location Updates | 1M drivers x 1 update/3 sec x 100 bytes | 333K writes/sec, 33 MB/sec |
| Spatial Index (memory) | 1M drivers x 100 bytes | ~100 MB per city replica |
| Trip Storage | 10K trips/sec x 5 KB metadata | ~50 MB/sec → 4 TB/day |
| Trajectory Storage | 10K active trips x 1 point/3 sec x 50 bytes | ~170K writes/sec |
| Redis (driver state) | 1M drivers x 500 bytes | ~500 MB |
| Matching Compute | 10K matches/sec, each queries ~1000 candidates | ~50 match servers |

---

## What Separates Senior from Staff from Principal

| Level | What they demonstrate | Example from this design |
|-------|----------------------|-------------------------|
| Senior | Designs the basic flow (request → match → trip → payment), uses geohash, handles matching | Implements geohash-based driver lookup, designs trip state machine, handles basic concurrency |
| Staff | Addresses ETA calculation, surge pricing, driver-side experience, failure modes in matching | Proposes road-network-based ETA, designs surge pricing algorithm, handles driver acceptance timeout chain, discusses payment failure recovery |
| Principal | Thinks about marketplace dynamics, global optimization, fairness, and platform evolution | Proposes batched matching (optimizing across multiple simultaneous requests), discusses driver earning fairness, designs A/B testing for matching algorithms, considers regulatory requirements (driver employment law, accessibility requirements) |

---

## Red Flags & Common Mistakes

- **Using SQL spatial queries for real-time matching**: At 10K queries/sec against 1M rows, SQL (even with PostGIS) is too slow for the hot path. The spatial index must be in-memory.
- **No concurrency handling in matching**: If you don't address the "two riders get the same driver" race condition, the interviewer will push on it. The CAS/optimistic lock is essential.
- **Straight-line distance for ETA**: Haversine distance between two points ignores roads, traffic, and one-way streets. A 3 km straight-line distance could be a 15-minute drive. At least mention road network routing.
- **Forgetting the driver's perspective**: Most candidates design only the rider flow. The driver acceptance flow (offer → accept/decline → timeout → re-offer) is equally important.
- **Over-engineering with a centralized matching queue**: A single queue processing ride requests one-by-one becomes a bottleneck. Partition by city and use optimistic concurrency.
