# Design / Data Structure — Complete Interview Guide

## When to Use This Pattern

### Signals That Point to Design Problems
1. **"Design a data structure that supports X, Y, Z operations in O(1)"** — you need to combine data structures creatively.
2. **Cache design** — LRU, LFU, time-based, or size-limited caches.
3. **"Implement class with these methods"** — the problem is about API design and internal data structure choice.
4. **Random access + ordering** — you need both O(1) lookup and some notion of order (recency, frequency, insertion time).
5. **Time-based queries** — "what was the value at time T?" or "how many events in the last 5 minutes?"
6. **Weighted random selection** — pick elements with probability proportional to weight.

### When NOT to Use
- If the problem is about traversing a graph or tree — use graph/tree algorithms.
- If the problem is a pure optimization (min/max something) — consider DP or greedy.
- If only one operation needs to be fast — a simple data structure likely suffices.

---

## Core Mechanics

### The "Combine Two Data Structures" Meta-Pattern
The single most important concept for design problems: **no single data structure gives O(1) for everything**. The solution is almost always to combine two (or more) data structures where each covers the other's weakness.

| What you need | Data structure 1 | Data structure 2 | Combined |
|--------------|------------------|------------------|----------|
| O(1) lookup + O(1) ordered eviction | HashMap | Doubly Linked List | LRU Cache |
| O(1) lookup + O(1) random access | HashMap | Array/List | Insert Delete GetRandom |
| O(1) lookup + frequency tracking | HashMap (key->node) | HashMap (freq->DLL) | LFU Cache |
| O(1) lookup + time ordering | HashMap | Sorted List / Binary Search | Time-Based KV Store |
| O(1) increment/decrement + max/min | HashMap | Doubly Linked List of buckets | All O(1) DS |

### The Design Process
When you see a design problem, follow this framework:

1. **List the required operations and their time constraints.**
2. **For each operation, ask: what data structure gives this in O(1) or O(log n)?**
3. **Identify the gap**: which operation is NOT supported efficiently by any single structure?
4. **Bridge the gap**: add a second data structure that covers the weakness.
5. **Define the interface between the two structures**: usually one stores references/pointers into the other.

### OrderedDict / Doubly Linked List + HashMap
This is THE pattern for Meta interviews. Python's `OrderedDict` is an implementation of DLL + HashMap. Understanding how it works internally is essential:

- **Doubly Linked List**: Maintains order (insertion, access, or frequency). Supports O(1) removal and insertion given a node reference.
- **HashMap**: Maps keys to DLL nodes. Supports O(1) lookup.

Together: O(1) lookup (via hashmap) + O(1) reorder/remove (via DLL node reference).

### When to Use What: HashMap vs TreeMap vs Sorted List
| Structure | Lookup | Insert | Delete | Min/Max | Ordered Iteration |
|-----------|--------|--------|--------|---------|-------------------|
| HashMap | O(1) avg | O(1) avg | O(1) avg | O(n) | No |
| TreeMap (balanced BST) | O(log n) | O(log n) | O(log n) | O(log n) | Yes |
| Sorted Array + Binary Search | O(log n) | O(n) | O(n) | O(1) | Yes |
| Heap | O(n) | O(log n) | O(n)* | O(1) for min/max | No |

*O(log n) if you have the index; O(n) to find an arbitrary element.

**Choose HashMap** when you only need lookup/insert/delete and do not care about order.
**Choose TreeMap** when you need ordered operations (floor, ceiling, range queries).
**Choose Heap** when you only need the min or max, not arbitrary lookup.

### Amortized Analysis — Explained Simply
Some operations are occasionally expensive but cheap on average. **Amortized O(1)** means: over a sequence of n operations, the total cost is O(n), even if individual operations sometimes cost O(n).

**Example — Dynamic Array (ArrayList)**:
- Append is usually O(1) (just add to the end).
- When the array is full, we double its size and copy everything — O(n).
- But doubling happens at sizes 1, 2, 4, 8, ..., n. Total copy cost: 1+2+4+...+n = 2n-1 = O(n).
- Over n operations, total cost is O(n), so amortized cost per operation is O(1).

**Example — Hash Table Resizing**:
- Similar to dynamic arrays. When load factor exceeds threshold, resize and rehash everything.
- Amortized O(1) per operation.

**For interviews**: When an interviewer asks "is this really O(1)?", explain the amortized argument. Show that expensive operations happen rarely enough that the average is still O(1).

---

## The Templates

### Python — DLL + HashMap (LRU Cache Template)
```python
class DLLNode:
    def __init__(self, key=0, val=0):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None

class DLLWithHashMap:
    """Base template for ordered cache designs."""
    def __init__(self):
        self.map = {}  # key -> DLLNode
        self.head = DLLNode()  # sentinel
        self.tail = DLLNode()  # sentinel
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_after(self, node, target):
        """Insert node right after target."""
        node.prev = target
        node.next = target.next
        target.next.prev = node
        target.next = node

    def _add_to_front(self, node):
        self._add_after(node, self.head)

    def _add_to_back(self, node):
        self._add_after(node, self.tail.prev)

    def _pop_back(self):
        """Remove and return the node just before tail."""
        node = self.tail.prev
        if node == self.head:
            return None
        self._remove(node)
        return node
```

