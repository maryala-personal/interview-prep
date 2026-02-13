# Graph Algorithms Pattern Guide

## What are Graph Algorithms?

### Explain Like I'm 5
Imagine you have a bunch of cities and roads connecting them. Graph algorithms help you answer questions like:
- "What's the shortest way to drive from City A to City B?"
- "Can I visit all cities starting from my home?"
- "Which cities can I reach if some roads are closed?"

A graph is just a collection of things (called "nodes" or "vertices") connected by relationships (called "edges"). Think of it like a connect-the-dots picture, but the dots can connect to each other in any way!

### Technical Definition
A graph is a data structure consisting of:
- **Vertices (V)**: A set of nodes/points
- **Edges (E)**: A set of connections between vertices

Graphs can be:
- **Directed**: Edges have direction (one-way streets)
- **Undirected**: Edges are bidirectional (two-way streets)
- **Weighted**: Edges have values/costs (distance, time, cost)
- **Unweighted**: All edges are equal

## Real-World Analogy

### GPS Navigation Systems
When you use Google Maps to find directions:
- **Cities/Intersections** = Nodes/Vertices
- **Roads** = Edges
- **Distance/Time** = Edge Weights
- **Finding the shortest route** = Dijkstra's Algorithm

The GPS doesn't check every possible route (that would take forever!). Instead, it uses graph algorithms to efficiently find the best path.

### Social Networks
On platforms like LinkedIn or Facebook:
- **People** = Nodes
- **Friendships/Connections** = Edges
- **Degrees of separation** = Shortest path
- **Mutual friends** = Common neighbors
- **Influence spread** = Graph traversal

### Course Prerequisites
In college:
- **Courses** = Nodes
- **Prerequisites** = Directed Edges
- **Finding what order to take classes** = Topological Sort
- **Detecting impossible requirements** = Cycle detection

## When to Use Graph Algorithms

### Clear Signals You Need Graphs:

1. **The problem mentions:**
   - Networks, connections, relationships
   - Paths, routes, journeys
   - Dependencies, prerequisites, ordering
   - Social networks, followers, friends
   - Maps, cities, roads

2. **You need to find:**
   - Shortest path between points
   - Whether a path exists
   - All reachable destinations
   - Groups/clusters of connected items
   - Ordering based on dependencies

3. **The data structure involves:**
   - Things connected to other things
   - Hierarchical relationships (but not strictly a tree)
   - Many-to-many relationships

## Core Graph Problems and Algorithms

### 1. Dijkstra's Algorithm (Shortest Path)
**Purpose**: Find the shortest path from a source to all other vertices in a weighted graph (with non-negative weights).

**When to Use**:
- GPS navigation
- Network routing
- Finding cheapest flights
- Any "minimize cost" problem on a graph

### 2. Topological Sort
**Purpose**: Order vertices in a directed acyclic graph (DAG) such that for every edge u→v, u comes before v.

**When to Use**:
- Course scheduling
- Build systems (compilation order)
- Task dependencies
- Recipe steps

### 3. Strongly Connected Components (SCC)
**Purpose**: Find groups of vertices where every vertex can reach every other vertex in the group.

**When to Use**:
- Social network analysis
- Finding circular dependencies
- Web page clustering
- Compiler optimization

### 4. Breadth-First Search (BFS)
**Purpose**: Explore graph level by level, finding shortest path in unweighted graphs.

**When to Use**:
- Shortest path in unweighted graph
- Level-order exploration
- Finding connected components

### 5. Depth-First Search (DFS)
**Purpose**: Explore graph by going deep before going wide.

**When to Use**:
- Cycle detection
- Path finding
- Topological sorting
- Connected components

## The Problems: Detailed Solutions

### Problem 1: Dijkstra's Shortest Path

#### Brute Force Approach
```python
def dijkstra_brute_force(graph, start):
    """
    Brute force: Check all possible paths
    This would explore every possible route - extremely inefficient!

    Time: O(V!) - factorial time, practically impossible for large graphs
    Space: O(V)
    """
    n = len(graph)
    # distances[i] = shortest distance from start to i
    distances = [float('inf')] * n
    distances[start] = 0
    visited = [False] * n

    # Visit each vertex
    for _ in range(n):
        # Find minimum distance vertex among unvisited (O(V))
        min_dist = float('inf')
        min_vertex = -1

        for v in range(n):
            if not visited[v] and distances[v] < min_dist:
                min_dist = distances[v]
                min_vertex = v

        if min_vertex == -1:
            break

        visited[min_vertex] = True

        # Update distances to neighbors
        for neighbor, weight in graph[min_vertex]:
            if not visited[neighbor]:
                new_dist = distances[min_vertex] + weight
                distances[neighbor] = min(distances[neighbor], new_dist)

    return distances
```

