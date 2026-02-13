# Heap / Priority Queue Pattern

## What is a Heap?

### Explain Like I'm 5
Imagine you have a magical box that always knows which toy is the biggest (or smallest). Every time you put a new toy in, the box rearranges itself so that you can INSTANTLY grab the biggest (or smallest) toy without looking through all of them. That's what a heap does with numbers!

### Technical Definition
A **heap** is a specialized tree-based data structure that satisfies the heap property:
- **Max-Heap**: The parent node is always greater than or equal to its children (largest element at the root)
- **Min-Heap**: The parent node is always less than or equal to its children (smallest element at the root)

A heap is typically implemented as a complete binary tree stored in an array, where for any element at index `i`:
- Left child is at index `2*i + 1`
- Right child is at index `2*i + 2`
- Parent is at index `(i-1) // 2`

## Real-World Analogy

### Emergency Room Triage
Think of a hospital emergency room:
- Patients arrive at different times
- They're NOT treated first-come-first-served
- Instead, they're prioritized by severity (critical > urgent > stable)
- The doctor always sees the MOST CRITICAL patient next
- When a new patient arrives, they're inserted into the queue based on their priority

This is exactly how a **min-heap priority queue** works (assuming lower severity numbers = more critical). The heap ensures the highest priority item is always accessible in O(1) time.

### Other Examples
- **Task Manager**: CPU scheduler prioritizing processes
- **Dijkstra's Algorithm**: Always exploring the nearest unvisited node
- **Event-Driven Simulation**: Processing events in chronological order
- **Email Inbox**: Starred/important emails at the top

## When to Use a Heap

### Clear Signals
Use a heap when you see these keywords or patterns:

1. **"Top K" or "K largest/smallest"** - Find K largest/smallest elements
2. **"Kth largest/smallest"** - Find the Kth element in order
3. **"Median" or "running median"** - Track middle value in a stream
4. **"Merge K sorted"** - Merge multiple sorted lists/arrays
5. **"Closest K points"** - K nearest neighbors
6. **"Continuous stream"** - Process data as it arrives
7. **"Priority"** - Items need processing in priority order
8. **"Scheduling"** - Tasks with different priorities/deadlines

### The Pattern
If you need to repeatedly:
- Find the minimum or maximum element
- Remove the minimum or maximum element
- Add new elements dynamically

Then a heap is likely the right choice!

## The Problem: Kth Largest Element in an Array

**Problem**: Given an unsorted array, find the kth largest element.

**Example**:
```
Input: nums = [3, 2, 1, 5, 6, 4], k = 2
Output: 5
Explanation: The 2nd largest element is 5 (sorted: [1,2,3,4,5,6])
```

## Brute Force Approach

### Solution: Sort the Array
The simplest approach is to sort the array and return the kth element from the end.

```python
def findKthLargest_bruteforce(nums, k):
    """
    Find kth largest element by sorting

    Approach:
    1. Sort the array in descending order
    2. Return the element at index k-1
    """
    # Sort in descending order: [6, 5, 4, 3, 2, 1]
    nums.sort(reverse=True)

    # k=1 means largest (index 0)
    # k=2 means 2nd largest (index 1)
    return nums[k - 1]

# Example
nums = [3, 2, 1, 5, 6, 4]
k = 2
print(findKthLargest_bruteforce(nums, k))  # Output: 5
```

### Time & Space Complexity (Brute Force)
- **Time**: O(n log n) - sorting dominates
- **Space**: O(1) or O(n) depending on sorting algorithm

### Problems with Brute Force
1. We don't need the ENTIRE array sorted, just the kth largest
2. Wastes time sorting elements we don't care about
3. Not efficient for large datasets or streaming data

## Optimized Solution: Min-Heap

### The Insight
Instead of sorting everything, maintain a min-heap of size K containing the K largest elements seen so far. The root of this heap will be the Kth largest!

**Why Min-Heap (not Max-Heap)?**
- We want the SMALLEST of the K largest elements at the root
- This makes it easy to know when to evict an element (if new element > root, it deserves to be in top K)

### Visualization
```
Finding 2nd largest in [3, 2, 1, 5, 6, 4] with k=2

Step 1: Add 3
Heap: [3]

Step 2: Add 2
Heap: [2, 3]  (min-heap, so 2 is at root)

Step 3: Add 1
1 < 2 (root), not in top 2, skip
Heap: [2, 3]

Step 4: Add 5
5 > 2 (root), remove 2, add 5
Heap: [3, 5]

Step 5: Add 6
6 > 3 (root), remove 3, add 6
Heap: [5, 6]

Step 6: Add 4
4 < 5 (root), not in top 2, skip
Heap: [5, 6]

Result: Root of heap = 5 (the 2nd largest)
```

