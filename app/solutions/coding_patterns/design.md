# Design / Data Structures Pattern Guide

## What are Design Problems?

### Explain Like I'm 5
Imagine you're building a custom toy organizer. You need to decide:
- Where to put each type of toy so you can find it quickly
- How to remember which toys you played with recently
- How to make sure your favorite toys are always easy to reach

Design problems are like building custom tools - you get to choose which "containers" (data structures) to use and how they work together to solve a specific problem efficiently.

### Technical Definition
Design problems require you to **implement a system or data structure** with specific operations and performance requirements. You must choose the right combination of data structures (arrays, hash maps, heaps, linked lists, etc.) to meet the operational constraints, typically with target time complexities like O(1) or O(log n) for key operations.

## Real-World Analogy

Think of designing a **library checkout system**:
- You need a **catalog** (hash map) to quickly look up books by ID
- You need a **queue** to track who's waiting for popular books
- You need a **history log** (linked list) to see recent checkouts
- You need a **priority system** (heap) for VIP members

Each component serves a specific purpose, and they work together to create an efficient system. That's exactly what you do in design problems - combine data structures to build something useful.

## When to Use This Pattern

### Key Signals
- **Explicit design questions**: "Design a...", "Implement a..."
- **System with operations**: Multiple methods that need to work together
- **Performance requirements**: "in O(1) time", "efficiently"
- **State management**: Need to maintain and update information over time
- **Custom behavior**: Built-in structures don't quite fit the requirements

### Common Problem Phrases
- "Design an LRU Cache"
- "Implement a Min Stack"
- "Design a Twitter feed"
- "Create a file system"
- "Build a rate limiter"
- "Design a parking lot system"

## The Problems: Key Examples

### 1. LRU Cache (Least Recently Used Cache)
**Problem**: Design a cache that:
- Stores key-value pairs
- Has a maximum capacity
- Removes the least recently used item when full
- Both `get` and `put` operations must be O(1)

### 2. Min Stack
**Problem**: Design a stack that:
- Supports standard push, pop, and top operations
- Also retrieves the minimum element in O(1) time
- All operations must be O(1)

### 3. Design Twitter
**Problem**: Design a simplified Twitter that:
- Users can post tweets
- Users can follow/unfollow others
- Users can see their news feed (recent tweets from people they follow)
- Feed should be efficiently generated

## Brute Force Approaches

### LRU Cache - Brute Force
```python
class LRUCache:
    """
    Brute force: Use a list to track access order
    Time: O(n) for get/put due to list operations
    Space: O(capacity)
    """
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> value
        self.order = []  # track access order (most recent at end)

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1

        # Move to end to mark as recently used - O(n) operation!
        self.order.remove(key)
        self.order.append(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Update existing key
            self.order.remove(key)  # O(n)
            self.order.append(key)
            self.cache[key] = value
        else:
            if len(self.cache) >= self.capacity:
                # Remove least recently used (first in list)
                lru_key = self.order.pop(0)  # O(n)
                del self.cache[lru_key]

            self.cache[key] = value
            self.order.append(key)
```

**Problem**: List operations (`remove`, `pop(0)`) are O(n), not O(1).

### Min Stack - Brute Force
```python
class MinStack:
    """
    Brute force: Scan entire stack to find minimum
    Time: O(1) for push/pop, O(n) for getMin
    Space: O(n)
    """
    def __init__(self):
        self.stack = []

    def push(self, val: int) -> None:
        self.stack.append(val)

    def pop(self) -> None:
        self.stack.pop()

    def top(self) -> int:
        return self.stack[-1]

    def getMin(self) -> int:
        # O(n) scan to find minimum
        return min(self.stack)
```

**Problem**: Finding minimum requires scanning the entire stack.

## Optimized Solutions

### 1. LRU Cache - Optimal Solution

**Key Insight**: Use **HashMap + Doubly Linked List**
- HashMap: O(1) lookup by key
- Doubly Linked List: O(1) add/remove operations at both ends

