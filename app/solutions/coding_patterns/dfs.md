# Depth-First Search (DFS) Pattern Guide

## What is DFS?

### Explain Like I'm 5
Imagine you're in a huge maze with many paths. Instead of trying to look at all paths at once, you pick ONE path and follow it as far as you can go. When you hit a dead end, you backtrack (go back) to the last place where you had a choice, and try a different path. You keep doing this until you've explored everything or found what you're looking for.

It's like reading a "Choose Your Own Adventure" book where you follow one storyline all the way to the end, then go back and try different choices.

### Technical Definition
Depth-First Search (DFS) is a graph/tree traversal algorithm that explores as far as possible along each branch before backtracking. It uses a stack data structure (either explicitly or implicitly through recursion) to keep track of vertices to visit. DFS visits a node, then recursively visits all its unvisited neighbors before moving to the next branch.

## Real-World Analogy

### The Cave Explorer
Imagine you're exploring a cave system with multiple tunnels:

1. You enter the cave and mark the entrance with chalk (visited)
2. You see 3 tunnels - you pick the LEFT one and go deep
3. That tunnel splits into 2 more tunnels - you pick one and keep going deeper
4. You reach a dead end (no more tunnels)
5. You backtrack to the last split and try the OTHER tunnel
6. You keep exploring deeper until you've checked every possible path
7. Then you backtrack all the way and try the MIDDLE tunnel from the entrance
8. Finally, you try the RIGHT tunnel

This is DFS - you go DEEP first, then WIDE.

### Solving a Maze
When solving a maze, you might:
- Follow one path until you hit a wall
- Backtrack and try another path
- Mark visited areas so you don't go in circles
- Eventually, you've explored all possible routes

## When to Use DFS

DFS is your go-to pattern when you see these signals:

✅ **Use DFS when:**
- You need to visit **ALL nodes** in a graph/tree
- You're looking for a **path** between two nodes
- You need to detect **cycles** in a graph
- You're exploring **all possible solutions** (permutations, combinations)
- The problem involves **backtracking** (N-Queens, Sudoku)
- You need to check if a graph is **connected**
- You're working with **tree traversal** (preorder, inorder, postorder)
- You need to find **connected components** (islands, regions)
- The problem mentions "explore all paths" or "find all solutions"
- You're working with **maze problems** or **grid exploration**

🚫 **DON'T use DFS when:**
- You need the **shortest path** (use BFS instead)
- You're working with an **infinite graph** (DFS can go infinitely deep)
- You need to explore level-by-level (use BFS)

## The Problem: Number of Islands

**Problem Statement:**
Given a 2D grid map of `'1'`s (land) and `'0'`s (water), count the number of islands. An island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically. You may assume all four edges of the grid are surrounded by water.

**Example:**
```
Input: grid = [
  ["1","1","0","0","0"],
  ["1","1","0","0","0"],
  ["0","0","1","0","0"],
  ["0","0","0","1","1"]
]
Output: 3

Explanation:
Island 1: Top-left corner (2x2 block of 1s)
Island 2: Middle (single 1)
Island 3: Bottom-right corner (2 connected 1s)
```

## Brute Force Approach

A naive approach might be to:
1. Check every cell one by one
2. For each '1', manually trace all connected cells
3. Use a separate 2D array to track what we've counted
4. Count duplicates multiple times

This would be inefficient and error-prone. We'd revisit the same cells multiple times and have complex logic to avoid double-counting.

## Optimized Solution: DFS Approach

### Solution 1: Recursive DFS (Most Common)