**Why This is Slow**: We linearly search for the minimum distance vertex every time (O(V) operation done V times = O(V²)).

#### Optimized Solution: Dijkstra with Min-Heap
```python
import heapq
from collections import defaultdict

def dijkstra_optimized(graph, start, n):
    """
    Optimized Dijkstra using a min-heap (priority queue)

    The key insight: Use a heap to always get the next closest unvisited vertex in O(log V) time

    Time: O((V + E) log V) where V = vertices, E = edges
    Space: O(V + E)

    Args:
        graph: adjacency list {vertex: [(neighbor, weight), ...]}
        start: starting vertex
        n: number of vertices
    """
    # distances[i] = shortest distance from start to i
    distances = [float('inf')] * n
    distances[start] = 0

    # Min-heap: (distance, vertex)
    # We want to always process the closest unvisited vertex
    min_heap = [(0, start)]
    visited = set()

    while min_heap:
        # Get vertex with minimum distance (O(log V))
        current_dist, current_vertex = heapq.heappop(min_heap)

        # Skip if already visited
        if current_vertex in visited:
            continue

        visited.add(current_vertex)

        # If we popped a longer path, skip it
        if current_dist > distances[current_vertex]:
            continue

        # Check all neighbors
        if current_vertex in graph:
            for neighbor, weight in graph[current_vertex]:
                # Calculate new distance through current vertex
                new_distance = distances[current_vertex] + weight

                # If we found a shorter path, update it
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    heapq.heappush(min_heap, (new_distance, neighbor))

    return distances

# Example usage with path reconstruction
def dijkstra_with_path(graph, start, end, n):
    """
    Dijkstra that also returns the actual path, not just distance
    """
    distances = [float('inf')] * n
    distances[start] = 0
    parent = [-1] * n  # Track the path

    min_heap = [(0, start)]
    visited = set()

    while min_heap:
        current_dist, current_vertex = heapq.heappop(min_heap)

        if current_vertex in visited:
            continue

        visited.add(current_vertex)

        # Early termination if we reached the target
        if current_vertex == end:
            break

        if current_vertex in graph:
            for neighbor, weight in graph[current_vertex]:
                new_distance = distances[current_vertex] + weight

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    parent[neighbor] = current_vertex
                    heapq.heappush(min_heap, (new_distance, neighbor))

    # Reconstruct path
    path = []
    current = end
    while current != -1:
        path.append(current)
        current = parent[current]
    path.reverse()

    return distances[end], path if path[0] == start else []

# Example
graph = {
    0: [(1, 4), (2, 1)],
    1: [(3, 1)],
    2: [(1, 2), (3, 5)],
    3: []
}
print(dijkstra_optimized(graph, 0, 4))  # [0, 3, 1, 4]
print(dijkstra_with_path(graph, 0, 3, 4))  # (4, [0, 2, 1, 3])
```

**Time Complexity**: O((V + E) log V)
- Each vertex is added to heap once: O(V log V)
- Each edge causes at most one heap operation: O(E log V)

**Space Complexity**: O(V + E)
- Graph storage: O(V + E)
- Distances array: O(V)
- Heap: O(V) in worst case

---

### Problem 2: Topological Sort

#### Brute Force Approach
```python
def topological_sort_brute(graph, n):
    """
    Brute force: Try all permutations and check if valid

    Time: O(V! × E) - factorial time, completely impractical
    Space: O(V)
    """
    from itertools import permutations

    # Try all possible orderings
    for perm in permutations(range(n)):
        valid = True
        # Check if this ordering respects all edges
        position = {node: i for i, node in enumerate(perm)}

        for node in graph:
            for neighbor in graph[node]:
                if position[node] >= position[neighbor]:
                    valid = False
                    break
            if not valid:
                break

        if valid:
            return list(perm)

    return []  # No valid ordering (cycle exists)
```

