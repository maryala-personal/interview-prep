# Union-Find (Disjoint Set Union) Pattern

## What is Union-Find?

### Explain Like I'm 5
Imagine you have a bunch of friends at school. Some friends know each other, and some don't. When two friends meet, their entire friend groups become one big group. Union-Find is like keeping track of which big friend group each person belongs to. You can quickly check if two people are in the same friend group, or merge two friend groups together.

### Technical Definition
Union-Find, also known as Disjoint Set Union (DSU), is a data structure that tracks a set of elements partitioned into disjoint (non-overlapping) subsets. It provides near-constant-time operations to:
- **Union**: Merge two subsets into a single subset
- **Find**: Determine which subset a particular element is in

## Real-World Analogy

### Social Network Friend Groups
Think of Facebook or LinkedIn connections:
- Initially, everyone is in their own group (just themselves)
- When person A connects with person B, their groups merge
- You can quickly check if two people are connected (directly or through mutual connections)
- Friend recommendations can use this: "You might know X because you're both in the same network component"

### Connected Cities
Imagine cities connected by roads:
- Initially, each city is isolated
- As roads are built, cities become connected
- Union-Find helps answer: "Can I drive from City A to City B?" (even through other cities)
- Adding a new road is a union operation
- Checking connectivity is a find operation

## When to Use Union-Find

### Clear Signals
Use Union-Find when you see these patterns:

1. **Connected Components**: Need to find or count groups of connected elements
2. **Dynamic Connectivity**: Elements are being connected over time, and you need to query connectivity
3. **Cycle Detection**: In undirected graphs, detect if adding an edge creates a cycle
4. **Grouping/Clustering**: Merging groups based on some relationship
5. **Equivalence Relations**: Track transitive relationships (if A~B and B~C, then A~C)

### Keywords to Look For
- "Connected components"
- "Groups" or "clusters"
- "Merge" or "union"
- "Are X and Y in the same group?"
- "Number of distinct groups"
- "Redundant connection"
- "Network connectivity"

## The Problem: Number of Connected Components

```
Given n nodes labeled from 0 to n-1 and a list of undirected edges,
write a function to find the number of connected components in an undirected graph.

Example 1:
Input: n = 5, edges = [[0,1], [1,2], [3,4]]
Output: 2
Explanation:
  0---1---2    3---4

Example 2:
Input: n = 5, edges = [[0,1], [1,2], [2,3], [3,4]]
Output: 1
Explanation:
  0---1---2---3---4
```

## Brute Force Approach: DFS/BFS

```python
def countComponents(n, edges):
    """
    Use DFS to explore each component
    Time: O(V + E) where V = vertices, E = edges
    Space: O(V + E) for adjacency list and visited set
    """
    # Build adjacency list
    graph = {i: [] for i in range(n)}
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    visited = set()
    components = 0

    def dfs(node):
        if node in visited:
            return
        visited.add(node)
        for neighbor in graph[node]:
            dfs(neighbor)

    # Start DFS from each unvisited node
    for i in range(n):
        if i not in visited:
            dfs(i)
            components += 1

    return components
```

**Limitations of DFS/BFS:**
- Must traverse entire component for each query
- Not efficient for dynamic connectivity (edges added over time)
- Cannot easily merge components
- Requires rebuilding graph structure for updates

## Optimized Solution: Union-Find with Path Compression & Union by Rank

```python
class UnionFind:
    def __init__(self, n):
        """
        Initialize Union-Find with n elements (0 to n-1)
        Each element starts as its own parent (separate component)
        """
        self.parent = list(range(n))  # parent[i] = parent of node i
        self.rank = [1] * n           # rank[i] = approximate depth of tree rooted at i
        self.components = n           # track number of components

    def find(self, x):
        """
        Find the root/representative of the set containing x
        Uses path compression: make all nodes point directly to root

        Time: O(α(n)) - inverse Ackermann, practically O(1)
        """
        if self.parent[x] != x:
            # Path compression: set parent to root
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        """
        Merge the sets containing x and y
        Uses union by rank: attach smaller tree under root of larger tree

        Returns: True if union performed, False if already in same set
        Time: O(α(n)) - practically O(1)
        """
        root_x = self.find(x)
        root_y = self.find(y)

        # Already in same component
        if root_x == root_y:
            return False

        # Union by rank: attach smaller tree under larger tree
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            # Same rank: choose one as root, increase its rank
            self.parent[root_y] = root_x
            self.rank[root_x] += 1

        self.components -= 1
        return True

    def connected(self, x, y):
        """
        Check if x and y are in the same component
        Time: O(α(n)) - practically O(1)
        """
        return self.find(x) == self.find(y)

    def count_components(self):
        """
        Return number of distinct components
        Time: O(1)
        """
        return self.components


def countComponents(n, edges):
    """
    Count connected components using Union-Find
    Time: O(E * α(n)) where E = edges, α(n) ≈ O(1)
    Space: O(n) for parent and rank arrays
    """
    uf = UnionFind(n)

    for u, v in edges:
        uf.union(u, v)

    return uf.count_components()


# Example usage
n = 5
edges = [[0,1], [1,2], [3,4]]
print(countComponents(n, edges))  # Output: 2
```

