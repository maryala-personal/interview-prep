# Dynamic Programming — Complete Interview Guide

## When to Use This Pattern

Dynamic programming applies when a problem has two key properties: **optimal substructure** (the optimal solution can be constructed from optimal solutions to subproblems) and **overlapping subproblems** (the same subproblems are solved repeatedly in a naive recursive approach).

**Signals that indicate DP:**
1. The problem asks for an **optimum** (minimum, maximum, longest, shortest, count of ways).
2. You can define the answer in terms of **smaller versions of the same problem** — there is a recurrence relation.
3. A brute-force recursive solution re-computes the same subproblem many times (draw the recursion tree and look for repeated nodes).
4. The problem involves **making a sequence of decisions** where each decision affects future choices (buy/sell stocks, include/exclude items, choose a path).
5. The input involves sequences, grids, or intervals, and the answer depends on contiguous or subsequence relationships.
6. The problem says "count the number of ways" or "is it possible" — these often reduce to summing or OR-ing over subproblems.

**When NOT to use DP:**
- The problem has a greedy solution (each local choice leads to a global optimum without needing to consider all subproblems).
- There are no overlapping subproblems — pure divide-and-conquer suffices (e.g., merge sort).
- The state space is too large to enumerate (consider approximation or other techniques).

---

### ⚡ Pattern Overlap & Decision Guide

#### DP vs Commonly Confused Patterns

| Signal in Problem | Likely Pattern | NOT DP Because... |
|---|---|---|
| "Minimum coins to make amount" with standard denominations (1,5,10,25) | **Greedy** | Greedy choice property holds: always pick largest coin |
| "Minimum coins to make amount" with arbitrary denominations (1,3,4) | **DP** | Greedy fails: for amount=6, greedy gives 4+1+1=3 coins, but 3+3=2 coins is optimal |
| "Generate all valid combinations" | **Backtracking** | Need to enumerate, not count/optimize |
| "Count the number of ways" with overlapping subproblems | **DP** | Classic DP signal |
| "Find minimum path sum in grid" | **DP** | Optimal substructure + overlapping subproblems |
| "Find shortest path in weighted graph" | **Dijkstra/Bellman-Ford** | Graph structure, not sequence/grid DP |
| "Can this string be segmented?" (with repeated checks) | **DP** | Overlapping subproblems in backtracking |
| "Compute running sum / range sum quickly" | **Prefix Sum** | No optimization decision; just precomputation |

#### Quick Signals That Point to DP Specifically
- **"How many ways..."** + input has repeated substructure = DP (not just backtracking)
- **"Minimum/maximum..."** + decisions affect future choices = DP (not greedy)
- **"Is it possible to..."** + recursive solution has overlapping subproblems = DP
- The recurrence involves `min()`, `max()`, or `sum()` over subproblems

#### Common Mistakes: "I thought it was X, but it's actually DP"