#### Optimized Solution 1: Kahn's Algorithm (BFS-based)
```python
from collections import deque, defaultdict

def topological_sort_kahn(graph, n):
    """
    Kahn's Algorithm: Remove vertices with no incoming edges iteratively

    Intuition:
    - Start with nodes that have no prerequisites
    - Remove them and their outgoing edges
    - Repeat with newly freed nodes

    Time: O(V + E)
    Space: O(V + E)

    Args:
        graph: adjacency list {vertex: [neighbors]}
        n: number of vertices
    """
    # Calculate in-degree (number of incoming edges) for each vertex
    in_degree = [0] * n

    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] += 1

    # Start with all nodes that have no incoming edges
    queue = deque([i for i in range(n) if in_degree[i] == 0])
    result = []

    while queue:
        # Take a node with no prerequisites
        current = queue.popleft()
        result.append(current)

        # Remove this node's outgoing edges
        if current in graph:
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                # If neighbor now has no incoming edges, add to queue
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

    # If we processed all nodes, we have a valid ordering
    # Otherwise, there's a cycle
    return result if len(result) == n else []

# Example: Course Schedule
def can_finish_courses(num_courses, prerequisites):
    """
    LeetCode 207: Course Schedule

    Example: numCourses = 4, prerequisites = [[1,0],[2,0],[3,1],[3,2]]
    Meaning: To take course 1, you must first take course 0
    """
    # Build graph
    graph = defaultdict(list)
    for course, prereq in prerequisites:
        graph[prereq].append(course)  # prereq -> course

    result = topological_sort_kahn(graph, num_courses)
    return len(result) == num_courses  # True if no cycle

print(can_finish_courses(4, [[1,0],[2,0],[3,1],[3,2]]))  # True
print(can_finish_courses(2, [[1,0],[0,1]]))  # False (cycle)
```

#### Optimized Solution 2: DFS-based Topological Sort
```python
def topological_sort_dfs(graph, n):
    """
    DFS-based topological sort

    Intuition:
    - Use DFS to explore as deep as possible
    - Add nodes to result in POST-order (after visiting all children)
    - Reverse the result

    Time: O(V + E)
    Space: O(V)
    """
    WHITE, GRAY, BLACK = 0, 1, 2  # Unvisited, Visiting, Visited
    color = [WHITE] * n
    result = []
    has_cycle = False

    def dfs(node):
        nonlocal has_cycle

        if color[node] == GRAY:  # Back edge = cycle
            has_cycle = True
            return

        if color[node] == BLACK:  # Already processed
            return

        color[node] = GRAY  # Mark as being processed

        if node in graph:
            for neighbor in graph[node]:
                dfs(neighbor)
                if has_cycle:
                    return

        color[node] = BLACK  # Mark as completely processed
        result.append(node)  # Add in post-order

    # Try DFS from each unvisited node
    for i in range(n):
        if color[i] == WHITE:
            dfs(i)
            if has_cycle:
                return []

    return result[::-1]  # Reverse to get topological order

# Example
graph = {0: [1, 2], 1: [3], 2: [3]}
print(topological_sort_dfs(graph, 4))  # [0, 2, 1, 3] or [0, 1, 2, 3]
```

**Time Complexity**: O(V + E)
- We visit each vertex once: O(V)
- We examine each edge once: O(E)

**Space Complexity**: O(V + E)
- Graph storage: O(V + E)
- In-degree array/color array: O(V)
- Queue/recursion stack: O(V)

---

### Problem 3: Strongly Connected Components (Kosaraju's Algorithm)

#### Brute Force Approach
```python
def scc_brute_force(graph, n):
    """
    Brute force: For each pair of vertices, check if they can reach each other

    Time: O(V² × (V + E)) - run BFS/DFS for each pair
    Space: O(V)
    """
    def can_reach(start, end):
        """Check if end is reachable from start using BFS"""
        visited = set([start])
        queue = deque([start])

        while queue:
            node = queue.popleft()
            if node == end:
                return True

            if node in graph:
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
        return False

    # Group nodes that can reach each other
    components = []
    assigned = [False] * n

    for i in range(n):
        if assigned[i]:
            continue

        component = [i]
        assigned[i] = True

        for j in range(i + 1, n):
            if not assigned[j]:
                # Check if i and j can reach each other
                if can_reach(i, j) and can_reach(j, i):
                    component.append(j)
                    assigned[j] = True

        components.append(component)

    return components
```

