# DFS (Depth-First Search) — Complete Interview Guide

## When to Use This Pattern

**Signals that indicate DFS:**
1. You need to explore **all paths**, **all solutions**, or **all connected components**
2. The problem involves **cycle detection** in a directed graph
3. Keywords: "connected components", "islands", "regions", "topological order"
4. The problem requires **backtracking** (permutations, combinations, valid parentheses)
5. You need to determine if a graph is **connected** or **bipartite**
6. **Tree traversal** problems (preorder, inorder, postorder)
7. The problem asks to **clone/copy** a graph structure
8. You need to find an **ordering** with dependencies (topological sort)

**When NOT to use it:**
- You need the **shortest path** -- use BFS instead
- Level-by-level processing is needed -- BFS is more natural
- The graph is potentially infinite and you might explore forever -- use BFS or iterative deepening
- Memory for the recursion stack is a concern and the graph is very deep but not wide

## Core Mechanics

DFS explores as deep as possible along each branch before backtracking. It uses a **stack** -- either the call stack (recursive DFS) or an explicit stack (iterative DFS).

**Why it works for connected components:** Starting from any node, DFS visits every reachable node exactly once. If you run DFS from an unvisited node, you discover an entire connected component. The number of times you start a new DFS equals the number of components.

**Why it works for cycle detection:** In a directed graph, a cycle exists if and only if during DFS we encounter a node that is currently on the recursion stack (a "back edge"). We track this with three states: unvisited, in-progress (on stack), and completed.

**The invariant:** DFS maintains a path from the source to the current node. When it backtracks, it removes the current node from the path and tries the next neighbor.

### ASCII Walkthrough

```
Number of Islands:
Grid:
  1 1 0 0 0
  1 1 0 0 0
  0 0 1 0 0
  0 0 0 1 1

DFS from (0,0):
  Visit (0,0) -> mark 0. Visit (0,1) -> mark 0. Visit (1,1) -> mark 0.
  Visit (1,0) -> mark 0. Backtrack. Island 1 complete.

  Scan continues. (0,2),(0,3),(0,4) are 0, skip.
  (1,0)...(1,4) are 0, skip.
  (2,2) is 1 -> DFS: mark 0. No land neighbors. Island 2.
  (3,3) is 1 -> DFS: mark 0. Visit (3,4) -> mark 0. Island 3.

  Answer: 3 islands.
```

## The Template

**Recursive DFS on graph:**
```python
def dfs_template(graph):
    visited = set()

    def dfs(node):
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor)

    for node in graph:
        if node not in visited:
            dfs(node)  # new component
```

**Recursive DFS on grid:**
```python
def dfs_grid(grid, r, c, rows, cols):
    if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] == '0':
        return
    grid[r][c] = '0'  # mark visited
    for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
        dfs_grid(grid, r + dr, c + dc, rows, cols)
```

**Cycle detection in directed graph:**
```python
def has_cycle(graph):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}

    def dfs(node):
        color[node] = GRAY
        for neighbor in graph[node]:
            if color[neighbor] == GRAY:
                return True  # back edge = cycle
            if color[neighbor] == WHITE and dfs(neighbor):
                return True
        color[node] = BLACK
        return False

    return any(color[n] == WHITE and dfs(n) for n in graph)
```

```go
func dfsTemplate(graph map[int][]int) {
	visited := make(map[int]bool)

	var dfs func(node int)
	dfs = func(node int) {
		visited[node] = true
		for _, neighbor := range graph[node] {
			if !visited[neighbor] {
				dfs(neighbor)
			}
		}
	}

	for node := range graph {
		if !visited[node] {
			dfs(node) // new component
		}
	}
}
```

## Variant Subpatterns

### 1. Grid DFS (Connected Components / Flood Fill)

Mark visited cells and explore all 4 (or 8) directions recursively.

Problems: Number of Islands, Flood Fill, Max Area of Island.

### 2. Graph DFS with Cycle Detection

Use three-color marking (white/gray/black) to detect back edges in directed graphs.

