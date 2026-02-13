# Backtracking Pattern

## What is Backtracking?

### Explain Like I'm 5 👶

Imagine you're in a maze trying to find the exit. You walk down a path, and if you hit a dead end, you go back to where you made your last choice and try a different path. You keep doing this - trying paths and backing up when they don't work - until you find the exit or try every possible path.

That's backtracking! It's like saying "Let me try this... oops, that didn't work. Let me go back and try something else."

### Technical Definition

Backtracking is an algorithmic technique for solving problems by **incrementally building candidates** to solutions and **abandoning a candidate** ("backtracking") as soon as it determines that the candidate cannot lead to a valid solution.

It's essentially a **depth-first search (DFS)** with the added property that we undo our choices when we need to explore different possibilities. The key insight is:
- Make a choice
- Explore the consequences
- Undo the choice (backtrack)
- Make a different choice

## Real-World Analogy 🌍

### Solving a Sudoku Puzzle

When you solve a Sudoku puzzle:

1. **Make a choice**: You write a number in an empty cell (say, put "5" in a cell)
2. **Explore**: You continue filling other cells based on this choice
3. **Hit a problem**: You realize later that this choice makes it impossible to complete the puzzle
4. **Backtrack**: You erase the "5" and try a different number
5. **Repeat**: Keep trying until you find the right combination

### Trying Keys in Locks

Imagine you have 10 keys and need to open 3 different locks:

- You try different combinations of keys
- If a combination doesn't work, you "backtrack" by removing keys you've tried
- You systematically try every possible combination until you find what works

## When to Use Backtracking ⚡

Use backtracking when the problem asks you to:

### Clear Signals:
- ✅ **"Find ALL possible solutions"** - Not just one solution, but every combination
- ✅ **"Generate all permutations"** - Every possible ordering
- ✅ **"Generate all combinations"** - Every possible selection
- ✅ **"Generate all subsets"** - Every possible grouping including empty set
- ✅ **Constraint satisfaction problems** - Where you need to satisfy certain rules (N-Queens, Sudoku)
- ✅ **"Find all ways to..."** - Any problem asking for exhaustive enumeration

### Keywords to Watch For:
- "all possible"
- "generate all"
- "find all ways"
- "every combination"
- "every permutation"
- "all subsets"
- "all paths"

### Problem Characteristics:
- You need to explore **all possibilities**
- You can **prune** invalid paths early
- The solution space forms a **tree structure**
- You can build solutions **incrementally**

## The Problem: Generate All Subsets 📋

**Problem Statement:**

Given an array of unique integers `nums`, return all possible subsets (the power set). The solution set must not contain duplicate subsets.

**Example:**
```
Input: nums = [1, 2, 3]

Output:
[
  [],           # Empty subset
  [1],          # Single elements
  [2],
  [3],
  [1, 2],       # Two elements
  [1, 3],
  [2, 3],
  [1, 2, 3]     # All elements
]
```

**Explanation:**

For an array of size n, there are 2^n possible subsets because for each element, we have 2 choices: include it or exclude it.

For `[1, 2, 3]`:
- For `1`: include or exclude → 2 choices
- For `2`: include or exclude → 2 choices
- For `3`: include or exclude → 2 choices
- Total: 2 × 2 × 2 = 8 subsets

## Brute Force Approach 💪

One way to generate all subsets is using **bit manipulation**. We can use numbers from 0 to 2^n - 1, where each bit represents whether to include an element.

```python
def subsets_bruteforce(nums):
    """
    Generate all subsets using bit manipulation.

    For each number from 0 to 2^n - 1, use its binary representation
    to decide which elements to include.

    Example: nums = [1, 2, 3]
    Number 5 in binary is 101
    - Bit 0 (rightmost) is 1: include nums[0] = 1
    - Bit 1 is 0: exclude nums[1] = 2
    - Bit 2 is 1: include nums[2] = 3
    - Result: [1, 3]
    """
    n = len(nums)
    result = []

    # Generate all numbers from 0 to 2^n - 1
    for i in range(2 ** n):
        subset = []

        # Check each bit in the number
        for j in range(n):
            # If j-th bit is set, include nums[j]
            if i & (1 << j):
                subset.append(nums[j])

        result.append(subset)

    return result

# Example usage
nums = [1, 2, 3]
print(subsets_bruteforce(nums))
# Output: [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]
```

