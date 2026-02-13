# Design YouTube / Netflix (Video Streaming)

> **Companies**: Netflix, YouTube/Google, Amazon (Prime Video), Meta (Reels/Watch), Disney+, Uber | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: This question probes your understanding of large-scale media processing pipelines, adaptive bitrate streaming protocols, CDN architecture for video delivery, and the trade-offs between storage cost and user experience. The interviewer wants to see you reason about the complete lifecycle — upload, transcode, store, deliver — and the economics of video at scale (storage and bandwidth dominate costs).

---

## The First 5 Minutes — Scoping & Technical Clarifications

**Questions that show the interviewer you know what you're doing:**

- "Are we focusing on the upload/transcoding pipeline, the playback/delivery system, or the recommendation engine? These are very different systems."
- "What's the scale? YouTube-level (500 hours uploaded per minute) or a smaller service?"
- "What's the playback latency target? For VOD, initial buffering under 2 seconds? For live streaming, end-to-end under 5 seconds?"
- "Do we need adaptive bitrate streaming? What resolution range — 360p to 4K?"
- "What's the expected concurrent viewer count for a single popular video? Millions (like a Super Bowl stream)?"
- "Global or single-region delivery?"
- "Do we need DRM (Digital Rights Management)? This adds significant complexity."
- "What's our storage budget constraint? Video at scale is a storage cost problem."

### Working Assumptions
| Parameter | Value | Derivation |
|-----------|-------|------------|
| DAU | 200M | Large-scale video platform |
| Videos watched/user/day | 10 | Average engagement |
| Average video duration | 5 minutes | Mix of short and long content |
| Total daily video views | 2B | 200M x 10 |
| Concurrent streams (peak) | 10M | ~5% of DAU at peak hour |
| Video uploads/day | 500K | User-generated content platform |
| Storage per video (all renditions) | 2GB avg | 1080p source transcoded to 6 renditions |
| Total storage | 1EB+ (exabyte) | Years of accumulated content |
| Playback start latency | < 2 seconds | Time to first frame |
| Adaptive bitrate range | 240p (200kbps) to 4K (20Mbps) | 6-8 renditions per video |
| CDN bandwidth (peak) | 100+ Tbps | Video is bandwidth-intensive |

---

## High-Level Design (Brief — 5 minutes)

```
UPLOAD PATH:
                                                    +------------------+
User uploads video                                  |  Blob Storage    |
    |                                               |  (S3/GCS)        |
    v                                               |  - Original      |
+---------------+     +------------------+          |  - Transcoded    |
| Upload Service|---->| Message Queue    |--------->|    renditions    |
| (chunked      |     | (SQS/Kafka)     |          +------------------+
|  upload, S3)  |     +--------+---------+
+---------------+              |
                    +----------v-----------+
                    | Transcoding Pipeline |
                    | (FFmpeg workers,     |
                    |  GPU-accelerated)    |
                    | - Multiple bitrates  |
                    | - Generate thumbnails|
                    | - Extract metadata   |
                    +-----------+----------+
                                |
                    +-----------v----------+
                    | Video Metadata DB    |
                    | (PostgreSQL/DynamoDB)|
                    +----------------------+

PLAYBACK PATH:
User clicks play
    |
    v
+---------------+     +------------------+     +------------------+
| Client Player |---->| API Server       |---->| Video Metadata   |
| (ABR player,  |     | (manifest URL,   |     | DB               |
|  HLS/DASH)    |     |  auth, metering) |     +------------------+
+-------+-------+     +------------------+
        |
        v  (fetch manifest, then segments)
+------------------+     +------------------+
| CDN Edge PoP     |---->| Blob Storage     |
| (cached segments)|     | (origin)         |
+------------------+     +------------------+
```

**Why this architecture?**: The upload and playback paths are completely decoupled. Upload is a write-heavy, compute-intensive pipeline (transcoding can take 10-100x real-time). Playback is a read-heavy, bandwidth-intensive delivery problem. Separating them allows independent scaling — you scale transcoding workers for upload volume and CDN capacity for playback volume.

---

## Core Concepts Deep Dive

### Concept 1: Adaptive Bitrate Streaming (ABR) — HLS & DASH

**What it is**: Instead of streaming a single video file, the video is split into small segments (2-10 seconds each), each encoded at multiple bitrates/resolutions. A manifest file lists all available renditions and their segment URLs. The client player measures its available bandwidth and switches between renditions segment-by-segment.