Problems: Course Schedule, Course Schedule II.

### 3. DFS with Backtracking

Explore a path, and when you return, undo the choice to explore alternatives.

```python
def backtrack(path, choices):
    if is_solution(path):
        result.append(path[:])
        return
    for choice in choices:
        path.append(choice)
        backtrack(path, remaining_choices)
        path.pop()  # undo
```

Problems: Remove Invalid Parentheses, Permutations, N-Queens.

### 4. Topological Sort (DFS-based)

Process nodes in reverse post-order to get a valid topological ordering.

```python
def topological_sort(graph):
    visited = set()
    order = []

    def dfs(node):
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor)
        order.append(node)  # post-order

    for node in graph:
        if node not in visited:
            dfs(node)

    return order[::-1]  # reverse post-order
```

Problems: Alien Dictionary, Course Schedule II.

### 5. Tarjan's Algorithm (Bridge Finding)

Find bridges (critical edges) and articulation points using DFS discovery times.

Problems: Critical Connections in a Network.

---

## Problem Walkthroughs

---

### Problem: Number of Islands (LC #200) — Medium

**Companies:** Amazon, Google, Meta, Microsoft, Bloomberg (one of the most asked problems overall)
**Why it is asked:** The canonical DFS/BFS grid problem. Tests connected component counting with clean boundary handling.

**The Brute Force:**
```python
def numIslands_brute(grid):
    # Union-Find approach (alternative, not brute force per se)
    # More complex implementation for the same result
    pass
```

There is no simpler approach than DFS/BFS for this problem. The "brute force" would be the same algorithm with worse implementation.

**The Key Insight:** Each island is a connected component of '1' cells. Start DFS from every unvisited '1' cell. Each DFS start means a new island. During DFS, mark cells as visited (flip to '0') to avoid re-counting.

**Optimal Solution:**
```python
def numIslands(grid):
    if not grid:
        return 0

    rows, cols = len(grid), len(grid[0])
    count = 0

    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] == '0':
            return
        grid[r][c] = '0'  # mark visited
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                count += 1
                dfs(r, c)

    return count
```

**Dry Run:**
```
Input: grid = [["1","1","0","0","0"],
               ["1","1","0","0","0"],
               ["0","0","1","0","0"],
               ["0","0","0","1","1"]]

Scan (0,0)='1': count=1. DFS marks (0,0),(0,1),(1,0),(1,1) as '0'.
Scan (0,1)='0': skip. ... (0,4)='0': skip.
Scan (1,0)='0': skip. ... (1,4)='0': skip.
Scan (2,0)='0': skip. (2,1)='0': skip.
Scan (2,2)='1': count=2. DFS marks (2,2) as '0'.
Scan (3,3)='1': count=3. DFS marks (3,3),(3,4) as '0'.

Answer: 3
```

**Edge Cases:**
- Empty grid: return 0.
- All water: return 0.
- All land: return 1.
- Single cell: return 1 if '1', else 0.
- Large grid with recursion depth issue: use iterative DFS with explicit stack, or increase Python recursion limit.

**Complexity:** Time O(m * n), Space O(m * n) worst case for recursion stack (snake-shaped island).

**Follow-up questions interviewers might ask:**
- "Can you do it without modifying the grid?" -- Use a visited set.
- "Can you use BFS instead?" -- Yes, same complexity, different traversal order.
- "What about Union-Find?" -- Yes, O(m * n * alpha(m * n)) which is effectively O(m * n).
- "What if the grid is too large for recursion?" -- Use iterative DFS with explicit stack.

---

### Problem: Clone Graph (LC #133) — Medium

**Companies:** Meta, Amazon, Google, Microsoft
**Why it is asked:** Tests DFS with hash map for graph cloning. You must handle cycles correctly.

**The Brute Force:** There is no simpler approach. DFS/BFS with a mapping from old to new nodes is the standard.

