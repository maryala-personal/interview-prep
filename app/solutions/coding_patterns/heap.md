# Heap / Priority Queue — Complete Interview Guide

## When to Use This Pattern

A heap (priority queue) gives you O(1) access to the minimum or maximum element with O(log n) insertion and deletion. Use it when you repeatedly need the "best" element from a collection that changes over time.

**Primary signals:**
- "Top K" / "Kth largest" / "Kth smallest" — need the K best elements
- "Median" / "running median" — track the middle value in a stream
- "Merge K sorted lists" — efficiently pick the smallest across K sources
- "Task scheduler" / "reorganize string" — greedy scheduling with cooldowns
- "Closest K points" / "K nearest neighbors"
- "Process in priority order" / "always handle the most urgent first"

**When heap vs sorting vs quickselect:**

| Approach | When to Use | Time |
|----------|------------|------|
| Sort | Need all elements in order, one-time | O(n log n) |
| Heap (size K) | Top K from a stream or large dataset | O(n log k) |
| Quickselect | Kth element from a static array, no stream | O(n) average |
| Two heaps | Running median | O(n log n) total |

**Min-heap vs Max-heap:**
- Python's `heapq` is a min-heap. For a max-heap, negate values.
- Min-heap: smallest at top. Use for "Kth largest" (maintain K largest, pop smallest).
- Max-heap: largest at top. Use for "Kth smallest" (maintain K smallest, pop largest).

This is counterintuitive — to find the Kth **largest**, use a min-heap of size K. The top of the heap is the Kth largest because it is the smallest among the K largest.

---

## Core Mechanics

### Heap Operations and Their Costs

```
Operation          Min-Heap Cost    What It Does
─────────────────────────────────────────────────
peek/top           O(1)             Look at smallest element
push/insert        O(log n)         Add element, bubble up
pop/extract-min    O(log n)         Remove smallest, bubble down
heapify            O(n)             Build heap from array
```

### How a Heap Works (Binary Heap)

A heap is a complete binary tree stored as an array:
- Parent of index i: `(i - 1) // 2`
- Left child of i: `2 * i + 1`
- Right child of i: `2 * i + 2`

**Min-heap property:** Every parent is <= both children.

```
Array: [1, 3, 5, 7, 9, 8, 6]

Tree view:
        1
       / \
      3    5
     / \  / \
    7  9 8   6

Parent <= children at every level.
```

**Push (insert):** Add to end of array, then "bubble up" — swap with parent while smaller than parent.

```
Push 2 into [1, 3, 5, 7, 9, 8, 6]:

Step 1: Add at end → [1, 3, 5, 7, 9, 8, 6, 2]
Step 2: 2 < parent 7 → swap → [1, 3, 5, 2, 9, 8, 6, 7]
Step 3: 2 < parent 3 → swap → [1, 2, 5, 3, 9, 8, 6, 7]
Step 4: 2 > parent 1 → stop.
```

**Pop (extract-min):** Swap root with last element, remove last, then "bubble down" — swap with the smaller child while larger than a child.

### The Two-Heap Pattern (for Median)

Maintain two heaps:
- **max_heap** (left half): stores the smaller half of numbers. The top is the largest of the small half.
- **min_heap** (right half): stores the larger half of numbers. The top is the smallest of the large half.

**Invariants:**
1. All elements in max_heap <= all elements in min_heap
2. Size difference between heaps is at most 1

**Median:**
- If heaps have equal size: median = (max_heap.top + min_heap.top) / 2
- If one heap is larger: median = larger_heap.top

```
Numbers added: 1, 5, 2, 8, 3

After 1: max_heap = [1], min_heap = []
  Median = 1

After 5: max_heap = [1], min_heap = [5]
  Median = (1+5)/2 = 3

After 2: max_heap = [2, 1], min_heap = [5]
  Median = 2

After 8: max_heap = [2, 1], min_heap = [5, 8]
  Median = (2+5)/2 = 3.5

After 3: max_heap = [3, 1, 2], min_heap = [5, 8]
  Median = 3
```

### Heapify: Building a Heap in O(n)

You might expect building a heap from n elements to cost O(n log n) (n insertions of O(log n) each). But `heapify` does it in O(n) using a bottom-up approach.

**Why O(n)?**
Most nodes are near the bottom of the tree and only need to bubble down a small distance. Specifically:
- n/2 nodes are leaves (no bubble down needed)
- n/4 nodes bubble down at most 1 level
- n/8 nodes bubble down at most 2 levels
- ...
- 1 node (root) bubbles down at most log n levels

Total work = sum(n/2^(k+1) * k) for k=0 to log n = O(n)

This matters in interviews when you start with an existing array. Use `heapq.heapify(arr)` — it is O(n), not O(n log n).

### Lazy Deletion

Sometimes you need to "remove" an element from a heap that is not at the top. Since heaps only support efficient removal from the top, use lazy deletion: mark the element as deleted, and skip it when it reaches the top during pop operations.

```python
# Lazy deletion pattern
deleted = set()

def lazy_pop(heap):
    while heap and heap[0] in deleted:
        heapq.heappop(heap)
    return heapq.heappop(heap) if heap else None
```

---

## The Template

### Python — Min-Heap Basics