1. **Looks like Greedy, but is DP**: *Coin Change (LC #322)* with denominations [1, 3, 4]. Greedy picks 4+1+1=3 coins for amount 6, but optimal is 3+3=2 coins. The greedy choice property fails because picking the largest coin now can force suboptimal choices later.

2. **Looks like Backtracking, but is DP**: *Target Sum (LC #494)*. You might start with backtracking (assign + or - to each number), but notice the recursion tree has massive overlap. Adding memoization transforms it into DP. The tell: you only need the COUNT of ways, not all actual assignments.

3. **Looks like DFS+Memoization, but is actually Prefix Sum**: *Range Sum Query (LC #303)*. You might think about dp[i] = sum of first i elements, but this is simpler -- it is a prefix sum array with no optimization decisions. DP requires making choices; prefix sum is just precomputation.

4. **Looks like DP, but is actually Greedy**: *Jump Game (LC #55)*. A DP solution works (dp[i] = can we reach index i?) but is O(n^2). The key insight is that a simple greedy scan tracking the farthest reachable index gives O(n). The greedy choice property holds: if you can reach index i, you can reach everything before it.

---

## Core Mechanics

### Why Does DP Work?

DP trades **space for time**. A naive recursive solution might have exponential time complexity because it recomputes the same subproblems. DP stores (memoizes) the result of each subproblem so it is computed only once.

There are two implementation styles:

**Top-Down (Memoization):** Write the natural recursion, then add a cache. This is often easier to think about because you write the recurrence directly.

**Bottom-Up (Tabulation):** Fill a table iteratively, starting from the smallest subproblems and building up. This avoids recursion overhead and can be easier to optimize for space.

### Step-by-Step Framework for Solving Any DP Problem

1. **Define the state.** What information do you need to uniquely describe a subproblem? This becomes the parameters of your function or the indices of your table. Common states: `dp[i]` = answer considering the first `i` elements, `dp[i][j]` = answer for a subproblem defined by two parameters.

2. **Write the recurrence relation.** Express `dp[i]` in terms of smaller subproblems. This is the heart of DP. Think: "If I knew the answer to all smaller problems, how would I compute the answer to this problem?"

3. **Identify the base cases.** What are the smallest subproblems whose answers you know directly?

4. **Determine the iteration order.** When filling the table bottom-up, ensure that when you compute `dp[i]`, all subproblems it depends on have already been computed.

5. **Identify the final answer.** Which entry (or combination of entries) in the table gives the answer to the original problem?

6. **Optimize space if possible.** If `dp[i]` depends only on `dp[i-1]` (or a fixed number of previous rows), you can reduce space from O(n) to O(1), or from O(n*m) to O(m).

### Visual Walkthrough: Fibonacci as the Simplest DP

Consider computing `fib(5)`:

```
Naive recursion tree (exponential work):

                    fib(5)
                   /      \
              fib(4)       fib(3)      <-- fib(3) computed TWICE
             /     \       /    \
         fib(3)  fib(2) fib(2) fib(1)  <-- fib(2) computed THREE times
        /    \
    fib(2)  fib(1)

With memoization, each fib(k) is computed once:

fib(0) = 0  [stored]
fib(1) = 1  [stored]
fib(2) = fib(1) + fib(0) = 1  [stored, never recomputed]
fib(3) = fib(2) + fib(1) = 2  [stored, never recomputed]
fib(4) = fib(3) + fib(2) = 3  [stored]
fib(5) = fib(4) + fib(3) = 5  [stored]
```

Time drops from O(2^n) to O(n). Space is O(n) for the cache (or O(1) with rolling variables).

---

## Sub-Pattern Templates

### 1D DP Template

Used when the state depends on a single index (position in an array or sequence).

```python
def solve_1d_dp(nums):
    n = len(nums)
    # dp[i] = answer for subproblem ending at or considering index i
    dp = [0] * n

    # Base case
    dp[0] = nums[0]  # problem-specific

    # Fill table left to right
    for i in range(1, n):
        # Recurrence: dp[i] depends on dp[j] for j < i
        dp[i] = max(dp[i - 1] + nums[i], nums[i])  # example recurrence

    return max(dp)  # or dp[n-1], depending on problem
```

```go
func solve1DDP(nums []int) int {
    n := len(nums)
    dp := make([]int, n)

    // Base case
    dp[0] = nums[0]

    // Fill table
    for i := 1; i < n; i++ {
        dp[i] = max(dp[i-1]+nums[i], nums[i])
    }

    result := dp[0]
    for _, v := range dp {
        if v > result {
            result = v
        }
    }
    return result
}
```

### 2D DP Template

Used when the state requires two parameters (e.g., two strings, grid coordinates, interval endpoints).

```python
def solve_2d_dp(text1, text2):
    m, n = len(text1), len(text2)
    # dp[i][j] = answer for text1[:i] and text2[:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Base cases: dp[0][j] = 0, dp[i][0] = 0 (empty string cases)

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[m][n]
```

```go
func solve2DDP(text1, text2 string) int {
    m, n := len(text1), len(text2)
    dp := make([][]int, m+1)
    for i := range dp {
        dp[i] = make([]int, n+1)
    }

    for i := 1; i <= m; i++ {
        for j := 1; j <= n; j++ {
            if text1[i-1] == text2[j-1] {
                dp[i][j] = dp[i-1][j-1] + 1
            } else {
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
            }
        }
    }
    return dp[m][n]
}
```

### 0/1 Knapsack Template

Each item can be included or excluded exactly once. The state tracks which items we have considered and the remaining capacity.

```python
def knapsack_01(weights, values, capacity):
    n = len(weights)
    # dp[i][w] = max value using items 0..i-1 with capacity w
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(capacity + 1):
            # Don't take item i
            dp[i][w] = dp[i - 1][w]
            # Take item i (if it fits)
            if weights[i - 1] <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - weights[i - 1]] + values[i - 1])

    return dp[n][capacity]
```

```go
func knapsack01(weights, values []int, capacity int) int {
    n := len(weights)
    dp := make([][]int, n+1)
    for i := range dp {
        dp[i] = make([]int, capacity+1)
    }

    for i := 1; i <= n; i++ {
        for w := 0; w <= capacity; w++ {
            dp[i][w] = dp[i-1][w]
            if weights[i-1] <= w {
                dp[i][w] = max(dp[i][w], dp[i-1][w-weights[i-1]]+values[i-1])
            }
        }
    }
    return dp[n][capacity]
}
```

**Space-optimized 1D version** (iterate capacity in reverse to avoid using an item twice):

```python
def knapsack_01_optimized(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for i in range(len(weights)):
        for w in range(capacity, weights[i] - 1, -1):  # reverse!
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    return dp[capacity]
```

### Interval DP Template

Used when the subproblem is defined over a contiguous range [i, j] and you try every possible split point.

```python
def interval_dp(arr):
    n = len(arr)
    dp = [[0] * n for _ in range(n)]

    # Base case: intervals of length 1
    for i in range(n):
        dp[i][i] = 0  # or some base value

    # Enumerate by interval length
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float('inf')
            for k in range(i, j):  # split point
                dp[i][j] = min(dp[i][j], dp[i][k] + dp[k + 1][j] + cost(i, j, k))

    return dp[0][n - 1]
```

```go
func intervalDP(arr []int) int {
    n := len(arr)
    dp := make([][]int, n)
    for i := range dp {
        dp[i] = make([]int, n)
    }

    for length := 2; length <= n; length++ {
        for i := 0; i <= n-length; i++ {
            j := i + length - 1
            dp[i][j] = math.MaxInt32
            for k := i; k < j; k++ {
                val := dp[i][k] + dp[k+1][j] + cost(arr, i, j, k)
                if val < dp[i][j] {
                    dp[i][j] = val
                }
            }
        }
    }
    return dp[0][n-1]
}
```

### State Machine DP Template

Used for problems where decisions at each step depend on the current "state" (e.g., holding stock vs not, cooldown period). Model transitions between states explicitly.

```python
def state_machine_dp(prices):
    n = len(prices)
    # Define states: e.g., HELD, SOLD, REST
    # dp[i][state] = best profit at day i in the given state
    held = -prices[0]  # bought on day 0
    sold = 0
    rest = 0

    for i in range(1, n):
        prev_held, prev_sold, prev_rest = held, sold, rest
        held = max(prev_held, prev_rest - prices[i])   # hold or buy
        sold = prev_held + prices[i]                     # sell today
        rest = max(prev_rest, prev_sold)                 # do nothing

    return max(sold, rest)
```

```go
func stateMachineDP(prices []int) int {
    held := -prices[0]
    sold := 0
    rest := 0

    for i := 1; i < len(prices); i++ {
        prevHeld, prevSold, prevRest := held, sold, rest
        held = max(prevHeld, prevRest-prices[i])
        sold = prevHeld + prices[i]
        rest = max(prevRest, prevSold)
    }
    return max(sold, rest)
}
```

---

## Problem Walkthroughs

### Problem: Climbing Stairs (LC #70) — Easy
**Companies**: Google, Amazon, Meta, Microsoft, Apple — frequently used as a warm-up
**Why it's asked**: Tests whether you recognize the DP substructure in a simple setting and can optimize from recursion to iteration.

**Brute Force**:
```python
def climb_stairs_brute(n):
    """Try all possible ways: at each step, go 1 or 2 stairs."""
    if n <= 1:
        return 1
    return climb_stairs_brute(n - 1) + climb_stairs_brute(n - 2)
```
This is O(2^n) time because the recursion tree branches at every level, with massive recomputation.

**Key Insight**: The number of ways to reach step `n` is the sum of ways to reach step `n-1` (then take 1 step) and step `n-2` (then take 2 steps). This is exactly the Fibonacci recurrence: `dp[n] = dp[n-1] + dp[n-2]`.

**Optimal Solution**:
```python
def climb_stairs(n):
    if n <= 2:
        return n
    prev2, prev1 = 1, 2
    for i in range(3, n + 1):
        curr = prev1 + prev2
        prev2 = prev1
        prev1 = curr
    return prev1
```

**Dry Run 1** with `n = 5` (standard case):
```
Step 1: 1 way  (just take one step)
Step 2: 2 ways (1+1 or 2)
Step 3: prev2=1, prev1=2 -> curr=3 -> [1,2,3]
Step 4: prev2=2, prev1=3 -> curr=5 -> [1,2,3,5]
Step 5: prev2=3, prev1=5 -> curr=8 -> [1,2,3,5,8]
Answer: 8
```

**Dry Run 2** with `n = 1` (minimum edge case):
```
n <= 2, return n = 1.
Answer: 1 (only one way: take a single step)
```

**Dry Run 3** with `n = 3` (tricky: reveals WHY the recurrence works):
```
Step 1: 1 way  -> {1}
Step 2: 2 ways -> {1+1, 2}
Step 3: prev2=1, prev1=2 -> curr=3

Why 3? The paths to step 3 are EXACTLY:
  - All paths to step 2, each extended by "+1 step": {1+1+1, 2+1}
  - All paths to step 1, each extended by "+2 steps": {1+2}
  Total: 2 + 1 = 3. This is WHY dp[n] = dp[n-1] + dp[n-2].

Notice: you cannot reach step 3 by taking 3 single jumps from step 0 directly --
the recurrence captures all paths through the two possible last-step choices.
Answer: 3
```

**Edge Cases**: `n=1` returns 1, `n=0` returns 1 (one way to stay at ground), negative n is invalid.

**Complexity**: O(n) time, O(1) space.

**Follow-up questions**: "What if you can take 1, 2, or 3 steps?" — dp[i] = dp[i-1] + dp[i-2] + dp[i-3]. "What if the step costs are given and you want minimum cost?" — leads to LC #746 Min Cost Climbing Stairs.

---

### Problem: House Robber (LC #198) — Medium
**Companies**: Google, Amazon, Microsoft, Meta
**Why it's asked**: Classic 1D DP that tests the "include or exclude" decision at each step, the most fundamental DP pattern.

**Brute Force**:
```python
def rob_brute(nums):
    """Try all subsets of non-adjacent houses."""
    def helper(i):
        if i < 0:
            return 0
        return max(helper(i - 1), helper(i - 2) + nums[i])
    return helper(len(nums) - 1)
```
O(2^n) time due to branching at each house.

**Key Insight**: At each house `i`, you have two choices: skip it (take the best from houses 0..i-1) or rob it (take nums[i] plus the best from houses 0..i-2, since adjacent houses cannot both be robbed). This gives the recurrence `dp[i] = max(dp[i-1], dp[i-2] + nums[i])`.

**Optimal Solution**:
```python
def rob(nums):
    if not nums:
        return 0
    if len(nums) == 1:
        return nums[0]

    prev2, prev1 = 0, 0
    for num in nums:
        curr = max(prev1, prev2 + num)
        prev2 = prev1
        prev1 = curr
    return prev1
```

**Dry Run 1** with `nums = [2, 7, 9, 3, 1]` (standard case):
```
num=2: curr=max(0, 0+2)=2, prev2=0, prev1=2
num=7: curr=max(2, 0+7)=7, prev2=2, prev1=7
num=9: curr=max(7, 2+9)=11, prev2=7, prev1=11
num=3: curr=max(11, 7+3)=11, prev2=11, prev1=11  (skip house with 3)
num=1: curr=max(11, 11+1)=12, prev2=11, prev1=12
Answer: 12 (rob houses with 2, 9, 1)
```

**Dry Run 2** with `nums = [2, 1, 1, 2]` (tricky: greedy "pick the max" fails):
```
A greedy approach might pick index 0 (value 2) and index 3 (value 2) = 4.
But is there a better option? Let's trace DP:

num=2: curr=max(0, 0+2)=2, prev2=0, prev1=2
num=1: curr=max(2, 0+1)=2, prev2=2, prev1=2  (skip 1, keeping 2)
num=1: curr=max(2, 2+1)=3, prev2=2, prev1=3  (take 1 at index 2, total=2+1=3)
num=2: curr=max(3, 2+2)=4, prev2=3, prev1=4

Answer: 4 (rob indices 0 and 3, OR indices 0 and 2 gives 3, so 0+3 is best)

Notice: the DP considers BOTH options at each step. A greedy "always pick
highest available" would pick 2 (index 0), skip 1, skip 1, pick 2 (index 3) = 4.
Here greedy happens to match, but consider...
```

**Dry Run 3** with `nums = [4, 1, 2, 7, 5, 3, 1]` (tricky: non-adjacent constraint forces skipping a tempting large value):
```
num=4: curr=max(0,0+4)=4,   prev2=0, prev1=4
num=1: curr=max(4,0+1)=4,   prev2=4, prev1=4   (skip 1)
num=2: curr=max(4,4+2)=6,   prev2=4, prev1=6   (take 2, combined with 4)
num=7: curr=max(6,4+7)=11,  prev2=6, prev1=11  (take 7, combined with earlier 4)
num=5: curr=max(11,6+5)=11, prev2=11, prev1=11 (skip 5! taking it would mean skipping 7)
num=3: curr=max(11,11+3)=14, prev2=11, prev1=14 (take 3, combined with 7+4=11)
num=1: curr=max(14,11+1)=14, prev2=14, prev1=14

Answer: 14 (rob 4, 7, 3 at indices 0, 3, 5)

Notice at step 5 (num=5): even though 5 is large, taking it means giving up 7
from the previous step. The DP correctly sees that 11 > 6+5=11 (tie, skip).
This is WHY greedy "pick all large values" fails -- adjacency constraints create
non-obvious trade-offs.
```

**Edge Cases**: Single house (return its value), two houses (return max), all same values, empty array.

**Complexity**: O(n) time, O(1) space.

**Follow-up questions**: "What if the houses are in a circle?" — House Robber II (LC #213): run the algorithm twice, once on `nums[0..n-2]` and once on `nums[1..n-1]`, take the max. "What if it's a binary tree?" — House Robber III (LC #337): tree DP where each node returns (rob_this, skip_this).

---

### Problem: Longest Increasing Subsequence (LC #300) — Medium
**Companies**: Google, Microsoft, Amazon, Meta, Uber — extremely common
**Why it's asked**: Tests both the O(n^2) DP approach and the O(n log n) patience sorting / binary search optimization. Interviewers often want both.

**Brute Force**:
```python
def length_of_lis_brute(nums):
    """Generate all subsequences, filter increasing ones, return max length."""
    def backtrack(i, prev):
        if i == len(nums):
            return 0
        # Skip nums[i]
        result = backtrack(i + 1, prev)
        # Take nums[i] if it extends the increasing subsequence
        if prev < nums[i]:
            result = max(result, 1 + backtrack(i + 1, nums[i]))
        return result
    return backtrack(0, float('-inf'))
```
O(2^n) time.

**Key Insight (O(n^2) DP)**: Define `dp[i]` as the length of the longest increasing subsequence ending at index `i`. For each `i`, look at all `j < i` where `nums[j] < nums[i]` and set `dp[i] = max(dp[j] + 1)`. Every element by itself is a subsequence of length 1, so initialize `dp[i] = 1`.

**O(n^2) Solution**:
```python
def length_of_lis(nums):
    n = len(nums)
    dp = [1] * n

    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)

    return max(dp)
```

**Key Insight (O(n log n))**: Maintain an array `tails` where `tails[k]` is the smallest possible tail element of an increasing subsequence of length `k+1`. For each number, binary search for its position in `tails`. If it is larger than all elements, append it (extending the longest subsequence). Otherwise, replace the first element in `tails` that is >= it. The length of `tails` at the end is the LIS length.

**Optimal O(n log n) Solution**:
```python
import bisect

def length_of_lis_optimal(nums):
    tails = []
    for num in nums:
        pos = bisect.bisect_left(tails, num)
        if pos == len(tails):
            tails.append(num)
        else:
            tails[pos] = num
    return len(tails)
```

**Dry Run 1** with `nums = [10, 9, 2, 5, 3, 7, 101, 18]` (standard case, O(n log n)):
```
O(n log n) approach, tracking tails array:
num=10:  tails=[] -> pos=0, append -> tails=[10]
num=9:   tails=[10] -> pos=0 (9<10), replace -> tails=[9]
num=2:   tails=[9] -> pos=0 (2<9), replace -> tails=[2]
num=5:   tails=[2] -> pos=1, append -> tails=[2,5]
num=3:   tails=[2,5] -> pos=1 (3<5), replace -> tails=[2,3]
num=7:   tails=[2,3] -> pos=2, append -> tails=[2,3,7]
num=101: tails=[2,3,7] -> pos=3, append -> tails=[2,3,7,101]
num=18:  tails=[2,3,7,101] -> pos=3 (18<101), replace -> tails=[2,3,7,18]
Answer: len(tails) = 4
```

Note: `tails` is NOT the actual LIS. It tracks the minimum possible tail for each length.

**Dry Run 2** with `nums = [3, 5, 6, 2, 5, 4, 19, 5, 6, 7, 12]` (tricky: replacing in tails does NOT shorten LIS, it prepares for future extensions):
```
num=3:   tails=[3]
num=5:   tails=[3,5]
num=6:   tails=[3,5,6]
num=2:   tails=[2,5,6]        <- replace 3 with 2. LIS length still 3!
num=5:   tails=[2,5,6]        <- bisect_left finds pos=1 (5==5), no change
num=4:   tails=[2,4,6]        <- replace 5 with 4
num=19:  tails=[2,4,6,19]     <- extend to length 4
num=5:   tails=[2,4,5,19]     <- replace 6 with 5
num=6:   tails=[2,4,5,6]      <- replace 19 with 6
num=7:   tails=[2,4,5,6,7]    <- extend to length 5
num=12:  tails=[2,4,5,6,7,12] <- extend to length 6
Answer: 6

Notice: when we replaced 3 with 2 at step 4, the LIS length did NOT decrease.
The replacement made tails[0] smaller, opening the door for future subsequences
starting with small values. tails=[2,5,6] means "there exists an IS of length 3
ending with 6, AND there exists an IS of length 1 ending with 2." These may be
DIFFERENT subsequences -- tails is not one coherent subsequence.
```

**Dry Run 3** with `nums = [1, 2, 3, 0, 2]` (tricky: a zero resets the beginning but does not destroy existing LIS):
```
num=1: tails=[1]
num=2: tails=[1,2]
num=3: tails=[1,2,3]       <- LIS of length 3
num=0: tails=[0,2,3]       <- replace 1 with 0. Length stays 3!
num=2: tails=[0,2,3]       <- bisect_left(tails,2)=1, tails[1]==2, no change
Answer: 3

The 0 replaced the first element but did NOT reduce the LIS length.
This confuses many people: "doesn't 0 break the increasing sequence?"
No -- tails[0]=0 just means there IS a subsequence of length 1 ending at 0.
The original LIS [1,2,3] is still valid. The replacement only matters if
future elements could build a LONGER sequence using 0 as a start.
```

**Edge Cases**: Array of length 1 (return 1), strictly decreasing array (return 1), all same elements (return 1), already sorted (return n).

**Complexity**: O(n^2) for basic DP, O(n log n) for binary search approach. Space O(n).

**Follow-up questions**: "How do you reconstruct the actual subsequence?" — maintain parent pointers. "What if we need the number of LIS of that length?" — LC #673, maintain a count array alongside dp.

---

### Problem: Word Break (LC #139) — Medium
**Companies**: Meta, Google, Amazon, Microsoft, Bloomberg — very frequently asked
**Why it's asked**: Tests DP combined with string processing. The key challenge is defining the right subproblem.

**Brute Force**:
```python
def word_break_brute(s, wordDict):
    """Try every possible partition recursively."""
    word_set = set(wordDict)
    def backtrack(start):
        if start == len(s):
            return True
        for end in range(start + 1, len(s) + 1):
            if s[start:end] in word_set and backtrack(end):
                return True
        return False
    return backtrack(0)
```
O(2^n) in the worst case (e.g., `s = "aaaa...a"` with `wordDict = ["a", "aa", "aaa", ...]`).

**Key Insight**: Define `dp[i]` = True if `s[0:i]` can be segmented into words from the dictionary. For each position `i`, check all positions `j < i`: if `dp[j]` is True and `s[j:i]` is in the dictionary, then `dp[i]` is True. The base case is `dp[0] = True` (empty string can be segmented).

**Optimal Solution**:
```python
def word_break(s, wordDict):
    word_set = set(wordDict)
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True  # empty string

    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break  # no need to check further

    return dp[n]
```

**Optimization with max word length bound**:

```python
def word_break_optimized(s, wordDict):
    word_set = set(wordDict)
    max_len = max(len(w) for w in wordDict) if wordDict else 0
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True

    for i in range(1, n + 1):
        for j in range(max(0, i - max_len), i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break

    return dp[n]
```

**Dry Run 1** with `s = "leetcode"`, `wordDict = ["leet", "code"]` (standard case):
```
dp = [T, F, F, F, F, F, F, F, F]  (length 9, index 0..8)
i=1: check s[0:1]="l" -> not in dict. dp[1]=F
i=2: check s[0:2]="le" -> no. dp[2]=F
i=3: check s[0:3]="lee" -> no. dp[3]=F
i=4: check s[0:4]="leet" -> YES and dp[0]=T -> dp[4]=T
i=5: s[0:5]="leetc"->no, s[4:5]="c"->no. dp[5]=F
i=6: ... dp[6]=F
i=7: ... dp[7]=F
i=8: check j=4: dp[4]=T and s[4:8]="code"->YES -> dp[8]=T
Answer: True
```

**Dry Run 2** with `s = "catsandog"`, `wordDict = ["cats","dog","sand","and","cat"]` (tricky: False despite many partial matches):
```
dp = [T, F, F, F, F, F, F, F, F, F]  (length 10)

i=3: s[0:3]="cat" -> YES, dp[3]=T
i=4: s[0:4]="cats" -> YES, dp[4]=T
i=7: j=4: dp[4]=T, s[4:7]="san" -> no
     j=3: dp[3]=T, s[3:7]="sand" -> no wait: s[3:7]="sand"? s="catsandog"
     s[3]='s', so s[3:7]="sand"... but wait, s="c-a-t-s-a-n-d-o-g"
     s[4:7]="and" -> YES, dp[4]=T -> dp[7]=T
     Also: j=3: dp[3]=T, s[3:7]="sand" -> YES -> dp[7]=T
i=9: j=7: dp[7]=T, s[7:9]="og" -> NOT in dict
     j=4: dp[4]=T, s[4:9]="andog" -> no
     j=3: dp[3]=T, s[3:9]="sandog" -> no
     No valid split found!

Answer: False

Notice: even though "cats"+"and" gets us to position 7, the remainder "og"
is not in the dictionary. And "cat"+"sand" also reaches position 7 with the
same dead end. The DP correctly identifies that NO combination of dictionary
words covers the entire string, despite multiple valid partial segmentations.
```

**Dry Run 3** with `s = "aaaaaaa"`, `wordDict = ["aaaa","aaa"]` (tricky: worst-case overlapping, tests the break optimization):
```
dp = [T, F, F, F, F, F, F, F]

i=3: s[0:3]="aaa" -> YES, dp[3]=T (break)
i=4: s[0:4]="aaaa" -> YES, dp[4]=T (break)
i=6: j=3: dp[3]=T, s[3:6]="aaa" -> YES, dp[6]=T (break)
     Also valid: j=2: dp[2]=F, skip. j=4: dp[4]=T, s[4:6]="aa" -> no.
i=7: j=3: dp[3]=T, s[3:7]="aaaa" -> YES, dp[7]=T (break)
     Also valid: j=4: dp[4]=T, s[4:7]="aaa" -> YES

Answer: True (aaa+aaaa or aaaa+aaa)

This case has MANY overlapping subproblems. Without the `break` optimization,
every position checks ALL prior positions. The `break` cuts off early once a
valid split is found. Without memoization, the brute-force backtracking on
s="a"*n with dict=["a","aa",...] is O(2^n) -- classic worst case for Word Break.
```

**Edge Cases**: Empty string (True), single character in dict, no word matches, overlapping words, repeated words.

**Complexity**: O(n^2 * k) where k is the average word length for substring hashing. Space O(n).

**Follow-up questions**: "Return all possible segmentations" — Word Break II (LC #140), use backtracking with memoization. "What if the dictionary is very large?" — use a Trie for prefix matching.

---

### Problem: Unique Paths (LC #62) — Medium
**Companies**: Google, Amazon, Meta, Microsoft
**Why it's asked**: Foundational 2D grid DP problem. Tests whether the candidate can set up a 2D DP table and handle grid boundaries.

**Brute Force**:
```python
def unique_paths_brute(m, n):
    """Recursively try going right or down from (0,0) to (m-1,n-1)."""
    if m == 1 or n == 1:
        return 1
    return unique_paths_brute(m - 1, n) + unique_paths_brute(m, n - 1)
```
O(2^(m+n)) time.

**Key Insight**: The number of paths to cell (i, j) is the sum of paths to (i-1, j) and (i, j-1), since you can only move right or down. The first row and first column each have exactly 1 path. This also has a combinatorial solution: the answer is C(m+n-2, m-1) since you make exactly (m-1) down moves and (n-1) right moves in some order.

**Optimal Solution**:
```python
def unique_paths(m, n):
    dp = [[1] * n for _ in range(m)]

    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1]

    return dp[m - 1][n - 1]
```

**Space-optimized** (only need the previous row):
```python
def unique_paths_optimized(m, n):
    row = [1] * n
    for i in range(1, m):
        for j in range(1, n):
            row[j] += row[j - 1]
    return row[n - 1]
```

**Dry Run 1** with `m=3, n=3` (standard case):
```
Initial:  [1, 1, 1]
          [1, _, _]
          [1, _, _]

Fill:     [1, 1, 1]
          [1, 2, 3]
          [1, 3, 6]

Answer: 6
```

**Dry Run 2** with `m=1, n=5` (edge case: single row):
```
Row: [1, 1, 1, 1, 1]
Answer: 1 (can only move right, exactly one path)
```

**Dry Run 3** with `m=3, n=4` (tricky: demonstrates how paths accumulate asymmetrically):
```
Fill:     [1, 1,  1,  1]
          [1, 2,  3,  4]
          [1, 3,  6, 10]

Answer: 10

Notice at cell (2,3): dp[2][3] = dp[1][3] + dp[2][2] = 4 + 6 = 10.
The 4 paths from above represent all paths that arrive via the rightmost
column, while the 6 paths from the left represent all paths arriving via
the bottom row. The grid is NOT symmetric when m != n.

This also equals C(m+n-2, m-1) = C(5, 2) = 10, confirming the combinatorial formula.
The combinatorial interpretation: you make exactly 2 down-moves and 3 right-moves
in some order, choosing which 2 of the 5 moves are "down."
```

**Edge Cases**: 1x1 grid (1 path), 1xN or Mx1 (1 path), large grids (use modular arithmetic if needed).

**Complexity**: O(m*n) time, O(n) space optimized.

**Follow-up questions**: "What if some cells are blocked?" — Unique Paths II (LC #63), set dp[i][j] = 0 for obstacles. "What if you can also move diagonally?" — dp[i][j] = dp[i-1][j] + dp[i][j-1] + dp[i-1][j-1].

---

### Problem: Longest Common Subsequence (LC #1143) — Medium
**Companies**: Google, Amazon, Microsoft, Meta
**Why it's asked**: The quintessential 2D string DP problem. Tests your ability to define states over two sequences and optimize space.

**Brute Force**:
```python
def lcs_brute(text1, text2):
    def helper(i, j):
        if i == len(text1) or j == len(text2):
            return 0
        if text1[i] == text2[j]:
            return 1 + helper(i + 1, j + 1)
        return max(helper(i + 1, j), helper(i, j + 1))
    return helper(0, 0)
```
O(2^(m+n)) time.

**Key Insight**: Define `dp[i][j]` = length of LCS of `text1[0:i]` and `text2[0:j]`. If the characters match (`text1[i-1] == text2[j-1]`), both contribute to the LCS: `dp[i][j] = dp[i-1][j-1] + 1`. If they do not match, the LCS either does not include `text1[i-1]` or does not include `text2[j-1]`: `dp[i][j] = max(dp[i-1][j], dp[i][j-1])`.

**Optimal Solution**:
```python
def longest_common_subsequence(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[m][n]
```

**Space-optimized** (two rows):
```python
def longest_common_subsequence_optimized(text1, text2):
    m, n = len(text1), len(text2)
    prev = [0] * (n + 1)

    for i in range(1, m + 1):
        curr = [0] * (n + 1)
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev = curr

    return prev[n]
```

**Dry Run 1** with `text1 = "abcde"`, `text2 = "ace"` (standard case):
```
    ""  a  c  e
""   0  0  0  0
a    0  1  1  1
b    0  1  1  1
c    0  1  2  2
d    0  1  2  2
e    0  1  2  3

Answer: 3 (LCS = "ace")
```

**Dry Run 2** with `text1 = "abc"`, `text2 = "def"` (no common characters):
```
    ""  d  e  f
""   0  0  0  0
a    0  0  0  0
b    0  0  0  0
c    0  0  0  0

Answer: 0 (no common subsequence)
```

**Dry Run 3** with `text1 = "abcba"`, `text2 = "abcba"` (tricky: identical strings, multiple valid LCS):
```
    ""  a  b  c  b  a
""   0  0  0  0  0  0
a    0  1  1  1  1  1
b    0  1  2  2  2  2
c    0  1  2  3  3  3
b    0  1  2  3  4  4
a    0  1  2  3  4  5

Answer: 5 (LCS = "abcba" = the entire string)

Now consider text1 = "abcbdab", text2 = "bdcaba" (tricky: multiple LCS of same length):

    ""  b  d  c  a  b  a
""   0  0  0  0  0  0  0
a    0  0  0  0  1  1  1
b    0  1  1  1  1  2  2
c    0  1  1  2  2  2  2
b    0  1  1  2  2  3  3
d    0  1  2  2  2  3  3
a    0  1  2  2  3  3  4
b    0  1  2  2  3  4  4

Answer: 4 (one LCS is "bdab", another is "bcba", another is "bcab")

Notice at dp[7][6]=4: there are MULTIPLE longest common subsequences of length 4.
The DP table only gives the LENGTH. To reconstruct, you backtrack from dp[m][n]:
when dp[i][j] came from the diagonal (chars matched), include that char;
when it came from max(left, up), you have a choice -- each choice may lead
to a different valid LCS. This is why "reconstruct the LCS" is a common follow-up.
```

**Edge Cases**: One or both strings empty (0), identical strings (length of either), no common characters (0).

**Complexity**: O(m*n) time, O(min(m,n)) space optimized.

**Follow-up questions**: "How do you reconstruct the actual LCS?" — backtrack from dp[m][n]: if characters match go diag, else go in direction of larger value. "What about longest common substring (contiguous)?" — reset dp[i][j] to 0 when characters don't match, track global max.

---

### Problem: Edit Distance (LC #72) — Medium
**Companies**: Google, Microsoft, Amazon, Meta — a classic
**Why it's asked**: Tests 2D DP with three transition types (insert, delete, replace). Foundation for spell checkers, DNA alignment, and diff algorithms.

**Brute Force**:
```python
def min_distance_brute(word1, word2):
    def helper(i, j):
        if i == 0:
            return j
        if j == 0:
            return i
        if word1[i - 1] == word2[j - 1]:
            return helper(i - 1, j - 1)
        return 1 + min(
            helper(i - 1, j),      # delete from word1
            helper(i, j - 1),      # insert into word1
            helper(i - 1, j - 1)   # replace in word1
        )
    return helper(len(word1), len(word2))
```
O(3^(m+n)) time.

**Key Insight**: `dp[i][j]` is the minimum edits to convert `word1[0:i]` to `word2[0:j]`. If last characters match, no edit needed: `dp[i][j] = dp[i-1][j-1]`. Otherwise, take the minimum of three operations: insert (`dp[i][j-1] + 1`), delete (`dp[i-1][j] + 1`), or replace (`dp[i-1][j-1] + 1`). Base cases: converting empty string to a string of length k requires k insertions.

**Optimal Solution**:
```python
def min_distance(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Base cases
    for i in range(m + 1):
        dp[i][0] = i  # delete all characters from word1
    for j in range(n + 1):
        dp[0][j] = j  # insert all characters of word2

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # delete
                    dp[i][j - 1],      # insert
                    dp[i - 1][j - 1]   # replace
                )

    return dp[m][n]
```

**Dry Run 1** with `word1 = "horse"`, `word2 = "ros"` (standard case):
```
      ""  r  o  s
""     0  1  2  3
h      1  1  2  3
o      2  2  1  2
r      3  2  2  2
s      4  3  3  2
e      5  4  4  3

Answer: 3 (horse -> rorse -> rose -> ros)
```

**Dry Run 2** with `word1 = "intention"`, `word2 = "execution"` (tricky: shared suffix, tests all three operations):
```
         ""  e  x  e  c  u  t  i  o  n
""        0  1  2  3  4  5  6  7  8  9
i         1  1  2  3  4  5  6  6  7  8
n         2  2  2  3  4  5  6  7  7  7
t         3  3  3  3  4  5  5  6  7  8
e         4  3  4  3  4  5  6  6  7  8
n         5  4  4  4  4  5  6  7  7  7
t         6  5  5  5  5  5  5  6  7  8
i         7  6  6  6  6  6  6  5  6  7
o         8  7  7  7  7  7  7  6  5  6
n         9  8  8  8  8  8  8  7  6  5

Answer: 5

Notice at dp[9][9]=5: the path goes through a mix of replace, insert, and delete.
At dp[1][1]=1: 'i' != 'e', so we take 1 + min(dp[0][0], dp[0][1], dp[1][0])
= 1 + min(0, 1, 1) = 1 (replace 'i' with 'e').
At dp[7][7]=5: 'i' == 'i', match! dp[7][7] = dp[6][6] = 5 (free diagonal step).
This shows HOW character matches create "free" transitions on the diagonal.
```

**Dry Run 3** with `word1 = ""`, `word2 = "abc"` (edge case: empty to non-empty):
```
      ""  a  b  c
""     0  1  2  3

Answer: 3 (insert 'a', insert 'b', insert 'c')
This is the base case: converting empty string to "abc" requires exactly 3 insertions.
Conversely, "abc" to "" requires 3 deletions. This base case initialization
(first row and first column) is where many candidates make mistakes.
```

**Edge Cases**: Both empty (0), one empty (length of the other), identical strings (0), single character strings.

**Complexity**: O(m*n) time, O(m*n) space (O(n) with rolling array).

**Follow-up questions**: "Can you do it in O(min(m,n)) space?" — yes, use rolling 1D array. "What if insert/delete/replace have different costs?" — use those costs instead of 1. "What if you can only insert and delete (no replace)?" — answer is m + n - 2 * LCS(word1, word2).

---

### Problem: Coin Change (LC #322) — Medium
**Companies**: Amazon, Google, Microsoft, Meta, Uber
**Why it's asked**: Classic unbounded knapsack variant. Tests the difference between 0/1 knapsack (each item used once) and unbounded (each item used unlimited times).

**Brute Force**:
```python
def coin_change_brute(coins, amount):
    def helper(remaining):
        if remaining == 0:
            return 0
        if remaining < 0:
            return float('inf')
        min_coins = float('inf')
        for coin in coins:
            min_coins = min(min_coins, 1 + helper(remaining - coin))
        return min_coins
    result = helper(amount)
    return result if result != float('inf') else -1
```
Exponential time.

**Key Insight**: `dp[i]` = minimum number of coins needed to make amount `i`. For each amount, try every coin: `dp[i] = min(dp[i - coin] + 1)` for all valid coins. Unlike 0/1 knapsack, we iterate capacity in the forward direction because coins can be reused.

**Optimal Solution**:
```python
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0

    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i and dp[i - coin] != float('inf'):
                dp[i] = min(dp[i], dp[i - coin] + 1)

    return dp[amount] if dp[amount] != float('inf') else -1
```

**Dry Run** with `coins = [1, 3, 4]`, `amount = 6`:
```
dp[0] = 0
dp[1] = min(dp[0]+1) = 1             (use coin 1)
dp[2] = min(dp[1]+1) = 2             (use coin 1 twice)
dp[3] = min(dp[2]+1, dp[0]+1) = 1    (use coin 3)
dp[4] = min(dp[3]+1, dp[1]+1, dp[0]+1) = 1  (use coin 4)
dp[5] = min(dp[4]+1, dp[2]+1) = 2    (use coins 4+1 or 3+2x1)
dp[6] = min(dp[5]+1, dp[3]+1, dp[2]+1) = 2  (use coins 3+3)
Answer: 2
```

**Edge Cases**: Amount 0 (return 0), impossible amount (return -1), single coin, coin larger than amount.

**Complexity**: O(amount * len(coins)) time, O(amount) space.

**Follow-up questions**: "What if you need the number of ways instead of the minimum?" — Coin Change II (LC #518). "What if each coin can only be used once?" — 0/1 knapsack, iterate amount in reverse.

---

### Problem: Partition Equal Subset Sum (LC #416) — Medium
**Companies**: Meta, Google, Amazon, Microsoft
**Why it's asked**: Direct application of 0/1 knapsack. Tests whether you can transform a partition problem into a subset sum problem.

**Brute Force**:
```python
def can_partition_brute(nums):
    total = sum(nums)
    if total % 2 != 0:
        return False
    target = total // 2

    def backtrack(i, remaining):
        if remaining == 0:
            return True
        if i == len(nums) or remaining < 0:
            return False
        return backtrack(i + 1, remaining - nums[i]) or backtrack(i + 1, remaining)

    return backtrack(0, target)
```
O(2^n) time.

**Key Insight**: The array can be partitioned into two subsets with equal sum only if the total sum is even. If it is, the problem reduces to: "Can we find a subset that sums to `total // 2`?" This is exactly the 0/1 knapsack (subset sum) problem.

**Optimal Solution**:
```python
def can_partition(nums):
    total = sum(nums)
    if total % 2 != 0:
        return False
    target = total // 2

    dp = [False] * (target + 1)
    dp[0] = True

    for num in nums:
        # Iterate in reverse to ensure each number is used at most once
        for j in range(target, num - 1, -1):
            dp[j] = dp[j] or dp[j - num]

    return dp[target]
```

**Dry Run** with `nums = [1, 5, 11, 5]`, total=22, target=11:
```
Initial: dp = [T, F, F, F, F, F, F, F, F, F, F, F]

num=1:  dp[1] = dp[1] or dp[0] = T
        dp = [T, T, F, F, F, F, F, F, F, F, F, F]

num=5:  dp[6]=dp[6]|dp[1]=T, dp[5]=dp[5]|dp[0]=T
        dp = [T, T, F, F, F, T, T, F, F, F, F, F]

num=11: dp[11]=dp[11]|dp[0]=T
        dp = [T, T, F, F, F, T, T, F, F, F, F, T]

Answer: True (subset {11} or {5,5,1} sums to 11)
```

**Edge Cases**: Single element (False), two equal elements (True), odd total sum (False immediately), all zeros.

**Complexity**: O(n * target) time, O(target) space.

**Follow-up questions**: "What if you need to minimize the difference between two partitions?" — run subset sum for all possible sums up to total/2, find the largest reachable sum. "What about three-way partition?" — significantly harder, need 2D DP.

---

### Problem: Target Sum (LC #494) — Medium
**Companies**: Meta, Google, Amazon
**Why it's asked**: A twist on subset sum that looks like backtracking but is elegantly solved with DP. Tests mathematical transformation skills.

**Brute Force**:
```python
def find_target_sum_ways_brute(nums, target):
    def backtrack(i, current_sum):
        if i == len(nums):
            return 1 if current_sum == target else 0
        return (backtrack(i + 1, current_sum + nums[i]) +
                backtrack(i + 1, current_sum - nums[i]))
    return backtrack(0, 0)
```
O(2^n) time.

**Key Insight**: Let P be the set of numbers with `+` and N be the set with `-`. Then `sum(P) - sum(N) = target` and `sum(P) + sum(N) = total`. Adding these: `2 * sum(P) = target + total`, so `sum(P) = (target + total) / 2`. This transforms the problem into "count the number of subsets that sum to `(target + total) / 2`" — a counting version of 0/1 knapsack.

**Optimal Solution**:
```python
def find_target_sum_ways(nums, target):
    total = sum(nums)

    # sum(P) = (target + total) / 2 must be a non-negative integer
    if (target + total) % 2 != 0 or abs(target) > total:
        return 0

    subset_sum = (target + total) // 2

    dp = [0] * (subset_sum + 1)
    dp[0] = 1

    for num in nums:
        for j in range(subset_sum, num - 1, -1):
            dp[j] += dp[j - num]

    return dp[subset_sum]
```

**Dry Run** with `nums = [1, 1, 1, 1, 1]`, `target = 3`:
```
total = 5, subset_sum = (3+5)/2 = 4
dp = [1, 0, 0, 0, 0]

num=1: j=4: dp[4]+=dp[3]=0, j=3: dp[3]+=dp[2]=0,
       j=2: dp[2]+=dp[1]=0, j=1: dp[1]+=dp[0]=1
       dp = [1, 1, 0, 0, 0]

num=1: j=4..1: dp[2]+=dp[1]=1, dp[1]+=dp[0]=2
       dp = [1, 2, 1, 0, 0]

num=1: dp[3]+=dp[2]=1, dp[2]+=dp[1]=3, dp[1]+=dp[0]=3
       dp = [1, 3, 3, 1, 0]

num=1: dp[4]+=dp[3]=1, dp[3]+=dp[2]=4, dp[2]+=dp[1]=6, dp[1]+=dp[0]=4
       dp = [1, 4, 6, 4, 1]

num=1: dp[4]+=dp[3]=5, dp[3]+=dp[2]=10, dp[2]+=dp[1]=10, dp[1]+=dp[0]=5
       dp = [1, 5, 10, 10, 5]
Answer: 5
```

**Edge Cases**: Target unreachable (0), target + total is odd (0), all zeros (2^n ways), single element.

**Complexity**: O(n * subset_sum) time, O(subset_sum) space.

**Follow-up questions**: "What if numbers can be negative?" — the mathematical transformation needs adjustment. "What if you need to print all expressions?" — backtracking with memoization.

---

### Problem: Best Time to Buy and Sell Stock with Cooldown (LC #309) — Medium
**Companies**: Google, Amazon, Meta
**Why it's asked**: Classic state machine DP. Tests your ability to model states and transitions explicitly.

**Brute Force**:
```python
def max_profit_brute(prices):
    def helper(i, holding):
        if i >= len(prices):
            return 0
        if holding:
            # sell or hold
            return max(prices[i] + helper(i + 2, False),  # sell + cooldown
                      helper(i + 1, True))                  # hold
        else:
            # buy or skip
            return max(-prices[i] + helper(i + 1, True),  # buy
                      helper(i + 1, False))                 # skip
    return helper(0, False)
```

**Key Insight**: Model three states for each day: HELD (holding a stock), SOLD (just sold today, enters cooldown), REST (not holding, no cooldown). The transitions are:
- HELD: either continue holding from yesterday, or buy today from REST state.
- SOLD: must have been HELD yesterday and sell today.
- REST: either was already resting, or was in SOLD state yesterday (cooldown finished).

**Optimal Solution**:
```python
def max_profit(prices):
    if not prices:
        return 0

    held = -prices[0]   # bought on day 0
    sold = 0            # impossible to have sold on day 0, but 0 works
    rest = 0            # doing nothing

    for i in range(1, len(prices)):
        prev_held = held
        prev_sold = sold
        prev_rest = rest

        held = max(prev_held, prev_rest - prices[i])
        sold = prev_held + prices[i]
        rest = max(prev_rest, prev_sold)

    return max(sold, rest)
```

**Dry Run** with `prices = [1, 2, 3, 0, 2]`:
```
Day 0: held=-1, sold=0, rest=0

Day 1 (price=2):
  held = max(-1, 0-2) = -1  (keep holding)
  sold = -1+2 = 1           (sell what we hold)
  rest = max(0, 0) = 0
  State: held=-1, sold=1, rest=0

Day 2 (price=3):
  held = max(-1, 0-3) = -1
  sold = -1+3 = 2
  rest = max(0, 1) = 1      (cooldown from yesterday's sale)
  State: held=-1, sold=2, rest=1

Day 3 (price=0):
  held = max(-1, 1-0) = 1   (buy at price 0, coming from rest)
  sold = -1+0 = -1
  rest = max(1, 2) = 2
  State: held=1, sold=-1, rest=2

Day 4 (price=2):
  held = max(1, 2-2) = 1
  sold = 1+2 = 3            (sell what we bought at price 0)
  rest = max(2, -1) = 2
  State: held=1, sold=3, rest=2

Answer: max(3, 2) = 3  (buy@1, sell@2, cooldown, buy@0, sell@2)
```

**Edge Cases**: Single price (0 profit), two prices (sell if profitable), all decreasing (0), all same price (0).

**Complexity**: O(n) time, O(1) space.

**Follow-up questions**: "What if cooldown is k days?" — state machine with k REST states or use dp[i] = max over dp[0..i-k-1]. "What if you can do at most 2 transactions?" — Best Time to Buy and Sell Stock III (LC #123).

---

### Problem: Regular Expression Matching (LC #10) — Hard
**Companies**: Google, Meta, Microsoft, Amazon
**Why it's asked**: Hard DP that tests careful state definition and handling of the `*` wildcard. Frequently asked at E6/L6 level.

**Brute Force**:
```python
def is_match_brute(s, p):
    if not p:
        return not s

    first_match = bool(s) and (p[0] == s[0] or p[0] == '.')

    if len(p) >= 2 and p[1] == '*':
        # Either skip "x*" entirely (zero occurrences) or
        # use "x*" to match first char and keep the pattern
        return (is_match_brute(s, p[2:]) or
                (first_match and is_match_brute(s[1:], p)))
    else:
        return first_match and is_match_brute(s[1:], p[1:])
```
Exponential in the worst case.

**Key Insight**: `dp[i][j]` = True if `s[0:i]` matches `p[0:j]`. The tricky case is `*`: pattern `p[j-2..j-1]` is "x*" which can match zero or more of character x. Zero occurrences: `dp[i][j] = dp[i][j-2]`. One or more: `dp[i][j] = dp[i-1][j]` if `s[i-1]` matches `p[j-2]`. The base case is `dp[0][0] = True`, and `dp[0][j]` can be True if the pattern consists of pairs that each match zero times (like "a*b*c*").

**Optimal Solution**:
```python
def is_match(s, p):
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True

    # Base case: empty string vs pattern like "a*b*c*"
    for j in range(2, n + 1):
        if p[j - 1] == '*':
            dp[0][j] = dp[0][j - 2]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j - 1] == '*':
                # Zero occurrences of preceding element
                dp[i][j] = dp[i][j - 2]
                # One or more occurrences
                if p[j - 2] == '.' or p[j - 2] == s[i - 1]:
                    dp[i][j] = dp[i][j] or dp[i - 1][j]
            elif p[j - 1] == '.' or p[j - 1] == s[i - 1]:
                dp[i][j] = dp[i - 1][j - 1]

    return dp[m][n]
```

**Dry Run** with `s = "aab"`, `p = "c*a*b"`:
```
Pattern "c*a*b" means: zero or more 'c', then zero or more 'a', then 'b'.

      ""    c    *    a    *    b
""     T    F    T    F    T    F
a      F    F    F    T    T    F
a      F    F    F    F    T    F
b      F    F    F    F    F    T

dp[0][2]=T: c* matches empty (zero c's)
dp[0][4]=T: c*a* matches empty (zero c's, zero a's)
dp[1][3]=T: 'a' matches 'a' and dp[0][2]=T
dp[1][4]=T: a* matches 'a' (one a) via dp[0][4] or dp[1-1][4]
dp[2][4]=T: a* matches 'aa' (two a's) via dp[1][4]
dp[3][5]=T: 'b' matches 'b', and dp[2][4]=T

Answer: True
```

**Edge Cases**: Both empty (True), pattern empty but string not (False), pattern is all `.*` (matches anything), consecutive `*` should not appear in valid input.

**Complexity**: O(m*n) time and space.

**Follow-up questions**: "What about wildcard matching with `?` and `*`?" — LC #44, simpler since `*` matches any sequence without a preceding character. "How would you implement this for a production regex engine?" — discuss NFA/DFA construction.

---

### Problem: Burst Balloons (LC #312) — Hard
**Companies**: Google, Microsoft, Amazon
**Why it's asked**: Interval DP at its finest. Tests whether you can think about the problem in reverse and define subproblems over intervals.

**Brute Force**:
```python
def max_coins_brute(nums):
    """Try every permutation of bursting order."""
    if not nums:
        return 0
    max_result = 0
    for i in range(len(nums)):
        left = nums[i - 1] if i > 0 else 1
        right = nums[i + 1] if i < len(nums) - 1 else 1
        coins = left * nums[i] * right
        remaining = nums[:i] + nums[i + 1:]
        max_result = max(max_result, coins + max_coins_brute(remaining))
    return max_result
```
O(n! * n) time — trying all orderings.

**Key Insight**: Think about which balloon to burst **last** in a range, not first. If balloon `k` is the last one burst in range `[i, j]`, then at the time of bursting it, the only remaining balloons in [i, j] are `nums[i-1]`, `nums[k]`, and `nums[j+1]` (the boundaries). The coins collected from `k` are `nums[i-1] * nums[k] * nums[j+1]`, and the subproblems [i, k-1] and [k+1, j] are independent because their boundaries do not change when `k` is the last to be burst. Define `dp[i][j]` = max coins from bursting all balloons in range [i, j]. Pad the array with 1s on both sides.

**Optimal Solution**:
```python
def max_coins(nums):
    # Pad with 1s on both sides
    balloons = [1] + nums + [1]
    n = len(balloons)
    dp = [[0] * n for _ in range(n)]

    # length = number of balloons in the range (at least 1)
    for length in range(1, n - 1):  # subproblem sizes
        for left in range(1, n - length):
            right = left + length - 1
            for k in range(left, right + 1):  # which balloon to burst last
                coins = (balloons[left - 1] * balloons[k] * balloons[right + 1] +
                        dp[left][k - 1] + dp[k + 1][right])
                dp[left][right] = max(dp[left][right], coins)

    return dp[1][n - 2]
```

**Dry Run** with `nums = [3, 1, 5, 8]`:
```
balloons = [1, 3, 1, 5, 8, 1]  (indices 0-5)
We need dp[1][4].

Length 1 (single balloons):
  dp[1][1]: burst 3 last -> 1*3*1 = 3
  dp[2][2]: burst 1 last -> 3*1*5 = 15
  dp[3][3]: burst 5 last -> 1*5*8 = 40
  dp[4][4]: burst 8 last -> 5*8*1 = 40

Length 2:
  dp[1][2]: k=1: 1*3*5 + dp[2][2] = 15+15=30
            k=2: dp[1][1] + 1*1*5 = 3+5=8
            -> dp[1][2] = 30
  dp[2][3]: k=2: 3*1*8 + dp[3][3] = 24+40=64
            k=3: dp[2][2] + 3*5*8 = 15+120=135
            -> dp[2][3] = 135
  dp[3][4]: k=3: 1*5*1 + dp[4][4] = 5+40=45
            k=4: dp[3][3] + 1*8*1 = 40+8=48
            -> dp[3][4] = 48

Length 3:
  dp[1][3]: k=1: 1*3*8 + dp[2][3] = 24+135=159
            k=2: dp[1][1] + 1*1*8 + dp[3][3] = 3+8+40=51
            k=3: dp[1][2] + 1*5*8 = 30+40=70
            -> dp[1][3] = 159
  dp[2][4]: k=2: 3*1*1 + dp[3][4] = 3+48=51
            k=3: dp[2][2] + 3*5*1 + dp[4][4] = 15+15+40=70
            k=4: dp[2][3] + 3*8*1 = 135+24=159
            -> dp[2][4] = 159

Length 4:
  dp[1][4]: k=1: 1*3*1 + dp[2][4] = 3+159=162
            k=2: dp[1][1] + 1*1*1 + dp[3][4] = 3+1+48=52
            k=3: dp[1][2] + 1*5*1 + dp[4][4] = 30+5+40=75
            k=4: dp[1][3] + 1*8*1 = 159+8=167
            -> dp[1][4] = 167

Answer: 167
```

**Edge Cases**: Single balloon (its value), two balloons (try both orders), empty array (0).

**Complexity**: O(n^3) time, O(n^2) space.

**Follow-up questions**: "Can you optimize below O(n^3)?" — not easily for general case. "What if you need to reconstruct the optimal order?" — store the choice of `k` at each step and backtrack.

---

## Common Mistakes & Interview Tips

### Common Mistakes

1. **Wrong base case.** The most common source of bugs. Always think carefully about what happens when indices are 0, arrays are empty, or strings are of length 0 or 1.

2. **Off-by-one errors in table dimensions.** When `dp[i]` represents "first i elements," the table needs size `n+1`. When `dp[i]` represents "ending at index i," size `n` suffices.

3. **Wrong iteration direction in space-optimized solutions.** In 0/1 knapsack, iterate capacity in reverse. In unbounded knapsack (coin change), iterate forward. Getting this wrong lets you use an item multiple times (or prevents reuse when you should allow it).

4. **Not handling impossible states.** When computing minimums, initialize with `float('inf')`. When computing counts, initialize with 0. Forgetting this leads to wrong answers on edge cases.

5. **Trying to be clever with the state before understanding the recurrence.** Start with the naive DP (potentially higher-dimensional state), verify correctness, then optimize.

### Interview Tips

1. **Start with recursion.** In an interview, first write the recursive solution with clear base cases. Then add memoization. Finally, convert to bottom-up if time permits or if the interviewer asks. This shows clear thinking progression.

2. **Explicitly state the DP definition.** Say "dp[i] represents the maximum profit considering the first i items" out loud. This helps both you and the interviewer track your logic.

3. **Draw the table for small inputs.** For 2D DP, drawing the table on the whiteboard and filling in a few cells is extremely clarifying and impressive to interviewers.

4. **Discuss space optimization last.** Get the O(m*n) solution correct first. The interviewer will prompt you about space if they want it.

5. **Know the sub-patterns.** Recognizing "this is a 0/1 knapsack" or "this is interval DP" immediately narrows down the solution structure and saves precious interview time.

6. **Practice the transformation step.** Many problems (Target Sum, Partition Equal Subset Sum) require transforming the problem statement into a known DP pattern. This algebraic step is where most candidates get stuck.

---

## Pattern Connections

- **DP + Binary Search**: LIS uses binary search inside DP for the O(n log n) solution. Many DP problems can be optimized with monotonic data structures or binary search.

- **DP + Graphs**: Shortest path algorithms (Dijkstra, Bellman-Ford) are fundamentally DP on graphs. DAG shortest path is pure DP via topological order.

- **DP vs Greedy**: If the problem has optimal substructure AND the greedy choice property, greedy suffices and is simpler. DP is needed when the greedy choice property fails (you need to consider all subproblems, not just the locally optimal one).

- **DP + Backtracking**: Many DP problems are discovered by first writing a backtracking solution and noticing overlapping subproblems. The memoized backtracking IS top-down DP.

- **Knapsack variants**: 0/1 knapsack (Partition Equal Subset Sum, Target Sum), unbounded knapsack (Coin Change), bounded knapsack (each item has a count limit). Recognizing which variant you face immediately gives you the template.

- **Interval DP**: Burst Balloons, Matrix Chain Multiplication, Palindrome problems. The key pattern is iterating by interval length and choosing a "split point."

- **State Machine DP**: Stock problems with cooldown/transaction limits, problems with multiple modes or phases. Model each state as a separate DP variable with clear transition rules.

- **String DP**: LCS, Edit Distance, Regular Expression Matching. Almost always 2D DP over the indices of two strings. The recurrence has a diagonal transition (characters match) and horizontal/vertical transitions (skip a character).
