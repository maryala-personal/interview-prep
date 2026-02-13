# Breadth-First Search (BFS) Pattern Guide

## 1. What is BFS?

### Explain Like I'm 5
Imagine you're standing in the middle of a pond and you throw a pebble into the water. The ripples spread out in circles - first the closest ring forms, then the next ring, then the next. BFS explores data the same way - it visits all the neighbors at the current "distance" before moving to the next level.

Think of it like exploring a building floor by floor. You explore every room on the 1st floor completely before going to the 2nd floor. Then you explore every room on the 2nd floor before going to the 3rd floor.

### Technical Definition
BFS is a graph/tree traversal algorithm that explores nodes level by level, visiting all nodes at distance `k` from the source before visiting any nodes at distance `k+1`. It uses a **queue** (First-In-First-Out) data structure to maintain the order of exploration.

## 2. Real-World Analogy

### The Movie Theater Evacuation
Imagine a fire alarm goes off in a movie theater. The evacuation happens in waves:
- **Wave 1**: People nearest to the exit leave first
- **Wave 2**: People one row back leave next
- **Wave 3**: People two rows back follow

This is exactly how BFS works - it processes items in waves based on their distance from the starting point.

### Google Maps Shortest Route
When you search for directions on Google Maps, it explores routes in expanding circles from your location, finding the shortest path to your destination. It doesn't go all the way down one route before trying others - it explores all nearby possibilities first.

## 3. When to Use BFS

BFS is your go-to algorithm when you see these signals:

- **"Shortest path"** in an unweighted graph/grid
- **"Level order"** traversal of a tree
- **"Minimum number of steps/moves"** to reach somewhere
- **"Nearest/closest"** element or node
- **"Layer by layer"** or "level by level" processing
- **Problems involving spreading/propagation** (e.g., rotting oranges, virus spread)
- **Finding all nodes within k distance**
- **Connected components** in a graph

**Red Flags for BFS:**
- The problem mentions "shortest path" or "minimum steps"
- You need to explore neighbors before going deeper
- The graph is unweighted (all edges have the same cost)

## 4. The Problem: Binary Tree Level Order Traversal

**LeetCode 102 - Binary Tree Level Order Traversal**

Given the root of a binary tree, return the level order traversal of its nodes' values (i.e., from left to right, level by level).

**Example:**
```
Input:
       3
      / \
     9  20
       /  \
      15   7

Output: [[3], [9, 20], [15, 7]]
```

**Why BFS?** The problem explicitly asks for "level by level" traversal - a clear BFS signal!

## 5. Brute Force Approach

A naive approach might use recursion with depth tracking (DFS-based):

```python
def levelOrder(root):
    """
    DFS approach with level tracking
    Time: O(n), Space: O(h) where h is height
    """
    if not root:
        return []

    result = []

    def dfs(node, level):
        if not node:
            return

        # Ensure the result list has a sublist for this level
        if len(result) == level:
            result.append([])

        # Add current node to its level
        result[level].append(node.val)

        # Visit children at next level
        dfs(node.left, level + 1)
        dfs(node.right, level + 1)

    dfs(root, 0)
    return result
```

**Drawback:** While this works, it's not intuitive for level-order problems and doesn't naturally give you the "layer by layer" feeling. It also makes harder problems (like finding the shortest path) more complex.

## 6. Optimized Solution: Classic BFS

```python
from collections import deque

def levelOrder(root):
    """
    BFS approach using a queue

    Key Insight: Process nodes level by level using a queue.
    The queue ensures we visit all nodes at distance k before
    visiting any nodes at distance k+1.

    Time: O(n) - visit each node exactly once
    Space: O(w) - where w is maximum width of tree (max nodes in queue)
    """
    if not root:
        return []

    result = []
    queue = deque([root])  # Initialize queue with root

    # Continue while there are nodes to process
    while queue:
        level_size = len(queue)  # Number of nodes at current level
        current_level = []       # Store values for this level

        # Process all nodes at current level
        for i in range(level_size):
            # Get the front node from queue
            node = queue.popleft()
            current_level.append(node.val)

            # Add children to queue for next level
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        # Add current level to result
        result.append(current_level)

    return result
```

### Step-by-Step Walkthrough

Let's trace through the example tree:
```
       3
      / \
     9  20
       /  \
      15   7
```

**Initial State:**
- `queue = [3]`
- `result = []`

**Iteration 1 (Level 0):**
- `level_size = 1` (only node 3)
- Process node 3: `current_level = [3]`
- Add children 9 and 20 to queue
- `queue = [9, 20]`
- `result = [[3]]`