```python
import heapq

# Create a min-heap
heap = []
heapq.heappush(heap, 5)
heapq.heappush(heap, 2)
heapq.heappush(heap, 8)

# Peek at minimum
print(heap[0])  # 2

# Pop minimum
min_val = heapq.heappop(heap)  # 2

# Heapify an existing list (in-place, O(n))
arr = [5, 2, 8, 1, 9]
heapq.heapify(arr)  # arr is now a valid min-heap

# Max-heap: negate values
max_heap = []
heapq.heappush(max_heap, -5)
heapq.heappush(max_heap, -2)
print(-max_heap[0])  # 5 (the max)

# Top K smallest: use nlargest/nsmallest
heapq.nsmallest(3, arr)  # 3 smallest elements
heapq.nlargest(3, arr)   # 3 largest elements
```

### Python — Two-Heap Template (Median)

```python
import heapq

class MedianFinder:
    def __init__(self):
        self.lo = []  # max-heap (negate values) for lower half
        self.hi = []  # min-heap for upper half

    def addNum(self, num: int) -> None:
        heapq.heappush(self.lo, -num)
        # Ensure max of lo <= min of hi
        heapq.heappush(self.hi, -heapq.heappop(self.lo))
        # Balance sizes: lo can have at most 1 more than hi
        if len(self.hi) > len(self.lo):
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def findMedian(self) -> float:
        if len(self.lo) > len(self.hi):
            return -self.lo[0]
        return (-self.lo[0] + self.hi[0]) / 2.0
```

### Go — Heap Interface

```go
import (
    "container/heap"
)

// MinIntHeap implements heap.Interface for integers
type MinIntHeap []int

func (h MinIntHeap) Len() int            { return len(h) }
func (h MinIntHeap) Less(i, j int) bool   { return h[i] < h[j] }
func (h MinIntHeap) Swap(i, j int)        { h[i], h[j] = h[j], h[i] }

func (h *MinIntHeap) Push(x interface{}) {
    *h = append(*h, x.(int))
}

func (h *MinIntHeap) Pop() interface{} {
    old := *h
    n := len(old)
    x := old[n-1]
    *h = old[:n-1]
    return x
}

// Usage:
// h := &MinIntHeap{}
// heap.Init(h)
// heap.Push(h, 5)
// min := heap.Pop(h).(int)
```

### Go — Custom Struct Heap

```go
type Item struct {
    value    int
    priority int
}

type PriorityQueue []*Item

func (pq PriorityQueue) Len() int            { return len(pq) }
func (pq PriorityQueue) Less(i, j int) bool   { return pq[i].priority < pq[j].priority }
func (pq PriorityQueue) Swap(i, j int)        { pq[i], pq[j] = pq[j], pq[i] }

func (pq *PriorityQueue) Push(x interface{}) {
    *pq = append(*pq, x.(*Item))
}

func (pq *PriorityQueue) Pop() interface{} {
    old := *pq
    n := len(old)
    item := old[n-1]
    *pq = old[:n-1]
    return item
}
```

---

## Variant Subpatterns

### 1. Top K Elements
Maintain a heap of size K. For "K largest," use a min-heap — push elements, pop when size > K. The heap always contains the K largest seen so far.

### 2. Two-Heap (Median / Balanced Partition)
Split elements into two halves using a max-heap (lower) and min-heap (upper). Used for running median, sliding window median.

### 3. Merge K Sorted Sequences
Push the first element of each sequence into a min-heap. Pop the minimum, push the next element from the same sequence. This merges K sorted sequences in O(n log K) where n is total elements.

### 4. Greedy Scheduling
Use a heap to always process the most frequent / highest priority item. Used in Task Scheduler, Reorganize String.

### 5. Dijkstra's Algorithm
Min-heap of (distance, node). Always process the node with smallest tentative distance. This is the canonical heap-based shortest path algorithm.

### 6. K-Way External Merge
Variant of merge K sorted, used in database systems for sorting data that does not fit in memory.

---

## Problem Walkthroughs

---

### Problem 1: Kth Largest Element in an Array (LC 215 — Medium)

**Problem:** Find the Kth largest element in an unsorted array. Note: it is the Kth largest in sorted order, not the Kth distinct element.

**Brute Force:**
Sort the array, return the element at index n-k. O(n log n).

**Key Insight (Heap approach):**
Maintain a min-heap of size K. After processing all elements, the heap top is the Kth largest. Why min-heap? Because we want the smallest of the K largest — and that is exactly what the min-heap top gives us.

**Key Insight (Quickselect):**
Partition the array like quicksort. If the pivot lands at position n-k, we are done. Otherwise, recurse on the side that contains position n-k. Average O(n), worst case O(n^2).

**Optimal Solution (Heap):**

```python
import heapq

def findKthLargest_heap(nums: list[int], k: int) -> int:
    """
    LC 215: Kth Largest Element — Heap

    Time: O(n log k)
    Space: O(k)
    """
    heap = []
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)  # Remove smallest, keep K largest
    return heap[0]
```

**Optimal Solution (Quickselect):**

```python
import random

def findKthLargest(nums: list[int], k: int) -> int:
    """
    LC 215: Kth Largest Element — Quickselect

    Time: O(n) average, O(n^2) worst
    Space: O(1) (in-place partitioning)
    """
    target = len(nums) - k  # Index in sorted array

    def quickselect(left, right):
        # Random pivot to avoid worst case
        pivot_idx = random.randint(left, right)
        nums[pivot_idx], nums[right] = nums[right], nums[pivot_idx]
        pivot = nums[right]

        # Partition: elements < pivot on left, >= pivot on right
        store = left
        for i in range(left, right):
            if nums[i] < pivot:
                nums[i], nums[store] = nums[store], nums[i]
                store += 1
        nums[store], nums[right] = nums[right], nums[store]

        if store == target:
            return nums[store]
        elif store < target:
            return quickselect(store + 1, right)
        else:
            return quickselect(left, store - 1)

    return quickselect(0, len(nums) - 1)
```

