# Union-Find (Disjoint Set Union) — Complete Interview Guide

## When to Use This Pattern

Union-Find is the right tool when you see these signals in an interview problem:

**Primary signals:**
- "Find the number of connected components"
- "Are X and Y in the same group/component?"
- "Merge groups dynamically" — elements are being connected over time
- "Detect a cycle in an undirected graph"
- "Redundant connection" — which edge creates a cycle?
- "Equivalence classes" — if A relates to B and B relates to C, then A relates to C

**When to pick Union-Find over BFS/DFS:**
- You need to process edges/connections incrementally (online queries)
- You only care about connectivity, not the actual path
- You need to count or track components as edges are added
- The graph is given as a list of edges, not an adjacency list
- You need repeated "are X and Y connected?" queries after unions

**When BFS/DFS is better:**
- You need the actual path between nodes
- You need shortest path
- The graph structure is fixed (no dynamic merging)
- You need to process neighbors in a specific order (level-order, etc.)

**Complexity comparison:**
| Operation | Union-Find (optimized) | BFS/DFS |
|-----------|----------------------|---------|
| Union two components | O(alpha(n)) ~ O(1) | O(V + E) rebuild |
| Check connectivity | O(alpha(n)) ~ O(1) | O(V + E) |
| Count components | O(1) with counter | O(V + E) |
| Find actual path | Not supported | O(V + E) |

---

## Complexity Analysis Deep Dive

**Time complexity of Union-Find with both optimizations:**

The inverse Ackermann function alpha(n) grows extraordinarily slowly. For any practical input size (even 10^80, the estimated number of atoms in the universe), alpha(n) <= 4. This means Union-Find operations are effectively O(1) amortized.

| n (elements) | alpha(n) |
|--------------|----------|
| 1 | 0 |
| 3 | 1 |
| 7 | 2 |
| 2047 | 3 |
| 10^80 | 4 |

**Why amortized, not worst case?** Path compression makes individual finds faster over time, but a single find before compression could traverse a path of length O(log n). The amortized analysis averages this cost over a sequence of operations.

**Without optimizations (naive Union-Find):**
- Find: O(n) worst case (linear chain)
- Union: O(n) worst case (depends on find)

**With path compression only:** O(log n) amortized per operation.

**With union by rank only:** O(log n) worst case per operation.

**With both:** O(alpha(n)) amortized — the best known bound for this data structure.

---

## Core Mechanics

### The Fundamental Idea

Union-Find manages a collection of disjoint sets. Each set has a "representative" element (the root). Two elements are in the same set if and only if they have the same root.

Think of it as a forest of trees. Each tree is one set. The root of each tree is the representative. When you merge two sets, you attach one tree's root under the other.

### The Two Operations

**Find(x):** Follow parent pointers from x up to the root. The root is the representative of x's set.

```
Before path compression:        After path compression:
       1                              1
      / \                          / | | \
     2   3                        2  3  4  5
    / \
   4   5

Find(5) walks: 5 → 2 → 1        Find(5) walks: 5 → 1 (direct)
```

**Union(x, y):** Find the roots of x and y. If they differ, make one root point to the other. This merges the two sets into one.

### Two Critical Optimizations

Without optimizations, Union-Find degenerates to O(n) per operation. With both optimizations, it achieves O(alpha(n)) amortized — effectively constant time.

**1. Path Compression (in Find)**

When finding the root, make every node on the path point directly to the root. This flattens the tree, making future finds faster.

```
Without path compression:       With path compression:
Find(5):                        Find(5):
    1                               1
    |                            / | | \
    2                           2  3  4  5
    |
    3                           Every node now points directly to root.
    |                           Next Find(5) is O(1).
    4
    |
    5
```

**2. Union by Rank (in Union)**

When merging two trees, attach the shorter tree under the taller tree. This keeps trees balanced and prevents them from becoming long chains.

```
rank[A] = 2, rank[B] = 1

Correct (attach B under A):    Wrong (attach A under B):
      A                              B
     / \                             |
    ..  B                            A
        |                           / \
        ..                         ..  ..
                                   (taller, slower finds)
```

**Why both matter together:**
- Path compression alone: amortized O(log n)
- Union by rank alone: O(log n) worst case
- Both together: O(alpha(n)) amortized, where alpha is the inverse Ackermann function (practically <= 4 for any realistic input)

### The Invariant

At all times, two elements x and y are in the same connected component if and only if `find(x) == find(y)`. The number of distinct roots equals the number of connected components.

---

## The Template

### Python Template

```python
class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))  # Each element is its own parent
        self.rank = [0] * n           # Rank (upper bound on height)
        self.count = n                # Number of connected components

    def find(self, x: int) -> int:
        """Find root with path compression."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        """Union by rank. Returns True if x and y were in different components."""
        root_x, root_y = self.find(x), self.find(y)
        if root_x == root_y:
            return False  # Already in same component

        # Attach smaller tree under larger tree
        if self.rank[root_x] < self.rank[root_y]:
            root_x, root_y = root_y, root_x
        self.parent[root_y] = root_x
        if self.rank[root_x] == self.rank[root_y]:
            self.rank[root_x] += 1

        self.count -= 1  # One fewer component
        return True

    def connected(self, x: int, y: int) -> bool:
        """Check if x and y are in the same component."""
        return self.find(x) == self.find(y)
```

