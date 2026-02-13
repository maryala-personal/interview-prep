# Dynamic Programming (DP) Pattern Guide

## What is Dynamic Programming?

### Explain Like I'm 5
Imagine you're climbing stairs and someone asks you "How many ways can you reach step 10?" You start calculating... but then they ask "How about step 11?" Instead of starting over, you remember that to reach step 11, you can use your answer from step 10 and step 9! Dynamic Programming is like having a really good memory - you solve small problems once, write down the answers, and use them to solve bigger problems without doing the same work twice.

### Technical Definition
Dynamic Programming is an algorithmic paradigm that solves complex problems by breaking them down into simpler overlapping subproblems, solving each subproblem only once, and storing their solutions (memoization) to avoid redundant computations. It's an optimization technique that trades space for time complexity.

## Real-World Analogy

Think about calculating your cumulative GPA across semesters:
- **Without DP (Naive)**: Every semester, you recalculate your GPA from scratch, going through ALL past grades
- **With DP (Memoization)**: You remember last semester's GPA and credit hours, then just add the new semester's data

Another example - Route planning:
- **Without DP**: Every time you want to go from A to D, you recalculate all possible paths (A→B→D, A→C→D, A→B→C→D)
- **With DP**: You remember "best way from A to B" and "best way from B to D", then combine them

## When to Use Dynamic Programming

### Clear Signals
1. **Optimal Substructure**: The optimal solution to the problem contains optimal solutions to subproblems
   - Example: Shortest path from A to C through B = Shortest(A→B) + Shortest(B→C)

2. **Overlapping Subproblems**: The same subproblems are solved multiple times
   - Example: fib(5) = fib(4) + fib(3), and fib(4) = fib(3) + fib(2) - notice fib(3) is calculated twice!

3. **Problem asks for**:
   - Minimum/Maximum value
   - Count of ways to do something
   - True/False possibility
   - Longest/Shortest subsequence

### Red Flags (When NOT to use DP)
- No overlapping subproblems (use Divide & Conquer instead like Merge Sort)
- Problems with online/streaming data
- When greedy approach works and is simpler
- When space constraints are extremely tight and memoization isn't feasible

## The Problem: Classic Examples

### Example 1: Fibonacci Numbers

**Problem**: Calculate the nth Fibonacci number where F(n) = F(n-1) + F(n-2), with F(0) = 0, F(1) = 1.

### Example 2: Climbing Stairs

**Problem**: You are climbing a staircase with `n` steps. Each time you can climb 1 or 2 steps. In how many distinct ways can you climb to the top?

```
Input: n = 3
Output: 3
Explanation: Three ways to climb to the top:
1. 1 step + 1 step + 1 step
2. 1 step + 2 steps
3. 2 steps + 1 step
```

### Example 3: House Robber

**Problem**: You are a robber planning to rob houses along a street. Each house has a certain amount of money. You cannot rob two adjacent houses (alarm will trigger). What is the maximum money you can rob?

```
Input: nums = [2, 7, 9, 3, 1]
Output: 12
Explanation: Rob house 0 (2) + house 2 (9) + house 4 (1) = 12
```

## Brute Force Approach

### Fibonacci - Recursive (Exponential Time)

```python
def fib_brute_force(n):
    """
    Time Complexity: O(2^n) - exponential!
    Space Complexity: O(n) - recursion call stack

    Why so slow? fib(5) calculates fib(3) twice, fib(2) three times!
    The recursion tree has massive redundancy.
    """
    # Base cases
    if n <= 1:
        return n

    # Recursive case - pure recursion, no memory
    return fib_brute_force(n - 1) + fib_brute_force(n - 2)

# Example: fib(5) makes 15 function calls!
# fib(5)
# ├── fib(4)
# │   ├── fib(3)
# │   │   ├── fib(2)
# │   │   │   ├── fib(1) → 1
# │   │   │   └── fib(0) → 0
# │   │   └── fib(1) → 1
# │   └── fib(2)  ← RECALCULATED!
# │       ├── fib(1) → 1
# │       └── fib(0) → 0
# └── fib(3)  ← RECALCULATED AGAIN!
#     ├── fib(2)
#     │   ├── fib(1) → 1
#     │   └── fib(0) → 0
#     └── fib(1) → 1
```

### Climbing Stairs - Brute Force