**Dry Run (Heap):**
```
nums = [3,2,1,5,6,4], k = 2

Process 3: heap=[3]
Process 2: heap=[2,3]
Process 1: heap=[1,2,3] → size 3 > 2, pop 1 → heap=[2,3]
Process 5: heap=[2,3,5] → pop 2 → heap=[3,5]
Process 6: heap=[3,5,6] → pop 3 → heap=[5,6]
Process 4: heap=[4,5,6] → pop 4 → heap=[5,6]

Return heap[0] = 5. (5 is the 2nd largest)
```

**Edge Cases:**
- k = 1: return maximum
- k = n: return minimum
- All elements identical: return that element
- Array of size 1: return that element

**Follow-up:** What if elements are streaming? Heap approach works naturally for streams — just maintain a heap of size K. Quickselect requires the full array upfront.

**When to use which:**
- Heap: streaming data, or when k << n (O(n log k) is better than O(n log n))
- Quickselect: static array, when you want average O(n)
- Sort: simplest code, acceptable when O(n log n) is fine

**Quickselect deep dive:**
Quickselect is the selection algorithm analog of quicksort. Key properties:
- Average case: O(n) — expected because each partition halves the search space
- Worst case: O(n^2) — can hit this with pathological pivots (already sorted, always pick smallest)
- Randomized pivot: makes worst case astronomically unlikely (1/n! probability for repeated bad pivots)
- In-place: O(1) extra space (modifies the input array)

In interviews, mention: "I use a randomized pivot to avoid the O(n^2) worst case. In practice, this gives reliable O(n) performance."

**Python shortcut:** `heapq.nlargest(k, nums)` returns the k largest elements. It uses a min-heap internally and runs in O(n log k). Good for quick solutions in interviews, but show you understand the algorithm.

---

### Problem 2: Top K Frequent Elements (LC 347 — Medium)

**Problem:** Given an integer array `nums` and an integer `k`, return the `k` most frequent elements. Any order is acceptable.

**Brute Force:**
Count frequencies, sort by frequency, take top k. O(n log n).

**Key Insight:**
Count frequencies with a hashmap. Then use a min-heap of size K to keep the K most frequent. Alternatively, use bucket sort: create an array where index = frequency, value = list of elements with that frequency.

**Optimal Solution (Heap):**

```python
import heapq
from collections import Counter

def topKFrequent_heap(nums: list[int], k: int) -> list[int]:
    """
    LC 347: Top K Frequent Elements — Heap

    Time: O(n log k)
    Space: O(n)
    """
    counts = Counter(nums)
    # Min-heap of size k, keyed by frequency
    heap = []
    for num, freq in counts.items():
        heapq.heappush(heap, (freq, num))
        if len(heap) > k:
            heapq.heappop(heap)

    return [num for freq, num in heap]
```

**Optimal Solution (Bucket Sort — O(n)):**

```python
from collections import Counter

def topKFrequent(nums: list[int], k: int) -> list[int]:
    """
    LC 347: Top K Frequent Elements — Bucket Sort

    Time: O(n)
    Space: O(n)
    """
    counts = Counter(nums)
    # Bucket: index = frequency, value = list of elements
    buckets = [[] for _ in range(len(nums) + 1)]
    for num, freq in counts.items():
        buckets[freq].append(num)

    result = []
    for freq in range(len(buckets) - 1, 0, -1):
        for num in buckets[freq]:
            result.append(num)
            if len(result) == k:
                return result

    return result
```

**Dry Run (Heap):**
```
nums = [1,1,1,2,2,3], k = 2

counts = {1:3, 2:2, 3:1}

Process (3,1): heap=[(3,1)]
Process (2,2): heap=[(2,2),(3,1)]
Process (1,3): heap=[(1,3),(3,1),(2,2)] → size 3 > 2, pop (1,3)
  heap=[(2,2),(3,1)]

Return [2, 1]
```

**Edge Cases:**
- k equals number of distinct elements: return all
- All elements same: return [element]
- k = 1: return most frequent

**Follow-up:** What if elements are streaming and you periodically need top K? Maintain a frequency map and a heap. Update on each insertion. What about approximate top-K for very large streams? Use Count-Min Sketch.

---

### Problem 3: Task Scheduler (LC 621 — Medium)

**Problem:** Given a list of tasks (characters) and a cooldown interval `n`, find the minimum number of CPU intervals needed to execute all tasks. The same task must have at least `n` intervals between executions. Idle intervals can be inserted.

**Brute Force:**
Simulate the CPU cycle by cycle, picking the most frequent available task each time. O(total_time * 26).

**Key Insight:**
Greedy: always execute the most frequent remaining task (to avoid wasting idle time later). Use a max-heap of remaining counts. After executing a task, it cannot be executed again for n intervals — put it in a cooldown queue.

There is also a mathematical formula: `total_time = max(len(tasks), (max_freq - 1) * (n + 1) + count_of_max_freq)`.

**Optimal Solution (Heap + Queue):**