#### Optimized Solution: Kosaraju's Algorithm
```python
def strongly_connected_components(graph, n):
    """
    Kosaraju's Algorithm for finding Strongly Connected Components

    Intuition:
    1. Do DFS on original graph, track finish times
    2. Create reversed graph (flip all edges)
    3. Do DFS on reversed graph in decreasing finish time order
    4. Each DFS tree in step 3 is a strongly connected component

    Why this works:
    - If we finish vertex u before v in first DFS, there's no path v -> u
    - In reversed graph, if there was path u -> v, now it's v -> u
    - Starting from highest finish time ensures we find complete SCCs

    Time: O(V + E)
    Space: O(V + E)
    """
    # Step 1: First DFS to get finish times
    visited = [False] * n
    finish_stack = []

    def dfs1(node):
        visited[node] = True
        if node in graph:
            for neighbor in graph[node]:
                if not visited[neighbor]:
                    dfs1(neighbor)
        finish_stack.append(node)  # Add to stack in post-order

    for i in range(n):
        if not visited[i]:
            dfs1(i)

    # Step 2: Create reversed graph
    reversed_graph = defaultdict(list)
    for node in graph:
        for neighbor in graph[node]:
            reversed_graph[neighbor].append(node)

    # Step 3: DFS on reversed graph in decreasing finish time
    visited = [False] * n
    components = []

    def dfs2(node, component):
        visited[node] = True
        component.append(node)
        if node in reversed_graph:
            for neighbor in reversed_graph[node]:
                if not visited[neighbor]:
                    dfs2(neighbor, component)

    # Process in reverse finish order
    while finish_stack:
        node = finish_stack.pop()
        if not visited[node]:
            component = []
            dfs2(node, component)
            components.append(component)

    return components

# Example: Social network where edges are "follows"
graph = {
    0: [1],
    1: [2],
    2: [0, 3],
    3: [4],
    4: [5],
    5: [3]
}
print(strongly_connected_components(graph, 6))
# [[0, 2, 1], [3, 5, 4]] - Two groups where everyone follows everyone in the group
```

**Time Complexity**: O(V + E)
- First DFS: O(V + E)
- Creating reversed graph: O(V + E)
- Second DFS: O(V + E)

**Space Complexity**: O(V + E)
- Original and reversed graphs: O(V + E)
- Recursion stack: O(V)

---

### Problem 4: Union-Find (Disjoint Set Union)

```python
class UnionFind:
    """
    Union-Find data structure for efficiently managing disjoint sets

    Used for:
    - Detecting cycles in undirected graphs
    - Finding connected components
    - Kruskal's MST algorithm

    Time: O(α(n)) per operation, where α is inverse Ackermann (practically O(1))
    Space: O(n)
    """

    def __init__(self, n):
        self.parent = list(range(n))  # Each node is its own parent initially
        self.rank = [0] * n  # Track tree height for union by rank
        self.components = n  # Number of disjoint sets

    def find(self, x):
        """
        Find the root of x with path compression

        Path compression: Make every node point directly to root
        This flattens the tree structure
        """
        if self.parent[x] != x:
            # Recursively find root and compress path
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        """
        Union two sets containing x and y

        Union by rank: Attach smaller tree under larger tree
        This keeps trees balanced
        """
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False  # Already in same set

        # Union by rank
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1

        self.components -= 1
        return True

    def connected(self, x, y):
        """Check if x and y are in the same set"""
        return self.find(x) == self.find(y)

# Example: Detect cycle in undirected graph
def has_cycle_undirected(n, edges):
    """
    edges: [(u, v), ...] undirected edges
    """
    uf = UnionFind(n)

    for u, v in edges:
        # If u and v already connected, adding this edge creates a cycle
        if uf.connected(u, v):
            return True
        uf.union(u, v)

    return False

print(has_cycle_undirected(3, [(0, 1), (1, 2)]))  # False
print(has_cycle_undirected(3, [(0, 1), (1, 2), (2, 0)]))  # True
```

---

### Problem 5: Minimum Spanning Tree (Kruskal's Algorithm)

```python
def kruskal_mst(n, edges):
    """
    Kruskal's Algorithm: Find Minimum Spanning Tree

    A spanning tree connects all vertices with minimum total edge weight

    Algorithm:
    1. Sort edges by weight
    2. Add edges one by one if they don't create a cycle (use Union-Find)
    3. Stop when we have V-1 edges

    Time: O(E log E) - dominated by sorting
    Space: O(V)

    Args:
        n: number of vertices
        edges: [(u, v, weight), ...]
    """
    # Sort edges by weight
    edges.sort(key=lambda x: x[2])

    uf = UnionFind(n)
    mst_edges = []
    total_weight = 0

    for u, v, weight in edges:
        # Add edge if it doesn't create a cycle
        if uf.union(u, v):
            mst_edges.append((u, v, weight))
            total_weight += weight

            # MST has exactly V-1 edges
            if len(mst_edges) == n - 1:
                break

    return mst_edges, total_weight

# Example: Connect cities with minimum cable length
edges = [
    (0, 1, 4), (0, 2, 3),
    (1, 2, 1), (1, 3, 2),
    (2, 3, 4)
]
mst, cost = kruskal_mst(4, edges)
print(f"MST edges: {mst}, Total cost: {cost}")
# MST edges: [(1, 2, 1), (1, 3, 2), (0, 2, 3)], Total cost: 6
```

---

## Time & Space Complexity Summary