**How it works:**
- For `nums = [1, 2, 3]`, n = 3, so we iterate from 0 to 7
- Number 0 (binary: 000) → []
- Number 1 (binary: 001) → [1]
- Number 2 (binary: 010) → [2]
- Number 3 (binary: 011) → [1, 2]
- Number 5 (binary: 101) → [1, 3]
- And so on...

**Limitations:**
- Not intuitive or extensible
- Doesn't work well when you need to add constraints
- Hard to modify for permutations or combinations with specific rules

## Optimized Solution: Backtracking Template 🚀

The backtracking approach is more intuitive and flexible. We build subsets incrementally by making choices.

```python
def subsets_backtracking(nums):
    """
    Generate all subsets using backtracking.

    Time Complexity: O(n * 2^n)
    - 2^n subsets to generate
    - Each subset takes O(n) time to copy

    Space Complexity: O(n)
    - Recursion depth is O(n)
    - Not counting output space
    """
    result = []
    current_subset = []

    def backtrack(start_index):
        """
        Backtracking helper function.

        Args:
            start_index: Index to start exploring from (prevents duplicates)

        The key insight:
        - At each step, we can either INCLUDE or EXCLUDE the current element
        - We explore both choices recursively
        - We backtrack by removing the element after exploring
        """

        # BASE CASE: We've made decisions for all elements
        # Add the current subset to results
        # Important: Create a copy! Don't append the reference
        result.append(current_subset[:])  # or list(current_subset)

        # RECURSIVE CASE: Try including each remaining element
        for i in range(start_index, len(nums)):
            # MAKE A CHOICE: Include nums[i] in current subset
            current_subset.append(nums[i])

            # EXPLORE: Recursively build subsets starting from next index
            # We use i+1 to avoid using the same element twice
            backtrack(i + 1)

            # UNDO THE CHOICE: Remove nums[i] to try other possibilities
            # This is the "backtracking" step!
            current_subset.pop()

    # Start backtracking from index 0
    backtrack(0)
    return result


# Example usage with detailed trace
nums = [1, 2, 3]
print(subsets_backtracking(nums))
```

### Step-by-Step Execution Trace

Let's trace through `nums = [1, 2, 3]`:

```
backtrack(0), current = []
├─ Add [] to result                          → [[], ...]
├─ Choose 1, current = [1]
│  ├─ backtrack(1), current = [1]
│  │  ├─ Add [1] to result                   → [[], [1], ...]
│  │  ├─ Choose 2, current = [1, 2]
│  │  │  ├─ backtrack(2), current = [1, 2]
│  │  │  │  ├─ Add [1, 2] to result          → [[], [1], [1,2], ...]
│  │  │  │  ├─ Choose 3, current = [1, 2, 3]
│  │  │  │  │  ├─ backtrack(3)
│  │  │  │  │  │  └─ Add [1, 2, 3]           → [[], [1], [1,2], [1,2,3], ...]
│  │  │  │  │  └─ Undo 3, current = [1, 2]
│  │  │  └─ Undo 2, current = [1]
│  │  ├─ Choose 3, current = [1, 3]
│  │  │  ├─ backtrack(3), current = [1, 3]
│  │  │  │  └─ Add [1, 3]                    → [..., [1,3], ...]
│  │  └─ Undo 3, current = [1]
│  └─ Undo 1, current = []
├─ Choose 2, current = [2]
│  ├─ backtrack(2), current = [2]
│  │  ├─ Add [2] to result                   → [..., [2], ...]
│  │  ├─ Choose 3, current = [2, 3]
│  │  │  ├─ backtrack(3)
│  │  │  │  └─ Add [2, 3]                    → [..., [2,3], ...]
│  │  └─ Undo 3, current = [2]
│  └─ Undo 2, current = []
├─ Choose 3, current = [3]
│  ├─ backtrack(3), current = [3]
│  │  └─ Add [3] to result                   → [..., [3]]
│  └─ Undo 3, current = []

Final result: [[], [1], [1,2], [1,2,3], [1,3], [2], [2,3], [3]]
```