```python
import heapq
from collections import Counter, deque

def leastInterval_heap(tasks: list[str], n: int) -> int:
    """
    LC 621: Task Scheduler — Heap + Cooldown Queue

    Time: O(total_time * log 26) = O(total_time)
    Space: O(26) = O(1)
    """
    counts = Counter(tasks)
    # Max-heap of remaining counts (negate for min-heap)
    heap = [-cnt for cnt in counts.values()]
    heapq.heapify(heap)

    time = 0
    cooldown = deque()  # (available_time, remaining_count)

    while heap or cooldown:
        time += 1

        if heap:
            cnt = heapq.heappop(heap) + 1  # Execute one instance (cnt is negative)
            if cnt < 0:  # More instances remaining
                cooldown.append((time + n, cnt))
        # else: idle cycle

        # Check if any task's cooldown has expired
        if cooldown and cooldown[0][0] == time:
            _, cnt = cooldown.popleft()
            heapq.heappush(heap, cnt)

    return time
```

**Optimal Solution (Math Formula):**

```python
from collections import Counter

def leastInterval(tasks: list[str], n: int) -> int:
    """
    LC 621: Task Scheduler — Math

    Time: O(n)
    Space: O(1)
    """
    counts = Counter(tasks)
    max_freq = max(counts.values())
    # How many tasks have the maximum frequency
    max_count = sum(1 for freq in counts.values() if freq == max_freq)

    # Formula: (max_freq - 1) chunks of size (n+1), plus final partial chunk
    result = (max_freq - 1) * (n + 1) + max_count
    # But we need at least len(tasks) intervals (no idle needed if tasks fill all slots)
    return max(result, len(tasks))
```

**Why the formula works:**
```
tasks = [A,A,A,B,B,B], n=2

Arrange most frequent first:
A _ _ A _ _ A
  Fill slots with B:
A B _ A B _ A B

Framework: (max_freq-1) groups of (n+1) + max_count
         = (3-1) * 3 + 2 = 8

Result: A B _ A B _ A B = 8 intervals
```

**Dry Run (Heap):**
```
tasks = ["A","A","A","B","B","B"], n = 2
counts = {A:3, B:3}
heap = [-3, -3]

time=1: Pop -3 → cnt=-2 (A executed). Cooldown: (3, -2). heap=[-3]
time=2: Pop -3 → cnt=-2 (B executed). Cooldown: (3,-2),(4,-2). heap=[]
time=3: heap empty → idle. But cooldown[0]=(3,-2), time==3 → push -2. heap=[-2]
time=4: Pop -2 → cnt=-1 (A). Cooldown: (4,-2),(6,-1).
        cooldown[0]=(4,-2), time==4 → push -2. heap=[-2]
time=5: Pop -2 → cnt=-1 (B). Cooldown: (6,-1),(7,-1). heap=[]
time=6: idle. cooldown[0]=(6,-1), time==6 → push -1. heap=[-1]
time=7: Pop -1 → cnt=0 (A done). cooldown[0]=(7,-1), time==7 → push -1. heap=[-1]
time=8: Pop -1 → cnt=0 (B done). heap=[], cooldown=[]. Done.

Total = 8
```

**Edge Cases:**
- n = 0: no cooldown, answer = len(tasks)
- Single task type: `(freq - 1) * (n + 1) + 1` (lots of idle)
- Many task types: enough variety to fill cooldown slots, answer = len(tasks)

**Follow-up:** What if tasks have different execution times? This becomes a more complex scheduling problem (weighted scheduling with cooldowns).

---

### Problem 4: Reorganize String (LC 767 — Medium)

**Problem:** Given a string `s`, rearrange the characters so that no two adjacent characters are the same. Return any valid rearrangement, or `""` if impossible.

**Brute Force:**
Try all permutations, check if any has no adjacent duplicates. O(n!).

**Key Insight:**
Greedy with max-heap: always place the most frequent remaining character. After placing a character, it cannot be placed again immediately — save it and place the next most frequent character in the next position.

**Impossible condition:** If any character appears more than `(n + 1) / 2` times, it is impossible (pigeonhole principle — there are not enough "slots" to separate them).

**Optimal Solution:**

```python
import heapq
from collections import Counter

def reorganizeString(s: str) -> str:
    """
    LC 767: Reorganize String

    Time: O(n log 26) = O(n)
    Space: O(26) = O(1)
    """
    counts = Counter(s)

    # Check impossibility
    max_freq = max(counts.values())
    if max_freq > (len(s) + 1) // 2:
        return ""

    # Max-heap of (negative_count, char)
    heap = [(-cnt, ch) for ch, cnt in counts.items()]
    heapq.heapify(heap)

    result = []
    prev_cnt, prev_ch = 0, ''

    while heap:
        cnt, ch = heapq.heappop(heap)
        result.append(ch)

        # Push back the previously used character (if it has remaining count)
        if prev_cnt < 0:
            heapq.heappush(heap, (prev_cnt, prev_ch))

        # Save current character for next iteration
        prev_cnt, prev_ch = cnt + 1, ch  # cnt is negative, +1 decreases magnitude

    return ''.join(result)
```

**Dry Run:**
```
s = "aab"
counts = {a:2, b:1}
heap = [(-2,'a'), (-1,'b')]

Step 1: Pop (-2,'a'). result=['a']. prev=(-1,'a'). heap=[(-1,'b')]
Step 2: Pop (-1,'b'). Push prev (-1,'a'). result=['a','b']. prev=(0,'b'). heap=[(-1,'a')]
Step 3: Pop (-1,'a'). prev=(0,'b'), don't push. result=['a','b','a']. prev=(0,'a'). heap=[]

Result: "aba"
```