### Python — HashMap + Array (Insert Delete GetRandom Template)
```python
import random

class RandomizedSet:
    def __init__(self):
        self.val_to_idx = {}  # value -> index in list
        self.vals = []        # list of values

    def insert(self, val):
        if val in self.val_to_idx:
            return False
        self.val_to_idx[val] = len(self.vals)
        self.vals.append(val)
        return True

    def remove(self, val):
        if val not in self.val_to_idx:
            return False
        idx = self.val_to_idx[val]
        last = self.vals[-1]
        # Swap with last element
        self.vals[idx] = last
        self.val_to_idx[last] = idx
        # Remove last element
        self.vals.pop()
        del self.val_to_idx[val]
        return True

    def getRandom(self):
        return random.choice(self.vals)
```

### Go — HashMap + Array Template
```go
import "math/rand"

type RandomizedSet struct {
    valToIdx map[int]int
    vals     []int
}

func Constructor() RandomizedSet {
    return RandomizedSet{
        valToIdx: make(map[int]int),
        vals:     []int{},
    }
}

func (rs *RandomizedSet) Insert(val int) bool {
    if _, ok := rs.valToIdx[val]; ok {
        return false
    }
    rs.valToIdx[val] = len(rs.vals)
    rs.vals = append(rs.vals, val)
    return true
}

func (rs *RandomizedSet) Remove(val int) bool {
    idx, ok := rs.valToIdx[val]
    if !ok {
        return false
    }
    last := rs.vals[len(rs.vals)-1]
    rs.vals[idx] = last
    rs.valToIdx[last] = idx
    rs.vals = rs.vals[:len(rs.vals)-1]
    delete(rs.valToIdx, val)
    return true
}

func (rs *RandomizedSet) GetRandom() int {
    return rs.vals[rand.Intn(len(rs.vals))]
}
```

---

## Variant Subpatterns

### 1. Recency-Based (LRU)
Track the most/least recently used item. DLL maintains access order, hashmap provides O(1) lookup. Move-to-front on access, evict from tail.

### 2. Frequency-Based (LFU)
Track the least frequently used item. Maintain frequency buckets, each containing a DLL. On access, move item to the next frequency bucket. Evict from the lowest non-empty frequency bucket's tail.

### 3. Time-Based
Store values with timestamps. Query the value at a given time. Binary search on timestamps gives O(log n) per query.

### 4. Stack-Based (Min Stack, Max Frequency Stack)
Augment a stack with additional tracking. Min Stack: each entry also stores the min up to that point. Frequency Stack: push most frequent element, tracking frequencies with a stack per frequency.

### 5. Randomized Access
Need O(1) insert, delete, and uniform random selection. Array + HashMap: array gives random access, hashmap gives O(1) lookup, swap-with-last gives O(1) deletion.

---

## Problem Walkthroughs

---

