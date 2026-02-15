# Matrix / Grid — Complete Interview Guide

## When to Use This Pattern

Grid and matrix problems operate on 2D arrays. They appear frequently in coding interviews because they combine spatial reasoning with standard algorithmic techniques (BFS, DFS, DP, binary search).

**Primary signals:**
- "Given a 2D matrix/grid..."
- "Rotate the image" / "Spiral order"
- "Shortest path in a grid" (with or without obstacles)
- "Maximal square/rectangle" in a binary matrix
- "Set matrix zeroes" / "modify in place"
- "Search in a sorted 2D matrix"
- "Number of islands" / "flood fill" (grid traversal)

**Core grid techniques:**
1. **Traversal patterns:** 4-directional, 8-directional, diagonal, spiral, layer-by-layer
2. **BFS on grids:** Shortest path, multi-source BFS, state-space BFS
3. **DFS on grids:** Connected components, flood fill, backtracking on grids
4. **DP on grids:** Maximal square, unique paths, minimum path sum, dungeon game
5. **Matrix manipulation:** Rotation, transposition, spiral traversal, in-place modifications

**When to use BFS vs DFS vs DP on grids:**

| Technique | Use When |
|-----------|----------|
| BFS | Shortest path (unweighted), level-by-level expansion |
| DFS | Connected components, flood fill, all paths |
| DP | Optimization (max/min), counting paths, prefix sums |
| Binary Search | Sorted matrix queries |
| In-place tricks | Constant space modifications |

---

## Core Mechanics

### Grid Traversal Directions

```python
# 4-directional (up, down, left, right)
directions_4 = [(0, 1), (0, -1), (1, 0), (-1, 0)]

# 8-directional (includes diagonals)
directions_8 = [(0, 1), (0, -1), (1, 0), (-1, 0),
                (1, 1), (1, -1), (-1, 1), (-1, -1)]

# Diagonal only
directions_diag = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

# Boundary check
def in_bounds(r, c, rows, cols):
    return 0 <= r < rows and 0 <= c < cols
```

### Matrix Rotation and Transposition

**90-degree clockwise rotation = Transpose + Reverse each row**

```
Original:    Transpose:    Reverse rows:
1 2 3        1 4 7         7 4 1
4 5 6   →    2 5 8    →    8 5 2
7 8 9        3 6 9         9 6 3
```

**Why this works:** Transposing flips the matrix over the main diagonal (row i, col j → row j, col i). Reversing each row then completes the 90-degree rotation.

**Other rotations:**
- 90 CCW: Transpose + Reverse each column (or Reverse rows + Transpose)
- 180: Reverse each row, then reverse row order
- Transpose: swap `matrix[i][j]` with `matrix[j][i]`

### Spiral Traversal

Process the matrix in concentric layers, shrinking the boundaries after each complete traversal.

```
Layer 0 (outer):  →→→→↓
                       ↓
                  ←←←←↓
                  ↑
                  ↑→→↓  ← Layer 1 (inner)
                    ←↓
```

Maintain four boundaries: `top`, `bottom`, `left`, `right`. After going right across the top, increment top. After going down the right side, decrement right. And so on.

### BFS on Grids with State

For problems where the state is more than just position (e.g., "obstacles remaining," "keys collected"), the BFS state is `(row, col, extra_state)`. Use a visited set that includes the extra state to avoid revisiting states.

```
Shortest path with at most k obstacles:
State: (row, col, obstacles_remaining)
Visited: set of (row, col, obstacles_remaining)
```

### DP on Grids

Many grid problems have optimal substructure: the answer at cell (i, j) depends on answers at adjacent cells. Common patterns:

**Top-left to bottom-right:** `dp[i][j]` depends on `dp[i-1][j]` and `dp[i][j-1]`
- Unique Paths, Minimum Path Sum

**Bottom-right to top-left:** `dp[i][j]` depends on `dp[i+1][j]` and `dp[i][j+1]`
- Dungeon Game

**All directions:** `dp[i][j]` depends on `dp[i-1][j]`, `dp[i][j-1]`, `dp[i-1][j-1]`
- Maximal Square

---

## The Template

### Python — Grid BFS (Shortest Path)

```python
from collections import deque

def bfs_grid(grid: list[list[int]], start: tuple, end: tuple) -> int:
    """BFS shortest path on a grid. Returns distance or -1."""
    rows, cols = len(grid), len(grid[0])
    queue = deque([(start[0], start[1], 0)])  # (row, col, distance)
    visited = {start}

    while queue:
        r, c, dist = queue.popleft()
        if (r, c) == end:
            return dist

        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and (nr, nc) not in visited
                    and grid[nr][nc] != 1):  # 1 = obstacle
                visited.add((nr, nc))
                queue.append((nr, nc, dist + 1))

    return -1
```

### Python — Grid DFS (Connected Components)

```python
def count_components(grid: list[list[int]]) -> int:
    """Count connected components of 1s in a grid."""
    rows, cols = len(grid), len(grid[0])
    count = 0

    def dfs(r, c):
        if (r < 0 or r >= rows or c < 0 or c >= cols
                or grid[r][c] != 1):
            return
        grid[r][c] = 0  # Mark visited
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            dfs(r + dr, c + dc)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                dfs(r, c)
                count += 1

    return count
```

### Go — Grid BFS