**Edge Cases:**
- Single character: return it
- Two characters alternating: `"aabb"` → `"abab"`
- Impossible: `"aaab"` → `""` (a appears 3 times, but max allowed is (4+1)/2 = 2)
- All same: only possible if length 1

**Follow-up:** What about Rearrange String K Distance Apart (LC 358)? Same approach but with cooldown K instead of 2. Use a queue to track cooldown.

---

### Problem 5: Merge K Sorted Lists (LC 23 — Hard)

**Problem:** Merge `k` sorted linked lists into one sorted linked list.

**Brute Force:**
Collect all values, sort them, create a new linked list. O(N log N) where N is total nodes.

**Key Insight:**
Use a min-heap of size K. Push the head of each list. Pop the minimum, add it to the result, and push the popped node's next (if it exists). At any time, the heap has at most K elements, so each operation is O(log K).

**Optimal Solution:**

```python
import heapq

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def mergeKLists(lists: list[ListNode]) -> ListNode:
    """
    LC 23: Merge K Sorted Lists

    Time: O(N log k) where N = total nodes, k = number of lists
    Space: O(k) for the heap
    """
    # Min-heap: (value, index, node)
    # Index is used as a tiebreaker to avoid comparing ListNode objects
    heap = []
    for i, head in enumerate(lists):
        if head:
            heapq.heappush(heap, (head.val, i, head))

    dummy = ListNode(0)
    current = dummy

    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next
```

**Why we need the index tiebreaker:** Python's heapq compares tuples element by element. If two nodes have the same value, it would try to compare ListNode objects, which is not supported. The index (unique per list) breaks ties without needing to compare nodes.

**Dry Run:**
```
lists = [1→4→5, 1→3→4, 2→6]

Initial heap: [(1,0,node_1a), (1,1,node_1b), (2,2,node_2)]

Pop (1,0,1→4→5): result=[1]. Push (4,0,4→5). heap=[(1,1,...),(2,2,...),(4,0,...)]
Pop (1,1,1→3→4): result=[1,1]. Push (3,1,3→4). heap=[(2,2,...),(3,1,...),(4,0,...)]
Pop (2,2,2→6): result=[1,1,2]. Push (6,2,6). heap=[(3,1,...),(4,0,...),(6,2,...)]
Pop (3,1,3→4): result=[1,1,2,3]. Push (4,1,4). heap=[(4,0,...),(4,1,...),(6,2,...)]
Pop (4,0,4→5): result=[1,1,2,3,4]. Push (5,0,5). heap=[(4,1,...),(5,0,...),(6,2,...)]
Pop (4,1,4): result=[1,1,2,3,4,4]. No next. heap=[(5,0,...),(6,2,...)]
Pop (5,0,5): result=[1,1,2,3,4,4,5]. No next. heap=[(6,2,...)]
Pop (6,2,6): result=[1,1,2,3,4,4,5,6]. No next. heap=[]

Result: 1→1→2→3→4→4→5→6
```

**Edge Cases:**
- Empty lists array: return None
- Some lists are None: skip them
- Single list: return it as-is
- All lists have one element: just sort K elements

**Follow-up:** Divide and conquer approach merges pairs of lists recursively (like merge sort). Same O(N log k) complexity but avoids the heap overhead. Good to mention in interviews.

```python
def mergeKLists_dc(lists):
    """Divide and conquer: merge pairs recursively."""
    if not lists:
        return None
    while len(lists) > 1:
        merged = []
        for i in range(0, len(lists), 2):
            l1 = lists[i]
            l2 = lists[i + 1] if i + 1 < len(lists) else None
            merged.append(merge_two(l1, l2))
        lists = merged
    return lists[0]

def merge_two(l1, l2):
    dummy = ListNode(0)
    curr = dummy
    while l1 and l2:
        if l1.val <= l2.val:
            curr.next = l1
            l1 = l1.next
        else:
            curr.next = l2
            l2 = l2.next
        curr = curr.next
    curr.next = l1 or l2
    return dummy.next
```

---

### Problem 6: Find Median from Data Stream (LC 295 — Hard)

**Problem:** Design a data structure that supports:
- `addNum(num)`: Add an integer to the data structure
- `findMedian()`: Return the median of all elements added so far

**Brute Force:**
Keep a sorted list. Insert in O(n) (find position + shift). Median in O(1).

**Key Insight (Two Heaps):**
Maintain a max-heap for the lower half and a min-heap for the upper half. The median is always accessible from the tops of the heaps.

- `addNum`: Push to max_heap, then balance by moving the top to min_heap, then rebalance sizes.
- `findMedian`: If sizes are equal, average the two tops. Otherwise, the larger heap's top.

**Optimal Solution:**

```python
import heapq

class MedianFinder:
    """
    LC 295: Find Median from Data Stream

    addNum: O(log n)
    findMedian: O(1)
    Space: O(n)
    """
    def __init__(self):
        # Max-heap for lower half (store negated values)
        self.lo = []
        # Min-heap for upper half
        self.hi = []

    def addNum(self, num: int) -> None:
        # Step 1: Add to max-heap (lower half)
        heapq.heappush(self.lo, -num)

        # Step 2: Ensure max of lo <= min of hi
        heapq.heappush(self.hi, -heapq.heappop(self.lo))

        # Step 3: Balance sizes (lo can be 1 larger than hi)
        if len(self.hi) > len(self.lo):
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def findMedian(self) -> float:
        if len(self.lo) > len(self.hi):
            return -self.lo[0]
        return (-self.lo[0] + self.hi[0]) / 2.0
```

