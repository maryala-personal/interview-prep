# Design a Notification System

> **Companies**: Meta, Google, Amazon, Uber, Netflix, Airbnb, LinkedIn | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you design a multi-channel delivery system (push, email, SMS, in-app) with reliable delivery guarantees, handle rate limiting and user preferences, and reason about the ordering/deduplication challenges of distributed event processing? This problem tests your ability to design a platform that other teams integrate with — it's as much about API design and extensibility as it is about infrastructure.

---

## The First 5 Minutes — Scoping & Technical Clarifications

**These are the questions that make the interviewer think "this person knows what they're doing."**

- "What notification channels do we need? Push (APNs/FCM), email, SMS, in-app? All of them or a subset?"
- "What's the throughput? How many notifications per second across all channels? Are there burst scenarios (e.g., flash sale notifications to 100M users)?"
- "What's the delivery latency SLA? Real-time (< 1 second for push) or near-real-time (< 5 minutes for email)?"
- "What's the delivery guarantee? At-least-once, at-most-once, or exactly-once? Push notifications are inherently at-most-once (APNs/FCM don't guarantee delivery)."
- "Do we need user preference management? Users should be able to opt out of specific notification types per channel."
- "What about rate limiting? We can't send 50 push notifications in a minute to the same user — that's spam."
- "Do we need templating and personalization? Or are notifications pre-formatted by the sending service?"
- "Is this a multi-tenant platform (multiple internal teams send notifications through it) or a single application's notification system?"

### Working Assumptions

| Parameter | Value |
|-----------|-------|
| DAU | 500M |
| Notifications sent/day | 10B (across all channels) |
| Peak notification rate | 500K/sec (burst during events) |
| Channels | Push (APNs/FCM), Email, SMS, In-App |
| Push delivery latency | p99 < 1 sec |
| Email delivery latency | p99 < 5 min |
| SMS delivery latency | p99 < 30 sec |
| Availability | 99.99% |

**The math**:
- 10B notifications/day = ~116K/sec average, 500K/sec peak
- Push: ~60% of volume = 6B/day. APNs/FCM rate limits: ~100K/sec per connection, need ~5 connections.
- Email: ~30% = 3B/day. At 500 emails/sec per SMTP connection, need ~700 connections (or use SES/SendGrid).
- SMS: ~10% = 1B/day. At ~100 SMS/sec per Twilio connection, need ~100 connections.
- Storage: notification logs — 10B x 200 bytes = 2 TB/day.

---

## High-Level Design (Keep it brief — 5 minutes max)

```
┌──────────────┐     ┌──────────────┐
│  Service A   │     │  Service B   │  ← Internal services that trigger notifications
│  (orders)    │     │  (social)    │
└──────┬───────┘     └──────┬───────┘
       │                    │
       └────────┬───────────┘
                │
       ┌────────▼────────┐
       │  Notification   │  ← API gateway: validates, deduplicates, checks preferences
       │  Service API    │
       └────────┬────────┘
                │
       ┌────────▼────────┐
       │  Message Queue  │  ← Kafka: buffers burst traffic, ensures durability
       │  (Kafka)        │
       └────────┬────────┘
                │
       ┌────────▼────────┐
       │  Notification   │  ← Applies templates, user preferences, rate limits, dedup
       │  Processor      │
       └────────┬────────┘
                │
    ┌───────────┼───────────┬──────────────┐
    │           │           │              │
┌───▼───┐  ┌───▼───┐  ┌───▼───┐   ┌──────▼──────┐
│ Push  │  │ Email │  │ SMS   │   │  In-App     │
│ Worker│  │ Worker│  │ Worker│   │  Worker     │
│(APNs/ │  │(SES/  │  │(Twilio│   │ (WebSocket  │
│ FCM)  │  │SendGrid)│ │ /SNS)│   │  /SSE)     │
└───────┘  └───────┘  └───────┘   └─────────────┘
```

**Why this architecture?** The key insight is that this is a multi-channel routing problem. The Notification Service API provides a single interface for all internal teams ("send notification X to user Y via channels Z"). Kafka decouples the producers (services that trigger notifications) from the consumers (channel-specific workers), absorbing traffic bursts. The processor layer is where the intelligence lives — preference checks, dedup, rate limiting, and template rendering happen before the message is dispatched to channel-specific workers.