### The Universal Backtracking Template

```python
def backtrack_template(choices, constraints):
    """
    Universal backtracking template.
    """
    result = []
    current_path = []

    def backtrack(state):
        # BASE CASE: Solution is complete
        if is_solution(state):
            result.append(current_path[:])  # Save a copy
            return

        # RECURSIVE CASE: Try all possible choices
        for choice in get_choices(state):
            # CONSTRAINT CHECK: Is this choice valid?
            if is_valid(choice, current_path, constraints):
                # MAKE CHOICE: Add to current path
                current_path.append(choice)

                # EXPLORE: Recurse with updated state
                backtrack(get_next_state(state, choice))

                # UNDO CHOICE: Backtrack!
                current_path.pop()

    backtrack(initial_state)
    return result
```

## Time & Space Complexity Analysis ⏱️

### Time Complexity: O(n × 2^n)

**Why 2^n?**
- For each element, we have 2 choices: include it or exclude it
- With n elements, total combinations = 2 × 2 × 2 × ... (n times) = 2^n

**Why the extra n?**
- Each subset needs to be copied to the result
- Copying a subset of size k takes O(k) time
- Average subset size is n/2
- Total: O(2^n × n/2) = O(n × 2^n)

**Detailed breakdown:**
```
Level 0: [] → 1 subset                    = 2^0 = 1
Level 1: [1], [2], [3] → 3 subsets        = 2^1 + ... (multiple paths)
Level 2: [1,2], [1,3], [2,3] → 3 subsets
Level 3: [1,2,3] → 1 subset

Total operations:
- Number of subsets: 2^n
- Copy operation per subset: O(n) average
- Total: O(n × 2^n)
```

### Space Complexity: O(n)

**Recursion call stack:**
- Maximum depth of recursion is n (when we include all elements)
- Each recursive call adds a frame to the call stack
- Space: O(n)

**Current path storage:**
- At most n elements in current_subset
- Space: O(n)

**Total: O(n)** (not counting output space)

**Note:** If we count the output space, it's O(n × 2^n) because we store 2^n subsets, each averaging n/2 elements.

### Comparison with Other Patterns

| Pattern | Time | Space | Use Case |
|---------|------|-------|----------|
| Backtracking (Subsets) | O(n × 2^n) | O(n) | Generate all combinations |
| Backtracking (Permutations) | O(n × n!) | O(n) | Generate all orderings |
| Dynamic Programming | O(n²) - O(n³) | O(n) - O(n²) | Optimization problems |
| Greedy | O(n log n) | O(1) | Local optimal → global |

## Variations & Common Problems 🎯

### 1. Subsets (Power Set)

**Problem:** Generate all possible subsets.

```python
def subsets(nums):
    """Generate all subsets including empty set."""
    result = []

    def backtrack(start, path):
        result.append(path[:])

        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
    return result
```

### 2. Subsets II (With Duplicates)

**Problem:** Generate all subsets when input contains duplicates.

```python
def subsetsWithDup(nums):
    """
    Generate subsets avoiding duplicate subsets.

    Key insight: Sort first, then skip duplicates at the same level.
    """
    result = []
    nums.sort()  # CRITICAL: Must sort to group duplicates

    def backtrack(start, path):
        result.append(path[:])

        for i in range(start, len(nums)):
            # Skip duplicates at the SAME LEVEL
            # i > start ensures we only skip at same recursion level
            # not when going deeper
            if i > start and nums[i] == nums[i - 1]:
                continue

            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
    return result

# Example
nums = [1, 2, 2]
print(subsetsWithDup(nums))
# Output: [[], [1], [1,2], [1,2,2], [2], [2,2]]
# Note: [1,2] appears only once, not twice
```

### 3. Permutations

**Problem:** Generate all possible orderings.

