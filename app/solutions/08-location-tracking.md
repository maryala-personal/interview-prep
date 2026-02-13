# Design a Real-Time Location Tracking System

> **Companies**: Uber, Lyft, DoorDash, Google Maps, Amazon (logistics), FedEx, Instacart | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you design a system that ingests millions of location updates per second, fan out real-time position data to interested subscribers, and handle the storage challenges of time-series geospatial data? This problem tests your understanding of pub/sub at scale, time-series databases, and the difference between storing data for real-time consumption vs. historical analytics.

---

## The First 5 Minutes — Scoping & Technical Clarifications

**These are the questions that make the interviewer think "this person knows what they're doing."**

- "What's the update frequency? Are we tracking vehicles at 1 Hz (1 update/sec) or IoT sensors at 0.1 Hz? This determines write throughput."
- "How many entities are we tracking simultaneously? 1M (Uber-scale) or 100M (all smartphones in a country)?"
- "Who needs to see the real-time positions? Just the dispatch system, or also end users watching their delivery approach?"
- "What's the latency requirement for real-time updates? Sub-second for the viewer seeing a position change?"
- "Do we need historical location data? For how long? This changes the storage model dramatically."
- "What's the precision requirement? GPS-level (5-10m) or cell-tower-level (100m+)?"
- "Do we need geofencing — triggering events when an entity enters or leaves a defined area?"
- "Single region or global? A global fleet tracking system has very different characteristics than a city-level food delivery tracker."

### Working Assumptions

| Parameter | Value |
|-----------|-------|
| Tracked entities | 5M (delivery drivers, vehicles, couriers) |
| Update frequency | 1 update every 4 seconds per entity |
| Write QPS (location updates) | 1.25M/sec |
| Active subscriptions (viewers watching locations) | 10M (customers tracking deliveries) |
| Real-time fan-out | Each update goes to 1-5 subscribers |
| Real-time latency (update to viewer) | p99 < 1 second |
| Historical retention | 30 days detailed, 1 year aggregated |
| Availability | 99.99% |

**The math**:
- 5M entities x 1 update/4 sec = 1.25M writes/sec
- Each update: ~100 bytes (entity_id, lat, lng, heading, speed, timestamp, metadata)
- Write bandwidth: 1.25M x 100 bytes = 125 MB/sec
- Storage (30 days): 1.25M/sec x 100 bytes x 86400 sec/day x 30 days = ~324 TB raw
- With compression (10x for time-series): ~32 TB
- Fan-out: 1.25M updates/sec x 2 avg subscribers = 2.5M push messages/sec

---

## High-Level Design (Keep it brief — 5 minutes max)

```
┌──────────────┐
│  Tracked     │  GPS update every 4 sec
│  Entities    │  (drivers, vehicles, couriers)
└──────┬───────┘
       │ MQTT / WebSocket / HTTP
       │
┌──────▼───────┐
│  Ingestion   │  ← Receives 1.25M updates/sec, validates, enriches
│  Service     │
└──────┬───────┘
       │
┌──────▼───────┐
│  Kafka       │  ← Durable stream of all location events
│  (Location   │     Partitioned by entity_id
│   Stream)    │
└──┬───────┬───┘
   │       │
   │  ┌────▼────────┐     ┌────────────────┐
   │  │ Real-Time   │────→│  Subscribers   │  ← WebSocket push to customers tracking deliveries
   │  │ Fan-Out     │     │  (10M active)  │
   │  │ Service     │     └────────────────┘
   │  └─────────────┘
   │
   │  ┌─────────────┐     ┌────────────────┐
   └──│ Storage     │────→│  TimescaleDB / │  ← Time-series optimized for location data
      │ Writer      │     │  InfluxDB /    │
      └─────────────┘     │  Cassandra     │
                          └────────────────┘
                                   │
                          ┌────────▼────────┐
                          │  Current State  │  ← Redis: latest position per entity (hot store)
                          │  Cache (Redis)  │
                          └─────────────────┘
```

**Why this architecture?** We separate three concerns: (1) ingestion — high-throughput write path that must never block, (2) real-time fan-out — pushing updates to subscribers with sub-second latency, and (3) historical storage — persisting time-series data for analytics and replay. Kafka ties them together: it absorbs the 1.25M writes/sec, provides durability, and feeds both the fan-out and storage paths independently.

---

## Core Concepts Deep Dive

