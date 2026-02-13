# Design a Chat/Messaging System

> **Companies**: Meta (very common), Google, Microsoft, Uber, Slack, Discord | **Level**: Senior/Staff/Principal | **Duration**: 45-60 min
> **What interviewers are REALLY testing**: Can you design a real-time bidirectional communication system with persistent connections (WebSockets), handle message ordering and delivery guarantees in a distributed system, and reason about presence/typing indicators as a separate subsystem? This problem tests your understanding of connection management, message queuing, and the CAP theorem applied to real-time data.

---

## The First 5 Minutes — Scoping & Technical Clarifications

**These are the questions that make the interviewer think "this person knows what they're doing."**

- "Are we designing 1:1 messaging, group chats, or both? Group chat changes the fan-out and ordering model."
- "What's the message delivery guarantee? At-least-once, at-most-once, or exactly-once? WhatsApp does at-least-once with client-side dedup."
- "What's the expected concurrent connection count? This drives WebSocket server sizing — each connection holds ~20KB of kernel memory."
- "What's the latency SLA for message delivery? p99 < 200ms for online users?"
- "Do we need end-to-end encryption? This moves encryption to the client and means the server can't index messages."
- "What's the message retention policy? Forever (like Slack) or ephemeral (like Snapchat)? This changes the storage model."
- "Do we need read receipts, typing indicators, and presence (online/offline)? These are separate real-time subsystems."
- "What's the expected group chat size? 10 people or 10,000 (like Discord servers)?"

### Working Assumptions

| Parameter | Value |
|-----------|-------|
| DAU | 500M |
| Concurrent connections | 100M (20% of DAU online simultaneously) |
| Messages sent/day | 50B (100 messages/user/day) |
| Write QPS (messages) | ~580K/sec |
| Avg message size | 200 bytes |
| Group chat max size | 500 members |
| p99 delivery latency (online) | < 200ms |
| p99 delivery latency (offline, push) | < 2 sec |
| Availability | 99.99% |

**The math**:
- 500M DAU x 100 messages/day = 50B messages/day
- 50B / 86400 = ~580K messages/sec
- 100M concurrent WebSocket connections / 50K connections per server = 2000 WebSocket servers
- Storage: 50B msgs/day x 200 bytes = 10 TB/day = 3.6 PB/year

---

## High-Level Design (Keep it brief — 5 minutes max)

```
┌──────────┐    WebSocket    ┌────────────────┐
│  Client  │◄──────────────►│  WS Gateway     │ ← Maintains persistent connections, ~50K per server
│          │                │  (2000 servers)  │
└──────────┘                └───────┬─────────┘
                                    │
                            ┌───────▼─────────┐
                            │  Message Router  │ ← Determines which WS server has recipient's connection
                            │                  │
                            └──┬────────────┬──┘
                               │            │
                    ┌──────────▼──┐    ┌────▼──────────┐
                    │ Message     │    │ Connection     │
                    │ Store       │    │ Registry       │ ← Maps user_id → ws_server_id (Redis)
                    │ (Cassandra) │    │ (Redis)        │
                    └─────────────┘    └───────────────┘
                               │
                    ┌──────────▼──┐    ┌───────────────┐
                    │ Push        │    │ Presence       │
                    │ Notification│    │ Service        │ ← Heartbeat-based online/offline tracking
                    │ Service     │    │                │
                    └─────────────┘    └───────────────┘
```

**Why this architecture?** The WebSocket gateway is the critical component — it maintains millions of persistent TCP connections. We separate it from business logic so we can scale connection handling independently from message routing. The connection registry (Redis) is the lookup table that answers "which server is user X connected to?" — without it, we'd need to broadcast every message to all 2000 servers.

---

## Core Concepts Deep Dive

### Concept 1: WebSocket Connection Management