```python
def numIslands(grid):
    """
    Count the number of islands using recursive DFS.

    Time Complexity: O(M * N) where M = rows, N = cols
    Space Complexity: O(M * N) worst case for recursion stack
    """
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    island_count = 0

    def dfs(row, col):
        """
        Recursive DFS to mark all cells of current island as visited.
        We modify the grid in-place, changing '1' to '0' to mark as visited.
        """
        # Base case: out of bounds
        if row < 0 or row >= rows or col < 0 or col >= cols:
            return

        # Base case: water or already visited
        if grid[row][col] == '0':
            return

        # Mark current cell as visited by changing it to water
        grid[row][col] = '0'

        # Explore all 4 directions: up, down, left, right
        # This is the "going deeper" part of DFS
        dfs(row - 1, col)  # Up
        dfs(row + 1, col)  # Down
        dfs(row, col - 1)  # Left
        dfs(row, col + 1)  # Right

    # Iterate through every cell in the grid
    for row in range(rows):
        for col in range(cols):
            # If we find unvisited land ('1')
            if grid[row][col] == '1':
                # We found a new island!
                island_count += 1
                # Use DFS to mark all connected land as visited
                # This ensures we don't count the same island multiple times
                dfs(row, col)

    return island_count


# Example usage:
grid = [
    ["1","1","0","0","0"],
    ["1","1","0","0","0"],
    ["0","0","1","0","0"],
    ["0","0","0","1","1"]
]
print(numIslands(grid))  # Output: 3
```

### Solution 2: Iterative DFS with Explicit Stack

```python
def numIslands_iterative(grid):
    """
    Count islands using iterative DFS with an explicit stack.
    This avoids potential stack overflow for very large grids.

    Time Complexity: O(M * N)
    Space Complexity: O(min(M, N)) for the stack
    """
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    island_count = 0

    def dfs_iterative(start_row, start_col):
        """
        Iterative DFS using an explicit stack.
        Stack holds (row, col) tuples to visit.
        """
        # Initialize stack with starting position
        stack = [(start_row, start_col)]

        while stack:
            # Pop from stack (LIFO - Last In First Out)
            row, col = stack.pop()

            # Skip if out of bounds
            if row < 0 or row >= rows or col < 0 or col >= cols:
                continue

            # Skip if water or already visited
            if grid[row][col] == '0':
                continue

            # Mark as visited
            grid[row][col] = '0'

            # Add all 4 neighbors to stack
            # Order doesn't matter for counting islands,
            # but affects traversal order
            stack.append((row - 1, col))  # Up
            stack.append((row + 1, col))  # Down
            stack.append((row, col - 1))  # Left
            stack.append((row, col + 1))  # Right

    # Main loop: check every cell
    for row in range(rows):
        for col in range(cols):
            if grid[row][col] == '1':
                island_count += 1
                dfs_iterative(row, col)

    return island_count
```

### Solution 3: DFS with Separate Visited Set (Non-Destructive)

```python
def numIslands_with_visited(grid):
    """
    Count islands using DFS with a separate visited set.
    This preserves the original grid.

    Time Complexity: O(M * N)
    Space Complexity: O(M * N) for visited set + recursion
    """
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    visited = set()  # Store (row, col) tuples
    island_count = 0

    def dfs(row, col):
        """DFS with visited tracking."""
        # Out of bounds check
        if row < 0 or row >= rows or col < 0 or col >= cols:
            return

        # Already visited or water
        if (row, col) in visited or grid[row][col] == '0':
            return

        # Mark as visited
        visited.add((row, col))

        # Explore neighbors
        dfs(row - 1, col)
        dfs(row + 1, col)
        dfs(row, col - 1)
        dfs(row, col + 1)

    for row in range(rows):
        for col in range(cols):
            if grid[row][col] == '1' and (row, col) not in visited:
                island_count += 1
                dfs(row, col)

    return island_count
```

## Time & Space Complexity Analysis

### Time Complexity: O(M × N)
- **M** = number of rows
- **N** = number of columns
- We visit each cell **at most once**
- For each cell, we do constant work (check boundaries, mark visited)
- Even though DFS is recursive, each cell is processed only once
- Total operations: M × N cells × O(1) work per cell = **O(M × N)**

### Space Complexity Analysis

**Recursive DFS:**
- **Worst Case: O(M × N)** for the recursion call stack
- This happens when the entire grid is land in a snake-like pattern
- The recursion would go M × N levels deep
- Example worst case:
  ```
  1-1-1
      |
  1-1-1
  |
  1-1-1
  ```
