# Intervals Pattern Guide

## 1. What are Interval Problems?

### Explain Like I'm 5
Imagine you have a bunch of toy trains on different tracks, and each train runs during a specific time period. Some trains might be running at the same time (their times overlap), and sometimes you need to figure out things like:
- "Are any two trains running at the same time?"
- "Can I combine train schedules that overlap into one big schedule?"
- "Do I have enough tracks for all the trains?"

### Technical Definition
Interval problems involve working with ranges of values (typically time or numbers) represented as pairs `[start, end]`. These problems require understanding relationships between intervals such as:
- **Overlapping**: Two intervals share common values
- **Merging**: Combining overlapping/adjacent intervals
- **Intersection**: Finding common portions between intervals
- **Scheduling**: Determining resource allocation across time ranges

## 2. Real-World Analogy

**Meeting Room Scheduler:**
Imagine you're managing a company's conference rooms. You have booking requests like:
- Meeting A: 9:00 AM - 10:30 AM
- Meeting B: 10:00 AM - 11:00 AM
- Meeting C: 11:00 AM - 12:00 PM

Questions you might need to answer:
- Do any meetings overlap? (Yes, A and B overlap from 10:00-10:30)
- Can I merge consecutive/overlapping bookings? (A and B can be merged to 9:00-11:00)
- How many rooms do I need at peak time? (2 rooms at 10:00 AM)
- Where can I fit a new 30-minute meeting? (Need to find a gap)

## 3. When to Use This Pattern

**Clear Signals:**
- Problem mentions "intervals", "ranges", "time slots", "bookings"
- Need to find **overlapping** periods
- Asked to **merge** or **combine** ranges
- Scheduling problems with resources (meeting rooms, tasks, CPU scheduling)
- Looking for **gaps** between ranges
- Need to determine **maximum concurrent** events
- Problems involving "insert", "remove", or "query" on ranges

**Keywords to Watch For:**
- "merge overlapping"
- "meeting rooms"
- "non-overlapping"
- "minimum intervals to remove"
- "insert interval"
- "find free time"
- "maximum concurrent"

## 4. The Problem: Merge Intervals

**Classic Example (LeetCode 56):**

Given an array of intervals where `intervals[i] = [start_i, end_i]`, merge all overlapping intervals and return an array of the non-overlapping intervals that cover all the intervals in the input.

```
Example 1:
Input: intervals = [[1,3],[2,6],[8,10],[15,18]]
Output: [[1,6],[8,10],[15,18]]
Explanation: Since intervals [1,3] and [2,6] overlap, merge them into [1,6].

Example 2:
Input: intervals = [[1,4],[4,5]]
Output: [[1,5]]
Explanation: Intervals [1,4] and [4,5] are considered overlapping.
```

**What Makes This Challenging:**
- Intervals can be in any order
- Need to detect when intervals overlap
- Must handle adjacent intervals (touching but not overlapping)
- Edge cases: single interval, all overlapping, none overlapping

## 5. Brute Force Approach

**Naive Strategy:**
Compare every interval with every other interval to find overlaps, then recursively merge until no more merging is possible.

```python
def merge_intervals_brute_force(intervals):
    """
    Brute force: Keep finding and merging overlapping pairs until no more merges possible.

    Time Complexity: O(n^3) - worst case, we might need n iterations of O(n^2) comparisons
    Space Complexity: O(n) - storing the result
    """
    if not intervals:
        return []

    # Keep merging until no changes occur
    changed = True
    result = intervals[:]

    while changed:
        changed = False
        new_result = []
        merged = [False] * len(result)

        # Compare each pair of intervals
        for i in range(len(result)):
            if merged[i]:
                continue

            current = result[i]
            found_merge = False

            # Try to merge with any other interval
            for j in range(i + 1, len(result)):
                if merged[j]:
                    continue

                other = result[j]

                # Check if they overlap
                if current[0] <= other[1] and other[0] <= current[1]:
                    # Merge them
                    merged_interval = [
                        min(current[0], other[0]),
                        max(current[1], other[1])
                    ]
                    new_result.append(merged_interval)
                    merged[i] = merged[j] = True
                    found_merge = True
                    changed = True
                    break

            if not found_merge and not merged[i]:
                new_result.append(current)
                merged[i] = True

        result = new_result

    return result

# Test
intervals = [[1,3],[2,6],[8,10],[15,18]]
print(merge_intervals_brute_force(intervals))  # [[1,6],[8,10],[15,18]]
```