**The Key Insight:** Use a hash map mapping `old_node -> new_node`. When you visit a node, create its clone and store it in the map. For each neighbor, if it is already cloned (in the map), use the existing clone. Otherwise, recursively clone it. The hash map prevents infinite loops on cycles.

**Optimal Solution:**
```python
class Node:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

def cloneGraph(node):
    if not node:
        return None

    cloned = {}  # old_node -> new_node

    def dfs(original):
        if original in cloned:
            return cloned[original]

        copy = Node(original.val)
        cloned[original] = copy  # store before recursing to handle cycles

        for neighbor in original.neighbors:
            copy.neighbors.append(dfs(neighbor))

        return copy

    return dfs(node)
```

**Dry Run:**
```
Input: Graph with nodes 1-2-3-4 forming a cycle: 1--2, 2--3, 3--4, 4--1, plus 2--4

dfs(1): create clone(1), cloned={1:clone(1)}
  neighbor 2: dfs(2): create clone(2), cloned={1:clone(1),2:clone(2)}
    neighbor 1: already in cloned, return clone(1)
    neighbor 3: dfs(3): create clone(3)
      neighbor 2: already cloned, return clone(2)
      neighbor 4: dfs(4): create clone(4)
        neighbor 1: already cloned, return clone(1)
        neighbor 3: already cloned, return clone(3)
      return clone(4)
    return clone(3)
  return clone(2)
  neighbor 4: already cloned, return clone(4)
return clone(1)
```

**Edge Cases:**
- Null input: return null.
- Single node with no neighbors: return new node with same value.
- Single node with self-loop: clone it with self-reference.
- Fully connected graph.

**Complexity:** Time O(V + E), Space O(V) for the hash map.

**Follow-up questions interviewers might ask:**
- "Can you do it with BFS?" -- Yes, use a queue and the same hash map approach.
- "What prevents infinite loops?" -- The `cloned` map: we check if a node is already cloned before recursing.
- "What if nodes have unique IDs?" -- You could use IDs as map keys, but node references work fine.

---

### Problem: Course Schedule (LC #207) — Medium

**Companies:** Amazon, Meta, Google, Microsoft, Uber
**Why it is asked:** Tests cycle detection in a directed graph. The three-color DFS approach is the classic solution.

**The Brute Force:**
```python
def canFinish_brute(numCourses, prerequisites):
    # Build adjacency list and check every possible ordering
    # Exponential time -- impractical
    pass
```

**The Key Insight:** You can finish all courses if and only if the prerequisite graph has no cycles. Use DFS with three states:
- WHITE (0): unvisited
- GRAY (1): currently being processed (on the recursion stack)
- BLACK (2): fully processed

If you encounter a GRAY node during DFS, you have found a cycle (back edge).

**Optimal Solution:**
```python
def canFinish(numCourses, prerequisites):
    graph = [[] for _ in range(numCourses)]
    for course, prereq in prerequisites:
        graph[prereq].append(course)

    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * numCourses

    def has_cycle(node):
        color[node] = GRAY
        for neighbor in graph[node]:
            if color[neighbor] == GRAY:
                return True  # cycle!
            if color[neighbor] == WHITE and has_cycle(neighbor):
                return True
        color[node] = BLACK
        return False

    for i in range(numCourses):
        if color[i] == WHITE:
            if has_cycle(i):
                return False

    return True
```

**Alternative: Kahn's Algorithm (BFS topological sort):**
```python
from collections import deque

def canFinish_kahn(numCourses, prerequisites):
    graph = [[] for _ in range(numCourses)]
    in_degree = [0] * numCourses

    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1

    queue = deque(i for i in range(numCourses) if in_degree[i] == 0)
    processed = 0

    while queue:
        node = queue.popleft()
        processed += 1
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return processed == numCourses
```