**What it is**: Unlike HTTP (request-response), chat requires bidirectional real-time communication. WebSockets upgrade an HTTP connection to a persistent TCP connection. The server can push messages to the client without the client polling.

**How it applies here**: Each WebSocket gateway server holds ~50K concurrent connections. When a user connects, we register the mapping `user_id → gateway_server_id` in Redis. When a message needs to be delivered, we look up which gateway server the recipient is connected to and route the message there.

**The math/mechanics**:
- Each WebSocket connection: ~20KB kernel memory (TCP buffers) + ~2KB application state
- 50K connections per server: ~1.1 GB memory just for connections
- 100M total connections / 50K per server = 2000 gateway servers
- Connection churn: users connect/disconnect frequently. At 20% churn/hour, that's 20M connect/disconnect events/hour = ~5500/sec — Redis handles this easily

**Common misconception**: Candidates often say "just use long polling." Long polling works but has 2-3x the latency of WebSockets and much higher server CPU (constant connection teardown/setup). For a chat system at this scale, WebSockets are non-negotiable. Long polling is a fallback for environments that block WebSockets (corporate firewalls).

### Concept 2: Message Ordering and Delivery Guarantees

**What it is**: In a distributed system, ensuring messages appear in the correct order is hard. Two users chatting might have their messages processed by different servers, arrive at different times, and be stored out of order.

**How it applies here**: We need two ordering guarantees: (1) within a single conversation, messages must appear in the order they were sent, and (2) a user must never miss a message (at-least-once delivery).

**The math/mechanics**:
- **Per-conversation sequence numbers**: Each conversation maintains a monotonically increasing sequence counter. When Alice sends a message in conversation C, the server atomically increments C's counter and assigns that sequence number. This ensures total order within a conversation.
- **Client-side ordering**: The client buffers incoming messages and displays them in sequence order. If message 5 arrives before message 4, buffer 5 until 4 arrives.
- **At-least-once delivery**: The server stores the message, then attempts delivery. If the client doesn't ACK within a timeout, retry. The client deduplicates using the message's unique ID.

**Common misconception**: Candidates use wall-clock timestamps for ordering. Clocks drift between servers — two messages sent 1ms apart could get identical or reversed timestamps. Always use logical sequence numbers per conversation, not timestamps.

### Concept 3: Presence and Typing Indicators — Separate Subsystem

**What it is**: "Online," "last seen 5 min ago," and "typing..." are real-time status signals that are fundamentally different from messages. They're high-frequency, low-importance, and ephemeral.

**How it applies here**: A naive approach sends presence updates to all your contacts whenever you go online/offline. With 500 contacts and 100M online users, that's massive fan-out. Instead, we use a "lazy" presence model.

**The math/mechanics**:
- Heartbeat: client sends a heartbeat every 30 seconds. Server marks user as "online" with a 60-second TTL in Redis. If two heartbeats are missed, the user is considered offline.
- Lazy presence: when Alice opens a chat with Bob, the client queries Bob's presence. It subscribes to Bob's presence channel only while the chat is open. This avoids broadcasting presence to all 500 contacts.
- Typing indicators: sent as a lightweight WebSocket message to the other user in the conversation. No persistence, no retry. If it's lost, no one cares.

**Common misconception**: Candidates treat presence as a database problem. It's a pub/sub problem. Storing "online" in a database and polling it is too slow. Use Redis pub/sub or a dedicated presence service with in-memory state.

---

## How the Interview Actually Flows — Deep Dive Paths

### Deep Dive Path 1: "Message Delivery — Online and Offline"

**Interviewer**: "Walk me through what happens when Alice sends a message to Bob, and Bob is online."