### Why This Works

1. **Initialization**: Each node starts as its own parent (n components)
2. **Union Operations**: Each edge connects two components, reducing count by 1
3. **Path Compression**: During find, flatten tree to make future queries faster
4. **Union by Rank**: Keep trees balanced to prevent degeneration to linked lists

## Time & Space Complexity Analysis

### Without Optimizations (Naive Union-Find)
- **Find**: O(n) worst case - tree can become a linked list
- **Union**: O(n) worst case - must call find twice
- **Overall**: O(n²) for processing all edges

### With Path Compression Only
- **Amortized**: O(log n) per operation
- Better than naive, but still not optimal

### With Union by Rank Only
- **Worst case**: O(log n) per operation
- Trees stay balanced, depth is at most log n

### With Both Optimizations (Path Compression + Union by Rank)
- **Time per operation**: O(α(n)) where α is inverse Ackermann function
- **Practical reality**: α(n) ≤ 5 for any practical value of n (even n = 10^80)
- **Effectively**: Constant time O(1) per operation
- **Overall for E edges**: O(E) in practice

### Space Complexity
- **O(n)**: Store parent and rank arrays
- **O(1) additional**: For each operation

## Variations and Related Problems

### 1. Redundant Connection (Cycle Detection)
```python
def findRedundantConnection(edges):
    """
    Given a tree with one extra edge, find the edge that can be removed.
    Returns the edge that creates a cycle.

    LeetCode 684: Redundant Connection
    """
    n = len(edges)
    uf = UnionFind(n + 1)  # nodes are 1-indexed

    for u, v in edges:
        # If u and v already connected, this edge creates a cycle
        if not uf.union(u, v):
            return [u, v]

    return []

# Example
edges = [[1,2], [1,3], [2,3]]
print(findRedundantConnection(edges))  # Output: [2,3]
```

### 2. Accounts Merge (String-based Union-Find)
```python
def accountsMerge(accounts):
    """
    Merge accounts that share common emails.
    LeetCode 721: Accounts Merge

    accounts = [
        ["John", "john@mail.com", "john_work@mail.com"],
        ["John", "john@mail.com", "john_home@mail.com"],
        ["Mary", "mary@mail.com"]
    ]
    """
    from collections import defaultdict

    uf = UnionFind(len(accounts))
    email_to_id = {}  # Map email to account index

    # Step 1: Build union-find structure
    for i, account in enumerate(accounts):
        for email in account[1:]:  # Skip name at index 0
            if email in email_to_id:
                # Merge with existing account
                uf.union(i, email_to_id[email])
            else:
                email_to_id[email] = i

    # Step 2: Group emails by root account
    root_to_emails = defaultdict(set)
    for email, account_id in email_to_id.items():
        root = uf.find(account_id)
        root_to_emails[root].add(email)

    # Step 3: Format result
    result = []
    for root, emails in root_to_emails.items():
        name = accounts[root][0]
        result.append([name] + sorted(emails))

    return result
```

### 3. Most Stones Removed with Same Row or Column
```python
def removeStones(stones):
    """
    Stones in same row or column are connected.
    Maximum stones we can remove = total_stones - number_of_components

    LeetCode 947: Most Stones Removed
    """
    uf = UnionFind(20001)  # Max coordinate value

    for x, y in stones:
        # Connect row and column (offset column by 10000 to avoid collision)
        uf.union(x, y + 10001)

    # Count unique components (only those with stones)
    unique_roots = len({uf.find(x) for x, y in stones})

    return len(stones) - unique_roots
```

### 4. Satisfiability of Equality Equations
```python
def equationsPossible(equations):
    """
    Check if equality equations can all be satisfied.
    equations = ["a==b", "b!=a"] -> False
    equations = ["a==b", "b==c", "a!=c"] -> False

    LeetCode 990: Satisfiability of Equality Equations
    """
    uf = UnionFind(26)  # 26 letters

    # Process all equality equations first
    for eq in equations:
        if eq[1] == '=':  # "=="
            x = ord(eq[0]) - ord('a')
            y = ord(eq[3]) - ord('a')
            uf.union(x, y)

    # Check inequality equations
    for eq in equations:
        if eq[1] == '!':  # "!="
            x = ord(eq[0]) - ord('a')
            y = ord(eq[3]) - ord('a')
            if uf.connected(x, y):
                return False

    return True
```