- **Best Case: O(min(M, N))** when the grid is square and balanced

**Iterative DFS:**
- **Worst Case: O(min(M, N))** for the explicit stack
- More space-efficient than recursive version
- Stack size is bounded by the "width" of the search

**General Graph DFS:**
- **Time: O(V + E)** where V = vertices, E = edges
- Visit each vertex once: O(V)
- Explore each edge once: O(E)
- **Space: O(V)** for visited set + O(H) for recursion stack where H is height

## Variations of DFS

### 1. DFS on Binary Tree

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def dfs_preorder(root):
    """Preorder: Root -> Left -> Right"""
    if not root:
        return []

    result = []
    result.append(root.val)           # Visit root first
    result.extend(dfs_preorder(root.left))   # Then left subtree
    result.extend(dfs_preorder(root.right))  # Then right subtree
    return result

def dfs_inorder(root):
    """Inorder: Left -> Root -> Right (gives sorted order in BST)"""
    if not root:
        return []

    result = []
    result.extend(dfs_inorder(root.left))    # Left subtree first
    result.append(root.val)                  # Then root
    result.extend(dfs_inorder(root.right))   # Then right subtree
    return result

def dfs_postorder(root):
    """Postorder: Left -> Right -> Root (useful for deletion)"""
    if not root:
        return []

    result = []
    result.extend(dfs_postorder(root.left))   # Left subtree
    result.extend(dfs_postorder(root.right))  # Right subtree
    result.append(root.val)                   # Root last
    return result
```

### 2. DFS on Graph (Adjacency List)

```python
def dfs_graph(graph, start):
    """
    DFS on a graph represented as adjacency list.
    graph = {node: [neighbor1, neighbor2, ...]}
    """
    visited = set()
    result = []

    def dfs(node):
        if node in visited:
            return

        visited.add(node)
        result.append(node)

        # Visit all neighbors
        for neighbor in graph.get(node, []):
            dfs(neighbor)

    dfs(start)
    return result