| Algorithm | Time Complexity | Space Complexity | Use Case |
|-----------|----------------|------------------|----------|
| Dijkstra (Array) | O(V²) | O(V) | Dense graphs, small V |
| Dijkstra (Heap) | O((V+E) log V) | O(V+E) | Sparse graphs, large V |
| Bellman-Ford | O(VE) | O(V) | Negative weights |
| Topological Sort (Kahn) | O(V+E) | O(V+E) | BFS-based ordering |
| Topological Sort (DFS) | O(V+E) | O(V) | DFS-based ordering |
| Kosaraju's SCC | O(V+E) | O(V+E) | Strongly connected components |
| Union-Find | O(α(n)) | O(n) | Disjoint sets, cycle detection |
| Kruskal's MST | O(E log E) | O(V) | Minimum spanning tree |
| BFS | O(V+E) | O(V) | Shortest path (unweighted) |
| DFS | O(V+E) | O(V) | Path finding, cycles |

---

## Variations and Extensions

### 1. Graph Representations

#### Adjacency Matrix
```python
# Space: O(V²) - wasteful for sparse graphs
# Access time: O(1) - fast to check if edge exists
# Good for: Dense graphs, need quick edge lookup

graph_matrix = [
    [0, 4, 3, 0],  # Node 0's edges
    [0, 0, 0, 2],  # Node 1's edges
    [0, 1, 0, 4],  # Node 2's edges
    [0, 0, 0, 0]   # Node 3's edges
]
# graph_matrix[i][j] = weight of edge i->j, or 0 if no edge
```

#### Adjacency List
```python
# Space: O(V + E) - efficient for sparse graphs
# Access time: O(degree) - need to iterate through neighbors
# Good for: Most real-world graphs (sparse)

graph_list = {
    0: [(1, 4), (2, 3)],  # Node 0 connects to 1 (weight 4) and 2 (weight 3)
    1: [(3, 2)],
    2: [(1, 1), (3, 4)],
    3: []
}
```

#### Edge List
```python
# Space: O(E)
# Good for: Kruskal's MST, when you process edges directly

edges = [
    (0, 1, 4),  # Edge from 0 to 1 with weight 4
    (0, 2, 3),
    (1, 3, 2),
    (2, 1, 1),
    (2, 3, 4)
]
```

### 2. Weighted vs Unweighted Graphs

```python
# Unweighted: Use BFS for shortest path
def shortest_path_unweighted(graph, start, end, n):
    """O(V + E) - BFS finds shortest path in unweighted graph"""
    queue = deque([(start, 0)])  # (node, distance)
    visited = {start}

    while queue:
        node, dist = queue.popleft()
        if node == end:
            return dist

        if node in graph:
            for neighbor in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))

    return -1  # Not reachable

# Weighted: Use Dijkstra (non-negative) or Bellman-Ford (negative weights)
```

### 3. Handling Negative Weights: Bellman-Ford

```python
def bellman_ford(graph, start, n):
    """
    Bellman-Ford: Handles negative weight edges
    Also detects negative cycles

    Time: O(VE) - slower than Dijkstra but handles negative weights
    Space: O(V)
    """
    distances = [float('inf')] * n
    distances[start] = 0

    # Relax all edges V-1 times
    for _ in range(n - 1):
        for u in graph:
            for v, weight in graph[u]:
                if distances[u] != float('inf'):
                    distances[v] = min(distances[v], distances[u] + weight)

    # Check for negative cycles
    for u in graph:
        for v, weight in graph[u]:
            if distances[u] != float('inf'):
                if distances[u] + weight < distances[v]:
                    return None  # Negative cycle detected

    return distances

# Example with negative weights
graph = {
    0: [(1, 4), (2, 5)],
    1: [(2, -3)],  # Negative weight
    2: []
}
print(bellman_ford(graph, 0, 3))  # [0, 4, 1]
```

### 4. Bidirectional Search

```python
def bidirectional_search(graph, start, end, n):
    """
    Search from both start and end simultaneously
    Meets in the middle - much faster for large graphs

    Time: O(b^(d/2)) vs O(b^d) for regular BFS
    where b = branching factor, d = distance
    """
    if start == end:
        return [start]

    # Forward search from start
    forward_queue = deque([start])
    forward_visited = {start: None}

    # Backward search from end
    backward_queue = deque([end])
    backward_visited = {end: None}

    while forward_queue and backward_queue:
        # Expand forward
        current = forward_queue.popleft()
        if current in backward_visited:
            return reconstruct_path(current, forward_visited, backward_visited)

        if current in graph:
            for neighbor in graph[current]:
                if neighbor not in forward_visited:
                    forward_visited[neighbor] = current
                    forward_queue.append(neighbor)

        # Expand backward (need reversed graph)
        current = backward_queue.popleft()
        if current in forward_visited:
            return reconstruct_path(current, forward_visited, backward_visited)

    return []  # No path found

def reconstruct_path(meeting_point, forward_visited, backward_visited):
    """Reconstruct path from both searches"""
    path = []

    # Forward path
    node = meeting_point
    while node is not None:
        path.append(node)
        node = forward_visited[node]
    path.reverse()

    # Backward path
    node = backward_visited[meeting_point]
    while node is not None:
        path.append(node)
        node = backward_visited[node]

    return path
```