```python
def permute(nums):
    """
    Generate all permutations.

    Difference from subsets:
    - We use ALL elements in each permutation
    - Order matters: [1,2,3] ≠ [3,2,1]
    - Use a 'used' array to track what's been used
    """
    result = []

    def backtrack(path):
        # BASE CASE: Used all numbers
        if len(path) == len(nums):
            result.append(path[:])
            return

        # Try each number
        for num in nums:
            # Skip if already used in current path
            if num in path:
                continue

            path.append(num)
            backtrack(path)
            path.pop()

    backtrack([])
    return result

# More efficient version using index tracking
def permute_efficient(nums):
    result = []
    used = [False] * len(nums)

    def backtrack(path):
        if len(path) == len(nums):
            result.append(path[:])
            return

        for i in range(len(nums)):
            if used[i]:
                continue

            used[i] = True
            path.append(nums[i])
            backtrack(path)
            path.pop()
            used[i] = False

    backtrack([])
    return result
```

### 4. Combinations

**Problem:** Choose k elements from n elements.

```python
def combine(n, k):
    """
    Generate all combinations of k numbers from 1 to n.

    Example: n=4, k=2
    Output: [[1,2], [1,3], [1,4], [2,3], [2,4], [3,4]]
    """
    result = []

    def backtrack(start, path):
        # BASE CASE: We've selected k numbers
        if len(path) == k:
            result.append(path[:])
            return

        # OPTIMIZATION: Pruning
        # If we need k elements and have selected len(path),
        # we need k - len(path) more elements
        # So we can only start from positions where enough elements remain
        need = k - len(path)
        remain = n - start + 1
        available = remain

        for i in range(start, n + 1):
            # Pruning: Not enough elements left
            if available < need:
                break

            path.append(i)
            backtrack(i + 1, path)
            path.pop()

            available -= 1

    backtrack(1, [])
    return result
```

### 5. N-Queens

**Problem:** Place N queens on an N×N chessboard so no two queens attack each other.

```python
def solveNQueens(n):
    """
    Classic backtracking problem with constraint checking.

    Constraints:
    - One queen per row
    - One queen per column
    - One queen per diagonal
    """
    result = []
    board = [['.'] * n for _ in range(n)]

    # Track occupied columns and diagonals
    cols = set()
    diag1 = set()  # row - col is constant on these diagonals
    diag2 = set()  # row + col is constant on these diagonals

    def backtrack(row):
        # BASE CASE: Placed queen in all rows
        if row == n:
            result.append([''.join(row) for row in board])
            return

        # Try placing queen in each column of current row
        for col in range(n):
            # CHECK CONSTRAINTS
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue

            # MAKE CHOICE
            board[row][col] = 'Q'
            cols.add(col)
            diag1.add(row - col)
            diag2.add(row + col)

            # EXPLORE
            backtrack(row + 1)

            # UNDO CHOICE
            board[row][col] = '.'
            cols.remove(col)
            diag1.remove(row - col)
            diag2.remove(row + col)

    backtrack(0)
    return result
```

### 6. Word Search

**Problem:** Find if a word exists in a 2D board.

```python
def exist(board, word):
    """
    Search for word in board using backtracking.

    Can move up, down, left, right.
    Can't use same cell twice.
    """
    rows, cols = len(board), len(board[0])

    def backtrack(r, c, index):
        # BASE CASE: Found all characters
        if index == len(word):
            return True

        # BOUNDARY & CONSTRAINT CHECKS
        if (r < 0 or r >= rows or c < 0 or c >= cols or
            board[r][c] != word[index] or board[r][c] == '#'):
            return False

        # MAKE CHOICE: Mark as visited
        temp = board[r][c]
        board[r][c] = '#'

        # EXPLORE: Try all 4 directions
        found = (backtrack(r + 1, c, index + 1) or
                 backtrack(r - 1, c, index + 1) or
                 backtrack(r, c + 1, index + 1) or
                 backtrack(r, c - 1, index + 1))

        # UNDO CHOICE: Restore cell
        board[r][c] = temp

        return found

    # Try starting from each cell
    for r in range(rows):
        for c in range(cols):
            if backtrack(r, c, 0):
                return True

    return False
```

### 7. Palindrome Partitioning

**Problem:** Partition string into substrings where each is a palindrome.

