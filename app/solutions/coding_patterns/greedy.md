# Greedy Algorithms Pattern Guide

## What is a Greedy Algorithm?

### Explain Like I'm 5
Imagine you're at a candy store with $5, and you want to buy as many candies as possible. A greedy approach means you always pick the cheapest candy available right now, over and over, until your money runs out. You don't plan ahead or think "maybe I should save money for a special combo later" - you just grab the best option you can see at each moment.

### Technical Definition
A **greedy algorithm** makes the locally optimal choice at each step with the hope of finding a global optimum. Instead of exploring all possible solutions (like dynamic programming), it makes a series of choices, each of which looks best at the moment, and never reconsiders those decisions.

**Key characteristics:**
- Makes decisions based on current information without looking ahead
- Once a choice is made, it's never reconsidered
- Builds a solution piece by piece
- Not always guaranteed to find the optimal solution (but when it does, it's very efficient)

## Real-World Analogy

### Making Change with Coins
Suppose you need to give someone $0.67 in change using US coins (quarters=25¢, dimes=10¢, nickels=5¢, pennies=1¢).

**Greedy Approach:**
1. Use as many quarters as possible: 2 quarters = 50¢ (17¢ remaining)
2. Use as many dimes as possible: 1 dime = 10¢ (7¢ remaining)
3. Use as many nickels as possible: 1 nickel = 5¢ (2¢ remaining)
4. Use pennies: 2 pennies = 2¢ (0¢ remaining)

**Result:** 6 coins total (2+1+1+2)

This greedy approach works for US coins because of their special denominations. However, if coins were [25¢, 10¢, 4¢, 1¢] and you needed 30¢, greedy would give you 6 coins (25+4+1), but optimal is 3 coins (10+10+10). This shows greedy doesn't always work!

## When to Use Greedy Algorithms

### Clear Signals That Greedy Might Work

1. **Greedy Choice Property**: A global optimum can be arrived at by making locally optimal choices
2. **Optimal Substructure**: An optimal solution contains optimal solutions to subproblems
3. **No need to reconsider**: Once you make a choice, you never need to backtrack
4. **Sorting helps**: Many greedy problems benefit from sorting the input first

### How to Prove Greedy Works

To prove a greedy algorithm is correct, you typically need to show:

1. **Exchange Argument**: Show that if there's an optimal solution different from the greedy choice, you can "exchange" parts to make it match the greedy choice without making it worse
2. **Induction**: Prove that the greedy choice at each step maintains the optimality
3. **"Staying Ahead"**: Show the greedy solution is always at least as good as any other solution at every step

### Problem Categories Where Greedy Often Works

- **Interval Scheduling** (meeting rooms, job scheduling)
- **Huffman Coding** (data compression)
- **Minimum Spanning Trees** (Kruskal's, Prim's algorithms)
- **Shortest Paths** (Dijkstra's algorithm for non-negative weights)
- **Activity Selection** (maximize non-overlapping activities)
- **Fractional Knapsack** (can take fractions of items)

## The Problem: Jump Game II

**LeetCode 45 - Jump Game II (Medium)**

Given an array of non-negative integers `nums`, you are initially positioned at the first index. Each element represents your maximum jump length at that position. Your goal is to reach the last index in the minimum number of jumps.

You can assume that you can always reach the last index.

```
Example 1:
Input: nums = [2,3,1,1,4]
Output: 2
Explanation: Jump 1 step from index 0 to 1, then 3 steps to the last index.

Example 2:
Input: nums = [2,3,0,1,4]
Output: 2
```

## Brute Force Approach: Dynamic Programming

The brute force approach uses Dynamic Programming to explore all possible jump sequences.

```python
def jump_dp(nums):
    """
    DP approach: Try all possible jumps from each position
    dp[i] = minimum jumps needed to reach index i

    Time: O(n²) - for each position, check all reachable positions
    Space: O(n) - dp array
    """
    n = len(nums)

    # dp[i] represents minimum jumps to reach index i
    dp = [float('inf')] * n
    dp[0] = 0  # Start at index 0, need 0 jumps

    # For each position
    for i in range(n):
        # Try all possible jump distances from position i
        for jump in range(1, nums[i] + 1):
            next_pos = i + jump

            # If we can reach a valid position
            if next_pos < n:
                # Update minimum jumps needed to reach next_pos
                dp[next_pos] = min(dp[next_pos], dp[i] + 1)

    return dp[n - 1]

# Example trace for [2,3,1,1,4]:
# i=0, nums[0]=2: can jump to indices 1,2
#   - dp[1] = min(inf, 0+1) = 1
#   - dp[2] = min(inf, 0+1) = 1
# i=1, nums[1]=3: can jump to indices 2,3,4
#   - dp[2] = min(1, 1+1) = 1 (no change)
#   - dp[3] = min(inf, 1+1) = 2
#   - dp[4] = min(inf, 1+1) = 2
# i=2, nums[2]=1: can jump to index 3
#   - dp[3] = min(2, 1+1) = 2 (no change)
# Result: dp[4] = 2
```

**Why this works but is slow:**
- We calculate minimum jumps for every position
- For each position, we try every possible jump distance
- Lots of redundant work checking the same positions multiple times

## Optimized Solution: Greedy Approach

The key insight: **We don't need to find the exact sequence of jumps - we just need to count how many "jump zones" we pass through**.

Think of it as levels in a game:
- Level 0: Starting position
- Level 1: All positions reachable in 1 jump
- Level 2: All positions reachable in 2 jumps
- ...

We greedily extend our reach as far as possible at each level.

```python
def jump_greedy(nums):
    """
    Greedy approach: Think of it as BFS levels
    Track the farthest we can reach with current number of jumps

    Time: O(n) - single pass through array
    Space: O(1) - only a few variables
    """
    n = len(nums)

    # If only one element, we're already at the end
    if n == 1:
        return 0

    jumps = 0           # Number of jumps made so far
    current_end = 0     # Farthest index we can reach with current jumps
    farthest = 0        # Farthest index we can reach overall

    # We don't need to process the last index (we stop when we reach it)
    for i in range(n - 1):
        # Update the farthest position we can reach from current position
        farthest = max(farthest, i + nums[i])

        # If we've reached the end of current jump range
        if i == current_end:
            # We must make another jump
            jumps += 1
            # Update the end of next jump range to the farthest we can reach
            current_end = farthest

            # Early exit: if we can already reach the end
            if current_end >= n - 1:
                break

    return jumps


# Detailed trace for [2,3,1,1,4]:
"""
Initial: jumps=0, current_end=0, farthest=0

i=0: nums[0]=2
  - farthest = max(0, 0+2) = 2
  - i == current_end (0==0), so make a jump!
    - jumps = 1
    - current_end = 2 (can reach indices 1,2 with 1 jump)
  State: jumps=1, current_end=2, farthest=2

i=1: nums[1]=3
  - farthest = max(2, 1+3) = 4
  - i != current_end (1!=2), so continue exploring
  State: jumps=1, current_end=2, farthest=4

i=2: nums[2]=1
  - farthest = max(4, 2+1) = 4 (no change)
  - i == current_end (2==2), so make a jump!
    - jumps = 2
    - current_end = 4 (can reach index 4 with 2 jumps)
    - current_end >= n-1 (4>=4), break early
  State: jumps=2, current_end=4, farthest=4

Result: 2 jumps
"""
```

### Why This Greedy Approach Works

1. **Greedy Choice**: At each jump, we go as far as possible within the current range. We don't need to pick the exact index to jump to - we just track the farthest reachable position.

2. **Optimal Substructure**: If we can reach position X in k jumps optimally, and from positions 0 to X we can reach Y, then Y is reachable in at most k+1 jumps.

3. **Proof of Correctness**:
   - We process positions in order (left to right)
   - At any point, `farthest` represents the maximum reach with one more jump
   - When we reach `current_end`, we've explored all positions reachable with current jumps
   - We must make another jump to explore further positions
   - Since we've maximized our reach at each step, we use minimum jumps

## Time & Space Complexity Analysis

| Approach | Time Complexity | Space Complexity | Explanation |
|----------|----------------|------------------|-------------|
| **Dynamic Programming** | O(n²) | O(n) | For each of n positions, we might check up to n positions; need dp array |
| **Greedy** | O(n) | O(1) | Single pass through array; only use constant extra space |

**Performance Comparison:**
- For `n = 10,000`:
  - DP: ~100 million operations
  - Greedy: ~10,000 operations
  - **Greedy is 10,000x faster!**

## Variations and Common Greedy Patterns

### 1. Interval Scheduling (Meeting Rooms II)

**Problem:** Given meeting time intervals, find minimum number of conference rooms required.

```python
def min_meeting_rooms(intervals):
    """
    Greedy: Process events chronologically
    When a meeting starts, need a room; when it ends, free a room

    Time: O(n log n) - sorting
    Space: O(n) - storing events
    """
    events = []

    # Create separate events for start and end times
    for start, end in intervals:
        events.append((start, 1))    # 1 means meeting starts
        events.append((end, -1))      # -1 means meeting ends

    # Sort by time; if same time, process ends before starts
    events.sort(key=lambda x: (x[0], x[1]))

    rooms_needed = 0
    max_rooms = 0

    for time, event_type in events:
        rooms_needed += event_type
        max_rooms = max(max_rooms, rooms_needed)

    return max_rooms

# Example: [(0,30), (5,10), (15,20)]
# Events: [(0,1), (5,1), (10,-1), (15,1), (20,-1), (30,-1)]
# Process:
#   (0,1):   rooms=1, max=1
#   (5,1):   rooms=2, max=2  <- need 2 rooms
#   (10,-1): rooms=1, max=2
#   (15,1):  rooms=2, max=2
#   (20,-1): rooms=1, max=2
#   (30,-1): rooms=0, max=2
# Result: 2 rooms needed
```

### 2. Kadane's Algorithm (Maximum Subarray)

**Problem:** Find the contiguous subarray with the largest sum.

```python
def max_subarray(nums):
    """
    Greedy: At each position, decide whether to extend current subarray
    or start fresh from current position

    Greedy choice: Keep current subarray only if it's helping (sum > 0)

    Time: O(n)
    Space: O(1)
    """
    max_sum = nums[0]      # Best sum seen so far
    current_sum = 0        # Sum of current subarray

    for num in nums:
        # Greedy choice: start fresh if previous sum hurts us
        current_sum = max(num, current_sum + num)

        # Update global maximum
        max_sum = max(max_sum, current_sum)

    return max_sum

# Alternative implementation (more explicit):
def max_subarray_explicit(nums):
    max_sum = nums[0]
    current_sum = 0

    for num in nums:
        # If current sum is negative, it's hurting us - drop it
        if current_sum < 0:
            current_sum = 0

        current_sum += num
        max_sum = max(max_sum, current_sum)

    return max_sum

# Example: [-2,1,-3,4,-1,2,1,-5,4]
# i=0: num=-2, current=0-2=-2, max=-2
# i=1: num=1,  current=-2+1=-1 vs 1 -> choose 1, max=1
# i=2: num=-3, current=1-3=-2, max=1
# i=3: num=4,  current=-2+4=2 vs 4 -> choose 4, max=4
# i=4: num=-1, current=4-1=3, max=4
# i=5: num=2,  current=3+2=5, max=5
# i=6: num=1,  current=5+1=6, max=6  <- best subarray [4,-1,2,1]
# i=7: num=-5, current=6-5=1, max=6
# i=8: num=4,  current=1+4=5, max=6
```

### 3. Gas Station (Circular Array)

**Problem:** Find starting gas station to complete circular route.

```python
def can_complete_circuit(gas, cost):
    """
    Greedy insights:
    1. If total gas >= total cost, solution exists
    2. If we can't reach station j from station i, then we can't reach j
       from any station between i and j either
    3. So if we fail at position j starting from i, next try starts at j+1

    Time: O(n)
    Space: O(1)
    """
    n = len(gas)
    total_tank = 0      # Track if solution is possible at all
    current_tank = 0    # Track current journey
    start = 0           # Starting position

    for i in range(n):
        total_tank += gas[i] - cost[i]
        current_tank += gas[i] - cost[i]

        # If we can't reach next station from current start
        if current_tank < 0:
            # Start must be after current position
            start = i + 1
            current_tank = 0  # Reset for new journey

    # If total gas >= total cost, solution exists at 'start'
    return start if total_tank >= 0 else -1

# Example: gas=[1,2,3,4,5], cost=[3,4,5,1,2]
# i=0: total=-2, current=-2, current<0 -> start=1, reset
# i=1: total=-4, current=-2, current<0 -> start=2, reset
# i=2: total=-6, current=-2, current<0 -> start=3, reset
# i=3: total=-3, current=3, continue
# i=4: total=0, current=6, continue
# total_tank=0 >= 0, so return start=3
```

### 4. Merge Intervals

**Problem:** Merge all overlapping intervals.

```python
def merge_intervals(intervals):
    """
    Greedy: Sort by start time, then merge when intervals overlap

    Time: O(n log n) - sorting dominates
    Space: O(n) - output array
    """
    if not intervals:
        return []

    # Sort by start time
    intervals.sort(key=lambda x: x[0])

    merged = [intervals[0]]

    for current in intervals[1:]:
        last_merged = merged[-1]

        # If current overlaps with last merged interval
        if current[0] <= last_merged[1]:
            # Extend the last merged interval
            last_merged[1] = max(last_merged[1], current[1])
        else:
            # No overlap, add as new interval
            merged.append(current)

    return merged

# Example: [[1,3],[2,6],[8,10],[15,18]]
# After sort: [[1,3],[2,6],[8,10],[15,18]] (already sorted)
#
# merged = [[1,3]]
#
# Process [2,6]:
#   2 <= 3 (overlaps), extend to [1, max(3,6)] = [1,6]
#   merged = [[1,6]]
#
# Process [8,10]:
#   8 > 6 (no overlap), add new
#   merged = [[1,6], [8,10]]
#
# Process [15,18]:
#   15 > 10 (no overlap), add new
#   merged = [[1,6], [8,10], [15,18]]
```

### 5. Partition Labels

**Problem:** Partition string so each letter appears in at most one part.

```python
def partition_labels(s):
    """
    Greedy: Track last occurrence of each character
    Extend current partition until we've seen all characters' last occurrence

    Time: O(n)
    Space: O(1) - only 26 letters
    """
    # Store last index of each character
    last_occurrence = {char: i for i, char in enumerate(s)}

    partitions = []
    start = 0
    end = 0

    for i, char in enumerate(s):
        # Extend partition to include last occurrence of current char
        end = max(end, last_occurrence[char])

        # If we've reached the end of current partition
        if i == end:
            partitions.append(end - start + 1)
            start = i + 1

    return partitions

# Example: "ababcbacadefegdehijhklij"
# last_occurrence = {'a':8, 'b':5, 'c':7, 'd':14, 'e':15, ...}
#
# i=0, char='a': end=max(0,8)=8
# i=1, char='b': end=max(8,5)=8
# ...
# i=8, char='a': end=max(8,8)=8, i==end -> partition size = 9
#
# i=9, char='d': end=max(9,14)=14
# ...
# i=15, char='e': end=max(15,15)=15, i==end -> partition size = 7
#
# Result: [9, 7, 8]
```

## Pro Tips for Senior Engineers

### 1. Proving Greedy Correctness

Before implementing a greedy solution, prove it works using one of these methods:

**Exchange Argument Template:**
```
1. Assume there exists an optimal solution OPT different from greedy solution G
2. Find the first position where OPT differs from G
3. Show you can "exchange" OPT's choice with G's choice
4. Prove the exchanged solution is still optimal
5. Repeat until OPT = G, contradicting that they're different
6. Therefore, G must be optimal
```

**Example - Activity Selection:**
- Problem: Select maximum non-overlapping activities
- Greedy: Always pick activity that ends earliest
- Proof: If optimal solution picks activity that ends later than greedy's first choice, we can exchange it with greedy's choice and still have room for at least as many activities

### 2. When Greedy Fails - Red Flags

Greedy algorithms FAIL when:

```python
# Red Flag 1: Future information affects current choice
# Example: Coin change with coins [1, 5, 6, 9]
# Target: 11
# Greedy: 9+1+1 = 3 coins
# Optimal: 5+6 = 2 coins
# Greedy fails because choosing 9 now doesn't consider future combinations

# Red Flag 2: Dependencies between choices
# Example: 0/1 Knapsack (can't take fractions)
# Items: [(value=60, weight=10), (value=100, weight=20), (value=120, weight=30)]
# Capacity: 50
# Greedy by value/weight ratio: 60/10=6, 100/20=5, 120/30=4
# Takes items 1&2: value=160
# Optimal: Take items 2&3: value=220
# Greedy fails because items can't be broken into pieces

# Red Flag 3: Need to explore multiple paths
# Example: Matrix path sum with obstacles
# Greedy might take a locally good path that leads to dead end
```

### 3. Edge Cases to Consider

Always test these edge cases:

```python
# Empty input
assert jump([]) == 0  # or handle appropriately

# Single element
assert jump([0]) == 0

# All same values
assert jump([2,2,2,2,2]) == ?

# Maximum values
assert jump([10000] * 10000) == 1  # Can jump to end immediately

# Minimum values (if applicable)
assert jump([1,1,1,1,1]) == 4  # Must jump one at a time

# Already at goal
assert jump([0]) == 0
```

### 4. Debugging Greedy Algorithms

When your greedy solution gives wrong answers:

```python
def debug_greedy(nums):
    """Add extensive logging to understand greedy choices"""
    jumps = 0
    current_end = 0
    farthest = 0
    path = [0]  # Track the jump sequence

    for i in range(len(nums) - 1):
        old_farthest = farthest
        farthest = max(farthest, i + nums[i])

        if farthest != old_farthest:
            print(f"At index {i}, can now reach {farthest}")

        if i == current_end:
            jumps += 1
            current_end = farthest
            path.append(current_end)
            print(f"Jump #{jumps}: moved to {current_end}")

    print(f"Path taken: {path}")
    return jumps
```

### 5. Optimization Tricks

```python
# Trick 1: Sort first (most greedy algorithms benefit)
intervals.sort(key=lambda x: x[0])  # Sort by start time
intervals.sort(key=lambda x: x[1])  # Or by end time

# Trick 2: Use heap for dynamic greedy choices
import heapq
heap = []
heapq.heappush(heap, item)  # Automatically maintains min-heap
smallest = heapq.heappop(heap)

# Trick 3: Two-pass when needed
# Pass 1: Compute auxiliary information
last_occurrence = {char: i for i, char in enumerate(s)}
# Pass 2: Make greedy choices based on Pass 1

# Trick 4: Event-based processing
events = [(time, event_type) for ...]
events.sort()  # Process events chronologically
```

## Problem Recognition: Greedy vs Dynamic Programming

### Use GREEDY when:

1. **Local optimal = Global optimal**: Making the best choice at each step leads to best overall solution
2. **Can't undo choices**: Once decision is made, never need to reconsider
3. **Sorting helps**: Problem becomes easier after sorting
4. **Pattern matching**: Problem resembles known greedy patterns (intervals, scheduling, etc.)

**Example indicators:**
- "Minimum number of..."
- "Maximum number of non-overlapping..."
- "Earliest deadline first..."
- "Largest/smallest first..."

### Use DYNAMIC PROGRAMMING when:

1. **Overlapping subproblems**: Same subproblem computed multiple times
2. **Need to try all options**: Can't determine best choice without exploring alternatives
3. **Optimal substructure**: Optimal solution contains optimal subsolutions
4. **Greedy counterexample exists**: Can show greedy fails

**Example indicators:**
- "Maximum/minimum among all possible..."
- "How many ways to..."
- "Is it possible to..."
- "Best strategy considering all options..."

### Quick Decision Tree

```
Question: Can you sort and make local choices?
├─ Yes → Try GREEDY
│   └─ Can you prove it works?
│       ├─ Yes → Use GREEDY
│       └─ No → Try DP
└─ No → Likely DP
    └─ Are there overlapping subproblems?
        ├─ Yes → Use DP
        └─ No → Might be backtracking or DFS
```

## Practice Problems

### Easy
1. **Best Time to Buy and Sell Stock II** (LeetCode 122)
   - Greedy: Buy and sell whenever price increases next day
   - Time: O(n), Space: O(1)

2. **Assign Cookies** (LeetCode 455)
   - Greedy: Sort both arrays, assign smallest cookie that satisfies each child
   - Time: O(n log n), Space: O(1)

### Medium
3. **Jump Game** (LeetCode 55)
   - Greedy: Track farthest reachable position
   - Time: O(n), Space: O(1)

4. **Jump Game II** (LeetCode 45)
   - Greedy: Count jump "levels" (covered above)
   - Time: O(n), Space: O(1)

5. **Gas Station** (LeetCode 134)
   - Greedy: If total gas ≥ total cost, find starting point
   - Time: O(n), Space: O(1)

6. **Partition Labels** (LeetCode 763)
   - Greedy: Track last occurrence of each character
   - Time: O(n), Space: O(1)

### Hard
7. **Candy** (LeetCode 135)
   - Greedy: Two passes - left to right, then right to left
   - Time: O(n), Space: O(n)

8. **Meeting Rooms II** (LeetCode 253)
   - Greedy: Event-based processing or min-heap
   - Time: O(n log n), Space: O(n)

9. **Minimum Number of Arrows to Burst Balloons** (LeetCode 452)
   - Greedy: Sort by end position, shoot at end of balloon
   - Time: O(n log n), Space: O(1)

## Common Mistakes

### Mistake 1: Assuming Greedy Always Works

```python
# WRONG: Assuming greedy works without proof
def coin_change_wrong(coins, amount):
    """This fails for coins=[1,5,6,9], amount=11"""
    coins.sort(reverse=True)  # Largest first
    count = 0

    for coin in coins:
        while amount >= coin:
            amount -= coin
            count += 1

    return count if amount == 0 else -1

# Example failure:
# coins=[1,5,6,9], amount=11
# Greedy: 9+1+1 = 3 coins
# Optimal: 5+6 = 2 coins (needs DP!)
```

**Lesson:** Always test greedy with counterexamples or provide proof.

### Mistake 2: Wrong Sorting Criteria

```python
# WRONG: Sorting by start time for activity selection
def max_activities_wrong(activities):
    """Should sort by END time, not start time"""
    activities.sort(key=lambda x: x[0])  # Sorting by start - WRONG!
    # This can miss optimal solution

# Example failure:
# Activities: [(1,10), (2,3), (4,5)]
# Sort by start: [(1,10), (2,3), (4,5)]
# Greedy picks (1,10), can't pick others: 1 activity
# Optimal: (2,3) and (4,5): 2 activities

# CORRECT: Sort by end time
def max_activities_correct(activities):
    activities.sort(key=lambda x: x[1])  # Sort by END time
    # Pick first activity, then pick next that starts after current ends
```

### Mistake 3: Not Considering Edge Cases

```python
# WRONG: Not handling edge cases
def jump_wrong(nums):
    if not nums:  # Missing check!
        return 0

    jumps = 0
    current_end = 0
    farthest = 0

    # BUG: Should be range(len(nums) - 1), not range(len(nums))
    for i in range(len(nums)):  # Will fail on last index
        farthest = max(farthest, i + nums[i])

        if i == current_end:
            jumps += 1
            current_end = farthest

    return jumps

# Fails on nums=[0] because it makes unnecessary jump
```

### Mistake 4: Incorrect Greedy Choice

```python
# WRONG: Greedy choice that seems logical but isn't optimal
def job_scheduling_wrong(jobs):
    """
    Jobs have (start, end, profit)
    WRONG: Pick job with highest profit first
    """
    jobs.sort(key=lambda x: x[2], reverse=True)  # Sort by profit
    # This doesn't account for time conflicts properly

# CORRECT: Need DP to consider all non-overlapping combinations
# Or greedy by end time with careful selection
```

### Mistake 5: Forgetting to Update State

```python
# WRONG: Not updating all necessary variables
def merge_intervals_wrong(intervals):
    intervals.sort()
    merged = [intervals[0]]

    for current in intervals[1:]:
        last = merged[-1]

        if current[0] <= last[1]:
            # BUG: Directly modifying tuple/list reference incorrectly
            last[1] = current[1]  # Might not update correctly
            # CORRECT: merged[-1] = [last[0], max(last[1], current[1])]
        else:
            merged.append(current)

    return merged
```

### Mistake 6: Off-by-One Errors

```python
# WRONG: Loop bounds causing off-by-one errors
def jump_off_by_one(nums):
    jumps = 0
    current_end = 0
    farthest = 0

    # BUG: Should be range(len(nums) - 1)
    # Processing last index causes unnecessary jump
    for i in range(len(nums)):
        farthest = max(farthest, i + nums[i])

        if i == current_end:
            jumps += 1
            current_end = farthest

    return jumps

# For nums=[2,3,1], this returns 2 instead of 1
```

## Summary

Greedy algorithms are powerful when they work, offering optimal solutions with excellent time complexity. The key is:

1. **Recognize** when greedy might apply (interval problems, scheduling, making change with standard coins)
2. **Prove** or verify that greedy works for your specific problem
3. **Identify** the greedy choice (what makes a choice "locally optimal"?)
4. **Sort** the input if it helps make greedy choices clearer
5. **Test** edge cases and counterexamples thoroughly

Remember: **Greedy is fast but not always correct. DP is slower but more reliable for optimization problems.** When in doubt, try to find a counterexample to greedy - if you can't, greedy might work!