**How it applies here**: A 5-minute video is split into 150 segments (2 seconds each), each encoded at 6 quality levels (240p/200kbps, 360p/500kbps, 480p/1Mbps, 720p/2.5Mbps, 1080p/5Mbps, 4K/20Mbps). The manifest (M3U8 for HLS, MPD for DASH) is a text file listing all 900 segment URLs (150 segments x 6 renditions). The player starts at a low bitrate for fast startup, then adapts upward as it measures bandwidth.

**The math/mechanics**: HLS manifest example:
```
#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=500000,RESOLUTION=640x360
360p/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720
720p/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080
1080p/playlist.m3u8
```
Each rendition's playlist then lists individual segments. Segment size trade-off: smaller segments (2s) = faster quality switching but more HTTP requests and larger manifest; larger segments (10s) = fewer requests but slower adaptation.

**Common misconception**: Candidates describe "progressive download" (one file, one quality) instead of ABR. ABR is the standard for modern video. Also, candidates forget that the client does the ABR switching logic — the server just serves segments. The intelligence is in the player's bandwidth estimation algorithm.

### Concept 2: Video Transcoding Pipeline

**What it is**: The uploaded video (which could be any codec, resolution, frame rate) must be transcoded into all target renditions. Transcoding is CPU/GPU-intensive — encoding 1 minute of 4K H.264 takes ~5-10 minutes on a modern CPU, ~30 seconds on a GPU.

**How it applies here**: The transcoding pipeline is a DAG of jobs: (1) validate and probe the input (codec, resolution, duration), (2) split into chunks for parallel transcoding (split at keyframes), (3) transcode each chunk into each rendition in parallel, (4) concatenate transcoded chunks, (5) generate segment files and manifests, (6) create thumbnails and preview sprites, (7) update metadata DB with URLs.

**The math/mechanics**: 500K uploads/day, average 5 minutes. Each video produces 6 renditions. Total transcoding work: 500K x 5 min x 6 = 15M minutes of transcoding per day. With GPU workers doing 10x real-time: need 15M / (24 x 60 x 10) = ~1,042 concurrent GPU workers. With chunked parallel transcoding (split into 30-second chunks), a 5-minute video processes in ~30 seconds instead of 50 minutes — latency vs. throughput trade-off.

**Common misconception**: Candidates say "just use FFmpeg" without discussing parallelization. A single FFmpeg process transcoding a 1-hour video at 6 renditions would take hours. The key is splitting the video into chunks at keyframe boundaries and transcoding them in parallel across many workers.

### Concept 3: Video Storage Economics

**What it is**: Video storage is the dominant cost at scale. A single 5-minute video at 6 renditions = ~2GB. With 500K uploads/day = 1PB/day of new storage. Over a year, that's 365PB. At $0.023/GB/month (S3 standard), that's $8.4M/month for storage alone.

**How it applies here**: Tiered storage is essential. Hot content (viewed in the last 30 days) stays on fast storage (S3 Standard or SSD-backed). Warm content (30-180 days) moves to S3 Infrequent Access (~60% cheaper). Cold content (>180 days, rarely viewed) moves to S3 Glacier (~90% cheaper). Transcoding optimization: don't generate 4K rendition for a 360p source video. Don't store renditions nobody watches — if analytics show 240p gets <0.1% of views, stop generating it.

**The math/mechanics**: Storage cost optimization: if 80% of views go to content uploaded in the last 30 days, and that's only 5% of total content, you can keep 5% on Standard and 95% on cheaper tiers. Cost reduction: from $8.4M/month to ~$2M/month. Also, encoding efficiency: H.265 (HEVC) provides ~50% bitrate savings over H.264 at the same quality but with 10x encoding cost. AV1 provides ~30% savings over H.265 but with even higher encoding cost. The trade-off: more CPU spend on encoding vs. less storage and bandwidth spend.

**Common misconception**: Candidates focus on compute cost and ignore storage/bandwidth. At YouTube scale, bandwidth and storage dominate. A 4K video segment at 20Mbps viewed by 1M users = 20 Tbps of bandwidth for a single video. Bandwidth costs typically exceed storage costs.

### Concept 4: CDN Strategy for Video