**Iteration 2 (Level 1):**
- `level_size = 2` (nodes 9 and 20)
- Process node 9: `current_level = [9]`, no children
- Process node 20: `current_level = [9, 20]`, add children 15 and 7
- `queue = [15, 7]`
- `result = [[3], [9, 20]]`

**Iteration 3 (Level 2):**
- `level_size = 2` (nodes 15 and 7)
- Process node 15: `current_level = [15]`, no children
- Process node 7: `current_level = [15, 7]`, no children
- `queue = []`
- `result = [[3], [9, 20], [15, 7]]`

**Queue is empty, we're done!**

## 7. Time & Space Complexity Analysis

### Binary Tree BFS
- **Time Complexity: O(n)** - We visit each node exactly once
- **Space Complexity: O(w)** - Where w is the maximum width of the tree
  - Worst case: Complete binary tree where last level has n/2 nodes → O(n)
  - Best case: Skewed tree → O(1)

### Graph BFS
- **Time Complexity: O(V + E)**
  - V = number of vertices (we visit each once)
  - E = number of edges (we explore each edge once)
- **Space Complexity: O(V)**
  - Queue can hold at most all vertices
  - Visited set stores all vertices

**Why O(V + E)?**
- We visit each vertex once: O(V)
- For each vertex, we explore its edges: O(E)
- Total: O(V + E)

## 8. Variations of BFS

### Variation 1: Multi-Source BFS

**Problem:** Rotting Oranges - oranges at multiple positions start rotting simultaneously

```python
def orangesRotting(grid):
    """
    Multi-source BFS: Start from multiple sources at once

    Key Insight: Add ALL initial rotten oranges to queue before BFS
    """
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh_count = 0

    # Find all initial rotten oranges (multiple sources)
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c, 0))  # (row, col, time)
            elif grid[r][c] == 1:
                fresh_count += 1

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    max_time = 0

    # BFS from all sources simultaneously
    while queue:
        r, c, time = queue.popleft()
        max_time = max(max_time, time)

        # Spread to 4 adjacent cells
        for dr, dc in directions:
            nr, nc = r + dr, c + dc

            # If valid fresh orange, rot it
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                grid[nr][nc] = 2  # Mark as rotten
                fresh_count -= 1
                queue.append((nr, nc, time + 1))

    return max_time if fresh_count == 0 else -1
```

### Variation 2: BFS on Grid (Matrix)

**Problem:** Shortest Path in Binary Matrix

```python
def shortestPathBinaryMatrix(grid):
    """
    BFS on 2D grid with 8-directional movement

    Key Insight: Treat grid cells as graph nodes
    """
    n = len(grid)

    # Edge cases
    if grid[0][0] == 1 or grid[n-1][n-1] == 1:
        return -1

    # 8 directions: up, down, left, right, and 4 diagonals
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]

    queue = deque([(0, 0, 1)])  # (row, col, path_length)
    grid[0][0] = 1  # Mark as visited (reuse grid)

    while queue:
        r, c, length = queue.popleft()

        # Reached bottom-right?
        if r == n - 1 and c == n - 1:
            return length

        # Explore all 8 neighbors
        for dr, dc in directions:
            nr, nc = r + dr, c + dc

            # Valid unvisited cell?
            if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 0:
                grid[nr][nc] = 1  # Mark visited
                queue.append((nr, nc, length + 1))

    return -1  # No path found
```

### Variation 3: BFS on Graph (Adjacency List)

**Problem:** Find shortest path in unweighted graph

```python
def shortestPath(graph, start, end):
    """
    BFS on graph represented as adjacency list

    graph = {
        'A': ['B', 'C'],
        'B': ['A', 'D', 'E'],
        'C': ['A', 'F'],
        ...
    }
    """
    queue = deque([(start, 0)])  # (node, distance)
    visited = {start}

    while queue:
        node, dist = queue.popleft()

        # Found the target?
        if node == end:
            return dist

        # Explore neighbors
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))

    return -1  # No path exists
```

### Variation 4: Bidirectional BFS

**Problem:** Word Ladder - find shortest transformation sequence