**You**: "Alice's client sends the message over her WebSocket connection to gateway server G1. G1 assigns a server-side timestamp and forwards the message to the Message Router. The router writes the message to Cassandra (conversation partition) — this is the durability guarantee. Then it looks up Bob's connection in Redis: `connection:bob` → `gateway_server:G7`. It sends the message to G7 via an internal RPC (gRPC). G7 pushes the message down Bob's WebSocket. Bob's client receives it, renders it, and sends an ACK back through G7 → router → Cassandra (marks the message as delivered). The ACK is relayed to Alice's client, which shows the checkmark. End-to-end: ~50-100ms."

**Interviewer**: "Now Bob is offline. What changes?"

**You**: "The flow is identical until the router looks up Bob's connection in Redis and finds nothing — Bob has no active WebSocket. The router still writes the message to Cassandra (it's stored). Then it publishes to the push notification service, which sends an APNs/FCM push notification to Bob's device. When Bob comes back online and establishes a WebSocket connection, the gateway does a 'sync' — it queries Cassandra for all undelivered messages for Bob since his last sync timestamp. These messages are delivered in bulk over the WebSocket. Bob's client processes them, updates the UI, and sends ACKs for each."

**Interviewer**: "What if Bob has two devices — a phone and a laptop? Both are online."

**You**: "Each device has its own WebSocket connection. The connection registry maps `bob` → `[G7 (phone), G12 (laptop)]`. The router sends the message to both gateways. Both devices receive and display it. The ACK/read receipt is tied to the message, not the device — once Bob reads the message on either device, a 'read' event is sent, and all of Bob's devices update to show 'read.' This requires device-level connection tracking: `connection:bob:device1` → G7, `connection:bob:device2` → G12."

**Interviewer**: "How do you handle the case where the message is written to Cassandra but the router crashes before delivering it?"

**You**: "This is the at-least-once guarantee in action. When the router picks up a message, it writes it to Cassandra first (durable), then attempts delivery. If the router crashes after writing to Cassandra but before delivery, the message is safe in storage. Bob will get it during his next sync. For online delivery, we use a delivery status field in Cassandra: 'stored' → 'delivered' → 'read'. The router marks it as 'delivered' only after receiving the ACK. A background reconciliation job periodically scans for messages that have been in 'stored' state for more than 5 seconds and re-queues them for delivery. This handles the crash-before-delivery case."

### Deep Dive Path 2: "Group Chat at Scale"

**Interviewer**: "How does your design change for a 500-person group chat?"

**You**: "The write path is the same — message goes to the router, is stored in Cassandra (partitioned by group_id). The delivery path changes: instead of looking up one recipient, we look up 500 members. We fetch the member list from the group metadata service, then look up which members are online and on which gateway servers. We batch the sends by gateway server — if 50 members are on G7, we send one RPC to G7 with the message and a list of 50 user IDs. G7 fans out to the 50 WebSocket connections locally. For offline members, we batch the push notifications. The key optimization is that group messages are stored once (not 500 copies) — each member's client fetches from the same conversation partition."

**Interviewer**: "What about ordering in a group chat? Multiple people could send messages at the same time."

**You**: "We use a per-group sequence number. The message router, before writing to Cassandra, atomically increments a counter for the group: `INCR group:g123:seq` in Redis. This gives a total ordering. If Alice and Bob both send to the group at the exact same time, their messages hit the router (possibly different router instances), but the Redis INCR is atomic — one gets sequence 47, the other gets 48. The order is arbitrary but consistent. All group members see the same order. The challenge is that Redis INCR is single-threaded for a given key — at very high message rates (1000 msgs/sec in one group), this becomes a bottleneck. For Discord-scale servers (100K+ members), you'd shard the counter or use a Lamport timestamp with tiebreaking."

**Interviewer**: "Discord has servers with 100K+ members. How would you handle that?"