---

## Pro Tips for Senior Engineers

### 1. Choosing the Right Algorithm

```
Shortest Path:
├── Unweighted graph → BFS
├── Non-negative weights → Dijkstra
├── Negative weights → Bellman-Ford
├── All pairs → Floyd-Warshall
└── Large graph, specific target → A* (with heuristic)

Cycle Detection:
├── Undirected → Union-Find or DFS
└── Directed → DFS with coloring (WHITE/GRAY/BLACK)

Ordering:
├── Linear ordering with dependencies → Topological Sort
└── Must visit all vertices → Hamiltonian Path (NP-hard)

Connected Components:
├── Undirected → DFS/BFS/Union-Find
├── Directed → Kosaraju's or Tarjan's
└── Need online updates → Union-Find
```

### 2. Graph Construction is Half the Battle

```python
# Often the hardest part is recognizing and building the graph

# Example: Word Ladder (LC 127)
# Transform "hit" -> "cog" changing one letter at a time
# This is a shortest path problem!

def build_word_graph(word_list):
    """
    Each word is a node
    Edge exists if words differ by one character
    """
    graph = defaultdict(list)

    # Optimization: Use intermediate states
    # "hit" -> "*it", "h*t", "hi*"
    for word in word_list:
        for i in range(len(word)):
            pattern = word[:i] + '*' + word[i+1:]
            graph[pattern].append(word)

    return graph

# Example: Task Scheduling with cooldown
# This becomes a graph coloring problem!
```

### 3. Edge Cases to Watch

```python
# 1. Disconnected graphs
def handle_disconnected(graph, n):
    """Don't assume graph is connected!"""
    visited = set()
    components = []

    for i in range(n):
        if i not in visited:
            component = []
            dfs(graph, i, visited, component)
            components.append(component)

    return components

# 2. Self-loops and parallel edges
graph = {
    0: [(0, 1), (1, 5), (1, 3)]  # Self-loop and parallel edges
}

# 3. Negative cycles (make Dijkstra fail)
# Always use Bellman-Ford if negative weights possible

# 4. Empty graph or single node
if n == 0:
    return []
if n == 1:
    return [0]

# 5. Unreachable target
if target not in visited:
    return -1  # or float('inf')
```

### 4. Space Optimizations

```python
# Implicit graphs - don't build the whole graph in memory
def bfs_implicit(start, is_goal, get_neighbors):
    """
    For huge graphs (like chess positions), generate neighbors on-the-fly
    """
    queue = deque([start])
    visited = {start}

    while queue:
        current = queue.popleft()
        if is_goal(current):
            return current

        for neighbor in get_neighbors(current):  # Generate on-demand
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return None

# Example: Knight moves on infinite chessboard
def get_knight_moves(pos):
    x, y = pos
    moves = [(2,1), (2,-1), (-2,1), (-2,-1),
             (1,2), (1,-2), (-1,2), (-1,-2)]
    return [(x+dx, y+dy) for dx, dy in moves]
```

### 5. Performance Optimizations

```python
# 1. Early termination in Dijkstra
if current_vertex == target:
    break  # Found shortest path to target

# 2. Bidirectional search for specific target
# Search from both ends, meet in middle

# 3. Use deque for BFS (not list)
queue = deque()  # O(1) popleft
# NOT: queue = [] with queue.pop(0)  # O(n) pop

# 4. Set for O(1) membership, not list
visited = set()  # O(1) lookup
# NOT: visited = []  # O(n) lookup

# 5. Default dict for cleaner code
from collections import defaultdict
graph = defaultdict(list)  # No KeyError
# NOT: graph = {}  # Need to check if key exists
```

---

## Problem Recognition Patterns

### How to Spot Graph Problems

#### Pattern 1: "Can you reach...?"
```
Keywords: path, route, journey, traverse, visit
Examples:
- "Can you travel from city A to city B?"
- "Is there a path from start to end?"
- "Can you visit all nodes?"

Solution: BFS/DFS
```

#### Pattern 2: "What's the shortest/cheapest...?"
```
Keywords: shortest, minimum, cheapest, fastest, optimal
Examples:
- "Shortest path from A to B"
- "Minimum cost to connect all cities"
- "Fewest moves to reach target"

Solution:
- Unweighted: BFS
- Weighted: Dijkstra or Bellman-Ford
- Connect all: MST (Kruskal/Prim)
```