```python
def climb_stairs_brute(n):
    """
    Time Complexity: O(2^n)
    Space Complexity: O(n)

    At each step, we have 2 choices (1 step or 2 steps).
    This creates a binary tree of possibilities.
    """
    if n <= 2:
        return n

    # Total ways = ways if we take 1 step + ways if we take 2 steps
    return climb_stairs_brute(n - 1) + climb_stairs_brute(n - 2)
```

### House Robber - Brute Force

```python
def rob_brute(nums, i=0):
    """
    Time Complexity: O(2^n)
    Space Complexity: O(n)

    At each house, we have 2 choices: rob it or skip it.
    """
    if i >= len(nums):
        return 0

    # Choice 1: Rob current house, skip next house
    rob_current = nums[i] + rob_brute(nums, i + 2)

    # Choice 2: Skip current house, can rob next house
    skip_current = rob_brute(nums, i + 1)

    return max(rob_current, skip_current)
```

## Optimized Solution

### Approach 1: Memoization (Top-Down DP)

Memoization = Recursion + Caching. Start from the original problem and break it down, storing results.

```python
def fib_memo(n, memo=None):
    """
    Time Complexity: O(n) - each fib(i) calculated once
    Space Complexity: O(n) - memo dictionary + recursion stack

    Key insight: Store results in a dictionary/array to avoid recalculation
    """
    if memo is None:
        memo = {}

    # Base cases
    if n <= 1:
        return n

    # Check if already computed
    if n in memo:
        return memo[n]

    # Compute and store
    memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]


def climb_stairs_memo(n, memo=None):
    """
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    if memo is None:
        memo = {}

    if n <= 2:
        return n

    if n in memo:
        return memo[n]

    memo[n] = climb_stairs_memo(n - 1, memo) + climb_stairs_memo(n - 2, memo)
    return memo[n]


def rob_memo(nums):
    """
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    memo = {}

    def dp(i):
        if i >= len(nums):
            return 0

        if i in memo:
            return memo[i]

        # Rob current or skip current
        memo[i] = max(nums[i] + dp(i + 2), dp(i + 1))
        return memo[i]

    return dp(0)
```

### Approach 2: Tabulation (Bottom-Up DP)

Tabulation = Iteration + Table. Start from the smallest subproblem and build up to the answer.

```python
def fib_tabulation(n):
    """
    Time Complexity: O(n)
    Space Complexity: O(n)

    Build solution from bottom-up: solve fib(0), then fib(1), then fib(2), etc.
    No recursion - just iteration!
    """
    if n <= 1:
        return n

    # Create DP table
    dp = [0] * (n + 1)

    # Base cases
    dp[0] = 0
    dp[1] = 1

    # Fill table bottom-up
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]

    return dp[n]


def climb_stairs_tabulation(n):
    """
    Time Complexity: O(n)
    Space Complexity: O(n)

    dp[i] represents: number of ways to reach step i
    """
    if n <= 2:
        return n

    dp = [0] * (n + 1)
    dp[1] = 1  # 1 way to reach step 1
    dp[2] = 2  # 2 ways to reach step 2 (1+1 or 2)

    for i in range(3, n + 1):
        # Ways to reach step i = ways to reach (i-1) + ways to reach (i-2)
        dp[i] = dp[i - 1] + dp[i - 2]

    return dp[n]


def rob_tabulation(nums):
    """
    Time Complexity: O(n)
    Space Complexity: O(n)

    dp[i] represents: max money we can rob from houses 0 to i
    """
    if not nums:
        return 0
    if len(nums) == 1:
        return nums[0]

    n = len(nums)
    dp = [0] * n

    # Base cases
    dp[0] = nums[0]  # Only one house, rob it
    dp[1] = max(nums[0], nums[1])  # Two houses, rob the richer one

    # Build up the solution
    for i in range(2, n):
        # Choice 1: rob house i + max from houses 0 to i-2
        # Choice 2: don't rob house i, take max from houses 0 to i-1
        dp[i] = max(nums[i] + dp[i - 2], dp[i - 1])

    return dp[n - 1]
```

### Approach 3: Space-Optimized DP

Often we only need the last 1-2 values, not the entire array!