```python
def ladderLength(beginWord, endWord, wordList):
    """
    Bidirectional BFS: Search from both start and end simultaneously

    Key Insight: Two BFS searches meet in the middle, reducing search space
    Time: O(M^2 * N) where M = word length, N = wordList size
    """
    if endWord not in wordList:
        return 0

    wordList = set(wordList)

    # Two sets for forward and backward search
    forward = {beginWord}
    backward = {endWord}
    visited = set()
    length = 1

    while forward and backward:
        # Always expand the smaller frontier (optimization)
        if len(forward) > len(backward):
            forward, backward = backward, forward

        next_level = set()

        for word in forward:
            # Try all possible one-letter changes
            for i in range(len(word)):
                for c in 'abcdefghijklmnopqrstuvwxyz':
                    next_word = word[:i] + c + word[i+1:]

                    # Found intersection of two searches!
                    if next_word in backward:
                        return length + 1

                    if next_word in wordList and next_word not in visited:
                        visited.add(next_word)
                        next_level.add(next_word)

        forward = next_level
        length += 1

    return 0
```

## 9. Pro Tips for Senior Engineers

### 1. Queue vs Deque
```python
# Don't use list as queue - O(n) for pop(0)
queue = [root]  # ❌ BAD
node = queue.pop(0)  # O(n) operation

# Use deque for O(1) operations
from collections import deque
queue = deque([root])  # ✅ GOOD
node = queue.popleft()  # O(1) operation
```

### 2. Track Level Information
```python
# Method 1: Process level by level (cleaner for tree problems)
while queue:
    level_size = len(queue)
    for i in range(level_size):
        node = queue.popleft()
        # Process node...

# Method 2: Store level with each node (better for shortest path)
queue = deque([(start, 0)])  # (node, level)
while queue:
    node, level = queue.popleft()
```

### 3. BFS vs DFS Decision Matrix

| Problem Type | Use BFS | Use DFS |
|--------------|---------|---------|
| Shortest path (unweighted) | ✅ Yes | ❌ No |
| All paths | ❌ No | ✅ Yes |
| Detect cycle | Either | ✅ Better |
| Connected components | Either | ✅ Better (less memory) |
| Level-order traversal | ✅ Yes | Can work but awkward |
| Topological sort | Can work | ✅ Better |
| Memory constraint | ❌ No (uses more) | ✅ Yes |

### 4. When NOT to Use BFS