**Why this always works:**
After every `addNum`:
1. We push to `lo` first (temporarily may violate ordering)
2. We move `lo`'s max to `hi` (restores ordering invariant: all lo <= all hi)
3. We rebalance sizes (if hi grew too large, move its min back to lo)

This ensures both invariants hold after every insertion.

**Dry Run:**
```
addNum(1):
  Push -1 to lo. lo=[-1]
  Pop lo (1), push to hi. lo=[], hi=[1]
  hi larger → pop hi (1), push to lo. lo=[-1], hi=[]
  Median: -lo[0] = 1

addNum(2):
  Push -2 to lo. lo=[-2,-1]
  Pop lo (2), push to hi. lo=[-1], hi=[2]
  Sizes equal. lo=[-1], hi=[2]
  Median: (1 + 2) / 2 = 1.5

addNum(3):
  Push -3 to lo. lo=[-3,-1]
  Pop lo (3), push to hi. lo=[-1], hi=[2,3]
  hi larger → pop hi (2), push to lo. lo=[-2,-1], hi=[3]
  Median: -lo[0] = 2

addNum(0):
  Push 0 to lo. lo=[-2,-1,0]
  Pop lo (2), push to hi. lo=[-1,0], hi=[2,3]
  Sizes equal. lo=[-1,0], hi=[2,3]
  Wait: lo has [-1,0] → max is 0 (note: -lo[0] = 1, so max of lo is 1...

  Hmm, lo stores negated values. lo=[-2,-1,0]: heap property means -2 is at top,
  so -lo[0] = 2. That means the max of the lower half is 2.

  Let me redo: After push -0=0 to lo: lo = [-2, -1, 0] with heap top = -2.
  Pop lo: -(-2) = 2, push 2 to hi. lo=[-1, 0], hi=[2, 2, 3].
  hi (size 3) > lo (size 2) → pop hi (2), push -2 to lo. lo=[-2, -1, 0], hi=[2, 3].

  Wait, that gives lo max = 2, hi min = 2. That is fine (lo max <= hi min).

  Actually let me re-examine more carefully.

  lo stores negated: lo=[-2, 0, -1] (heap order). -lo[0] = 2. Max of lower half = 2.
  hi = [2, 3]. Min of upper half = 2.
  2 <= 2. Invariant holds.

  Median = (2 + 2) / 2 = 2.0? But elements are [0, 1, 2, 3], median should be 1.5.

  Something is wrong with my dry run. Let me redo from scratch.
```

Let me redo the dry run more carefully:
```
addNum(1):
  lo=[], hi=[]
  Push -1 to lo → lo=[-1]
  Pop lo → -(-1)=1, push to hi → hi=[1]. lo=[]
  len(hi)=1 > len(lo)=0 → pop hi → 1, push -1 to lo → lo=[-1]. hi=[]
  State: lo=[-1], hi=[]

addNum(2):
  Push -2 to lo → lo=[-2,-1]
  Pop lo → -(-2)=2, push to hi → hi=[2]. lo=[-1]
  len(hi)=1 == len(lo)=1, balanced.
  State: lo=[-1], hi=[2]
  Median = (1+2)/2 = 1.5

addNum(3):
  Push -3 to lo → lo=[-3,-1]
  Pop lo → -(-3)=3, push to hi → hi=[2,3]. lo=[-1]
  len(hi)=2 > len(lo)=1 → pop hi → 2, push -2 to lo → lo=[-2,-1]. hi=[3]
  State: lo=[-2,-1], hi=[3]. Max of lo = 2, min of hi = 3.
  Median = 2

addNum(0):
  Push 0 to lo → lo=[-2,-1,0]
  Pop lo → -(-2)=2, push to hi → hi=[2,3]. lo=[-1,0]
  len(hi)=2 == len(lo)=2, balanced.
  State: lo=[-1,0], hi=[2,3]. Max of lo = -(-1)=1. Min of hi = 2.
  Elements so far: 0, 1, 2, 3. Median = (1+2)/2 = 1.5.

  Hmm, lo=[-1, 0] as a heap. Heap top is -1, so -lo[0] = 1. But lo also has 0,
  meaning the value 0 is in the lower half. -0 = 0, so the actual value is 0.
  Lower half values: {1, 0}. Max = 1. Correct!

  Median = (1 + 2) / 2 = 1.5. Correct!
```

**Edge Cases:**
- Single element: return it
- Two elements: return average
- All same elements: return that element
- Alternating large and small: heaps balance

**Follow-up:** What about sliding window median (LC 480)? Use two heaps with lazy deletion. When an element leaves the window, mark it as deleted and only actually remove it when it surfaces at a heap top.

**Sliding Window Median (LC 480) sketch:**