```python
def partition(s):
    """
    Find all ways to partition s into palindromes.

    Example: s = "aab"
    Output: [["a","a","b"], ["aa","b"]]
    """
    result = []

    def is_palindrome(string):
        return string == string[::-1]

    def backtrack(start, path):
        # BASE CASE: Reached end of string
        if start == len(s):
            result.append(path[:])
            return

        # Try all possible substrings starting at 'start'
        for end in range(start + 1, len(s) + 1):
            substring = s[start:end]

            # Only continue if current substring is palindrome
            if is_palindrome(substring):
                path.append(substring)
                backtrack(end, path)
                path.pop()

    backtrack(0, [])
    return result
```

## Pro Tips for Senior Engineers 🎓

### 1. Pruning: Cut Branches Early

**Bad approach:** Generate all possibilities, then filter

```python
# DON'T DO THIS
def combinations_bad(n, k):
    result = []

    def backtrack(start, path):
        # Generate everything, filter later
        if start > n:
            if len(path) == k:  # Check at the end
                result.append(path[:])
            return

        backtrack(start + 1, path + [start])
        backtrack(start + 1, path)

    backtrack(1, [])
    return result
```

**Good approach:** Prune invalid paths immediately

```python
# DO THIS
def combinations_good(n, k):
    result = []

    def backtrack(start, path):
        # PRUNE: Not enough elements left
        if len(path) + (n - start + 1) < k:
            return

        # BASE CASE: Found valid combination
        if len(path) == k:
            result.append(path[:])
            return

        for i in range(start, n + 1):
            backtrack(i + 1, path + [i])

    backtrack(1, [])
    return result
```

### 2. Avoid Duplicates in Results

**Key technique:** Sort first, then skip duplicates at same level

```python
def subsetsWithDup(nums):
    nums.sort()  # Sort to group duplicates
    result = []

    def backtrack(start, path):
        result.append(path[:])

        for i in range(start, len(nums)):
            # CRITICAL: i > start, not i > 0
            # Skip duplicates at SAME recursion level only
            if i > start and nums[i] == nums[i-1]:
                continue

            backtrack(i + 1, path + [nums[i]])

    backtrack(0, [])
    return result
```

### 3. State Management: Copy vs. Reference

**Wrong:** Appending reference

```python
def subsets_wrong(nums):
    result = []
    path = []

    def backtrack(start):
        result.append(path)  # WRONG! Appends reference

        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1)
            path.pop()

    backtrack(0)
    return result
# All subsets will be empty! They all reference the same list
```

**Right:** Creating copies

```python
def subsets_right(nums):
    result = []
    path = []

    def backtrack(start):
        result.append(path[:])  # CORRECT! Creates a copy
        # or result.append(list(path))

        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1)
            path.pop()

    backtrack(0)
    return result
```

### 4. When NOT to Use Backtracking

**Don't use backtracking when:**

1. **You only need ONE solution, not all solutions**
   - Use BFS/DFS instead
   - Example: Finding a path in a maze (just need one path)

2. **The problem has overlapping subproblems**
   - Use Dynamic Programming instead
   - Example: Fibonacci, longest common subsequence

3. **You need the optimal solution, not all solutions**
   - Use DP or Greedy instead
   - Example: Shortest path, minimum cost

4. **The search space is too large without good pruning**
   - Backtracking without pruning can be slower than iterative approaches
   - Example: If you need subsets but can't prune effectively

### 5. Optimization Techniques

**a) Use iterators instead of generating lists**

```python
# Less memory efficient
for choice in list(range(start, n)):
    backtrack(choice)

# More memory efficient
for choice in range(start, n):
    backtrack(choice)
```

**b) Use sets for O(1) membership checking**

```python
# Slow: O(n) lookup
if num in path:  # path is a list
    continue

# Fast: O(1) lookup
if num in used:  # used is a set
    continue
```

**c) Memoization for repeated states**

```python
def backtrack(state):
    if state in memo:
        return memo[state]

    # ... backtracking logic ...

    memo[state] = result
    return result
```

### 6. The "Return Early" Optimization