**Don't use BFS when:**
- Graph is weighted (use Dijkstra's or Bellman-Ford instead)
- You need ALL paths, not just shortest (use DFS with backtracking)
- Tree is very wide (BFS queue will be huge, use DFS for O(h) space)
- You need to go deep first (maze solving, sudoku)

### 5. Interview Gotchas

**Gotcha #1: Forgetting to mark as visited WHEN ADDING to queue**
```python
# ❌ WRONG - might add same node multiple times
while queue:
    node = queue.popleft()
    visited.add(node)  # Too late!
    for neighbor in graph[node]:
        if neighbor not in visited:
            queue.append(neighbor)

# ✅ CORRECT - mark visited when adding
while queue:
    node = queue.popleft()
    for neighbor in graph[node]:
        if neighbor not in visited:
            visited.add(neighbor)  # Mark here!
            queue.append(neighbor)
```

**Gotcha #2: Not handling empty input**
```python
def levelOrder(root):
    if not root:  # ✅ Always check!
        return []
    # ... rest of code
```

**Gotcha #3: Grid boundary checks**
```python
# ✅ Check all boundaries before accessing grid
if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == target:
    # Safe to access
```

**Gotcha #4: Modifying graph/grid for visited tracking**
```python
# Option 1: Use separate visited set (safer, more memory)
visited = set()

# Option 2: Modify in-place (less memory, but destructive)
grid[r][c] = -1  # Mark as visited
# Only if problem allows it!
```

## 10. Problem Recognition: How to Spot BFS

Ask yourself these questions:

1. **Does the problem mention "shortest"?**
   - "shortest path", "minimum steps", "fewest moves"
   - → BFS is likely the answer

2. **Is the graph/tree unweighted?**
   - All edges have same cost?
   - → BFS finds shortest path

3. **Does it mention "level" or "layer"?**
   - "level order", "layer by layer", "distance k"
   - → Classic BFS application

4. **Is it about spreading or propagation?**
   - Virus spreading, water flowing, fire spreading
   - → Multi-source BFS

5. **Grid/Matrix problem asking for shortest path?**
   - Navigate through maze, reach bottom-right
   - → BFS on grid

### Pattern Checklist
- [ ] Shortest path in unweighted graph
- [ ] Level-order traversal
- [ ] Minimum steps/moves
- [ ] Nearest/closest element
- [ ] Spreading/propagation
- [ ] Connected components exploration
- [ ] Distance within k hops

## 11. Practice Problems

### Easy
1. **Binary Tree Level Order Traversal** (LeetCode 102)
   - Classic BFS on tree

2. **Cousins in Binary Tree** (LeetCode 993)
   - BFS to find nodes at same level

3. **N-ary Tree Level Order Traversal** (LeetCode 429)
   - BFS with multiple children

### Medium
4. **Rotting Oranges** (LeetCode 994)
   - Multi-source BFS on grid

5. **Word Ladder** (LeetCode 127)
   - BFS on implicit graph

6. **01 Matrix** (LeetCode 542)
   - Multi-source BFS for nearest distance

7. **Shortest Path in Binary Matrix** (LeetCode 1091)
   - BFS on 2D grid with 8 directions

8. **Clone Graph** (LeetCode 133)
   - BFS for graph traversal and cloning

### Hard
9. **Bus Routes** (LeetCode 815)
   - BFS with complex state management

10. **Shortest Path to Get All Keys** (LeetCode 864)
    - BFS with state encoding (position + keys collected)

11. **Cut Off Trees for Golf Event** (LeetCode 675)
    - Multiple BFS calls

## 12. Common Mistakes

### Mistake #1: Using list.pop(0) instead of deque
**Problem:** `list.pop(0)` is O(n) because it shifts all elements
```python
# ❌ WRONG - O(n) per operation
queue = []
queue.pop(0)

# ✅ CORRECT - O(1) per operation
from collections import deque
queue = deque()
queue.popleft()
```

### Mistake #2: Not tracking visited nodes
**Problem:** Revisiting nodes causes infinite loops
```python
# ❌ WRONG - infinite loop on cyclic graphs
queue = deque([start])
while queue:
    node = queue.popleft()
    for neighbor in graph[node]:
        queue.append(neighbor)  # Will revisit!

# ✅ CORRECT - track visited
visited = {start}
queue = deque([start])
while queue:
    node = queue.popleft()
    for neighbor in graph[node]:
        if neighbor not in visited:
            visited.add(neighbor)
            queue.append(neighbor)
```

### Mistake #3: Marking visited too late
**Problem:** Same node added to queue multiple times
```python
# ❌ WRONG - node added multiple times before being processed
while queue:
    node = queue.popleft()
    if node in visited:  # Check here is too late
        continue
    visited.add(node)

# ✅ CORRECT - mark when adding to queue
while queue:
    node = queue.popleft()
    for neighbor in graph[node]:
        if neighbor not in visited:
            visited.add(neighbor)  # Mark immediately
            queue.append(neighbor)
```

### Mistake #4: Off-by-one errors in level counting
```python
# ❌ WRONG - returns 0-indexed level
def maxDepth(root):
    if not root:
        return 0
    queue = deque([root])
    depth = 0
    while queue:
        depth += 1  # Increment happens even for last level
        # ...
    return depth  # Correct!

# Common mistake: starting depth at 1 or returning depth - 1
```

### Mistake #5: Not handling grid boundaries
```python
# ❌ WRONG - index out of bounds
nr, nc = r + dr, c + dc
if grid[nr][nc] == 0:  # Crash if out of bounds!

# ✅ CORRECT - check boundaries first
nr, nc = r + dr, c + dc
if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
```

### Mistake #6: Forgetting to check empty queue
```python
# ❌ WRONG - assumes queue has elements
while queue:
    level_size = len(queue)
    for i in range(level_size):
        node = queue.popleft()
        # What if queue becomes empty mid-loop?

# ✅ CORRECT - for loop won't execute if level_size is 0
# The level_size snapshot ensures we process exactly that many
```

### Mistake #7: Modifying list while iterating
```python
# ❌ WRONG - modifying queue during iteration
for node in queue:  # Don't iterate directly
    queue.append(neighbor)

# ✅ CORRECT - use while loop and popleft
while queue:
    node = queue.popleft()
    queue.append(neighbor)
```

---

## Summary Cheat Sheet

**BFS Template:**
```python
from collections import deque

def bfs(start):
    queue = deque([start])
    visited = {start}

    while queue:
        node = queue.popleft()

        # Process node
        # ...

        for neighbor in get_neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

**Remember:**
- Use `deque` for O(1) operations
- Mark visited when ADDING to queue
- Check boundaries for grids
- Track level info when needed
- BFS = shortest path for unweighted graphs
- Queue = First In First Out (FIFO)

**Time to master BFS!** 🚀