#### Pattern 3: "In what order...?"
```
Keywords: order, sequence, dependencies, prerequisites
Examples:
- "What order to take courses?"
- "Task scheduling with dependencies"
- "Build order for projects"

Solution: Topological Sort
```

#### Pattern 4: "Are there groups/clusters...?"
```
Keywords: groups, components, clusters, islands, regions
Examples:
- "How many islands?" (connected components)
- "Find friend circles" (connected components)
- "Number of provinces" (connected components)

Solution:
- Undirected: DFS/BFS/Union-Find
- Directed: Kosaraju's/Tarjan's
```

#### Pattern 5: "Is there a cycle...?"
```
Keywords: circular, loop, cycle, deadlock
Examples:
- "Can you finish all courses?" (cycle detection)
- "Is there a circular dependency?"
- "Detect deadlock"

Solution:
- Undirected: Union-Find or DFS
- Directed: DFS with coloring
```

---

## Practice Problems (Ordered by Difficulty)

### Beginner Level
1. **Number of Islands** (LeetCode 200)
   - Pattern: Connected components
   - Approach: DFS/BFS on grid
   - Key: Treat grid as graph

2. **Clone Graph** (LeetCode 133)
   - Pattern: Graph traversal
   - Approach: DFS/BFS with hashmap
   - Key: Handle cycles with visited map

3. **All Paths From Source to Target** (LeetCode 797)
   - Pattern: Path finding in DAG
   - Approach: DFS backtracking
   - Key: No need for visited set (DAG)