### Code Implementation

```python
import heapq

def findKthLargest(nums, k):
    """
    Find kth largest element using a min-heap

    Approach:
    1. Maintain a min-heap of size k
    2. The heap contains the k largest elements seen so far
    3. The root (minimum) of this heap is the kth largest

    Time: O(n log k)
    Space: O(k)
    """
    # Create a min-heap to store k largest elements
    min_heap = []

    for num in nums:
        # Add current number to heap
        heapq.heappush(min_heap, num)

        # If heap size exceeds k, remove the smallest
        # This ensures we only keep the k largest elements
        if len(min_heap) > k:
            heapq.heappop(min_heap)

    # The root of the heap is the kth largest element
    # (it's the smallest among the k largest)
    return min_heap[0]


# Alternative: Using heapify (slightly different approach)
def findKthLargest_v2(nums, k):
    """
    Alternative: Create max-heap and pop k-1 times

    Python's heapq is a min-heap, so we negate values
    to simulate a max-heap
    """
    # Negate all values to simulate max-heap
    max_heap = [-num for num in nums]
    heapq.heapify(max_heap)

    # Pop k-1 largest elements
    for _ in range(k - 1):
        heapq.heappop(max_heap)

    # The next element is the kth largest
    return -heapq.heappop(max_heap)


# Example usage
nums = [3, 2, 1, 5, 6, 4]
k = 2
print(findKthLargest(nums, k))     # Output: 5
print(findKthLargest_v2(nums, k))  # Output: 5
```

### Step-by-Step Walkthrough

```python
# Let's trace findKthLargest([3, 2, 1, 5, 6, 4], k=2)

# Initial state
min_heap = []
k = 2

# Process 3
heapq.heappush(min_heap, 3)  # min_heap = [3]
# Size = 1, not > k, keep it

# Process 2
heapq.heappush(min_heap, 2)  # min_heap = [2, 3]
# Size = 2, not > k, keep it

# Process 1
heapq.heappush(min_heap, 1)  # min_heap = [1, 3, 2]
# Size = 3 > k, pop smallest
heapq.heappop(min_heap)      # min_heap = [2, 3]

# Process 5
heapq.heappush(min_heap, 5)  # min_heap = [2, 3, 5]
# Size = 3 > k, pop smallest
heapq.heappop(min_heap)      # min_heap = [3, 5]

# Process 6
heapq.heappush(min_heap, 6)  # min_heap = [3, 5, 6]
# Size = 3 > k, pop smallest
heapq.heappop(min_heap)      # min_heap = [5, 6]

# Process 4
heapq.heappush(min_heap, 4)  # min_heap = [4, 6, 5]
# Size = 3 > k, pop smallest
heapq.heappop(min_heap)      # min_heap = [5, 6]

# Return the root (minimum of k largest)
return min_heap[0]  # Returns 5
```

## Time & Space Complexity Analysis

### Comparison Table

| Approach | Time Complexity | Space Complexity | Best For |
|----------|----------------|------------------|----------|
| **Brute Force (Sort)** | O(n log n) | O(1) - O(n) | Small arrays, when you need all elements sorted |
| **Min-Heap (Size K)** | O(n log k) | O(k) | Large arrays, small k, streaming data |
| **Max-Heap (Pop K times)** | O(n + k log n) | O(n) | When k is close to n |
| **QuickSelect** | O(n) average | O(1) | Best average case, but worst case O(n²) |

### Why Min-Heap Wins
- When k << n (k is much smaller than n), O(n log k) beats O(n log n)
- Example: Finding top 10 elements in 1 million items
  - Sort: 1M * log(1M) ≈ 20M operations
  - Heap: 1M * log(10) ≈ 3.3M operations
  - **6x faster!**

### Detailed Complexity Breakdown

**Min-Heap Approach (Size K)**:
- **Time**: O(n log k)
  - We process n elements
  - Each heap operation (push/pop) takes O(log k)
  - Total: n * log k
- **Space**: O(k)
  - We only store k elements in the heap

**Max-Heap Approach**:
- **Time**: O(n + k log n)
  - Heapify: O(n)
  - Pop k times: k * log n
  - Total: O(n + k log n)
- **Space**: O(n)
  - We store all n elements

## Variations

### 1. Min-Heap vs Max-Heap