**Dry Run:**
```
Input: numCourses=4, prerequisites=[[1,0],[2,0],[3,1],[3,2]]

Graph: 0 -> [1, 2], 1 -> [3], 2 -> [3], 3 -> []

DFS from 0: color[0]=GRAY
  Visit 1: color[1]=GRAY
    Visit 3: color[3]=GRAY -> no neighbors -> color[3]=BLACK
  color[1]=BLACK
  Visit 2: color[2]=GRAY
    Visit 3: color[3]=BLACK, skip
  color[2]=BLACK
color[0]=BLACK

All nodes processed, no cycle. Return True.

With cycle: prerequisites=[[1,0],[0,1]]
Graph: 0 -> [1], 1 -> [0]
DFS from 0: color[0]=GRAY
  Visit 1: color[1]=GRAY
    Visit 0: color[0]=GRAY -> CYCLE! Return False.
```

**Edge Cases:**
- No prerequisites: always possible.
- Self-loops: `[0, 0]` means course 0 requires itself -- cycle.
- Disconnected graph: must check all components.

**Complexity:** Time O(V + E), Space O(V + E).

**Follow-up questions interviewers might ask:**
- "Can you return the order?" -- LC #210, Course Schedule II. Use topological sort (DFS post-order reversed, or Kahn's algorithm).
- "What if you want to find the cycle?" -- Track parent pointers during DFS and reconstruct the cycle when a back edge is found.
- "DFS vs BFS (Kahn's)?" -- Both are O(V + E). Kahn's is often preferred in practice because it does not require recursion and directly gives the order.

---

### Problem: Number of Connected Components in an Undirected Graph (LC #323) — Medium

**Companies:** Meta, Google, Amazon, LinkedIn
**Why it is asked:** Direct application of DFS to count connected components. Also testable with Union-Find.

**The Brute Force:** DFS/BFS is already the standard O(V + E) solution. Union-Find is an alternative.

**The Key Insight:** Run DFS from each unvisited node. Each DFS starting point represents a new connected component.

**Optimal Solution:**
```python
def countComponents(n, edges):
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    visited = [False] * n
    count = 0

    def dfs(node):
        visited[node] = True
        for neighbor in graph[node]:
            if not visited[neighbor]:
                dfs(neighbor)

    for i in range(n):
        if not visited[i]:
            count += 1
            dfs(i)

    return count
```

**Union-Find Alternative:**
```python
def countComponents_uf(n, edges):
    parent = list(range(n))
    rank = [0] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]  # path compression
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px == py:
            return False
        if rank[px] < rank[py]:
            px, py = py, px
        parent[py] = px
        if rank[px] == rank[py]:
            rank[px] += 1
        return True

    components = n
    for u, v in edges:
        if union(u, v):
            components -= 1

    return components
```

**Dry Run:**
```
Input: n=5, edges=[[0,1],[1,2],[3,4]]

Graph: 0-[1], 1-[0,2], 2-[1], 3-[4], 4-[3]

DFS from 0: visits 0,1,2. Component 1.
Node 1,2 already visited. Skip.
DFS from 3: visits 3,4. Component 2.
Node 4 visited. Skip.

Answer: 2
```

**Edge Cases:**
- n nodes, no edges: n components.
- Fully connected: 1 component.
- Single node: 1 component.

**Complexity:** Time O(V + E), Space O(V + E).

**Follow-up questions interviewers might ask:**
- "Can you do it with Union-Find?" -- Yes, as shown above.
- "What if edges are added dynamically?" -- Union-Find is better for online/incremental queries.
- "How do you count components in a directed graph?" -- Use Kosaraju's or Tarjan's algorithm for strongly connected components.

---

### Problem: Alien Dictionary (LC #269) — Hard

**Companies:** Meta, Google, Amazon, Uber, Apple
**Why it is asked:** Combines graph construction from character ordering with topological sort. Tests both problem decomposition and algorithm implementation.

**The Brute Force:**
```python
def alienOrder_brute(words):
    # Try all possible orderings of characters and check consistency
    # Exponential -- impractical
    pass
```

**The Key Insight:** Compare adjacent words in the sorted list to extract ordering constraints. Each pair of adjacent words that differ at some position gives an edge: `words[i][j] < words[i+1][j]` at the first differing position. Build a directed graph from these edges and perform topological sort. If there is a cycle, no valid ordering exists. Also handle the edge case where a longer word comes before its prefix (invalid).