### Intermediate Level
4. **Course Schedule** (LeetCode 207)
   - Pattern: Cycle detection in directed graph
   - Approach: Topological sort (Kahn's or DFS)
   - Key: If topo sort completes, no cycle

5. **Course Schedule II** (LeetCode 210)
   - Pattern: Topological ordering
   - Approach: Kahn's algorithm or DFS
   - Key: Return the actual ordering

6. **Network Delay Time** (LeetCode 743)
   - Pattern: Single-source shortest path
   - Approach: Dijkstra with heap
   - Key: Return max distance (time for all nodes)

7. **Cheapest Flights Within K Stops** (LeetCode 787)
   - Pattern: Constrained shortest path
   - Approach: Modified Dijkstra or BFS
   - Key: Track number of stops

### Advanced Level
8. **Word Ladder** (LeetCode 127)
   - Pattern: Shortest path in implicit graph
   - Approach: BFS with pattern matching
   - Key: Build graph using wildcard patterns

9. **Redundant Connection** (LeetCode 684)
   - Pattern: Cycle detection in undirected graph
   - Approach: Union-Find
   - Key: Find edge that completes a cycle

10. **Critical Connections in a Network** (LeetCode 1192)
    - Pattern: Finding bridges (cut edges)
    - Approach: Tarjan's algorithm (DFS with timestamps)
    - Key: Edge is bridge if no back edge bypasses it

11. **Minimum Height Trees** (LeetCode 310)
    - Pattern: Finding tree centers
    - Approach: Topological sort-like peeling
    - Key: Peel leaf nodes layer by layer

12. **Alien Dictionary** (LeetCode 269) - Premium
    - Pattern: Topological sort with partial ordering
    - Approach: Build graph from character ordering
    - Key: Edge cases (cycles, invalid input)

---

## Common Mistakes to Avoid

### 1. Forgetting to Handle Disconnected Graphs
```python
# WRONG - only processes one component
visited = set()
dfs(0, visited)

# CORRECT - process all components
visited = set()
for i in range(n):
    if i not in visited:
        dfs(i, visited)
```

### 2. Modifying Graph While Iterating
```python
# WRONG - modifying during iteration
for node in graph:
    for neighbor in graph[node]:
        graph[neighbor].remove(node)  # Error!

# CORRECT - collect changes first
to_remove = []
for node in graph:
    for neighbor in graph[node]:
        to_remove.append((neighbor, node))

for neighbor, node in to_remove:
    graph[neighbor].remove(node)
```

### 3. Using Wrong Data Structure for Queue
```python
# WRONG - O(n) for pop(0)
queue = []
queue.append(1)
node = queue.pop(0)  # Slow!

# CORRECT - O(1) for popleft()
from collections import deque
queue = deque()
queue.append(1)
node = queue.popleft()  # Fast!
```

### 4. Not Checking for Negative Weights
```python
# WRONG - Dijkstra with negative weights
# Will give incorrect results!

# CORRECT - Check edge weights
has_negative = any(weight < 0 for u in graph for v, weight in graph[u])
if has_negative:
    result = bellman_ford(graph, start, n)
else:
    result = dijkstra(graph, start, n)
```

### 5. Forgetting to Track Path in Dijkstra
```python
# Common mistake: Only storing distances
distances = [float('inf')] * n

# Better: Also store parent to reconstruct path
distances = [float('inf')] * n
parent = [-1] * n

# When updating distance:
if new_dist < distances[neighbor]:
    distances[neighbor] = new_dist
    parent[neighbor] = current  # Track the path!
```

### 6. Incorrect Cycle Detection in Directed Graphs
```python
# WRONG - Using simple visited set (works for undirected only)
def has_cycle_wrong(graph, node, visited):
    visited.add(node)
    for neighbor in graph[node]:
        if neighbor in visited:
            return True  # Wrong! Might be ancestor, not cycle
        if has_cycle_wrong(graph, neighbor, visited):
            return True
    return False

# CORRECT - Use recursion stack or colors
def has_cycle_correct(graph, node, visited, rec_stack):
    visited.add(node)
    rec_stack.add(node)

    for neighbor in graph[node]:
        if neighbor not in visited:
            if has_cycle_correct(graph, neighbor, visited, rec_stack):
                return True
        elif neighbor in rec_stack:  # Back edge to ancestor
            return True

    rec_stack.remove(node)  # Remove from recursion stack
    return False
```

### 7. Off-by-One in Graph Size
```python
# WRONG - Graph has n nodes (0 to n-1), but using n as node
graph = defaultdict(list)
for i in range(n):  # i goes 0 to n-1
    graph[i]  # OK
graph[n]  # WRONG! Node n doesn't exist

# CORRECT - Be clear about node numbering
# Nodes are 0-indexed: 0, 1, 2, ..., n-1
```

### 8. Not Handling Self-Loops
```python
# WRONG - Assumes no self-loops
for node in graph:
    for neighbor in graph[node]:
        # Process edge node -> neighbor

# CORRECT - Check for self-loops if they matter
for node in graph:
    for neighbor in graph[node]:
        if neighbor == node:
            continue  # Skip self-loop
        # Process edge node -> neighbor
```

### 9. Infinite Loop in BFS/DFS Without Visited Set
```python
# WRONG - No visited tracking with cycles
def bfs_wrong(start):
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            queue.append(neighbor)  # Infinite loop if cycle!

# CORRECT - Always track visited
def bfs_correct(start):
    queue = deque([start])
    visited = {start}
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

### 10. Confusing Directed vs Undirected
```python
# For undirected graph, add edge in BOTH directions
def add_undirected_edge(graph, u, v, weight):
    graph[u].append((v, weight))
    graph[v].append((u, weight))  # Don't forget this!

# For directed graph, add edge in ONE direction
def add_directed_edge(graph, u, v, weight):
    graph[u].append((v, weight))
```

---

## Visual Debugging Tips

```python
def visualize_graph(graph, n):
    """Print graph in readable format"""
    print("Graph Structure:")
    for node in range(n):
        neighbors = graph.get(node, [])
        print(f"  {node} -> {neighbors}")

def print_distances(distances, labels=None):
    """Print distances array nicely"""
    if labels is None:
        labels = range(len(distances))

    print("Distances:")
    for label, dist in zip(labels, distances):
        dist_str = str(dist) if dist != float('inf') else '∞'
        print(f"  {label}: {dist_str}")

def trace_path(parent, start, end):
    """Reconstruct and print path"""
    path = []
    current = end
    while current != -1:
        path.append(current)
        current = parent[current]

    path.reverse()
    if path[0] == start:
        print(f"Path: {' -> '.join(map(str, path))}")
    else:
        print("No path exists")
```

---

## Final Checklist for Interviews

Before coding:
- [ ] Is this a graph problem? (nodes and edges?)
- [ ] Directed or undirected?
- [ ] Weighted or unweighted?
- [ ] Can there be cycles?
- [ ] Can there be negative weights?
- [ ] Is the graph connected or disconnected?
- [ ] How many nodes/edges? (Choose algorithm based on density)

While coding:
- [ ] Using appropriate data structure (deque for BFS, set for visited)
- [ ] Handling disconnected components
- [ ] Checking for cycles if directed
- [ ] Early termination when target found
- [ ] Edge cases (empty graph, single node, unreachable nodes)

After coding:
- [ ] Test with small example
- [ ] Test with disconnected graph
- [ ] Test with cycles
- [ ] Analyze time and space complexity
- [ ] Can you optimize further?

---

**Remember**: Graph problems look intimidating but follow clear patterns. Master BFS, DFS, and the core algorithms (Dijkstra, Topological Sort, Union-Find), and you'll handle 90% of interview questions. The key is recognizing which pattern fits the problem!