```go
type Point struct {
    r, c, dist int
}

func bfsGrid(grid [][]int, sr, sc, er, ec int) int {
    rows, cols := len(grid), len(grid[0])
    visited := map[[2]int]bool{{sr, sc}: true}
    queue := []Point{{sr, sc, 0}}
    dirs := [][2]int{{0, 1}, {0, -1}, {1, 0}, {-1, 0}}

    for len(queue) > 0 {
        cur := queue[0]
        queue = queue[1:]
        if cur.r == er && cur.c == ec {
            return cur.dist
        }
        for _, d := range dirs {
            nr, nc := cur.r+d[0], cur.c+d[1]
            key := [2]int{nr, nc}
            if nr >= 0 && nr < rows && nc >= 0 && nc < cols &&
                !visited[key] && grid[nr][nc] != 1 {
                visited[key] = true
                queue = append(queue, Point{nr, nc, cur.dist + 1})
            }
        }
    }
    return -1
}
```

### Python — Spiral Traversal

```python
def spiral_order(matrix: list[list[int]]) -> list[int]:
    """Traverse matrix in spiral order."""
    if not matrix:
        return []
    result = []
    top, bottom, left, right = 0, len(matrix) - 1, 0, len(matrix[0]) - 1

    while top <= bottom and left <= right:
        # Go right across top
        for c in range(left, right + 1):
            result.append(matrix[top][c])
        top += 1

        # Go down right side
        for r in range(top, bottom + 1):
            result.append(matrix[r][right])
        right -= 1

        # Go left across bottom (if still valid)
        if top <= bottom:
            for c in range(right, left - 1, -1):
                result.append(matrix[bottom][c])
            bottom -= 1

        # Go up left side (if still valid)
        if left <= right:
            for r in range(bottom, top - 1, -1):
                result.append(matrix[r][left])
            left += 1

    return result
```

### In-Place State Encoding

Many grid problems need a "visited" marker but require O(1) extra space. Common techniques:

**Overwrite with a sentinel:** Set visited cells to a value not in the original data (e.g., 0 for land, '#' for visited in char grids).

**Use the sign bit:** For integer grids, negate values to mark visited. The original value is still recoverable via `abs()`.

**Encode multiple states in one cell:** For Set Matrix Zeroes, the first row/column stores "should this row/column be zeroed?" This piggybacks state onto existing data.

**Two-pass encoding (Game of Life, LC 289):**
Use intermediate states to encode both old and new values:
- 0 → 0: stays dead → encode as 0
- 0 → 1: becomes alive → encode as 2
- 1 → 0: dies → encode as -1
- 1 → 1: stays alive → encode as 1

First pass: apply rules using intermediate states (read old value as `state > 0` or `abs(state) == 1`).
Second pass: convert intermediate states to final states.

### Multi-Source BFS

Some grid problems start from multiple sources simultaneously. Examples:
- 01 Matrix (LC 542): find distance from each cell to nearest 0
- Rotting Oranges (LC 994): all rotten oranges spread simultaneously
- Walls and Gates (LC 286): all gates spread simultaneously

**Pattern:** Add all source cells to the queue initially, then BFS outward. This is equivalent to creating a "super source" connected to all starting points.

```python
from collections import deque

def multi_source_bfs(grid, sources):
    """BFS from multiple sources simultaneously."""
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    dist = [[float('inf')] * cols for _ in range(rows)]

    for r, c in sources:
        queue.append((r, c))
        dist[r][c] = 0

    while queue:
        r, c = queue.popleft()
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and dist[nr][nc] == float('inf')):
                dist[nr][nc] = dist[r][c] + 1
                queue.append((nr, nc))

    return dist
```

---

## Variant Subpatterns

### 1. Matrix Manipulation (In-place)
Set Matrix Zeroes, Rotate Image. Use the matrix itself to store state (first row/column as markers).

### 2. Spiral / Layer Traversal
Process the matrix in concentric rectangular layers. Track four boundaries.

### 3. BFS Shortest Path on Grid
Standard BFS. Each cell is a node, edges connect adjacent cells. Weight 1 per step.

### 4. BFS with Extra State
State = (position + additional info like obstacles remaining, keys collected). Visited set includes the full state.

### 5. DP on Grid
Top-left to bottom-right or reverse. Common for path counting, min cost, and maximal shapes.

### 6. Binary Search on Sorted Matrix
Row-sorted and/or column-sorted matrices. Use staircase search from top-right or bottom-left.

---

## Problem Walkthroughs

---

### Problem 1: Set Matrix Zeroes (LC 73 — Medium)

**Problem:** Given an m x n integer matrix, if an element is 0, set its entire row and column to 0. Do it in-place.

**Brute Force:**
Copy the matrix. Scan for zeros. For each zero, set the row and column in the original matrix. O(mn) space.

**Better:** Use two sets to record which rows and columns should be zeroed. O(m + n) space.

**Key Insight (O(1) space):**
Use the first row and first column of the matrix itself as markers. If `matrix[i][j] == 0`, set `matrix[i][0] = 0` (mark row i) and `matrix[0][j] = 0` (mark column j). Then iterate again and zero out cells based on markers.

Special care: the first row and first column share `matrix[0][0]`, so use a separate flag for one of them.

**Optimal Solution:**