**You**: "At that scale, the 'group chat' is really a 'channel' or 'broadcast' system. Key changes: (1) Don't fan out delivery to all 100K members. Instead, only deliver to members who have the channel open (active subscribers). Others get a badge count increment and fetch messages on-demand. (2) Message storage is the same (partitioned by channel_id). (3) Presence in the channel is managed via pub/sub — when a member opens the channel, they subscribe to a Redis pub/sub channel. New messages are published there. With 10K active viewers in a channel, that's 10K pub/sub deliveries per message. (4) For the member list, use a Bloom filter or HyperLogLog for approximate counts rather than materializing 100K member IDs on every operation."

### Deep Dive Path 3: "Storage, Sync, and Multi-Device"

**Interviewer**: "Why Cassandra for message storage? Why not MySQL or DynamoDB?"

**You**: "Chat messages have a very specific access pattern: write-heavy (580K/sec), append-only (messages aren't updated), and reads are always sequential within a conversation (fetching the last N messages). Cassandra excels here because: (1) Its LSM-tree storage engine is optimized for sequential writes. (2) Partition key = conversation_id, clustering key = message_id (TimeUUID) gives us sorted messages within a conversation with a single partition read. (3) Linear horizontal scaling — add nodes to handle more write throughput. DynamoDB would also work well (similar model, managed), but Cassandra gives us more control over compaction strategies. MySQL struggles with this write volume unless heavily sharded, and join-free reads mean we don't benefit from SQL."

**Interviewer**: "How do you handle the sync protocol when a user comes online after being offline for a week?"

**You**: "Each device tracks a `last_sync_sequence` per conversation — the sequence number of the last message it received. On reconnect, the device sends all its `last_sync_sequence` values (one per conversation with activity). The sync service compares these against the latest sequence numbers in Cassandra. For conversations where the device is behind, it fetches the delta: `SELECT * FROM messages WHERE conversation_id = ? AND seq > ? LIMIT 100`. We page through the delta 100 messages at a time, delivering them over the WebSocket. For a week offline with 100 active conversations and ~50 new messages each, that's 5000 messages — delivered in ~50 batches over a few seconds. We prioritize conversations by recency."

**Interviewer**: "What about end-to-end encryption? How does that change the architecture?"

**You**: "With E2E encryption (like Signal protocol, used by WhatsApp), the server never sees plaintext messages. The encryption/decryption happens on the client device. Key changes: (1) The server stores ciphertext — no indexing, no search, no server-side spam filtering on message content. (2) Key management: each user has a public/private key pair. The public key is stored on the server. When Alice sends to Bob, she encrypts with Bob's public key. For group chats, the sender encrypts N times (once per member's public key) — this is why E2E encrypted group chats have a practical size limit (~256 members in WhatsApp). (3) Multi-device: each device has its own key pair. Alice encrypts the message N x D times (N recipients x D devices per recipient). (4) Key rotation, device verification, and the 'safety number' comparison are all additional complexity."

---

## How Real Companies Built This

- **WhatsApp**: Uses Erlang/FreeBSD for the connection layer — Erlang's lightweight processes map naturally to per-connection actors. Each server handles ~2M connections. They use MQTT-based protocol (not raw WebSockets) with custom modifications. See: "How WhatsApp Serves 2 Billion Users" (Rick Reed, Erlang Factory SF 2014).
- **Discord**: Uses Elixir (also BEAM/Erlang VM) for their real-time gateway. They route messages through a pub/sub system (originally Erlang, later moved to Rust for the read states service). Large servers (100K+ members) use a "lazy loading" model — only active channel viewers get messages pushed. See: "How Discord Stores Billions of Messages" (Discord Engineering Blog, 2023) and "Using Rust to Scale Elixir for 11 Million Concurrent Users" (Discord Blog, 2020).
- **Slack**: Uses a combination of WebSockets for real-time delivery and MySQL (Vitess-sharded) for message storage. They faced significant scaling challenges with MySQL and wrote extensively about their migration. See: "Scaling Slack's Job Queue" (Slack Engineering Blog).
- **Key lesson**: The connection layer (WebSocket management) and the message routing layer must be decoupled. Every company at scale separates these concerns. The connection layer is an infrastructure problem (TCP, memory, kernel tuning); message routing is an application problem (who gets what).