```python
def exist(board, word):
    """Return immediately when solution is found."""

    def backtrack(r, c, index):
        if index == len(word):
            return True  # Found it! Return immediately

        # ... validation ...

        temp = board[r][c]
        board[r][c] = '#'

        # Return True immediately if any path succeeds
        if backtrack(r+1, c, index+1): return True
        if backtrack(r-1, c, index+1): return True
        if backtrack(r, c+1, index+1): return True
        if backtrack(r, c-1, index+1): return True

        board[r][c] = temp
        return False

    for r in range(len(board)):
        for c in range(len(board[0])):
            if backtrack(r, c, 0):
                return True  # Don't keep searching!
    return False
```

## Problem Recognition: How to Identify Backtracking Problems 🔍

### Keywords That Scream "Backtracking":

1. **"All possible"** - Not just one, but every solution
2. **"Generate all"** - Exhaustive generation
3. **"Find all ways"** - Multiple valid solutions
4. **"Every combination/permutation"** - Complete enumeration
5. **"Return all solutions"** - Comprehensive search

### Question Patterns:

| If the problem says... | It's likely... | Example |
|------------------------|----------------|---------|
| "All subsets" | Backtracking | Power set problem |
| "All permutations" | Backtracking | String permutations |
| "All combinations" | Backtracking | Combination sum |
| "Generate all valid..." | Backtracking | Generate parentheses |
| "Find all solutions" | Backtracking | N-Queens |
| "All possible ways" | Backtracking | Word break II |
| "Partition into..." | Backtracking | Palindrome partition |

### Decision Tree:

```
Does the problem ask for ALL solutions?
├─ NO → Not backtracking (use DFS/BFS/DP/Greedy)
└─ YES
   ├─ Can you build solutions incrementally?
   │  ├─ YES
   │  │  └─ Can you prune invalid paths early?
   │  │     ├─ YES → BACKTRACKING! ✓
   │  │     └─ NO → Consider iterative generation
   │  └─ NO → Consider other approaches
   └─ Is it a constraint satisfaction problem?
      └─ YES → BACKTRACKING! ✓ (Sudoku, N-Queens)
```

## Practice Problems (Ordered by Difficulty) 📚

### Easy (Start Here)

1. **Subsets (LeetCode 78)**
   - Classic introduction to backtracking
   - Generate all subsets of a set
   - Time: O(n × 2^n)

2. **Binary Watch (LeetCode 401)**
   - Return all possible times with n LEDs on
   - Good for understanding choices
   - Time: O(1) - fixed number of LEDs

### Medium (Build Your Skills)

3. **Permutations (LeetCode 46)**
   - Generate all permutations
   - Learn about "used" tracking
   - Time: O(n × n!)

4. **Combination Sum (LeetCode 39)**
   - Find combinations that sum to target
   - Elements can be reused
   - Learn about pruning
   - Time: O(n^target)

5. **Subsets II (LeetCode 90)**
   - Subsets with duplicates
   - Master duplicate handling
   - Time: O(n × 2^n)

6. **Palindrome Partitioning (LeetCode 131)**
   - Partition string into palindromes
   - Combine backtracking with palindrome checking
   - Time: O(n × 2^n)

7. **Generate Parentheses (LeetCode 22)**
   - Generate all valid parentheses combinations
   - Great for constraint-based backtracking
   - Time: O(4^n / √n) - Catalan number

### Hard (Master the Pattern)

8. **N-Queens (LeetCode 51)**
   - Place N queens on N×N board
   - Classic constraint satisfaction
   - Time: O(n!)

9. **Word Search II (LeetCode 212)**
   - Find all words in a board
   - Combine backtracking with Trie
   - Time: O(m × n × 4^L) where L is word length

10. **Sudoku Solver (LeetCode 37)**
    - Solve a Sudoku puzzle
    - Complex constraint checking
    - Time: O(9^(n×n)) for n×n board

## Common Mistakes & How to Avoid Them ❌

### Mistake 1: Not Creating a Copy of the Path

```python
# WRONG
result.append(path)  # Appends reference, will be empty later

# RIGHT
result.append(path[:])  # Creates a copy
result.append(list(path))  # Also creates a copy
```

**Why it matters:** All your results will point to the same list, which will be empty at the end.