---

## Core Concepts Deep Dive

### Concept 1: Message Queue as the Backbone — Kafka Partitioning Strategy

**What it is**: Kafka sits between the notification API and the processors. It serves three purposes: (1) absorb burst traffic (500K/sec spikes during flash sales), (2) ensure durability (messages aren't lost if a processor crashes), and (3) enable independent scaling of each channel.

**How it applies here**:
- **Topic per channel**: `notifications.push`, `notifications.email`, `notifications.sms`, `notifications.inapp`. Each channel scales independently.
- **Partitioning**: Partition by `user_id`. This ensures all notifications for a single user go to the same partition, enabling per-user rate limiting and ordering without coordination.
- **Consumer groups**: Each channel has its own consumer group. Push workers consume from `notifications.push`, email workers from `notifications.email`, etc.

**The math/mechanics**:
- 500K/sec peak → with 100 partitions per topic, each partition handles 5K/sec — well within Kafka's per-partition throughput.
- Consumer lag target: < 10 seconds. Monitor with Kafka consumer group lag metrics.
- Message size: ~500 bytes (notification payload + metadata). At 500K/sec: 250 MB/sec write throughput to Kafka.

**Common misconception**: Candidates use a single Kafka topic for all channels. This means a slow email delivery can back up push notifications. Separate topics per channel give independent backpressure and scaling.

### Concept 2: Preference Management and Notification Routing

**What it is**: Users can control which notifications they receive and through which channels. This is a matrix: (notification_type) x (channel) x (enabled/disabled).

**How it applies here**:
```
User 12345's preferences:
{
    "order_updates": {"push": true, "email": true, "sms": false},
    "friend_requests": {"push": true, "email": false, "sms": false},
    "marketing": {"push": false, "email": true, "sms": false}
}
```
- The processor checks preferences BEFORE dispatching to channel workers. This prevents sending unwanted notifications.
- Preferences are cached in Redis (user's preference is ~200 bytes, 500M users = 100 GB — Redis Cluster).
- Legal requirements: GDPR requires explicit opt-in for marketing communications. CAN-SPAM requires unsubscribe functionality.

**The math/mechanics**:
- Preference check adds ~0.5ms per notification (Redis GET).
- At 500K notifications/sec, that's 500K Redis reads/sec — manageable with a Redis Cluster.
- Preference updates are rare (< 1 write/user/month) so write throughput is negligible.

**Common misconception**: Candidates design the notification system without preferences. In production, preferences are the first thing product managers ask about — and regulators require. A notification system without preference management is incomplete.

### Concept 3: Delivery Guarantees Across Channels

**What it is**: Each channel has different delivery characteristics. Push (APNs/FCM) is fire-and-forget — you send it and hope it arrives. Email has bounces and delivery status. SMS has delivery receipts. The notification system must track delivery status per-notification-per-channel.

**How it applies here**:
- **Push (APNs/FCM)**: Send via the provider API. APNs returns a success/failure synchronously. FCM returns a message_id. Neither guarantees the notification was displayed on the device. Store the provider response as the delivery status.
- **Email (SES/SendGrid)**: Send via API. Status tracking via webhooks: `sent` → `delivered` → `opened` → `clicked` (or `bounced`, `complained`). Store each status transition.
- **SMS (Twilio/SNS)**: Send via API. Delivery receipt callback updates status: `sent` → `delivered` (or `failed`, `undelivered`).
- **In-App**: Write to a per-user notification inbox (Cassandra/DynamoDB). Deliver via WebSocket if online, mark as "unread" for later retrieval.

**Common misconception**: Candidates assume push notifications are reliable. APNs and FCM have no delivery guarantee — if the device is offline, the notification may or may not be queued (APNs collapses notifications to the latest one). For critical notifications (payment confirmations), always send through multiple channels.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: "Reliability and Exactly-Once Delivery"

**Interviewer**: "A user reports getting the same push notification twice. How is that possible and how do you prevent it?"

**You**: "Duplicates happen in several ways. Most commonly: the Kafka consumer processes a notification, sends it to APNs, but crashes before committing the offset. When the consumer restarts, it re-processes the same message and sends a duplicate push. This is the inherent behavior of at-least-once delivery with Kafka. To prevent it, I'd use an idempotency key — a unique `notification_id` assigned when the notification enters the system. Before sending via any channel, the processor checks a dedup store (Redis with TTL): `SETNX dedup:{notification_id}:{channel} 1 EX 86400`. If the key already exists, skip the send. This gives us effectively-once delivery — the dedup check is O(1) and catches retries within a 24-hour window."

**Interviewer**: "What about the case where Service A triggers the same notification twice? User places an order and your order service fires two 'order confirmed' events."

**You**: "That's producer-side duplication. The dedup key should be based on the business event, not just the notification. I'd require the sending service to include an `idempotency_key` in the API request — e.g., `order_confirmed:order_12345`. The notification API deduplicates on this key before writing to Kafka. This catches duplicates from the source. For defense in depth, we have two dedup layers: (1) API-level dedup on idempotency_key (catches producer retries), and (2) processor-level dedup on notification_id (catches Kafka consumer retries)."

**Interviewer**: "Your dedup store (Redis) goes down. What happens?"

**You**: "If Redis is unavailable, the dedup check fails. We have two options: (1) fail open — skip the dedup check and accept possible duplicates. This is usually the right choice because a duplicate notification is annoying but not catastrophic. (2) Fail closed — reject the notification and let the producer retry. This guarantees no duplicates but might delay critical notifications. I'd fail open with a fallback: use a local in-memory Bloom filter as a secondary dedup layer. It won't catch all duplicates (limited by memory) but catches the most common case — immediate retries within seconds. Log the dedup skip event for monitoring."

**Interviewer**: "How do you handle notification ordering? User gets 'order shipped' before 'order confirmed.'"

**You**: "Ordering is tricky because different notifications may flow through different Kafka partitions or be processed at different speeds. Solution: partition Kafka by user_id so all notifications for a user go to the same partition and are processed in order by a single consumer. But this only ensures ordering within a channel. Cross-channel ordering (push arrives before email) is not guaranteed and generally not important — channels have different latency profiles. For strict within-channel ordering, the consumer processes notifications sequentially per user. If ordering is critical for a specific notification type, the sending service can include a `sequence_number` and the processor can buffer and reorder."

### Deep Dive Path 2: "Scaling for Burst Traffic"

**Interviewer**: "It's Black Friday. Every customer who placed an order in the last 24 hours gets a 'deals available' push notification. That's 100M notifications in a burst. How do you handle it?"

**You**: "This is a batch notification scenario. Sending 100M push notifications one-by-one through the regular pipeline would take 100M / 500K = 200 seconds at peak throughput — about 3 minutes. That's probably fine for a non-urgent marketing notification. But it would saturate the pipeline and delay real-time notifications (order confirmations, security alerts). The solution: priority queues. High-priority notifications (transactional: order updates, security) go to a separate Kafka topic with dedicated consumer groups. Marketing bulk notifications go to a lower-priority topic with rate-limited consumers. The bulk consumer sends at most 50K/sec, leaving 450K/sec capacity for real-time notifications. The 100M marketing push completes in ~33 minutes — acceptable for a marketing campaign."

**Interviewer**: "How do you implement the rate limiting on the consumer side?"

**You**: "Two levels. First, global rate limiting: the bulk consumer uses a token bucket (in Redis) to limit total sends to 50K/sec. Before processing a batch of messages, it acquires tokens. If no tokens, it pauses and retries. Second, per-user rate limiting: even within the 50K/sec global rate, we don't want to send a user 10 notifications in a row. The processor enforces a per-user rate: max 1 push notification per minute per category. It checks Redis: `rate:push:{user_id}:{category}` with a 60-second TTL. If the key exists, the notification is either delayed (re-enqueued with a delay) or dropped (for low-priority categories). Third, channel provider rate limits: APNs allows ~100K/sec per connection. FCM allows ~500K/sec. We pre-provision enough connections."

**Interviewer**: "Your Kafka cluster is struggling under the burst. How do you prevent backpressure from affecting real-time notifications?"

**You**: "Isolation. Real-time (transactional) and bulk (marketing) notifications use completely separate Kafka clusters. Or at minimum, separate topics on the same cluster with separate brokers assigned to each topic's partitions. This gives physical isolation — bulk traffic can't starve real-time partitions of disk I/O or network bandwidth. Additionally, the API gateway validates and routes: transactional notifications go to the real-time cluster, bulk requests (identified by batch size or a `priority` flag in the API request) go to the bulk cluster. Monitoring: alert if real-time consumer lag exceeds 5 seconds."

### Deep Dive Path 3: "Multi-Channel Coordination and Failure Handling"

**Interviewer**: "A notification needs to go to both push and email. Push succeeds but email fails. What's the user's experience, and how do you handle it?"

**You**: "From the user's perspective, they get the push notification immediately. The email failure is invisible to them (they just don't get the email). Our system tracks per-channel delivery status. The notification record in the database shows: `push: delivered, email: failed`. For the failed email, we retry — the email worker implements exponential backoff with jitter: retry at 1s, 2s, 4s, 8s, up to a max of 5 retries. If all retries fail, we mark it as `email: permanently_failed` and emit an alert metric. We don't try to resend via a different channel (e.g., sending an SMS because email failed) unless the sending service explicitly configures cross-channel fallback. The reason: uninvited channel switching is confusing ('why am I getting an SMS about this?')."

**Interviewer**: "How do you handle APNs token invalidation? A user uninstalls the app and their push token becomes invalid."

**You**: "APNs returns a specific error for invalid tokens (HTTP 410 Gone). When our push worker gets this response, it publishes an event to a device token invalidation topic. A separate service consumes these events and removes the invalid token from our device token store. The user's device token entry is marked as inactive. On the next notification attempt, the preference check sees no valid push token and skips the push channel (or falls back to another channel if configured). For FCM, the response includes a canonical registration ID if the token has been refreshed — we update to the new token. Monitoring: we track token invalidation rate. A sudden spike in invalidations might indicate an app update that changed the push registration."

**Interviewer**: "How do you design the in-app notification inbox? That's the 'bell icon' with unread count."

**You**: "The inbox is a per-user sorted list of notifications, newest first, with an unread counter. Storage: Cassandra with partition key = user_id and clustering key = notification_id (TimeUUID for time ordering). The unread count is a separate counter: `INCR inbox:unread:{user_id}` in Redis when a new in-app notification is created, `DECR` when the user reads it (or `SET 0` when they 'mark all as read'). Reading the inbox: `SELECT * FROM inbox WHERE user_id = ? ORDER BY notification_id DESC LIMIT 20` with cursor-based pagination. For the real-time update: when a new in-app notification is created, if the user has an active WebSocket, push it immediately. The client increments the badge count locally."

---

## How Real Companies Built This

- **Amazon SNS + SQS**: AWS's notification service (SNS) is a pub/sub system that fans out to multiple channels (SQS queues, Lambda, HTTP endpoints, email, SMS, push). It's a good reference for the fan-out architecture. See: AWS SNS documentation and architecture.
- **Uber**: Uses a service called "Hermes" for notification delivery. It handles 1B+ notifications/day across push, SMS, and email. Key challenge: delivery timing (don't send 'your driver is arriving' 5 minutes late). See: "Uber's Real-Time Push Platform" (Uber Engineering Blog).
- **Netflix**: Sends billions of push notifications for content recommendations. They use a priority-based system where user engagement signals determine notification timing. See: "Rapid Event Notification System at Netflix" (Netflix Tech Blog).
- **Firebase Cloud Messaging (FCM)**: Google's push notification service. Understanding FCM's architecture helps — it handles topic messaging (broadcast to subscribers), device groups, and condition-based targeting. See: FCM architecture documentation.
- **Key lesson**: The notification system is a platform, not a feature. In every large company, it becomes a shared service that dozens of teams integrate with. API design, extensibility, and self-service configuration matter more than any individual feature.

---

## The Complete Reference Design

### API Design
```
POST /api/v1/notifications/send
Request: {
    "idempotency_key": "order_confirmed:ord_12345",
    "recipient_id": "u_67890",
    "notification_type": "order_update",
    "priority": "high",                    // high, medium, low
    "channels": ["push", "email"],         // desired channels
    "content": {
        "title": "Order Confirmed",
        "body": "Your order #12345 has been confirmed",
        "data": {                          // structured data for the app
            "order_id": "ord_12345",
            "action": "open_order_details"
        }
    },
    "template_id": "order_confirmed_v2",   // optional: use template engine
    "template_vars": {                     // template variables
        "order_number": "12345",
        "delivery_date": "Feb 15, 2026"
    },
    "scheduled_at": null                   // null = immediate, or ISO timestamp
}
Response: {
    "notification_id": "ntf_abc123",
    "status": "queued",
    "channels_targeted": ["push", "email"],
    "channels_skipped": [],                // channels skipped due to preferences
    "created_at": "2026-02-12T10:00:00Z"
}
Headers: X-Request-ID: uuid-v4

# Batch send (for marketing/bulk)
POST /api/v1/notifications/send-batch
Request: {
    "idempotency_key": "black_friday_2026",
    "recipient_filter": {
        "segments": ["active_last_30_days"],
        "exclude_segments": ["unsubscribed_marketing"]
    },
    "notification_type": "marketing",
    "priority": "low",
    "channels": ["push"],
    "content": { ... }
}
Response: {
    "batch_id": "batch_xyz",
    "estimated_recipients": 98000000,
    "status": "processing",
    "estimated_completion": "2026-02-12T10:33:00Z"
}

# Get notification status
GET /api/v1/notifications/ntf_abc123
Response: {
    "notification_id": "ntf_abc123",
    "status": "delivered",
    "channel_status": {
        "push": {"status": "delivered", "delivered_at": "2026-02-12T10:00:01Z"},
        "email": {"status": "delivered", "delivered_at": "2026-02-12T10:00:03Z"}
    }
}

# User preferences
GET /api/v1/users/{user_id}/notification-preferences
PUT /api/v1/users/{user_id}/notification-preferences
Request: {
    "order_update": {"push": true, "email": true, "sms": false},
    "marketing": {"push": false, "email": true, "sms": false}
}
```

### Database Schema
```sql
-- PostgreSQL: Notification log (for auditing and status tracking)
CREATE TABLE notifications (
    notification_id   UUID PRIMARY KEY,
    idempotency_key   VARCHAR(255) NOT NULL,
    recipient_id      BIGINT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    priority          VARCHAR(10) NOT NULL,
    content           JSONB NOT NULL,
    status            VARCHAR(20) NOT NULL DEFAULT 'queued',
    created_at        TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (idempotency_key)
) PARTITION BY RANGE (created_at);

CREATE TABLE notification_channel_status (
    notification_id UUID NOT NULL REFERENCES notifications(notification_id),
    channel         VARCHAR(20) NOT NULL,
    status          VARCHAR(20) NOT NULL,     -- queued, sent, delivered, failed
    provider_id     VARCHAR(255),              -- APNs/FCM/SES message ID
    sent_at         TIMESTAMP,
    delivered_at    TIMESTAMP,
    error_message   TEXT,
    retry_count     INT DEFAULT 0,
    PRIMARY KEY (notification_id, channel)
);

-- Cassandra: In-App notification inbox
CREATE TABLE notification_inbox (
    user_id          BIGINT,
    notification_id  TIMEUUID,
    title            TEXT,
    body             TEXT,
    notification_type TEXT,
    data             TEXT,      -- JSON payload
    is_read          BOOLEAN,
    created_at       TIMESTAMP,
    PRIMARY KEY (user_id, notification_id)
) WITH CLUSTERING ORDER BY (notification_id DESC)
  AND default_time_to_live = 7776000;  -- 90 days

-- Redis: User preferences
-- Key: prefs:{user_id}
-- Value: JSON blob of preferences
-- TTL: none (permanent, updated on write)

-- Redis: Deduplication
-- Key: dedup:{idempotency_key}
-- Value: notification_id
-- TTL: 86400 (24 hours)

-- Redis: Per-user rate limit
-- Key: rate:notif:{user_id}:{channel}:{category}
-- Value: count
-- TTL: 60 seconds
```

### Key Algorithms
```python
import asyncio
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class Channel(Enum):
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"

@dataclass
class NotificationRequest:
    notification_id: str
    idempotency_key: str
    recipient_id: str
    notification_type: str
    priority: str
    channels: list[Channel]
    content: dict

async def process_notification(request: NotificationRequest):
    """Main notification processing pipeline."""

    # Step 1: Deduplicate
    if not await deduplicate(request.idempotency_key, request.notification_id):
        return  # Duplicate — skip

    # Step 2: Check user preferences
    prefs = await get_user_preferences(request.recipient_id)
    allowed_channels = [
        ch for ch in request.channels
        if prefs.get(request.notification_type, {}).get(ch.value, True)
    ]

    if not allowed_channels:
        await update_status(request.notification_id, "skipped_preferences")
        return

    # Step 3: Per-user rate limit check
    for channel in list(allowed_channels):
        if not await check_rate_limit(request.recipient_id, channel, request.notification_type):
            allowed_channels.remove(channel)

    # Step 4: Render template (if template_id provided)
    rendered_content = await render_template(request.content)

    # Step 5: Dispatch to channel workers
    tasks = [
        dispatch_to_channel(channel, request.recipient_id, rendered_content, request.notification_id)
        for channel in allowed_channels
    ]
    await asyncio.gather(*tasks)

async def deduplicate(idempotency_key: str, notification_id: str) -> bool:
    """Returns True if this is a new notification, False if duplicate."""
    result = await redis.set(
        f"dedup:{idempotency_key}",
        notification_id,
        nx=True,   # Only set if not exists
        ex=86400   # 24h TTL
    )
    return result is not None

async def check_rate_limit(user_id: str, channel: Channel, notif_type: str) -> bool:
    """Per-user per-channel rate limit. Max 1 per minute per category."""
    key = f"rate:notif:{user_id}:{channel.value}:{notif_type}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, 60)
    return count <= 1  # Allow only the first one per minute

async def dispatch_to_channel(channel: Channel, user_id: str, content: dict, notif_id: str):
    """Send to the appropriate channel worker via Kafka."""
    topic = f"notifications.{channel.value}"
    await kafka_producer.send(
        topic=topic,
        key=user_id.encode(),
        value={
            "notification_id": notif_id,
            "user_id": user_id,
            "content": content,
        }
    )
```

### Capacity Planning

| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Kafka Throughput | 500K msgs/sec x 500 bytes | ~250 MB/sec |
| Kafka Storage | 10B msgs/day x 500 bytes x 3 days retention | ~15 TB |
| Preference Cache (Redis) | 500M users x 200 bytes | ~100 GB |
| Dedup Cache (Redis) | 10B keys/day x 50 bytes (with TTL) | ~50 GB peak |
| Notification Log DB | 10B rows/day x 300 bytes x 90 days | ~270 TB |
| In-App Inbox (Cassandra) | 500M users x 100 notifs x 200 bytes | ~10 TB |
| Push Workers | 6B/day = 70K/sec peak / 10K per worker | ~7 workers |
| Email Workers | 3B/day = 35K/sec peak / 500 per worker | ~70 workers |

---

## What Separates Senior from Staff from Principal

| Level | What they demonstrate | Example from this design |
|-------|----------------------|-------------------------|
| Senior | Designs the basic pipeline — API → queue → worker → channel provider, handles one channel well | Implements push notification delivery, basic Kafka pipeline, handles retries |
| Staff | Addresses multi-channel coordination, user preferences, rate limiting, deduplication, and priority isolation | Designs the preference system, implements per-user rate limiting, proposes priority queues for traffic isolation, handles cross-channel delivery tracking |
| Principal | Designs this as a platform with self-service API, considers organizational impact, proposes notification intelligence | Proposes ML-based notification timing (send when user is most likely to engage), designs a self-service portal for internal teams to configure notification types, discusses regulatory compliance (GDPR, CAN-SPAM), proposes A/B testing framework for notification content |

---

## Red Flags & Common Mistakes

- **No deduplication**: In a distributed system, duplicates are inevitable. Not mentioning idempotency keys and dedup is a major gap.
- **Ignoring user preferences**: A notification system without opt-out is both a bad product and potentially illegal (GDPR/CAN-SPAM). Always mention preferences.
- **Single Kafka topic for all channels**: This creates coupling — a slow email provider backs up push notifications. Use separate topics per channel.
- **Not discussing priority**: A marketing blast should not delay a fraud alert. Priority queues or separate clusters for transactional vs. marketing notifications are essential.
- **Assuming push notifications are reliable**: APNs and FCM are best-effort. For critical notifications (2FA codes, payment confirmations), always send through multiple channels and track delivery status.