### 5. Number of Islands II (Dynamic Connectivity)
```python
def numIslands2(m, n, positions):
    """
    Grid starts empty. Islands added one at a time.
    Return count of islands after each addition.

    LeetCode 305: Number of Islands II (Premium)
    """
    uf = UnionFind(m * n)
    grid = [[0] * n for _ in range(m)]
    result = []
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    for r, c in positions:
        if grid[r][c] == 1:
            # Already an island
            result.append(uf.components)
            continue

        grid[r][c] = 1
        island_id = r * n + c
        uf.components += 1

        # Check 4 neighbors
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == 1:
                neighbor_id = nr * n + nc
                uf.union(island_id, neighbor_id)

        result.append(uf.components)

    return result
```

## Pro Tips for Senior Engineers

### 1. Union-Find vs DFS/BFS Decision Matrix

**Use Union-Find when:**
- Dynamic connectivity queries (edges added over time)
- Need to quickly check if two elements are connected
- Need to count components efficiently
- Merging sets is common operation
- Multiple connectivity queries on same data
- Problem involves "grouping" or "merging"

**Use DFS/BFS when:**
- Need to find actual path between nodes
- Need to process nodes in specific order
- Need to track distances
- Graph is already built and static
- Need to find all nodes in a component
- Problem requires exploring graph structure

### 2. Implementation Optimizations

```python
class OptimizedUnionFind:
    """Advanced implementation with additional features"""

    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [1] * n
        self.size = [1] * n  # Track component sizes
        self.components = n

    def find(self, x):
        """Path compression with iterative approach (avoids recursion)"""
        root = x
        while root != self.parent[root]:
            root = self.parent[root]

        # Path compression: make all nodes point to root
        while x != root:
            next_node = self.parent[x]
            self.parent[x] = root
            x = next_node

        return root

    def union(self, x, y):
        """Union by size (alternative to rank)"""
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False

        # Attach smaller component to larger
        if self.size[root_x] < self.size[root_y]:
            self.parent[root_x] = root_y
            self.size[root_y] += self.size[root_x]
        else:
            self.parent[root_y] = root_x
            self.size[root_x] += self.size[root_y]

        self.components -= 1
        return True

    def get_component_size(self, x):
        """Get size of component containing x"""
        return self.size[self.find(x)]

    def get_all_components(self):
        """Return list of all components as sets"""
        from collections import defaultdict
        components = defaultdict(set)
        for i in range(len(self.parent)):
            components[self.find(i)].add(i)
        return list(components.values())
```

### 3. Common Pitfalls to Avoid

**Mistake 1: Not using path compression**
```python
# BAD - No path compression
def find(self, x):
    if self.parent[x] == x:
        return x
    return self.find(self.parent[x])

# GOOD - With path compression
def find(self, x):
    if self.parent[x] != x:
        self.parent[x] = self.find(self.parent[x])
    return self.parent[x]
```

**Mistake 2: Forgetting to find roots before union**
```python
# BAD - Directly using x and y
def union(self, x, y):
    self.parent[x] = y  # Wrong!

# GOOD - Find roots first
def union(self, x, y):
    root_x = self.find(x)
    root_y = self.find(y)
    if root_x != root_y:
        self.parent[root_x] = root_y
```

**Mistake 3: Not handling already-connected case**
```python
# Consider for cycle detection problems
def union(self, x, y):
    root_x = self.find(x)
    root_y = self.find(y)

    if root_x == root_y:
        return False  # Important: indicates cycle!

    self.parent[root_x] = root_y
    return True
```

### 4. Space Optimization Tricks

For problems with large coordinate spaces but few actual elements:
```python
# Instead of UnionFind(10^9) for large coordinates
# Use coordinate compression
def compress_coordinates(stones):
    uf = UnionFind(len(stones))
    x_map = {}
    y_map = {}

    for i, (x, y) in enumerate(stones):
        if x not in x_map:
            x_map[x] = []
        if y not in y_map:
            y_map[y] = []
        x_map[x].append(i)
        y_map[y].append(i)

    # Union stones with same x or y
    for stones_list in x_map.values():
        for i in range(1, len(stones_list)):
            uf.union(stones_list[0], stones_list[i])

    for stones_list in y_map.values():
        for i in range(1, len(stones_list)):
            uf.union(stones_list[0], stones_list[i])
```