```python
def setZeroes(matrix: list[list[int]]) -> None:
    """
    LC 73: Set Matrix Zeroes — O(1) space

    Time: O(m * n)
    Space: O(1)
    """
    m, n = len(matrix), len(matrix[0])
    first_row_zero = False
    first_col_zero = False

    # Check if first row has any zero
    for j in range(n):
        if matrix[0][j] == 0:
            first_row_zero = True
            break

    # Check if first column has any zero
    for i in range(m):
        if matrix[i][0] == 0:
            first_col_zero = True
            break

    # Use first row/col as markers for the rest
    for i in range(1, m):
        for j in range(1, n):
            if matrix[i][j] == 0:
                matrix[i][0] = 0  # Mark row
                matrix[0][j] = 0  # Mark col

    # Zero out cells based on markers
    for i in range(1, m):
        for j in range(1, n):
            if matrix[i][0] == 0 or matrix[0][j] == 0:
                matrix[i][j] = 0

    # Zero out first row if needed
    if first_row_zero:
        for j in range(n):
            matrix[0][j] = 0

    # Zero out first column if needed
    if first_col_zero:
        for i in range(m):
            matrix[i][0] = 0
```

**Dry Run:**
```
matrix = [[1,1,1],
          [1,0,1],
          [1,1,1]]

first_row_zero = False, first_col_zero = False

Scan for zeros (rows 1+, cols 1+):
  matrix[1][1] = 0 → matrix[1][0] = 0, matrix[0][1] = 0

matrix = [[1,0,1],
          [0,0,1],
          [1,1,1]]

Zero out based on markers:
  Row 1 (matrix[1][0]=0): zero entire row 1
  Col 1 (matrix[0][1]=0): zero entire col 1

matrix = [[1,0,1],
          [0,0,0],
          [1,0,1]]

first_row_zero = False → don't zero row 0 (except already done for col 1)
first_col_zero = False → don't zero col 0

Final: [[1,0,1],[0,0,0],[1,0,1]]
```

**Edge Cases:**
- No zeros: no changes
- Entire matrix is zero: stays zero
- Zero in first row or first column: handled by separate flags
- 1x1 matrix: if 0, stays 0

**Follow-up:** What if you need to support multiple operations efficiently (set zero, then query)? Use a more sophisticated data structure.

---

### Problem 2: Spiral Matrix (LC 54 — Medium)

**Problem:** Given an m x n matrix, return all elements in spiral order.

**Brute Force:**
Simulate walking through the matrix, turning right when hitting a boundary or visited cell. O(mn) with visited array.

**Key Insight:**
Use four boundaries (top, bottom, left, right) and peel off one layer at a time. After traversing the top row, increment top. After traversing the right column, decrement right. And so on.

**Optimal Solution:**

```python
def spiralOrder(matrix: list[list[int]]) -> list[int]:
    """
    LC 54: Spiral Matrix

    Time: O(m * n)
    Space: O(1) extra (output not counted)
    """
    result = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1

    while top <= bottom and left <= right:
        # Right across top row
        for c in range(left, right + 1):
            result.append(matrix[top][c])
        top += 1

        # Down right column
        for r in range(top, bottom + 1):
            result.append(matrix[r][right])
        right -= 1

        # Left across bottom row
        if top <= bottom:
            for c in range(right, left - 1, -1):
                result.append(matrix[bottom][c])
            bottom -= 1

        # Up left column
        if left <= right:
            for r in range(bottom, top - 1, -1):
                result.append(matrix[r][left])
            left += 1

    return result
```

**Dry Run:**
```
matrix = [[1,2,3],[4,5,6],[7,8,9]]

top=0, bottom=2, left=0, right=2

Layer 1:
  Right: 1, 2, 3 (top=0). top→1
  Down: 6, 9 (right=2). right→1
  Left: 8, 7 (bottom=2). bottom→1
  Up: 4 (left=0). left→1

top=1, bottom=1, left=1, right=1

Layer 2:
  Right: 5. top→2. top > bottom, stop.

Result: [1, 2, 3, 6, 9, 8, 7, 4, 5]
```

**Edge Cases:**
- Single row: `[[1,2,3]]` → `[1,2,3]`
- Single column: `[[1],[2],[3]]` → `[1,2,3]`
- 1x1: `[[5]]` → `[5]`
- Non-square matrix: boundaries shrink asymmetrically

**Follow-up:** Spiral Matrix II (LC 59) — fill a matrix in spiral order. Same boundary approach but assign values instead of reading them.

---

### Problem 3: Rotate Image (LC 48 — Medium)

**Problem:** Rotate an n x n matrix 90 degrees clockwise. Do it in-place.

**Brute Force:**
Create a new matrix, copy elements to rotated positions. O(n^2) space.

**Key Insight:**
90-degree clockwise rotation = Transpose + Reverse each row.

Why: Position (i, j) maps to (j, n-1-i) after 90-degree clockwise rotation.
Transpose maps (i, j) → (j, i). Reversing row j maps (j, i) → (j, n-1-i). Combined: (i, j) → (j, n-1-i).

**Optimal Solution:**

```python
def rotate(matrix: list[list[int]]) -> None:
    """
    LC 48: Rotate Image — 90 degrees clockwise

    Time: O(n^2)
    Space: O(1)
    """
    n = len(matrix)

    # Step 1: Transpose (swap across main diagonal)
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]

    # Step 2: Reverse each row
    for i in range(n):
        matrix[i].reverse()
```

**Alternative (four-way swap, layer by layer):**

```python
def rotate_swap(matrix: list[list[int]]) -> None:
    """Rotate by swapping four elements at a time."""
    n = len(matrix)
    for layer in range(n // 2):
        first, last = layer, n - 1 - layer
        for i in range(first, last):
            offset = i - first
            # Save top
            top = matrix[first][i]
            # Left → Top
            matrix[first][i] = matrix[last - offset][first]
            # Bottom → Left
            matrix[last - offset][first] = matrix[last][last - offset]
            # Right → Bottom
            matrix[last][last - offset] = matrix[i][last]
            # Top → Right
            matrix[i][last] = top
```