```python
class Node:
    """
    Doubly linked list node for LRU Cache
    Stores key (needed for cache removal) and value
    """
    def __init__(self, key: int = 0, value: int = 0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    """
    Optimal LRU Cache using HashMap + Doubly Linked List

    Data Structures:
    - cache (dict): key -> Node mapping for O(1) access
    - Doubly Linked List: maintains access order
      - head.next = most recently used
      - tail.prev = least recently used

    Time Complexity: O(1) for get and put
    Space Complexity: O(capacity)
    """
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> Node

        # Dummy head and tail nodes simplify edge cases
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        """Remove node from doubly linked list - O(1)"""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add_to_head(self, node: Node) -> None:
        """Add node right after head (most recent position) - O(1)"""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        """
        Get value by key and mark as recently used
        Time: O(1)
        """
        if key not in self.cache:
            return -1

        # Move to head (most recently used position)
        node = self.cache[key]
        self._remove(node)
        self._add_to_head(node)

        return node.value

    def put(self, key: int, value: int) -> None:
        """
        Insert or update key-value pair
        Time: O(1)
        """
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_head(node)
        else:
            # Add new key
            if len(self.cache) >= self.capacity:
                # Remove least recently used (node before tail)
                lru_node = self.tail.prev
                self._remove(lru_node)
                del self.cache[lru_node.key]

            # Add new node
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)

# Usage example
cache = LRUCache(2)
cache.put(1, 1)  # cache: {1=1}
cache.put(2, 2)  # cache: {1=1, 2=2}
print(cache.get(1))  # returns 1, cache: {2=2, 1=1}
cache.put(3, 3)  # evicts key 2, cache: {1=1, 3=3}
print(cache.get(2))  # returns -1 (not found)
```

### 2. Min Stack - Optimal Solution

**Key Insight**: Use **two stacks** - one for values, one for minimums

```python
class MinStack:
    """
    Optimal Min Stack using two stacks

    Data Structures:
    - stack: stores all values
    - min_stack: stores minimum values at each level

    Key Insight: The minimum at any point is the minimum of all
    elements currently in the stack. We maintain this efficiently
    by tracking minimums as we push/pop.

    Time Complexity: O(1) for all operations
    Space Complexity: O(n) - worst case, all elements are in both stacks
    """
    def __init__(self):
        self.stack = []
        self.min_stack = []  # Stores minimum at each stack level

    def push(self, val: int) -> None:
        """
        Push value and update minimum
        Time: O(1)
        """
        self.stack.append(val)

        # Push current minimum onto min_stack
        if not self.min_stack:
            self.min_stack.append(val)
        else:
            # Minimum is either new value or current minimum
            current_min = min(val, self.min_stack[-1])
            self.min_stack.append(current_min)

    def pop(self) -> None:
        """
        Pop value and corresponding minimum
        Time: O(1)
        """
        self.stack.pop()
        self.min_stack.pop()

    def top(self) -> int:
        """
        Get top value
        Time: O(1)
        """
        return self.stack[-1]

    def getMin(self) -> int:
        """
        Get minimum value in O(1)
        Time: O(1)
        """
        return self.min_stack[-1]

# Alternative space-optimized approach
class MinStackOptimized:
    """
    Space-optimized version: only push to min_stack when new minimum found

    Trade-off: Slightly more complex logic, but uses less space when
    many duplicate or larger values are pushed.
    """
    def __init__(self):
        self.stack = []
        self.min_stack = []

    def push(self, val: int) -> None:
        self.stack.append(val)
        # Only push if it's a new minimum
        if not self.min_stack or val <= self.min_stack[-1]:
            self.min_stack.append(val)

    def pop(self) -> None:
        val = self.stack.pop()
        # Only pop from min_stack if we're removing the minimum
        if val == self.min_stack[-1]:
            self.min_stack.pop()

    def top(self) -> int:
        return self.stack[-1]

    def getMin(self) -> int:
        return self.min_stack[-1]
```

### 3. Design Twitter - Optimal Solution

**Key Insight**: Use **HashMap + Heap** for efficient feed generation