```python
def fib_optimized(n):
    """
    Time Complexity: O(n)
    Space Complexity: O(1) - only storing 2 variables!

    Key insight: We only need the last 2 Fibonacci numbers to calculate the next one
    """
    if n <= 1:
        return n

    prev2 = 0  # fib(i-2)
    prev1 = 1  # fib(i-1)

    for i in range(2, n + 1):
        current = prev1 + prev2
        prev2 = prev1
        prev1 = current

    return prev1


def climb_stairs_optimized(n):
    """
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if n <= 2:
        return n

    two_steps_before = 1
    one_step_before = 2

    for i in range(3, n + 1):
        current = one_step_before + two_steps_before
        two_steps_before = one_step_before
        one_step_before = current

    return one_step_before


def rob_optimized(nums):
    """
    Time Complexity: O(n)
    Space Complexity: O(1)

    We only need to track: rob_prev2 and rob_prev1
    """
    if not nums:
        return 0
    if len(nums) == 1:
        return nums[0]

    prev2 = nums[0]  # dp[i-2]
    prev1 = max(nums[0], nums[1])  # dp[i-1]

    for i in range(2, len(nums)):
        current = max(nums[i] + prev2, prev1)
        prev2 = prev1
        prev1 = current

    return prev1
```

## Time & Space Complexity Analysis

| Approach | Time Complexity | Space Complexity | Notes |
|----------|----------------|------------------|-------|
| Brute Force (Recursion) | O(2^n) | O(n) | Exponential - unusable for n > 30 |
| Memoization (Top-Down) | O(n) | O(n) | Recursion stack + cache |
| Tabulation (Bottom-Up) | O(n) | O(n) | Iterative, cache only |
| Space-Optimized | O(n) | O(1) | Best for 1D DP |

### Why is Brute Force O(2^n)?
At each step, we make 2 recursive calls. Tree depth is n, so total calls ≈ 2^n.

### Why is DP O(n)?
With memoization/tabulation, we compute each subproblem exactly once. n subproblems × O(1) work per subproblem = O(n).

## Variations and Patterns

### 1. 1D DP (Linear DP)
Used when state depends on previous 1-2 elements.

**Examples**: Fibonacci, Climbing Stairs, House Robber, Decode Ways

**Template**:
```python
def linear_dp(arr):
    n = len(arr)
    dp = [0] * n

    # Initialize base cases
    dp[0] = base_case_0
    dp[1] = base_case_1

    # Fill the DP table
    for i in range(2, n):
        dp[i] = function_of(dp[i-1], dp[i-2], arr[i])

    return dp[n-1]
```

### 2. 2D DP (Grid DP)
Used for problems with two changing parameters.

**Examples**: Longest Common Subsequence, Edit Distance, Unique Paths, Knapsack

**Template**:
```python
def grid_dp(s1, s2):
    m, n = len(s1), len(s2)
    # dp[i][j] represents solution for s1[0:i] and s2[0:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Initialize base cases
    for i in range(m + 1):
        dp[i][0] = base_case_for_column_0
    for j in range(n + 1):
        dp[0][j] = base_case_for_row_0

    # Fill the DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = function_of(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])

    return dp[m][n]
```

**Example: Unique Paths**
```python
def unique_paths(m, n):
    """
    Robot in m x n grid. Can only move right or down.
    How many unique paths from top-left to bottom-right?

    Time: O(m * n), Space: O(m * n)
    """
    dp = [[0] * n for _ in range(m)]

    # Base case: first row and column have only 1 path
    for i in range(m):
        dp[i][0] = 1
    for j in range(n):
        dp[0][j] = 1

    # Fill the table
    for i in range(1, m):
        for j in range(1, n):
            # Paths to (i,j) = paths from above + paths from left
            dp[i][j] = dp[i-1][j] + dp[i][j-1]

    return dp[m-1][n-1]
```

### 3. Knapsack Pattern
Classic DP pattern for optimization with constraints.

**0/1 Knapsack**:
```python
def knapsack(weights, values, capacity):
    """
    Given n items with weights and values, and a knapsack of capacity W,
    find the maximum value we can carry.

    dp[i][w] = max value using items 0 to i with weight limit w

    Time: O(n * W), Space: O(n * W)
    """
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(capacity + 1):
            # Option 1: Don't take item i-1
            dp[i][w] = dp[i-1][w]

            # Option 2: Take item i-1 (if it fits)
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i][w],
                              dp[i-1][w - weights[i-1]] + values[i-1])

    return dp[n][capacity]
```