```python
import heapq
from collections import defaultdict

class SlidingWindowMedian:
    def __init__(self):
        self.lo = []  # max-heap (lower half)
        self.hi = []  # min-heap (upper half)
        self.delayed = defaultdict(int)  # lazy deletion counts
        self.lo_size = 0
        self.hi_size = 0

    def add(self, num):
        if not self.lo or num <= -self.lo[0]:
            heapq.heappush(self.lo, -num)
            self.lo_size += 1
        else:
            heapq.heappush(self.hi, num)
            self.hi_size += 1
        self._balance()

    def remove(self, num):
        self.delayed[num] += 1
        if num <= -self.lo[0]:
            self.lo_size -= 1
        else:
            self.hi_size -= 1
        self._balance()

    def _balance(self):
        # lo can have at most 1 more element than hi
        while self.lo_size > self.hi_size + 1:
            val = -heapq.heappop(self.lo)
            self._prune(self.lo)
            heapq.heappush(self.hi, val)
            self.lo_size -= 1
            self.hi_size += 1
        while self.hi_size > self.lo_size:
            val = heapq.heappop(self.hi)
            self._prune(self.hi)
            heapq.heappush(self.lo, -val)
            self.hi_size -= 1
            self.lo_size += 1

    def _prune(self, heap):
        while heap:
            val = -heap[0] if heap is self.lo else heap[0]
            if self.delayed[val] > 0:
                self.delayed[val] -= 1
                heapq.heappop(heap)
            else:
                break

    def median(self):
        if self.lo_size > self.hi_size:
            return -self.lo[0]
        return (-self.lo[0] + self.hi[0]) / 2.0
```

This demonstrates the lazy deletion pattern — a frequently tested concept at Google and Meta.

---

## Common Mistakes & Interview Tips

### Common Mistakes

1. **Forgetting Python's heapq is min-heap:** For max-heap, negate values. This is the #1 source of bugs.

2. **Not using a tiebreaker in tuples:** When heap elements have equal priority, Python tries to compare the next tuple element. If that element is not comparable (like a ListNode), it crashes. Always include a unique tiebreaker (like an index).

3. **Modifying heap elements in place:** Heaps do not re-heapify when you change an element's value. Either use lazy deletion or re-heapify manually.

4. **Using heap when sorting suffices:** If you process all data at once and only need the final result, sorting may be simpler and equally efficient. Heaps shine for streaming data or when K << N.

5. **Overflow in two-heap median:** When computing the median as the average of two values, use `(a + b) / 2.0` (float division) not `(a + b) // 2` (integer division). In Python this is not an issue, but it matters in Go/Java/C++.

6. **Heap size management for Top K:** When maintaining a heap of size K, always check `if len(heap) > k` after pushing. A common bug is checking before pushing.

### Interview Tips

1. **State complexity precisely:** "Using a min-heap of size K, each push/pop is O(log K). Over N elements, total time is O(N log K)."

2. **Know the two-heap pattern cold:** Median from Data Stream is extremely common at Meta, Google, and Amazon. The three-step addNum (push to lo, move to hi, rebalance) should be automatic.

3. **Mention alternatives:** For Kth Largest, mention both heap O(N log K) and quickselect O(N) average. For Top K, mention bucket sort O(N). Showing you know multiple approaches is impressive.

4. **Python heapq shortcuts:** `heapq.nlargest(k, iterable)` and `heapq.nsmallest(k, iterable)` exist but are O(N log K) internally. Good for quick solutions but mention you know the underlying algorithm.

5. **Custom comparators in Python:** Python heapq does not support custom comparators. Use tuples with the comparison key first, or negate values. In Go, implement the heap.Interface.

6. **Lazy deletion:** For problems like Sliding Window Median or IPO, you often need to "remove" elements from the middle of a heap. Lazy deletion (mark as removed, skip when popped) is the standard technique. Explain this proactively.

---

## Pattern Connections

| From Heap | Connect To | How |
|-----------|-----------|-----|
| Top K Elements | Quickselect | O(n) average alternative for static data |
| Merge K Sorted Lists | Divide and Conquer | Merge pairs recursively as alternative |
| Task Scheduler | Greedy | Always pick most frequent first |
| Find Median | Two Pointers (conceptual) | Partition into two halves |
| Dijkstra's Algorithm | Graph BFS | Heap replaces queue for weighted graphs |
| Sliding Window Median | Monotonic Deque | Deque for window max, heaps for median |
| Employee Free Time | Intervals | Heap-based merge of sorted lists |
| Reorganize String | Greedy + Cooldown | Same pattern as Task Scheduler |

### Decision Framework

```
Need repeated access to min/max in a changing collection?
├── Need just the top element?
│   └── Single Heap — O(log n) per operation
├── Need Kth element?
│   ├── Static array → Quickselect O(n)
│   └── Stream → Min-heap of size K, O(n log k)
├── Need median?
│   └── Two Heaps — max-heap (lower) + min-heap (upper)
├── Merging K sorted sequences?
│   └── Min-heap of size K
├── Greedy scheduling with priorities?
│   └── Max-heap of frequencies + cooldown queue
└── Need min/max in sliding window?
    └── Monotonic Deque (not heap) — O(n)
```

---

## Additional Problem: K Closest Points to Origin (LC 973 — Medium)

**Problem:** Given an array of points, return the K closest points to the origin (0, 0).

**Key Insight:**
Use a max-heap of size K. For each point, compute its squared distance (no need for sqrt — comparing squared distances preserves order). Push to the heap, pop if size > K.