### Go Template

```go
type UnionFind struct {
    parent []int
    rank   []int
    count  int
}

func NewUnionFind(n int) *UnionFind {
    uf := &UnionFind{
        parent: make([]int, n),
        rank:   make([]int, n),
        count:  n,
    }
    for i := range uf.parent {
        uf.parent[i] = i
    }
    return uf
}

func (uf *UnionFind) Find(x int) int {
    if uf.parent[x] != x {
        uf.parent[x] = uf.Find(uf.parent[x]) // Path compression
    }
    return uf.parent[x]
}

func (uf *UnionFind) Union(x, y int) bool {
    rootX, rootY := uf.Find(x), uf.Find(y)
    if rootX == rootY {
        return false
    }
    if uf.rank[rootX] < uf.rank[rootY] {
        rootX, rootY = rootY, rootX
    }
    uf.parent[rootY] = rootX
    if uf.rank[rootX] == uf.rank[rootY] {
        uf.rank[rootX]++
    }
    uf.count--
    return true
}

func (uf *UnionFind) Connected(x, y int) bool {
    return uf.Find(x) == uf.Find(y)
}
```

### Variant: Iterative Path Compression (avoids stack overflow)

```python
class UnionFindIterative:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n

    def find(self, x: int) -> int:
        """Iterative find with two-pass path compression."""
        # First pass: find root
        root = x
        while self.parent[root] != root:
            root = self.parent[root]

        # Second pass: compress path
        while self.parent[x] != root:
            next_x = self.parent[x]
            self.parent[x] = root
            x = next_x

        return root

    def union(self, x: int, y: int) -> bool:
        root_x, root_y = self.find(x), self.find(y)
        if root_x == root_y:
            return False
        if self.rank[root_x] < self.rank[root_y]:
            root_x, root_y = root_y, root_x
        self.parent[root_y] = root_x
        if self.rank[root_x] == self.rank[root_y]:
            self.rank[root_x] += 1
        self.count -= 1
        return True
```

When to use iterative vs recursive: In interviews, recursive is cleaner and perfectly fine. In production systems with very deep trees (before optimizations stabilize), iterative avoids stack overflow. Mention this trade-off if the interviewer asks.

### Variant: Union by Size (tracks component sizes)

```python
class UnionFindWithSize:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.size = [1] * n  # Size of each component
        self.count = n

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        root_x, root_y = self.find(x), self.find(y)
        if root_x == root_y:
            return False
        # Attach smaller component under larger
        if self.size[root_x] < self.size[root_y]:
            root_x, root_y = root_y, root_x
        self.parent[root_y] = root_x
        self.size[root_x] += self.size[root_y]
        self.count -= 1
        return True

    def get_size(self, x: int) -> int:
        return self.size[self.find(x)]
```

---

## Variant Subpatterns

### 1. Basic Component Counting
Count connected components after processing edges. The simplest application.

### 2. Cycle Detection in Undirected Graphs
If `union(u, v)` returns False, the edge (u, v) creates a cycle because u and v were already connected.

### 3. Weighted Union-Find
Each edge has a weight. Track the "distance" or "relationship" from each node to its root. Used in problems like evaluating division equations.

### 4. Union-Find with String Keys
Use a dictionary instead of an array for parent mapping. Useful when elements are strings (like email addresses in Accounts Merge).

### 5. Dynamic Union-Find (Online)
Process edges one at a time and answer queries between additions. This is where Union-Find truly shines over BFS/DFS.

### 6. Union-Find on 2D Grids
For grid problems like Number of Islands, map 2D coordinates to 1D indices: `id = row * cols + col`. This lets you use the standard array-based Union-Find.

```python
def to_id(r, c, cols):
    return r * cols + c

# For a 3x4 grid:
# (0,0)=0, (0,1)=1, (0,2)=2, (0,3)=3
# (1,0)=4, (1,1)=5, (1,2)=6, (1,3)=7
# (2,0)=8, (2,1)=9, (2,2)=10, (2,3)=11
```

---

## Problem Walkthroughs

---

### Problem 1: Number of Connected Components in an Undirected Graph (LC 323 — Medium)

**Problem:** You have `n` nodes labeled from 0 to n-1 and a list of undirected edges. Write a function to find the number of connected components.

**Brute Force Approach:**
Run BFS/DFS from every unvisited node, counting the number of times you start a new traversal. Time: O(V + E), Space: O(V + E) for adjacency list.

**Key Insight:**
Start with n components (each node is its own component). For each edge, union the two endpoints. Each successful union reduces the component count by 1. The final count is the answer.

**Optimal Solution:**