```python
import heapq

# MIN-HEAP (default in Python)
min_heap = []
heapq.heappush(min_heap, 5)
heapq.heappush(min_heap, 2)
heapq.heappush(min_heap, 8)
print(min_heap[0])  # 2 (smallest at root)

# MAX-HEAP (negate values to simulate)
max_heap = []
heapq.heappush(max_heap, -5)
heapq.heappush(max_heap, -2)
heapq.heappush(max_heap, -8)
print(-max_heap[0])  # 8 (largest at root)

# Or use list comprehension
values = [5, 2, 8, 1, 9]
max_heap = [-x for x in values]
heapq.heapify(max_heap)
largest = -max_heap[0]  # 9
```

### 2. Two Heaps (Finding Median)

**Problem**: Find median in a data stream

**Approach**: Use two heaps!
- **Max-heap** (left): Stores smaller half
- **Min-heap** (right): Stores larger half
- Median is either the root of the larger heap, or average of both roots

```python
import heapq

class MedianFinder:
    """
    Find median in a data stream using two heaps

    Invariants:
    1. Max-heap (left) contains smaller half
    2. Min-heap (right) contains larger half
    3. len(left) == len(right) OR len(left) == len(right) + 1
    """

    def __init__(self):
        # Max-heap for smaller half (negate values)
        self.left = []
        # Min-heap for larger half
        self.right = []

    def addNum(self, num):
        """Add a number to the data structure"""
        # Always add to left (max-heap) first
        heapq.heappush(self.left, -num)

        # Balance: move largest from left to right
        # This ensures all elements in left <= all elements in right
        heapq.heappush(self.right, -heapq.heappop(self.left))

        # If right becomes larger, move smallest back to left
        if len(self.right) > len(self.left):
            heapq.heappush(self.left, -heapq.heappop(self.right))

    def findMedian(self):
        """Return the median of all elements"""
        if len(self.left) > len(self.right):
            # Odd number of elements, median is root of left
            return -self.left[0]
        else:
            # Even number, median is average of both roots
            return (-self.left[0] + self.right[0]) / 2.0


# Example usage
mf = MedianFinder()
mf.addNum(1)    # [1], median = 1
print(mf.findMedian())  # 1

mf.addNum(2)    # [1, 2], median = 1.5
print(mf.findMedian())  # 1.5

mf.addNum(3)    # [1, 2, 3], median = 2
print(mf.findMedian())  # 2
```

### 3. Heap as Priority Queue

```python
import heapq

class Task:
    def __init__(self, priority, description):
        self.priority = priority
        self.description = description

    # Define comparison for heap (lower priority = higher importance)
    def __lt__(self, other):
        return self.priority < other.priority

    def __repr__(self):
        return f"Task(priority={self.priority}, desc='{self.description}')"


# Create priority queue
pq = []

# Add tasks with priorities
heapq.heappush(pq, Task(3, "Write email"))
heapq.heappush(pq, Task(1, "Fix critical bug"))
heapq.heappush(pq, Task(2, "Review PR"))

# Process tasks in priority order
while pq:
    task = heapq.heappop(pq)
    print(f"Processing: {task}")

# Output:
# Processing: Task(priority=1, desc='Fix critical bug')
# Processing: Task(priority=2, desc='Review PR')
# Processing: Task(priority=3, desc='Write email')
```

### 4. Merge K Sorted Lists

```python
import heapq
from typing import List, Optional

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def mergeKLists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge K sorted linked lists using a min-heap

    Approach:
    1. Add first node of each list to heap
    2. Pop smallest, add to result
    3. Add next node from that list to heap
    4. Repeat until heap is empty

    Time: O(N log k) where N = total nodes, k = number of lists
    Space: O(k) for the heap
    """
    # Min-heap: (value, list_index, node)
    # We need list_index to know which list to advance
    min_heap = []

    # Add first node of each list to heap
    for i, head in enumerate(lists):
        if head:
            heapq.heappush(min_heap, (head.val, i, head))

    # Dummy node to build result
    dummy = ListNode(0)
    current = dummy

    while min_heap:
        # Get smallest node
        val, list_idx, node = heapq.heappop(min_heap)

        # Add to result
        current.next = node
        current = current.next

        # Add next node from same list to heap
        if node.next:
            heapq.heappush(min_heap, (node.next.val, list_idx, node.next))

    return dummy.next
```

## Pro Tips for Senior Engineers

### 1. When to Use Heap vs Sorting