**Problems with Brute Force:**
- Very slow: O(n³) time complexity
- Multiple passes needed
- Complicated logic with nested loops
- Hard to reason about correctness

## 6. Optimized Solution: Sort + Linear Merge

**Key Insight:**
If we **sort intervals by start time**, we only need to check if the current interval overlaps with the previous one we're building. This turns an O(n²) comparison problem into an O(n) linear scan after O(n log n) sorting.

```python
def merge_intervals(intervals):
    """
    Optimal approach: Sort intervals by start time, then merge in one pass.

    Algorithm:
    1. Sort intervals by start time
    2. Iterate through sorted intervals
    3. If current overlaps with last merged interval, extend the end time
    4. Otherwise, add current interval as new merged interval

    Time Complexity: O(n log n) - dominated by sorting
    Space Complexity: O(n) - for output array (or O(log n) if counting sort space)
    """
    if not intervals:
        return []

    # Step 1: Sort by start time
    # This ensures we process intervals in chronological order
    intervals.sort(key=lambda x: x[0])

    # Step 2: Initialize result with first interval
    merged = [intervals[0]]

    # Step 3: Iterate through remaining intervals
    for current in intervals[1:]:
        # Get the last interval we've added to result
        last_merged = merged[-1]

        # Check if current interval overlaps with last merged interval
        # Overlap condition: current starts before or when last merged ends
        if current[0] <= last_merged[1]:
            # Overlapping - extend the end time of last merged interval
            # Take the maximum of both end times
            last_merged[1] = max(last_merged[1], current[1])
        else:
            # No overlap - add current interval as new merged interval
            merged.append(current)

    return merged


def merge_intervals_detailed(intervals):
    """
    Same algorithm with detailed comments showing the merge process.
    """
    if not intervals:
        return []

    # Sort: [[1,3],[2,6],[8,10],[15,18]] stays sorted by start
    intervals.sort(key=lambda x: x[0])

    result = []
    current_start, current_end = intervals[0]

    for i in range(1, len(intervals)):
        next_start, next_end = intervals[i]

        # Does next interval start before current ends?
        if next_start <= current_end:
            # Yes - they overlap, extend current_end if needed
            # Example: [1,3] + [2,6] → [1,6]
            current_end = max(current_end, next_end)
        else:
            # No - gap between intervals, save current and start new
            # Example: after [1,6], we see [8,10] → save [1,6], start [8,10]
            result.append([current_start, current_end])
            current_start, current_end = next_start, next_end

    # Don't forget the last interval
    result.append([current_start, current_end])

    return result


# Alternative: Using a class for clarity
class Solution:
    def merge(self, intervals: list[list[int]]) -> list[list[int]]:
        """
        Clean implementation suitable for interviews.
        """
        if not intervals:
            return []

        intervals.sort(key=lambda x: x[0])
        merged = [intervals[0]]

        for current in intervals[1:]:
            if current[0] <= merged[-1][1]:
                # Overlap: merge by extending end time
                merged[-1][1] = max(merged[-1][1], current[1])
            else:
                # No overlap: add as new interval
                merged.append(current)

        return merged


# Test cases
test_cases = [
    [[1,3],[2,6],[8,10],[15,18]],  # Expected: [[1,6],[8,10],[15,18]]
    [[1,4],[4,5]],                  # Expected: [[1,5]]
    [[1,4],[0,4]],                  # Expected: [[0,4]]
    [[1,4],[2,3]],                  # Expected: [[1,4]] (one contains other)
    [[1,4],[0,0]],                  # Expected: [[0,0],[1,4]]
]

for test in test_cases:
    print(f"Input: {test}")
    print(f"Output: {merge_intervals(test)}")
    print()
```