### Problem: LRU Cache (LC #146) — Medium
**Companies**: Meta (#1 most asked), Amazon, Google, Microsoft, Bloomberg, Apple, Uber.

See the comprehensive walkthrough in the **Linked List** guide. The LRU Cache is covered there with full code, detailed dry run, and all follow-ups since it is fundamentally a linked list + hashmap problem.

**Quick Reference** — the core idea:
- **HashMap**: `key -> DLLNode` for O(1) lookup.
- **Doubly Linked List**: maintains access order. Head = MRU, tail = LRU.
- **get(key)**: look up in hashmap, move node to front, return value.
- **put(key, value)**: if exists, update and move to front. If new, create node, add to front. If over capacity, evict tail.prev.
- **Why key is stored in DLLNode**: during eviction, we need the key to delete from the hashmap.

```python
class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        self.head = DLLNode()
        self.tail = DLLNode()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_to_front(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            node = self.cache[key]
            node.val = value
            self._remove(node)
            self._add_to_front(node)
        else:
            if len(self.cache) >= self.capacity:
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]
            new_node = DLLNode(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
```

---

### Problem: Min Stack (LC #155) — Medium
**Companies**: Amazon, Google, Microsoft, Bloomberg.

**Problem**: Design a stack that supports push, pop, top, and retrieving the minimum element — all in O(1).

**Key Insight**: Each stack entry stores not just the value, but also the minimum of all elements at or below it. When we push a new element, the new minimum is `min(val, current_min)`. When we pop, the previous minimum is automatically restored.

**Optimal Solution**:
```python
class MinStack:
    def __init__(self):
        self.stack = []  # each element is (val, current_min)

    def push(self, val: int) -> None:
        if not self.stack:
            self.stack.append((val, val))
        else:
            current_min = min(val, self.stack[-1][1])
            self.stack.append((val, current_min))

    def pop(self) -> None:
        self.stack.pop()

    def top(self) -> int:
        return self.stack[-1][0]

    def getMin(self) -> int:
        return self.stack[-1][1]
```
Time: O(1) for all operations. Space: O(n).

**Space-optimized version** (only store min when it changes):
```python
class MinStack:
    def __init__(self):
        self.stack = []
        self.min_stack = []  # stores minimums

    def push(self, val: int) -> None:
        self.stack.append(val)
        if not self.min_stack or val <= self.min_stack[-1]:
            self.min_stack.append(val)

    def pop(self) -> None:
        val = self.stack.pop()
        if val == self.min_stack[-1]:
            self.min_stack.pop()

    def top(self) -> int:
        return self.stack[-1]

    def getMin(self) -> int:
        return self.min_stack[-1]
```

**Dry Run**:
```
push(-2): stack=[(-2,-2)]
push(0):  stack=[(-2,-2),(0,-2)]      min(0,-2)=-2
push(-3): stack=[(-2,-2),(0,-2),(-3,-3)]  min(-3,-2)=-3
getMin(): -3
pop():    stack=[(-2,-2),(0,-2)]
top():    0
getMin(): -2  (automatically restored!)
```

**Edge Cases**: All same elements, strictly decreasing order (every element is a new min).

**Follow-up Questions**:
- Can you implement Max Stack? (Same idea — track max instead of min. But if you also need popMax, it is much harder — LC 716.)
- What if you need O(1) for both getMin and getMax? (Store both min and max in each entry.)
- How would you implement this with a single stack and no extra space? (Encode min into the value using arithmetic tricks — fragile but possible.)

---

### Problem: Design Twitter (LC #355) — Medium
**Companies**: Amazon, Google, Meta.

**Problem**: Design a simplified Twitter:
- `postTweet(userId, tweetId)` — compose a new tweet.
- `getNewsFeed(userId)` — retrieve the 10 most recent tweets from the user and their followees.
- `follow(followerId, followeeId)` — follower follows followee.
- `unfollow(followerId, followeeId)` — follower unfollows followee.

**Key Insight**: This is a merge-K-sorted-lists problem disguised as a design problem. Each user has a timeline (sorted by time). The news feed merges the timelines of the user and all their followees, taking the top 10.

**Optimal Solution**:
```python
import heapq
from collections import defaultdict

class Twitter:
    def __init__(self):
        self.time = 0
        self.tweets = defaultdict(list)     # userId -> [(time, tweetId), ...]
        self.following = defaultdict(set)   # userId -> set of followeeIds

    def postTweet(self, userId: int, tweetId: int) -> None:
        self.tweets[userId].append((self.time, tweetId))
        self.time += 1

    def getNewsFeed(self, userId: int) -> list:
        # Merge k sorted lists (user + followees), get top 10
        heap = []
        # Include user's own tweets
        users = self.following[userId] | {userId}
        for uid in users:
            if self.tweets[uid]:
                idx = len(self.tweets[uid]) - 1
                time, tid = self.tweets[uid][idx]
                # Max heap (negate time for max behavior with min heap)
                heapq.heappush(heap, (-time, tid, uid, idx))

        result = []
        while heap and len(result) < 10:
            neg_time, tid, uid, idx = heapq.heappop(heap)
            result.append(tid)
            if idx > 0:
                idx -= 1
                time, tid = self.tweets[uid][idx]
                heapq.heappush(heap, (-time, tid, uid, idx))

        return result

    def follow(self, followerId: int, followeeId: int) -> None:
        if followerId != followeeId:
            self.following[followerId].add(followeeId)

    def unfollow(self, followerId: int, followeeId: int) -> None:
        self.following[followerId].discard(followeeId)
```
Time: postTweet O(1), getNewsFeed O(k log k + 10 log k) where k = number of followees, follow/unfollow O(1).
Space: O(total tweets + total follow relationships).

**Dry Run**:
```
postTweet(1, 5): tweets[1] = [(0, 5)], time=1
postTweet(1, 3): tweets[1] = [(0, 5), (1, 3)], time=2
postTweet(2, 101): tweets[2] = [(2, 101)], time=3
follow(1, 2): following[1] = {2}

getNewsFeed(1):
  Users: {2, 1}
  Heap init: push (-1, 3, 1, 1) and (-2, 101, 2, 0)
  Pop (-2, 101, 2, 0): result=[101]. No more tweets from user 2.
  Pop (-1, 3, 1, 1): result=[101, 3]. Push (-0, 5, 1, 0).
  Pop (0, 5, 1, 0): result=[101, 3, 5]. No more tweets from user 1.
  Return [101, 3, 5]
```

**Edge Cases**: User with no tweets, user with no followees, user follows then unfollows.

**Follow-up Questions**:
- How would you scale this for millions of users? (Fan-out on write vs fan-out on read.)
- What about pagination? (Cursor-based pagination with the heap state.)
- How would you handle tweet deletion? (Lazy deletion with a deleted set.)

---

### Problem: Design Hit Counter (LC #362) — Medium
**Companies**: Google, Amazon, Microsoft, Uber.

**Problem**: Design a hit counter that counts the number of hits received in the past 5 minutes (300 seconds). `hit(timestamp)` and `getHits(timestamp)` are called with monotonically increasing timestamps.

**Brute Force**: Store all timestamps, filter those within the 5-minute window.
```python
from collections import deque

class HitCounter:
    def __init__(self):
        self.hits = deque()

    def hit(self, timestamp: int) -> None:
        self.hits.append(timestamp)

    def getHits(self, timestamp: int) -> int:
        while self.hits and self.hits[0] <= timestamp - 300:
            self.hits.popleft()
        return len(self.hits)
```
Time: hit O(1), getHits O(n) worst case but amortized O(1) since each hit is removed at most once.
Space: O(number of hits in window).

**Key Insight — Circular Buffer**: Since the window is fixed at 300 seconds, use two arrays of size 300. `times[i]` stores the timestamp at bucket `i = timestamp % 300`. `counts[i]` stores the hit count. On a new hit, check if the stored timestamp matches; if not, reset.

**Optimal Solution — Circular Buffer**:
```python
class HitCounter:
    def __init__(self):
        self.times = [0] * 300
        self.counts = [0] * 300

    def hit(self, timestamp: int) -> None:
        idx = timestamp % 300
        if self.times[idx] != timestamp:
            # New time slot — reset
            self.times[idx] = timestamp
            self.counts[idx] = 1
        else:
            self.counts[idx] += 1

    def getHits(self, timestamp: int) -> int:
        total = 0
        for i in range(300):
            if timestamp - self.times[i] < 300:
                total += self.counts[i]
        return total
```
Time: hit O(1), getHits O(300) = O(1). Space: O(300) = O(1).

**Dry Run**:
```
hit(1):   idx=1, times[1]=1, counts[1]=1
hit(2):   idx=2, times[2]=2, counts[2]=1
hit(3):   idx=3, times[3]=3, counts[3]=1
getHits(4): check all 300 slots, 3 have timestamp within [4-300, 4). Return 3.
hit(300): idx=0, times[0]=300, counts[0]=1
getHits(300): slots 1,2,3 have timestamps 1,2,3. 300-1=299 < 300, so all valid. Slot 0: 300-300=0 < 300? Yes. Return 4.
getHits(301): slot 1: 301-1=300, NOT < 300, so invalid. Slots 2,3,0 valid. Return 3.
```

**Edge Cases**: Hits at the same timestamp, query at a time far in the future (all slots expired), no hits.

**Follow-up Questions**:
- What if hits can come out of order? (Use a different approach — sorted container or timestamp-indexed map.)
- What if the window is configurable? (Use the deque approach, or a dynamically-sized circular buffer.)
- How would you make this thread-safe? (Atomic operations or locking per bucket.)
- What about distributed hit counting? (Aggregate counts from multiple servers — eventually consistent.)

---

### Problem: Insert Delete GetRandom O(1) (LC #380) — Medium
**Companies**: Meta, Amazon, Google, Microsoft, Uber.

**Problem**: Implement a data structure supporting insert, remove, and getRandom — all in average O(1).

**Why this is hard**: A hashmap gives O(1) insert/delete but not O(1) random. An array gives O(1) random but O(n) delete (shifting). The solution combines both.

**Key Insight**: Use an array for O(1) random access and a hashmap for O(1) lookup. For O(1) deletion: swap the element to delete with the last element, then pop the last element.

**Optimal Solution**:
```python
import random

class RandomizedSet:
    def __init__(self):
        self.val_to_idx = {}  # value -> index in self.vals
        self.vals = []        # stores the actual values

    def insert(self, val: int) -> bool:
        if val in self.val_to_idx:
            return False
        self.val_to_idx[val] = len(self.vals)
        self.vals.append(val)
        return True

    def remove(self, val: int) -> bool:
        if val not in self.val_to_idx:
            return False
        # Swap val with last element, then pop
        idx = self.val_to_idx[val]
        last_val = self.vals[-1]

        # Move last element to idx
        self.vals[idx] = last_val
        self.val_to_idx[last_val] = idx

        # Remove last element
        self.vals.pop()
        del self.val_to_idx[val]
        return True

    def getRandom(self) -> int:
        return random.choice(self.vals)
```
Time: O(1) average for all operations. Space: O(n).

**Dry Run**:
```
insert(1): vals=[1], map={1:0}. Return True.
insert(2): vals=[1,2], map={1:0, 2:1}. Return True.
remove(1):
  idx = map[1] = 0
  last_val = vals[-1] = 2
  Swap: vals[0] = 2, map[2] = 0
  Pop: vals = [2], del map[1]
  map = {2:0}, vals = [2]. Return True.
insert(2): 2 in map -> Return False.
getRandom(): random.choice([2]) -> 2.
```

**Edge Cases**: Remove the only element, insert then immediately remove, getRandom with one element.

**Follow-up Questions**:
- What if we allow duplicates? (LC 381 — use a set of indices per value instead of a single index.)
- What about weighted random? (Store weights, use prefix sums with binary search.)
- How would you make this thread-safe? (Read-write lock, or use concurrent data structures.)

---

### Problem: Time Based Key-Value Store (LC #981) — Medium
**Companies**: Google, Amazon, Microsoft, Uber.

**Problem**: Design a key-value store where each key can have multiple values at different timestamps. `set(key, value, timestamp)` stores value at timestamp. `get(key, timestamp)` returns the value with the largest timestamp <= given timestamp.

**Key Insight**: For each key, store a list of (timestamp, value) pairs. Since timestamps are strictly increasing per the constraint, the list is already sorted. Use binary search to find the largest timestamp <= query timestamp.

**Optimal Solution**:
```python
from collections import defaultdict
import bisect

class TimeMap:
    def __init__(self):
        self.store = defaultdict(list)  # key -> [(timestamp, value), ...]

    def set(self, key: str, value: str, timestamp: int) -> None:
        self.store[key].append((timestamp, value))

    def get(self, key: str, timestamp: int) -> str:
        if key not in self.store:
            return ""
        entries = self.store[key]
        # Binary search for largest timestamp <= given timestamp
        idx = bisect.bisect_right(entries, (timestamp, chr(127))) - 1
        if idx < 0:
            return ""
        return entries[idx][1]
```

**Alternative without bisect** (manual binary search — better for interviews):
```python
class TimeMap:
    def __init__(self):
        self.store = {}

    def set(self, key: str, value: str, timestamp: int) -> None:
        if key not in self.store:
            self.store[key] = []
        self.store[key].append((timestamp, value))

    def get(self, key: str, timestamp: int) -> str:
        if key not in self.store:
            return ""
        entries = self.store[key]
        left, right = 0, len(entries) - 1
        result = ""
        while left <= right:
            mid = (left + right) // 2
            if entries[mid][0] <= timestamp:
                result = entries[mid][1]
                left = mid + 1
            else:
                right = mid - 1
        return result
```
Time: set O(1), get O(log n). Space: O(total entries).

**Dry Run**:
```
set("foo", "bar", 1):  store = {"foo": [(1, "bar")]}
get("foo", 1): binary search for 1. Found (1, "bar"). Return "bar".
get("foo", 3): binary search for 3. (1, "bar") has timestamp 1 <= 3. Return "bar".
set("foo", "bar2", 4): store = {"foo": [(1, "bar"), (4, "bar2")]}
get("foo", 4): found (4, "bar2"). Return "bar2".
get("foo", 5): (4, "bar2") has timestamp 4 <= 5. Return "bar2".
get("foo", 0): no timestamp <= 0. Return "".
```

**Edge Cases**: Key does not exist, timestamp before any set, timestamp exactly matching.

**Follow-up Questions**:
- What if timestamps are not monotonically increasing? (Need to insert in sorted order — use a balanced BST or sorted list with binary search insertion.)
- How would you handle deletions? (Mark entries as deleted, skip in binary search.)
- How does this relate to LSM trees? (Similar concept — time-ordered writes with read-time merging.)

---

### Problem: Random Pick with Weight (LC #528) — Medium
**Companies**: Meta, Google, Uber.

**Problem**: Given an array `w` where `w[i]` is the weight of index `i`, implement `pickIndex()` that randomly picks an index proportional to its weight.

**Key Insight**: Build a prefix sum array. Generate a random number in `[1, total_weight]`. Binary search for the first prefix sum >= the random number. The index found is the picked index.

Why this works: Each index `i` "owns" a range of the number line proportional to its weight. The prefix sum array defines these ranges. Binary search finds which range the random number falls into.

**Optimal Solution**:
```python
import random
import bisect

class Solution:
    def __init__(self, w: list):
        self.prefix = []
        total = 0
        for weight in w:
            total += weight
            self.prefix.append(total)
        self.total = total

    def pickIndex(self) -> int:
        target = random.randint(1, self.total)
        return bisect.bisect_left(self.prefix, target)
```
Time: init O(n), pickIndex O(log n). Space: O(n).

**Manual binary search version**:
```python
class Solution:
    def __init__(self, w: list):
        self.prefix = []
        total = 0
        for weight in w:
            total += weight
            self.prefix.append(total)
        self.total = total

    def pickIndex(self) -> int:
        target = random.randint(1, self.total)
        left, right = 0, len(self.prefix) - 1
        while left < right:
            mid = (left + right) // 2
            if self.prefix[mid] < target:
                left = mid + 1
            else:
                right = mid
        return left
```

**Dry Run** with `w = [1, 3, 2]`:
```
prefix = [1, 4, 6], total = 6

Random ranges:
  Index 0: target in [1, 1] -> probability 1/6
  Index 1: target in [2, 4] -> probability 3/6 = 1/2
  Index 2: target in [5, 6] -> probability 2/6 = 1/3

pickIndex(): target = random(1, 6), say target = 3
  bisect_left([1, 4, 6], 3) = 1  (prefix[1]=4 >= 3, prefix[0]=1 < 3)
  Return index 1.
```

**Edge Cases**: All weights equal, single element, very large weights.

**Follow-up Questions**:
- What if weights change dynamically? (Use a Fenwick tree / Binary Indexed Tree for O(log n) update and query.)
- What about reservoir sampling for streaming data?
- Can you do O(1) pickIndex? (Alias method — precompute in O(n), then O(1) per pick.)

---

### Problem: LFU Cache (LC #460) — Hard
**Companies**: Amazon, Google, Microsoft.

**Problem**: Design a Least Frequently Used (LFU) cache. When the cache is full and a new key is inserted, remove the least frequently used key. If there is a tie (multiple keys with same frequency), remove the least recently used among them.

**Why this is significantly harder than LRU**: In LRU, there is a single ordering (by recency). In LFU, there are TWO orderings: primary by frequency, secondary by recency within each frequency.

**Key Insight**: Maintain:
1. A hashmap from key to node (for O(1) lookup).
2. A hashmap from frequency to a doubly linked list (or OrderedDict) of nodes at that frequency.
3. Track the minimum frequency.

On access, move the node from its current frequency list to the next frequency list. If the old frequency list becomes empty and it was the minimum frequency, increment min_freq.

**Optimal Solution**:
```python
from collections import defaultdict, OrderedDict

class LFUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.min_freq = 0
        self.key_to_val = {}            # key -> value
        self.key_to_freq = {}           # key -> frequency
        self.freq_to_keys = defaultdict(OrderedDict)  # freq -> OrderedDict of keys

    def _update(self, key):
        """Increase frequency of key by 1, maintaining all structures."""
        freq = self.key_to_freq[key]
        # Remove from current frequency bucket
        del self.freq_to_keys[freq][key]
        if not self.freq_to_keys[freq]:
            del self.freq_to_keys[freq]
            if self.min_freq == freq:
                self.min_freq += 1
        # Add to next frequency bucket
        self.key_to_freq[key] = freq + 1
        self.freq_to_keys[freq + 1][key] = None  # value does not matter, just ordering

    def get(self, key: int) -> int:
        if key not in self.key_to_val:
            return -1
        self._update(key)
        return self.key_to_val[key]

    def put(self, key: int, value: int) -> None:
        if self.capacity <= 0:
            return
        if key in self.key_to_val:
            self.key_to_val[key] = value
            self._update(key)
        else:
            if len(self.key_to_val) >= self.capacity:
                # Evict LFU (and LRU among ties)
                evict_key, _ = self.freq_to_keys[self.min_freq].popitem(last=False)
                del self.key_to_val[evict_key]
                del self.key_to_freq[evict_key]
                if not self.freq_to_keys[self.min_freq]:
                    del self.freq_to_keys[self.min_freq]

            self.key_to_val[key] = value
            self.key_to_freq[key] = 1
            self.freq_to_keys[1][key] = None
            self.min_freq = 1  # new key always has frequency 1
```

**Full DLL implementation** (without OrderedDict — what interviewers want to see):
```python
class DLLNode:
    def __init__(self, key=0, val=0):
        self.key = key
        self.val = val
        self.freq = 1
        self.prev = None
        self.next = None

class DLL:
    """Doubly linked list with sentinel nodes."""
    def __init__(self):
        self.head = DLLNode()
        self.tail = DLLNode()
        self.head.next = self.tail
        self.tail.prev = self.head
        self.size = 0

    def add_to_front(self, node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
        self.size += 1

    def remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
        self.size -= 1

    def remove_last(self):
        if self.size == 0:
            return None
        node = self.tail.prev
        self.remove(node)
        return node

class LFUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.min_freq = 0
        self.cache = {}                    # key -> DLLNode
        self.freq_map = {}                 # freq -> DLL

    def _update(self, node):
        freq = node.freq
        self.freq_map[freq].remove(node)
        if self.freq_map[freq].size == 0:
            del self.freq_map[freq]
            if self.min_freq == freq:
                self.min_freq += 1
        node.freq += 1
        if node.freq not in self.freq_map:
            self.freq_map[node.freq] = DLL()
        self.freq_map[node.freq].add_to_front(node)

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._update(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        if self.capacity <= 0:
            return
        if key in self.cache:
            node = self.cache[key]
            node.val = value
            self._update(node)
        else:
            if len(self.cache) >= self.capacity:
                dll = self.freq_map[self.min_freq]
                evicted = dll.remove_last()
                del self.cache[evicted.key]
                if dll.size == 0:
                    del self.freq_map[self.min_freq]

            new_node = DLLNode(key, value)
            self.cache[key] = new_node
            if 1 not in self.freq_map:
                self.freq_map[1] = DLL()
            self.freq_map[1].add_to_front(new_node)
            self.min_freq = 1
```
Time: O(1) for all operations. Space: O(capacity).

**Dry Run** with capacity=2:
```
put(1, 1): cache={1:Node(1,1,freq=1)}, freq_map={1: [1]}, min_freq=1
put(2, 2): cache={1:Node, 2:Node}, freq_map={1: [2,1]}, min_freq=1
get(1) -> 1:
  Update freq of 1: remove from freq_map[1], add to freq_map[2]
  freq_map={1: [2], 2: [1]}, min_freq=1 (freq_map[1] still has entries)
put(3, 3):
  Cache full. Evict LFU: min_freq=1, remove last from freq_map[1] -> evict key 2.
  Add key 3 with freq=1. min_freq=1.
  cache={1:Node(freq=2), 3:Node(freq=1)}, freq_map={1: [3], 2: [1]}
get(2) -> -1 (evicted)
get(3) -> 3:
  Update freq of 3: freq 1->2. freq_map={2: [3,1]}, min_freq=2
put(4, 4):
  Cache full. Evict LFU: min_freq=2, remove last from freq_map[2] -> evict key 1 (LRU among freq=2).
  Add key 4 with freq=1. min_freq=1.
  cache={3:Node(freq=2), 4:Node(freq=1)}
```

**Edge Cases**: Capacity 0, single capacity, multiple operations on same key, evicting when frequencies are tied.

**Follow-up Questions**:
- What is the time complexity of each operation? Prove O(1).
- How does this compare to LRU in practice? (LFU is better for stable workloads; LRU is better for temporal locality.)
- How would you make this distributed? (Consistent hashing to shard keys, local LFU per shard.)

---

### Problem: All O(1) Data Structure (LC #432) — Hard
**Companies**: Google, Amazon, Meta.

**Problem**: Design a data structure that supports inc(key), dec(key), getMaxKey(), getMinKey() — all in O(1).

**Key Insight**: Use a doubly linked list of "buckets" where each bucket represents a count. Each bucket contains a set of keys with that count. The DLL is ordered by count, so head.next has the minimum count and tail.prev has the maximum count. A hashmap maps each key to its bucket.

**Optimal Solution**:
```python
class Bucket:
    def __init__(self, count=0):
        self.count = count
        self.keys = set()
        self.prev = None
        self.next = None

class AllOne:
    def __init__(self):
        self.head = Bucket()     # sentinel min
        self.tail = Bucket()     # sentinel max
        self.head.next = self.tail
        self.tail.prev = self.head
        self.key_to_bucket = {}  # key -> Bucket

    def _insert_after(self, new_bucket, prev_bucket):
        new_bucket.prev = prev_bucket
        new_bucket.next = prev_bucket.next
        prev_bucket.next.prev = new_bucket
        prev_bucket.next = new_bucket

    def _remove_bucket(self, bucket):
        bucket.prev.next = bucket.next
        bucket.next.prev = bucket.prev

    def inc(self, key: str) -> None:
        if key in self.key_to_bucket:
            bucket = self.key_to_bucket[key]
            new_count = bucket.count + 1
            # Get or create the next bucket
            next_bucket = bucket.next
            if next_bucket == self.tail or next_bucket.count != new_count:
                next_bucket = Bucket(new_count)
                self._insert_after(next_bucket, bucket)
            next_bucket.keys.add(key)
            self.key_to_bucket[key] = next_bucket
            # Remove key from old bucket
            bucket.keys.remove(key)
            if not bucket.keys:
                self._remove_bucket(bucket)
        else:
            # New key with count 1
            first_bucket = self.head.next
            if first_bucket == self.tail or first_bucket.count != 1:
                first_bucket = Bucket(1)
                self._insert_after(first_bucket, self.head)
            first_bucket.keys.add(key)
            self.key_to_bucket[key] = first_bucket

    def dec(self, key: str) -> None:
        if key not in self.key_to_bucket:
            return
        bucket = self.key_to_bucket[key]
        new_count = bucket.count - 1
        if new_count == 0:
            del self.key_to_bucket[key]
        else:
            prev_bucket = bucket.prev
            if prev_bucket == self.head or prev_bucket.count != new_count:
                prev_bucket = Bucket(new_count)
                self._insert_after(prev_bucket, bucket.prev)
            prev_bucket.keys.add(key)
            self.key_to_bucket[key] = prev_bucket
        # Remove key from old bucket
        bucket.keys.remove(key)
        if not bucket.keys:
            self._remove_bucket(bucket)

    def getMaxKey(self) -> str:
        if self.tail.prev == self.head:
            return ""
        # Return any key from the max bucket
        return next(iter(self.tail.prev.keys))

    def getMinKey(self) -> str:
        if self.head.next == self.tail:
            return ""
        return next(iter(self.head.next.keys))
```
Time: O(1) for all operations. Space: O(n).

**Why this works**: The DLL of buckets is always sorted by count. When we increment a key, it moves to the next count bucket (which is either the existing next bucket or a new one we insert). When we decrement, it moves to the previous count bucket. The min is always at head.next, the max at tail.prev.

**Edge Cases**: Inc then dec back to 0 (key is removed), all keys with same count, single key.

**Follow-up Questions**:
- How is this different from a balanced BST approach? (BST gives O(log n), this gives O(1).)
- Could you use this for a leaderboard? (With modifications — need to support arbitrary key lookup for score.)

---

### Problem: Design In-Memory File System (LC #588) — Hard
**Companies**: Amazon, Google, Microsoft.

**Problem**: Design an in-memory file system with: `ls(path)`, `mkdir(path)`, `addContentToFile(filePath, content)`, `readContentFromFile(filePath)`.

**Key Insight**: Use a trie (tree of directories). Each node has children (subdirectories and files) and optionally content (if it is a file).

**Optimal Solution**:
```python
class FileNode:
    def __init__(self):
        self.children = {}  # name -> FileNode
        self.content = ""   # non-empty means this is a file
        self.is_file = False

class FileSystem:
    def __init__(self):
        self.root = FileNode()

    def _navigate(self, path: str) -> FileNode:
        """Navigate to the node at the given path, creating directories as needed."""
        node = self.root
        if path == "/":
            return node
        parts = path.split("/")[1:]  # skip empty string from leading "/"
        for part in parts:
            if part not in node.children:
                node.children[part] = FileNode()
            node = node.children[part]
        return node

    def ls(self, path: str) -> list:
        node = self._navigate(path)
        if node.is_file:
            # If it is a file, return just its name
            return [path.split("/")[-1]]
        # If directory, return sorted list of children
        return sorted(node.children.keys())

    def mkdir(self, path: str) -> None:
        self._navigate(path)  # creates directories along the way

    def addContentToFile(self, filePath: str, content: str) -> None:
        node = self._navigate(filePath)
        node.is_file = True
        node.content += content

    def readContentFromFile(self, filePath: str) -> str:
        node = self._navigate(filePath)
        return node.content
```
Time: All operations O(L) where L is the path length (number of components). Space: O(total path components).

**Dry Run**:
```
mkdir("/a/b/c"):
  root -> create "a" -> create "b" -> create "c"

addContentToFile("/a/b/c/d", "hello"):
  Navigate root -> a -> b -> c -> create "d"
  d.is_file = True, d.content = "hello"

ls("/a/b"):
  Navigate to "b". Children: {"c": ...}. Return ["c"].

readContentFromFile("/a/b/c/d"):
  Navigate to "d". Return "hello".

ls("/a/b/c"):
  Navigate to "c". Children: {"d": ...}. Return ["d"].

ls("/a/b/c/d"):
  Navigate to "d". is_file=True. Return ["d"].
```

**Edge Cases**: Root directory ls, file and directory with same parent, appending to existing file.

**Follow-up Questions**:
- How would you add delete and move operations?
- How would you handle permissions?
- How would you make this persistent? (Write-ahead log + periodic snapshots.)
- How does this relate to real file systems? (Inodes, B-trees for large directories.)

---

### Problem: Maximum Frequency Stack (LC #895) — Hard
**Companies**: Amazon, Google, Meta.

**Problem**: Design a stack that pushes elements and pops the most frequent element. If there is a tie, pop the most recently pushed one.

**Key Insight**: Maintain:
1. A frequency map: `key -> frequency`.
2. A map of stacks: `frequency -> stack of elements at that frequency`.
3. Track `max_freq`.

When we push x, increase its frequency and add it to the stack at the new frequency. When we pop, take from the stack at max_freq. If that stack becomes empty, decrement max_freq.

The brilliant insight: an element pushed with frequency f also exists in stacks for frequencies 1, 2, ..., f-1 (from previous pushes). So popping from the top of the max_freq stack gives us the most recently pushed element with the highest frequency.

**Optimal Solution**:
```python
from collections import defaultdict

class FreqStack:
    def __init__(self):
        self.freq = {}                        # val -> current frequency
        self.freq_stacks = defaultdict(list)  # freq -> stack of values
        self.max_freq = 0

    def push(self, val: int) -> None:
        # Increase frequency
        f = self.freq.get(val, 0) + 1
        self.freq[val] = f
        self.max_freq = max(self.max_freq, f)
        # Add to the stack at this frequency
        self.freq_stacks[f].append(val)

    def pop(self) -> int:
        # Pop from the max frequency stack
        val = self.freq_stacks[self.max_freq].pop()
        # Decrease frequency
        self.freq[val] -= 1
        # If max frequency stack is empty, decrease max_freq
        if not self.freq_stacks[self.max_freq]:
            self.max_freq -= 1
        return val
```
Time: O(1) for both push and pop. Space: O(n).

**Dry Run** with pushes [5, 7, 5, 7, 4, 5]:
```
push(5): freq={5:1}, freq_stacks={1:[5]}, max_freq=1
push(7): freq={5:1,7:1}, freq_stacks={1:[5,7]}, max_freq=1
push(5): freq={5:2,7:1}, freq_stacks={1:[5,7], 2:[5]}, max_freq=2
push(7): freq={5:2,7:2}, freq_stacks={1:[5,7], 2:[5,7]}, max_freq=2
push(4): freq={5:2,7:2,4:1}, freq_stacks={1:[5,7,4], 2:[5,7]}, max_freq=2
push(5): freq={5:3,7:2,4:1}, freq_stacks={1:[5,7,4], 2:[5,7], 3:[5]}, max_freq=3

pop(): max_freq=3, pop from freq_stacks[3] -> 5. freq[5]=2.
  freq_stacks[3] empty -> max_freq=2. Return 5.
pop(): max_freq=2, pop from freq_stacks[2] -> 7. freq[7]=1.
  freq_stacks[2]=[5] (not empty). Return 7.
pop(): max_freq=2, pop from freq_stacks[2] -> 5. freq[5]=1.
  freq_stacks[2] empty -> max_freq=1. Return 5.
pop(): max_freq=1, pop from freq_stacks[1] -> 4. freq[4]=0.
  freq_stacks[1]=[5,7] (not empty). Return 4.
```

**Edge Cases**: Pop all elements, single element pushed multiple times, all elements with frequency 1.

**Follow-up Questions**:
- Can you also support peek? (Return freq_stacks[max_freq][-1] without removing.)
- What about arbitrary removal by value? (Much harder — need to track positions.)

---

## Common Mistakes & Interview Tips

### Mistakes to Avoid
1. **Not storing enough info in the node** — In LRU, the key must be in the DLL node. In LFU, the frequency must be tracked per key. Missing metadata leads to O(n) lookups.
2. **Forgetting sentinel nodes** — Without sentinels, every DLL operation needs null checks. Sentinels make the code cleaner and less error-prone.
3. **Not handling the empty case** — What happens when you call getMin on an empty structure? Always have a guard.
4. **Incorrect eviction in LFU** — The min_freq tracking is subtle. New keys always set min_freq to 1. Incrementing a key might make min_freq's bucket empty, requiring min_freq++.
5. **Swap-with-last bug in RandomizedSet** — When removing the last element (the element is already at the end), make sure the swap does not corrupt the map.
6. **Thread safety assumptions** — Interview solutions are typically single-threaded. Mention thread safety only when asked.

### Interview Tips
1. **Start with the API** — Write out the method signatures before any implementation. This clarifies the requirements.
2. **Draw the data structures** — Draw the DLL, the hashmap, the connections between them. This is your "architecture diagram."
3. **Explain the "why" of combining structures** — "A hashmap alone does not track order. A DLL alone does not give O(1) lookup. Together, each covers the other's weakness."
4. **Walk through the operations step by step** — For each method, trace through what happens in EACH data structure.
5. **Know the O(1) proof** — Be ready to explain why each operation is O(1). Point to the specific constant-time operations: hashmap lookup, DLL node removal with direct reference, etc.
6. **Practice LRU Cache until you can write it in 5 minutes** — It is the most frequently asked design problem.
7. **For LFU, explain the min_freq tracking** — This is the trickiest part. Walk through why min_freq is always correct.
8. **Mention OrderedDict for LRU but implement from scratch** — Shows you know the standard library AND can implement the fundamentals.

---

## Pattern Connections

| Pattern | Connection to Design Problems |
|---------|------------------------------|
| **Linked List** | DLL is the backbone of LRU, LFU, All O(1). Master DLL operations. |
| **Hash Map** | Every design problem uses a hashmap for O(1) lookup. |
| **Stack** | Min Stack, Max Frequency Stack are augmented stacks. |
| **Heap** | Alternative for priority-based designs (Design Twitter's news feed). |
| **Binary Search** | Time-based KV store, weighted random selection. |
| **Trie** | In-memory file system uses a trie of directories. |
| **System Design** | These coding problems are miniature versions of real system design problems (caching, rate limiting, feed ranking). |

### Progression Path
```
Min Stack (155) -> Max Stack (716) -> All O(1) DS (432)
LRU Cache (146) -> LFU Cache (460) -> Design with multiple eviction policies
Insert Delete GetRandom (380) -> with Duplicates (381)
Design Twitter (355) -> merge K sorted lists pattern
Hit Counter (362) -> Rate Limiter -> Sliding Window Counter
Time-Based KV (981) -> Snapshot Array (1146)
Max Frequency Stack (895) -> combines frequency tracking + stack ordering
In-Memory File System (588) -> Trie-based design
```