```python
from collections import defaultdict
import heapq
from typing import List

class Twitter:
    """
    Simplified Twitter design using HashMap + Heap

    Data Structures:
    - tweets: user_id -> list of (timestamp, tweet_id) tuples
    - following: user_id -> set of followed user_ids
    - timestamp: global counter for tweet ordering

    Key Operations:
    - postTweet: O(1)
    - follow/unfollow: O(1)
    - getNewsFeed: O(N log K) where N = total tweets from followed users, K = 10

    Space Complexity: O(U * T + U * F) where U = users, T = tweets per user, F = follows per user
    """
    def __init__(self):
        self.tweets = defaultdict(list)  # user_id -> [(timestamp, tweet_id)]
        self.following = defaultdict(set)  # user_id -> set of followed user_ids
        self.timestamp = 0  # Global counter for tweet order

    def postTweet(self, userId: int, tweetId: int) -> None:
        """
        Post a new tweet
        Time: O(1)
        """
        self.tweets[userId].append((self.timestamp, tweetId))
        self.timestamp += 1

    def getNewsFeed(self, userId: int) -> List[int]:
        """
        Retrieve 10 most recent tweets from user's feed

        Approach: Use max heap to merge recent tweets from all followed users
        Time: O(N log K) where N = tweets from followed users, K = 10
        """
        # Max heap (use negative timestamp for max heap behavior)
        max_heap = []

        # Add user's own tweets
        for timestamp, tweet_id in self.tweets[userId]:
            heapq.heappush(max_heap, (-timestamp, tweet_id))

        # Add tweets from followed users
        for followed_id in self.following[userId]:
            for timestamp, tweet_id in self.tweets[followed_id]:
                heapq.heappush(max_heap, (-timestamp, tweet_id))

        # Extract 10 most recent tweets
        feed = []
        for _ in range(10):
            if not max_heap:
                break
            _, tweet_id = heapq.heappop(max_heap)
            feed.append(tweet_id)

        return feed

    def follow(self, followerId: int, followeeId: int) -> None:
        """
        Follow a user
        Time: O(1)
        """
        if followerId != followeeId:  # Can't follow yourself
            self.following[followerId].add(followeeId)

    def unfollow(self, followerId: int, followeeId: int) -> None:
        """
        Unfollow a user
        Time: O(1)
        """
        self.following[followerId].discard(followeeId)

# Optimized version with tweet limit per user
class TwitterOptimized:
    """
    Optimized version: Store only last 10 tweets per user

    Trade-off: Reduces space and improves getNewsFeed performance,
    but loses older tweet history.
    """
    def __init__(self):
        self.tweets = defaultdict(list)
        self.following = defaultdict(set)
        self.timestamp = 0
        self.MAX_TWEETS_PER_USER = 10

    def postTweet(self, userId: int, tweetId: int) -> None:
        # Keep only last 10 tweets
        if len(self.tweets[userId]) >= self.MAX_TWEETS_PER_USER:
            self.tweets[userId].pop(0)
        self.tweets[userId].append((self.timestamp, tweetId))
        self.timestamp += 1

    def getNewsFeed(self, userId: int) -> List[int]:
        # Same implementation as above, but with fewer tweets to process
        max_heap = []

        for timestamp, tweet_id in self.tweets[userId]:
            heapq.heappush(max_heap, (-timestamp, tweet_id))

        for followed_id in self.following[userId]:
            for timestamp, tweet_id in self.tweets[followed_id]:
                heapq.heappush(max_heap, (-timestamp, tweet_id))

        feed = []
        for _ in range(10):
            if not max_heap:
                break
            _, tweet_id = heapq.heappop(max_heap)
            feed.append(tweet_id)

        return feed

    def follow(self, followerId: int, followeeId: int) -> None:
        if followerId != followeeId:
            self.following[followerId].add(followeeId)

    def unfollow(self, followerId: int, followeeId: int) -> None:
        self.following[followerId].discard(followeeId)
```

### 4. Design HashMap - Optimal Solution

**Key Insight**: Use **array of buckets with chaining** for collision handling

```python
class ListNode:
    """Node for chaining in hash map buckets"""
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None

class MyHashMap:
    """
    Custom HashMap implementation using array + linked list chaining

    Data Structures:
    - buckets: array of linked list heads (for collision handling)

    Design Decisions:
    - Size: 1000 buckets (trade-off between space and collision probability)
    - Hash Function: key % size (simple modulo)
    - Collision Resolution: Chaining with linked lists

    Time Complexity:
    - Average: O(1) for put, get, remove
    - Worst: O(n) if all keys hash to same bucket

    Space Complexity: O(n + m) where n = number of keys, m = bucket size
    """
    def __init__(self):
        self.size = 1000
        self.buckets = [None] * self.size

    def _hash(self, key: int) -> int:
        """Hash function: simple modulo"""
        return key % self.size

    def put(self, key: int, value: int) -> None:
        """
        Insert or update key-value pair
        Time: O(1) average, O(n) worst case
        """
        bucket_idx = self._hash(key)

        # If bucket is empty, create new node
        if not self.buckets[bucket_idx]:
            self.buckets[bucket_idx] = ListNode(key, value)
            return

        # Search for key in bucket
        curr = self.buckets[bucket_idx]
        while curr:
            if curr.key == key:
                # Update existing key
                curr.value = value
                return
            if not curr.next:
                # Reached end, add new node
                curr.next = ListNode(key, value)
                return
            curr = curr.next

    def get(self, key: int) -> int:
        """
        Get value by key
        Time: O(1) average, O(n) worst case
        """
        bucket_idx = self._hash(key)
        curr = self.buckets[bucket_idx]

        # Search for key in bucket
        while curr:
            if curr.key == key:
                return curr.value
            curr = curr.next

        return -1  # Key not found

    def remove(self, key: int) -> None:
        """
        Remove key-value pair
        Time: O(1) average, O(n) worst case
        """
        bucket_idx = self._hash(key)
        curr = self.buckets[bucket_idx]

        if not curr:
            return

        # Special case: remove head node
        if curr.key == key:
            self.buckets[bucket_idx] = curr.next
            return

        # Search for key and remove
        while curr.next:
            if curr.next.key == key:
                curr.next = curr.next.next
                return
            curr = curr.next
```

