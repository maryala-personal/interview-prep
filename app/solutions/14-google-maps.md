# Design Google Maps / Proximity Service

> **Companies**: Google, Uber, Lyft, DoorDash, Yelp, Meta (Nearby Friends), Apple | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you design systems that efficiently query spatial data? This probes your understanding of geospatial indexing (geohash, quadtree, S2 cells), proximity search algorithms, map tile serving at scale, and routing/pathfinding. The interviewer wants to see you reason about how to turn "find things near me" from an O(N) scan into an O(log N) or O(1) lookup.

---

## The First 5 Minutes — Scoping & Technical Clarifications

**Questions that show the interviewer you know what you're doing:**

- "Are we designing the proximity service (find nearby places/drivers), the map rendering (tiles), or the routing engine (directions)? These are distinct systems."
- "What's the query pattern — find K nearest neighbors, or find all entities within a radius?"
- "How many entities are we indexing? Millions of static places, or millions of real-time moving objects (like drivers)?"
- "What's the update frequency? Static POIs change rarely, but driver locations update every 3-5 seconds."
- "What's the p99 latency target for a proximity query?"
- "What's the geographic scope — single city, single country, or global?"
- "What accuracy is needed? Within 10 meters or 1 kilometer?"
- "Do we need to handle density variations — dense cities vs. sparse rural areas?"

### Working Assumptions
| Parameter | Value | Derivation |
|-----------|-------|------------|
| Total places/POIs | 200M globally | Restaurants, shops, landmarks, etc. |
| Active moving entities (drivers) | 5M simultaneously | Uber/Lyft scale across all cities |
| Location update frequency | Every 4 seconds per entity | 5M / 4 = 1.25M updates/sec |
| Proximity queries | 500K QPS | Users searching for nearby places/drivers |
| Search radius | 1-50 km (default 5km) | Typical "near me" search |
| Results per query | Top 20 nearest | Standard UX |
| Query latency SLA | p50 < 20ms, p99 < 100ms | Must feel instant |
| Map tile requests | 5M QPS | Tile serving at global scale |
| Storage per POI | ~500 bytes | Name, location, category, metadata |
| Geographic precision | ~10 meters | Sufficient for most applications |

---

## High-Level Design (Brief — 5 minutes)

```
PROXIMITY SERVICE (find nearby):

User: "restaurants near me"
    |
    v
+------------------+     +--------------------+     +-------------------+
| API Gateway /    |---->| Proximity Service  |---->| Geospatial Index  |
| Load Balancer    |     | (stateless)        |     | (geohash-based    |
+------------------+     +--------------------+     |  in-memory index) |
                                                    +-------------------+

LOCATION UPDATE PATH (for moving entities):

Driver app sends location
    |
    v
+------------------+     +--------------------+     +-------------------+
| Location Ingest  |---->| Kafka              |---->| Index Updater     |
| Service          |     | (location events)  |     | (updates geohash  |
+------------------+     +--------------------+     |  index in-memory) |
                                                    +-------------------+

MAP TILE SERVING:

User pans/zooms map
    |
    v
+------------------+     +--------------------+     +-------------------+
| Client (Mapbox/  |---->| CDN Edge           |---->| Tile Server       |
|  custom renderer)|     | (cached tiles)     |     | (pre-rendered or  |
+------------------+     +--------------------+     |  dynamic tiles)   |
                                                    +-------------------+
```