# Example:
graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': [],
    'E': ['F'],
    'F': []
}
print(dfs_graph(graph, 'A'))  # Output: ['A', 'B', 'D', 'E', 'F', 'C']
```

### 3. DFS for Cycle Detection

```python
def has_cycle(graph):
    """
    Detect cycle in directed graph using DFS.
    Uses 3 colors: white (unvisited), gray (visiting), black (done)
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}

    def dfs(node):
        if color[node] == GRAY:
            # Found a back edge - cycle detected!
            return True

        if color[node] == BLACK:
            # Already processed
            return False

        # Mark as currently visiting
        color[node] = GRAY

        # Visit neighbors
        for neighbor in graph.get(node, []):
            if dfs(neighbor):
                return True

        # Mark as completely processed
        color[node] = BLACK
        return False

    # Check all nodes (graph might be disconnected)
    for node in graph:
        if color[node] == WHITE:
            if dfs(node):
                return True

    return False

# Example with cycle:
graph_with_cycle = {
    'A': ['B'],
    'B': ['C'],
    'C': ['A']  # Creates cycle: A -> B -> C -> A
}
print(has_cycle(graph_with_cycle))  # True
```

### 4. DFS on Grid (8 Directions)

```python
def dfs_grid_8_directions(grid, row, col):
    """
    DFS exploring all 8 directions (including diagonals).
    Useful for problems like word search or minesweeper.
    """
    if not grid or not grid[0]:
        return

    rows, cols = len(grid), len(grid[0])
    visited = set()

    # 8 directions: up, down, left, right, and 4 diagonals
    directions = [
        (-1, 0),   # Up
        (1, 0),    # Down
        (0, -1),   # Left
        (0, 1),    # Right
        (-1, -1),  # Top-left diagonal
        (-1, 1),   # Top-right diagonal
        (1, -1),   # Bottom-left diagonal
        (1, 1)     # Bottom-right diagonal
    ]

    def dfs(r, c):
        if (r < 0 or r >= rows or c < 0 or c >= cols or
            (r, c) in visited or grid[r][c] == 0):
            return

        visited.add((r, c))

        # Explore all 8 directions
        for dr, dc in directions:
            dfs(r + dr, c + dc)

    dfs(row, col)
    return visited
```

### 5. DFS for Path Finding

```python
def find_all_paths(graph, start, end):
    """
    Find all paths from start to end using DFS.
    Returns list of all possible paths.
    """
    all_paths = []
    current_path = []

    def dfs(node):
        # Add current node to path
        current_path.append(node)

        # Found the destination
        if node == end:
            # Important: append a COPY of current_path
            all_paths.append(current_path[:])
        else:
            # Explore neighbors
            for neighbor in graph.get(node, []):
                # Avoid cycles in current path
                if neighbor not in current_path:
                    dfs(neighbor)

        # Backtrack: remove node from current path
        current_path.pop()

    dfs(start)
    return all_paths

# Example:
graph = {
    'A': ['B', 'C'],
    'B': ['D'],
    'C': ['D'],
    'D': ['E'],
    'E': []
}
print(find_all_paths(graph, 'A', 'E'))
# Output: [['A', 'B', 'D', 'E'], ['A', 'C', 'D', 'E']]
```

## Pro Tips for Senior Engineers

### 1. Recursive vs Iterative DFS
```python
# Recursive: Cleaner, more intuitive
# Cons: Stack overflow risk for deep recursion (Python limit ~1000)
def recursive_dfs(node):
    if not node:
        return
    process(node)
    recursive_dfs(node.left)
    recursive_dfs(node.right)

# Iterative: More control, no stack overflow
# Cons: Slightly more code
def iterative_dfs(root):
    if not root:
        return
    stack = [root]
    while stack:
        node = stack.pop()
        process(node)
        if node.right:  # Push right first (will be processed last)
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
```

**When to choose:**
- **Recursive:** Most interview problems, cleaner code, smaller inputs
- **Iterative:** Very large inputs, production code, need fine control

### 2. In-Place Modification vs Visited Set

```python
# In-place: Saves space, but destroys original data
def dfs_inplace(grid, r, c):
    grid[r][c] = '0'  # Modify original grid
    # ... explore neighbors

# Visited set: Preserves data, uses extra space
def dfs_visited(grid, r, c, visited):
    visited.add((r, c))
    # ... explore neighbors
```

**Trade-off:**
- In-place: O(1) extra space but mutates input
- Visited set: O(V) space but preserves input
- Interview tip: Ask interviewer if you can modify the input!

### 3. Edge Cases to Handle

```python
def robust_dfs(grid):
    # Edge case 1: Empty input
    if not grid or not grid[0]:
        return 0

    # Edge case 2: Single cell
    if len(grid) == 1 and len(grid[0]) == 1:
        return 1 if grid[0][0] == '1' else 0

    # Edge case 3: All water
    # Edge case 4: All land
    # Edge case 5: Disconnected components

    # Your DFS logic here
    pass
```

### 4. DFS vs BFS - When to Use What

| Criteria | DFS | BFS |
|----------|-----|-----|
| **Shortest Path** | ❌ No | ✅ Yes |
| **All Paths** | ✅ Yes | ❌ Harder |
| **Memory** | O(height) | O(width) |
| **Use Cases** | Topological sort, cycle detection, maze solving | Shortest path, level-order, peer nodes |
| **Implementation** | Recursion or stack | Queue |

### 5. When NOT to Use DFS

❌ **Shortest path in unweighted graph** → Use BFS
❌ **Infinite graphs** → DFS can go infinitely deep
❌ **Level-by-level processing** → Use BFS
❌ **Finding closest node** → Use BFS
❌ **Weighted graphs** → Use Dijkstra or A*

### 6. Interview Gotchas

**Gotcha 1: Forgetting to mark as visited**
```python
# Wrong: Infinite recursion!
def dfs_wrong(grid, r, c):
    if grid[r][c] == '0':
        return
    # Missing: grid[r][c] = '0'
    dfs_wrong(grid, r-1, c)  # Can revisit same cell!

# Correct:
def dfs_correct(grid, r, c):
    if grid[r][c] == '0':
        return
    grid[r][c] = '0'  # Mark visited BEFORE recursion
    dfs_correct(grid, r-1, c)
```

**Gotcha 2: Boundary checks order matters**
```python
# Wrong: Can cause index out of bounds!
def dfs_wrong(grid, r, c):
    if grid[r][c] == '0':  # Crashes if r, c out of bounds!
        return

# Correct: Check bounds FIRST
def dfs_correct(grid, r, c):
    if r < 0 or r >= len(grid) or c < 0 or c >= len(grid[0]):
        return
    if grid[r][c] == '0':
        return
```

**Gotcha 3: Modifying list while iterating**
```python
# Wrong: Can cause bugs
for neighbor in graph[node]:
    if should_remove:
        graph[node].remove(neighbor)  # Modifying while iterating!

# Correct: Iterate over copy
for neighbor in list(graph[node]):
    if should_remove:
        graph[node].remove(neighbor)
```

## Problem Recognition: How to Spot DFS Patterns

Look for these keywords in problem statements:

🔍 **Pattern Signals:**
- "Find **all** possible solutions"
- "**Explore** all paths"
- "**Connected components**"
- "**Islands** / regions / clusters"
- "**Maze** / grid navigation"
- "Can you reach from A to B"
- "Detect **cycles**"
- "**Backtracking**" (N-Queens, Sudoku, permutations)
- "Tree **traversal**"
- "**Topological** sort"
- "**Path finding** (not shortest)"

### Pattern Recognition Examples

**Example 1: "Number of Islands"**
- Keywords: "connected", "adjacent", "grid"
- Pattern: DFS to explore connected components
- Solution: DFS from each unvisited land cell

**Example 2: "Course Schedule"**
- Keywords: "prerequisites", "directed graph", "cycle"
- Pattern: DFS for cycle detection
- Solution: DFS with 3-color marking

**Example 3: "Word Search"**
- Keywords: "grid", "path", "backtracking"
- Pattern: DFS with backtracking
- Solution: DFS exploring all 4 directions with visited tracking

**Example 4: "Clone Graph"**
- Keywords: "graph", "copy", "connected"
- Pattern: DFS to traverse and copy
- Solution: DFS with HashMap to store cloned nodes

## Practice Problems

### Easy Level
1. **Maximum Depth of Binary Tree** (LeetCode 104)
   - Simple tree DFS, good starting point
   - Practice: Recursive DFS returning max depth

2. **Path Sum** (LeetCode 112)
   - DFS with target sum tracking
   - Practice: DFS with cumulative state

3. **Invert Binary Tree** (LeetCode 226)
   - Tree DFS with modification
   - Practice: DFS with node swapping

### Medium Level
4. **Number of Islands** (LeetCode 200)
   - Classic grid DFS, must-know problem
   - Practice: DFS on 2D grid with visited tracking

5. **Course Schedule** (LeetCode 207)
   - Cycle detection in directed graph
   - Practice: DFS with 3-color marking

6. **Word Search** (LeetCode 79)
   - Grid DFS with backtracking
   - Practice: DFS with path tracking and backtracking

7. **Clone Graph** (LeetCode 133)
   - Graph DFS with HashMap
   - Practice: DFS with node copying

8. **Pacific Atlantic Water Flow** (LeetCode 417)
   - Multi-source DFS on grid
   - Practice: DFS from multiple starting points

### Hard Level
9. **Word Search II** (LeetCode 212)
   - DFS + Trie, very common in interviews
   - Practice: Combining DFS with advanced data structures

10. **Longest Increasing Path in Matrix** (LeetCode 329)
    - DFS with memoization (DP)
    - Practice: DFS with caching results

11. **Serialize and Deserialize Binary Tree** (LeetCode 297)
    - DFS for tree serialization
    - Practice: DFS with string building

## Common Mistakes

### Mistake 1: Infinite Recursion
```python
# WRONG: No visited check
def dfs_bad(graph, node):
    for neighbor in graph[node]:
        dfs_bad(graph, neighbor)  # Can revisit nodes infinitely!

# CORRECT: Track visited nodes
def dfs_good(graph, node, visited):
    if node in visited:
        return
    visited.add(node)
    for neighbor in graph[node]:
        dfs_good(graph, neighbor, visited)
```

### Mistake 2: Forgetting Base Cases
```python
# WRONG: No termination condition
def dfs_bad(root):
    process(root.val)
    dfs_bad(root.left)   # Crashes when root.left is None!
    dfs_bad(root.right)

# CORRECT: Check for None
def dfs_good(root):
    if not root:  # Base case
        return
    process(root.val)
    dfs_good(root.left)
    dfs_good(root.right)
```

### Mistake 3: Wrong Boundary Checks
```python
# WRONG: Checking grid value before bounds
def dfs_bad(grid, r, c):
    if grid[r][c] == '0':  # Index error if r or c out of bounds!
        return

# CORRECT: Check bounds first
def dfs_good(grid, r, c):
    if r < 0 or r >= len(grid) or c < 0 or c >= len(grid[0]):
        return
    if grid[r][c] == '0':
        return
```

### Mistake 4: Not Backtracking in Path Problems
```python
# WRONG: Doesn't backtrack, can't explore all paths
def find_paths_bad(graph, node, path, all_paths):
    path.append(node)
    if is_target(node):
        all_paths.append(path)
    for neighbor in graph[node]:
        find_paths_bad(graph, neighbor, path, all_paths)
    # Missing: path.pop() to backtrack!

# CORRECT: Backtrack after exploring
def find_paths_good(graph, node, path, all_paths):
    path.append(node)
    if is_target(node):
        all_paths.append(path[:])  # Copy path!
    for neighbor in graph[node]:
        if neighbor not in path:  # Avoid cycles
            find_paths_good(graph, neighbor, path, all_paths)
    path.pop()  # Backtrack
```

### Mistake 5: Shallow Copy Issues
```python
# WRONG: All paths reference same list
all_paths = []
current_path = []

def dfs_bad(node):
    current_path.append(node)
    if is_target:
        all_paths.append(current_path)  # All point to same list!

# CORRECT: Deep copy when saving
def dfs_good(node):
    current_path.append(node)
    if is_target:
        all_paths.append(current_path[:])  # Create new list
    current_path.pop()
```

### Mistake 6: Using BFS When You Need DFS
```python
# WRONG: Using BFS for "find all paths"
# BFS explores level by level, doesn't maintain path easily

# CORRECT: Use DFS for exploring all paths
# DFS naturally maintains path through recursion stack
```

### Mistake 7: Stack Overflow with Deep Recursion
```python
# PROBLEM: Python's recursion limit is ~1000
# For very deep trees/graphs, recursive DFS fails

# SOLUTION: Use iterative DFS with explicit stack
def dfs_iterative(root):
    stack = [root]
    while stack:
        node = stack.pop()
        process(node)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
```

---

## Summary: DFS Quick Reference

**Core Idea:** Go deep first, backtrack when you hit a dead end

**Time Complexity:** O(V + E) for graphs, O(M × N) for grids

**Space Complexity:** O(height) for recursion stack

**When to Use:**
- Finding all paths/solutions
- Cycle detection
- Connected components
- Tree traversal
- Backtracking problems

**When NOT to Use:**
- Shortest path (use BFS)
- Level-by-level processing (use BFS)

**Key Template:**
```python
def dfs(node, visited):
    if base_case:
        return

    visited.add(node)

    for neighbor in get_neighbors(node):
        if neighbor not in visited:
            dfs(neighbor, visited)
```

**Remember:** Mark visited BEFORE recursion, check bounds FIRST, and don't forget to backtrack in path-finding problems!