**Use Heap When**:
- You only need top K elements (K << N)
- Data arrives in a stream (can't sort upfront)
- You need to repeatedly access min/max
- You're implementing a priority queue

**Use Sorting When**:
- You need all elements sorted
- K is close to N
- You need random access to sorted elements
- The data is static (not streaming)

### 2. Python heapq Tricks

```python
import heapq

# 1. heapify is O(n), not O(n log n)!
arr = [3, 1, 4, 1, 5, 9, 2, 6]
heapq.heapify(arr)  # O(n) - faster than n pushes

# 2. nlargest and nsmallest for quick queries
numbers = [10, 2, 5, 8, 3, 9, 1]
top_3 = heapq.nlargest(3, numbers)    # [10, 9, 8]
bottom_3 = heapq.nsmallest(3, numbers)  # [1, 2, 3]

# 3. Custom comparison with tuples (automatic)
heap = []
heapq.heappush(heap, (1, "high priority"))
heapq.heappush(heap, (5, "low priority"))
heapq.heappush(heap, (1, "also high"))  # Breaks tie with string

# 4. heapreplace: pop and push in one operation
heapq.heapreplace(heap, (2, "medium"))  # Atomic pop + push

# 5. Using with custom objects (define __lt__)
class Item:
    def __init__(self, value):
        self.value = value
    def __lt__(self, other):
        return self.value < other.value
```

### 3. Common Pitfalls

```python
# WRONG: Accessing heap as sorted array
heap = [1, 3, 2, 5, 4]
heapq.heapify(heap)
print(heap[1])  # Don't assume heap[1] is 2nd smallest!
# Heap property only guarantees parent < children

# RIGHT: Always pop to get elements in order
result = []
while heap:
    result.append(heapq.heappop(heap))
# Now result is [1, 2, 3, 4, 5]

# WRONG: Modifying heap directly
heap[0] = 100  # Breaks heap property!

# RIGHT: Pop and push
old_min = heapq.heappop(heap)
heapq.heappush(heap, 100)
```

### 4. Space Optimization

```python
# Problem: Find kth largest in 1 billion numbers
# Don't do this: O(n) space
def kth_largest_bad(nums, k):
    max_heap = [-x for x in nums]  # Creates new array!
    heapq.heapify(max_heap)
    # ...

# Do this: O(k) space
def kth_largest_good(nums, k):
    min_heap = []
    for num in nums:
        heapq.heappush(min_heap, num)
        if len(min_heap) > k:
            heapq.heappop(min_heap)
    return min_heap[0]
```

## Problem Recognition Keywords

When you see these words in a problem, think HEAP:

### Instant Heap Signals
- **"Top K"** → Min-heap of size K
- **"Kth largest/smallest"** → Min-heap of size K
- **"Median"** → Two heaps
- **"Merge K sorted"** → Min-heap
- **"Priority"** → Priority queue (heap)
- **"Closest K points"** → Min-heap with distance

### Context Clues
- **"Stream" or "continuous"** → Can't sort upfront, use heap
- **"At any time"** → Need dynamic structure, use heap
- **"Frequent queries"** → Heap maintains order efficiently
- **"Scheduling"** → Tasks with priorities = heap
- **"Optimization" problems** → Dijkstra, A* use heaps

### Examples in the Wild
```
"Find the K closest points to origin" → Heap
"Running median of data stream" → Two heaps
"Task scheduler with priorities" → Priority queue
"Merge K sorted arrays" → Min-heap
"Kth largest element in array" → Min-heap size K
"Top K frequent elements" → Heap with frequencies
```

## Practice Problems

### Easy
1. **Kth Largest Element in an Array** (LeetCode 215)
   - Classic heap problem
   - Practice: Both min-heap and max-heap approaches

2. **Last Stone Weight** (LeetCode 1046)
   - Simulate smashing stones (always pick 2 heaviest)
   - Use max-heap

3. **Relative Ranks** (LeetCode 506)
   - Assign ranks based on scores
   - Practice with heap + hashmap

### Medium
4. **Top K Frequent Elements** (LeetCode 347)
   - Count frequencies, then heap
   - Practice: Min-heap of size K with custom comparator

5. **Kth Largest Element in a Stream** (LeetCode 703)
   - Maintain min-heap of size K
   - Add elements one at a time

6. **K Closest Points to Origin** (LeetCode 973)
   - Calculate distances, maintain heap
   - Practice: Custom comparison with tuples

7. **Find Median from Data Stream** (LeetCode 295)
   - Classic two-heap problem
   - Must master this for interviews!

### Hard
8. **Merge K Sorted Lists** (LeetCode 23)
   - Use heap to track smallest head from each list
   - Time: O(N log K)

9. **Sliding Window Median** (LeetCode 480)
   - Combine two heaps + sliding window
   - Very challenging!

10. **IPO** (LeetCode 502)
    - Maximize capital with project selection
    - Two heaps: available projects + selected projects

## Common Mistakes

### 1. Min-Heap vs Max-Heap Confusion

```python
# WRONG: Using max-heap for "K largest"
def kth_largest_wrong(nums, k):
    max_heap = [-x for x in nums]
    heapq.heapify(max_heap)
    for _ in range(k):
        result = -heapq.heappop(max_heap)
    return result
# Time: O(n + k log n) - inefficient!

# RIGHT: Use min-heap of size K
def kth_largest_right(nums, k):
    min_heap = []
    for num in nums:
        heapq.heappush(min_heap, num)
        if len(min_heap) > k:
            heapq.heappop(min_heap)
    return min_heap[0]
# Time: O(n log k) - much better!
```

**Rule**: For "K largest", use min-heap. For "K smallest", use max-heap (negated).

### 2. Not Maintaining Heap Property

```python
# WRONG: Directly modifying heap
heap = [1, 3, 2, 5]
heapq.heapify(heap)
heap[0] = 10  # Breaks heap property!

# RIGHT: Use heap operations
heapq.heappop(heap)
heapq.heappush(heap, 10)
```

### 3. Assuming Heap is Sorted

```python
heap = [5, 2, 8, 1, 9, 3]
heapq.heapify(heap)
# heap might be [1, 2, 3, 5, 9, 8]
# Don't assume heap[1] is the 2nd smallest!

# Only heap[0] is guaranteed to be the minimum
# To get elements in order, must pop repeatedly
```

### 4. Off-by-One Errors with K

```python
# Find 3rd largest in [1, 2, 3, 4, 5]
k = 3

# WRONG
result = nums[-k]  # This gives 3, not 3rd largest (which is 3)
# Wait, this works! But only if sorted...

# WRONG: In unsorted array
nums = [5, 2, 4, 1, 3]
result = nums[-k]  # Gives 4, but 3rd largest is 3!

# RIGHT: Use heap
min_heap = []
for num in nums:
    heapq.heappush(min_heap, num)
    if len(min_heap) > k:
        heapq.heappop(min_heap)
result = min_heap[0]  # Correct: 3
```

### 5. Forgetting to Negate for Max-Heap

```python
# WRONG: Python has no max-heap, this doesn't work
import heapq
max_heap = heapq.MaxHeap()  # No such thing!

# RIGHT: Negate values
max_heap = []
for num in [1, 5, 3]:
    heapq.heappush(max_heap, -num)

# Get max
max_val = -heapq.heappop(max_heap)  # Remember to negate back!
```

### 6. Using Heap When You Don't Need To

```python
# Problem: Find max in array
nums = [3, 1, 4, 1, 5]

# OVERKILL: Using heap
heap = nums.copy()
heapq.heapify(heap)
# Then convert to max-heap... too much work!

# SIMPLE: Just use max()
result = max(nums)  # O(n), simple and clear
```

**Remember**: Heaps are for when you need **repeated** access to min/max, or you're processing **streaming data**. For one-time queries, built-in functions are better.

## Summary Cheat Sheet

```
HEAP PATTERN DECISION TREE:

See "top K" or "Kth largest/smallest"?
├─ YES → Use min-heap of size K
└─ NO → Continue

See "median" or "running median"?
├─ YES → Use two heaps (max-heap left, min-heap right)
└─ NO → Continue

See "merge K sorted"?
├─ YES → Use min-heap with (value, list_index, node)
└─ NO → Continue

See "priority" or "scheduling"?
├─ YES → Use heap as priority queue
└─ NO → Probably don't need a heap

COMPLEXITY QUICK REFERENCE:
- Push/Pop: O(log n)
- Peek (access min/max): O(1)
- Heapify: O(n)
- Build heap of size k from n elements: O(n log k)

PYTHON HEAPQ ESSENTIALS:
- heapq is MIN-HEAP only
- Max-heap: negate values
- heapify() is O(n)
- nlargest(k, arr) / nsmallest(k, arr) for quick queries
- Tuples auto-compare lexicographically
```

---

**Final Thoughts**: Heaps are powerful when you need efficient access to the extreme elements (min/max) in a dynamic dataset. They shine in streaming scenarios and when K << N. However, don't over-engineer—if you just need to find the max once, `max()` is your friend. Master the two-heap median pattern and "top K with size-K min-heap" pattern, and you'll handle 90% of heap interview questions!