```python
def countComponents(n: int, edges: list[list[int]]) -> int:
    """
    LC 323: Number of Connected Components

    Time: O(E * alpha(n)) ≈ O(E)
    Space: O(n)
    """
    uf = UnionFind(n)
    for u, v in edges:
        uf.union(u, v)
    return uf.count
```

**Dry Run:**
```
n = 5, edges = [[0,1], [1,2], [3,4]]

Initial: Components = 5, each node is its own root
  parent: [0, 1, 2, 3, 4]

Process edge [0,1]:
  find(0)=0, find(1)=1, different → union
  parent: [0, 0, 2, 3, 4], count = 4

Process edge [1,2]:
  find(1)=0, find(2)=2, different → union
  parent: [0, 0, 0, 3, 4], count = 3

Process edge [3,4]:
  find(3)=3, find(4)=4, different → union
  parent: [0, 0, 0, 3, 3], count = 2

Result: 2 components → {0,1,2} and {3,4}
```

**Edge Cases:**
- n = 1, no edges: return 1
- Fully connected graph: return 1
- No edges: return n
- Duplicate edges: union returns False, no effect

**Follow-up:** What if edges are added dynamically and you need to answer "how many components?" after each addition? Union-Find handles this naturally — just return `uf.count` after each union.

**BFS/DFS alternative for comparison:**

```python
def countComponents_bfs(n, edges):
    """BFS approach for comparison. O(V + E) time, O(V + E) space."""
    from collections import defaultdict, deque
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    visited = set()
    count = 0
    for node in range(n):
        if node not in visited:
            count += 1
            queue = deque([node])
            visited.add(node)
            while queue:
                curr = queue.popleft()
                for neighbor in graph[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
    return count
```

Both approaches give O(V + E) for a single computation. Union-Find wins when you need to answer queries after each edge addition.

---

### Problem 2: Redundant Connection (LC 684 — Medium)

**Problem:** A tree with n nodes has exactly n-1 edges. Given a graph that started as a tree and has one extra edge added, find and return the extra edge. If multiple answers, return the one that occurs last in the input.

**Brute Force:**
For each edge, remove it and check if the remaining graph is still connected (using BFS/DFS). O(E * (V + E)).

**Key Insight:**
A tree has exactly n-1 edges and no cycles. The extra edge is the one that creates a cycle. Process edges in order — the first edge where both endpoints are already connected (same component) is creating a cycle. Since we want the last such edge in the input, and a tree with one extra edge has exactly one cycle, there is exactly one such edge.

**Optimal Solution:**

```python
def findRedundantConnection(edges: list[list[int]]) -> list[int]:
    """
    LC 684: Redundant Connection

    Time: O(n * alpha(n)) ≈ O(n)
    Space: O(n)
    """
    n = len(edges)
    uf = UnionFind(n + 1)  # Nodes are 1-indexed

    for u, v in edges:
        if not uf.union(u, v):
            return [u, v]  # This edge creates a cycle

    return []  # Should not reach here per problem constraints
```

**Dry Run:**
```
edges = [[1,2], [1,3], [2,3]]

Process [1,2]: find(1)=1, find(2)=2 → different, union them
Process [1,3]: find(1)=1, find(3)=3 → different, union them
Process [2,3]: find(2)=1, find(3)=1 → SAME! This is redundant.

Return [2,3]
```

**Edge Cases:**
- The extra edge connects nodes already in a chain
- Self-loops (not in this problem, but worth mentioning)
- Multiple edges between same pair (problem guarantees unique edges)

**Follow-up:** What about directed graphs? See Redundant Connection II (LC 685 — Hard). The directed version requires handling cases where a node has two parents or there is a cycle.

---

### Problem 3: Accounts Merge (LC 721 — Medium)

**Problem:** Given a list of accounts where each account is `[name, email1, email2, ...]`, merge accounts that share at least one common email. Return merged accounts with sorted emails.

**Brute Force:**
For each pair of accounts, check if they share any email. If yes, merge them. O(n^2 * m) where m is average emails per account.

**Key Insight:**
This is a connected components problem where emails are nodes and accounts define edges. If two emails appear in the same account, they are connected. All emails in the same connected component belong to the same person.

Strategy: Map each email to an integer ID. For each account, union all emails in that account together. Then group emails by their root and reconstruct accounts.

**Optimal Solution:**

```python
def accountsMerge(accounts: list[list[str]]) -> list[list[str]]:
    """
    LC 721: Accounts Merge

    Time: O(n * m * alpha(n*m)) where n = accounts, m = avg emails
    Space: O(n * m)
    """
    from collections import defaultdict

    # Step 1: Assign an ID to each unique email
    email_to_id = {}
    email_to_name = {}
    next_id = 0

    for account in accounts:
        name = account[0]
        for email in account[1:]:
            if email not in email_to_id:
                email_to_id[email] = next_id
                next_id += 1
            email_to_name[email] = name

    # Step 2: Union all emails within the same account
    uf = UnionFind(next_id)
    for account in accounts:
        first_email_id = email_to_id[account[1]]
        for email in account[2:]:
            uf.union(first_email_id, email_to_id[email])

    # Step 3: Group emails by their root
    root_to_emails = defaultdict(list)
    for email, eid in email_to_id.items():
        root = uf.find(eid)
        root_to_emails[root].append(email)

    # Step 4: Build result
    result = []
    for root, emails in root_to_emails.items():
        emails.sort()
        name = email_to_name[emails[0]]
        result.append([name] + emails)

    return result
```

