# Greedy Algorithms — Complete Interview Guide

## When to Use This Pattern

A greedy algorithm makes the locally optimal choice at each step, hoping that these local optima lead to a global optimum. Unlike DP, which considers all subproblems, greedy commits to one choice and never reconsiders.

**Signals that indicate greedy:**
1. The problem asks for a **single optimum** (maximum, minimum) or a **feasibility check** (can we reach the end?).
2. There is a natural **ordering** or **priority** that determines which choice to make next (sort by deadline, pick the largest, pick the smallest).
3. Making the locally best choice does not invalidate future choices — the **greedy choice property** holds.
4. The problem involves **intervals** (scheduling, merging, covering) or **sequences** where decisions are made left to right.
5. A DP solution exists but the DP table reveals that only one transition is ever taken (the greedy one), meaning the full table is unnecessary.
6. The problem has **optimal substructure** AND the greedy choice property (if only optimal substructure, you need DP).

**When NOT to use greedy:**
- When the locally optimal choice can lead to a globally suboptimal solution (e.g., coin change with arbitrary denominations, 0/1 knapsack).
- When you need to enumerate all solutions, not just the optimal one.
- When the problem requires considering future consequences of current decisions (use DP).

---

## Core Mechanics

### Why Does Greedy Work?

Greedy algorithms work when two conditions are met:

1. **Greedy Choice Property**: A globally optimal solution can be arrived at by making a locally optimal choice. In other words, you can safely commit to the best-looking option right now without worrying about future consequences.

2. **Optimal Substructure**: After making the greedy choice, the remaining subproblem has the same structure, and the optimal solution to the remaining subproblem combined with the greedy choice gives the optimal solution to the original problem.

### How to Prove a Greedy Algorithm Is Correct

The standard proof technique is the **exchange argument**:

1. Assume there is an optimal solution OPT that does not make the greedy choice at some step.
2. Show that you can "exchange" the non-greedy choice with the greedy choice without worsening the solution.
3. Repeat until OPT is transformed into the greedy solution, proving greedy is at least as good as OPT.

**Example — Activity Selection**: Greedy picks the activity that finishes earliest. Suppose OPT picks activity A that finishes later than the greedy choice G. Since G finishes no later than A, replacing A with G still leaves room for all remaining activities in OPT. So the greedy solution is no worse.

### Common Greedy Strategies

- **Sort and scan**: Sort by some criterion, then scan left to right making decisions.
- **Priority queue (heap)**: Always process the highest-priority item next.
- **Two pointers**: Move pointers based on local decisions.
- **Kadane's approach**: Maintain a running optimum, resetting when continuing is suboptimal.

---

## The Template

Greedy does not have a single template like backtracking does, because the "greedy choice" varies by problem. However, many greedy problems follow this structure:

```python
def greedy_solve(items):
    # Step 1: Sort by the greedy criterion
    items.sort(key=lambda x: x.some_property)

    # Step 2: Initialize state
    result = initial_value

    # Step 3: Iterate and make greedy choices
    for item in items:
        if item satisfies constraint:
            # Make the greedy choice (commit to this item)
            update result and state

    return result
```

```go
func greedySolve(items []Item) int {
    // Step 1: Sort by greedy criterion
    sort.Slice(items, func(i, j int) bool {
        return items[i].SomeProperty < items[j].SomeProperty
    })

    // Step 2: Initialize state
    result := initialValue

    // Step 3: Iterate and make greedy choices
    for _, item := range items {
        if satisfiesConstraint(item) {
            // Update result and state
        }
    }
    return result
}
```

### Interval Greedy Template

Many greedy problems involve intervals. The typical pattern:

```python
def interval_greedy(intervals):
    # Sort by end time (or start time, depending on the problem)
    intervals.sort(key=lambda x: x[1])

    count = 0
    prev_end = float('-inf')

    for start, end in intervals:
        if start >= prev_end:  # no overlap
            count += 1
            prev_end = end

    return count
```