**What it is**: Video segments are the perfect CDN workload — immutable, heavily accessed, and latency-sensitive (buffering kills user experience). The CDN caches segments at edge PoPs. Popular videos (viral content) have near-100% cache hit rates. Long-tail content (old, unpopular videos) has low hit rates and may require origin fetch.

**How it applies here**: The CDN stores video segments, not complete videos. Each segment (2 seconds, ~1-5MB depending on bitrate) is independently cacheable with a long TTL (days to weeks — segments are immutable). The manifest file has a shorter TTL or is served from the API server (it's small and may change if renditions are added). For popular videos, segments are pre-warmed to major PoPs via a push CDN model.

**Common misconception**: Candidates try to stream the entire video from origin through the CDN. Modern CDN-based video delivery serves individual segments as regular HTTP GET requests. The player fetches segments sequentially — it's just HTTP, not a persistent streaming connection. This is why HLS/DASH won over RTMP — HTTP infrastructure (CDNs, load balancers, proxies) already exists.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: Upload & Transcoding Pipeline

**Interviewer**: "A user uploads a 10-minute 4K video. Walk me through everything that happens until it's playable."

**You**: "The client uploads in chunks using a multipart upload protocol. Each chunk (say 5MB) is uploaded independently — this allows resume on network failure. The upload service writes chunks to S3 as they arrive. Once all chunks are uploaded, it sends a 'video ready' event to our message queue (SQS or Kafka).

A transcoding orchestrator picks up the event. Step 1: probe the source — FFprobe extracts codec, resolution, frame rate, duration. Step 2: create a transcoding plan — for a 4K source, we generate 6 renditions (240p through 4K). Step 3: split the source into ~30-second chunks at keyframe boundaries (GOP-aligned split to avoid re-encoding artifacts). Step 4: for each chunk x each rendition, submit a transcoding job. That's 20 chunks x 6 renditions = 120 parallel jobs. Each job runs FFmpeg on a GPU worker: `ffmpeg -i chunk_05.mp4 -vcodec h264 -b:v 2500k -s 1280x720 chunk_05_720p.mp4`.

Step 5: as chunks complete, concatenate them per rendition and segment into HLS/DASH segments (2-second segments). Step 6: generate the master manifest and per-rendition playlists. Step 7: upload all segments and manifests to S3. Step 8: update the metadata DB — mark the video as 'ready' and store manifest URL. Step 9: trigger CDN pre-warming for the manifest and first few segments. Total time: 2-3 minutes for a 10-minute video with enough GPU workers."

**Interviewer**: "What if a transcoding job fails mid-way? Say the GPU worker crashes."

**You**: "Each job is idempotent — the output is deterministic from the input chunk + encoding parameters. The orchestrator uses a job queue with at-least-once delivery (SQS with visibility timeout). If a worker crashes, the message becomes visible again after the timeout (e.g., 5 minutes) and another worker picks it up. The new worker re-transcodes the chunk from the original source on S3 — no state to recover.

For the overall pipeline, I use a state machine (AWS Step Functions or Temporal) that tracks which chunks have been transcoded for which renditions. If a job fails 3 times, the pipeline marks that rendition as failed but continues with others — the video becomes available in fewer renditions rather than being completely blocked. We alert on failure rate and have a dead-letter queue for investigation."

**Interviewer**: "How do you handle different input formats? Someone uploads an AVI from 2005 vs. a ProRes 4K file."

**You**: "The probe step is critical. FFprobe tells us the container format, codec, resolution, frame rate, color space, and audio format. The transcoding plan adapts: for a 360p AVI input, we only generate 240p and 360p renditions — no point upscaling. For a ProRes 4K HDR input, we generate all renditions plus an HDR-to-SDR tone mapping step. We also normalize audio to AAC stereo at 128kbps (or multi-track for 5.1 surround if source has it). The key principle: the output renditions are always a standardized set — H.264 for broad compatibility, with H.265 and AV1 for modern devices — regardless of the input format."

**Interviewer**: "Cost. You mentioned 1,042 GPU workers. How do you optimize this?"

**You**: "Three strategies. First, spot/preemptible instances — transcoding is fault-tolerant (retry on interruption), so spot instances at 60-70% discount are ideal. Second, encoding ladder optimization — Netflix's per-title encoding approach: instead of fixed bitrate targets, use VMAF (perceptual quality metric) to find the minimum bitrate that achieves target quality per video. An animated video at 720p might need only 1.5Mbps vs. 2.5Mbps for an action movie. This reduces storage and bandwidth by 20-30%. Third, lazy transcoding for long-tail content — don't pre-generate all renditions for every video. Start with 360p and 720p only; if the video gets popular, trigger on-demand transcoding for 1080p and 4K. This reduces initial compute by ~60%."

### Deep Dive Path 2: Playback & Adaptive Bitrate

**Interviewer**: "User hits play. What happens end-to-end until they see the first frame?"

**You**: "The client calls our API: `GET /api/v1/videos/{id}/manifest`. The API server checks authorization (is the user allowed to view this video?), looks up the manifest URL from the metadata DB, and returns a signed CDN URL for the manifest file. The CDN URL has a limited TTL (1 hour) and is bound to the user's IP for DRM/geo-restriction.

The client fetches the manifest from CDN. The ABR player parses it, sees 6 renditions, and starts with the lowest bitrate (240p/200kbps) for fast startup. It fetches the first segment (2 seconds at 200kbps = 50KB) — this downloads in <100ms over any reasonable connection. The player decodes and displays the first frame — time to first frame is typically under 1 second.

While playing the first segment, the player measures download throughput. If bandwidth is 10Mbps, it switches to 1080p for the second segment. Adaptive bitrate logic: `next_bitrate = min(measured_bandwidth * 0.8, highest_available)`. The 0.8 factor is a safety margin to avoid buffering."

**Interviewer**: "The user is on a train, bandwidth fluctuates between 1Mbps and 10Mbps. How does ABR handle this?"

**You**: "The ABR algorithm must be conservative to avoid buffering but not so conservative that quality is permanently low. Production players use buffer-based ABR: the decisions are based on the current buffer level, not just bandwidth. If the buffer is >10 seconds of content, the player is safe to switch to a higher bitrate. If the buffer drops below 5 seconds, switch down aggressively. Below 2 seconds, switch to the lowest bitrate. This buffer-based approach is more stable than bandwidth-based — it naturally smooths out fluctuations.

Netflix's ABR algorithm also considers historical bandwidth (exponential moving average) and reduces the number of quality switches — frequent switching is visually jarring. They target a minimum of 10 seconds at each quality level before switching."

**Interviewer**: "What about seek? User jumps to 45 minutes into a movie."

**You**: "When the user seeks, the player calculates which segment corresponds to the target timestamp (segment_index = floor(target_time / segment_duration)). It fetches that segment from CDN at the current bitrate. If the segment isn't keyframe-aligned precisely, the player fetches the nearest keyframe and decodes forward to the exact timestamp. This is why shorter GOP (Group of Pictures) intervals improve seek accuracy at the cost of compression efficiency. For a 2-second segment with a keyframe at the start, seek precision is 2 seconds. The CDN likely has the popular segment cached; for cold content, it's a cache miss with origin fetch — adds 100-200ms."

### Deep Dive Path 3: Scale, Storage & Cost

**Interviewer**: "YouTube has 800 million videos. How do you handle storage at that scale?"

**You**: "At 2GB average per video (all renditions), that's 1.6EB total. At $0.023/GB/month S3 Standard, that's $36.8M/month — unsustainable. Three approaches:

First, tiered storage. 80/20 rule applies: 80% of views go to 5% of videos. Keep those 5% (40M videos, 80PB) on fast storage. Move the rest to S3 Infrequent Access ($0.0125/GB/month) or Glacier ($0.004/GB/month). This alone cuts costs 4-5x.

Second, intelligent encoding. Not all renditions are needed for all videos. If a video is only viewed at 480p and below (90% of videos), delete the 1080p and 4K renditions. Per-title encoding (Netflix approach) using VMAF quality targets reduces bitrates 20-30% with no perceptual quality loss.

Third, codec migration. Re-encode popular content from H.264 to H.265 (50% bitrate reduction) or AV1 (70% reduction vs. H.264). The re-encoding costs compute upfront but saves ongoing storage and bandwidth. At Netflix scale, the bandwidth savings alone justify the compute cost within weeks."

**Interviewer**: "What about live streaming? How does the architecture change?"

**You**: "Live streaming flips the pipeline. Instead of pre-processing, we're encoding in real-time. The source (camera/encoder) sends a stream to our ingest servers via RTMP or SRT protocol. The ingest server: (1) transcodes to multiple renditions in real-time using GPU, (2) segments the output into 2-6 second HLS/DASH segments, (3) uploads segments to origin immediately, (4) updates the live manifest to append the new segment.

The manifest for live has a sliding window — it lists the last N segments (typically 3-5). The CDN caches segments with short TTL (equal to segment duration). The manifest is NOT cached or has a very short TTL (1s) so players always get the latest.

End-to-end latency: glass-to-glass (camera to viewer screen) is 5-30 seconds with HLS, 2-5 seconds with Low-Latency HLS (LL-HLS) using partial segments and PUSH/PRELOAD hints, and sub-second with WebRTC for truly interactive use cases (like Twitch's low-latency mode)."

**Interviewer**: "What if 10 million people are watching the same live event? How do you handle that concurrent load?"

**You**: "This is where CDN edge caching shines. All 10M viewers watch the same content, just slightly time-shifted. Each edge PoP caches segments as they arrive. The origin only sends each segment once per PoP (or once per shield region), and the PoP serves it to all local viewers. 10M viewers / 200 PoPs = 50K viewers per PoP on average, each consuming ~5Mbps (1080p) = 250Gbps per PoP peak. Large PoPs are provisioned for this.

The manifest is the bottleneck — every player polls for the updated manifest every segment duration (2-6 seconds). 10M users polling every 4 seconds = 2.5M requests/sec for the manifest alone. This MUST be served from edge cache with a TTL of 1-2 seconds, not from origin."

---

## How Real Companies Built This

- **Netflix**: Uses a multi-step encoding pipeline with per-title optimization. Each video gets its own encoding ladder based on content complexity — simple cartoons get lower bitrates than action movies at the same perceptual quality. Uses AWS for transcoding (EC2 GPU instances) and their own CDN (Open Connect) for delivery. Encodes in H.264, H.265, VP9, and AV1 depending on client device. Blog: https://netflixtechblog.com/ — their encoding posts are essential reading.

- **YouTube**: Processes 500+ hours of video per minute. Uses a DAG-based pipeline where upload triggers a cascade of processing jobs (transcoding, thumbnail generation, content moderation via ML, copyright detection via Content ID). YouTube pioneered VP9 and now AV1 for bandwidth savings. They serve from Google's global CDN with deep ISP peering.

- **Twitch**: Optimized for low-latency live streaming. Uses a modified HLS with smaller segments and preloading. Their ingest system handles millions of concurrent broadcasters each sending a unique live stream — unlike Netflix/YouTube where a single asset is consumed by many viewers.

- **Key lesson**: At scale, video is a cost optimization problem. The systems are built to minimize storage (smart encoding ladders), bandwidth (efficient codecs, CDN caching), and compute (lazy transcoding, spot instances). The viewing experience (time to first frame, no buffering, fast quality adaptation) is solved primarily by the ABR player and CDN — not the backend.

---

## The Complete Reference Design

### API Design
```
# Upload initiation
POST /v1/videos/upload
Request: {
  "title": "My Video",
  "description": "...",
  "file_size_bytes": 524288000,
  "content_type": "video/mp4"
}
Response 200: {
  "upload_id": "upload-abc123",
  "upload_url": "https://upload.cdn.example.com/...",  # presigned S3 URL
  "chunk_size_bytes": 5242880  # 5MB chunks
}

# Get video manifest for playback
GET /v1/videos/{video_id}/manifest
Headers: Authorization: Bearer <token>
Response 200: {
  "manifest_url": "https://cdn.example.com/v/abc123/master.m3u8?token=signed&expires=...",
  "thumbnail_url": "https://cdn.example.com/v/abc123/thumb.jpg",
  "duration_seconds": 300,
  "available_renditions": ["240p", "360p", "480p", "720p", "1080p"]
}

# Video metadata
GET /v1/videos/{video_id}
Response 200: {
  "id": "abc123",
  "title": "My Video",
  "status": "ready",      # uploading | processing | ready | failed
  "duration": 300,
  "views": 1234567,
  "renditions": [
    {"resolution": "720p", "bitrate": 2500000, "codec": "h264"},
    {"resolution": "1080p", "bitrate": 5000000, "codec": "h264"}
  ]
}
```

### Database Schema
```sql
-- Video metadata (PostgreSQL or DynamoDB)
CREATE TABLE videos (
    video_id        VARCHAR(36) PRIMARY KEY,
    user_id         VARCHAR(36) NOT NULL,
    title           VARCHAR(500),
    description     TEXT,
    status          VARCHAR(20) DEFAULT 'uploading',
    duration_ms     INTEGER,
    source_codec    VARCHAR(50),
    source_width    INTEGER,
    source_height   INTEGER,
    manifest_url    VARCHAR(500),
    thumbnail_url   VARCHAR(500),
    storage_bytes   BIGINT,
    view_count      BIGINT DEFAULT 0,
    created_at      TIMESTAMP DEFAULT NOW(),
    published_at    TIMESTAMP,
    storage_tier    VARCHAR(20) DEFAULT 'hot'
);

CREATE INDEX idx_videos_user ON videos(user_id, created_at DESC);
CREATE INDEX idx_videos_status ON videos(status) WHERE status != 'ready';

-- Renditions
CREATE TABLE video_renditions (
    video_id        VARCHAR(36) REFERENCES videos(video_id),
    rendition_id    VARCHAR(50),
    resolution      VARCHAR(10),        -- "720p", "1080p"
    bitrate_bps     INTEGER,
    codec           VARCHAR(20),        -- "h264", "h265", "av1"
    segment_count   INTEGER,
    segment_duration_ms INTEGER,
    manifest_path   VARCHAR(500),
    total_bytes     BIGINT,
    created_at      TIMESTAMP,
    PRIMARY KEY (video_id, rendition_id)
);

-- Transcoding jobs
CREATE TABLE transcoding_jobs (
    job_id          VARCHAR(36) PRIMARY KEY,
    video_id        VARCHAR(36) REFERENCES videos(video_id),
    chunk_index     INTEGER,
    rendition_id    VARCHAR(50),
    status          VARCHAR(20),        -- queued | running | completed | failed
    worker_id       VARCHAR(50),
    started_at      TIMESTAMP,
    completed_at    TIMESTAMP,
    retry_count     INTEGER DEFAULT 0,
    error_message   TEXT
);

CREATE INDEX idx_jobs_status ON transcoding_jobs(status, created_at);
```

### Key Algorithms
```python
import subprocess
import json
from dataclasses import dataclass

@dataclass
class Rendition:
    name: str
    width: int
    height: int
    bitrate: int    # bps
    codec: str

ENCODING_LADDER = [
    Rendition("240p",   426,  240,   200_000, "h264"),
    Rendition("360p",   640,  360,   500_000, "h264"),
    Rendition("480p",   854,  480, 1_000_000, "h264"),
    Rendition("720p",  1280,  720, 2_500_000, "h264"),
    Rendition("1080p", 1920, 1080, 5_000_000, "h264"),
    Rendition("4k",    3840, 2160, 20_000_000, "h264"),
]

def create_encoding_plan(source_width, source_height):
    """Only generate renditions up to source resolution."""
    return [r for r in ENCODING_LADDER
            if r.width <= source_width and r.height <= source_height]


def transcode_chunk(input_path, output_path, rendition: Rendition):
    """Transcode a single video chunk to a target rendition."""
    cmd = [
        "ffmpeg", "-i", input_path,
        "-vcodec", rendition.codec,
        "-b:v", str(rendition.bitrate),
        "-s", f"{rendition.width}x{rendition.height}",
        "-acodec", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        "-y", output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {result.stderr}")
    return output_path


def generate_hls_segments(transcoded_path, output_dir, segment_duration=2):
    """Split transcoded file into HLS segments."""
    cmd = [
        "ffmpeg", "-i", transcoded_path,
        "-codec", "copy",
        "-f", "hls",
        "-hls_time", str(segment_duration),
        "-hls_list_size", "0",          # keep all segments in playlist
        "-hls_segment_filename", f"{output_dir}/segment_%04d.ts",
        f"{output_dir}/playlist.m3u8"
    ]
    subprocess.run(cmd, check=True)


def generate_master_manifest(video_id, renditions):
    """Generate HLS master playlist listing all renditions."""
    lines = ["#EXTM3U"]
    for r in renditions:
        lines.append(
            f"#EXT-X-STREAM-INF:BANDWIDTH={r.bitrate},"
            f"RESOLUTION={r.width}x{r.height}"
        )
        lines.append(f"{r.name}/playlist.m3u8")
    return "\n".join(lines)


# ABR bandwidth estimation (client-side, simplified)
class ABRController:
    """Simplified adaptive bitrate controller using buffer level."""
    def __init__(self, renditions: list):
        self.renditions = sorted(renditions, key=lambda r: r.bitrate)
        self.current_index = 0  # start at lowest
        self.bandwidth_samples = []

    def on_segment_downloaded(self, segment_bytes, download_time_ms):
        bw = (segment_bytes * 8 * 1000) / download_time_ms  # bps
        self.bandwidth_samples.append(bw)
        if len(self.bandwidth_samples) > 10:
            self.bandwidth_samples.pop(0)

    def select_rendition(self, buffer_level_seconds):
        avg_bw = sum(self.bandwidth_samples) / len(self.bandwidth_samples) \
            if self.bandwidth_samples else 0
        safe_bw = avg_bw * 0.8  # 80% safety margin

        if buffer_level_seconds < 2:
            # Emergency: drop to lowest
            self.current_index = 0
        elif buffer_level_seconds < 5:
            # Conservative: drop one level if possible
            self.current_index = max(0, self.current_index - 1)
        else:
            # Normal: pick highest rendition that fits bandwidth
            for i, r in enumerate(self.renditions):
                if r.bitrate <= safe_bw:
                    self.current_index = i
        return self.renditions[self.current_index]
```

### Capacity Planning
| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Transcoding workers (GPU) | 500K videos/day x 5 min x 6 renditions / (24h x 60min x 10x speed) | ~1,042 GPU workers |
| Storage (new content/day) | 500K x 2GB avg | ~1PB/day |
| Storage (total, with tiering) | 80PB hot + 800PB cold | ~880PB total |
| CDN bandwidth (peak) | 10M concurrent x 5Mbps avg | 50Tbps |
| Manifest requests | 10M concurrent / 4s poll interval | 2.5M requests/sec |
| Origin bandwidth (CDN miss) | 50Tbps x 5% miss rate | 2.5Tbps from origin |
| Metadata DB QPS | 2B views/day x 2 queries each / 86,400 | ~46K QPS |
| Upload bandwidth | 500K x 500MB avg / 86,400 | ~2.9GB/s = ~23Gbps |

---

## What Separates Senior from Staff from Principal

| Level | What they demonstrate | Example from this design |
|-------|----------------------|-------------------------|
| Senior | Understands ABR, can describe upload->transcode->serve flow, reasonable capacity estimates | Designs the basic pipeline, picks HLS, describes segment-based delivery via CDN |
| Staff | Designs fault-tolerant transcoding pipeline, reasons about encoding ladders and codec trade-offs, considers storage cost optimization, discusses live vs. VOD differences | Adds per-title encoding with VMAF, lazy transcoding for long-tail, tiered storage lifecycle, designs robust job orchestration with Temporal/Step Functions |
| Principal | Thinks about system economics at scale (bandwidth costs > compute costs), designs for codec migration (H.264 -> AV1 fleet-wide re-encoding), considers DRM architecture, reasons about ISP peering (Netflix Open Connect model) | Proposes building custom CDN hardware inside ISPs, designs incremental codec rollout strategy, considers content moderation pipeline integration, thinks about multi-tenant architecture for a video platform-as-a-service |

---

## Red Flags & Common Mistakes
- **Describing progressive download instead of ABR**: Modern video streaming uses segmented adaptive bitrate (HLS/DASH). Saying "stream the MP4 file" is a red flag.
- **No transcoding pipeline**: The video must be transcoded into multiple renditions. You can't serve the original upload directly.
- **Ignoring storage costs**: At scale, storage and bandwidth dominate. Not discussing tiered storage shows lack of practical experience.
- **Single segment duration without trade-off discussion**: Segment size (2s vs. 10s) is a key trade-off between adaptation speed and overhead.
- **No fault tolerance in transcoding**: Transcoding workers crash. The pipeline must handle retries, partial failures, and dead-letter queues.
- **Forgetting about seek**: How does seek work with segmented video? Keyframe alignment matters.
- **Not mentioning CDN for delivery**: Video without CDN means every viewer hits origin. This is a non-starter at scale.