### 5. Time-Based Key-Value Store

**Key Insight**: Use **HashMap + Binary Search** for timestamped values

```python
from collections import defaultdict
import bisect

class TimeMap:
    """
    Time-based key-value store using HashMap + Binary Search

    Data Structures:
    - store: key -> list of (timestamp, value) tuples (sorted by timestamp)

    Key Insight: Timestamps are strictly increasing, so we can use
    binary search to find the value at or before a given timestamp.

    Time Complexity:
    - set: O(1) (append to list)
    - get: O(log n) where n = number of values for the key

    Space Complexity: O(n * m) where n = keys, m = values per key
    """
    def __init__(self):
        self.store = defaultdict(list)  # key -> [(timestamp, value)]

    def set(self, key: str, value: str, timestamp: int) -> None:
        """
        Store key-value pair with timestamp
        Time: O(1)

        Note: Timestamps are strictly increasing, so we can simply append
        """
        self.store[key].append((timestamp, value))

    def get(self, key: str, timestamp: int) -> str:
        """
        Get value at or before given timestamp
        Time: O(log n) where n = number of values for key

        Approach: Binary search to find largest timestamp <= target
        """
        if key not in self.store:
            return ""

        values = self.store[key]

        # Binary search for rightmost timestamp <= target
        # bisect_right returns insertion point for timestamp+1
        # So bisect_right(timestamp) - 1 gives us the rightmost <= timestamp
        idx = bisect.bisect_right(values, (timestamp, chr(255)))

        if idx == 0:
            return ""  # No value at or before timestamp

        return values[idx - 1][1]

# Alternative implementation with manual binary search
class TimeMapManual:
    """
    Same as TimeMap but with manual binary search implementation
    for educational purposes
    """
    def __init__(self):
        self.store = defaultdict(list)

    def set(self, key: str, value: str, timestamp: int) -> None:
        self.store[key].append((timestamp, value))

    def get(self, key: str, timestamp: int) -> str:
        if key not in self.store:
            return ""

        values = self.store[key]

        # Manual binary search
        left, right = 0, len(values) - 1
        result = ""

        while left <= right:
            mid = (left + right) // 2
            if values[mid][0] <= timestamp:
                result = values[mid][1]  # Valid candidate
                left = mid + 1  # Look for larger timestamp
            else:
                right = mid - 1  # Look for smaller timestamp

        return result
```

## Time & Space Complexity Analysis

### Target Complexities for Common Operations

| Data Structure/System | Operation | Target Time | Space |
|----------------------|-----------|-------------|-------|
| **LRU Cache** | get | O(1) | O(capacity) |
| | put | O(1) | |
| **Min Stack** | push | O(1) | O(n) |
| | pop | O(1) | |
| | getMin | O(1) | |
| **Twitter** | postTweet | O(1) | O(U*T + U*F) |
| | getNewsFeed | O(N log K) | |
| | follow/unfollow | O(1) | |
| **HashMap** | put | O(1) avg | O(n + m) |
| | get | O(1) avg | |
| | remove | O(1) avg | |
| **Time-Based Store** | set | O(1) | O(n * m) |
| | get | O(log n) | |

**Key**: U = users, T = tweets per user, F = follows per user, N = total tweets, K = feed size, n = keys, m = values per key

### Complexity Trade-offs

1. **LRU Cache**: HashMap gives O(1) lookup, DLL gives O(1) add/remove at ends
2. **Min Stack**: Extra space (second stack) trades for O(1) minimum lookup
3. **Twitter**: Heap-based feed generation is O(N log K) but very practical for small K
4. **HashMap**: Array + chaining trades space for average O(1) operations
5. **Time-Based Store**: Sorted list enables O(log n) binary search vs O(n) linear scan

