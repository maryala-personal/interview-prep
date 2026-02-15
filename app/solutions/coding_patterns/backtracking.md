# Backtracking — Complete Interview Guide

## When to Use This Pattern

Backtracking is systematic trial-and-error. You build a solution incrementally, one piece at a time, and when you realize a partial solution cannot lead to a valid complete solution, you undo ("backtrack") the last choice and try the next option. It is essentially a depth-first search through the solution space.

**Signals that indicate backtracking:**
1. The problem asks you to **generate all** valid configurations (all subsets, all permutations, all valid arrangements).
2. The problem asks you to **find any one** valid configuration that satisfies constraints (N-Queens, Sudoku).
3. The solution space is a **decision tree** where at each node you have multiple choices and need to explore them exhaustively.
4. Constraints eliminate large portions of the search space (pruning makes brute force feasible).
5. The problem involves placing items under constraints (queens on a board, letters in a grid, numbers in cells).
6. The phrase "generate," "enumerate," or "list all" appears in the problem statement.

**When NOT to use backtracking:**
- When you only need the count or optimum (not all solutions) and overlapping subproblems exist — use DP instead.
- When a greedy or mathematical approach produces the answer directly.
- When the search space cannot be pruned enough and the problem is NP-hard at its core with large inputs — backtracking will TLE.

---

## Core Mechanics

### Why Does Backtracking Work?

Every combinatorial problem can be modeled as a tree of decisions. At each level of the tree, you make a choice (which element to include, which cell to fill, which direction to go). Backtracking explores this tree depth-first, but skips entire subtrees when the current partial solution is already invalid. This pruning is what makes backtracking dramatically faster than brute force in practice, even though the worst-case complexity may be the same.

### The Choose-Explore-Unchoose Framework

Every backtracking solution follows this three-step pattern:

1. **Choose**: Make a decision — add an element to the current path, place a queen, mark a cell as visited.
2. **Explore**: Recursively solve the smaller subproblem with this choice in place.
3. **Unchoose**: Undo the decision — remove the element, unplace the queen, unmark the cell. This restores state so the next choice at this level starts from a clean slate.

```
backtrack(state):
    if state is a complete solution:
        record/return it
        return

    for each choice available in current state:
        if choice is valid (pruning):
            make the choice          # CHOOSE
            backtrack(new state)     # EXPLORE
            undo the choice          # UNCHOOSE
```

### Visual Walkthrough: Subsets of [1, 2, 3]

The decision tree for generating subsets: at each element, decide "include" or "exclude."

```
                         []
                       /    \
                   [1]        []
                  /   \      /   \
             [1,2]   [1]  [2]    []
             / \     / \   / \   / \
        [1,2,3] [1,2] [1,3] [1] [2,3] [2] [3] []
```

Reading the leaves: {1,2,3}, {1,2}, {1,3}, {1}, {2,3}, {2}, {3}, {}. That is all 2^3 = 8 subsets.

In practice, we model this more efficiently by iterating over remaining elements starting from a given index:

```
backtrack(start=0, path=[])
  -> add []
  -> choose 1: backtrack(start=1, path=[1])
       -> add [1]
       -> choose 2: backtrack(start=2, path=[1,2])
            -> add [1,2]
            -> choose 3: backtrack(start=3, path=[1,2,3])
                 -> add [1,2,3]
            -> unchoose 3
       -> unchoose 2
       -> choose 3: backtrack(start=3, path=[1,3])
            -> add [1,3]
       -> unchoose 3
  -> unchoose 1
  -> choose 2: backtrack(start=2, path=[2])
       ... and so on
```

### Complexity Analysis

Backtracking complexity depends on the problem:
- **Subsets**: O(2^n) subsets, each up to O(n) to copy, total O(n * 2^n).
- **Permutations**: O(n!) permutations, each O(n) to copy, total O(n * n!).
- **Constrained problems** (N-Queens, Sudoku): hard to express in closed form; pruning can reduce the search space dramatically.

---

## The Template

### Subsets/Combinations Template (order does not matter, use start index)

```python
def backtrack_subsets(nums):
    result = []

    def backtrack(start, path):
        result.append(path[:])  # record current subset

        for i in range(start, len(nums)):
            path.append(nums[i])        # choose
            backtrack(i + 1, path)       # explore (i+1 to avoid reusing)
            path.pop()                   # unchoose

    backtrack(0, [])
    return result
```