---

## The Complete Reference Design

### API Design
```
# WebSocket Messages (JSON over WS)

# Client → Server: Send message
{
    "type": "message.send",
    "request_id": "req_abc123",          // Client-generated, for ACK matching
    "conversation_id": "conv_xyz",
    "content": "Hello!",
    "client_timestamp": 1707696000000
}

# Server → Client: Message delivered
{
    "type": "message.new",
    "message_id": "msg_789",
    "conversation_id": "conv_xyz",
    "sender_id": "u_alice",
    "content": "Hello!",
    "sequence": 47,
    "server_timestamp": 1707696000123
}

# Client → Server: ACK
{
    "type": "message.ack",
    "message_id": "msg_789"
}

# Server → Client: Read receipt
{
    "type": "message.read",
    "conversation_id": "conv_xyz",
    "reader_id": "u_bob",
    "last_read_sequence": 47
}

# REST APIs for non-real-time operations
GET /api/v1/conversations/{conv_id}/messages?before_seq=47&limit=50
POST /api/v1/conversations  (create group)
GET /api/v1/conversations  (list user's conversations)
```

### Database Schema
```sql
-- Cassandra: Messages
CREATE TABLE messages (
    conversation_id TIMEUUID,
    message_id      TIMEUUID,
    sequence        BIGINT,
    sender_id       BIGINT,
    content         TEXT,          -- plaintext or ciphertext (E2E)
    content_type    TEXT,          -- 'text', 'image', 'file'
    created_at      TIMESTAMP,
    PRIMARY KEY (conversation_id, sequence)
) WITH CLUSTERING ORDER BY (sequence DESC)
  AND compaction = {'class': 'LeveledCompactionStrategy'};

-- Cassandra: Conversation membership
CREATE TABLE conversation_members (
    conversation_id TIMEUUID,
    user_id         BIGINT,
    role            TEXT,          -- 'admin', 'member'
    joined_at       TIMESTAMP,
    last_read_seq   BIGINT,
    PRIMARY KEY (conversation_id, user_id)
);

-- Cassandra: User's conversation list (for inbox)
CREATE TABLE user_conversations (
    user_id             BIGINT,
    last_activity_at    TIMESTAMP,
    conversation_id     TIMEUUID,
    last_message_preview TEXT,
    unread_count        INT,
    PRIMARY KEY (user_id, last_activity_at)
) WITH CLUSTERING ORDER BY (last_activity_at DESC);

-- Redis: Connection registry
-- Key: connection:{user_id}:{device_id}
-- Value: gateway_server_id
-- TTL: 90 seconds (refreshed by heartbeat)

-- Redis: Conversation sequence counter
-- Key: seq:{conversation_id}
-- Value: integer (atomic INCR)
```