## Common Design Patterns

### Pattern 1: HashMap + Doubly Linked List
**Use Case**: Need O(1) lookup AND O(1) add/remove with ordering

**Examples**:
- LRU Cache (track access order)
- LFU Cache (track frequency order)
- Browser history (track visit order)

**Structure**:
```python
class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class DataStructure:
    def __init__(self):
        self.map = {}  # key -> Node
        self.head = Node(0, 0)  # Dummy nodes
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
```

**Why It Works**:
- HashMap: O(1) access to any node by key
- DLL: O(1) move/remove node, maintain order
- Dummy nodes: Simplify edge cases

### Pattern 2: HashMap + Heap
**Use Case**: Need O(1) lookup AND efficient priority/sorting

**Examples**:
- Twitter feed (merge sorted tweet streams)
- Top K frequent elements (track frequencies)
- Task scheduler (priority-based execution)

**Structure**:
```python
from collections import defaultdict
import heapq

class DataStructure:
    def __init__(self):
        self.map = defaultdict(list)  # key -> list of items
        self.heap = []  # Min/max heap for priority
```

**Why It Works**:
- HashMap: O(1) access to collections by key
- Heap: O(log n) insert/remove, O(1) peek at min/max
- Combined: Efficient merge of multiple sorted sequences

### Pattern 3: Multiple Synchronized Data Structures
**Use Case**: Different operations need different data structure strengths

**Examples**:
- Insert Delete GetRandom O(1) (ArrayList + HashMap)
- All O(1) Data Structure (multiple hashmaps)
- Max Stack (stack + heap + hashmap)

**Structure**:
```python
class RandomizedSet:
    def __init__(self):
        self.nums = []  # For random access
        self.pos = {}  # num -> index in nums
```

**Why It Works**:
- Each structure optimizes different operations
- Keep structures synchronized on every operation
- Trade space for time efficiency

### Pattern 4: Array of Buckets + Chaining
**Use Case**: Implement hash-based structures from scratch

**Examples**:
- Design HashMap
- Design HashSet
- Design distributed hash table

**Structure**:
```python
class HashMap:
    def __init__(self):
        self.size = 1000
        self.buckets = [None] * self.size  # Array of linked lists
```

**Why It Works**:
- Array: O(1) bucket access via hash function
- Chaining: Handles collisions without resizing
- Simple and efficient for most cases

### Pattern 5: HashMap + Sorted Structure
**Use Case**: Need fast lookup AND ordered/timestamped data

**Examples**:
- Time-based key-value store (list + binary search)
- Stock price tracker (TreeMap/SortedDict)
- Event scheduler (sorted events)

**Structure**:
```python
from collections import defaultdict

class TimeMap:
    def __init__(self):
        self.store = defaultdict(list)  # key -> [(timestamp, value)]
```

**Why It Works**:
- HashMap: O(1) access to collection by key
- Sorted list: O(log n) binary search for range queries
- Append-only: Maintains sorted order without re-sorting

## Pro Tips for Senior Engineers

### 1. Clarify Requirements First
Before writing code, ask:
- **Performance requirements**: What operations need to be O(1)? What can be O(log n)?
- **Scale**: How many users? How many operations per second?
- **Data constraints**: Maximum capacity? Data retention period?
- **Trade-offs**: Optimize for speed or space? Consistency or availability?

**Example Questions for LRU Cache**:
- "What should happen when we get a key that doesn't exist?"
- "Is there a maximum size for keys/values?"
- "Do we need thread safety?"
- "Should we support TTL (time-to-live) for entries?"

### 2. Design the API First
Start with method signatures and behavior:
```python
class LRUCache:
    """
    Design the API contract before implementation
    """
    def __init__(self, capacity: int):
        """Initialize with maximum capacity"""
        pass

    def get(self, key: int) -> int:
        """
        Return value if exists, -1 otherwise
        Side effect: marks key as recently used
        """
        pass

    def put(self, key: int, value: int) -> None:
        """
        Insert/update key-value pair
        Side effect: evicts LRU item if at capacity
        """
        pass
```

### 3. State Your Assumptions
Make your thinking transparent:
- "I'm assuming timestamps are unique and strictly increasing"
- "I'll use a hash map because keys are integers and we need O(1) lookup"
- "I'm using dummy nodes to simplify edge cases in the linked list"