### Mistake 2: Forgetting to Backtrack (Undo Changes)

```python
# WRONG
def backtrack(path):
    path.append(choice)
    backtrack(path)
    # Forgot to remove choice!

# RIGHT
def backtrack(path):
    path.append(choice)
    backtrack(path)
    path.pop()  # Must undo the choice
```

**Why it matters:** State leaks into other branches, producing incorrect results.

### Mistake 3: Not Handling Duplicates Correctly

```python
# WRONG - Checking i > 0 skips duplicates everywhere
if i > 0 and nums[i] == nums[i-1]:
    continue

# RIGHT - Only skip duplicates at same recursion level
if i > start and nums[i] == nums[i-1]:
    continue
```

**Why it matters:** `i > start` ensures we skip duplicates only at the same level, not when going deeper.

### Mistake 4: Modifying Input and Not Restoring

```python
# WRONG
board[r][c] = '#'  # Mark as visited
backtrack(r, c)
# Forgot to restore!

# RIGHT
temp = board[r][c]
board[r][c] = '#'
backtrack(r, c)
board[r][c] = temp  # Restore original value
```

### Mistake 5: Not Pruning When Possible

```python
# WRONG - Generates all paths then filters
def backtrack(path):
    if len(path) > k:  # Too late to prune!
        return

    # ... continue backtracking ...

# RIGHT - Prunes early
def backtrack(path):
    if len(path) == k:  # Stop at right point
        result.append(path[:])
        return

    # Only continue if we haven't reached k yet
```

### Mistake 6: Using Wrong Base Case

```python
# WRONG - Checks condition after recursion
def backtrack(start):
    for i in range(start, n):
        path.append(i)
        backtrack(i + 1)
        path.pop()

    if len(path) == k:  # Too late!
        result.append(path[:])

# RIGHT - Checks at start of function
def backtrack(start):
    if len(path) == k:
        result.append(path[:])
        return

    for i in range(start, n):
        path.append(i)
        backtrack(i + 1)
        path.pop()
```

### Mistake 7: Reusing Same Element When You Shouldn't

```python
# WRONG - Can reuse same element
for i in range(len(nums)):
    path.append(nums[i])
    backtrack(i)  # Should be i+1 for combinations!
    path.pop()

# RIGHT - Can't reuse same element
for i in range(start, len(nums)):
    path.append(nums[i])
    backtrack(i + 1)  # Move to next element
    path.pop()
```

## Quick Reference Card 📇

```python
# BACKTRACKING TEMPLATE
def backtrack_solution(input):
    result = []
    current_path = []

    def backtrack(state):
        # BASE CASE: Solution complete
        if is_complete(state):
            result.append(current_path[:])  # COPY!
            return

        # TRY ALL CHOICES
        for choice in get_choices(state):
            # CONSTRAINT CHECK
            if not is_valid(choice):
                continue

            # MAKE CHOICE
            current_path.append(choice)

            # RECURSE
            backtrack(next_state)

            # UNDO (BACKTRACK!)
            current_path.pop()

    backtrack(initial_state)
    return result

# Key points:
# 1. Always copy path when adding to results: path[:]
# 2. Always backtrack (undo): path.pop()
# 3. Skip duplicates: if i > start and nums[i] == nums[i-1]: continue
# 4. Use start index to avoid revisiting: backtrack(i + 1, ...)
# 5. Prune early: return immediately when constraints violated
```

## Summary

**Backtracking is:**
- A systematic way to explore all possibilities
- Building solutions incrementally and abandoning invalid paths
- Making choices, exploring, and undoing (the three-step dance)

**Use it when:**
- Problem asks for "all possible" solutions
- You need to generate combinations, permutations, or subsets
- It's a constraint satisfaction problem
- You can prune invalid paths early

**Remember:**
- Always create copies: `result.append(path[:])`
- Always backtrack: `path.pop()`
- Prune early for efficiency
- Handle duplicates at the same level: `i > start`
- Time complexity is usually exponential: O(2^n) or O(n!)

**The golden rule:** Make a choice → Explore → Undo the choice

Happy backtracking! 🚀