**Dry Run:**
```
accounts = [
    ["John", "john@a.com", "john@b.com"],
    ["John", "john@b.com", "john@c.com"],
    ["Mary", "mary@a.com"]
]

Step 1: email_to_id = {john@a: 0, john@b: 1, john@c: 2, mary@a: 3}

Step 2:
  Account 0: union(0, 1) → {john@a, john@b} merged
  Account 1: union(1, 2) → find(1)=0, find(2)=2, union → {john@a, john@b, john@c}
  Account 2: only one email, nothing to union

Step 3:
  root 0 → [john@a.com, john@b.com, john@c.com]
  root 3 → [mary@a.com]

Result: [["John", "john@a.com", "john@b.com", "john@c.com"], ["Mary", "mary@a.com"]]
```

**Edge Cases:**
- Same name, different people (different email sets)
- Account with single email (no unions needed)
- Long chains of accounts connected transitively

**Follow-up:** How would you handle this if accounts are streaming in? You would maintain the Union-Find structure and email mappings, updating as new accounts arrive.

---

### Problem 4: Smallest String With Swaps (LC 1202 — Medium)

**Problem:** Given a string `s` and a list of pairs of indices where you can swap the characters at those indices any number of times, return the lexicographically smallest string possible.

**Brute Force:**
Try all possible sequences of swaps using BFS/backtracking. Exponential time.

**Key Insight:**
If you can swap positions i and j, and also j and k, then transitively you can rearrange positions i, j, k in any order. So all positions in the same connected component can be freely rearranged. For each component, sort the characters to get the lexicographically smallest arrangement.

**Optimal Solution:**

```python
def smallestStringWithSwaps(s: str, pairs: list[list[int]]) -> str:
    """
    LC 1202: Smallest String With Swaps

    Time: O(n log n + E * alpha(n))
    Space: O(n)
    """
    from collections import defaultdict

    n = len(s)
    uf = UnionFind(n)

    # Union all swappable positions
    for i, j in pairs:
        uf.union(i, j)

    # Group indices by their root
    root_to_indices = defaultdict(list)
    for i in range(n):
        root_to_indices[uf.find(i)].append(i)

    # For each component, sort characters and assign back
    result = list(s)
    for indices in root_to_indices.values():
        chars = sorted(result[i] for i in indices)
        for i, idx in enumerate(sorted(indices)):
            result[idx] = chars[i]

    return ''.join(result)
```

**Dry Run:**
```
s = "dcab", pairs = [[0,3], [1,2]]

Union(0, 3): positions 0 and 3 are in one component
Union(1, 2): positions 1 and 2 are in one component

Components: {0, 3} and {1, 2}

Component {0, 3}: chars at positions 0,3 are 'd','b' → sorted: 'b','d'
  → position 0 = 'b', position 3 = 'd'

Component {1, 2}: chars at positions 1,2 are 'c','a' → sorted: 'a','c'
  → position 1 = 'a', position 2 = 'c'

Result: "bacd"
```

**Edge Cases:**
- No pairs: return the original string
- All positions connected: sort the entire string
- Single character string

**Follow-up:** What if swaps have costs and you want the smallest string with minimum cost? That becomes an MST + sorting problem.

---

### Problem 5: Number of Islands II (LC 305 — Hard)

**Problem:** Given an m x n grid initially all water (0), you are given a list of positions to turn into land (1) one at a time. After each operation, return the number of islands. An island is a group of connected land cells (4-directional).

**Brute Force:**
After each land addition, run BFS/DFS to count all islands from scratch. Time: O(k * m * n) where k is number of operations.

**Key Insight:**
This is a dynamic connectivity problem — Union-Find's specialty. When a new land cell is added:
1. It starts as its own island (component count + 1)
2. Check all 4 neighbors. If a neighbor is also land, union them (each successful union reduces count by 1)
3. The current count is the answer for this step

**Optimal Solution:**

```python
def numIslands2(m: int, n: int, positions: list[list[int]]) -> list[int]:
    """
    LC 305: Number of Islands II

    Time: O(k * alpha(m*n)) per operation ≈ O(k)
    Space: O(m * n)
    """
    parent = {}
    rank = {}
    count = 0
    result = []

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        nonlocal count
        rx, ry = find(x), find(y)
        if rx == ry:
            return
        if rank.get(rx, 0) < rank.get(ry, 0):
            rx, ry = ry, rx
        parent[ry] = rx
        if rank.get(rx, 0) == rank.get(ry, 0):
            rank[rx] = rank.get(rx, 0) + 1
        count -= 1

    for r, c in positions:
        pos = (r, c)
        if pos in parent:  # Duplicate position, skip
            result.append(count)
            continue

        parent[pos] = pos
        rank[pos] = 0
        count += 1  # New island

        # Check 4 neighbors
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            neighbor = (nr, nc)
            if neighbor in parent:  # Neighbor is land
                union(pos, neighbor)

        result.append(count)

    return result
```