### 4. Discuss Trade-offs
Show you understand the design space:

**LRU Cache**:
- "HashMap + DLL gives O(1) operations but uses more space than an array"
- "We could use OrderedDict in Python, but I'll implement from scratch to show understanding"

**Twitter Feed**:
- "Heap-based merge is O(N log K) which works well for K=10, but pre-computing feeds would be O(1) read with O(1) write to update all followers' feeds"
- "Trade-off: real-time generation vs. pre-computed feeds (read-heavy vs. write-heavy)"

### 5. Consider Edge Cases
Think about boundary conditions:
- Empty structures (what does `getMin` return on empty stack?)
- Single element (does LRU eviction work correctly?)
- Capacity limits (at capacity, below capacity, adding duplicate keys)
- Null/invalid inputs (null keys, negative timestamps)

### 6. Plan for Extension
Show you think about maintainability:
- "We could extend this to LFU by tracking frequency counts"
- "Adding TTL would require a timestamp field and periodic cleanup"
- "For thread safety, we'd need locks around get/put operations"

### 7. Optimize Iteratively
Start with working solution, then optimize:
1. **Brute force**: Get it working
2. **Identify bottleneck**: Profile operations
3. **Choose right data structure**: Target the bottleneck
4. **Implement**: Clean, commented code
5. **Test**: Edge cases and performance

### 8. Use Helper Methods
Keep code clean and modular:
```python
class LRUCache:
    def _remove(self, node):
        """Extract DLL removal logic"""
        pass

    def _add_to_head(self, node):
        """Extract DLL insertion logic"""
        pass
```

Benefits:
- Easier to test individual pieces
- More readable main methods
- Easier to debug and modify

### 9. Consider Real-World Extensions

**LRU Cache** → **Production Cache**:
- Add TTL (time-to-live)
- Add stats (hit rate, eviction count)
- Add thread safety (locks/RWLock)
- Add persistence (save to disk)
- Add distributed support (consistent hashing)

**Min Stack** → **Statistical Stack**:
- Track median, not just minimum
- Track top K elements
- Support range queries

### 10. Code Quality Matters
Even in interviews:
- Use descriptive variable names (`lru_node` not `n`)
- Add docstrings explaining approach
- Include complexity analysis in comments
- Use proper data types (type hints)

**Good**:
```python
def get(self, key: int) -> int:
    """
    Retrieve value and mark as recently used.
    Time: O(1), Space: O(1)
    """
    if key not in self.cache:
        return -1

    # Move to most recent position
    node = self.cache[key]
    self._remove(node)
    self._add_to_head(node)

    return node.value
```

**Bad**:
```python
def get(self, k):
    if k not in self.c:
        return -1
    n = self.c[k]
    self._r(n)
    self._a(n)
    return n.v
```

## Problem Recognition Checklist

### Is it a Design Problem?

✅ **YES if**:
- Problem says "Design a...", "Implement a..."
- Multiple methods need to work together
- Performance requirements specified (O(1), O(log n))
- Need to maintain state across operations
- Custom behavior not available in standard libraries

❌ **NO if**:
- Single operation/query on static data
- Standard algorithms (sort, search, graph traversal)
- Mathematical formula or string manipulation
- One-time transformation without state

### Choosing Data Structures

Ask yourself:

1. **What operations are required?**
   - Lookup by key → HashMap
   - Ordered access → Heap, BST, Sorted List
   - Fast add/remove at ends → Deque, DLL
   - Random access → Array
   - LIFO/FIFO → Stack/Queue

2. **What's the performance target?**
   - O(1) lookup + O(1) ordering → HashMap + DLL
   - O(1) lookup + O(log n) range → HashMap + Binary Search
   - O(1) everything → Multiple structures synchronized

3. **What's being tracked?**
   - Recency → Doubly Linked List (LRU)
   - Frequency → HashMap with counters (LFU)
   - Priority → Heap
   - Order with lookup → OrderedDict or HashMap + DLL

4. **What are the constraints?**
   - Limited capacity → Need eviction strategy
   - Time-ordered → Need timestamps or sorted structure
   - Concurrent access → Need thread safety

## Practice Problems

### Essential Design Problems (Master These)

1. **LRU Cache** (Medium) - [LeetCode 146]
   - Pattern: HashMap + Doubly Linked List
   - Key Skill: O(1) operations with ordering
   - Real-World: Caching systems, memory management