**Why this architecture?**: Proximity search and map rendering are fundamentally different workloads. Proximity is a real-time query problem (find things near a point) that benefits from in-memory spatial indexes. Map tiles are a pre-computed, cache-friendly workload (the map doesn't change every second). Separating them allows optimizing each independently.

---

## Core Concepts Deep Dive

### Concept 1: Geohashing — Turning 2D Space into 1D Keys

**What it is**: Geohash encodes a latitude/longitude pair into a string by alternating bits of longitude and latitude and mapping to base-32. "9q8yyk" represents a rectangular cell in San Francisco. Longer strings = smaller cells = higher precision. The critical property: strings with a common prefix are geographically close. This turns 2D proximity search into a 1D prefix search.

**How it applies here**: Each POI or driver is assigned a geohash. To find nearby entities, compute the user's geohash, find all entities sharing a prefix (shorter prefix = larger search area). For a 5km search radius, a geohash prefix of length 5 (~5km x 5km cell) captures most results. But you must also check the 8 neighboring cells (the cell boundary problem).

**The math/mechanics**:
| Geohash length | Cell width | Cell height |
|---------------|------------|-------------|
| 4 | 39.1 km | 19.5 km |
| 5 | 4.9 km | 4.9 km |
| 6 | 1.2 km | 0.6 km |
| 7 | 153 m | 153 m |
| 8 | 38.2 m | 19.1 m |

For a 5km radius search, use prefix length 5 (4.9km cells). Query the user's cell + 8 neighbors = 9 cells. Each cell lookup is a simple prefix scan on a sorted index.

**Common misconception**: Candidates use geohash without mentioning the boundary problem. A user at the edge of a geohash cell may be 10 meters from a POI in the adjacent cell. You MUST query neighboring cells. Also, geohash cells at the same prefix length are not the same physical size at different latitudes (longitude degrees shrink near the poles).

### Concept 2: Quadtree — Adaptive Spatial Partitioning

**What it is**: A quadtree recursively divides 2D space into 4 quadrants. Each leaf node contains at most K entities. Dense areas (Manhattan) get many small cells; sparse areas (Sahara) get few large cells. This naturally adapts to density variations.

**How it applies here**: Build a quadtree over all POIs. Start with the entire world as the root. If a node has > 100 POIs, split it into 4 quadrants. Continue until all leaves have <= 100 POIs. Manhattan might reach depth 15 (cells of ~10 meters), while rural Wyoming stays at depth 5 (~100km cells). Proximity search: traverse the tree from root, visiting only branches that intersect the search circle.

**The math/mechanics**: For 200M POIs with max 100 per leaf = 2M leaf nodes. Average depth: ~12 levels (4^12 = 16M potential cells, but the tree is sparse). Memory: each node = 4 child pointers + bounding box = ~40 bytes. 2M leaves x 40 bytes = 80MB. Extremely compact — fits in memory on a single machine, but we shard by geographic region for locality.

**Common misconception**: Candidates describe quadtrees as better than geohash in all cases. Geohash is simpler to implement (it's just a string prefix), integrates directly with any sorted data store (Redis, DynamoDB), and is easier to shard. Quadtrees are better when density varies wildly and you need adaptive precision. Google S2 cells (which Google actually uses) combine the best of both — a hierarchical cell system with a 1D key mapping like geohash.

### Concept 3: Real-Time Location Updates for Moving Entities

**What it is**: For services like Uber, driver locations change every 3-5 seconds. The spatial index must handle 1M+ updates/second while serving proximity queries at sub-50ms latency. This rules out disk-based storage for the hot path.

**How it applies here**: Driver locations are stored in an in-memory data structure (hash map + geohash index). When a location update arrives: (1) remove the driver from their old geohash cell, (2) compute their new geohash, (3) insert into the new cell. Each operation is O(1). The in-memory index is partitioned by city/region across multiple servers. Updates flow through Kafka for durability and fan-out to index replicas.

**The math/mechanics**: 5M active drivers, updating every 4 seconds = 1.25M updates/sec. Each update: remove from old cell (hash lookup + delete, O(1)) + insert into new cell (hash lookup + insert, O(1)). On a single server handling 1 city (say 100K drivers), that's 25K updates/sec — trivially handled in-memory. Memory per driver: 100 bytes (ID, lat/lng, geohash, timestamp, metadata) x 100K = 10MB per city. Entire global fleet: 5M x 100 bytes = 500MB — fits on one machine, but we shard for availability and locality.

**Common misconception**: Candidates try to store real-time locations in a traditional database (PostgreSQL with PostGIS). At 1M+ updates/sec, no RDBMS can keep up. The hot path must be in-memory. The database is used for historical location storage (for analytics, trip replay) but not for real-time proximity queries.

### Concept 4: Map Tile Rendering & Serving

**What it is**: Maps are rendered as a grid of square tiles at multiple zoom levels. Each zoom level doubles the number of tiles in each dimension: zoom 0 = 1 tile (whole world), zoom 1 = 4 tiles, zoom 2 = 16, ..., zoom 18 = 68 billion tiles. Tiles are pre-rendered as PNG (raster) or served as vector tiles (PBF) for client-side rendering.

**How it applies here**: Vector tiles are the modern approach. The server sends geographic data (roads, buildings, labels) encoded in Protocol Buffers, and the client renders them on GPU. This reduces bandwidth (10x smaller than raster), supports rotation/3D, and allows dynamic styling. Tiles are served via CDN — they change infrequently and are extremely cache-friendly.

**The math/mechanics**: At zoom level 18 (street level), the world has 2^18 x 2^18 = ~68B tiles. But most are ocean/empty — only ~5% (~3.4B) contain meaningful data. At ~20KB average per vector tile = ~68TB total. Across all zoom levels: ~100TB total. This is served from S3/GCS with CDN caching. At 5M QPS, with 95% CDN hit rate, origin handles 250K QPS.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: Proximity Search — Finding Nearest Drivers

**Interviewer**: "A rider opens the Uber app. Walk me through how we find the 5 nearest drivers."

**You**: "The rider's app sends their location to our API: `GET /v1/nearby/drivers?lat=37.7749&lng=-122.4194&limit=5`. The proximity service computes the rider's geohash at precision 6 (approximately 1.2km x 0.6km cell): `9q8yyk`. It queries the in-memory index for all drivers in this cell. Geohash is the key in a hash map, and the value is a list of driver entries `{driver_id, lat, lng, last_updated}`.

But one cell might not have enough drivers, and there are boundary effects. So we also query the 8 neighboring cells: `9q8yyh`, `9q8yym`, `9q8yyn`, etc. That gives us all drivers within roughly a 3.6km x 1.8km area. We compute the actual Haversine distance from the rider to each driver, filter those beyond our max radius (say 5km), sort by distance, and return the top 5.

If we still don't have enough, we shorten the geohash prefix to length 5 (4.9km cells) and repeat. This is an expanding search — start precise, widen if needed."

**Interviewer**: "How does this work when Manhattan has 10,000 drivers per square kilometer and Wyoming has 0.1 per square kilometer?"

**You**: "In dense areas, a precision-6 geohash cell might contain thousands of drivers — but that's fine because we only need the 5 nearest. We scan the cell, compute distances, and use a min-heap of size 5 to track the closest. O(N) scan where N is drivers in the cell — typically hundreds, which takes microseconds.

In sparse areas, the initial cell is empty, so we expand: shorten the geohash prefix and query a larger area. This might require 2-3 expansions in very sparse areas, adding latency. To optimize: maintain a secondary index of 'active geohash cells' — cells that have at least one driver. When the initial cell is empty, jump directly to the nearest non-empty cell rather than iterating through empty ones.

An alternative is the quadtree approach, which naturally handles density variation — dense areas have deeper, smaller cells. But for production simplicity, geohash + expanding search is more common because it integrates cleanly with any key-value store."

**Interviewer**: "What about the ETA? The nearest driver by straight-line distance might be 20 minutes away by road."

**You**: "Great point — proximity by distance is a heuristic. For ride-sharing, what matters is ETA (estimated time of arrival), not Euclidean distance. After finding the 20 nearest drivers by distance, we compute road-based ETA for each using the routing engine (Dijkstra/A* on the road graph). Return the 5 with the lowest ETA. This is more expensive — each ETA calculation takes 5-50ms depending on distance — so we pre-filter with distance and only route-calculate for the candidates.

Uber also precomputes ETA grids: for each city, divide into 1km^2 cells and precompute approximate drive time between every pair of adjacent cells. This gives instant approximate ETAs for filtering, with exact routing only for the final top candidates."

**Interviewer**: "You mentioned sharding by city/region. How do you handle proximity queries at city boundaries?"

**You**: "Queries near shard boundaries need to fan out to multiple shards. If the rider is in San Francisco near the Oakland border, we query both the SF shard and the Oakland shard, merge results, and return the top-K. The routing layer knows the geographic boundaries of each shard and determines which shards to query based on the rider's location + search radius. Most queries (95%+) hit a single shard. The 5% that span boundaries have slightly higher latency due to fan-out but are functionally correct."

### Deep Dive Path 2: Real-Time Location Updates at Scale

**Interviewer**: "5 million drivers sending location updates every 4 seconds. Walk me through the data flow."

**You**: "Driver app sends location via WebSocket or HTTP: `{driver_id, lat, lng, heading, speed, timestamp}`. The location ingest service validates and publishes to Kafka — partitioned by city_id so all updates for one city go to the same partition (preserving ordering per driver).

A fleet of index updater workers consumes from Kafka. Each worker owns one or more city partitions. On receiving an update: (1) look up the driver's previous geohash in a hash map, (2) remove from old geohash cell, (3) compute new geohash, (4) insert into new geohash cell, (5) update the driver's entry with new coordinates and timestamp. All in-memory operations — each update takes ~1 microsecond.

The in-memory index is the primary data store for real-time queries. For durability, the Kafka topic retains events for 24 hours — on worker restart, it replays from the latest offset to rebuild the in-memory state. Location history (for trip reconstruction, analytics) is written to a time-series database (TimescaleDB or Cassandra) asynchronously."

**Interviewer**: "What if an index updater crashes? How do you maintain availability?"

**You**: "Two approaches. First, standby replicas: for each city partition, a standby consumer reads the same Kafka partition and maintains a shadow index. On primary failure, the standby takes over — failover time is the Kafka consumer rebalance time (~10-30 seconds). During failover, queries return stale results (last known positions) which is acceptable for a few seconds.

Second, we can shard more finely and use Kafka consumer groups. If the 'New York' partition is on one worker and it dies, Kafka rebalances the partition to another worker in the group. That worker replays recent events from Kafka (last 30 seconds) to rebuild the NYC index. The rebuild is fast: 30 seconds x 50K drivers / 4s = ~375K events to replay at 1M events/sec = <1 second."

**Interviewer**: "How do you handle stale locations? A driver's app crashes and stops sending updates."

**You**: "Each location entry has a timestamp. A background sweeper runs every 30 seconds, scanning the index for entries older than 60 seconds. Any driver not updated in 60 seconds is marked as 'inactive' and excluded from proximity query results (but kept in the index for 5 minutes in case they reconnect). After 5 minutes with no update, the entry is removed entirely. This prevents stale ghost drivers from appearing in search results."

### Deep Dive Path 3: Routing & Pathfinding

**Interviewer**: "How does the turn-by-turn navigation work? How do you compute routes?"

**You**: "The road network is modeled as a weighted directed graph. Nodes are intersections, edges are road segments. Edge weights encode: distance, speed limit, current traffic speed, turn costs, road type (highway vs. residential). The graph for the entire world has ~500M nodes and ~1B edges.

For single-source shortest path, Dijkstra's algorithm works but is too slow for long-distance routes (explores too many nodes). A* with geographic heuristic (straight-line distance to destination / max speed) prunes the search space significantly. But even A* is too slow for continental routes.

The production solution is Contraction Hierarchies (CH): a preprocessing step that adds 'shortcut' edges between important nodes (highways, major intersections). The preprocessed graph allows bidirectional Dijkstra to find the shortest path in milliseconds even for cross-country routes. Preprocessing takes hours but is done offline. Runtime query: 2-5ms for any pair of points, even thousands of kilometers apart."

**Interviewer**: "What about real-time traffic? Contraction Hierarchies are based on static weights."

**You**: "Standard CH doesn't handle dynamic weights well — re-preprocessing the hierarchy on every traffic change is too expensive. Two approaches: (1) Customizable Contraction Hierarchies (CCH) — separate the graph topology (preprocessed once) from the weights (customized per query). Weight customization takes ~1 second for the full graph, so we can update every 1-5 minutes as traffic data changes. (2) Hybrid approach — use CH for the backbone (highways, which have stable travel times) and A* for the first/last mile (local roads where traffic varies more). Google Maps reportedly uses a variant of this.

Traffic data comes from: (1) probe data — GPS traces from drivers/phones currently on the road (Uber/Google have millions of active probes), (2) historical patterns — Tuesday 8am on Highway 101 typically takes 25 minutes, (3) incident reports — accidents, road closures from Waze-style user reports."

**Interviewer**: "How do you serve map tiles for a smooth panning/zooming experience?"

**You**: "Map tiles follow the Slippy Map standard: each tile is identified by `{zoom}/{x}/{y}`. At zoom level 0, the world is one tile. At zoom level 18, it's 2^18 x 2^18 = 68 billion tiles. The client requests tiles for its current viewport and zoom level.

I'd use vector tiles (Mapbox Vector Tiles / MVT format — Protocol Buffers). The tile server reads geographic data from a spatial database (PostGIS), clips to the tile boundary, simplifies geometry at the appropriate zoom level, and encodes as PBF. Vector tiles are served through CDN — tiles change infrequently (daily rebuilds), and the CDN hit rate is 95%+.

Client-side rendering with WebGL/GPU: the client decodes the vector data and renders roads, buildings, labels, and styling on the GPU. This allows rotation, tilting, 3D buildings, dynamic styling (dark mode), and smooth zooming without re-fetching tiles."

---

## How Real Companies Built This

- **Google (S2 Geometry)**: Uses S2 cells — a hierarchical spatial indexing system based on a Hilbert curve mapping of the sphere to a 1D key space. S2 cells are the foundation of Google Maps' spatial queries. Unlike geohash (which has varying cell sizes at different latitudes), S2 cells have roughly equal area at the same level. Open-sourced: https://s2geometry.io/

- **Uber (H3)**: Developed H3, a hexagonal hierarchical spatial index. Hexagons have the property that all neighbors are equidistant from the center (unlike square geohash cells where diagonal neighbors are sqrt(2)x farther). Used for surge pricing, ETA estimation, and driver dispatch. Open-sourced: https://h3geo.org/ Blog: https://www.uber.com/blog/h3/

- **Mapbox**: Pioneered vector tile rendering. Their specification (MVT) is now an industry standard. Uses PostGIS for tile generation and a custom GL-based renderer for client-side rendering.

- **Lyft**: Uses a combination of geohash for coarse filtering and in-memory spatial indexes for fine-grained proximity. Their dispatch system computes ETAs using a road graph with real-time traffic overlays.

- **Key lesson**: Geohash is good enough for most applications. S2 and H3 are better for production systems with global coverage and precision requirements. For the interview, geohash is the right default answer — mention S2/H3 as production alternatives to show depth.

---

## The Complete Reference Design

### API Design
```
# Proximity search — find nearby places
GET /v1/nearby/places?lat=37.7749&lng=-122.4194&radius_m=5000&category=restaurant&limit=20
Response 200: {
  "results": [
    {
      "place_id": "place-abc",
      "name": "Best Pizza",
      "lat": 37.7751,
      "lng": -122.4180,
      "distance_m": 120,
      "category": "restaurant",
      "rating": 4.5
    }
  ],
  "next_cursor": "...",
  "search_geohash": "9q8yyk"
}

# Proximity search — find nearby drivers
GET /v1/nearby/drivers?lat=37.7749&lng=-122.4194&limit=5&vehicle_type=uberx
Response 200: {
  "drivers": [
    {
      "driver_id": "d-123",
      "lat": 37.7755,
      "lng": -122.4190,
      "distance_m": 85,
      "eta_seconds": 180,
      "heading": 45,
      "last_updated": "2026-02-12T10:30:00Z"
    }
  ]
}

# Location update (from driver app)
POST /v1/locations/update
Request: {
  "entity_id": "d-123",
  "lat": 37.7755,
  "lng": -122.4190,
  "heading": 45,
  "speed_mps": 12.5,
  "timestamp": "2026-02-12T10:30:00Z"
}
Response 200: { "ack": true }

# Routing
GET /v1/routes?origin_lat=37.77&origin_lng=-122.41&dest_lat=37.33&dest_lng=-121.89
Response 200: {
  "routes": [
    {
      "distance_m": 77000,
      "duration_seconds": 3600,
      "polyline": "encoded_polyline_string",
      "steps": [...]
    }
  ]
}
```

### Database Schema
```sql
-- Static places/POIs
CREATE TABLE places (
    place_id    VARCHAR(36) PRIMARY KEY,
    name        VARCHAR(500) NOT NULL,
    lat         DOUBLE NOT NULL,
    lng         DOUBLE NOT NULL,
    geohash     VARCHAR(12) NOT NULL,      -- precomputed for indexing
    category    VARCHAR(50),
    address     TEXT,
    rating      DECIMAL(2,1),
    metadata    JSONB,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

-- Geohash index for prefix-based proximity search
CREATE INDEX idx_places_geohash ON places(geohash);
CREATE INDEX idx_places_category_geohash ON places(category, geohash);

-- For PostGIS-based queries (alternative to geohash)
-- SELECT AddGeometryColumn('places', 'geom', 4326, 'POINT', 2);
-- CREATE INDEX idx_places_geom ON places USING GIST(geom);

-- Real-time entity locations (for analytics/history — hot path is in-memory)
CREATE TABLE location_history (
    entity_id   VARCHAR(36),
    timestamp   TIMESTAMP,
    lat         DOUBLE,
    lng         DOUBLE,
    geohash     VARCHAR(12),
    speed_mps   REAL,
    heading     SMALLINT,
    PRIMARY KEY (entity_id, timestamp)
) PARTITION BY RANGE (timestamp);

-- Road network graph (simplified — typically stored in custom binary format)
CREATE TABLE road_segments (
    segment_id  BIGINT PRIMARY KEY,
    start_node  BIGINT NOT NULL,
    end_node    BIGINT NOT NULL,
    distance_m  INTEGER,
    speed_limit_kmh SMALLINT,
    road_type   VARCHAR(20),    -- highway, primary, residential
    is_oneway   BOOLEAN DEFAULT FALSE,
    geometry    GEOMETRY(LINESTRING, 4326)
);

CREATE INDEX idx_road_start ON road_segments(start_node);
CREATE INDEX idx_road_end ON road_segments(end_node);
```

### Key Algorithms
```python
import math
from typing import List, Tuple, Dict
import heapq

# --- Geohash Implementation ---
BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"

def encode_geohash(lat: float, lng: float, precision: int = 6) -> str:
    """Encode lat/lng to geohash string."""
    lat_range = (-90.0, 90.0)
    lng_range = (-180.0, 180.0)
    bits = 0
    hash_value = 0
    result = []
    is_lng = True  # alternate between longitude and latitude bits

    while len(result) < precision:
        if is_lng:
            mid = (lng_range[0] + lng_range[1]) / 2
            if lng >= mid:
                hash_value = (hash_value << 1) | 1
                lng_range = (mid, lng_range[1])
            else:
                hash_value = hash_value << 1
                lng_range = (lng_range[0], mid)
        else:
            mid = (lat_range[0] + lat_range[1]) / 2
            if lat >= mid:
                hash_value = (hash_value << 1) | 1
                lat_range = (mid, lat_range[1])
            else:
                hash_value = hash_value << 1
                lat_range = (lat_range[0], mid)
        is_lng = not is_lng
        bits += 1
        if bits == 5:
            result.append(BASE32[hash_value])
            bits = 0
            hash_value = 0

    return "".join(result)


def get_neighbors(geohash: str) -> List[str]:
    """Return the 8 neighboring geohash cells."""
    # Decode center of the geohash cell, then encode at 8 offset positions
    # Simplified — production implementations use bit manipulation
    lat, lng = decode_geohash(geohash)
    precision = len(geohash)
    # Approximate cell dimensions
    lat_err = 180.0 / (2 ** (precision * 5 // 2))
    lng_err = 360.0 / (2 ** ((precision * 5 + 1) // 2))
    neighbors = []
    for dlat in [-lat_err, 0, lat_err]:
        for dlng in [-lng_err, 0, lng_err]:
            if dlat == 0 and dlng == 0:
                continue
            neighbors.append(
                encode_geohash(lat + dlat, lng + dlng, precision)
            )
    return neighbors


def decode_geohash(geohash: str) -> Tuple[float, float]:
    """Decode geohash to (lat, lng) center point."""
    lat_range = (-90.0, 90.0)
    lng_range = (-180.0, 180.0)
    is_lng = True
    for ch in geohash:
        val = BASE32.index(ch)
        for i in range(4, -1, -1):
            bit = (val >> i) & 1
            if is_lng:
                mid = (lng_range[0] + lng_range[1]) / 2
                if bit:
                    lng_range = (mid, lng_range[1])
                else:
                    lng_range = (lng_range[0], mid)
            else:
                mid = (lat_range[0] + lat_range[1]) / 2
                if bit:
                    lat_range = (mid, lat_range[1])
                else:
                    lat_range = (lat_range[0], mid)
            is_lng = not is_lng
    return (lat_range[0] + lat_range[1]) / 2, (lng_range[0] + lng_range[1]) / 2


# --- Proximity Search with Geohash ---
class ProximityIndex:
    """In-memory geohash-based spatial index."""
    def __init__(self):
        self.cells = {}         # geohash -> {entity_id: (lat, lng, metadata)}
        self.entity_cells = {}  # entity_id -> current geohash

    def update(self, entity_id: str, lat: float, lng: float, metadata=None):
        new_hash = encode_geohash(lat, lng, precision=6)
        # Remove from old cell
        old_hash = self.entity_cells.get(entity_id)
        if old_hash and old_hash in self.cells:
            self.cells[old_hash].pop(entity_id, None)
        # Insert into new cell
        if new_hash not in self.cells:
            self.cells[new_hash] = {}
        self.cells[new_hash][entity_id] = (lat, lng, metadata)
        self.entity_cells[entity_id] = new_hash

    def search_nearby(self, lat: float, lng: float, radius_m: float,
                      limit: int = 20) -> List:
        center_hash = encode_geohash(lat, lng, precision=6)
        candidate_cells = [center_hash] + get_neighbors(center_hash)

        # Collect all entities in candidate cells
        candidates = []
        for cell_hash in candidate_cells:
            if cell_hash in self.cells:
                for eid, (elat, elng, meta) in self.cells[cell_hash].items():
                    dist = haversine_distance(lat, lng, elat, elng)
                    if dist <= radius_m:
                        candidates.append((dist, eid, elat, elng, meta))

        # Return top K nearest
        candidates.sort(key=lambda x: x[0])
        return candidates[:limit]


def haversine_distance(lat1, lng1, lat2, lng2) -> float:
    """Distance in meters between two lat/lng points."""
    R = 6371000  # Earth's radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = (math.sin(dphi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
```

### Capacity Planning
| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| In-memory index (drivers) | 5M drivers x 100 bytes | 500MB (fits one machine, shard for availability) |
| In-memory index (POIs) | 200M x 500 bytes | 100GB (shard by region across 20 servers) |
| Location update throughput | 1.25M updates/sec | 3-5 Kafka partitions per city |
| Proximity query throughput | 500K QPS | 10-20 proximity servers (50K QPS each) |
| Map tile storage | ~100TB (all zoom levels, vector) | S3 + CDN |
| Map tile QPS | 5M QPS (95% CDN hit) | 250K QPS to tile origin |
| Road graph memory | 500M nodes x 20 bytes + 1B edges x 16 bytes | ~26GB (fits in RAM) |
| Routing query time | Contraction Hierarchy | 2-5ms per query |

---

## What Separates Senior from Staff from Principal

| Level | What they demonstrate | Example from this design |
|-------|----------------------|-------------------------|
| Senior | Understands geohash, designs basic proximity search, can describe tile serving | Implements geohash-based proximity with neighbor cell querying, serves map tiles from CDN |
| Staff | Compares geohash vs. quadtree vs. S2, designs real-time location update pipeline, reasons about density variation, discusses routing algorithms | Designs the Kafka-based location ingestion pipeline, explains Contraction Hierarchies for routing, handles the hot-path in-memory index with failover, discusses ETA computation |
| Principal | Designs the full platform (proximity + routing + tiles as integrated system), reasons about cell system choice (H3 hexagons for Uber use cases), thinks about cross-cutting concerns (privacy, data freshness SLAs, fleet management) | Proposes H3 for equal-distance neighbors in dispatch, designs privacy-preserving location handling, considers how the same infrastructure serves ride-sharing + food delivery + freight |

---

## Red Flags & Common Mistakes
- **Using raw lat/lng queries with distance formula on every POI**: O(N) scan doesn't scale. You need a spatial index (geohash, quadtree, R-tree, S2).
- **Forgetting the boundary problem with geohash**: If you don't query neighboring cells, you miss results near cell edges.
- **Storing real-time locations in PostgreSQL/PostGIS**: Too slow for 1M+ updates/sec. The hot path must be in-memory.
- **Ignoring density variation**: Manhattan has 10,000x more entities per km^2 than rural areas. Your solution must handle both.
- **Not mentioning vector tiles**: Raster tiles are the old approach. Modern map rendering uses vector tiles + client-side GPU rendering.
- **Conflating proximity search with routing**: "Find nearest" is Euclidean/Haversine distance. "Find fastest route" requires a graph algorithm on the road network. These are different systems.
- **Over-engineering the routing**: Unless the interviewer specifically asks about navigation, keep routing brief and focus on proximity search.