**Dry Run:**
```
m=3, n=3, positions = [[0,0], [0,1], [1,2], [2,1], [1,1]]

Add (0,0): No land neighbors. count=1. Result: [1]
  Land: {(0,0)}

Add (0,1): Neighbor (0,0) is land. Union → count=1. Result: [1,1]
  Components: {(0,0),(0,1)}

Add (1,2): No land neighbors. count=2. Result: [1,1,2]
  Components: {(0,0),(0,1)}, {(1,2)}

Add (2,1): No land neighbors. count=3. Result: [1,1,2,3]
  Components: {(0,0),(0,1)}, {(1,2)}, {(2,1)}

Add (1,1): Neighbors (0,1) is land, (1,2) is land, (2,1) is land.
  count starts at 4 (new island)
  Union with (0,1): count=3
  Union with (1,2): count=2
  Union with (2,1): count=1
  Result: [1,1,2,3,1]
```

**Edge Cases:**
- Duplicate positions in the input (handle by checking if already land)
- Position at grid boundary (neighbors may be out of bounds)
- All positions in a line (chain of unions)

**Follow-up:** What if you also need to support removing land? Union-Find does not support efficient "undo" — you would need a different data structure or process operations in reverse.

---

### Problem 6: Minimize Malware Spread (LC 924 — Hard)

**Problem:** Given a graph as an adjacency matrix and an initial list of infected nodes, removing exactly one infected node from the initial list minimizes the final number of infected nodes. Return that node. If ties, return the one with the smallest index.

**Brute Force:**
For each infected node, simulate removing it and run BFS/DFS to count total infected nodes. Time: O(k * n^2) where k = number of initially infected nodes.

**Key Insight:**
Build the connected components ignoring all infected nodes. For each component, count how many infected nodes are adjacent to it. If a component touches exactly one infected node, removing that node saves the entire component. Choose the node that saves the most nodes (tie-break by smallest index).

Actually, the cleaner approach: Build Union-Find for all nodes. Then for each connected component, count how many nodes from `initial` are in it. If a component has exactly 1 infected node, removing it saves that component. If a component has 2+ infected nodes, removing one still leaves the others to infect it.

**Optimal Solution:**

```python
def minMalwareSpread(graph: list[list[int]], initial: list[int]) -> int:
    """
    LC 924: Minimize Malware Spread

    Time: O(n^2) to build components from adjacency matrix
    Space: O(n)
    """
    from collections import Counter

    n = len(graph)
    uf = UnionFind(n)

    # Build connected components
    for i in range(n):
        for j in range(i + 1, n):
            if graph[i][j] == 1:
                uf.union(i, j)

    # Count component sizes
    component_size = Counter()
    for i in range(n):
        component_size[uf.find(i)] += 1

    # For each component, count how many initially infected nodes it contains
    infected_set = set(initial)
    component_infected_count = Counter()
    for node in initial:
        component_infected_count[uf.find(node)] += 1

    # Find the node whose removal saves the most
    best_node = min(initial)  # Default: smallest index
    best_saved = 0

    for node in initial:
        root = uf.find(node)
        if component_infected_count[root] == 1:
            # This is the only infected node in its component
            # Removing it saves the entire component
            saved = component_size[root]
            if saved > best_saved or (saved == best_saved and node < best_node):
                best_saved = saved
                best_node = node

    return best_node
```

**Dry Run:**
```
graph = [[1,1,0],[1,1,0],[0,0,1]], initial = [0, 1]

Build components: union(0,1) since graph[0][1]=1
Components: {0,1} (size 2), {2} (size 1)

Infected in component of 0: find(0)=0, find(1)=0 → 2 infected nodes
Infected in component of 2: not in initial

Component {0,1} has 2 infected nodes → removing either doesn't save it
No component has exactly 1 infected node → best_saved=0

Return min(initial) = 0
```

**Edge Cases:**
- All infected nodes in the same component: return smallest index
- Infected node is isolated: removing it saves 1 node
- Single infected node: must return it

**Follow-up:** What about Minimize Malware Spread II (LC 928)? In that variant, you physically remove the node and all its edges, not just un-infect it. The approach changes: build components ignoring infected nodes entirely, then for each infected node, count how many unique components it connects to. Removing the infected node that uniquely connects the most uninfected nodes saves the most.

**Detailed complexity analysis:**
- Building Union-Find: O(n^2) to process the adjacency matrix
- Counting component sizes: O(n)
- Finding the best node to remove: O(|initial|)
- Total: O(n^2) dominated by the adjacency matrix traversal