2. **Min Stack** (Medium) - [LeetCode 155]
   - Pattern: Auxiliary data structure
   - Key Skill: Constant-time auxiliary queries
   - Real-World: Stock price tracking, monitoring systems

3. **Design Twitter** (Medium) - [LeetCode 355]
   - Pattern: HashMap + Heap
   - Key Skill: Merging sorted streams
   - Real-World: Social media feeds, news aggregation

4. **Time Based Key-Value Store** (Medium) - [LeetCode 981]
   - Pattern: HashMap + Binary Search
   - Key Skill: Versioned data, temporal queries
   - Real-World: Version control, time-series databases

5. **Insert Delete GetRandom O(1)** (Medium) - [LeetCode 380]
   - Pattern: ArrayList + HashMap
   - Key Skill: Random access with fast updates
   - Real-World: Random sampling, load balancing

6. **Design HashMap** (Easy) - [LeetCode 706]
   - Pattern: Array of buckets + chaining
   - Key Skill: Understanding hash tables fundamentals
   - Real-World: Building core data structures

### Advanced Design Problems

7. **LFU Cache** (Hard) - [LeetCode 460]
   - Pattern: HashMap + DLL + Min Heap (or clever DLL)
   - Key Skill: Multiple criteria (frequency + recency)
   - Real-World: Advanced caching strategies

8. **Design Search Autocomplete System** (Hard) - [LeetCode 642]
   - Pattern: Trie + Heap
   - Key Skill: Prefix matching with ranking
   - Real-World: Search engines, autocomplete

9. **Design In-Memory File System** (Hard) - [LeetCode 588]
   - Pattern: Trie/Tree + HashMap
   - Key Skill: Hierarchical data management
   - Real-World: File systems, directory structures

10. **All O(1) Data Structure** (Hard) - [LeetCode 432]
    - Pattern: Multiple HashMaps + DLL
    - Key Skill: Complex state synchronization
    - Real-World: Real-time leaderboards

### System Design Adjacent

11. **Design Tic-Tac-Toe** (Medium) - [LeetCode 348]
    - Pattern: State tracking with arrays
    - Key Skill: Efficient win detection
    - Real-World: Game state management

12. **Design Hit Counter** (Medium) - [LeetCode 362]
    - Pattern: Queue or circular buffer
    - Key Skill: Time-window queries
    - Real-World: Rate limiting, analytics

13. **Design Phone Directory** (Medium) - [LeetCode 379]
    - Pattern: HashSet + Queue/List
    - Key Skill: Availability tracking
    - Real-World: Resource allocation

### Practice Strategy

**Week 1-2**: Master the essentials
- LRU Cache (spend significant time here)
- Min Stack
- Design HashMap

**Week 3-4**: Expand to complex scenarios
- Design Twitter
- Time-Based Key-Value Store
- Insert Delete GetRandom O(1)

**Week 5+**: Tackle advanced problems
- LFU Cache
- Search Autocomplete System
- All O(1) Data Structure

## Common Mistakes to Avoid

### 1. Not Asking Clarifying Questions
❌ **Mistake**: Jump into coding without understanding requirements

**Example**: LRU Cache
- What if capacity is 0?
- What if we get/put same key multiple times?
- Do we need to support concurrent access?

✅ **Fix**: Always start with 2-3 clarifying questions

### 2. Wrong Data Structure Choice
❌ **Mistake**: Using list for LRU tracking (O(n) remove operation)

```python
# BAD: O(n) to find and remove from list
class LRUCache:
    def get(self, key):
        self.order.remove(key)  # O(n) - TOO SLOW!
        self.order.append(key)
```

✅ **Fix**: Use doubly linked list for O(1) removal

### 3. Forgetting to Update All Data Structures
❌ **Mistake**: Update one structure but forget the other

```python
# BAD: Removed from cache but not from DLL
class LRUCache:
    def put(self, key, value):
        if len(self.cache) >= self.capacity:
            lru_key = self.get_lru()
            del self.cache[lru_key]  # Removed from cache
            # FORGOT to remove from DLL!
```

✅ **Fix**: Always synchronize all structures

### 4. Not Handling Edge Cases
❌ **Mistake**: Crash on empty structure or boundary conditions

```python
# BAD: What if stack is empty?
class MinStack:
    def getMin(self):
        return self.min_stack[-1]  # IndexError if empty!
```

✅ **Fix**: Check for empty structures, handle edge cases

### 5. Incorrect Dummy Node Usage
❌ **Mistake**: Forgetting to connect dummy nodes or wrong pointer updates

