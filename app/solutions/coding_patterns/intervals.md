# Intervals — Complete Interview Guide

## When to Use This Pattern

Interval problems involve ranges of values — typically `[start, end]` pairs representing time slots, segments, or numeric ranges. The core operations are detecting overlaps, merging, splitting, and scheduling.

**Primary signals:**
- "Merge overlapping intervals"
- "How many meeting rooms are needed?"
- "Non-overlapping intervals" / "minimum removals"
- "Insert an interval into a sorted list"
- "Find free time" / "find gaps"
- "Maximum number of concurrent events"
- Problem gives you pairs `[start, end]` and asks about relationships between them

**Three fundamental relationships between intervals [a, b] and [c, d] (assuming a <= c):**
1. **No overlap:** `b < c` — they are disjoint
2. **Overlap:** `b >= c` — they share at least one point
3. **Containment:** `a <= c` and `b >= d` — one contains the other

**Sorting strategy — the critical first step:**
Almost every interval problem starts with sorting. The choice of sort key matters:
- **Sort by start time:** Used for merge, insert, and most general problems
- **Sort by end time:** Used for greedy selection (maximize non-overlapping intervals)
- **Sort by both (start, then end):** Default when you need a canonical ordering

---

## Core Mechanics

### The Sweep Line Technique

Instead of comparing every pair of intervals (O(n^2)), the sweep line technique processes events in sorted order. It transforms 2D interval relationships into a 1D sequence of events.

**How it works for "maximum concurrent events" (Meeting Rooms II):**

```
Intervals: [0,30], [5,10], [15,20]

Create events:
  (0, 'start'), (5, 'start'), (10, 'end'), (15, 'start'), (20, 'end'), (30, 'end')

Sort by time (break ties: end before start if using exclusive ends):
  t=0:  start → active=1
  t=5:  start → active=2  ← peak!
  t=10: end   → active=1
  t=15: start → active=2  ← peak!
  t=20: end   → active=1
  t=30: end   → active=0

Maximum concurrent = 2 → need 2 meeting rooms
```

**Why sweep line is powerful:** It reduces interval overlap questions to a simple counter that increments on starts and decrements on ends.

### The Merge Pattern