### Concept 1: High-Throughput Location Ingestion — Protocol Choice and Batching

**What it is**: 5M devices sending GPS updates creates a massive inbound data stream. The protocol and ingestion architecture must handle 1.25M messages/sec without becoming a bottleneck.

**How it applies here**:
- **Protocol choice**: MQTT is ideal for constrained devices (battery-efficient, lightweight). WebSocket for web/mobile apps. HTTP with batching for server-to-server (fleet management systems). In practice, the ingestion service supports all three via protocol-specific adapters.
- **Batching**: Instead of 1 update per message, the device buffers 4 seconds of GPS points and sends them in a batch of 4. This reduces connection overhead by 4x while maintaining freshness. The ingestion service unpacks the batch and processes each point.
- **Back-pressure**: If Kafka falls behind, the ingestion service buffers in memory (bounded ring buffer) and applies back-pressure to the devices via flow control (MQTT QoS 0 = fire-and-forget, acceptable for location data).

**The math/mechanics**:
- MQTT connection overhead: ~10 KB per connection. 5M connections = 50 GB — that's a lot. Solution: connection multiplexing at the edge. Run MQTT brokers (EMQ/VerneMQ) as an edge layer, consolidating device connections. 100 edge brokers x 50K connections each.
- Kafka partitioning: 500 partitions, each handling ~2500 writes/sec — well within Kafka's per-partition throughput.

**Common misconception**: Candidates propose HTTP POST for every location update. At 1.25M req/sec, the connection setup/teardown overhead of HTTP is enormous (3-way handshake, TLS negotiation). Persistent connections (MQTT, WebSocket) are 10x more efficient for high-frequency updates.

### Concept 2: Real-Time Fan-Out — Pub/Sub for Location Subscriptions

**What it is**: When a customer orders food delivery, they want to see the driver's location updating in real-time on a map. This requires a pub/sub system: the driver's location updates are "published" and the customer is a "subscriber."

**How it applies here**:
- When a customer starts tracking, they subscribe to `entity:{driver_id}`. The fan-out service maintains a mapping: `entity_id → set of subscriber WebSocket connections`.
- When a location update for that entity arrives (from Kafka), the fan-out service looks up all subscribers and pushes the update.
- Subscriptions are ephemeral — they last only while the customer is actively viewing the tracking screen. Average subscription duration: ~20 minutes for food delivery.

**The math/mechanics**:
- 10M active subscriptions. Average 2 subscribers per entity = 5M entities actively being watched.
- Fan-out writes: 5M entities x 1 update/4 sec x 2 subscribers = 2.5M push messages/sec.
- Each WebSocket connection: ~20 KB memory. 10M connections / 50K per server = 200 WebSocket servers.
- The fan-out service consumes from Kafka (partitioned by entity_id) and routes to the WebSocket server holding the subscriber's connection. This requires a connection registry (Redis): `subscriber:{user_id}` → `ws_server_id`.