**Unbounded Knapsack** (can use items multiple times):
```python
def unbounded_knapsack(weights, values, capacity):
    """
    Can use each item unlimited times.

    Time: O(n * W), Space: O(W)
    """
    dp = [0] * (capacity + 1)

    for w in range(1, capacity + 1):
        for i in range(len(weights)):
            if weights[i] <= w:
                dp[w] = max(dp[w], dp[w - weights[i]] + values[i])

    return dp[capacity]
```

### 4. State Machine DP
When problem has distinct states with transitions.

**Example: Best Time to Buy and Sell Stock with Cooldown**
```python
def max_profit_with_cooldown(prices):
    """
    You can buy and sell stocks, but after selling, you must wait 1 day (cooldown).

    States:
    - hold: currently holding a stock
    - sold: just sold a stock (in cooldown)
    - rest: resting (not holding, not in cooldown)

    Time: O(n), Space: O(1)
    """
    if not prices:
        return 0

    # Initialize states
    hold = float('-inf')  # Max profit when holding stock
    sold = float('-inf')  # Max profit when just sold (cooldown)
    rest = 0              # Max profit when resting

    for price in prices:
        prev_hold = hold
        prev_sold = sold
        prev_rest = rest

        # To hold today: either held yesterday, or buy today
        hold = max(prev_hold, prev_rest - price)

        # To be in cooldown today: must have sold today
        sold = prev_hold + price

        # To rest today: either rested yesterday or cooldown ended
        rest = max(prev_rest, prev_sold)

    # Max profit is when we're not holding stock
    return max(sold, rest)
```

### 5. String DP
Problems involving subsequences, substrings, or string transformations.

**Example: Longest Palindromic Substring**
```python
def longest_palindrome(s):
    """
    dp[i][j] = True if s[i:j+1] is a palindrome

    Time: O(n^2), Space: O(n^2)
    """
    n = len(s)
    if n < 2:
        return s

    dp = [[False] * n for _ in range(n)]
    start, max_len = 0, 1

    # Every single character is a palindrome
    for i in range(n):
        dp[i][i] = True

    # Check for length 2
    for i in range(n - 1):
        if s[i] == s[i + 1]:
            dp[i][i + 1] = True
            start = i
            max_len = 2

    # Check for lengths greater than 2
    for length in range(3, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1

            # s[i:j+1] is palindrome if:
            # 1. s[i] == s[j]
            # 2. s[i+1:j] is palindrome
            if s[i] == s[j] and dp[i + 1][j - 1]:
                dp[i][j] = True
                start = i
                max_len = length

    return s[start:start + max_len]
```

## Pro Tips for Senior Engineers

### 1. Identifying DP Problems
Ask yourself:
- **Can I break this into smaller subproblems?** (Optimal substructure)
- **Will I solve the same subproblem multiple times?** (Overlapping subproblems)
- **Does the problem ask for optimization (min/max) or counting?**

Keywords that scream DP:
- "Maximum/Minimum"
- "Count number of ways"
- "Is it possible to..."
- "Longest/Shortest"
- "All possible ways"

### 2. Choosing Between Memoization and Tabulation

**Use Memoization when**:
- Not all subproblems need to be solved
- Problem is naturally recursive
- You want to code quickly (easier to implement)

**Use Tabulation when**:
- All subproblems must be solved anyway
- You want to avoid recursion stack overflow
- You need to optimize space (easier to see what to discard)
- Performance is critical (iteration is slightly faster than recursion)

### 3. Space Optimization Tricks

**For 1D DP**:
```python
# If dp[i] only depends on dp[i-1] and dp[i-2]
# Replace array with 2 variables
prev2, prev1 = dp[i-2], dp[i-1]
current = f(prev1, prev2)
```

**For 2D DP**:
```python
# If dp[i][j] only depends on current row and previous row
# Replace 2D array with 2 1D arrays (or even 1 array with careful updates)
prev_row = [0] * n
curr_row = [0] * n

for i in range(m):
    for j in range(n):
        curr_row[j] = f(prev_row[j], curr_row[j-1])
    prev_row = curr_row[:]  # Copy curr_row to prev_row
```

### 4. The DP Process (Step-by-Step)