```python
import heapq

def kClosest(points: list[list[int]], k: int) -> list[list[int]]:
    """
    LC 973: K Closest Points to Origin

    Time: O(n log k)
    Space: O(k)
    """
    # Max-heap of size k: negate distance for max-heap behavior
    heap = []
    for x, y in points:
        dist = -(x * x + y * y)  # Negate for max-heap
        if len(heap) < k:
            heapq.heappush(heap, (dist, x, y))
        elif dist > heap[0][0]:  # Closer than the farthest in our k-set
            heapq.heapreplace(heap, (dist, x, y))

    return [[x, y] for _, x, y in heap]
```

**Why `heapreplace` instead of pop+push?** `heapreplace` is slightly more efficient — it combines pop and push into a single operation.

**Alternative (quickselect):**
Like Kth Largest Element, we can use a partition-based approach to find the K closest in O(n) average time.

---

## Additional Problem: IPO (LC 502 — Hard)

**Problem:** Given n projects with profits `profits[i]` and minimum capital requirements `capital[i]`, starting with initial capital `w`, you can complete at most `k` projects (one at a time). After completing a project, your capital increases by its profit. Maximize final capital.

**Key Insight:**
Greedy: always pick the most profitable available project. Use two data structures:
1. A min-heap sorted by capital requirement (to efficiently find unlocked projects)
2. A max-heap of profits of unlocked projects (to pick the most profitable)

```python
import heapq

def findMaximizedCapital(k: int, w: int, profits: list[int], capital: list[int]) -> int:
    """
    LC 502: IPO

    Time: O(n log n)
    Space: O(n)
    """
    # Min-heap of (capital_needed, profit)
    projects = [(cap, prof) for cap, prof in zip(capital, profits)]
    heapq.heapify(projects)

    # Max-heap of available profits
    available = []

    for _ in range(k):
        # Unlock all projects we can afford
        while projects and projects[0][0] <= w:
            cap, prof = heapq.heappop(projects)
            heapq.heappush(available, -prof)

        if not available:
            break

        # Pick the most profitable available project
        w += -heapq.heappop(available)

    return w
```

This problem demonstrates the "two-heap" pattern in a different context (not median, but unlock+select). It is a common pattern at Google and Amazon.

---

## Interview Cheat Sheet

**Python heap operations to know cold:**
```python
import heapq
heapq.heappush(heap, item)      # Push
heapq.heappop(heap)             # Pop smallest
heap[0]                         # Peek smallest (O(1))
heapq.heapify(list)             # Build heap in-place O(n)
heapq.heapreplace(heap, item)   # Pop + push in one operation
heapq.nlargest(k, iterable)    # K largest elements
heapq.nsmallest(k, iterable)   # K smallest elements
```

**Max-heap in Python (negate everything):**
```python
heapq.heappush(heap, -val)      # Push
max_val = -heapq.heappop(heap)  # Pop largest
peek_max = -heap[0]             # Peek largest
```

**Tuple comparison in heapq:**
Tuples are compared element by element. Use `(priority, tiebreaker, item)` format. The tiebreaker (e.g., an incrementing counter) prevents comparison of incomparable items.

**Five things to say when using a heap in an interview:**
1. "I use a min-heap of size K because the top of the heap gives me the Kth [largest/smallest]."
2. "Python's heapq is a min-heap. For max-heap behavior, I negate the values."
3. "Each push/pop is O(log K), and I process N elements, so total time is O(N log K)."
4. "For the two-heap median pattern: max-heap stores the lower half, min-heap stores the upper half, and I rebalance after each insertion."
5. "I include a tiebreaker in my heap tuples to avoid comparing incomparable objects."

---

## Problem Difficulty Progression

**Tier 1 — Foundation (must solve easily):**
1. Kth Largest Element in Array (LC 215) — basic heap / quickselect
2. Last Stone Weight (LC 1046) — max-heap simulation
3. K Closest Points to Origin (LC 973) — max-heap of size K

**Tier 2 — Core Patterns (should solve within 20 min):**
4. Top K Frequent Elements (LC 347) — frequency + heap
5. Task Scheduler (LC 621) — greedy scheduling
6. Reorganize String (LC 767) — greedy placement
7. Sort Characters By Frequency (LC 451) — frequency sort

**Tier 3 — Hard Applications (stretch goals):**
8. Merge K Sorted Lists (LC 23) — K-way merge
9. Find Median from Data Stream (LC 295) — two heaps
10. IPO (LC 502) — two heaps, unlock pattern
11. Sliding Window Median (LC 480) — two heaps + lazy deletion
12. Smallest Range Covering Elements from K Lists (LC 632) — K-way merge + window

---

## Common Variations in Interviews

### Variation 1: "Can you do this in O(n)?"
For Kth element in a static array, yes — use quickselect. For streaming data, no — O(n log k) with a heap is optimal.

### Variation 2: "What if duplicates matter?"
For Top K Frequent, duplicates increase frequency counts but the heap logic stays the same. For Kth Largest, duplicates count (the 2nd largest in [3,3,2] is 3, not 2).

### Variation 3: "What about a balanced BST instead of two heaps for median?"
A balanced BST (like a sorted container) supports O(log n) insertion, deletion, and median lookup. It is more flexible than two heaps (supports arbitrary deletion) but harder to implement. In Python, use `sortedcontainers.SortedList`. In Java, use `TreeMap`.

### Variation 4: "How does this scale to distributed systems?"
For Top K across multiple machines, each machine maintains a local top-K heap. A coordinator merges the top-K from all machines (merge K sorted lists). This is a common system design pattern.