**Optimal Solution:**
```python
from collections import deque

def alienOrder(words):
    # Step 1: Initialize graph with all unique characters
    graph = {}
    in_degree = {}
    for word in words:
        for ch in word:
            if ch not in graph:
                graph[ch] = set()
                in_degree[ch] = 0

    # Step 2: Build edges from adjacent word comparisons
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i + 1]
        min_len = min(len(w1), len(w2))

        # Edge case: if w1 is longer and shares prefix with w2, invalid
        if len(w1) > len(w2) and w1[:min_len] == w2[:min_len]:
            return ""

        for j in range(min_len):
            if w1[j] != w2[j]:
                if w2[j] not in graph[w1[j]]:
                    graph[w1[j]].add(w2[j])
                    in_degree[w2[j]] += 1
                break  # only first difference matters

    # Step 3: Topological sort (Kahn's algorithm)
    queue = deque(ch for ch in in_degree if in_degree[ch] == 0)
    result = []

    while queue:
        ch = queue.popleft()
        result.append(ch)
        for neighbor in graph[ch]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # If not all characters are in result, there is a cycle
    if len(result) != len(graph):
        return ""

    return "".join(result)
```

**Dry Run:**
```
Input: words = ["wrt", "wrf", "er", "ett", "rftt"]

Compare adjacent:
  "wrt" vs "wrf": first diff at index 2, t < f. Edge: t -> f
  "wrf" vs "er":  first diff at index 0, w < e. Edge: w -> e
  "er" vs "ett":  first diff at index 1, r < t. Edge: r -> t
  "ett" vs "rftt": first diff at index 0, e < r. Edge: e -> r

Graph: w -> {e}, e -> {r}, r -> {t}, t -> {f}
In-degree: w:0, e:1, r:1, t:1, f:1

Topo sort: queue=[w]
  Process w -> e's in_degree becomes 0. queue=[e]
  Process e -> r's in_degree becomes 0. queue=[r]
  Process r -> t's in_degree becomes 0. queue=[t]
  Process t -> f's in_degree becomes 0. queue=[f]
  Process f.

Result: "wertf"
```

**Edge Cases:**
- Single word: return all unique characters in any order.
- All words identical: return all unique characters in any order.
- Invalid input (longer prefix word before shorter): return "".
- Cycle in the graph: return "".
- Multiple valid orderings: return any one.

**Complexity:** Time O(C) where C = total characters across all words (for building graph and topo sort). Space O(1) since the alphabet has at most 26 characters.