**Dry Run (Transpose + Reverse):**
```
matrix = [[1,2,3],
          [4,5,6],
          [7,8,9]]

Transpose:
  swap (0,1)↔(1,0): 2↔4 → [[1,4,3],[2,5,6],[7,8,9]]
  Wait, that's wrong. Let me redo.

  swap matrix[0][1] and matrix[1][0]: 2↔4
  swap matrix[0][2] and matrix[2][0]: 3↔7
  swap matrix[1][2] and matrix[2][1]: 6↔8

  After transpose: [[1,4,7],
                     [2,5,8],
                     [3,6,9]]

Reverse each row:
  [1,4,7] → [7,4,1]
  [2,5,8] → [8,5,2]
  [3,6,9] → [9,6,3]

Result: [[7,4,1],
         [8,5,2],
         [9,6,3]]

This is the 90-degree clockwise rotation.
```

**Edge Cases:**
- 1x1 matrix: no change
- 2x2 matrix: one swap per layer
- Even vs odd n: center element (if odd) stays in place

**Follow-up:** Rotate 90 CCW? Transpose + reverse each column. Or reverse each row first, then transpose. Rotate 180? Reverse rows, then reverse row order.

---

### Problem 4: Search a 2D Matrix II (LC 240 — Medium)

**Problem:** Write an efficient algorithm to search for a target value in an m x n matrix where:
- Each row is sorted in ascending order
- Each column is sorted in ascending order

**Brute Force:**
Scan every cell. O(m * n).

**Better:** Binary search each row. O(m log n).

**Key Insight (Staircase search):**
Start at the top-right corner (or bottom-left). At position (r, c):
- If `matrix[r][c] == target`: found
- If `matrix[r][c] > target`: move left (eliminate column c — all values below are larger)
- If `matrix[r][c] < target`: move down (eliminate row r — all values to the left are smaller)

Each step eliminates a row or column, so at most m + n steps total.

**Optimal Solution:**

```python
def searchMatrix(matrix: list[list[int]], target: int) -> bool:
    """
    LC 240: Search a 2D Matrix II — Staircase Search

    Time: O(m + n)
    Space: O(1)
    """
    if not matrix or not matrix[0]:
        return False

    rows, cols = len(matrix), len(matrix[0])
    r, c = 0, cols - 1  # Start at top-right

    while r < rows and c >= 0:
        if matrix[r][c] == target:
            return True
        elif matrix[r][c] > target:
            c -= 1  # Eliminate this column
        else:
            r += 1  # Eliminate this row

    return False
```

**Dry Run:**
```
matrix = [[1,4,7,11,15],
          [2,5,8,12,19],
          [3,6,9,16,22],
          [10,13,14,17,24],
          [18,21,23,26,30]]
target = 5

Start: (0, 4) = 15. 15 > 5 → move left.
(0, 3) = 11. 11 > 5 → move left.
(0, 2) = 7. 7 > 5 → move left.
(0, 1) = 4. 4 < 5 → move down.
(1, 1) = 5. Found!
```

**Edge Cases:**
- Target smaller than all elements: quickly falls off top-left
- Target larger than all elements: quickly falls off bottom-right
- Single row or single column: degenerates to linear search (still O(m+n))
- Empty matrix

**Follow-up:** Search a 2D Matrix (LC 74) — rows are fully sorted (last element of row i < first element of row i+1). This allows treating the matrix as a flat sorted array and using binary search. O(log(mn)).

---

### Problem 5: Maximal Square (LC 221 — Medium)

**Problem:** Given an m x n binary matrix filled with '0's and '1's, find the largest square containing only '1's and return its area.

**Brute Force:**
For each cell, try all possible square sizes with that cell as top-left corner. Check if all cells in the square are '1'. O(m * n * min(m,n)^2).

**Key Insight (DP):**
`dp[i][j]` = side length of the largest square with its bottom-right corner at (i, j).

If `matrix[i][j] == '1'`:
`dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1`

Why the minimum of three neighbors? A square of side k with bottom-right at (i,j) requires:
- A square of side >= k-1 ending at (i-1, j) (above)
- A square of side >= k-1 ending at (i, j-1) (left)
- A square of side >= k-1 ending at (i-1, j-1) (diagonal)

The smallest of these three limits the square size.

```
  dp[i-1][j-1]  dp[i-1][j]

  dp[i][j-1]    dp[i][j] = min(↑, ←, ↖) + 1
```

**Optimal Solution:**

```python
def maximalSquare(matrix: list[list[str]]) -> int:
    """
    LC 221: Maximal Square

    Time: O(m * n)
    Space: O(n) with 1D DP optimization
    """
    if not matrix:
        return 0

    m, n = len(matrix), len(matrix[0])
    dp = [0] * (n + 1)  # 1-indexed to avoid boundary checks
    max_side = 0
    prev = 0  # dp[i-1][j-1]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            temp = dp[j]  # Save before overwriting (this becomes prev for next j)
            if matrix[i - 1][j - 1] == '1':
                dp[j] = min(dp[j], dp[j - 1], prev) + 1
                max_side = max(max_side, dp[j])
            else:
                dp[j] = 0
            prev = temp
        prev = 0  # Reset for new row (dp[-1][0] = 0)

    return max_side * max_side
```