```python
# BAD: Didn't initialize dummy node links
class LRUCache:
    def __init__(self, capacity):
        self.head = Node()
        self.tail = Node()
        # FORGOT: self.head.next = self.tail
        # FORGOT: self.tail.prev = self.head
```

✅ **Fix**: Always initialize dummy node connections

### 6. Inefficient Feed Generation
❌ **Mistake**: Creating full feed then sorting (Twitter example)

```python
# BAD: O(N log N) to sort all tweets
def getNewsFeed(self, userId):
    all_tweets = []
    # Collect all tweets
    for user_id in [userId] + list(self.following[userId]):
        all_tweets.extend(self.tweets[user_id])
    # Sort everything - INEFFICIENT!
    all_tweets.sort(reverse=True)
    return [t[1] for t in all_tweets[:10]]
```

✅ **Fix**: Use heap to merge sorted sequences efficiently (O(N log K))

### 7. Not Considering Space Complexity
❌ **Mistake**: Unbounded growth without cleanup

```python
# BAD: Tweets list grows indefinitely
class Twitter:
    def postTweet(self, userId, tweetId):
        self.tweets[userId].append(tweetId)
        # No limit on tweets per user - memory leak!
```

✅ **Fix**: Set reasonable limits, implement cleanup/eviction

### 8. Overcomplicating the Solution
❌ **Mistake**: Using complex data structures when simple ones suffice

**Example**: Using a balanced BST for Min Stack when two stacks work fine

✅ **Fix**: Start simple, optimize only if needed

### 9. Poor Variable Naming
❌ **Mistake**: Cryptic names make code hard to follow

```python
# BAD: What are n, p, and c?
def r(self, n):
    p = n.p
    c = n.n
    p.n = c
    c.p = p
```

✅ **Fix**: Use descriptive names

```python
# GOOD: Clear intent
def _remove_node(self, node):
    prev_node = node.prev
    next_node = node.next
    prev_node.next = next_node
    next_node.prev = prev_node
```

### 10. Not Testing the Design
❌ **Mistake**: Write code but don't verify it works

✅ **Fix**: Walk through test cases

```python
# Test LRU Cache
cache = LRUCache(2)
cache.put(1, 1)  # cache: {1=1}
cache.put(2, 2)  # cache: {1=1, 2=2}
assert cache.get(1) == 1  # returns 1, cache: {2=2, 1=1}
cache.put(3, 3)  # evicts 2, cache: {1=1, 3=3}
assert cache.get(2) == -1  # returns -1 (not found)
assert cache.get(3) == 3  # returns 3
```

### 11. Not Discussing Trade-offs
❌ **Mistake**: Present solution without explaining alternatives

✅ **Fix**: Discuss why you chose your approach
- "I'm using HashMap + DLL instead of OrderedDict to demonstrate understanding of the underlying mechanism"
- "For Twitter feed, we could pre-compute feeds for faster reads, but that's write-heavy. Real-time generation is better for this scale"

### 12. Ignoring Follow-up Questions
❌ **Mistake**: "My solution is complete, I don't need to think about extensions"

✅ **Fix**: Prepare for extensions
- "How would you handle expired entries?" → Add TTL
- "What about thread safety?" → Add locks
- "How to scale to millions of users?" → Discuss distributed design

## Key Takeaways

1. **Design problems test system thinking** - not just algorithms, but how to combine data structures effectively

2. **Clarify before coding** - understand requirements, constraints, and performance targets

3. **Know common patterns**:
   - HashMap + DLL → O(1) with ordering (LRU Cache)
   - HashMap + Heap → Priority with lookup (Twitter Feed)
   - Dual structures → Track multiple properties (Min Stack)
   - Array + Chaining → Build from scratch (HashMap)
   - Sorted + Binary Search → Range queries (Time-Based Store)

4. **Target complexities** - Most design problems want O(1) or O(log n) for key operations

5. **Code quality matters** - Clean, documented, tested code even under interview pressure

6. **Think like an engineer** - Discuss trade-offs, edge cases, extensions, and real-world considerations

7. **Practice deliberately** - Master LRU Cache first, it teaches HashMap + DLL pattern used everywhere

Design problems are where senior engineers shine - show not just coding skills, but architectural thinking, trade-off analysis, and practical engineering judgment.

---

**Remember**: Design problems aren't about memorizing solutions - they're about demonstrating your ability to build robust, efficient systems. Focus on understanding the patterns, asking good questions, and communicating your thought process clearly.