1. **Identify if it's DP**: Check for optimal substructure and overlapping subproblems
2. **Define the state**: What parameters uniquely identify a subproblem?
   - `dp[i]` - position i
   - `dp[i][j]` - two positions or two different parameters
   - `dp[i][j][k]` - three parameters (rare)
3. **Write the recurrence relation**: How does dp[i] relate to smaller subproblems?
4. **Identify base cases**: What are the simplest subproblems we know the answer to?
5. **Implement**: Start with memoization (easier), then optimize to tabulation
6. **Optimize space**: Can we reduce space complexity?

### 5. When NOT to Use DP

- **Greedy works**: If a greedy approach gives optimal solution, it's simpler
  - Example: Activity Selection, Huffman Coding
- **No overlapping subproblems**: Use Divide & Conquer instead
  - Example: Merge Sort, Quick Sort
- **Online algorithms**: DP typically requires all data upfront
- **Space is critical**: DP trades space for time

### 6. Debugging DP Solutions

```python
# Add print statements to see DP table
def debug_dp(n):
    dp = [0] * (n + 1)
    dp[0], dp[1] = 0, 1

    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
        print(f"dp[{i}] = {dp[i]}")  # See how table fills

    return dp[n]

# Test with small inputs first
# Verify base cases manually
# Check if recurrence relation matches your logic
```

## Problem Recognition: How to Spot DP Patterns

### Pattern 1: Min/Max Path to Target
**Signals**: "minimum cost", "maximum profit", "shortest path", "longest path"

**Examples**:
- Minimum Path Sum in Grid
- Coin Change (minimum coins)
- Maximum Subarray

**Recurrence Template**:
```python
dp[i] = min/max(dp[i-1], dp[i-2], ...) + cost[i]
```

### Pattern 2: Count Ways
**Signals**: "how many ways", "number of distinct ways", "count paths"

**Examples**:
- Climbing Stairs
- Unique Paths
- Decode Ways

**Recurrence Template**:
```python
dp[i] = dp[i-1] + dp[i-2] + ...
```

### Pattern 3: True/False Possibility
**Signals**: "is it possible", "can we achieve", "true or false"

**Examples**:
- Partition Equal Subset Sum
- Word Break
- Regular Expression Matching

**Recurrence Template**:
```python
dp[i] = dp[i-1] OR dp[i-2] OR ...
```

### Pattern 4: Subsequence/Substring
**Signals**: "longest/shortest subsequence", "common substring", "palindrome"

**Examples**:
- Longest Common Subsequence
- Longest Increasing Subsequence
- Palindromic Substrings

**Recurrence Template**:
```python
dp[i][j] = function_of(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
```

## Practice Problems (Beginner to Advanced)

### Easy (Foundation)
1. **Climbing Stairs** (LeetCode 70)
   - Classic 1D DP introduction
   - Pattern: Count ways

2. **House Robber** (LeetCode 198)
   - 1D DP with constraints
   - Pattern: Max value with non-adjacent selection

3. **Min Cost Climbing Stairs** (LeetCode 746)
   - 1D DP with cost array
   - Pattern: Min cost to target

### Medium (Core Skills)
4. **Coin Change** (LeetCode 322)
   - Unbounded knapsack variant
   - Pattern: Min count to reach target

5. **Longest Increasing Subsequence** (LeetCode 300)
   - Classic DP problem
   - Pattern: Longest subsequence with condition

6. **Unique Paths** (LeetCode 62)
   - 2D DP grid traversal
   - Pattern: Count paths in grid

7. **Longest Common Subsequence** (LeetCode 1143)
   - 2D DP on strings
   - Pattern: Matching between two sequences

8. **Word Break** (LeetCode 139)
   - String DP with dictionary
   - Pattern: True/False possibility

9. **House Robber II** (LeetCode 213)
   - Circular array variant
   - Pattern: Max value with circular constraint

### Hard (Interview Ready)
10. **Edit Distance** (LeetCode 72)
    - Classic 2D DP
    - Pattern: Transform one string to another

11. **Burst Balloons** (LeetCode 312)
    - Interval DP
    - Pattern: Optimal substructure with intervals

12. **Best Time to Buy and Sell Stock IV** (LeetCode 188)
    - State machine DP with transactions
    - Pattern: Max profit with k transactions