**2D DP version (clearer):**

```python
def maximalSquare_2d(matrix: list[list[str]]) -> int:
    """LC 221: Maximal Square — 2D DP."""
    if not matrix:
        return 0

    m, n = len(matrix), len(matrix[0])
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    max_side = 0

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if matrix[i - 1][j - 1] == '1':
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1
                max_side = max(max_side, dp[i][j])

    return max_side * max_side
```

**Dry Run:**
```
matrix = [["1","0","1","0","0"],
          ["1","0","1","1","1"],
          ["1","1","1","1","1"],
          ["1","0","0","1","0"]]

dp (2D, 1-indexed):
Row 1: [0, 1, 0, 1, 0, 0]
Row 2: [0, 1, 0, 1, 1, 1]
Row 3: [0, 1, 1, 1, 2, 2]
Row 4: [0, 1, 0, 0, 1, 0]

max_side = 2 (at positions (3,4) and (3,5))
Area = 4
```

**Edge Cases:**
- All zeros: return 0
- All ones: return min(m, n)^2
- Single cell: 0 or 1
- Single row/column: max side is 1 if any '1' exists

**Follow-up:** Maximal Rectangle (LC 85) — use histogram approach (see Monotonic Stack guide). Count Square Submatrices with All Ones (LC 1277) — sum all dp values instead of tracking max.

---

### Problem 6: Shortest Path in a Grid with Obstacles Elimination (LC 1293 — Hard)

**Problem:** Given an m x n grid where 0 = empty and 1 = obstacle, find the shortest path from (0,0) to (m-1, n-1). You can eliminate at most k obstacles. Return the length of the shortest path, or -1 if not possible.

**Brute Force:**
Try all paths using DFS/backtracking, tracking obstacles eliminated. Exponential.

**Key Insight:**
BFS with extended state: `(row, col, obstacles_remaining)`. This is a state-space BFS where the state includes not just position but also how many obstacles you can still eliminate. Two visits to the same cell with different remaining obstacles are different states.

**Optimization:** If `k >= m + n - 3`, you can eliminate enough obstacles to take the direct Manhattan path. Return `m + n - 2`.

**Optimal Solution:**

```python
from collections import deque

def shortestPath(grid: list[list[int]], k: int) -> int:
    """
    LC 1293: Shortest Path in a Grid with Obstacles Elimination

    Time: O(m * n * k)
    Space: O(m * n * k)
    """
    m, n = len(grid), len(grid[0])

    # Early termination: if we can eliminate enough, go straight
    if k >= m + n - 3:
        return m + n - 2

    # BFS with state (row, col, remaining_eliminations)
    queue = deque([(0, 0, k, 0)])  # (r, c, remaining, distance)
    visited = {(0, 0, k)}

    while queue:
        r, c, remaining, dist = queue.popleft()

        if r == m - 1 and c == n - 1:
            return dist

        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n:
                new_remaining = remaining - grid[nr][nc]
                if new_remaining >= 0 and (nr, nc, new_remaining) not in visited:
                    visited.add((nr, nc, new_remaining))
                    queue.append((nr, nc, new_remaining, dist + 1))

    return -1
```

**Dry Run:**
```
grid = [[0,0,0],
        [1,1,0],
        [0,0,0],
        [0,1,1],
        [0,0,0]], k = 1

Without elimination: must go around obstacles.
With k=1: can eliminate one obstacle for a shorter path.

BFS explores states (r, c, remaining):
  Start: (0,0,1,0)
  → (0,1,1,1), (1,0,0,1) [eliminated grid[1][0]=1]
  → (0,2,1,2), (1,1,0,2) [grid[1][1]=1, but remaining=0, can't]
  Wait, from (1,0,0,1): can go to (2,0,0,2)
  ...

Path found: (0,0)→(0,1)→(0,2)→(1,2)→(2,2)→(2,1)→(2,0)→(3,0)→(4,0)→(4,1)→(4,2)
Length = 10 without elimination.

With k=1, can eliminate (3,1): (0,0)→(1,0)[elim]→(2,0)→(3,0)→(3,1)[elim?]
No, already used elimination. Let me try another path.

Actually: (0,0)→(0,1)→(0,2)→(1,2)→(2,2)→(2,1)→(2,0)→(3,0)→(4,0)→(4,1)→(4,2) = 10
Or: (0,0)→(0,1)→(0,2)→(1,2)→(2,2)→(3,2)[elim, grid=1]→(4,2) = 6

Result: 6
```

**Edge Cases:**
- Start or end is an obstacle: if k >= 1, can handle; otherwise -1
- k = 0: standard BFS, cannot pass through any obstacle
- Grid is all empty: m + n - 2
- 1x1 grid: return 0

**Follow-up:** What if different obstacles have different costs to eliminate? Use Dijkstra's algorithm (min-heap BFS) with the total elimination cost as the priority.

---

### Problem 7: Maximal Rectangle (LC 85 — Hard)

This problem is covered in detail in the Monotonic Stack guide. The approach: treat each row as the base of a histogram, compute histogram heights, and apply Largest Rectangle in Histogram (LC 84) for each row.