```go
func backtrackSubsets(nums []int) [][]int {
    var result [][]int
    var path []int

    var backtrack func(start int)
    backtrack = func(start int) {
        // Make a copy and record
        tmp := make([]int, len(path))
        copy(tmp, path)
        result = append(result, tmp)

        for i := start; i < len(nums); i++ {
            path = append(path, nums[i])  // choose
            backtrack(i + 1)               // explore
            path = path[:len(path)-1]      // unchoose
        }
    }

    backtrack(0)
    return result
}
```

### Permutations Template (order matters, use visited set)

```python
def backtrack_permutations(nums):
    result = []

    def backtrack(path, used):
        if len(path) == len(nums):
            result.append(path[:])
            return

        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True             # choose
            path.append(nums[i])
            backtrack(path, used)      # explore
            path.pop()                 # unchoose
            used[i] = False

    backtrack([], [False] * len(nums))
    return result
```

```go
func backtrackPermutations(nums []int) [][]int {
    var result [][]int
    used := make([]bool, len(nums))
    var path []int

    var backtrack func()
    backtrack = func() {
        if len(path) == len(nums) {
            tmp := make([]int, len(path))
            copy(tmp, path)
            result = append(result, tmp)
            return
        }
        for i := 0; i < len(nums); i++ {
            if used[i] {
                continue
            }
            used[i] = true
            path = append(path, nums[i])
            backtrack()
            path = path[:len(path)-1]
            used[i] = false
        }
    }

    backtrack()
    return result
}
```

### Grid Search Template (explore in 4 directions, mark visited)

```python
def backtrack_grid(board, word):
    rows, cols = len(board), len(board[0])

    def backtrack(r, c, idx):
        if idx == len(word):
            return True
        if (r < 0 or r >= rows or c < 0 or c >= cols or
                board[r][c] != word[idx]):
            return False

        temp = board[r][c]
        board[r][c] = '#'  # choose (mark visited)

        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            if backtrack(r + dr, c + dc, idx + 1):  # explore
                return True

        board[r][c] = temp  # unchoose (restore)
        return False

    for r in range(rows):
        for c in range(cols):
            if backtrack(r, c, 0):
                return True
    return False
```

---

## Problem Walkthroughs

### Problem: Subsets (LC #78) — Medium
**Companies**: Meta, Google, Amazon, Microsoft, Uber
**Why it's asked**: The simplest backtracking problem. If you cannot solve this cleanly, the interviewer knows you will struggle with harder backtracking problems.

**Brute Force** (bit manipulation approach):
```python
def subsets_brute(nums):
    n = len(nums)
    result = []
    for mask in range(1 << n):  # 0 to 2^n - 1
        subset = []
        for i in range(n):
            if mask & (1 << i):
                subset.append(nums[i])
        result.append(subset)
    return result
```

**Key Insight**: At each element, we have two choices: include it or skip it. Using a start index ensures we only consider elements after the current one, avoiding duplicate subsets. Every node in the recursion tree (not just leaves) is a valid subset, so we record the path at every call.

**Optimal Solution**:
```python
def subsets(nums):
    result = []

    def backtrack(start, path):
        result.append(path[:])  # every path is a valid subset

        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
    return result
```

**Dry Run** with `nums = [1, 2, 3]`:
```
backtrack(0, [])        -> result: [[]]
  i=0: path=[1]
    backtrack(1, [1])   -> result: [[], [1]]
      i=1: path=[1,2]
        backtrack(2, [1,2]) -> result: [[], [1], [1,2]]
          i=2: path=[1,2,3]
            backtrack(3, [1,2,3]) -> result: [[], [1], [1,2], [1,2,3]]
          pop -> [1,2]
        pop -> [1]
      i=2: path=[1,3]
        backtrack(3, [1,3]) -> result: [[], [1], [1,2], [1,2,3], [1,3]]
      pop -> [1]
    pop -> []
  i=1: path=[2]
    backtrack(2, [2])   -> result: [..., [2]]
      i=2: path=[2,3]
        backtrack(3, [2,3]) -> result: [..., [2], [2,3]]
      pop -> [2]
    pop -> []
  i=2: path=[3]
    backtrack(3, [3])   -> result: [..., [3]]
  pop -> []

Final: [[], [1], [1,2], [1,2,3], [1,3], [2], [2,3], [3]]
```