13. **Regular Expression Matching** (LeetCode 10)
    - Complex string DP
    - Pattern: True/False matching

### Progression Tip
Master Easy → Medium → Hard in order. Don't jump ahead! Each level builds on previous patterns.

## Common Mistakes and Pitfalls

### Mistake 1: Not Identifying Base Cases Properly
```python
# ❌ WRONG: Missing base case
def climb_stairs(n):
    dp = [0] * n  # What if n = 1? IndexError!
    dp[0] = 1
    dp[1] = 2
    for i in range(2, n):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n-1]

# ✅ CORRECT: Handle edge cases
def climb_stairs(n):
    if n <= 2:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    dp[2] = 2
    for i in range(3, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
```

### Mistake 2: Wrong Array Size
```python
# ❌ WRONG: Array too small
dp = [0] * n  # If you need dp[n], this will cause IndexError

# ✅ CORRECT: Allocate enough space
dp = [0] * (n + 1)  # Now dp[n] is accessible
```

### Mistake 3: Confusing Memoization with Global State
```python
# ❌ WRONG: memo persists across function calls
memo = {}
def fib(n):
    if n <= 1:
        return n
    if n in memo:
        return memo[n]
    memo[n] = fib(n-1) + fib(n-2)
    return memo[n]

# ✅ CORRECT: Pass memo as parameter or use default argument
def fib(n, memo=None):
    if memo is None:
        memo = {}
    if n <= 1:
        return n
    if n in memo:
        return memo[n]
    memo[n] = fib(n-1, memo) + fib(n-2, memo)
    return memo[n]
```

### Mistake 4: Off-by-One Errors in 2D DP
```python
# ❌ WRONG: Indexing confusion
for i in range(m):
    for j in range(n):
        dp[i][j] = dp[i-1][j] + dp[i][j-1]  # What about i=0, j=0?

# ✅ CORRECT: Proper initialization and iteration
dp = [[0] * (n + 1) for _ in range(m + 1)]
for i in range(1, m + 1):
    for j in range(1, n + 1):
        dp[i][j] = dp[i-1][j] + dp[i][j-1]
```

### Mistake 5: Not Optimizing Space When Possible
```python
# ⚠️ WORKS but wasteful for large n
def fib(n):
    dp = [0] * (n + 1)  # O(n) space
    dp[0], dp[1] = 0, 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]

# ✅ BETTER: Only store what you need
def fib(n):
    if n <= 1:
        return n
    prev2, prev1 = 0, 1  # O(1) space
    for i in range(2, n + 1):
        current = prev1 + prev2
        prev2, prev1 = prev1, current
    return prev1
```

### Mistake 6: Forgetting to Return the Right Value
```python
# ❌ WRONG: Returning wrong index
def climb_stairs(n):
    dp = [0] * (n + 1)
    dp[0] = 1
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n-1]  # Should be dp[n]!

# ✅ CORRECT
return dp[n]
```

### Mistake 7: Modifying Input Array When You Need It Later
```python
# ❌ RISKY: Using input array as DP array
def rob(nums):
    for i in range(2, len(nums)):
        nums[i] = max(nums[i] + nums[i-2], nums[i-1])
    return nums[-1]  # Modifies input!

# ✅ BETTER: Use separate DP array
def rob(nums):
    if not nums:
        return 0
    if len(nums) == 1:
        return nums[0]

    dp = [0] * len(nums)
    dp[0] = nums[0]
    dp[1] = max(nums[0], nums[1])

    for i in range(2, len(nums)):
        dp[i] = max(nums[i] + dp[i-2], dp[i-1])
    return dp[-1]
```

## Key Takeaways

1. **DP = Recursion + Memoization**: Start by finding the recursive solution, then add caching
2. **Two approaches**: Top-down (memoization) or bottom-up (tabulation) - both have O(n) time
3. **Space optimization**: Often you can reduce O(n) space to O(1) by keeping only last few values
4. **Practice pattern recognition**: Learn to identify DP signals in problem statements
5. **Master the fundamentals**: Fibonacci, Climbing Stairs, House Robber are your foundation
6. **Build up complexity**: 1D DP → 2D DP → Advanced patterns

Dynamic Programming transforms exponential problems into polynomial ones by remembering solutions. It's not magic - it's just smart bookkeeping!