```python
def maximalRectangle(matrix: list[list[str]]) -> int:
    """LC 85: Maximal Rectangle — see Monotonic Stack guide for details."""
    if not matrix or not matrix[0]:
        return 0

    n = len(matrix[0])
    heights = [0] * n
    max_area = 0

    for row in matrix:
        for j in range(n):
            heights[j] = heights[j] + 1 if row[j] == '1' else 0

        # Largest rectangle in histogram
        stack = []
        heights_ext = heights + [0]
        for i in range(len(heights_ext)):
            while stack and heights_ext[i] < heights_ext[stack[-1]]:
                h = heights_ext[stack.pop()]
                w = i if not stack else i - stack[-1] - 1
                max_area = max(max_area, h * w)
            stack.append(i)

    return max_area
```

**Connection:** Maximal Square uses DP. Maximal Rectangle uses monotonic stack on histograms. Know when to apply each.

---

### Problem 8: Dungeon Game (LC 174 — Hard)

**Problem:** A knight starts at the top-left corner of an m x n grid and needs to reach the bottom-right princess. Each cell has a value (negative = damage, positive = health orb). The knight must have > 0 health at all times. Find the minimum initial health needed.

**Brute Force:**
Try all paths from top-left to bottom-right, track minimum health along each path. Exponential.

**Key Insight (DP from bottom-right to top-left):**
If we try DP from top-left, we need to track both the current health and the minimum health along the path — two dimensions. This is complex.

Instead, work backwards from the princess. Define `dp[i][j]` = minimum health needed when entering cell (i, j) to reach the princess alive.

At the princess cell (m-1, n-1):
`dp[m-1][n-1] = max(1, 1 - dungeon[m-1][n-1])`

For other cells:
`dp[i][j] = max(1, min(dp[i+1][j], dp[i][j+1]) - dungeon[i][j])`

We take the minimum of going down or right (we want to minimize starting health), then subtract the current cell's value (gain or damage).

**Optimal Solution:**

```python
def calculateMinimumHP(dungeon: list[list[int]]) -> int:
    """
    LC 174: Dungeon Game

    Time: O(m * n)
    Space: O(n) with 1D DP
    """
    m, n = len(dungeon), len(dungeon[0])
    dp = [float('inf')] * (n + 1)
    dp[n - 1] = 1  # Need at least 1 health to survive at princess

    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            # Minimum health needed to move right or down
            min_next = min(dp[j], dp[j + 1])
            dp[j] = max(1, min_next - dungeon[i][j])

    return dp[0]
```

**2D DP version (clearer):**

```python
def calculateMinimumHP_2d(dungeon: list[list[int]]) -> int:
    """LC 174: Dungeon Game — 2D DP."""
    m, n = len(dungeon), len(dungeon[0])
    dp = [[float('inf')] * (n + 1) for _ in range(m + 1)]
    dp[m][n - 1] = 1  # Boundary: need 1 health after last cell
    dp[m - 1][n] = 1

    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            min_next = min(dp[i + 1][j], dp[i][j + 1])
            dp[i][j] = max(1, min_next - dungeon[i][j])

    return dp[0][0]
```

**Dry Run:**
```
dungeon = [[-2, -3,  3],
           [-5, -10, 1],
           [10,  30, -5]]

Fill from bottom-right:
  dp[2][2] = max(1, 1-(-5)) = 6. Need 6 health entering (2,2) so that after -5 damage, still >= 1.
  dp[2][1] = max(1, 6-30) = max(1, -24) = 1. The +30 orb means you only need 1 health.
  dp[2][0] = max(1, 1-10) = max(1, -9) = 1. The +10 orb.
  dp[1][2] = max(1, 6-1) = 5.
  dp[1][1] = max(1, min(5, 1)-(-10)) = max(1, 1+10) = 11.
  dp[1][0] = max(1, min(11, 1)-(-5)) = max(1, 1+5) = 6.
  dp[0][2] = max(1, 5-3) = 2.
  dp[0][1] = max(1, min(2, 11)-(-3)) = max(1, 2+3) = 5.
  dp[0][0] = max(1, min(5, 6)-(-2)) = max(1, 5+2) = 7.

Result: 7. The knight needs 7 initial health.

Verify: Path (0,0)→(0,1)→(0,2)→(1,2)→(2,2)
  7 + (-2) = 5. 5 + (-3) = 2. 2 + 3 = 5. 5 + 1 = 6. 6 + (-5) = 1.
  Minimum along path = 1 > 0. Valid!
```

**Edge Cases:**
- Single cell positive: need 1 health
- Single cell negative: need `1 - value` health
- All positive: always need 1
- Very large grid: 1D DP keeps space O(n)

**Follow-up:** What if the knight can move in all 4 directions? Then DP does not work (no topological order). Use BFS or Dijkstra's with binary search on the initial health.

**Why reverse DP works but forward DP does not:**
Forward DP from (0,0) needs to track both the accumulated health AND the minimum health along the path. The optimal path depends on both quantities, leading to a 2D state (position + min health), which is expensive.

Reverse DP from (m-1, n-1) only needs to compute the minimum health required at each cell. Since we are going backwards, we know what the future demands are (from already-computed dp values), so a single value per cell suffices.

This is a general principle: when "what you need" depends on "what comes next," consider reversing the DP direction.

---

## Additional Problem: Word Search (LC 79 — Medium)

**Problem:** Given an m x n grid of characters and a string `word`, return true if the word can be found in the grid by moving horizontally or vertically to adjacent cells. Each cell may be used at most once.

**Key Insight:**
This is backtracking (DFS) on a grid. Start DFS from every cell that matches the first character. At each step, try all 4 directions. Mark cells as visited (temporarily modify grid) and unmark on backtrack.