**Why This Works:**
1. **Sorting**: After sorting by start time, we know that if interval B comes after interval A, B.start >= A.start
2. **Linear Scan**: We only need to check if current.start <= previous.end to detect overlap
3. **Greedy Merging**: We extend the end time greedily, knowing no future interval can extend earlier intervals (due to sorting)

## 7. Time & Space Complexity Analysis

### Brute Force Approach
- **Time Complexity**: O(n³)
  - Outer while loop: O(n) iterations in worst case
  - Inner nested loops: O(n²) per iteration
  - Total: O(n³)
- **Space Complexity**: O(n)
  - Storing the result array

### Optimized Sort + Merge Approach
- **Time Complexity**: O(n log n)
  - Sorting: O(n log n)
  - Single pass merge: O(n)
  - Total: O(n log n) - dominated by sorting
- **Space Complexity**:
  - O(n) for output array (this is required)
  - O(log n) or O(n) for sorting depending on implementation (Python's Timsort uses O(n))
  - If we don't count output: O(log n) to O(n) for sorting

### Comparison
| Approach | Time | Space | Readability | Interview Suitability |
|----------|------|-------|-------------|----------------------|
| Brute Force | O(n³) | O(n) | Complex | Poor - too slow |
| Sort + Merge | O(n log n) | O(n) | Excellent | Perfect ✓ |

**Key Takeaway**: Sorting is your friend! It reduces O(n²) comparisons to O(n) linear scan, making the O(n log n) sort cost worthwhile.

## 8. Variations

### 8.1 Insert Interval (LeetCode 57)

Insert a new interval into a sorted list of non-overlapping intervals and merge if necessary.

```python
def insert_interval(intervals, new_interval):
    """
    Insert and merge a new interval into sorted non-overlapping intervals.

    Algorithm:
    1. Add all intervals that end before new interval starts
    2. Merge all intervals that overlap with new interval
    3. Add all intervals that start after new interval ends

    Time: O(n), Space: O(n)
    """
    result = []
    i = 0
    n = len(intervals)

    # Step 1: Add all intervals that come before new interval (no overlap)
    while i < n and intervals[i][1] < new_interval[0]:
        result.append(intervals[i])
        i += 1

    # Step 2: Merge all overlapping intervals with new interval
    while i < n and intervals[i][0] <= new_interval[1]:
        # Extend new_interval to cover the overlapping interval
        new_interval[0] = min(new_interval[0], intervals[i][0])
        new_interval[1] = max(new_interval[1], intervals[i][1])
        i += 1

    # Add the merged interval
    result.append(new_interval)

    # Step 3: Add all remaining intervals (after new interval)
    while i < n:
        result.append(intervals[i])
        i += 1

    return result


# Test
intervals = [[1,3],[6,9]]
new_interval = [2,5]
print(insert_interval(intervals, new_interval))  # [[1,5],[6,9]]

intervals = [[1,2],[3,5],[6,7],[8,10],[12,16]]
new_interval = [4,8]
print(insert_interval(intervals, new_interval))  # [[1,2],[3,10],[12,16]]
```

### 8.2 Meeting Rooms II (LeetCode 253) - Minimum Meeting Rooms

Find the minimum number of meeting rooms required.

```python
import heapq

def min_meeting_rooms(intervals):
    """
    Find minimum meeting rooms needed (max concurrent meetings).

    Approach 1: Min Heap
    - Sort by start time
    - Use heap to track end times of ongoing meetings
    - When new meeting starts, remove all meetings that have ended
    - Heap size = rooms needed at that time

    Time: O(n log n), Space: O(n)
    """
    if not intervals:
        return 0

    # Sort by start time
    intervals.sort(key=lambda x: x[0])

    # Min heap to track end times of meetings
    heap = []

    for start, end in intervals:
        # Remove all meetings that ended before this one starts
        if heap and heap[0] <= start:
            heapq.heappop(heap)

        # Add current meeting's end time
        heapq.heappush(heap, end)

    # Heap size = max concurrent meetings = rooms needed
    return len(heap)


def min_meeting_rooms_sweep_line(intervals):
    """
    Approach 2: Sweep Line Algorithm
    - Create events for each start (+1) and end (-1)
    - Sort all events by time
    - Track running count of active meetings

    Time: O(n log n), Space: O(n)
    """
    events = []

    # Create events: (time, type)
    # Use type=1 for start, type=-1 for end
    # If start and end at same time, process end first (type=-1 < type=1)
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))

    # Sort by time, then by type (ends before starts at same time)
    events.sort()

    max_rooms = 0
    current_rooms = 0

    for time, event_type in events:
        current_rooms += event_type
        max_rooms = max(max_rooms, current_rooms)

    return max_rooms


# Test
intervals = [[0,30],[5,10],[15,20]]
print(min_meeting_rooms(intervals))  # 2
print(min_meeting_rooms_sweep_line(intervals))  # 2

intervals = [[7,10],[2,4]]
print(min_meeting_rooms(intervals))  # 1
```

### 8.3 Non-Overlapping Intervals (LeetCode 435)

Find minimum number of intervals to remove to make rest non-overlapping.

```python
def erase_overlap_intervals(intervals):
    """
    Remove minimum intervals to make rest non-overlapping.

    Greedy Strategy:
    - Sort by END time (key insight!)
    - Always keep interval that ends earliest
    - This leaves maximum room for future intervals

    Time: O(n log n), Space: O(1)
    """
    if not intervals:
        return 0

    # Sort by end time
    intervals.sort(key=lambda x: x[1])

    removed = 0
    prev_end = intervals[0][1]

    for i in range(1, len(intervals)):
        # If current starts before previous ended, they overlap
        if intervals[i][0] < prev_end:
            # Remove current interval (count it)
            removed += 1
            # Keep the one with earlier end (already in prev_end due to sorting)
        else:
            # No overlap, update prev_end
            prev_end = intervals[i][1]

    return removed


# Test
intervals = [[1,2],[2,3],[3,4],[1,3]]
print(erase_overlap_intervals(intervals))  # 1 (remove [1,3])

intervals = [[1,2],[1,2],[1,2]]
print(erase_overlap_intervals(intervals))  # 2 (remove 2 of them)
```

### 8.4 Interval List Intersections (LeetCode 986)

Find intersection of two lists of intervals.

```python
def interval_intersection(first_list, second_list):
    """
    Find all intersections between two interval lists.

    Two Pointer Approach:
    - Use pointer for each list
    - Find intersection of current intervals from both lists
    - Move pointer of interval that ends first

    Time: O(n + m), Space: O(1) excluding output
    """
    result = []
    i = j = 0

    while i < len(first_list) and j < len(second_list):
        # Find intersection
        start = max(first_list[i][0], second_list[j][0])
        end = min(first_list[i][1], second_list[j][1])

        # If valid intersection (start <= end), add it
        if start <= end:
            result.append([start, end])

        # Move pointer of interval that ends first
        if first_list[i][1] < second_list[j][1]:
            i += 1
        else:
            j += 1

    return result


# Test
first = [[0,2],[5,10],[13,23],[24,25]]
second = [[1,5],[8,12],[15,24],[25,26]]
print(interval_intersection(first, second))
# [[1,2],[5,5],[8,10],[15,23],[24,24],[25,25]]
```

### 8.5 Employee Free Time (LeetCode 759)

Find common free time for all employees given their schedules.

```python
def employee_free_time(schedule):
    """
    Find gaps in merged schedule of all employees.

    Algorithm:
    1. Flatten all intervals into one list
    2. Merge all intervals (find busy times)
    3. Find gaps between merged intervals (free times)

    Time: O(n log n), Space: O(n)
    """
    # Flatten all employee schedules
    all_intervals = []
    for employee_schedule in schedule:
        all_intervals.extend(employee_schedule)

    # Sort by start time
    all_intervals.sort(key=lambda x: x[0])

    # Merge intervals to find busy times
    merged = [all_intervals[0]]
    for current in all_intervals[1:]:
        if current[0] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], current[1])
        else:
            merged.append(current)

    # Find gaps between merged intervals
    free_time = []
    for i in range(1, len(merged)):
        # Gap between end of previous and start of current
        free_time.append([merged[i-1][1], merged[i][0]])

    return free_time


# Test
schedule = [[[1,3],[4,6]], [[2,4]], [[2,5],[9,12]]]
print(employee_free_time(schedule))  # [[6,9]]
```

## 9. Pro Tips for Senior Engineers

### 9.1 Sweep Line Algorithm

A powerful technique for interval problems, especially when dealing with multiple overlapping events.

**Concept**: Treat interval start and end as separate events. Process all events in order, maintaining a running state.

```python
def max_concurrent_events(intervals):
    """
    Sweep line: Find maximum number of concurrent intervals.

    Create events for each start/end, sort by time, track active count.
    """
    events = []

    for start, end in intervals:
        events.append((start, 'start'))
        events.append((end, 'end'))

    # Sort by time; if same time, process 'end' before 'start'
    events.sort(key=lambda x: (x[0], x[1] == 'start'))

    max_concurrent = 0
    active = 0

    for time, event_type in events:
        if event_type == 'start':
            active += 1
            max_concurrent = max(max_concurrent, active)
        else:
            active -= 1

    return max_concurrent
```

**When to Use Sweep Line:**
- Need to track state changes over time
- Multiple overlapping intervals with different properties
- Range query problems
- Event-driven simulations

### 9.2 Edge Cases to Always Consider

```python
def test_edge_cases():
    """
    Critical edge cases for interval problems.
    """
    # 1. Empty input
    assert merge_intervals([]) == []

    # 2. Single interval
    assert merge_intervals([[1,4]]) == [[1,4]]

    # 3. Adjacent intervals (touching but not overlapping)
    # Note: [1,4] and [4,5] are often considered overlapping
    assert merge_intervals([[1,4],[4,5]]) == [[1,5]]

    # 4. One interval contains another
    assert merge_intervals([[1,10],[2,5]]) == [[1,10]]

    # 5. All intervals overlap into one
    assert merge_intervals([[1,4],[2,5],[3,6]]) == [[1,6]]

    # 6. No overlaps
    assert merge_intervals([[1,2],[3,4],[5,6]]) == [[1,2],[3,4],[5,6]]

    # 7. Intervals in reverse order
    assert merge_intervals([[3,4],[1,2]]) == [[1,2],[3,4]]

    # 8. Negative numbers
    assert merge_intervals([[-2,0],[0,2]]) == [[-2,2]]

    # 9. Same start, different ends
    assert merge_intervals([[1,5],[1,3]]) == [[1,5]]

    # 10. Zero-length intervals
    assert merge_intervals([[1,1],[2,2]]) == [[1,1],[2,2]]

    print("All edge cases passed!")

test_edge_cases()
```

### 9.3 Optimization Tricks

```python
# 1. Early termination for insert interval
def insert_optimized(intervals, new_interval):
    """Use binary search to find insertion point."""
    import bisect

    if not intervals:
        return [new_interval]

    # Binary search for where to start merging
    start_idx = bisect.bisect_left(intervals, new_interval[0], key=lambda x: x[1])
    end_idx = bisect.bisect_right(intervals, new_interval[1], key=lambda x: x[0])

    # ... rest of merge logic


# 2. In-place modification (if allowed)
def merge_in_place(intervals):
    """
    Modify input array to save space.
    Only do this if problem allows it!
    """
    intervals.sort(key=lambda x: x[0])
    write_idx = 0

    for i in range(1, len(intervals)):
        if intervals[i][0] <= intervals[write_idx][1]:
            intervals[write_idx][1] = max(intervals[write_idx][1], intervals[i][1])
        else:
            write_idx += 1
            intervals[write_idx] = intervals[i]

    return intervals[:write_idx + 1]


# 3. Using tuple instead of list for immutability
def merge_tuples(intervals):
    """
    Use tuples for intervals - immutable and hashable.
    Useful when you need to store intervals in sets/dicts.
    """
    if not intervals:
        return []

    intervals = sorted(intervals)
    merged = [intervals[0]]

    for current in intervals[1:]:
        if current[0] <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], current[1]))
        else:
            merged.append(current)

    return merged
```

### 9.4 Common Patterns Summary

| Problem Type | Approach | Time | Key Insight |
|--------------|----------|------|-------------|
| Merge overlapping | Sort + greedy | O(n log n) | Sort by start |
| Find gaps | Merge then iterate | O(n log n) | Gaps = between merged intervals |
| Max concurrent | Heap or sweep line | O(n log n) | Track active intervals |
| Min removals | Sort by end, greedy | O(n log n) | Keep earliest ending |
| Intersections | Two pointers | O(n + m) | Advance pointer of earlier ending |
| Insert interval | Three-part scan | O(n) | Before, merge, after |

## 10. Problem Recognition

### When You See These Keywords:

✅ **Definite Interval Problem:**
- "merge overlapping intervals"
- "meeting rooms" / "conference rooms"
- "booking system"
- "schedule" / "calendar"
- "time ranges" / "time slots"
- "insert interval"
- "overlapping ranges"

✅ **Likely Interval Problem:**
- "ranges" with start/end
- "non-overlapping"
- "minimum intervals to remove"
- "maximum concurrent"
- "free time" / "available slots"
- "coverage" of ranges
- "interval list intersection"

### Quick Recognition Checklist:

1. ❓ Does input consist of pairs [start, end]?
2. ❓ Do I need to find overlaps between ranges?
3. ❓ Am I merging, combining, or splitting ranges?
4. ❓ Is this about scheduling or resource allocation?
5. ❓ Do I need to find gaps between ranges?

If you answered **YES to 2+ questions** → It's likely an interval problem!

### Not an Interval Problem (Common Confusion):

❌ Array problems with range queries (use prefix sum instead)
❌ Substring problems (use sliding window instead)
❌ Finding subarray with properties (use sliding window or two pointers)

## 11. Practice Problems

### Beginner Level:
1. **Merge Intervals** (LeetCode 56) - The classic
2. **Meeting Rooms** (LeetCode 252) - Check if person can attend all meetings
3. **Insert Interval** (LeetCode 57) - Insert and merge

### Intermediate Level:
4. **Meeting Rooms II** (LeetCode 253) - Minimum rooms needed
5. **Non-Overlapping Intervals** (LeetCode 435) - Minimum removals
6. **Interval List Intersections** (LeetCode 986) - Find intersections

### Advanced Level:
7. **Employee Free Time** (LeetCode 759) - Find common free time
8. **My Calendar I/II/III** (LeetCode 729/731/732) - Booking system with constraints
9. **Minimum Number of Arrows to Burst Balloons** (LeetCode 452) - Greedy intervals
10. **The Skyline Problem** (LeetCode 218) - Sweep line with priority queue

### Problem Solving Order:
Start with problems 1-3 to build foundation, then move to 4-6 for different techniques, finally tackle 7-10 for advanced patterns.

## 12. Common Mistakes

### Mistake 1: Forgetting to Sort
```python
# ❌ WRONG: Not sorting first
def merge_wrong(intervals):
    merged = [intervals[0]]
    for current in intervals[1:]:
        if current[0] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], current[1])
        else:
            merged.append(current)
    return merged

# Input: [[2,6],[1,3],[8,10]]
# Wrong output: [[2,6],[8,10]] - misses [1,3]!

# ✅ CORRECT: Always sort first
def merge_correct(intervals):
    intervals.sort(key=lambda x: x[0])  # Critical step!
    # ... rest of logic
```

### Mistake 2: Wrong Overlap Condition
```python
# ❌ WRONG: Using < instead of <=
if current[0] < merged[-1][1]:  # Misses adjacent intervals!
    # [[1,4],[4,5]] won't merge → [[1,4],[4,5]] (wrong)

# ✅ CORRECT: Use <= for adjacent intervals
if current[0] <= merged[-1][1]:  # Handles [[1,4],[4,5]] → [[1,5]]
```

### Mistake 3: Not Updating End Correctly
```python
# ❌ WRONG: Not taking max
merged[-1][1] = current[1]
# [[1,10],[2,5]] → [[1,5]] (wrong! Lost coverage)

# ✅ CORRECT: Take max of both ends
merged[-1][1] = max(merged[-1][1], current[1])
# [[1,10],[2,5]] → [[1,10]] (correct!)
```

### Mistake 4: Off-by-One in Sweep Line
```python
# ❌ WRONG: Not handling events at same time correctly
events.append((start, 1))
events.append((end, 1))  # Should be -1!
events.sort()  # End events should process before start events at same time

# ✅ CORRECT: Proper event types and sorting
events.append((start, 1))
events.append((end, -1))
events.sort(key=lambda x: (x[0], x[1]))  # Sort by time, then type
```

### Mistake 5: Modifying While Iterating
```python
# ❌ WRONG: Modifying list you're iterating over
for interval in intervals:
    if should_remove(interval):
        intervals.remove(interval)  # Skips elements!

# ✅ CORRECT: Build new list or iterate backwards
result = [interval for interval in intervals if not should_remove(interval)]
```

### Mistake 6: Ignoring Edge Cases
```python
def merge_incomplete(intervals):
    # ❌ WRONG: No validation
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]  # Crashes if intervals is empty!
    # ...

# ✅ CORRECT: Handle edge cases
def merge_complete(intervals):
    if not intervals:  # Check for empty
        return []
    if len(intervals) == 1:  # Single interval
        return intervals
    # ... rest of logic
```

### Mistake 7: Using Wrong Sort Key
```python
# ❌ WRONG: Sorting by end time for merge problem
intervals.sort(key=lambda x: x[1])
# Doesn't guarantee sequential processing!

# ✅ CORRECT: Sort by start time for merge
intervals.sort(key=lambda x: x[0])

# NOTE: Sort by end time IS correct for min removal problems!
def erase_overlaps(intervals):
    intervals.sort(key=lambda x: x[1])  # Correct for this problem!
```

### Mistake 8: Integer Overflow (in some languages)
```python
# ⚠️ CAREFUL: In languages like Java/C++
# int maxEnd = Integer.MAX_VALUE;
# if (start <= maxEnd) { ... }  # May overflow!

# In Python, integers don't overflow, but be aware in other languages
# Use float('inf') or proper bounds checking
```

### Mistake 9: Not Handling Unsorted Second List
```python
# For interval intersection problems:
# ❌ WRONG: Assuming both lists are sorted
def intersect_wrong(A, B):
    # Only sorts A, forgets B might be unsorted
    A.sort(key=lambda x: x[0])
    # ...

# ✅ CORRECT: Usually both lists are given sorted, but verify!
# If not, sort both or use different algorithm
```

### Mistake 10: Overthinking Complexity
```python
# ❌ WRONG: Trying to be too clever
def merge_overcomplicated(intervals):
    # Using complex data structures unnecessarily
    tree = SegmentTree()  # Overkill for merge intervals!
    # ...

# ✅ CORRECT: Keep it simple
def merge_simple(intervals):
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for current in intervals[1:]:
        if current[0] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], current[1])
        else:
            merged.append(current)
    return merged
```

---

## Summary Cheat Sheet

**The Interval Pattern in 4 Steps:**
1. **Sort** by start time (usually)
2. **Iterate** through sorted intervals
3. **Compare** current with last processed
4. **Merge** or **separate** based on overlap

**Key Techniques:**
- Sort + Linear Scan: O(n log n)
- Heap for concurrent tracking: O(n log n)
- Sweep Line for events: O(n log n)
- Two Pointers for intersections: O(n + m)

**Remember:**
- ✅ Always sort first (unless already sorted)
- ✅ Use `<=` for overlap check (includes adjacent)
- ✅ Take `max` when updating end time
- ✅ Handle empty and single-element cases
- ✅ Choose sort key based on problem type

Happy coding! 🚀