### 5. Debugging Tips

```python
def visualize_union_find(uf):
    """Helper function to debug Union-Find state"""
    from collections import defaultdict

    print("Parent array:", uf.parent)
    print("Rank array:", uf.rank)

    # Group by root
    components = defaultdict(list)
    for i in range(len(uf.parent)):
        root = uf.find(i)
        components[root].append(i)

    print(f"Total components: {uf.components}")
    for root, members in components.items():
        print(f"Component rooted at {root}: {members}")
```

## Problem Recognition Checklist

Ask yourself these questions:

- [ ] Does the problem involve grouping or merging elements?
- [ ] Do I need to check if two elements are in the same group?
- [ ] Are connections being added dynamically?
- [ ] Do I need to count the number of distinct groups?
- [ ] Is there a concept of "equivalence" or "connectivity"?
- [ ] Do edges/connections need to be processed efficiently?
- [ ] Would DFS/BFS require repeated full traversals?
- [ ] Is the graph undirected?

If you answered **yes to 3+ questions**, Union-Find is likely the right approach.

## Practice Problems

### Beginner
1. **LeetCode 547**: Number of Provinces (Friend Circles)
2. **LeetCode 684**: Redundant Connection
3. **LeetCode 200**: Number of Islands (can use Union-Find)

### Intermediate
4. **LeetCode 721**: Accounts Merge
5. **LeetCode 990**: Satisfiability of Equality Equations
6. **LeetCode 947**: Most Stones Removed with Same Row or Column
7. **LeetCode 1319**: Number of Operations to Make Network Connected
8. **LeetCode 128**: Longest Consecutive Sequence (Union-Find approach)

### Advanced
9. **LeetCode 305**: Number of Islands II (Premium, Dynamic)
10. **LeetCode 1202**: Smallest String With Swaps
11. **LeetCode 1631**: Path With Minimum Effort
12. **LeetCode 952**: Largest Component Size by Common Factor
13. **LeetCode 765**: Couples Holding Hands

## Common Mistakes in Interviews

### 1. Confusing Find and Union
```python
# WRONG: Calling union without find
self.parent[x] = y

# RIGHT: Always find roots first
root_x = self.find(x)
root_y = self.find(y)
self.parent[root_x] = root_y
```

### 2. Forgetting Path Compression
Without path compression, find operations can degrade to O(n). Always implement it!

### 3. Not Returning False for Already-Connected
In cycle detection problems, failing to detect when two nodes are already connected misses the cycle.

### 4. Off-by-One in Size Initialization
```python
# If nodes are 1-indexed (like in many graph problems)
uf = UnionFind(n + 1)  # Not just n

# If using coordinates as indices
max_coord = max(max(x, y) for x, y in stones)
uf = UnionFind(max_coord + 1)
```

### 5. Not Considering Component Count vs Component Size
- **Component count**: Number of distinct groups
- **Component size**: Number of elements in a group

Different problems need different tracking:
```python
# For counting components
self.components = n
def union(self, x, y):
    if root_x != root_y:
        self.components -= 1

# For tracking sizes
self.size = [1] * n
def union(self, x, y):
    if root_x != root_y:
        self.size[root_y] += self.size[root_x]
```

### 6. Inefficient Component Enumeration
```python
# SLOW: O(n²) - calling find for every node multiple times
components = {}
for i in range(n):
    root = uf.find(i)
    if root not in components:
        components[root] = []
    components[root].append(i)

# BETTER: O(n) with memoization
roots_seen = {}
components = []
for i in range(n):
    root = uf.find(i)
    if root not in roots_seen:
        roots_seen[root] = len(components)
        components.append([])
    components[roots_seen[root]].append(i)
```

### 7. Forgetting to Handle Edge Cases
```python
def countComponents(n, edges):
    if n == 0:
        return 0
    if not edges:
        return n  # Each node is its own component

    uf = UnionFind(n)
    for u, v in edges:
        uf.union(u, v)
    return uf.count_components()
```

## Summary

Union-Find is a powerful data structure for managing disjoint sets with near-constant time operations. The combination of **path compression** and **union by rank** makes it extremely efficient in practice.

**Key Takeaways:**
- Use for dynamic connectivity and grouping problems
- Path compression flattens trees during find
- Union by rank keeps trees balanced
- Practical time complexity: O(α(n)) ≈ O(1)
- Prefer over DFS/BFS for connectivity queries
- Watch for cycle detection use cases

**Remember**: Union-Find excels when you need to repeatedly check connectivity or merge groups. If you need to find paths or explore graph structure, consider DFS/BFS instead.