```python
def exist(board: list[list[str]], word: str) -> bool:
    """
    LC 79: Word Search

    Time: O(m * n * 3^L) where L = word length (3 directions after first step)
    Space: O(L) for recursion stack
    """
    m, n = len(board), len(board[0])

    def dfs(r, c, idx):
        if idx == len(word):
            return True
        if (r < 0 or r >= m or c < 0 or c >= n
                or board[r][c] != word[idx]):
            return False

        # Mark as visited
        temp = board[r][c]
        board[r][c] = '#'

        # Try all 4 directions
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            if dfs(r + dr, c + dc, idx + 1):
                board[r][c] = temp  # Restore before returning
                return True

        # Backtrack
        board[r][c] = temp
        return False

    for r in range(m):
        for c in range(n):
            if dfs(r, c, 0):
                return True
    return False
```

**Optimization:** Before starting DFS, check if all characters in `word` exist in `board` with sufficient frequency. This early termination avoids expensive backtracking for impossible cases.

---

## Additional Problem: Rotting Oranges (LC 994 — Medium)

**Problem:** In a grid, 0 = empty, 1 = fresh orange, 2 = rotten orange. Every minute, rotten oranges spread to adjacent fresh oranges. Return the minimum minutes until no fresh oranges remain, or -1 if impossible.

**Key Insight:**
Multi-source BFS from all initially rotten oranges. Each BFS level = one minute.

```python
from collections import deque

def orangesRotting(grid: list[list[int]]) -> int:
    """
    LC 994: Rotting Oranges

    Time: O(m * n)
    Space: O(m * n)
    """
    m, n = len(grid), len(grid[0])
    queue = deque()
    fresh = 0

    for r in range(m):
        for c in range(n):
            if grid[r][c] == 2:
                queue.append((r, c))
            elif grid[r][c] == 1:
                fresh += 1

    if fresh == 0:
        return 0

    minutes = 0
    while queue:
        minutes += 1
        for _ in range(len(queue)):
            r, c = queue.popleft()
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    queue.append((nr, nc))

    return minutes - 1 if fresh == 0 else -1
```

**Why `minutes - 1`?** The last iteration of the while loop processes the final layer of newly rotten oranges but does not actually rot any new ones. We counted one extra minute.

---

## Common Mistakes & Interview Tips

### Common Mistakes

1. **Off-by-one in boundary checks:** `0 <= r < rows` not `0 <= r <= rows`. This is the most common grid bug.

2. **Not marking visited before enqueueing (BFS):** If you mark visited when dequeuing instead of when enqueueing, you may add the same cell to the queue multiple times, causing TLE and incorrect results.

3. **Modifying input grid as visited marker:** This works but can lose information. If the grid values are needed later, use a separate visited set.

4. **Wrong DP direction:** Dungeon Game requires bottom-right to top-left. Minimum Path Sum requires top-left to bottom-right. Getting the direction wrong gives incorrect results.

5. **Forgetting to handle non-square matrices:** Many matrix manipulation tricks (rotation, transposition) only work for square matrices. Spiral traversal works for any shape.

6. **Spiral traversal boundary conditions:** After going right and down, check `if top <= bottom` before going left, and `if left <= right` before going up. Without these checks, you may double-count elements for single-row or single-column matrices.

### Interview Tips

1. **State the grid dimensions first:** "Let me define m = rows and n = cols." This avoids confusion throughout the solution.

2. **Define the direction array early:** `directions = [(0,1),(0,-1),(1,0),(-1,0)]`. This shows clean coding style and avoids repetitive code.

3. **For BFS: use the (row, col, dist) tuple pattern.** It is cleaner than tracking distance separately.

4. **For DP on grids: clearly state the DP definition.** "dp[i][j] represents the maximum side length of a square ending at (i,j)" or "dp[i][j] is the minimum health needed entering cell (i,j)."

5. **Mention space optimization:** "I can optimize from O(mn) to O(n) space by using a single row of DP since each cell only depends on the current and previous rows."

6. **For matrix manipulation:** Draw the indices. Rotation, transposition, and spiral traversal are easy to get wrong without a diagram. Take 30 seconds to draw a 3x3 example.

---

## Pattern Connections

| From Matrix/Grid | Connect To | How |
|-----------------|-----------|-----|
| Number of Islands | DFS/BFS, Union-Find | Grid connected components |
| Shortest Path w/ Obstacles | BFS with state | State = (pos, obstacles_left) |
| Maximal Square | DP | min(top, left, diagonal) + 1 |
| Maximal Rectangle | Monotonic Stack | Row-by-row histogram |
| Spiral Matrix | Simulation | Boundary tracking |
| Rotate Image | Matrix transpose | Transpose + reverse |
| Search 2D Matrix II | Binary Search / Staircase | Exploit sorted structure |
| Dungeon Game | DP (reverse direction) | Bottom-right to top-left |
| Word Search | Backtracking on grid | DFS with visited tracking |
| 01 Matrix (LC 542) | Multi-source BFS | BFS from all 0s simultaneously |

### Decision Framework

```
Grid/Matrix problem?
├── Shortest path (unweighted)?
│   ├── Simple: BFS
│   └── With state (obstacles, keys): State-space BFS
├── Connected components / flood fill?
│   ├── DFS (simpler, recursive)
│   └── Union-Find (if dynamic)
├── Optimization (max/min value, counting)?
│   └── DP on grid
│       ├── Top-left → bottom-right: paths, min sum
│       └── Bottom-right → top-left: Dungeon Game
├── Find element in sorted matrix?
│   ├── Row + column sorted: Staircase O(m+n)
│   └── Fully sorted: Binary search O(log mn)
├── Matrix manipulation?
│   ├── Rotate: Transpose + reverse
│   ├── Spiral: Boundary tracking
│   └── Set zeroes: Use first row/col as markers
└── Maximal shape?
    ├── Square: DP
    └── Rectangle: Monotonic stack on histograms
```