This problem tests whether you understand the difference between "removing infection from a node" (LC 924) and "removing a node entirely" (LC 928).

---

### Problem 7: Remove Max Number of Edges to Keep Graph Fully Traversable (LC 1579 — Hard)

This problem is a beautiful application of Union-Find that combines greedy strategy with dual data structures.

**Problem:** Alice and Bob have an undirected graph of n nodes. There are 3 types of edges:
- Type 1: only Alice can traverse
- Type 2: only Bob can traverse
- Type 3: both can traverse

Return the maximum number of edges you can remove while both Alice and Bob can still traverse the entire graph. Return -1 if impossible.

**Brute Force:**
Try all subsets of edges to remove. For each subset, check if the remaining graph is fully traversable by both Alice and Bob. Exponential.

**Key Insight:**
Greedy + two Union-Find structures. Process type 3 edges first (shared edges are most valuable — they serve double duty). Then process type 1 and type 2 edges separately. An edge is redundant (removable) if it connects two already-connected nodes.

**Optimal Solution:**

```python
def maxNumEdgesToRemove(n: int, edges: list[list[int]]) -> int:
    """
    LC 1579: Remove Max Number of Edges to Keep Graph Fully Traversable

    Time: O(E * alpha(n)) ≈ O(E)
    Space: O(n)
    """
    alice = UnionFind(n + 1)  # 1-indexed nodes
    bob = UnionFind(n + 1)
    removed = 0

    # Process type 3 edges first (most valuable)
    for edge_type, u, v in edges:
        if edge_type == 3:
            # Add to both Alice and Bob
            added_alice = alice.union(u, v)
            added_bob = bob.union(u, v)
            if not added_alice and not added_bob:
                removed += 1  # Redundant for both

    # Process type 1 (Alice only) and type 2 (Bob only)
    for edge_type, u, v in edges:
        if edge_type == 1:
            if not alice.union(u, v):
                removed += 1
        elif edge_type == 2:
            if not bob.union(u, v):
                removed += 1

    # Check if both can fully traverse (single component, ignoring node 0)
    # After unions, there should be exactly 2 components in each UF
    # (one real component + the unused node 0)
    if alice.count != 2 or bob.count != 2:
        return -1

    return removed
```

**Wait — there is a subtlety.** When we process type 3 edges, we need to count a type-3 edge as removable only if it is redundant for both Alice AND Bob. But actually, a type-3 edge is used by both, so if it is not needed by either, it can be removed. Let me reconsider.

Actually, the correct logic: A type-3 edge is added to both. If it was needed by at least one of them, it must stay. It can only be removed if it was redundant for both.

Let me fix:

```python
def maxNumEdgesToRemove(n: int, edges: list[list[int]]) -> int:
    """
    LC 1579: Remove Max Number of Edges to Keep Graph Fully Traversable

    Time: O(E * alpha(n)) ≈ O(E)
    Space: O(n)
    """
    alice = UnionFind(n + 1)  # 1-indexed, node 0 unused
    bob = UnionFind(n + 1)
    edges_used = 0

    # Process type 3 edges first (shared edges are most valuable)
    for edge_type, u, v in edges:
        if edge_type == 3:
            # Edge is used if it merges new components in at least one graph
            a = alice.union(u, v)
            b = bob.union(u, v)
            if a or b:
                edges_used += 1

    # Process type 1 (Alice only) and type 2 (Bob only)
    for edge_type, u, v in edges:
        if edge_type == 1:
            if alice.union(u, v):
                edges_used += 1
        elif edge_type == 2:
            if bob.union(u, v):
                edges_used += 1

    # Check full traversability: exactly 2 components (node 0 unused + 1 real)
    if alice.count != 2 or bob.count != 2:
        return -1

    return len(edges) - edges_used
```

**Dry Run:**
```
n=4, edges=[[3,1,2],[3,2,3],[1,1,3],[1,1,2],[2,1,3],[2,2,4],[2,3,4]]

Process type 3 edges:
  [3,1,2]: alice.union(1,2)=T, bob.union(1,2)=T → used. edges_used=1
  [3,2,3]: alice.union(2,3)=T, bob.union(2,3)=T → used. edges_used=2

Process type 1 (Alice):
  [1,1,3]: alice: find(1) and find(3) already same → not used
  [1,1,2]: alice: already same → not used

Process type 2 (Bob):
  [2,1,3]: bob: already same → not used
  [2,2,4]: bob.union(2,4)=T → used. edges_used=3
  [2,3,4]: bob: already same → not used

alice components: {0}, {1,2,3} → need node 4! Alice can't reach 4.
Wait — node 4 has no Alice edges. alice.count would be 3 (nodes 0, {1,2,3}, {4}).

Return -1? Let me re-examine...

Actually we need type 1 or type 3 edges to connect node 4 for Alice.
There are none, so Alice cannot reach node 4. Return -1.
```

**Edge Cases:**
- Graph already cannot be made fully traversable: return -1
- All edges are type 3: maximum sharing potential
- Only type 1 and type 2 edges: need separate spanning trees