---

## Problem Walkthroughs

### Problem: Maximum Subarray / Kadane's Algorithm (LC #53) — Medium
**Companies**: Google, Amazon, Meta, Microsoft, Uber — extremely common warm-up
**Why it's asked**: The simplest greedy/DP hybrid. Tests whether you understand when to extend vs. restart a running sum.

**Brute Force**:
```python
def max_subarray_brute(nums):
    """Check all subarrays."""
    n = len(nums)
    max_sum = float('-inf')
    for i in range(n):
        curr_sum = 0
        for j in range(i, n):
            curr_sum += nums[j]
            max_sum = max(max_sum, curr_sum)
    return max_sum
```
O(n^2) time.

**Key Insight**: At each position, the maximum subarray ending here is either: (1) the current element alone (start fresh), or (2) the current element plus the maximum subarray ending at the previous position (extend). If the running sum drops below the current element, it is better to start fresh. This is Kadane's algorithm.

**Optimal Solution**:
```python
def max_subarray(nums):
    max_sum = nums[0]
    current_sum = nums[0]

    for i in range(1, len(nums)):
        current_sum = max(nums[i], current_sum + nums[i])
        max_sum = max(max_sum, current_sum)

    return max_sum
```

**Dry Run** with `nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]`:
```
i=0: current=−2, max=−2
i=1: current=max(1, −2+1)=max(1,−1)=1, max=1
i=2: current=max(−3, 1−3)=max(−3,−2)=−2, max=1
i=3: current=max(4, −2+4)=max(4,2)=4, max=4
i=4: current=max(−1, 4−1)=3, max=4
i=5: current=max(2, 3+2)=5, max=5
i=6: current=max(1, 5+1)=6, max=6
i=7: current=max(−5, 6−5)=1, max=6
i=8: current=max(4, 1+4)=5, max=6
Answer: 6 (subarray [4,−1,2,1])
```

**Edge Cases**: All negative numbers (return the least negative), single element, all positive (return total sum).

**Complexity**: O(n) time, O(1) space.

**Follow-up questions**: "Return the actual subarray, not just the sum?" — track start and end indices. "What about maximum circular subarray?" — LC #918, also consider total_sum - min_subarray. "What about divide and conquer approach?" — O(n log n) using max crossing subarray at each split.

---

### Problem: Jump Game (LC #55) — Medium
**Companies**: Google, Amazon, Meta, Microsoft
**Why it's asked**: Tests greedy thinking with a reachability argument. Many candidates overcomplicate this with DP.

**Brute Force**:
```python
def can_jump_brute(nums):
    """DP: dp[i] = True if we can reach index i."""
    n = len(nums)
    dp = [False] * n
    dp[0] = True
    for i in range(1, n):
        for j in range(i):
            if dp[j] and j + nums[j] >= i:
                dp[i] = True
                break
    return dp[n - 1]
```
O(n^2) time.

**Key Insight**: Track the farthest index we can reach. Scan left to right: if the current index is within reach, update the farthest reachable index. If at any point the current index exceeds the farthest reach, we are stuck.

**Optimal Solution**:
```python
def can_jump(nums):
    farthest = 0
    for i in range(len(nums)):
        if i > farthest:
            return False  # cannot reach this index
        farthest = max(farthest, i + nums[i])
    return True
```

**Dry Run** with `nums = [2, 3, 1, 1, 4]`:
```
i=0: 0<=0, farthest=max(0, 0+2)=2
i=1: 1<=2, farthest=max(2, 1+3)=4
i=2: 2<=4, farthest=max(4, 2+1)=4
i=3: 3<=4, farthest=max(4, 3+1)=4
i=4: 4<=4, farthest=max(4, 4+4)=8
Answer: True (reached index 4)
```

With `nums = [3, 2, 1, 0, 4]`:
```
i=0: farthest=3
i=1: farthest=3
i=2: farthest=3
i=3: farthest=3  (0+3=3, stuck here)
i=4: 4>3 -> return False
```