---

## Additional Problem: Unique Paths (LC 62 — Medium)

**Problem:** A robot is located at the top-left corner of an m x n grid and can only move right or down. How many unique paths exist to the bottom-right corner?

**Key Insight:**
`dp[i][j]` = number of ways to reach cell (i, j). Since we can only come from above or from the left: `dp[i][j] = dp[i-1][j] + dp[i][j-1]`.

```python
def uniquePaths(m: int, n: int) -> int:
    """
    LC 62: Unique Paths

    Time: O(m * n)
    Space: O(n) with 1D DP
    """
    dp = [1] * n  # First row: all 1 (only one way to reach any cell in first row)
    for i in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j - 1]
    return dp[n - 1]
```

**Math solution:** This is choosing (m-1) downs and (n-1) rights from a total of (m+n-2) moves: C(m+n-2, m-1).

```python
from math import comb
def uniquePaths_math(m, n):
    return comb(m + n - 2, m - 1)
```

---

## Additional Problem: Minimum Path Sum (LC 64 — Medium)

**Problem:** Given an m x n grid filled with non-negative numbers, find a path from top-left to bottom-right that minimizes the sum. Can only move right or down.

```python
def minPathSum(grid: list[list[int]]) -> int:
    """
    LC 64: Minimum Path Sum

    Time: O(m * n)
    Space: O(n) with 1D DP
    """
    m, n = len(grid), len(grid[0])
    dp = [float('inf')] * n
    dp[0] = 0

    for i in range(m):
        dp[0] += grid[i][0]
        for j in range(1, n):
            if i == 0:
                dp[j] = dp[j - 1] + grid[i][j]
            else:
                dp[j] = min(dp[j], dp[j - 1]) + grid[i][j]

    return dp[n - 1]
```

---

## Additional Problem: Pacific Atlantic Water Flow (LC 417 — Medium)

**Problem:** Given an m x n matrix of heights, water can flow from a cell to an adjacent cell (4-directional) if the adjacent cell's height is <= current cell's height. Water can flow to the Pacific ocean (top/left borders) and the Atlantic ocean (bottom/right borders). Find all cells from which water can reach both oceans.

**Key Insight:**
Instead of flowing water downhill from each cell (expensive), flow water uphill from each ocean. Do a BFS/DFS from all Pacific border cells and all Atlantic border cells separately. Cells reachable from both are the answer.

```python
from collections import deque

def pacificAtlantic(heights: list[list[int]]) -> list[list[int]]:
    """
    LC 417: Pacific Atlantic Water Flow

    Time: O(m * n)
    Space: O(m * n)
    """
    if not heights:
        return []
    m, n = len(heights), len(heights[0])

    def bfs(starts):
        reachable = set(starts)
        queue = deque(starts)
        while queue:
            r, c = queue.popleft()
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if (0 <= nr < m and 0 <= nc < n
                        and (nr, nc) not in reachable
                        and heights[nr][nc] >= heights[r][c]):  # Flow uphill
                    reachable.add((nr, nc))
                    queue.append((nr, nc))
        return reachable

    # Pacific: top row + left column
    pacific_starts = [(0, c) for c in range(n)] + [(r, 0) for r in range(1, m)]
    # Atlantic: bottom row + right column
    atlantic_starts = [(m-1, c) for c in range(n)] + [(r, n-1) for r in range(m-1)]

    pacific = bfs(pacific_starts)
    atlantic = bfs(atlantic_starts)

    return [[r, c] for r, c in pacific & atlantic]
```

This demonstrates the "reverse BFS" technique — instead of searching from every cell to the boundary, search from the boundary inward. This reduces complexity from O(m^2 * n^2) to O(m * n).

---

## Interview Cheat Sheet

**Grid problem template setup (write this first):**
```python
m, n = len(grid), len(grid[0])
dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]

def in_bounds(r, c):
    return 0 <= r < m and 0 <= c < n
```

**BFS template (shortest path):**
```python
from collections import deque
queue = deque([(start_r, start_c, 0)])
visited = {(start_r, start_c)}
while queue:
    r, c, dist = queue.popleft()
    if (r, c) == target: return dist
    for dr, dc in dirs:
        nr, nc = r + dr, c + dc
        if in_bounds(nr, nc) and (nr, nc) not in visited and grid[nr][nc] != WALL:
            visited.add((nr, nc))
            queue.append((nr, nc, dist + 1))
return -1
```

**DFS template (connected components):**
```python
def dfs(r, c):
    if not in_bounds(r, c) or grid[r][c] != TARGET:
        return
    grid[r][c] = VISITED
    for dr, dc in dirs:
        dfs(r + dr, c + dc)
```

**Five things to say when solving grid problems:**
1. "Let me define m = rows, n = cols, and set up the direction array."
2. "I use BFS for shortest path / DFS for connected components."
3. "I mark cells as visited when adding to the queue, not when processing, to avoid duplicates."
4. "For the DP approach, dp[i][j] represents [state definition], and transitions come from [neighbors]."
5. "I can optimize space from O(mn) to O(n) since each cell only depends on the current and previous rows."