### Key Algorithms
```python
import asyncio
import time
from dataclasses import dataclass

@dataclass
class Message:
    message_id: str
    conversation_id: str
    sender_id: str
    content: str
    sequence: int
    server_timestamp: int

async def send_message(ws_connection, payload: dict) -> Message:
    """Handle an incoming message from a client."""
    conv_id = payload["conversation_id"]

    # 1. Assign sequence number (atomic increment)
    sequence = await redis.incr(f"seq:{conv_id}")

    # 2. Persist to Cassandra
    msg = Message(
        message_id=generate_timeuuid(),
        conversation_id=conv_id,
        sender_id=ws_connection.user_id,
        content=payload["content"],
        sequence=sequence,
        server_timestamp=int(time.time() * 1000),
    )
    await cassandra.execute(
        "INSERT INTO messages (conversation_id, message_id, sequence, sender_id, content, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (msg.conversation_id, msg.message_id, msg.sequence, msg.sender_id, msg.content, msg.server_timestamp)
    )

    # 3. ACK the sender
    await ws_connection.send({"type": "message.ack", "request_id": payload["request_id"], "sequence": sequence})

    # 4. Route to recipients
    members = await cassandra.execute(
        "SELECT user_id FROM conversation_members WHERE conversation_id = ?", (conv_id,)
    )
    for member in members:
        if member.user_id == msg.sender_id:
            continue
        await deliver_to_user(member.user_id, msg)

    return msg

async def deliver_to_user(user_id: str, msg: Message):
    """Deliver a message to a user — online or offline."""
    # Check all devices for this user
    device_keys = await redis.keys(f"connection:{user_id}:*")

    if device_keys:
        # User is online — deliver via WebSocket
        for key in device_keys:
            gateway_server = await redis.get(key)
            await rpc_to_gateway(gateway_server, user_id, msg)
    else:
        # User is offline — send push notification
        await push_service.send(
            user_id=user_id,
            title=f"New message from {msg.sender_id}",
            body=msg.content[:100],
        )

async def sync_on_connect(user_id: str, device_id: str, last_sync_sequences: dict):
    """Sync missed messages when a device reconnects."""
    for conv_id, last_seq in last_sync_sequences.items():
        current_seq = await redis.get(f"seq:{conv_id}")
        if current_seq and int(current_seq) > last_seq:
            # Fetch missed messages
            messages = await cassandra.execute(
                "SELECT * FROM messages WHERE conversation_id = ? AND sequence > ? LIMIT 100",
                (conv_id, last_seq)
            )
            for msg in messages:
                await deliver_to_user(user_id, msg)
```

### Capacity Planning

| Resource | Calculation | Requirement |
|----------|-------------|-------------|
| Message Storage | 50B msgs/day x 200 bytes x 365 days | ~3.6 PB/year |
| WebSocket Servers | 100M connections / 50K per server | 2,000 servers |
| Memory (WS servers) | 50K conn x 22 KB per conn | ~1.1 GB per server |
| Redis (connections) | 100M entries x 100 bytes | ~10 GB |
| Redis (seq counters) | 5B conversations x 16 bytes | ~80 GB |
| Network (inbound) | 580K msgs/sec x 200 bytes | ~116 MB/sec |
| Network (fan-out) | 580K msgs/sec x 2 avg recipients x 200 bytes | ~232 MB/sec |

---

## What Separates Senior from Staff from Principal

| Level | What they demonstrate | Example from this design |
|-------|----------------------|-------------------------|
| Senior | Designs WebSocket-based delivery, handles 1:1 chat, stores messages correctly | Explains connection registry, designs message storage in Cassandra, implements basic send/receive |
| Staff | Handles group chat, offline delivery, multi-device, and ordering guarantees | Designs per-conversation sequence numbers, implements sync protocol, addresses the fan-out problem for large groups |
| Principal | Proposes E2E encryption architecture, discusses protocol evolution, considers regulatory requirements | Designs Signal protocol integration, discusses how E2E encryption limits server-side features, proposes migration strategy from plaintext to encrypted, addresses data retention regulations (GDPR delete requirements) |

---

## Red Flags & Common Mistakes

- **Using HTTP polling instead of WebSockets**: For a chat system at this scale, long-polling or short-polling is a red flag. It shows you don't understand persistent connection architectures.
- **No message ordering strategy**: "Just use timestamps" will get you a follow-up question you can't answer. Use sequence numbers per conversation.
- **Forgetting offline delivery**: A chat system that only works when both users are online is useless. The sync-on-reconnect protocol is essential.
- **Treating presence and messaging as the same system**: Presence (online/offline/typing) is ephemeral, high-frequency, and lossy. Messages are durable, lower-frequency, and exactly-once. Mixing them creates scaling problems.
- **Ignoring the connection registry**: Without a way to map user → WebSocket server, you'd broadcast every message to every server. This is an O(N) vs O(1) difference.