**Follow-up questions interviewers might ask:**
- "What if there are multiple valid orderings?" -- Kahn's algorithm gives one valid ordering. For all orderings, you would need backtracking.
- "How do you detect invalid input?" -- Check for the prefix edge case and for cycles in the graph.
- "DFS or BFS for topological sort?" -- Both work. BFS (Kahn's) is often cleaner because it naturally detects cycles (if not all nodes are processed).

---

### Problem: Making A Large Island (LC #827) — Hard

**Companies:** Google, Amazon, Meta
**Why it is asked:** Tests DFS for component labeling combined with a clever enumeration step. The challenge is efficiently trying all possible flips.

**The Brute Force:**
```python
def largestIsland_brute(grid):
    # For each 0, flip it to 1, run numIslands/DFS to find max island size
    # O(n^2 * n^2) = O(n^4) -- too slow
    n = len(grid)
    max_size = 0
    for r in range(n):
        for c in range(n):
            if grid[r][c] == 0:
                grid[r][c] = 1
                max_size = max(max_size, compute_max_island(grid))
                grid[r][c] = 0
    return max_size if max_size > 0 else n * n  # all 1s case
```

For each 0 cell, flip it to 1, run DFS to find the largest island. O(n^4).

**The Key Insight:** Two passes:
1. Label each island with a unique ID and compute its size using DFS. Store size in a map.
2. For each 0 cell, check its 4 neighbors. Collect the unique island IDs adjacent to it. The potential island size is 1 (for the flipped cell) + sum of sizes of adjacent distinct islands.

This avoids re-running DFS for each flip.

**Optimal Solution:**
```python
def largestIsland(grid):
    n = len(grid)
    island_id = 2  # start labeling from 2 (0 and 1 are used)
    island_size = {}

    def dfs(r, c, label):
        if r < 0 or r >= n or c < 0 or c >= n or grid[r][c] != 1:
            return 0
        grid[r][c] = label
        size = 1
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            size += dfs(r + dr, c + dc, label)
        return size

    # Pass 1: Label all islands and compute sizes
    for r in range(n):
        for c in range(n):
            if grid[r][c] == 1:
                size = dfs(r, c, island_id)
                island_size[island_id] = size
                island_id += 1

    if not island_size:
        return 1  # all 0s, flip one to get island of size 1

    max_island = max(island_size.values())

    # Pass 2: Try flipping each 0
    for r in range(n):
        for c in range(n):
            if grid[r][c] == 0:
                neighbors = set()
                for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] > 1:
                        neighbors.add(grid[nr][nc])
                total = 1 + sum(island_size[label] for label in neighbors)
                max_island = max(max_island, total)

    return max_island
```

**Dry Run:**
```
Input: grid = [[1,0],[0,1]]

Pass 1: DFS from (0,0) -> label=2, size=1. DFS from (1,1) -> label=3, size=1.
island_size = {2:1, 3:1}
Grid: [[2,0],[0,3]]

Pass 2:
  (0,1)=0: neighbors={(2,3)} (up=none, down=3, left=2, right=none)
    Actually: (0,1) neighbors: (-1,1) OOB, (1,1)=3, (0,0)=2, (0,2) OOB
    neighbors={2,3}, total = 1+1+1 = 3

  (1,0)=0: neighbors: (0,0)=2, (2,0) OOB, (1,-1) OOB, (1,1)=3
    neighbors={2,3}, total = 1+1+1 = 3

max_island = 3
```

**Edge Cases:**
- All 1s: return n * n (no flip needed, or any flip is redundant).
- All 0s: return 1.
- Single 0 surrounded by one large island: size = island_size + 1.

**Complexity:** Time O(n^2), Space O(n^2).

**Follow-up questions interviewers might ask:**
- "Why label islands with unique IDs?" -- To avoid counting the same island multiple times when a 0 cell is adjacent to the same island from multiple sides.
- "Can you flip more than one cell?" -- That would be a different (harder) problem requiring a different approach.

---

### Problem: Remove Invalid Parentheses (LC #301) — Hard

**Companies:** Meta, Google, Amazon
**Why it is asked:** Tests BFS/DFS with pruning. The challenge is generating valid strings with minimum removals.

**The Brute Force:**
```python
def removeInvalidParentheses_brute(s):
    # Generate all possible subsets, check each for validity
    # O(2^n) -- exponential
    pass
```

**The Key Insight:** First, determine the minimum number of left and right parentheses to remove. Then use DFS with backtracking to generate all valid strings. Pruning: track open_count to avoid generating invalid states. Alternatively, BFS level by level: try removing one parenthesis at a time, and the first level that produces valid strings gives the minimum removals.

**Optimal Solution (DFS with pruning):**
```python
def removeInvalidParentheses(s):
    # Step 1: Count minimum removals needed
    left_rem = right_rem = 0
    for ch in s:
        if ch == '(':
            left_rem += 1
        elif ch == ')':
            if left_rem > 0:
                left_rem -= 1
            else:
                right_rem += 1

    result = set()

    def dfs(index, open_count, left_rem, right_rem, path):
        if index == len(s):
            if open_count == 0 and left_rem == 0 and right_rem == 0:
                result.add(path)
            return

        ch = s[index]

        if ch == '(':
            # Option 1: Remove this '('
            if left_rem > 0:
                dfs(index + 1, open_count, left_rem - 1, right_rem, path)
            # Option 2: Keep this '('
            dfs(index + 1, open_count + 1, left_rem, right_rem, path + ch)

        elif ch == ')':
            # Option 1: Remove this ')'
            if right_rem > 0:
                dfs(index + 1, open_count, left_rem, right_rem - 1, path)
            # Option 2: Keep this ')' (only if there is a matching open paren)
            if open_count > 0:
                dfs(index + 1, open_count - 1, left_rem, right_rem, path + ch)

        else:
            # Non-parenthesis character: always keep
            dfs(index + 1, open_count, left_rem, right_rem, path + ch)

    dfs(0, 0, left_rem, right_rem, "")
    return list(result)
```

**Dry Run:**
```
Input: s = "()())()"

Count removals: scanning "()()" -> left_rem=0, then ')' with no open -> right_rem=1,
then "()" -> balanced. left_rem=0, right_rem=1.

DFS explores removing exactly 1 ')'.
Possible valid results: ["(())()", "()()()" ]
```

**Edge Cases:**
- Empty string: return [""].
- No parentheses: return [s].
- All parentheses to remove: return [""].
- Already valid: return [s].

**Complexity:** Time O(2^n) worst case, but pruning makes it much faster in practice. Space O(n) for recursion depth.

**Follow-up questions interviewers might ask:**
- "Can you do it with BFS?" -- Yes, try removing each parenthesis one at a time, check validity. First level with valid results is the answer.
- "How do you avoid duplicates?" -- Use a set for results, or use index-based pruning (only remove the first of consecutive duplicates).

---

### Problem: Critical Connections in a Network (LC #1192) — Hard

**Companies:** Amazon (classic Amazon problem), Google
**Why it is asked:** Tests Tarjan's bridge-finding algorithm. Requires understanding of DFS discovery times and low-link values.

**The Brute Force:**
```python
def criticalConnections_brute(n, connections):
    # For each edge, remove it and check if graph is still connected
    # O(E * (V + E)) -- too slow for large graphs
    result = []
    for i, (u, v) in enumerate(connections):
        # Build graph without this edge
        graph = [[] for _ in range(n)]
        for j, (a, b) in enumerate(connections):
            if i != j:
                graph[a].append(b)
                graph[b].append(a)
        # Check connectivity with BFS/DFS
        visited = set()
        stack = [0]
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            for neighbor in graph[node]:
                stack.append(neighbor)
        if len(visited) < n:
            result.append([u, v])
    return result
```

Remove each edge one at a time and check connectivity. O(E * (V + E)).

**The Key Insight:** Use Tarjan's algorithm. During DFS, assign each node a discovery time (`disc`) and compute a `low` value (the minimum discovery time reachable from the subtree rooted at that node, considering back edges). An edge (u, v) is a bridge if and only if `low[v] > disc[u]` -- meaning there is no back edge from v's subtree that can reach u or any ancestor of u.

**Optimal Solution:**
```python
def criticalConnections(n, connections):
    graph = [[] for _ in range(n)]
    for u, v in connections:
        graph[u].append(v)
        graph[v].append(u)

    disc = [-1] * n
    low = [-1] * n
    bridges = []
    timer = [0]

    def dfs(node, parent):
        disc[node] = low[node] = timer[0]
        timer[0] += 1

        for neighbor in graph[node]:
            if neighbor == parent:
                continue
            if disc[neighbor] == -1:
                # Tree edge
                dfs(neighbor, node)
                low[node] = min(low[node], low[neighbor])
                if low[neighbor] > disc[node]:
                    bridges.append([node, neighbor])
            else:
                # Back edge
                low[node] = min(low[node], disc[neighbor])

    dfs(0, -1)
    return bridges
```

**Dry Run:**
```
Input: n=4, connections=[[0,1],[1,2],[2,0],[1,3]]

Graph: 0-[1,2], 1-[0,2,3], 2-[0,1], 3-[1]

DFS from 0 (parent=-1):
  disc[0]=0, low[0]=0
  Visit 1 (parent=0):
    disc[1]=1, low[1]=1
    Visit 2 (parent=1):
      disc[2]=2, low[2]=2
      Neighbor 0: disc[0]=0, back edge. low[2]=min(2,0)=0
      Neighbor 1: parent, skip.
    low[1]=min(1, low[2])=min(1,0)=0
    low[1] > disc[0]? 0 > 0? No. Not a bridge.
    Visit 3 (parent=1):
      disc[3]=3, low[3]=3
      Neighbor 1: parent, skip.
    low[1]=min(0, low[3])=min(0,3)=0
    low[3] > disc[1]? 3 > 1? Yes! Bridge: [1,3]
  Neighbor 2: disc[2]=2, back edge. low[0]=min(0,2)=0

Bridges: [[1,3]]
```

**Edge Cases:**
- Tree (no cycles): every edge is a bridge.
- Complete graph: no bridges.
- Disconnected graph: problem states connected, but if not, run DFS from each component.

**Complexity:** Time O(V + E), Space O(V + E).

**Follow-up questions interviewers might ask:**
- "What is the difference between bridges and articulation points?" -- A bridge is a critical edge; an articulation point is a critical node. Similar algorithm with slightly different condition.
- "Can you find articulation points?" -- Yes, modify Tarjan's: node u is an articulation point if (1) u is root with 2+ children, or (2) u is not root and has a child v with `low[v] >= disc[u]`.
- "What is the low value conceptually?" -- The earliest discovery time reachable from the subtree of node v via back edges. If low[v] > disc[u], v's subtree has no back edge to u or above, so removing (u,v) disconnects the graph.

---

## Common Mistakes and Interview Tips

### Top 5 Mistakes

1. **Forgetting to mark visited BEFORE recursing:** If you mark visited inside the recursive call (after the recursive calls to neighbors), you can visit the same node multiple times, causing infinite loops on cyclic graphs.

2. **Wrong boundary checks in grid DFS:** Always check bounds BEFORE accessing `grid[r][c]`. The order must be: bounds check, then value check.

3. **Not handling disconnected graphs:** If the graph might be disconnected, you must run DFS from every unvisited node, not just node 0.

4. **Confusing undirected and directed cycle detection:** In undirected graphs, a back edge to the parent is NOT a cycle -- you must exclude the parent. In directed graphs, three-color marking is needed.

5. **Shallow copy in backtracking:** When saving a path to results, use `path[:]` or `list(path)`. Appending the path object directly means all results point to the same (eventually empty) list.

### How to Recognize This Pattern in 30 Seconds

Ask: "Am I looking for connected components, cycles, topological order, or all paths?" If yes, DFS. If shortest path, BFS.

### What Senior/Staff Interviewers Look For

- **Correct cycle detection with three colors** for directed graphs.
- **Clean backtracking** with proper undo operations.
- **Tarjan's algorithm** for bridge/articulation point problems.
- **Topological sort** implementation (both DFS and Kahn's) and understanding of when each is appropriate.
- **Complexity analysis** that correctly accounts for the graph structure.

### Communication Tips

1. State whether the graph is directed or undirected -- this changes the cycle detection approach.
2. Choose between DFS and BFS and justify: "I am using DFS because I need to detect cycles / find all paths / count components."
3. For grid problems, state whether you are modifying the grid in-place or using a visited set.
4. For backtracking, explain the "choose, explore, unchoose" pattern.

## Pattern Connections

- **DFS** for shortest path is wrong -- use **BFS**.
- **DFS + memoization** becomes **Dynamic Programming** (top-down).
- **DFS with post-order processing** gives **topological sort**, which is the foundation for many **DP on DAGs** problems.
- **DFS on trees** connects to all **tree traversal** problems (LC #94, #144, #145).
- **Tarjan's DFS** (bridges, SCCs) connects to advanced **graph theory** problems.
- **DFS with backtracking** covers all **combinatorial search** problems (permutations, subsets, N-Queens).
- **Union-Find** is an alternative to DFS for connected component problems, especially when edges are added dynamically.