**Common misconception**: Candidates propose polling ("the client polls every 3 seconds"). This works but at 10M users polling every 3 seconds = 3.3M HTTP requests/sec that are mostly wasted (the driver hasn't moved 60% of the time). WebSocket push is 5x more efficient in bandwidth and eliminates unnecessary requests.

### Concept 3: Time-Series Storage — Partitioning and Downsampling

**What it is**: Location data is time-series data: each entity generates a stream of (timestamp, lat, lng, ...) points. Time-series databases are optimized for this access pattern: append-only writes, time-range queries, and automatic downsampling.

**How it applies here**:
- **Hot store (Redis)**: The latest position of each entity. Used for real-time queries ("where is driver X right now?"). 5M entries x 100 bytes = 500 MB.
- **Warm store (TimescaleDB / InfluxDB)**: Last 30 days of detailed data. Used for trip replay, geofence analysis, and debugging. Compressed time-series: ~32 TB.
- **Cold store (S3 / data warehouse)**: Aggregated data (1-minute averages instead of 4-second points). Used for long-term analytics. 1 year of aggregated data: ~2 TB.

**The math/mechanics**:
- TimescaleDB hypertable partitioned by time (1-day chunks) and entity_id (hash partitioning).
- Downsampling: after 7 days, aggregate 4-second points to 1-minute averages (15x compression). After 30 days, move to S3 in Parquet format.
- Query pattern: "show me entity X's path from 2 PM to 3 PM today" → scan 1 hour of data for 1 entity = 900 points (1 per 4 sec) = ~90 KB. This is a fast range scan on the time-series index.

**Common misconception**: Candidates use a regular SQL database (PostgreSQL) for location history. At 1.25M writes/sec, even a sharded PostgreSQL cluster will struggle. Time-series databases (TimescaleDB, InfluxDB, Cassandra) are purpose-built for this workload with columnar compression, time-based partitioning, and automatic downsampling.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: "Ingestion at Scale"

**Interviewer**: "1.25M writes per second. Walk me through the ingestion pipeline end-to-end."

**You**: "The device sends a GPS update via MQTT to one of 100 edge MQTT brokers (geographically distributed for low latency). The broker immediately ACKs the device (QoS 1 = at-least-once). The broker batches messages and forwards them to the ingestion service via gRPC (server-side streaming). The ingestion service validates the update (lat/lng range check, entity_id exists, timestamp is recent), enriches it (add geohash, city_id), and publishes to Kafka. Kafka is the durable backbone — topic `location-updates`, 500 partitions, partitioned by entity_id % 500. Three consumers read from Kafka: (1) the real-time fan-out service, (2) the storage writer (to TimescaleDB), and (3) the current-state updater (writes latest position to Redis). Each consumer runs independently at its own pace."

**Interviewer**: "What happens if the ingestion service gets a spike — say, 3x the normal rate (rush hour)?"

**You**: "Three safeguards. First, Kafka absorbs the burst — it can buffer hours of data on disk. The consumers process at their max rate and catch up during off-peak. Second, the ingestion service is horizontally scalable — if the fleet grows, we add more instances. With Kubernetes, we use HPA based on Kafka consumer lag: if lag exceeds 5 seconds, scale up. Third, the MQTT brokers have a bounded in-memory buffer. If the ingestion service can't keep up (rare), the buffer fills and the broker drops old messages (for location data, old = stale, so this is acceptable — we care about the latest position, not historical completeness in real-time). We log dropped messages for monitoring."

**Interviewer**: "Some devices send bad data — GPS drift, spoofed locations, timestamp in the future. How do you handle it?"

**You**: "Validation pipeline at the ingestion service. Checks: (1) Latitude [-90, 90], longitude [-180, 180]. Out of range → drop. (2) Speed check: if the entity moved more than physically possible since last update (e.g., > 200 km/h for a delivery bike), flag as anomaly. We still store it but mark it as `quality: suspect`. (3) Timestamp within 60 seconds of server time. Future timestamps or stale timestamps (> 60s old) → adjust to server timestamp. (4) Duplicate check: if entity_id + timestamp matches a recent update (Redis lookup), drop the duplicate. (5) Geofence check: if the entity is supposed to be in New York but reports coordinates in Tokyo, flag as possible spoof. These checks add ~1ms per update — negligible."

**Interviewer**: "How do you handle entities that stop sending updates? A driver's phone dies mid-delivery."

**You**: "The current-state store in Redis has a TTL per entity. Each update sets `driver:d123:last_seen` with a 30-second TTL. If no update arrives within 30 seconds, the key expires and the entity is considered 'stale' or 'offline.' A background job scans for stale entities and publishes 'entity offline' events. The tracking UI shows 'last seen X minutes ago' with the final known position. For the subscriber (customer tracking their delivery), the UI shows a static marker with a 'location unavailable' badge instead of a moving dot. The system publishes an alert to the dispatch/operations team if a driver goes offline mid-trip."

### Deep Dive Path 2: "Real-Time Fan-Out to Subscribers"

**Interviewer**: "Walk me through a customer opening the tracking screen on their phone. What happens?"

**You**: "The customer opens the delivery tracking screen. The app establishes a WebSocket connection to our WebSocket gateway (closest region). The gateway registers the connection: `subscriber:user_456` → `ws_server:ws-12` in Redis. The app sends a 'subscribe' message: `{entity_id: 'driver_789'}`. The fan-out service adds an entry: `entity:driver_789:subscribers` → `{user_456}` (Redis set). Now, whenever a location update for driver_789 arrives from Kafka, the fan-out service checks the subscriber set, looks up each subscriber's WebSocket server, and routes the update. The customer's app receives the update and moves the marker on the map. This entire path takes ~200-500ms from the driver's GPS fix to the customer's screen."

**Interviewer**: "That's a lot of Redis lookups per update. 1.25M updates/sec, each doing a subscriber set lookup and a connection registry lookup."

**You**: "Good catch. Optimization: the fan-out service maintains a local in-memory cache of the entity→subscribers mapping and the subscriber→ws_server mapping. The cache is populated on first lookup and invalidated via Redis pub/sub when subscriptions change (subscribe/unsubscribe events). Since subscription changes are rare compared to location updates (a subscription lasts 20 minutes, updates come every 4 seconds = 300 updates per subscription lifecycle), the cache hit rate is > 99.9%. The fan-out service only hits Redis on cache misses and subscription changes. This drops Redis load from 1.25M lookups/sec to ~10K/sec."

**Interviewer**: "A customer is watching their delivery and the WebSocket server crashes. What happens?"

**You**: "The WebSocket connection drops. The client detects the disconnect and reconnects within 2-3 seconds (with exponential backoff). The new connection might go to a different WS server. The client re-subscribes to the entity. During the 2-3 second gap, the customer misses 1 location update — they see the marker 'jump' to the new position on reconnect. The registration in Redis for the old WS server has a TTL (60 seconds), so it auto-cleans if the server doesn't re-register. The fan-out service, if it tries to route to the dead server, gets a connection error, marks the subscriber as disconnected, and removes them from the entity's subscriber set. No message is lost in the pipeline — Kafka retains the updates, and the fan-out service for that entity's partition will process them regardless of subscriber state."

**Interviewer**: "How does this scale if 1 million people watch the same event? Like a famous person's live location on a map."

**You**: "A 1:1M fan-out is fundamentally different from 1:2. We can't push 1M messages per location update from a single consumer. Solution: tiered fan-out. The fan-out service publishes the update to a Redis pub/sub channel (`location:entity:driver_789`). 200 WebSocket servers each subscribe to this channel. Each server holds ~5000 of the 1M subscribers. Redis pub/sub delivers the update to all 200 servers in one broadcast (not 200 individual messages — Redis does this efficiently). Each WS server then fans out locally to its 5000 connections. Total messages: 1 (Kafka) → 1 (Redis pub/sub) → 200 (server-level) → 1M (connection-level). The bottleneck shifts to the WS servers' outbound bandwidth: 5000 connections x 100 bytes x 0.25 Hz = 125 KB/sec per server — trivial."

### Deep Dive Path 3: "Historical Storage and Geofencing"

**Interviewer**: "You mentioned TimescaleDB for historical storage. Why not Cassandra? How does the schema work?"

**You**: "Both work. TimescaleDB is PostgreSQL with time-series extensions — it gives us SQL query flexibility (joins, window functions) for analytics. Cassandra gives better write throughput but weaker query capabilities. For a delivery company that needs 'show me all deliveries that passed through zone X last Tuesday between 2-3 PM,' SQL is much more productive than Cassandra's limited query language. Schema:
```sql
CREATE TABLE location_history (
    entity_id  BIGINT NOT NULL,
    timestamp  TIMESTAMPTZ NOT NULL,
    lat        DOUBLE PRECISION,
    lng        DOUBLE PRECISION,
    geohash    TEXT,
    heading    REAL,
    speed      REAL,
    metadata   JSONB
);
SELECT create_hypertable('location_history', 'timestamp', chunk_time_interval => INTERVAL '1 day');
CREATE INDEX idx_entity_time ON location_history (entity_id, timestamp DESC);
```
TimescaleDB chunks this by day and compresses old chunks automatically. Write throughput: TimescaleDB handles ~500K inserts/sec per node with batch inserts. We'd need 3 nodes for our 1.25M writes/sec."

**Interviewer**: "Walk me through geofencing. How do you trigger an event when a delivery driver enters a customer's neighborhood?"

**You**: "Geofencing is a continuous query over the location stream. For each location update, check if the entity has entered or exited any active geofence. Naive approach: for each update, check against all geofences — O(N) where N = number of geofences. Optimized approach: index geofences spatially using a geohash grid. When a location update arrives, compute its geohash. Look up which geofences overlap that geohash cell (pre-computed mapping: geohash_cell → list of geofences). For each overlapping geofence, do a precise point-in-polygon check. This reduces the check from O(N) to O(K) where K = geofences in that cell, typically 1-3."

**Interviewer**: "The customer's delivery geofence is a 500m radius around their home. How do you implement the enter/exit logic?"

**You**: "We maintain a per-entity state: `geofence:entity_789:fences` = set of geofence IDs the entity is currently inside. On each location update: (1) Check which geofences the entity is now inside (using the spatial lookup). (2) Compare to the stored set. (3) New entries in the set = 'entered' events. Removed entries = 'exited' events. (4) Update the stored set. For a delivery: when the driver enters the 500m radius, we fire an 'approaching' event → push notification to customer ('Your delivery is nearby!'). When the driver enters a 50m radius, fire an 'arrived' event. The state is stored in Redis for speed, and the geofence evaluation runs in the fan-out service pipeline — same consumer that reads location updates from Kafka. Adding geofence evaluation to the pipeline adds ~0.5ms per update."

---

## How Real Companies Built This

- **Uber**: Their location pipeline processes millions of GPS updates per second. They built "Ringpop" for consistent hashing of location subscriptions and "Marketplace" for matching. Key insight: they separate the "last known location" (hot, in Redis) from the location history (cold, in HDFS). See: "Scaling Uber's Real-Time Data" (Uber Engineering Blog) and "How Uber Serves Over 40 Million Reads Per Second from Online Storage" (Uber Engineering Blog).
- **Google Maps**: Processes anonymized location data from billions of Android devices to compute real-time traffic. The scale is orders of magnitude beyond ride-sharing. Their approach uses map-matching (snapping GPS to road segments) and aggregates speed data per road segment. See: "Google Maps 101: How AI Helps Predict Traffic" (Google Blog).
- **Amazon Logistics**: Tracks millions of packages and delivery vehicles. They use a purpose-built time-series service on DynamoDB with tiered storage (hot/warm/cold). The system handles the "last mile" tracking that customers see on the Amazon app.
- **Key lesson**: The split between "current state" (Redis, in-memory) and "historical data" (time-series DB, object store) is universal. Every company at this scale makes this separation. Trying to serve both real-time queries and historical analytics from the same data store is the #1 architectural mistake.

---

## The Complete Reference Design

### API Design
```
# Device → Server: Location update (MQTT or HTTP)
PUBLISH location/{entity_id}
Payload: {
    "entity_id": "d_789",
    "lat": 40.7128,
    "lng": -74.0060,
    "heading": 45.0,
    "speed": 12.5,          // m/s
    "accuracy": 8.0,        // meters
    "battery": 72,           // percent
    "timestamp": 1707696000123
}

# Client → Server: Subscribe to entity location (WebSocket)
→ {"type": "subscribe", "entity_ids": ["d_789"]}
← {"type": "location_update", "entity_id": "d_789", "lat": 40.7128, "lng": -74.0060, "heading": 45.0, "speed": 12.5, "timestamp": 1707696000123}

# REST APIs
GET /api/v1/entities/{entity_id}/location
Response: {
    "entity_id": "d_789",
    "lat": 40.7128,
    "lng": -74.0060,
    "heading": 45.0,
    "speed": 12.5,
    "last_updated": "2026-02-12T10:00:00.123Z",
    "status": "active"
}

GET /api/v1/entities/{entity_id}/history?start=2026-02-12T09:00:00Z&end=2026-02-12T10:00:00Z
Response: {
    "entity_id": "d_789",
    "points": [
        {"lat": 40.710, "lng": -74.008, "timestamp": "...", "speed": 10.2},
        {"lat": 40.711, "lng": -74.007, "timestamp": "...", "speed": 11.5},
        ...
    ],
    "total_distance_meters": 8500,
    "duration_seconds": 3600
}

POST /api/v1/geofences
Request: {
    "name": "Customer Home",
    "type": "circle",
    "center": {"lat": 40.7128, "lng": -74.0060},
    "radius_meters": 500,
    "entity_ids": ["d_789"],
    "trigger_on": ["enter", "exit"],
    "webhook_url": "https://my-service/geofence-events"
}
Response: {
    "geofence_id": "gf_abc123",
    "status": "active"
}
```

### Database Schema
```sql
-- TimescaleDB: Location history (hypertable)
CREATE TABLE location_history (
    entity_id    BIGINT NOT NULL,
    timestamp    TIMESTAMPTZ NOT NULL,
    lat          DOUBLE PRECISION NOT NULL,
    lng          DOUBLE PRECISION NOT NULL,
    geohash6     TEXT NOT NULL,
    heading      REAL,
    speed        REAL,
    accuracy     REAL,
    metadata     JSONB
);
SELECT create_hypertable('location_history', 'timestamp',
    chunk_time_interval => INTERVAL '1 day');
CREATE INDEX idx_entity_time ON location_history (entity_id, timestamp DESC);
CREATE INDEX idx_geohash ON location_history (geohash6, timestamp DESC);

-- Continuous aggregate for downsampling
CREATE MATERIALIZED VIEW location_1min
WITH (timescaledb.continuous) AS
SELECT
    entity_id,
    time_bucket('1 minute', timestamp) AS bucket,
    AVG(lat) AS avg_lat,
    AVG(lng) AS avg_lng,
    AVG(speed) AS avg_speed,
    MAX(speed) AS max_speed,
    COUNT(*) AS point_count
FROM location_history
GROUP BY entity_id, bucket;

-- PostgreSQL: Geofences
CREATE TABLE geofences (
    geofence_id   UUID PRIMARY KEY,
    name          TEXT,
    fence_type    TEXT NOT NULL,   -- 'circle', 'polygon'
    center_lat    DOUBLE PRECISION,
    center_lng    DOUBLE PRECISION,
    radius_meters INT,
    polygon       JSONB,           -- For polygon type
    entity_ids    BIGINT[],
    trigger_on    TEXT[],           -- 'enter', 'exit', 'dwell'
    webhook_url   TEXT,
    created_at    TIMESTAMP DEFAULT NOW()
);

-- Redis: Current state
-- Key: entity:{entity_id}:location → Hash {lat, lng, heading, speed, timestamp, geohash}
-- Key: entity:{entity_id}:subscribers → Set of subscriber user_ids
-- Key: subscriber:{user_id}:ws_server → WebSocket server ID
-- Key: geofence:cell:{geohash6} → Set of geofence_ids that overlap this cell
-- Key: geofence:entity:{entity_id}:inside → Set of geofence_ids entity is currently inside
```

### Key Algorithms
```python
import time
import math
from dataclasses import dataclass
from typing import List, Set, Optional

@dataclass
class LocationUpdate:
    entity_id: str
    lat: float
    lng: float
    heading: float
    speed: float
    accuracy: float
    timestamp: int

@dataclass
class Geofence:
    geofence_id: str
    center_lat: float
    center_lng: float
    radius_meters: float

class LocationPipeline:
    """Processes location updates from Kafka."""

    async def process_update(self, update: LocationUpdate):
        """Main processing pipeline for each location update."""

        # 1. Validate
        if not self.validate(update):
            return

        # 2. Update current state (Redis)
        geohash = geohash_encode(update.lat, update.lng, 6)
        await self.update_current_state(update, geohash)

        # 3. Check geofences
        await self.check_geofences(update, geohash)

        # 4. Fan out to subscribers
        await self.fan_out_to_subscribers(update)

        # 5. Write to time-series DB (batched)
        self.write_buffer.append(update)
        if len(self.write_buffer) >= 1000:
            await self.flush_to_timescaledb()

    def validate(self, update: LocationUpdate) -> bool:
        """Validate a location update."""
        if not (-90 <= update.lat <= 90 and -180 <= update.lng <= 180):
            return False
        if abs(update.timestamp - time.time() * 1000) > 60000:  # > 60s drift
            update.timestamp = int(time.time() * 1000)  # Correct to server time
        if update.speed > 200:  # > 200 m/s = 720 km/h, clearly wrong
            return False
        return True

    async def update_current_state(self, update: LocationUpdate, geohash: str):
        """Update Redis with latest position."""
        pipe = redis.pipeline()

        # Update location hash
        pipe.hmset(f"entity:{update.entity_id}:location", {
            "lat": update.lat, "lng": update.lng,
            "heading": update.heading, "speed": update.speed,
            "timestamp": update.timestamp, "geohash": geohash,
        })
        pipe.expire(f"entity:{update.entity_id}:location", 30)  # 30s TTL

        # Update geohash index (move from old cell to new cell)
        old_geohash = await redis.hget(f"entity:{update.entity_id}:location", "geohash")
        if old_geohash and old_geohash != geohash:
            pipe.srem(f"geohash:cell:{old_geohash}", update.entity_id)
            pipe.sadd(f"geohash:cell:{geohash}", update.entity_id)

        await pipe.execute()

    async def check_geofences(self, update: LocationUpdate, geohash: str):
        """Evaluate geofence enter/exit events."""
        # Get geofences overlapping this cell
        fence_ids = await redis.smembers(f"geofence:cell:{geohash}")
        if not fence_ids:
            return

        currently_inside: Set[str] = set()
        for fence_id in fence_ids:
            fence = await self.get_geofence(fence_id)
            if fence and self.point_in_geofence(update.lat, update.lng, fence):
                currently_inside.add(fence_id)

        # Compare with previous state
        previously_inside = await redis.smembers(f"geofence:entity:{update.entity_id}:inside")
        entered = currently_inside - previously_inside
        exited = previously_inside - currently_inside

        # Fire events
        for fence_id in entered:
            await self.fire_geofence_event(update.entity_id, fence_id, "enter")
        for fence_id in exited:
            await self.fire_geofence_event(update.entity_id, fence_id, "exit")

        # Update state
        if currently_inside:
            await redis.delete(f"geofence:entity:{update.entity_id}:inside")
            await redis.sadd(f"geofence:entity:{update.entity_id}:inside", *currently_inside)

    def point_in_geofence(self, lat: float, lng: float, fence: Geofence) -> bool:
        """Check if point is inside a circular geofence."""
        distance = haversine_distance(lat, lng, fence.center_lat, fence.center_lng)
        return distance <= fence.radius_meters

    async def fan_out_to_subscribers(self, update: LocationUpdate):
        """Push update to all active subscribers."""
        # Check local cache first (populated from Redis, invalidated via pub/sub)
        subscribers = self.subscriber_cache.get(update.entity_id, set())
        if not subscribers:
            subscribers = await redis.smembers(f"entity:{update.entity_id}:subscribers")
            self.subscriber_cache[update.entity_id] = subscribers

        for user_id in subscribers:
            ws_server = await self.get_ws_server(user_id)
            if ws_server:
                await self.push_to_ws_server(ws_server, user_id, update)
```

### Capacity Planning

| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Ingestion (Kafka) | 1.25M msgs/sec x 100 bytes | 125 MB/sec write |
| Kafka Storage | 125 MB/sec x 86400 sec x 3 days retention | ~32 TB |
| Redis (current state) | 5M entities x 200 bytes | ~1 GB |
| Redis (subscriber state) | 10M subscriptions x 100 bytes | ~1 GB |
| TimescaleDB | 1.25M writes/sec, 30 days retention | ~32 TB (compressed) |
| WebSocket Servers | 10M connections / 50K per server | 200 servers |
| Fan-out bandwidth | 2.5M pushes/sec x 100 bytes | 250 MB/sec outbound |
| MQTT Edge Brokers | 5M connections / 50K per broker | 100 brokers |

---

## What Separates Senior from Staff from Principal

| Level | What they demonstrate | Example from this design |
|-------|----------------------|-------------------------|
| Senior | Designs the basic pipeline: ingest → store → query. Handles real-time updates to clients | Implements Kafka ingestion, Redis current-state, WebSocket push to subscribers |
| Staff | Addresses fan-out scaling, geofencing, data quality, and tiered storage | Proposes subscriber caching to avoid Redis hotspots, implements geofence evaluation in the pipeline, designs downsampling strategy, handles device offline detection |
| Principal | Designs for multi-region deployment, considers data privacy (location is PII), proposes ML-based anomaly detection | Proposes regional ingestion with global event bus, designs data retention policies for GDPR compliance, implements trajectory prediction (where will the driver be in 2 minutes?), considers aggregated location data products for traffic/demand prediction |

---

## Red Flags & Common Mistakes

- **Using HTTP polling for real-time tracking**: At 10M users polling every 3 seconds, that's 3.3M req/sec of mostly empty responses. WebSocket push is the correct architecture.
- **Single data store for current state and history**: Real-time queries ("where is driver X?") and historical queries ("show me all trips last week") have fundamentally different access patterns. Trying to serve both from one store leads to performance problems in both.
- **Ignoring data quality**: GPS drift, spoofed locations, and network delays are real. A production system must validate, filter, and correct incoming data.
- **No geofencing**: If the interviewer asks "how would you implement notifications when the driver is nearby?" and you haven't mentioned geofencing, it suggests a gap in spatial thinking.
- **Underestimating the fan-out problem**: 1.25M updates/sec is the ingestion rate. The fan-out to subscribers multiplies this by the average subscriber count. At 2 subscribers per entity, you're pushing 2.5M messages/sec — this needs dedicated infrastructure.