**Follow-up:** What if we wanted to minimize the total weight of edges kept (MST variant)? Use Kruskal's algorithm with the same type-3-first priority.

---

## Common Mistakes & Interview Tips

### Common Mistakes

1. **Forgetting path compression:** Without it, find() degrades to O(n). Always include the one-liner: `self.parent[x] = self.find(self.parent[x])`

2. **Forgetting union by rank:** Without it, trees can become skewed chains. The combination of both optimizations is what gives O(alpha(n)).

3. **Off-by-one with 1-indexed nodes:** Many problems use 1-indexed nodes. Either allocate n+1 slots or convert to 0-indexed.

4. **Not checking if already connected before union:** The `union` function should return a boolean indicating whether a merge happened. This is critical for cycle detection (Redundant Connection) and edge counting.

5. **Confusing Union by Rank vs Union by Size:** Rank is an upper bound on tree height and does not change with path compression. Size is the actual count of nodes. They serve different purposes — use size when you need component sizes.

6. **Iterative vs Recursive Find:** In very deep trees (before optimizations kick in), recursive find can stack overflow. Use iterative path compression for safety in production (though recursive is fine for interviews):

```python
def find_iterative(self, x):
    root = x
    while self.parent[root] != root:
        root = self.parent[root]
    while self.parent[x] != root:
        self.parent[x], x = root, self.parent[x]
    return root
```

### Interview Tips

1. **State your approach clearly:** "I will use Union-Find because we need dynamic connectivity / component counting / cycle detection."

2. **Write the UF class first:** Interviewers expect you to know the template cold. Write it quickly and correctly, then use it as a building block.

3. **Mention optimizations proactively:** "I am using path compression and union by rank, which gives us amortized O(alpha(n)) per operation — effectively constant time."

4. **Know the BFS/DFS alternative:** Be prepared to discuss why you chose Union-Find over BFS/DFS. The key differentiator is dynamic connectivity and repeated queries.

5. **Component count tracking:** Always maintain a `count` variable that decrements on successful unions. Many problems need this.

6. **Dictionary-based UF:** For problems with non-integer keys (emails, strings), use `dict` for parent instead of a list. Show you can adapt the template.

---

## Pattern Connections

| From Union-Find | Connect To | How |
|-----------------|-----------|-----|
| Component counting | Graph DFS/BFS | Same goal, different trade-offs |
| Cycle detection | DFS back edges | UF works on edge lists, DFS works on adjacency lists |
| Kruskal's MST | Greedy algorithms | UF is the core data structure for Kruskal's |
| Accounts Merge | Graph connected components | UF with string keys |
| Number of Islands II | BFS/DFS grid problems | UF handles dynamic additions better |
| Redundant Connection | Tree properties | n nodes, n edges = exactly one cycle |
| Weighted UF | Evaluate Division (LC 399) | Track ratios along edges |

### Decision Framework

```
Need connectivity queries?
├── Static graph (built once, queried once)
│   └── Use BFS/DFS
├── Dynamic graph (edges added over time, queried repeatedly)
│   └── Use Union-Find
├── Need actual path?
│   └── Use BFS (shortest) or DFS (any path)
└── Need component sizes/counts as edges are added?
    └── Use Union-Find with size tracking
```

---

## Additional Problem: Evaluate Division (LC 399 — Medium)

**Problem:** Given equations like `a/b = 2.0`, `b/c = 3.0`, find answers to queries like `a/c = ?`. If the answer cannot be determined, return -1.0.

**Key Insight (Weighted Union-Find):**
Model this as a weighted graph where edge `a → b` has weight `a/b`. If `a/b = 2` and `b/c = 3`, then `a/c = a/b * b/c = 6`. Union-Find can track the weight (ratio) from each node to its root, allowing computation of ratios between any two nodes in the same component.

**Alternative:** BFS/DFS on the graph, multiplying weights along the path. Both approaches work, but weighted Union-Find is more elegant for repeated queries.

```python
class WeightedUnionFind:
    def __init__(self):
        self.parent = {}
        self.weight = {}  # weight[x] = x / parent[x]

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.weight[x] = 1.0
        if self.parent[x] != x:
            root = self.find(self.parent[x])
            self.weight[x] *= self.weight[self.parent[x]]
            self.parent[x] = root
        return self.parent[x]

    def union(self, x, y, w):
        """x / y = w"""
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        # weight[x] = x / rx, weight[y] = y / ry
        # We want rx / ry = (x / w) / (y / 1) * ... = w * weight[y] / weight[x]
        self.parent[rx] = ry
        self.weight[rx] = w * self.weight[y] / self.weight[x]

    def query(self, x, y):
        if x not in self.parent or y not in self.parent:
            return -1.0
        if self.find(x) != self.find(y):
            return -1.0
        return self.weight[x] / self.weight[y]


def calcEquation(equations, values, queries):
    uf = WeightedUnionFind()
    for (a, b), v in zip(equations, values):
        uf.union(a, b, v)
    return [uf.query(a, b) for a, b in queries]
```