**Edge Cases**: Single element (always True), first element is 0 and n > 1 (False), all zeros except last.

**Complexity**: O(n) time, O(1) space.

**Follow-up questions**: "What is the minimum number of jumps?" — Jump Game II (LC #45), greedy BFS approach. "What if you can jump backward too?" — this becomes BFS/graph problem.

---

### Problem: Task Scheduler (LC #621) — Medium
**Companies**: Meta, Google, Amazon, Microsoft, Uber
**Why it's asked**: Tests greedy with priority queue reasoning. The key insight involves understanding idle slots.

**Brute Force**:
```python
def least_interval_brute(tasks, n):
    """Simulate the CPU cycle by cycle."""
    from collections import Counter
    freq = Counter(tasks)
    time = 0
    while freq:
        # Pick up to n+1 most frequent tasks
        available = sorted(freq.keys(), key=lambda x: -freq[x])
        executed = []
        for i in range(n + 1):
            if i < len(available) and freq[available[i]] > 0:
                executed.append(available[i])
            time += 1
            if not any(freq[t] > 0 for t in freq):
                break
        for t in executed:
            freq[t] -= 1
            if freq[t] == 0:
                del freq[t]
    return time
```

**Key Insight**: The most frequent task determines the structure. If the most frequent task appears `f` times, it creates `f - 1` gaps of size `n` between its occurrences. The total intervals needed are at least `(f - 1) * (n + 1) + count_of_tasks_with_frequency_f`. But if there are enough different tasks to fill the gaps, the answer is just `len(tasks)` (no idle time needed). The answer is `max(len(tasks), (f - 1) * (n + 1) + count_max)`.

**Optimal Solution**:
```python
def least_interval(tasks, n):
    from collections import Counter
    freq = Counter(tasks)
    max_freq = max(freq.values())
    # Count how many tasks have the maximum frequency
    count_max = sum(1 for f in freq.values() if f == max_freq)

    # Formula: (max_freq - 1) gaps of size (n + 1), plus count_max for the last round
    result = (max_freq - 1) * (n + 1) + count_max

    # But if there are enough tasks to fill all gaps, answer is just total tasks
    return max(result, len(tasks))
```

**Dry Run** with `tasks = ["A","A","A","B","B","B"]`, `n = 2`:
```
freq = {A: 3, B: 3}
max_freq = 3
count_max = 2 (both A and B appear 3 times)

result = (3-1) * (2+1) + 2 = 2 * 3 + 2 = 8
len(tasks) = 6

Answer: max(8, 6) = 8
Schedule: A B _ A B _ A B  (8 intervals, but we can actually do A B idle A B idle A B)
```

With `tasks = ["A","A","A","B","B","B","C","C","D"]`, `n = 2`:
```
freq = {A:3, B:3, C:2, D:1}
max_freq = 3, count_max = 2

result = (3-1)*(2+1) + 2 = 8
len(tasks) = 9

Answer: max(8, 9) = 9
Schedule: A B C A B C A B D  (no idle needed, enough variety)
```

**Edge Cases**: n=0 (answer is always len(tasks)), single task type, all tasks different.

**Complexity**: O(n) time (where n is number of tasks), O(1) space (at most 26 different tasks).

**Follow-up questions**: "What if tasks have different durations?" — more complex scheduling problem, potentially need DP. "Return the actual schedule?" — use a heap simulation approach.

---

### Problem: Merge Intervals (LC #56) — Medium
**Companies**: Google, Meta, Amazon, Microsoft, Uber — extremely common
**Why it's asked**: Fundamental interval problem. Tests sorting + linear scan greedy. A building block for many harder problems.

**Brute Force**:
```python
def merge_brute(intervals):
    """Compare every pair of intervals, merge overlapping ones. Repeat."""
    # O(n^2) or worse, very messy to implement
    pass
```

**Key Insight**: Sort intervals by start time. Then scan left to right: if the current interval overlaps with the last merged interval (its start <= the end of the last merged), extend the last merged interval. Otherwise, start a new merged interval.

**Optimal Solution**:
```python
def merge(intervals):
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]

    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            # Overlapping: extend the end
            merged[-1][1] = max(merged[-1][1], end)
        else:
            # No overlap: start new interval
            merged.append([start, end])

    return merged
```

**Dry Run** with `intervals = [[1,3],[2,6],[8,10],[15,18]]`:
```
After sorting: [[1,3],[2,6],[8,10],[15,18]] (already sorted)
merged = [[1,3]]

[2,6]: 2 <= 3 (overlap) -> merged[-1] = [1, max(3,6)] = [1,6]
merged = [[1,6]]

[8,10]: 8 > 6 (no overlap) -> append
merged = [[1,6],[8,10]]

[15,18]: 15 > 10 (no overlap) -> append
merged = [[1,6],[8,10],[15,18]]

Answer: [[1,6],[8,10],[15,18]]
```

**Edge Cases**: Single interval, all overlapping (merge into one), no overlapping, intervals that touch at a point ([1,2],[2,3] merge to [1,3]).

**Complexity**: O(n log n) for sorting, O(n) for merging. Space O(n) for result.

**Follow-up questions**: "What if you need to insert a new interval?" — Insert Interval (LC #57). "What about finding free time slots?" — Employee Free Time (LC #759). "What if intervals arrive in a stream?" — maintain a sorted structure.

---

### Problem: Non-overlapping Intervals (LC #435) — Medium
**Companies**: Google, Amazon, Meta, Microsoft
**Why it's asked**: The classic activity selection / interval scheduling problem. Tests the exchange argument proof technique.

**Brute Force**:
```python
def erase_overlap_intervals_brute(intervals):
    """Try all subsets, find the largest non-overlapping set."""
    # O(2^n) — exponential
    pass
```

**Key Insight**: This is the interval scheduling maximization problem. Sort by end time. Greedily select intervals that do not overlap with the last selected one. The number of removed intervals = total - number of selected. Sorting by end time is optimal because choosing the earliest-finishing interval leaves the most room for future intervals (exchange argument).

**Optimal Solution**:
```python
def erase_overlap_intervals(intervals):
    intervals.sort(key=lambda x: x[1])  # sort by end time
    count = 0  # non-overlapping intervals selected
    prev_end = float('-inf')

    for start, end in intervals:
        if start >= prev_end:
            count += 1
            prev_end = end
        # else: this interval overlaps, skip it (remove it)

    return len(intervals) - count
```

**Dry Run** with `intervals = [[1,2],[2,3],[3,4],[1,3]]`:
```
After sorting by end: [[1,2],[2,3],[1,3],[3,4]]
prev_end = -inf, count = 0

[1,2]: 1 >= -inf -> select. count=1, prev_end=2
[2,3]: 2 >= 2 -> select. count=2, prev_end=3
[1,3]: 1 < 3 -> skip (overlaps)
[3,4]: 3 >= 3 -> select. count=3, prev_end=4

Removed = 4 - 3 = 1
Answer: 1 (remove [1,3])
```

**Edge Cases**: No overlapping intervals (0 removals), all overlapping (remove all but one), identical intervals.

**Complexity**: O(n log n) for sorting. O(1) extra space.

**Follow-up questions**: "What if you need to return which intervals to remove?" — track indices. "What if intervals have weights and you want max weight non-overlapping set?" — weighted interval scheduling, needs DP with binary search.

---

### Problem: Gas Station (LC #134) — Medium
**Companies**: Google, Amazon, Microsoft, Uber
**Why it's asked**: Tests a non-obvious greedy insight. The solution requires understanding that if total gas >= total cost, a solution exists, and the starting point can be found in a single pass.

**Brute Force**:
```python
def can_complete_circuit_brute(gas, cost):
    n = len(gas)
    for start in range(n):
        tank = 0
        can_complete = True
        for i in range(n):
            idx = (start + i) % n
            tank += gas[idx] - cost[idx]
            if tank < 0:
                can_complete = False
                break
        if can_complete:
            return start
    return -1
```
O(n^2) time.

**Key Insight**: Two observations: (1) If `sum(gas) >= sum(cost)`, a solution always exists (and is unique). (2) If starting from station `s` you run out of gas at station `t`, then no station between `s` and `t` can be a valid start either (because the tank was positive when passing through those stations, so starting from them with an empty tank would be even worse). This lets us find the answer in one pass: if the running tank drops below 0, reset the start to the next station.

**Optimal Solution**:
```python
def can_complete_circuit(gas, cost):
    if sum(gas) < sum(cost):
        return -1

    tank = 0
    start = 0

    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:
            start = i + 1  # reset start to next station
            tank = 0

    return start
```

**Dry Run** with `gas = [1,2,3,4,5]`, `cost = [3,4,5,1,2]`:
```
sum(gas)=15 >= sum(cost)=15, solution exists.

i=0: tank=1-3=-2 < 0 -> start=1, tank=0
i=1: tank=2-4=-2 < 0 -> start=2, tank=0
i=2: tank=3-5=-2 < 0 -> start=3, tank=0
i=3: tank=4-1=3
i=4: tank=3+5-2=6

Answer: start=3
Verify: start at 3, tank: 0+4-1=3, 3+5-2=6, 6+1-3=4, 4+2-4=2, 2+3-5=0. Yes!
```

**Edge Cases**: Single station (gas[0] >= cost[0]), all gas == cost (start at 0), impossible (return -1).

**Complexity**: O(n) time, O(1) space.

**Follow-up questions**: "Prove why this greedy works" — use the exchange argument: if the solution is station `k`, all prefix sums from `k` are non-negative. "What if there are multiple valid starts?" — the problem guarantees uniqueness.

---

### Problem: Candy (LC #135) — Hard
**Companies**: Google, Amazon, Microsoft, Meta
**Why it's asked**: Tests two-pass greedy. The insight is that constraints from left neighbors and right neighbors must be satisfied independently, then combined.

**Brute Force**:
```python
def candy_brute(ratings):
    """Start everyone at 1 candy, repeatedly fix violations until stable."""
    n = len(ratings)
    candies = [1] * n
    changed = True
    while changed:
        changed = False
        for i in range(n):
            if i > 0 and ratings[i] > ratings[i-1] and candies[i] <= candies[i-1]:
                candies[i] = candies[i-1] + 1
                changed = True
            if i < n-1 and ratings[i] > ratings[i+1] and candies[i] <= candies[i+1]:
                candies[i] = candies[i+1] + 1
                changed = True
    return sum(candies)
```
O(n^2) worst case.

**Key Insight**: The constraint is: a child with a higher rating than a neighbor must get more candy than that neighbor. Decompose into two independent constraints: (1) satisfy the left neighbor constraint with a left-to-right pass, (2) satisfy the right neighbor constraint with a right-to-left pass. The answer for each child is the maximum of both passes.

**Optimal Solution**:
```python
def candy(ratings):
    n = len(ratings)
    candies = [1] * n

    # Left to right: satisfy left-neighbor constraint
    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            candies[i] = candies[i - 1] + 1

    # Right to left: satisfy right-neighbor constraint
    for i in range(n - 2, -1, -1):
        if ratings[i] > ratings[i + 1]:
            candies[i] = max(candies[i], candies[i + 1] + 1)

    return sum(candies)
```

**Dry Run** with `ratings = [1, 0, 2]`:
```
Initial: candies = [1, 1, 1]

Left to right:
  i=1: ratings[1]=0 < ratings[0]=1 -> no change
  i=2: ratings[2]=2 > ratings[1]=0 -> candies[2] = candies[1]+1 = 2
  candies = [1, 1, 2]

Right to left:
  i=1: ratings[1]=0 < ratings[2]=2 -> no change
  i=0: ratings[0]=1 > ratings[1]=0 -> candies[0] = max(1, 1+1) = 2
  candies = [2, 1, 2]

Answer: 2+1+2 = 5
```

With `ratings = [1, 2, 2]`:
```
Left to right: candies = [1, 2, 1]  (ratings[2]==ratings[1], no increase)
Right to left: no changes needed
Answer: 1+2+1 = 4
```

**Edge Cases**: All same ratings (everyone gets 1), strictly increasing or decreasing, single child, V-shape and mountain patterns.

**Complexity**: O(n) time, O(n) space.

**Follow-up questions**: "Can you do it in O(1) space?" — yes, by counting slopes, but much more complex. "What if the constraint is >= instead of >?" — trivial change (use >= in comparisons).

---

### Problem: IPO (LC #502) — Hard
**Companies**: Google, Amazon, Microsoft
**Why it's asked**: Tests greedy with two heaps. You need to select projects that maximize capital, considering both profit and capital constraints.

**Brute Force**:
```python
def find_maximized_capital_brute(k, w, profits, capital):
    """Try all orderings of up to k projects."""
    # O(n^k) — combinatorial explosion
    n = len(profits)
    max_capital = w
    available = list(range(n))
    for _ in range(k):
        best = -1
        for i in available:
            if capital[i] <= max_capital:
                if best == -1 or profits[i] > profits[best]:
                    best = i
        if best == -1:
            break
        max_capital += profits[best]
        available.remove(best)
    return max_capital
```

**Key Insight**: At each step, among all projects we can afford (capital <= current wealth), we should pick the one with the highest profit. This is optimal because: (1) picking a high-profit project increases our capital the most, (2) all currently affordable projects will still be affordable later (we only gain capital), and (3) some currently unaffordable projects may become affordable with more capital. Use a min-heap sorted by capital to efficiently find affordable projects, and a max-heap sorted by profit to pick the best one.

**Optimal Solution**:
```python
import heapq

def find_maximized_capital(k, w, profits, capital):
    n = len(profits)
    # Min-heap of (capital_needed, profit) for projects not yet available
    projects = sorted(zip(capital, profits))
    idx = 0

    # Max-heap of profits for available projects (negate for max-heap)
    available = []

    for _ in range(k):
        # Move all newly affordable projects to the available heap
        while idx < n and projects[idx][0] <= w:
            heapq.heappush(available, -projects[idx][1])
            idx += 1

        if not available:
            break  # no affordable project

        # Pick the most profitable available project
        w += -heapq.heappop(available)

    return w
```

**Dry Run** with `k=2, w=0, profits=[1,2,3], capital=[0,1,1]`:
```
projects sorted by capital: [(0,1), (1,2), (1,3)]
idx=0, available=[]

Round 1: w=0
  projects[0]=(0,1): 0<=0, push profit 1 -> available=[-1]
  projects[1]=(1,2): 1>0, stop
  Pop -(-1)=1, w=0+1=1

Round 2: w=1
  projects[1]=(1,2): 1<=1, push profit 2 -> available=[-2]
  projects[2]=(1,3): 1<=1, push profit 3 -> available=[-3,-2]
  Pop -(-3)=3, w=1+3=4

Answer: 4
```

**Edge Cases**: k >= n (can do all projects), no affordable projects (return w), all projects have 0 profit.

**Complexity**: O(n log n) for sorting and heap operations. Space O(n).

**Follow-up questions**: "What if projects can be repeated?" — unbounded, just always pick the best affordable. "What if there are dependencies between projects?" — topological sort + greedy.

---

### Problem: Minimum Number of Refueling Stops (LC #871) — Hard
**Companies**: Google, Amazon
**Why it's asked**: Greedy with a max-heap. The insight is to delay fueling decisions: drive as far as you can, and when you run out, "retroactively" use the best gas station you passed.

**Brute Force**:
```python
def min_refuel_stops_brute(target, startFuel, stations):
    """DP: dp[i] = farthest distance with i refueling stops."""
    n = len(stations)
    dp = [startFuel] + [0] * n

    for i in range(n):
        for j in range(i, -1, -1):
            if dp[j] >= stations[i][0]:  # can reach station i with j stops
                dp[j + 1] = max(dp[j + 1], dp[j] + stations[i][1])

    for i in range(n + 1):
        if dp[i] >= target:
            return i
    return -1
```
O(n^2) time and space.

**Key Insight**: Drive greedily as far as possible. When you run out of fuel (current fuel < distance to next station or target), pick the station with the most fuel among all stations you have already passed. Use a max-heap to efficiently find this best past station. This works because fueling at a passed station does not change your current position — it just adds fuel.

**Optimal Solution**:
```python
import heapq

def min_refuel_stops(target, startFuel, stations):
    fuel = startFuel
    stops = 0
    heap = []  # max-heap of fuel amounts at passed stations (negated)
    i = 0

    while fuel < target:
        # Add all stations we can reach with current fuel
        while i < len(stations) and stations[i][0] <= fuel:
            heapq.heappush(heap, -stations[i][1])  # negate for max-heap
            i += 1

        if not heap:
            return -1  # cannot reach target or next station

        # Retroactively refuel at the best station we passed
        fuel += -heapq.heappop(heap)
        stops += 1

    return stops
```

**Dry Run** with `target = 100, startFuel = 10, stations = [[10,60],[20,30],[30,30],[60,40]]`:
```
fuel=10, stations reachable: [10,60] (position 10 <= fuel 10)
  heap = [-60]
fuel < 100, pop 60 -> fuel=70, stops=1
  Now reachable: [20,30] (20<=70), [30,30] (30<=70), [60,40] (60<=70)
  heap = [-40, -30, -30]
fuel=70 < 100, pop 40 -> fuel=110, stops=2
fuel=110 >= 100, done!

Answer: 2
```

**Edge Cases**: startFuel >= target (0 stops), no stations and startFuel < target (-1), stations not in order (problem guarantees sorted).

**Complexity**: O(n log n) for heap operations. Space O(n).

**Follow-up questions**: "What if fuel tanks have limited capacity?" — need to consider when to refuel more carefully. "What if stations also have a time cost?" — becomes a DP or graph problem.

---

### Problem: Course Schedule III (LC #630) — Hard
**Companies**: Google, Amazon
**Why it's asked**: Greedy with heap for scheduling under deadlines. Tests the "swap with worst choice" greedy strategy.

**Brute Force**:
```python
def schedule_course_brute(courses):
    """Try all subsets and orderings — exponential."""
    pass
```

**Key Insight**: Sort courses by deadline. Process them in deadline order: if a course fits (current_time + duration <= deadline), take it. If it does not fit, check if it is shorter than the longest course we have already taken. If so, swap it in (drop the longest, add this shorter one). This keeps the time usage minimal for the same number of courses. Use a max-heap to track durations of taken courses.

**Optimal Solution**:
```python
import heapq

def schedule_course(courses):
    # Sort by deadline
    courses.sort(key=lambda x: x[1])

    heap = []  # max-heap of durations (negated)
    current_time = 0

    for duration, deadline in courses:
        current_time += duration
        heapq.heappush(heap, -duration)

        # If we exceeded the deadline, drop the longest course
        if current_time > deadline:
            longest = -heapq.heappop(heap)
            current_time -= longest

    return len(heap)
```

**Dry Run** with `courses = [[100,200],[200,1300],[1000,1250],[2000,3200]]`:
```
Sorted by deadline: [[100,200],[1000,1250],[200,1300],[2000,3200]]

[100,200]: time=100, heap=[-100]. 100<=200, ok.
[1000,1250]: time=1100, heap=[-1000,-100]. 1100<=1250, ok.
[200,1300]: time=1300, heap=[-1000,-200,-100]. 1300>1300? No (<=), ok.
  Wait: 1300 <= 1300, so it fits!
[2000,3200]: time=3300, heap=[-2000,-1000,-200,-100]. 3300>3200, too late!
  Pop longest: 2000. time=3300-2000=1300, heap=[-1000,-200,-100].

Answer: 3 courses
```

**Edge Cases**: All courses fit, no course fits (0), courses with same deadline, course duration > deadline (impossible, skip).

**Complexity**: O(n log n) for sorting and heap operations. Space O(n).

**Follow-up questions**: "What if courses have different values and you want to maximize total value?" — weighted scheduling problem, needs DP. "What if some courses are prerequisites?" — topological sort first.

---

## Common Mistakes & Interview Tips

### Common Mistakes

1. **Assuming greedy works without proof.** The most dangerous mistake. Many problems look greedy but require DP. Always ask yourself: "Can I construct a counterexample where the greedy choice leads to a suboptimal result?" If not, informally argue why the exchange argument holds.

2. **Sorting by the wrong criterion.** In interval problems, sorting by start time vs. end time gives different results. Sorting by end time is correct for activity selection / non-overlapping intervals. Sorting by start time is correct for merging intervals.

3. **Off-by-one in interval overlap checks.** Is `[1,2]` overlapping with `[2,3]`? That depends on whether endpoints are inclusive. Clarify with the interviewer and be consistent. Usually `start >= prev_end` means no overlap (touching is ok).

4. **Not handling edge cases in heap problems.** Always check if the heap is empty before popping. This handles cases where no option is available (return -1 or similar).

5. **Greedy on wrong dimension.** Some problems have multiple attributes (profit and capital, duration and deadline). Greedily optimizing one without considering the other leads to wrong answers. Think about which attribute to sort by and which to greedily optimize.

### Interview Tips

1. **Start by considering whether greedy works.** Before jumping to DP, ask: "Is there a natural ordering where the locally best choice is globally best?" If you can argue it in 30 seconds, go greedy. If not, pivot to DP.

2. **Mention the exchange argument.** Even informally saying "if there were a better solution that did not make this greedy choice, I could swap in the greedy choice without making things worse" demonstrates mathematical maturity.

3. **Know the standard greedy problems.** Activity selection, Huffman coding, fractional knapsack, Dijkstra's. These are the building blocks. Most interview greedy problems are variations.

4. **Use heaps for online greedy.** When you need "the best option so far" or "the best among available choices," a heap gives O(log n) access. This pattern appears in IPO, Min Refueling Stops, Task Scheduler, and many others.

5. **Two-pass greedy is powerful.** Candy, Trapping Rain Water, and similar problems benefit from a left-to-right pass followed by a right-to-left pass. Each pass handles constraints in one direction.

---

## Pattern Connections

- **Greedy vs DP**: If greedy does not work, DP often does. The key difference: greedy commits to one choice per subproblem, DP considers all choices. Coin Change with standard denominations (1, 5, 10, 25) is greedy; with arbitrary denominations, it requires DP.

- **Greedy + Heap**: A very common combination. The heap maintains the "best available option" as the greedy scan progresses. See IPO, Course Schedule III, Min Refueling Stops.

- **Greedy + Sorting**: Almost all greedy interval problems start with sorting. The sorting criterion encodes the greedy strategy.

- **Greedy + Two Pointers**: Container With Most Water, Trapping Rain Water (one approach), and other problems use two pointers moving greedily inward.

- **Kadane's and DP**: Kadane's algorithm is both greedy and DP. The recurrence `dp[i] = max(nums[i], dp[i-1] + nums[i])` is DP. The observation that you only need the previous value and always take the local maximum is greedy.

- **Interval Problems Family**: Merge Intervals, Non-overlapping Intervals, Insert Interval, Meeting Rooms I/II, Employee Free Time. These all follow the sort-and-scan pattern with slight variations in the merge/select logic.