**Edge Cases**: Empty array (return [[]]), single element (return [[], [x]]), duplicate elements — see Subsets II (LC #90) which requires sorting and skipping duplicates.

**Complexity**: O(n * 2^n) — 2^n subsets, each takes O(n) to copy. Space O(n) for recursion depth.

**Follow-up questions**: "What if the input has duplicates?" — sort the array and skip `nums[i]` when `nums[i] == nums[i-1]` and `i > start`. "Can you do it iteratively?" — yes, start with [[]] and for each num, append it to all existing subsets.

---

### Problem: Permutations (LC #46) — Medium
**Companies**: Meta, Google, Amazon, Microsoft
**Why it's asked**: Tests the permutation backtracking template. Interviewers want to see you handle the "used" array or swap-based approach cleanly.

**Brute Force**:
```python
def permute_brute(nums):
    """Use itertools as reference (not acceptable in interview)."""
    from itertools import permutations
    return [list(p) for p in permutations(nums)]
```

**Key Insight**: Unlike subsets where we use a start index (because order does not matter), permutations consider all positions. We need a `used` array to track which elements are already in the current path. At each recursive level, we iterate over all elements and pick any unused one.

**Optimal Solution**:
```python
def permute(nums):
    result = []

    def backtrack(path, used):
        if len(path) == len(nums):
            result.append(path[:])
            return

        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            backtrack(path, used)
            path.pop()
            used[i] = False

    backtrack([], [False] * len(nums))
    return result
```

**Alternative swap-based approach** (avoids extra space for used array):
```python
def permute_swap(nums):
    result = []

    def backtrack(start):
        if start == len(nums):
            result.append(nums[:])
            return
        for i in range(start, len(nums)):
            nums[start], nums[i] = nums[i], nums[start]  # choose
            backtrack(start + 1)                            # explore
            nums[start], nums[i] = nums[i], nums[start]  # unchoose

    backtrack(0)
    return result
```

**Dry Run** with `nums = [1, 2, 3]` using the used-array approach:
```
backtrack([], [F,F,F])
  i=0: used=[T,F,F], path=[1]
    backtrack([1], [T,F,F])
      i=1: used=[T,T,F], path=[1,2]
        backtrack([1,2], [T,T,F])
          i=2: used=[T,T,T], path=[1,2,3] -> RECORD [1,2,3]
      i=2: used=[T,F,T], path=[1,3]
        backtrack([1,3], [T,F,T])
          i=1: path=[1,3,2] -> RECORD [1,3,2]
  i=1: path=[2]
    -> [2,1,3], [2,3,1]
  i=2: path=[3]
    -> [3,1,2], [3,2,1]

Result: [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]
```

**Edge Cases**: Single element ([[ x ]]), two elements ([[a,b],[b,a]]), empty (return [[]]).

**Complexity**: O(n * n!) — n! permutations, O(n) to copy each. Space O(n) for recursion.

**Follow-up questions**: "What if there are duplicate elements?" — Permutations II (LC #47): sort and skip when `nums[i] == nums[i-1]` and `not used[i-1]`. "What if you only need the k-th permutation?" — LC #60, use factorial number system.

---

### Problem: Combination Sum (LC #39) — Medium
**Companies**: Meta, Google, Amazon, Uber, Microsoft
**Why it's asked**: Tests the unbounded selection variant of backtracking (elements can be reused). Key difference from subsets: pass `i` instead of `i+1` to allow reuse.

**Brute Force**: The recursive approach IS essentially the solution, since we must enumerate all valid combinations.

**Key Insight**: This is like subsets, but with two modifications: (1) elements can be reused, so we recurse with `i` instead of `i+1`, and (2) we stop when the remaining target drops to 0 (success) or below 0 (prune). Sorting the candidates allows us to break early when `candidates[i] > remaining`.

**Optimal Solution**:
```python
def combination_sum(candidates, target):
    result = []
    candidates.sort()  # sorting enables early termination

    def backtrack(start, path, remaining):
        if remaining == 0:
            result.append(path[:])
            return
        for i in range(start, len(candidates)):
            if candidates[i] > remaining:
                break  # prune: no point trying larger candidates
            path.append(candidates[i])
            backtrack(i, path, remaining - candidates[i])  # i, not i+1 (reuse)
            path.pop()

    backtrack(0, [], target)
    return result
```

**Dry Run** with `candidates = [2, 3, 6, 7]`, `target = 7`:
```
backtrack(0, [], 7)
  i=0, cand=2: path=[2], remaining=5
    i=0, cand=2: path=[2,2], remaining=3
      i=0, cand=2: path=[2,2,2], remaining=1
        i=0, cand=2: 2>1, break
      pop -> [2,2]
      i=1, cand=3: path=[2,2,3], remaining=0 -> RECORD [2,2,3]
      pop -> [2,2]
    pop -> [2]
    i=1, cand=3: path=[2,3], remaining=2
      i=1, cand=3: 3>2, break
    pop -> [2]
    i=2, cand=6: 6>5, break
  pop -> []
  i=1, cand=3: path=[3], remaining=4
    i=1, cand=3: path=[3,3], remaining=1
      i=1, cand=3: 3>1, break
    pop -> [3]
  pop -> []
  i=2, cand=6: path=[6], remaining=1
    i=2, cand=6: 6>1, break
  pop -> []
  i=3, cand=7: path=[7], remaining=0 -> RECORD [7]

Result: [[2,2,3], [7]]
```

**Edge Cases**: Target is 0 (return [[]]), single candidate equal to target, no combination reaches target, very large target with small candidates.

**Complexity**: Hard to bound tightly. Worst case exponential (like change-making). Space O(target/min(candidates)) for recursion depth.

**Follow-up questions**: "What if each number can be used only once?" — Combination Sum II (LC #40): use `i+1` and skip duplicates. "What if you need exactly k numbers?" — Combination Sum III (LC #216): add a count constraint.

---

### Problem: Word Search (LC #79) — Medium
**Companies**: Meta, Google, Amazon, Microsoft, Uber — very frequently asked
**Why it's asked**: Tests grid-based backtracking with the visited-cell pattern. A great test of implementation skill.

**Brute Force**: The backtracking approach IS the expected solution. There is no polynomial-time shortcut.

**Key Insight**: For each cell that matches the first character of the word, launch a DFS/backtracking search in all 4 directions. Mark cells as visited (by temporarily modifying the board) to prevent revisiting. If the search fails, restore the cell (backtrack).

**Optimal Solution**:
```python
def exist(board, word):
    rows, cols = len(board), len(board[0])

    def backtrack(r, c, idx):
        if idx == len(word):
            return True
        if (r < 0 or r >= rows or c < 0 or c >= cols or
                board[r][c] != word[idx]):
            return False

        # Choose: mark as visited
        temp = board[r][c]
        board[r][c] = '#'

        # Explore all 4 directions
        found = (backtrack(r + 1, c, idx + 1) or
                 backtrack(r - 1, c, idx + 1) or
                 backtrack(r, c + 1, idx + 1) or
                 backtrack(r, c - 1, idx + 1))

        # Unchoose: restore
        board[r][c] = temp
        return found

    for r in range(rows):
        for c in range(cols):
            if backtrack(r, c, 0):
                return True
    return False
```

**Dry Run** with `board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]]`, `word = "ABCCED"`:
```
Start at (0,0)='A', matches word[0]
  Mark (0,0)='#', try neighbors for 'B'
  (0,1)='B', matches word[1]
    Mark (0,1)='#', try neighbors for 'C'
    (0,2)='C', matches word[2]
      Mark (0,2)='#', try neighbors for 'C'
      (1,2)='C', matches word[3]
        Mark (1,2)='#', try neighbors for 'E'
        (2,2)='E', matches word[4]
          Mark (2,2)='#', try neighbors for 'D'
          (2,1)='D', matches word[5]
            idx=6 == len(word) -> return True!

Answer: True, path: (0,0)->(0,1)->(0,2)->(1,2)->(2,2)->(2,1)
```

**Edge Cases**: Word longer than total cells (False), single cell board, word is single character, all cells same letter.

**Complexity**: O(m * n * 4^L) where L is the word length. Each cell can start a search, and at each step we branch into 4 directions (minus visited). Space O(L) for recursion depth.

**Follow-up questions**: "What if you need to find multiple words?" — Word Search II (LC #212), use a Trie to share prefix search. "How would you optimize this?" — prune by checking character frequency counts before searching.

---

### Problem: Generate Parentheses (LC #22) — Medium
**Companies**: Google, Meta, Amazon, Microsoft, Uber
**Why it's asked**: Beautiful constrained generation problem. Tests understanding of when a choice is valid (pruning).

**Brute Force**:
```python
def generate_parenthesis_brute(n):
    """Generate all strings of length 2n with ( and ), filter valid ones."""
    result = []
    def generate(s):
        if len(s) == 2 * n:
            if is_valid(s):
                result.append(s)
            return
        generate(s + '(')
        generate(s + ')')

    def is_valid(s):
        count = 0
        for c in s:
            count += 1 if c == '(' else -1
            if count < 0:
                return False
        return count == 0

    generate('')
    return result
```

**Key Insight**: Instead of generating all strings and filtering, we can prune during generation. Track how many open and close parentheses we have placed. We can place '(' if `open_count < n`, and we can place ')' if `close_count < open_count` (ensures we never have more closing than opening).

**Optimal Solution**:
```python
def generate_parenthesis(n):
    result = []

    def backtrack(path, open_count, close_count):
        if len(path) == 2 * n:
            result.append(''.join(path))
            return

        if open_count < n:
            path.append('(')
            backtrack(path, open_count + 1, close_count)
            path.pop()

        if close_count < open_count:
            path.append(')')
            backtrack(path, open_count, close_count + 1)
            path.pop()

    backtrack([], 0, 0)
    return result
```

**Dry Run** with `n = 2`:
```
backtrack([], 0, 0)
  open < 2: path=['(']
    backtrack(['('], 1, 0)
      open < 2: path=['(','(']
        backtrack(['(','('], 2, 0)
          close < open: path=['(','(', ')']
            backtrack(['(','(',')'], 2, 1)
              close < open: path=['(','(',')',')']
                len=4=2*2 -> RECORD "(())"
              pop
          pop
      pop
      close < open: path=['(',')']
        backtrack(['(',')'], 1, 1)
          open < 2: path=['(',')', '(']
            backtrack(['(',')','('], 2, 1)
              close < open: path=['(',')', '(',')']
                len=4 -> RECORD "()()"
              pop
          pop
      pop
  pop

Result: ["(())", "()()"]
```

**Edge Cases**: n=0 (return [""]), n=1 (return ["()"]).

**Complexity**: The number of valid parenthesizations is the n-th Catalan number, C(n) = C(2n, n) / (n+1), which is approximately 4^n / (n^(3/2) * sqrt(pi)). Space O(n) for recursion.

**Follow-up questions**: "What if there are multiple types of brackets?" — track counts for each type and ensure proper nesting. "What is the k-th valid parenthesization?" — use Catalan number properties for ranking/unranking.

---

### Problem: Palindrome Partitioning (LC #131) — Medium
**Companies**: Google, Meta, Amazon
**Why it's asked**: Combines backtracking (enumerate all partitions) with palindrome checking. Tests multi-level thinking.

**Brute Force**: The backtracking approach is the intended solution. There is no way to avoid enumeration since we need all partitions.

**Key Insight**: At each position, try every possible prefix that is a palindrome. If `s[start:end+1]` is a palindrome, take it as a partition piece and recurse on the remainder. This is a subset-style backtracking where the "elements" are all palindromic prefixes at each step.

**Optimal Solution**:
```python
def partition(s):
    result = []

    def is_palindrome(left, right):
        while left < right:
            if s[left] != s[right]:
                return False
            left += 1
            right -= 1
        return True

    def backtrack(start, path):
        if start == len(s):
            result.append(path[:])
            return

        for end in range(start, len(s)):
            if is_palindrome(start, end):
                path.append(s[start:end + 1])
                backtrack(end + 1, path)
                path.pop()

    backtrack(0, [])
    return result
```

**Optimization with precomputed palindrome table:**
```python
def partition_optimized(s):
    n = len(s)
    # Precompute: is_pal[i][j] = True if s[i:j+1] is a palindrome
    is_pal = [[False] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            if s[i] == s[j] and (j - i <= 2 or is_pal[i + 1][j - 1]):
                is_pal[i][j] = True

    result = []

    def backtrack(start, path):
        if start == n:
            result.append(path[:])
            return
        for end in range(start, n):
            if is_pal[start][end]:
                path.append(s[start:end + 1])
                backtrack(end + 1, path)
                path.pop()

    backtrack(0, [])
    return result
```

**Dry Run** with `s = "aab"`:
```
backtrack(0, [])
  end=0: "a" is palindrome -> path=["a"]
    backtrack(1, ["a"])
      end=1: "a" is palindrome -> path=["a","a"]
        backtrack(2, ["a","a"])
          end=2: "b" is palindrome -> path=["a","a","b"]
            backtrack(3, ["a","a","b"]) -> start==3 -> RECORD ["a","a","b"]
          pop
      end=2: "ab" is NOT palindrome -> skip
    pop
  end=1: "aa" is palindrome -> path=["aa"]
    backtrack(2, ["aa"])
      end=2: "b" is palindrome -> path=["aa","b"]
        backtrack(3, ["aa","b"]) -> RECORD ["aa","b"]
      pop
  end=2: "aab" is NOT palindrome -> skip

Result: [["a","a","b"], ["aa","b"]]
```

**Edge Cases**: Single character (one partition), entire string is a palindrome (include it as one option), all same characters.

**Complexity**: O(n * 2^n) worst case (exponentially many partitions). Palindrome precomputation is O(n^2). Space O(n) for recursion.

**Follow-up questions**: "What is the minimum number of cuts?" — LC #132, this is a DP problem, not backtracking. "Can you do it with a Trie?" — not directly applicable here.

---

### Problem: N-Queens (LC #51) — Hard
**Companies**: Google, Amazon, Microsoft, Meta
**Why it's asked**: The canonical constraint-satisfaction backtracking problem. Tests your ability to efficiently check constraints (diagonals, columns) while exploring the search space.

**Brute Force**:
```python
def solve_n_queens_brute(n):
    """Place queens in all n^2 choose n positions, check validity."""
    # This is astronomically slow — O(C(n^2, n) * n^2)
    pass
```

**Key Insight**: Place queens row by row (one per row is guaranteed). For each row, try each column. A placement is invalid if another queen is in the same column or on the same diagonal. We can track attacked columns and diagonals with sets for O(1) conflict checking. The two diagonals through (r, c) are identified by `r - c` (anti-diagonal) and `r + c` (main diagonal).

**Optimal Solution**:
```python
def solve_n_queens(n):
    result = []
    board = [['.' for _ in range(n)] for _ in range(n)]
    cols = set()
    diag1 = set()  # r - c (anti-diagonal, top-left to bottom-right)
    diag2 = set()  # r + c (main diagonal, top-right to bottom-left)

    def backtrack(row):
        if row == n:
            result.append([''.join(r) for r in board])
            return

        for col in range(n):
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue  # pruning: conflict detected

            # Choose
            board[row][col] = 'Q'
            cols.add(col)
            diag1.add(row - col)
            diag2.add(row + col)

            # Explore
            backtrack(row + 1)

            # Unchoose
            board[row][col] = '.'
            cols.remove(col)
            diag1.remove(row - col)
            diag2.remove(row + col)

    backtrack(0)
    return result
```

**Dry Run** with `n = 4`:
```
Row 0: try col 0
  Row 1: col 0 (same col), col 1 (diag), try col 2
    Row 2: col 0 (diag), col 1 (same col as future?), col 2 (same col)...
    -> no valid placement, backtrack
  Row 1: try col 3
    Row 2: try col 1
      Row 3: col 0 (diag), col 1 (col), col 2 (diag), col 3 (col)
      -> no valid, backtrack
    Row 2: try col 0 (skipped: diag)... eventually fails
  Backtrack to row 0

Row 0: try col 1
  Row 1: try col 3
    Row 2: try col 0
      Row 3: try col 2
        row==4 -> RECORD!
        Solution:  .Q..
                   ...Q
                   Q...
                   ..Q.

Row 0: try col 2
  Row 1: try col 0
    Row 2: try col 3
      Row 3: try col 1
        row==4 -> RECORD!
        Solution:  ..Q.
                   Q...
                   ...Q
                   .Q..

Result: 2 solutions for n=4
```

**Edge Cases**: n=1 (one solution: [["Q"]]), n=2 and n=3 (no solutions), n=8 (92 solutions).

**Complexity**: O(n!) roughly — at row 0 we have n choices, row 1 at most n-1 (column constraint alone), and further pruning from diagonals. Space O(n) for recursion and sets.

**Follow-up questions**: "Just return the count?" — N-Queens II (LC #52), same algorithm but just increment a counter. "Can you optimize for very large n?" — use bit manipulation for the constraint sets.

---

### Problem: Sudoku Solver (LC #37) — Hard
**Companies**: Google, Amazon, Microsoft, Meta
**Why it's asked**: Tests constraint propagation combined with backtracking. A realistic problem with real-world relevance.

**Brute Force**: Try all possible numbers in all empty cells — 9^(empty cells) possibilities, astronomically slow.

**Key Insight**: Process empty cells one at a time. For each empty cell, try digits 1-9 that do not violate any Sudoku constraint (row, column, 3x3 box). If no digit works, backtrack. The key optimization is efficient constraint checking using sets for each row, column, and box.

**Optimal Solution**:
```python
def solve_sudoku(board):
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    empty = []

    # Initialize constraint sets and find empty cells
    for r in range(9):
        for c in range(9):
            if board[r][c] != '.':
                num = board[r][c]
                rows[r].add(num)
                cols[c].add(num)
                boxes[(r // 3) * 3 + c // 3].add(num)
            else:
                empty.append((r, c))

    def backtrack(idx):
        if idx == len(empty):
            return True  # all cells filled

        r, c = empty[idx]
        box_id = (r // 3) * 3 + c // 3

        for num in '123456789':
            if num in rows[r] or num in cols[c] or num in boxes[box_id]:
                continue  # pruning

            # Choose
            board[r][c] = num
            rows[r].add(num)
            cols[c].add(num)
            boxes[box_id].add(num)

            # Explore
            if backtrack(idx + 1):
                return True

            # Unchoose
            board[r][c] = '.'
            rows[r].remove(num)
            cols[c].remove(num)
            boxes[box_id].remove(num)

        return False  # no valid digit, trigger backtrack

    backtrack(0)
```

**Dry Run** (abbreviated for a partially filled board):
```
Empty cells identified: [(0,2), (0,5), (1,0), ...]
Process cell (0,2):
  row 0 has {5,3,7}, col 2 has {}, box 0 has {5,3,6,9,8}
  Try '1': not in row/col/box -> place it
    Process cell (0,5):
      Try valid digits for this cell...
      If all lead to contradiction -> backtrack
    If backtrack reached: remove '1' from (0,2)
  Try '2': check constraints...
  ... continue until solution found
```

**Edge Cases**: Board with unique solution (guaranteed by problem), board nearly full (very fast), board nearly empty (slower but still feasible for 9x9).

**Complexity**: O(9^m) where m is the number of empty cells, but pruning reduces this dramatically in practice. A valid Sudoku puzzle has a unique solution, so the search tree is small. Space O(m) for recursion.

**Follow-up questions**: "How would you make this faster?" — use constraint propagation (naked singles, hidden singles) before backtracking. "How would you generate valid Sudoku puzzles?" — fill a grid with backtracking, then remove cells while ensuring unique solution.

---

### Problem: Word Search II (LC #212) — Hard
**Companies**: Google, Meta, Amazon, Microsoft, Uber
**Why it's asked**: Combines Trie + backtracking. Without the Trie optimization, searching for each word independently is too slow.

**Brute Force**:
```python
def find_words_brute(board, words):
    """Run Word Search (LC #79) for each word independently."""
    result = []
    for word in words:
        if exist(board, word):  # from LC #79
            result.append(word)
    return result
```
O(W * M * N * 4^L) where W is number of words, unacceptably slow for large word lists.

**Key Insight**: Build a Trie from all the words. Then do a single backtracking search over the grid, simultaneously searching for ALL words. At each cell, check if the current path forms a prefix in the Trie. If not, prune (no word starts with this prefix). If a complete word is found, record it. This shares computation across words with common prefixes.

**Optimal Solution**:
```python
def find_words(board, words):
    # Build Trie
    trie = {}
    for word in words:
        node = trie
        for ch in word:
            node = node.setdefault(ch, {})
        node['$'] = word  # store the complete word at the terminal node

    rows, cols = len(board), len(board[0])
    result = []

    def backtrack(r, c, parent):
        ch = board[r][c]
        node = parent.get(ch)
        if not node:
            return

        # Check if we found a word
        if '$' in node:
            result.append(node['$'])
            del node['$']  # avoid duplicate results

        # Choose: mark visited
        board[r][c] = '#'

        # Explore 4 directions
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != '#':
                backtrack(nr, nc, node)

        # Unchoose: restore
        board[r][c] = ch

        # Optimization: prune empty trie branches
        if not node:
            del parent[ch]

    for r in range(rows):
        for c in range(cols):
            backtrack(r, c, trie)

    return result
```

**Dry Run** with `board = [["o","a","a","n"],["e","t","a","e"],["i","h","k","r"],["i","f","l","v"]]`, `words = ["oath","pea","eat","rain"]`:
```
Trie built:
  o -> a -> t -> h -> {$: "oath"}
  p -> e -> a -> {$: "pea"}
  e -> a -> t -> {$: "eat"}
  r -> a -> i -> n -> {$: "rain"}

Search from (0,0)='o':
  'o' in trie -> descend
  neighbors: (0,1)='a', (1,0)='e'
  (0,1)='a': 'a' in trie['o'] -> descend
    (1,1)='t': 't' in trie['o']['a'] -> descend
      (2,1)='h': 'h' in trie['o']['a']['t'] -> descend
        '$' found -> record "oath"!

Search from (1,0)='e':
  'e' in trie -> descend
  (1,1)='t' isn't under 'e', but (0,0)='o' isn't either...
  Actually, (1,1) could lead somewhere via 'a':
  (0,0) already restored. Try (2,0)='i'... no path for "eat"

Search from various cells eventually finds "eat" starting at (1,1):
  (1,1)='e'? No, we need 'e' at top level...
  Actually (0,3)='n' or other e's...
  Path: (1,0)='e' isn't in the right neighborhood.

  The search finds "eat" via (1,1)->(1,2)->(0,2) isn't right...
  Correct path for "eat": depends on board connectivity.

Result: ["oath", "eat"]  (pea and rain have no valid paths)
```

**Edge Cases**: No words found, words share long prefixes (Trie shines), single cell board, duplicate words in input.

**Complexity**: O(M * N * 4^L) where L is the max word length, but Trie pruning makes it much faster in practice. Building the Trie is O(sum of word lengths). Space O(sum of word lengths) for Trie.

**Follow-up questions**: "How would you handle a streaming word list?" — incrementally add words to the Trie and re-search. "What if the board is very large but words are short?" — the 4^L branching factor means short words keep the search manageable.

---

## Common Mistakes & Interview Tips

### Common Mistakes

1. **Forgetting to unchoose (restore state).** The most common backtracking bug. Always have the "unchoose" step symmetric to the "choose" step. If you add to a set, remove from the set. If you modify a cell, restore it.

2. **Using `i+1` vs `i` for reuse.** In subsets and combinations without replacement, recurse with `i+1`. In combination sum with replacement, recurse with `i`. Getting this wrong either allows duplicates or misses valid combinations.

3. **Not handling the `start` parameter correctly.** For subsets and combinations, always pass and use `start` to avoid generating duplicate subsets in different orders.

4. **Copying the path incorrectly.** `result.append(path)` appends a reference; `result.append(path[:])` or `result.append(list(path))` appends a copy. The reference version means all entries in result point to the same (eventually empty) list.

5. **Pruning too aggressively or not enough.** Too aggressive and you miss valid solutions. Not enough and you time out. Test your pruning logic with small examples.

### Interview Tips

1. **Draw the decision tree first.** Before coding, sketch the first few levels of the recursion tree on the whiteboard. This clarifies the structure and helps you catch off-by-one issues.

2. **State the template you are using.** "I will use the subsets template with a start index because order does not matter and we cannot reuse elements." This signals expertise to the interviewer.

3. **Handle duplicates explicitly.** When the input has duplicates, always sort first and add: `if i > start and nums[i] == nums[i-1]: continue`. Explain why this works (it skips choosing the same value at the same decision level).

4. **Discuss pruning opportunities.** Even if not required for correctness, mentioning pruning shows optimization awareness. "We can sort and break early when the candidate exceeds the remaining target."

5. **Know the complexity.** Backtracking complexities are often exponential and hard to state precisely. It is fine to say "the worst case is O(2^n) for subsets" or "O(n!) for permutations" and note that pruning improves the practical runtime.

---

## Pattern Connections

- **Backtracking + Trie**: Word Search II (LC #212) combines grid backtracking with Trie pruning. This is a common pairing for multi-word search problems.

- **Backtracking to DP**: When backtracking has overlapping subproblems, add memoization and it becomes top-down DP. The transition from LC #494 Target Sum brute force to DP solution illustrates this perfectly.

- **Backtracking vs BFS**: Some problems (like generating parentheses) can also be solved with BFS level by level. Backtracking (DFS) uses O(depth) space while BFS uses O(width) space — usually DFS is more space-efficient.

- **Constraint Satisfaction**: N-Queens and Sudoku are constraint satisfaction problems (CSPs). The general approach is: pick an unassigned variable, try values that satisfy constraints, recurse, backtrack on failure. More advanced CSP techniques (arc consistency, constraint propagation) can pre-prune before backtracking.

- **Backtracking + Sorting**: Many backtracking problems benefit from sorting the input first. It enables: (1) skipping duplicates with `nums[i] == nums[i-1]`, (2) early termination when values exceed a threshold, (3) natural lexicographic ordering of results.

- **Subsets vs Permutations vs Combinations**: These three form the backbone of backtracking problems. Subsets: start index, include all prefixes. Permutations: used array, only full-length paths. Combinations: start index with target constraint, fixed-length paths.