This problem demonstrates that Union-Find can track more than just connectivity — it can maintain relationships (ratios, distances) between nodes.

---

## Interview Cheat Sheet

**Template to write first (30 seconds):**
```python
class UF:
    def __init__(self, n):
        self.p = list(range(n))
        self.r = [0] * n
        self.cnt = n

    def find(self, x):
        if self.p[x] != x:
            self.p[x] = self.find(self.p[x])
        return self.p[x]

    def union(self, x, y):
        a, b = self.find(x), self.find(y)
        if a == b: return False
        if self.r[a] < self.r[b]: a, b = b, a
        self.p[b] = a
        if self.r[a] == self.r[b]: self.r[a] += 1
        self.cnt -= 1
        return True
```

**Five things to say when using Union-Find in an interview:**
1. "I am using Union-Find because we need [dynamic connectivity / cycle detection / component counting]."
2. "I use path compression and union by rank for amortized O(alpha(n)) per operation."
3. "Each union returns a boolean indicating whether a merge occurred."
4. "I maintain a count of connected components that decrements on each successful union."
5. "The alternative would be BFS/DFS, but Union-Find is better here because [edges are processed incrementally / we need repeated queries]."

---

## Problem Difficulty Progression

**Tier 1 — Foundation (must solve easily):**
1. Number of Connected Components (LC 323) — template application
2. Redundant Connection (LC 684) — cycle detection
3. Number of Provinces (LC 547) — component counting with adjacency matrix

**Tier 2 — Core Patterns (should solve within 20 min):**
4. Accounts Merge (LC 721) — dictionary-based UF
5. Smallest String With Swaps (LC 1202) — transitivity insight
6. Satisfiability of Equality Equations (LC 990) — equals vs not-equals

**Tier 3 — Hard Applications (stretch goals):**
7. Number of Islands II (LC 305) — dynamic connectivity
8. Minimize Malware Spread (LC 924) — component analysis
9. Remove Max Number of Edges (LC 1579) — dual UF + greedy
10. Evaluate Division (LC 399) — weighted UF

---

## Common Variations in Interviews

### Variation 1: "Can you do this without Union-Find?"
Yes — BFS/DFS works for static graphs. Union-Find is an optimization for dynamic connectivity and repeated queries.

### Variation 2: "What about weighted edges?"
Weighted Union-Find tracks the relationship (ratio, distance) from each node to its root. See Evaluate Division (LC 399).

### Variation 3: "What if we need to undo unions?"
Standard Union-Find with path compression does not support efficient undo. Options:
- Persistent Union-Find (not practical in interviews)
- Process operations in reverse (offline)
- Use Union by rank WITHOUT path compression (enables rollback by storing the undo stack)

### Variation 4: "What is the space complexity?"
O(n) for the parent and rank arrays. If using dictionary-based UF, O(k) where k is the number of unique elements seen.

---

## Detailed Walkthrough: Why Union by Rank Keeps Trees Balanced

**Claim:** With union by rank (without path compression), the tree height is at most log(n).

**Proof sketch:** A tree of rank k has at least 2^k nodes. This is because:
- Base case: rank 0 tree has 1 = 2^0 node
- Inductive step: rank k is created only by merging two rank k-1 trees. By induction, each has >= 2^(k-1) nodes. Together: >= 2^k nodes.

Since a tree of rank k has >= 2^k nodes, and we have n nodes total, the maximum rank is log(n). This bounds the height, and therefore the find operation, to O(log n).

Path compression on top of this further reduces the amortized cost to O(alpha(n)).

**Why rank vs size:** Both give O(log n) height bounds. Rank is simpler (just an integer that never changes after creation). Size is more useful when you need to know how many elements are in a component. In practice, the choice rarely matters.

---

## Additional Problem: Most Stones Removed with Same Row or Column (LC 947 — Medium)

**Problem:** On a 2D plane, stones are placed at integer coordinates. A stone can be removed if it shares a row or column with another stone. Return the maximum number of stones that can be removed.

**Key Insight:**
Stones that share a row or column are connected. Each connected component of size k allows k-1 removals (you must leave one stone). Answer = total stones - number of components.

The clever trick: instead of connecting stones to stones (O(n^2)), connect stones to their row and column IDs. Use `~col` (bitwise complement) to distinguish column IDs from row IDs in the same Union-Find.

```python
def removeStones(stones: list[list[int]]) -> int:
    """
    LC 947: Most Stones Removed

    Time: O(n * alpha(n))
    Space: O(n)
    """
    parent = {}

    def find(x):
        if x not in parent:
            parent[x] = x
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        parent[find(x)] = find(y)

    for r, c in stones:
        union(r, ~c)  # ~c ensures column IDs don't collide with row IDs

    # Count components (unique roots among stone coordinates)
    components = len({find(r) for r, c in stones})
    return len(stones) - components
```

This problem beautifully demonstrates the power of Union-Find for implicit graph problems where building an explicit adjacency list would be too expensive.