When merging overlapping intervals, sort by start time, then iterate. Maintain a "current" interval. If the next interval overlaps with current (its start <= current's end), extend current's end. Otherwise, finalize current and start a new one.

```
Input:  [1,3], [2,6], [8,10], [15,18]
Sorted: [1,3], [2,6], [8,10], [15,18]

current = [1,3]
  [2,6]: 2 <= 3, overlap → current = [1, max(3,6)] = [1,6]
  [8,10]: 8 > 6, no overlap → emit [1,6], current = [8,10]
  [15,18]: 15 > 10, no overlap → emit [8,10], current = [15,18]
Emit [15,18]

Result: [1,6], [8,10], [15,18]
```

### Sort-by-Start vs Sort-by-End

**Sort by start:** "I want to process intervals in the order they begin." Used when merging, inserting, or sweeping from left to right.

**Sort by end:** "I want to greedily pick intervals that finish earliest." Used for maximum non-overlapping intervals (the activity selection problem). By always picking the interval that ends soonest, you leave the most room for future intervals.

**Example — Activity Selection:**
```
Intervals: [1,4], [2,3], [3,5], [0,6], [5,7], [8,9], [5,9]
Sorted by end: [2,3], [1,4], [3,5], [0,6], [5,7], [5,9], [8,9]

Pick [2,3] (ends first). Next must start >= 3.
Pick [3,5] (starts at 3 >= 3). Next must start >= 5.
Pick [5,7] (starts at 5 >= 5). Next must start >= 7.
Pick [8,9] (starts at 8 >= 7).

Max non-overlapping = 4.
```

### Overlap Detection — The Foundation

The ability to detect whether two intervals overlap is the fundamental building block for all interval problems. Let intervals be [a, b] and [c, d].

**General overlap test (unsorted):**
Two intervals overlap if and only if: `a <= d AND c <= b`

This can be remembered as: "neither interval ends before the other starts."

**Simplified test (sorted by start, a <= c):**
They overlap if and only if: `c <= b` (the second interval starts before the first one ends)

**Visual cases with [a,b] starting first:**
```
Case 1: No overlap     [a----b]
                                [c----d]    b < c

Case 2: Partial overlap [a----b]
                           [c----d]         c <= b, d > b

Case 3: b contains d   [a---------b]
                          [c--d]            c <= b, d <= b

Case 4: Touching        [a----b]
                              [c----d]      b == c (overlapping if inclusive)
```

### The Sweep Line Explained in Depth

The sweep line is a general-purpose technique for processing intervals. Instead of thinking about intervals as 2D objects, decompose each interval into two events: a start event and an end event. Then sort all events by time and process them in order.

**Why the sweep line works:**
At any time t, the number of active intervals equals the number of starts before t minus the number of ends before t. By processing events in sorted order, we maintain a running count of active intervals.

**Tie-breaking matters:**
When a start and end event happen at the same time, the order depends on whether endpoints are inclusive or exclusive:
- Inclusive endpoints (most LeetCode problems): process ends first (a room freed at time 5 can be used by a meeting starting at time 5)
- Exclusive endpoints: process starts first

In Python, when events are tuples `(time, delta)` where delta is +1 for start and -1 for end, sorting naturally puts -1 before +1 for the same time, which handles inclusive endpoints correctly.

---

## The Template

### Python — Merge Intervals

```python
def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    """Merge all overlapping intervals."""
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]

    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])

    return merged
```

### Python — Sweep Line (Count Maximum Overlap)

```python
def max_overlap(intervals: list[list[int]]) -> int:
    """Find maximum number of overlapping intervals at any point."""
    events = []
    for start, end in intervals:
        events.append((start, 1))   # +1 at start
        events.append((end, -1))    # -1 at end

    events.sort()  # Sort by time, then by type (-1 before +1 for ties)
    max_concurrent = 0
    current = 0

    for _, delta in events:
        current += delta
        max_concurrent = max(max_concurrent, current)

    return max_concurrent
```

### Go — Merge Intervals

```go
import "sort"

func merge(intervals [][]int) [][]int {
    sort.Slice(intervals, func(i, j int) bool {
        return intervals[i][0] < intervals[j][0]
    })

    merged := [][]int{intervals[0]}

    for _, interval := range intervals[1:] {
        last := merged[len(merged)-1]
        if interval[0] <= last[1] {
            if interval[1] > last[1] {
                last[1] = interval[1]
            }
        } else {
            merged = append(merged, interval)
        }
    }
    return merged
}
```

### Go — Sweep Line

```go
import "sort"

func maxOverlap(intervals [][]int) int {
    events := make([][2]int, 0, len(intervals)*2)
    for _, iv := range intervals {
        events = append(events, [2]int{iv[0], 1})
        events = append(events, [2]int{iv[1], -1})
    }
    sort.Slice(events, func(i, j int) bool {
        if events[i][0] == events[j][0] {
            return events[i][1] < events[j][1]
        }
        return events[i][0] < events[j][0]
    })
    maxC, cur := 0, 0
    for _, e := range events {
        cur += e[1]
        if cur > maxC {
            maxC = cur
        }
    }
    return maxC
}
```

---

## Variant Subpatterns

### 1. Merge Overlapping
Sort by start, greedily extend the current interval when overlaps are found.

### 2. Insert Into Sorted Intervals
Three phases: add intervals before the new one, merge overlapping ones, add intervals after.

### 3. Sweep Line / Event Processing
Convert intervals to start/end events, sort, and sweep. Used for counting concurrent events, finding maximum overlap.

### 4. Greedy Selection (Sort by End)
Pick the interval that ends earliest, skip all overlapping intervals, repeat. Maximizes the count of non-overlapping intervals.

### 5. Min-Heap for Interval Scheduling
Use a min-heap to track end times of active intervals. Used for Meeting Rooms II to count minimum resources.

### 6. Interval Query with Offline Processing
Sort both intervals and queries, process together. Used when you need to answer many "which interval contains this point?" queries.

---

## Problem Walkthroughs

---

### Problem 1: Merge Intervals (LC 56 — Medium)

**Problem:** Given an array of intervals where `intervals[i] = [start_i, end_i]`, merge all overlapping intervals and return an array of non-overlapping intervals that cover all the input ranges.

**Brute Force:**
Compare every pair of intervals. If they overlap, merge them. Repeat until no more merges are possible. O(n^2) or worse due to repeated passes.

**Key Insight:**
Sort by start time. Then a single pass suffices: if the current interval overlaps with the last merged interval, extend it. Otherwise, start a new merged interval. This works because sorting guarantees that if interval B does not overlap with A, then no interval after B can overlap with A either (they all start later).

**Optimal Solution:**

```python
def merge(intervals: list[list[int]]) -> list[list[int]]:
    """
    LC 56: Merge Intervals

    Time: O(n log n) for sorting
    Space: O(n) for output
    """
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]

    for start, end in intervals[1:]:
        if start <= merged[-1][1]:  # Overlaps with last merged
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])

    return merged
```

**Dry Run:**
```
intervals = [[1,3],[2,6],[8,10],[15,18]]
Sorted: [[1,3],[2,6],[8,10],[15,18]]

merged = [[1,3]]
  [2,6]: 2 <= 3 → overlap, extend to [1, max(3,6)] = [1,6]
  [8,10]: 8 > 6 → no overlap, add [8,10]
  [15,18]: 15 > 10 → no overlap, add [15,18]

Result: [[1,6],[8,10],[15,18]]
```

**Edge Cases:**
- Single interval: return as-is
- All intervals overlap: return one merged interval
- No overlaps: return sorted input
- One interval contains another: `[[1,10],[2,3]]` → `[[1,10]]`
- Adjacent but not overlapping: `[[1,2],[3,4]]` — depends on problem definition (usually not merged since 2 < 3)

**Follow-up:** What if intervals are streaming in one at a time? Maintain a sorted data structure (balanced BST or sorted list) and merge on insertion. See LC 352 (Data Stream as Disjoint Intervals).

**Why sorting works (proof sketch):**
After sorting by start time, for intervals A and B where A.start <= B.start:
- If B.start > A.end: A and B do not overlap, AND no future interval C (with C.start >= B.start) can overlap with A. So A is finalized.
- If B.start <= A.end: they overlap. Merge them by extending A.end = max(A.end, B.end). Continue checking the next interval against the merged result.

This greedy approach is correct because sorting ensures we never miss an overlap.

**Complexity Analysis:**
- Sorting: O(n log n)
- Single merge pass: O(n)
- Total: O(n log n) dominated by sorting
- Space: O(n) for the output (O(1) extra if done in-place)

---

### Problem 2: Insert Interval (LC 57 — Medium)

**Problem:** Given a sorted non-overlapping list of intervals and a new interval, insert the new interval and merge if necessary. Return the result sorted.

**Brute Force:**
Add the new interval to the list, then run the merge algorithm from LC 56. O(n log n) due to sorting.

**Key Insight:**
Since the list is already sorted and non-overlapping, we can do a single O(n) pass with three phases:
1. Add all intervals that end before the new interval starts (no overlap, left side)
2. Merge all intervals that overlap with the new interval
3. Add all intervals that start after the new interval ends (no overlap, right side)

**Optimal Solution:**

```python
def insert(intervals: list[list[int]], newInterval: list[int]) -> list[list[int]]:
    """
    LC 57: Insert Interval

    Time: O(n)
    Space: O(n) for output
    """
    result = []
    i = 0
    n = len(intervals)

    # Phase 1: Add intervals that come entirely before newInterval
    while i < n and intervals[i][1] < newInterval[0]:
        result.append(intervals[i])
        i += 1

    # Phase 2: Merge overlapping intervals with newInterval
    while i < n and intervals[i][0] <= newInterval[1]:
        newInterval[0] = min(newInterval[0], intervals[i][0])
        newInterval[1] = max(newInterval[1], intervals[i][1])
        i += 1
    result.append(newInterval)

    # Phase 3: Add intervals that come entirely after newInterval
    while i < n:
        result.append(intervals[i])
        i += 1

    return result
```

**Dry Run:**
```
intervals = [[1,2],[3,5],[6,7],[8,10],[12,16]], newInterval = [4,8]

Phase 1: intervals ending before 4:
  [1,2]: end=2 < 4 → add. result = [[1,2]]
  [3,5]: end=5 >= 4 → stop.

Phase 2: intervals starting <= 8:
  [3,5]: start=3 <= 8 → merge: newInterval = [min(4,3), max(8,5)] = [3,8]
  [6,7]: start=6 <= 8 → merge: newInterval = [min(3,6), max(8,7)] = [3,8]
  [8,10]: start=8 <= 8 → merge: newInterval = [min(3,8), max(8,10)] = [3,10]
  [12,16]: start=12 > 8 → stop.
  Add newInterval = [3,10]. result = [[1,2],[3,10]]

Phase 3: remaining intervals:
  [12,16] → add. result = [[1,2],[3,10],[12,16]]
```

**Edge Cases:**
- Empty intervals list: return `[newInterval]`
- New interval before all: insert at beginning
- New interval after all: insert at end
- New interval covers everything: single merged interval
- No overlap: insert in correct sorted position

**Follow-up:** What if you need to do many insertions? Use a balanced BST (like a sorted container) to maintain O(log n) insertion with merge.

---

### Problem 3: Meeting Rooms II (LC 253 — Medium)

**Problem:** Given an array of meeting time intervals `[start_i, end_i]`, find the minimum number of conference rooms required.

**Brute Force:**
For each time point, count how many meetings are active. O(n * max_time).

**Key Insight (Sweep Line):**
Convert to events: each meeting creates a +1 event at its start and a -1 event at its end. Sort events by time. Sweep through, maintaining a counter of active meetings. The maximum counter value is the answer.

**Alternative Insight (Min-Heap):**
Sort meetings by start time. Use a min-heap to track end times of ongoing meetings. For each new meeting, if it starts after the earliest ending meeting, that room is freed (pop from heap). Push the new meeting's end time. The heap size at any point is the number of rooms in use.

**Optimal Solution (Sweep Line):**

```python
def minMeetingRooms_sweep(intervals: list[list[int]]) -> int:
    """
    LC 253: Meeting Rooms II — Sweep Line

    Time: O(n log n)
    Space: O(n)
    """
    events = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))

    events.sort()  # Sort by time; ties: -1 before +1 (end before start)
    max_rooms = 0
    current = 0

    for _, delta in events:
        current += delta
        max_rooms = max(max_rooms, current)

    return max_rooms
```

**Optimal Solution (Min-Heap):**

```python
import heapq

def minMeetingRooms(intervals: list[list[int]]) -> int:
    """
    LC 253: Meeting Rooms II — Min-Heap

    Time: O(n log n)
    Space: O(n)
    """
    if not intervals:
        return 0

    intervals.sort(key=lambda x: x[0])
    heap = []  # Min-heap of end times

    for start, end in intervals:
        if heap and heap[0] <= start:
            heapq.heappop(heap)  # Room is freed
        heapq.heappush(heap, end)

    return len(heap)
```

**Dry Run (Min-Heap):**
```
intervals = [[0,30],[5,10],[15,20]]
Sorted: [[0,30],[5,10],[15,20]]

[0,30]: heap empty → push 30. heap=[30]. Rooms=1.
[5,10]: heap[0]=30, 30 > 5 → no room freed. Push 10. heap=[10,30]. Rooms=2.
[15,20]: heap[0]=10, 10 <= 15 → room freed! Pop 10. Push 20. heap=[20,30]. Rooms=2.

Max rooms = 2.
```

**Edge Cases:**
- No meetings: return 0
- One meeting: return 1
- All meetings overlap: return n
- Meetings that end exactly when another starts: `[1,5], [5,10]` → same room (depends on <= vs <)

**Follow-up:** What if each meeting has a priority and you want to assign rooms by priority? This becomes an assignment problem. What if rooms have different capacities? Constraint satisfaction.

**Why both approaches give the same answer:**
- Sweep line directly counts the maximum number of concurrent meetings
- Min-heap tracks room assignments: at any point, `len(heap)` equals the number of concurrent meetings

Both are O(n log n) due to sorting. The sweep line is more elegant for counting; the heap approach is more useful when you need to know which rooms are assigned.

**Variation — Meeting Rooms I (LC 252 — Easy):**
Given meeting intervals, determine if a person can attend all meetings (no overlaps). Simply sort by start time and check if any meeting starts before the previous one ends.

```python
def canAttendMeetings(intervals):
    intervals.sort()
    for i in range(1, len(intervals)):
        if intervals[i][0] < intervals[i-1][1]:
            return False
    return True
```

---

### Problem 4: Non-overlapping Intervals (LC 435 — Medium)

**Problem:** Given a collection of intervals, find the minimum number of intervals to remove to make the rest non-overlapping.

**Brute Force:**
Try all subsets of intervals, find the largest non-overlapping subset. O(2^n).

**Key Insight:**
This is the classic Activity Selection problem. The maximum number of non-overlapping intervals can be found greedily by sorting by end time and always picking the interval that ends earliest. The minimum removals = total intervals - maximum non-overlapping.

**Why sort by end time?** Picking the interval that ends earliest leaves the most room for subsequent intervals. This greedy choice is provably optimal.

**Optimal Solution:**

```python
def eraseOverlapIntervals(intervals: list[list[int]]) -> int:
    """
    LC 435: Non-overlapping Intervals

    Time: O(n log n)
    Space: O(1)
    """
    intervals.sort(key=lambda x: x[1])  # Sort by end time
    count = 0
    prev_end = float('-inf')

    for start, end in intervals:
        if start >= prev_end:
            # No overlap, keep this interval
            prev_end = end
        else:
            # Overlap, remove this interval (it ends later or equal)
            count += 1

    return count
```

**Dry Run:**
```
intervals = [[1,2],[2,3],[3,4],[1,3]]
Sorted by end: [[1,2],[2,3],[1,3],[3,4]]

prev_end = -inf
[1,2]: 1 >= -inf → keep. prev_end = 2. removed = 0
[2,3]: 2 >= 2  → keep. prev_end = 3. removed = 0
[1,3]: 1 < 3   → overlap, remove. removed = 1
[3,4]: 3 >= 3  → keep. prev_end = 4. removed = 1

Result: 1 (remove [1,3])
```

**Edge Cases:**
- All intervals identical: keep 1, remove n-1
- No overlaps: remove 0
- All pairwise overlapping: remove n-1 (keep 1)
- Intervals of length 0: `[1,1]` — valid, never overlaps with `[1,2]` if using strict comparison

**Follow-up:** What if intervals have weights and you want to maximize total weight of non-overlapping intervals? This becomes the Weighted Job Scheduling problem, solved with DP + binary search.

---

### Problem 5: Employee Free Time (LC 759 — Hard)

**Problem:** Given a list of employees, where each employee has a list of non-overlapping sorted intervals representing their working hours, find the free time common to all employees (intervals where no employee is working).

**Brute Force:**
Merge all employees' schedules into one timeline, find gaps. Need to handle overlaps carefully.

**Key Insight:**
Flatten all intervals from all employees into one list, sort by start time, then merge. The gaps between merged intervals are the free time periods.

Alternatively, use a min-heap to merge all sorted lists (similar to Merge K Sorted Lists), processing intervals in order of start time.

**Optimal Solution:**

```python
def employeeFreeTime(schedule: list[list[list[int]]]) -> list[list[int]]:
    """
    LC 759: Employee Free Time

    Time: O(n log n) where n = total intervals across all employees
    Space: O(n)
    """
    # Flatten all intervals
    all_intervals = []
    for employee in schedule:
        for interval in employee:
            all_intervals.append(interval)

    # Sort by start time
    all_intervals.sort(key=lambda x: x[0])

    # Find gaps between merged intervals
    free_time = []
    prev_end = all_intervals[0][1]

    for start, end in all_intervals[1:]:
        if start > prev_end:
            # Gap found — this is free time
            free_time.append([prev_end, start])
        prev_end = max(prev_end, end)

    return free_time
```

**Dry Run:**
```
schedule = [[[1,2],[5,6]], [[1,3]], [[4,10]]]

Flattened: [[1,2],[5,6],[1,3],[4,10]]
Sorted:    [[1,2],[1,3],[4,10],[5,6]]

prev_end = 2
[1,3]: 1 <= 2 → no gap. prev_end = max(2,3) = 3
[4,10]: 4 > 3 → gap! free_time = [[3,4]]. prev_end = max(3,10) = 10
[5,6]: 5 <= 10 → no gap. prev_end = 10

Result: [[3,4]]
```

**Edge Cases:**
- Single employee with contiguous schedule: no free time
- Employees with no overlap: many free time periods
- All employees share identical schedules: same result as single employee

**Follow-up (Heap-based approach for large inputs):**

```python
import heapq

def employeeFreeTime_heap(schedule):
    """Min-heap approach: merge k sorted interval lists."""
    heap = []  # (start, employee_idx, interval_idx)
    for emp_idx, employee in enumerate(schedule):
        if employee:
            heapq.heappush(heap, (employee[0][0], emp_idx, 0))

    free_time = []
    prev_end = float('-inf')

    while heap:
        start, emp_idx, iv_idx = heapq.heappop(heap)
        if prev_end != float('-inf') and start > prev_end:
            free_time.append([prev_end, start])
        prev_end = max(prev_end, schedule[emp_idx][iv_idx][1])

        # Push next interval from same employee
        if iv_idx + 1 < len(schedule[emp_idx]):
            next_start = schedule[emp_idx][iv_idx + 1][0]
            heapq.heappush(heap, (next_start, emp_idx, iv_idx + 1))

    return free_time
```

---

### Problem 6: Data Stream as Disjoint Intervals (LC 352 — Hard)

**Problem:** Design a data structure that:
- `addNum(val)`: Adds an integer to the stream
- `getIntervals()`: Returns a list of disjoint intervals covering all values added so far, in sorted order

**Brute Force:**
Keep a sorted list of all values. On `getIntervals`, scan through and merge consecutive values into intervals. addNum is O(n) for insertion, getIntervals is O(n).

**Key Insight:**
Maintain a sorted set of disjoint intervals. When adding a value, check if it extends an existing interval, merges two intervals, or creates a new one. Use a sorted container (like a BST or Python's `SortedList`) for efficient insertion and neighbor lookup.

**Optimal Solution:**

```python
from sortedcontainers import SortedList

class SummaryRanges:
    """
    LC 352: Data Stream as Disjoint Intervals

    addNum: O(log n)
    getIntervals: O(n)
    """
    def __init__(self):
        self.intervals = SortedList(key=lambda x: x[0])

    def addNum(self, val: int) -> None:
        new = [val, val]
        # Find insertion point
        idx = self.intervals.bisect_left([val, val])

        # Check if val merges with the previous interval
        if idx > 0 and self.intervals[idx - 1][1] >= val - 1:
            idx -= 1
            new[0] = min(new[0], self.intervals[idx][0])
            new[1] = max(new[1], self.intervals[idx][1])
            self.intervals.pop(idx)

        # Check if val merges with the next interval
        if idx < len(self.intervals) and self.intervals[idx][0] <= val + 1:
            new[0] = min(new[0], self.intervals[idx][0])
            new[1] = max(new[1], self.intervals[idx][1])
            self.intervals.pop(idx)

        self.intervals.add(new)

    def getIntervals(self) -> list[list[int]]:
        return list(self.intervals)
```

**Alternative (without SortedList):**

```python
import bisect

class SummaryRanges:
    def __init__(self):
        self.intervals = []

    def addNum(self, val: int) -> None:
        # Find the position to insert [val, val]
        new = [val, val]
        left, right = [], []

        for interval in self.intervals:
            if interval[1] < val - 1:
                left.append(interval)
            elif interval[0] > val + 1:
                right.append(interval)
            else:
                new[0] = min(new[0], interval[0])
                new[1] = max(new[1], interval[1])

        self.intervals = left + [new] + right

    def getIntervals(self) -> list[list[int]]:
        return self.intervals
```

**Dry Run:**
```
addNum(1): intervals = [[1,1]]
addNum(3): intervals = [[1,1],[3,3]]
addNum(7): intervals = [[1,1],[3,3],[7,7]]
addNum(2): 2 merges [1,1] and [3,3] → intervals = [[1,3],[7,7]]
addNum(6): 6 adjacent to [7,7] → intervals = [[1,3],[6,7]]

getIntervals() → [[1,3],[6,7]]
```

**Edge Cases:**
- Adding duplicates: no change
- Adding values in order: each creates a new interval, adjacent ones merge
- Adding a value that bridges two intervals: merges both

---

### Problem 7: Minimum Interval to Include Each Query (LC 1851 — Hard)

**Problem:** Given a list of intervals `[left_i, right_i]` and a list of queries `[q_1, q_2, ...]`, for each query find the length of the smallest interval that contains that query value. Return -1 if no interval contains the query.

**Brute Force:**
For each query, check all intervals. O(n * q).

**Key Insight:**
Offline processing: sort both intervals by start time and queries by value. Process queries in increasing order. For each query, add all intervals that start <= query to a min-heap (keyed by interval length). Remove intervals from the heap that end before the query. The top of the heap is the smallest valid interval.

**Optimal Solution:**

```python
import heapq

def minInterval(intervals: list[list[int]], queries: list[int]) -> list[int]:
    """
    LC 1851: Minimum Interval to Include Each Query

    Time: O((n + q) log n)
    Space: O(n + q)
    """
    intervals.sort()
    sorted_queries = sorted(enumerate(queries), key=lambda x: x[1])
    result = [-1] * len(queries)
    heap = []  # (interval_length, end)
    i = 0

    for orig_idx, q in sorted_queries:
        # Add all intervals that start <= q
        while i < len(intervals) and intervals[i][0] <= q:
            left, right = intervals[i]
            heapq.heappush(heap, (right - left + 1, right))
            i += 1

        # Remove intervals that end before q
        while heap and heap[0][1] < q:
            heapq.heappop(heap)

        # Top of heap is smallest interval containing q
        if heap:
            result[orig_idx] = heap[0][0]

    return result
```

**Dry Run:**
```
intervals = [[1,4],[2,4],[3,6],[4,4]], queries = [2,3,4,5]

Sort intervals: [[1,4],[2,4],[3,6],[4,4]]
Sort queries with indices: [(0,2),(1,3),(2,4),(3,5)]

Query q=2:
  Add [1,4] (start 1<=2): heap=[(4,4)]
  Add [2,4] (start 2<=2): heap=[(3,4),(4,4)]
  No removals (all end >= 2)
  result[0] = 3 (interval [2,4] has length 3)

Query q=3:
  Add [3,6] (start 3<=3): heap=[(3,4),(4,4),(4,6)]
  No removals
  result[1] = 3 (interval [2,4])

Query q=4:
  Add [4,4] (start 4<=4): heap=[(1,4),(3,4),(4,4),(4,6)]
  No removals
  result[2] = 1 (interval [4,4] has length 1)

Query q=5:
  No more intervals to add
  Remove (1,4): end 4 < 5. Remove (3,4): end 4 < 5. Remove (4,4): end 4 < 5.
  heap = [(4,6)]
  result[3] = 4 (interval [3,6])

Result: [3, 3, 1, 4]
```

**Edge Cases:**
- Query outside all intervals: return -1
- Multiple intervals of same length containing query: either works
- Single-point intervals: length = 1
- Queries with duplicate values: handled by sorting with indices

**Follow-up:** What if intervals are added dynamically? Use an interval tree or segment tree for online queries.

---

## Common Mistakes & Interview Tips

### Common Mistakes

1. **Not sorting first:** Almost every interval problem requires sorting as the first step. If you skip this, your solution will be wrong.

2. **Wrong overlap condition:** Two intervals `[a,b]` and `[c,d]` overlap when `a <= d AND c <= b` (assuming sorted, just check `c <= b`). Off-by-one errors here are extremely common.

3. **Confusing inclusive vs exclusive endpoints:** `[1,5]` and `[5,10]` — do these overlap? Depends on whether endpoints are inclusive. Most LeetCode problems use inclusive endpoints, so yes.

4. **Sort-by-start when sort-by-end is needed:** For the activity selection / non-overlapping intervals problem, sorting by end time is crucial. Sorting by start gives a wrong greedy.

5. **Modifying input intervals:** When merging, some solutions modify the interval objects in place. This can cause subtle bugs if the same interval objects are referenced elsewhere.

6. **Sweep line tie-breaking:** When a start event and end event happen at the same time, the order matters. For Meeting Rooms II with exclusive end times, process ends before starts at the same time (a room freed at time 5 can be used by a meeting starting at time 5).

### Interview Tips

1. **State the sort strategy immediately:** "First, I will sort by start time" (or end time). This frames your approach.

2. **Draw the intervals on a number line:** Visual representation makes overlap detection intuitive for both you and the interviewer.

3. **Know both sweep line and heap approaches for Meeting Rooms II:** Being able to discuss trade-offs shows depth.

4. **Mention the greedy proof for activity selection:** "Sorting by end time and greedily picking the earliest-ending interval is optimal because it maximizes remaining space for future intervals."

5. **Handle edge cases explicitly:** Empty input, single interval, all overlapping, no overlapping — mention these.

6. **Know when to use offline vs online processing:** Sorting queries for offline processing (LC 1851) is a powerful technique. Mention it proactively.

---

## Pattern Connections

| From Intervals | Connect To | How |
|---------------|-----------|-----|
| Merge Intervals | Sweep Line | Events are a generalization of intervals |
| Meeting Rooms II | Min-Heap | Track earliest end time for room reuse |
| Non-overlapping Intervals | Greedy (Activity Selection) | Sort by end, pick greedily |
| Employee Free Time | Merge K Sorted Lists | Heap-based merge of sorted interval lists |
| Min Interval for Query | Offline Processing + Heap | Sort queries, sweep with heap |
| Data Stream Intervals | Balanced BST / SortedList | Dynamic maintenance of sorted intervals |
| Sweep Line | Segment Tree | For range queries with updates |

### Decision Framework

```
Interval problem?
├── "Merge overlapping"
│   └── Sort by start, single pass merge
├── "How many rooms / max concurrent?"
│   ├── Sweep Line — events + counter
│   └── Min-Heap — track end times
├── "Maximum non-overlapping" / "minimum removals"
│   └── Greedy — sort by END time
├── "Insert into sorted intervals"
│   └── Three-phase scan (before, merge, after)
├── "Find gaps / free time"
│   └── Merge all, then find gaps between merged intervals
└── "Query: smallest interval containing X"
    └── Offline sort + min-heap
```

---

## Additional Problem: Interval List Intersections (LC 986 — Medium)

**Problem:** Given two sorted lists of disjoint intervals, return the intersection of the two lists.

**Key Insight:**
Two-pointer approach. Maintain a pointer for each list. At each step, the intersection of the current pair (if any) is `[max(a_start, b_start), min(a_end, b_end)]`. Advance the pointer whose current interval ends earlier.

```python
def intervalIntersection(firstList: list[list[int]], secondList: list[list[int]]) -> list[list[int]]:
    """
    LC 986: Interval List Intersections

    Time: O(m + n)
    Space: O(1) extra
    """
    result = []
    i, j = 0, 0

    while i < len(firstList) and j < len(secondList):
        a_start, a_end = firstList[i]
        b_start, b_end = secondList[j]

        # Check for intersection
        start = max(a_start, b_start)
        end = min(a_end, b_end)
        if start <= end:
            result.append([start, end])

        # Advance the pointer with the earlier end
        if a_end < b_end:
            i += 1
        else:
            j += 1

    return result
```

**Dry Run:**
```
firstList = [[0,2],[5,10],[13,23],[24,25]]
secondList = [[1,5],[8,12],[15,24],[25,26]]

i=0, j=0: [0,2] ∩ [1,5] = [max(0,1), min(2,5)] = [1,2]. a_end=2 < b_end=5, i++.
i=1, j=0: [5,10] ∩ [1,5] = [5,5]. a_end=10 > b_end=5, j++.
i=1, j=1: [5,10] ∩ [8,12] = [8,10]. a_end=10 < b_end=12, i++.
i=2, j=1: [13,23] ∩ [8,12] = [13,12] → 13>12, no intersection. j++.
i=2, j=2: [13,23] ∩ [15,24] = [15,23]. a_end=23 < b_end=24, i++.
i=3, j=2: [24,25] ∩ [15,24] = [24,24]. a_end=25 > b_end=24, j++.
i=3, j=3: [24,25] ∩ [25,26] = [25,25]. a_end=25 < b_end=26, i++.
i=4, done.

Result: [[1,2],[5,5],[8,10],[15,23],[24,24],[25,25]]
```

---

## Additional Problem: My Calendar I (LC 729 — Medium)

**Problem:** Implement a `MyCalendar` class that stores events. A new event `[start, end)` can be added if it does not cause a double booking (no two events overlap).

**Key Insight:**
Maintain a sorted list of booked intervals. For a new event, binary search for where it would be inserted and check neighbors for overlaps.

```python
from bisect import bisect_left, insort

class MyCalendar:
    """
    LC 729: My Calendar I

    book: O(n) due to list insertion
    Space: O(n)
    """
    def __init__(self):
        self.events = []  # Sorted by start time

    def book(self, start: int, end: int) -> bool:
        idx = bisect_left(self.events, (start, end))

        # Check overlap with previous event
        if idx > 0 and self.events[idx - 1][1] > start:
            return False

        # Check overlap with next event
        if idx < len(self.events) and self.events[idx][0] < end:
            return False

        insort(self.events, (start, end))
        return True
```

This problem bridges intervals with binary search and sorted containers. It is a common system design building block (calendar systems, scheduling).

---

## Interview Cheat Sheet

**The first thing to say for any interval problem:**
"I will start by sorting the intervals — by start time for merging/insertion, by end time for activity selection."

**Five-second mental model:**
```
Sort → Sweep/Merge → Collect results
```

**Critical formulas to remember:**
- Overlap test (sorted, A.start <= B.start): `B.start <= A.end`
- Merge: `[A.start, max(A.end, B.end)]`
- Intersection: `[max(A.start, B.start), min(A.end, B.end)]` (valid if start <= end)
- Number of rooms: max concurrent = max value of sweep counter

**When to sort by end vs start:**
- **Sort by start:** Merging, inserting, sweeping, most problems
- **Sort by end:** Greedy selection of maximum non-overlapping intervals

---

## Detailed Complexity Analysis

### Why Sorting is the Bottleneck

For most interval problems, the algorithm consists of two phases:
1. Sort: O(n log n)
2. Process: O(n) single pass

The sorting step dominates. You cannot do better than O(n log n) in the general case because intervals can arrive in any order.

**Exception:** If intervals are already sorted (as in LC 57 Insert Interval), the processing step is O(n) and no sorting is needed.

### Space Complexity Considerations

- **Merge Intervals:** O(n) for the output (required), O(1) extra (or O(log n) for sorting)
- **Sweep Line:** O(n) for the events array
- **Meeting Rooms II (Heap):** O(n) for the heap in worst case (all meetings overlap)
- **Meeting Rooms II (Sweep):** O(n) for events
- **In-place alternatives:** Some problems can be solved with O(1) extra space if you modify the input

### When Intervals Become Hard

Interval problems become hard when:
1. **Multiple constraints:** Non-overlapping + weighted selection (Weighted Job Scheduling)
2. **Dynamic operations:** Online insertion and deletion (require balanced BSTs)
3. **2D intervals:** Rectangle overlap detection (requires sweep line + BST)
4. **Circular intervals:** Intervals that wrap around (like a 24-hour clock)
5. **Query problems:** Offline processing with sorted queries (LC 1851)

---

## Problem Difficulty Progression

**Tier 1 — Foundation:**
1. Merge Intervals (LC 56) — sort + merge
2. Meeting Rooms (LC 252) — overlap check
3. Insert Interval (LC 57) — three-phase scan

**Tier 2 — Core Patterns:**
4. Meeting Rooms II (LC 253) — sweep line / heap
5. Non-overlapping Intervals (LC 435) — greedy
6. Interval List Intersections (LC 986) — two pointers

**Tier 3 — Advanced:**
7. Employee Free Time (LC 759) — merge + gaps
8. Data Stream as Disjoint Intervals (LC 352) — dynamic maintenance
9. Min Interval to Include Each Query (LC 1851) — offline + heap
10. Minimum Number of Arrows to Burst Balloons (LC 452) — greedy overlap

---

## Additional Problem: Minimum Number of Arrows to Burst Balloons (LC 452 — Medium)

**Problem:** Given balloons as intervals `[x_start, x_end]`, find the minimum number of arrows needed. An arrow at position x bursts all balloons where `x_start <= x <= x_end`.

**Key Insight:**
This is the activity selection problem: sort by end position, shoot an arrow at each end position. Skip all balloons that this arrow already covers.

```python
def findMinArrowShots(points: list[list[int]]) -> int:
    """
    LC 452: Minimum Number of Arrows

    Time: O(n log n)
    Space: O(1)
    """
    if not points:
        return 0

    points.sort(key=lambda x: x[1])  # Sort by end
    arrows = 1
    arrow_pos = points[0][1]

    for start, end in points[1:]:
        if start > arrow_pos:
            # Need a new arrow
            arrows += 1
            arrow_pos = end

    return arrows
```

This is mathematically equivalent to finding the maximum number of non-overlapping intervals — each "group" of overlapping balloons needs one arrow.

---

## Additional Problem: Weighted Job Scheduling (LC 1235 — Hard)

**Problem:** Given n jobs where each job has a start time, end time, and profit, find the maximum profit you can earn without taking overlapping jobs.

**Key Insight:**
This extends the activity selection problem with weights. Greedy (sort by end, take earliest ending) no longer works because a single high-profit long job may be better than many low-profit short jobs.

Use DP: sort jobs by end time. For each job i, binary search for the latest non-overlapping job j. `dp[i] = max(dp[i-1], profit[i] + dp[j])`.

```python
import bisect

def jobScheduling(startTime: list[int], endTime: list[int], profit: list[int]) -> int:
    """
    LC 1235: Job Scheduling for Maximum Profit

    Time: O(n log n)
    Space: O(n)
    """
    jobs = sorted(zip(endTime, startTime, profit))
    ends = [j[0] for j in jobs]
    dp = [0] * (len(jobs) + 1)

    for i in range(1, len(jobs) + 1):
        end, start, prof = jobs[i - 1]
        # Binary search: latest job ending <= start
        j = bisect.bisect_right(ends, start, 0, i)
        dp[i] = max(dp[i - 1], dp[j] + prof)

    return dp[-1]
```

**Dry Run:**
```
startTime = [1,2,3,3], endTime = [3,4,5,6], profit = [50,10,40,70]

Sorted by end: [(3,1,50), (4,2,10), (5,3,40), (6,3,70)]
ends = [3, 4, 5, 6]

dp[0] = 0
dp[1]: job (3,1,50). start=1. bisect_right(ends, 1, 0, 1) = 0. dp[1] = max(0, 0+50) = 50.
dp[2]: job (4,2,10). start=2. bisect_right(ends, 2, 0, 2) = 0. dp[2] = max(50, 0+10) = 50.
dp[3]: job (5,3,40). start=3. bisect_right(ends, 3, 0, 3) = 1. dp[3] = max(50, 50+40) = 90.
dp[4]: job (6,3,70). start=3. bisect_right(ends, 3, 0, 4) = 1. dp[4] = max(90, 50+70) = 120.

Result: 120. Take jobs [1,3] (profit 50) and [3,6] (profit 70).
```

This problem bridges intervals and DP. The binary search step is what makes it O(n log n) instead of O(n^2).

---

## Common Variations in Interviews

### Variation 1: "What if intervals can have negative values?"
Negative start/end values work fine — the algorithms only rely on ordering, not positivity.

### Variation 2: "What if endpoints are floating point?"
Same algorithms apply. Floating point comparison can introduce precision issues, but for interview purposes, the logic is identical.

### Variation 3: "What about 2D intervals (rectangles)?"
Rectangle overlap detection requires sweep line + balanced BST (or segment tree). Sort rectangles by x-coordinate, sweep from left to right, use a BST to track active y-ranges and detect overlaps.

### Variation 4: "What if we want to find the intersection of N interval lists?"
Generalize the two-pointer approach: use a priority queue (min-heap) to merge K sorted lists. Track the maximum start across all active intervals — the overlap exists while the minimum end >= maximum start.

---

## Thinking Framework: How to Approach a New Interval Problem

### Step 1: Understand the interval relationships
- Are we looking for overlaps, gaps, containment, or intersections?
- Are intervals given sorted? If not, sorting is almost always the first step.
- What defines "overlap"? Inclusive vs exclusive endpoints?

### Step 2: Choose the sort key
- **Merge / insert / sweep:** Sort by start time
- **Greedy selection:** Sort by end time
- **Both needed?** Two separate passes or two pointers

### Step 3: Choose the algorithm
- **Simple overlap detection:** Sort + single pass comparison
- **Count maximum concurrent:** Sweep line (events)
- **Track active set:** Min-heap of end times
- **Answer queries:** Offline sort + sweep

### Step 4: Handle edge cases
- Empty input
- Single interval
- All intervals identical
- Touching intervals (is [1,5] and [5,10] overlapping?)
- Very large or very small values

### Example: Applying the Framework to "Calendar" Problems

The LeetCode Calendar series (LC 729, 731, 732) tests interval mastery at increasing difficulty:

**My Calendar I (LC 729):** No double booking. Binary search for insert position, check neighbors.
**My Calendar II (LC 731):** Allow single overlap, no triple booking. Track overlapping intervals separately.
**My Calendar III (LC 732):** Return maximum K-booking at any time. Sweep line with a sorted map.

These are common interview problems at Google that combine intervals with data structure design.
