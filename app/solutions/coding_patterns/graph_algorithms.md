# Graph Algorithms — Complete Interview Guide

## When to Use This Pattern

This guide covers advanced graph algorithms beyond basic BFS/DFS traversal: shortest paths, cycle detection, topological sorting, and bridge/articulation point detection.

**Signals that indicate these algorithms:**
1. The problem asks for **shortest path** with weighted edges — Dijkstra, Bellman-Ford, or BFS on a modified graph.
2. The problem has **dependencies** or **ordering constraints** — topological sort (Course Schedule).
3. The problem asks about **connectivity**, **cycles**, or **bipartiteness** — Union-Find or DFS with coloring.
4. The problem involves finding **critical edges** or **cut vertices** — Tarjan's algorithm.
5. The problem asks for a path with **constraints** (at most K stops, minimum cost) — modified Dijkstra or Bellman-Ford.
6. The problem involves an **Euler path/circuit** — Hierholzer's algorithm.

**When NOT to use these:**
- Simple traversal (reachability, connected components) — basic BFS/DFS suffices.
- Unweighted shortest path — plain BFS is optimal.
- Tree problems — specialized tree algorithms are simpler.

---

## Core Mechanics

### Shortest Path Algorithms Overview

```
Algorithm       | Graph Type           | Time           | Negative Weights?
----------------|----------------------|----------------|------------------
BFS             | Unweighted           | O(V + E)       | N/A
Dijkstra        | Non-negative weights | O((V+E) log V) | No
Bellman-Ford    | Any weights          | O(V * E)       | Yes (detects neg cycles)
Floyd-Warshall  | All pairs            | O(V^3)         | Yes
0-1 BFS         | Weights 0 or 1       | O(V + E)       | No
```

### Dijkstra's Algorithm

Dijkstra finds the shortest path from a single source to all other nodes in a graph with non-negative edge weights.

**Why it works**: Dijkstra maintains a set of "finalized" nodes. At each step, it selects the unfinalized node with the smallest tentative distance. Since all edge weights are non-negative, this node's distance cannot be improved by going through other unfinalized nodes (any such path would be at least as long). This is the greedy choice property.

```
Visual: Dijkstra on a small graph

    (A)---1--->(B)---2--->(D)
     |          |          ^
     4          1          |
     v          v          1
    (C)---5--->(E)---1----+

Source: A
Process: A(0) -> B(1), C(4)
         B(1) -> D(3), E(2)
         E(2) -> D(3)  (3 not better than 3, no update)
         D(3) -> done
         C(4) -> E(9) (not better than 2)

Result: A=0, B=1, E=2, D=3, C=4
```

### Dijkstra Template

```python
import heapq

def dijkstra(graph, source):
    """graph: adjacency list {node: [(neighbor, weight), ...]}"""
    dist = {node: float('inf') for node in graph}
    dist[source] = 0
    heap = [(0, source)]  # (distance, node)

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue  # stale entry, skip

        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))

    return dist
```

```go
import (
    "container/heap"
    "math"
)

type Edge struct {
    To, Weight int
}

type Item struct {
    Node, Dist int
}

type PQ []Item
func (pq PQ) Len() int            { return len(pq) }
func (pq PQ) Less(i, j int) bool  { return pq[i].Dist < pq[j].Dist }
func (pq PQ) Swap(i, j int)       { pq[i], pq[j] = pq[j], pq[i] }
func (pq *PQ) Push(x interface{}) { *pq = append(*pq, x.(Item)) }
func (pq *PQ) Pop() interface{} {
    old := *pq
    n := len(old)
    x := old[n-1]
    *pq = old[:n-1]
    return x
}

func dijkstra(graph [][]Edge, source int) []int {
    n := len(graph)
    dist := make([]int, n)
    for i := range dist {
        dist[i] = math.MaxInt32
    }
    dist[source] = 0

    pq := &PQ{{source, 0}}
    heap.Init(pq)

    for pq.Len() > 0 {
        item := heap.Pop(pq).(Item)
        u, d := item.Node, item.Dist
        if d > dist[u] {
            continue
        }
        for _, e := range graph[u] {
            if dist[u]+e.Weight < dist[e.To] {
                dist[e.To] = dist[u] + e.Weight
                heap.Push(pq, Item{e.To, dist[e.To]})
            }
        }
    }
    return dist
}
```

### Bellman-Ford Template

```python
def bellman_ford(edges, n, source):
    """edges: list of (u, v, weight). n: number of nodes."""
    dist = [float('inf')] * n
    dist[source] = 0

    # Relax all edges V-1 times
    for _ in range(n - 1):
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w

    # Check for negative weight cycles
    for u, v, w in edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            return None  # negative cycle detected

    return dist
```

### Tarjan's Bridge-Finding Template

```python
def find_bridges(n, adj):
    """Find all bridges (critical connections) in an undirected graph."""
    disc = [-1] * n
    low = [-1] * n
    bridges = []
    timer = [0]

    def dfs(u, parent):
        disc[u] = low[u] = timer[0]
        timer[0] += 1

        for v in adj[u]:
            if v == parent:
                continue
            if disc[v] == -1:  # unvisited
                dfs(v, u)
                low[u] = min(low[u], low[v])
                if low[v] > disc[u]:
                    bridges.append((u, v))
            else:
                low[u] = min(low[u], disc[v])

    for i in range(n):
        if disc[i] == -1:
            dfs(i, -1)

    return bridges
```

```go
func findBridges(n int, adj [][]int) [][2]int {
    disc := make([]int, n)
    low := make([]int, n)
    for i := range disc {
        disc[i] = -1
    }
    timer := 0
    var bridges [][2]int

    var dfs func(u, parent int)
    dfs = func(u, parent int) {
        disc[u] = timer
        low[u] = timer
        timer++

        for _, v := range adj[u] {
            if v == parent {
                continue
            }
            if disc[v] == -1 {
                dfs(v, u)
                if low[v] < low[u] {
                    low[u] = low[v]
                }
                if low[v] > disc[u] {
                    bridges = append(bridges, [2]int{u, v})
                }
            } else {
                if disc[v] < low[u] {
                    low[u] = disc[v]
                }
            }
        }
    }

    for i := 0; i < n; i++ {
        if disc[i] == -1 {
            dfs(i, -1)
        }
    }
    return bridges
}
```

### Topological Sort (Kahn's BFS) Template

```python
from collections import deque

def topological_sort(n, edges):
    """Returns topological order, or empty list if cycle exists."""
    adj = [[] for _ in range(n)]
    indegree = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indegree[v] += 1

    queue = deque(i for i in range(n) if indegree[i] == 0)
    order = []

    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)

    return order if len(order) == n else []  # empty = cycle
```

---

## Problem Walkthroughs

### Problem: Course Schedule II (LC #210) — Medium
**Companies**: Google, Amazon, Meta, Microsoft, Uber
**Why it's asked**: Classic topological sort. Tests cycle detection and ordering under constraints. A fundamental graph problem.

**Brute Force**:
```python
def find_order_brute(numCourses, prerequisites):
    """DFS-based topological sort (not really brute force, but DFS approach)."""
    adj = [[] for _ in range(numCourses)]
    for a, b in prerequisites:
        adj[b].append(a)

    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * numCourses
    order = []

    def dfs(u):
        color[u] = GRAY
        for v in adj[u]:
            if color[v] == GRAY:
                return False  # cycle
            if color[v] == WHITE and not dfs(v):
                return False
        color[u] = BLACK
        order.append(u)
        return True

    for i in range(numCourses):
        if color[i] == WHITE and not dfs(i):
            return []

    return order[::-1]
```

**Key Insight**: This is a direct application of topological sort. Build a directed graph where an edge from B to A means "B must be taken before A." Use Kahn's algorithm (BFS with in-degree tracking) or DFS post-order. If a cycle exists, no valid ordering is possible.

**Optimal Solution (Kahn's BFS)**:
```python
def find_order(numCourses, prerequisites):
    from collections import deque

    adj = [[] for _ in range(numCourses)]
    indegree = [0] * numCourses

    for a, b in prerequisites:
        adj[b].append(a)  # b -> a (take b before a)
        indegree[a] += 1

    queue = deque(i for i in range(numCourses) if indegree[i] == 0)
    order = []

    while queue:
        course = queue.popleft()
        order.append(course)
        for next_course in adj[course]:
            indegree[next_course] -= 1
            if indegree[next_course] == 0:
                queue.append(next_course)

    return order if len(order) == numCourses else []
```

**Dry Run** with `numCourses=4, prerequisites=[[1,0],[2,0],[3,1],[3,2]]`:
```
Graph: 0->1, 0->2, 1->3, 2->3
Indegree: [0, 1, 1, 2]

Queue: [0] (only course 0 has indegree 0)
Pop 0: order=[0]. Reduce indegree of 1->0, 2->0. indegree=[0,0,0,2]. Queue: [1,2]
Pop 1: order=[0,1]. Reduce 3. indegree=[0,0,0,1]. Queue: [2]
Pop 2: order=[0,1,2]. Reduce 3. indegree=[0,0,0,0]. Queue: [3]
Pop 3: order=[0,1,2,3].

len(order)==4==numCourses, so return [0,1,2,3].
```

**Edge Cases**: No prerequisites (any order), cycle exists (return []), single course, parallel courses (multiple valid orderings).

**Complexity**: O(V + E) time and space.

**Follow-up questions**: "What if there are multiple valid orderings?" — Kahn's naturally finds one; for all orderings, use backtracking. "Can you detect which courses form a cycle?" — DFS with GRAY/BLACK coloring identifies cycle members.

---

### Problem: Network Delay Time / Dijkstra (LC #743) — Medium
**Companies**: Google, Amazon, Meta, Microsoft
**Why it's asked**: Direct application of Dijkstra's algorithm. Tests whether you can implement shortest path correctly with a priority queue.

**Brute Force**:
```python
def network_delay_time_brute(times, n, k):
    """Bellman-Ford approach (not truly brute force, but simpler)."""
    dist = [float('inf')] * (n + 1)
    dist[k] = 0
    for _ in range(n - 1):
        for u, v, w in times:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    max_dist = max(dist[1:])  # skip index 0 (1-indexed)
    return max_dist if max_dist != float('inf') else -1
```

**Key Insight**: This is asking for the maximum of shortest distances from source `k` to all other nodes. Run Dijkstra from `k`, then return the maximum distance. If any node is unreachable (distance remains infinity), return -1.

**Optimal Solution**:
```python
import heapq

def network_delay_time(times, n, k):
    # Build adjacency list
    graph = [[] for _ in range(n + 1)]  # 1-indexed
    for u, v, w in times:
        graph[u].append((v, w))

    dist = [float('inf')] * (n + 1)
    dist[k] = 0
    heap = [(0, k)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))

    max_dist = max(dist[1:])
    return max_dist if max_dist != float('inf') else -1
```

**Dry Run** with `times=[[2,1,1],[2,3,1],[3,4,1]], n=4, k=2`:
```
Graph: 2->[(1,1),(3,1)], 3->[(4,1)]
dist = [inf, inf, 0, inf, inf]
heap = [(0, 2)]

Pop (0, 2): process neighbors
  (1, 1): dist[1] = 0+1 = 1, push (1, 1)
  (3, 1): dist[3] = 0+1 = 1, push (1, 3)
heap = [(1, 1), (1, 3)]

Pop (1, 1): no outgoing edges
Pop (1, 3): process neighbors
  (4, 1): dist[4] = 1+1 = 2, push (2, 4)

Pop (2, 4): no outgoing edges

dist = [inf, 1, 0, 1, 2]
max(dist[1:]) = 2
Answer: 2
```

**Edge Cases**: Single node (0), disconnected graph (-1), self-loops (should not affect shortest paths to others).

**Complexity**: O((V + E) log V) with binary heap. Space O(V + E).

**Follow-up questions**: "What if edges have negative weights?" — use Bellman-Ford. "What if you need the actual path?" — maintain a parent array.

---

### Problem: Cheapest Flights Within K Stops (LC #787) — Medium
**Companies**: Google, Amazon, Meta, Microsoft, Uber
**Why it's asked**: Tests modified Bellman-Ford or modified Dijkstra with an additional constraint (at most K stops). A very practical problem (flight routing).

**Brute Force**:
```python
def find_cheapest_price_brute(n, flights, src, dst, k):
    """BFS trying all paths up to k+1 edges."""
    from collections import defaultdict, deque
    graph = defaultdict(list)
    for u, v, w in flights:
        graph[u].append((v, w))

    min_cost = float('inf')
    queue = deque([(src, 0, 0)])  # (node, cost, stops)

    while queue:
        node, cost, stops = queue.popleft()
        if node == dst:
            min_cost = min(min_cost, cost)
            continue
        if stops > k:
            continue
        for next_node, price in graph[node]:
            if cost + price < min_cost:
                queue.append((next_node, cost + price, stops + 1))

    return min_cost if min_cost != float('inf') else -1
```

**Key Insight**: Bellman-Ford naturally handles the "at most K stops" constraint. Run at most `K + 1` relaxation rounds (K stops = K+1 edges). After round `i`, `dist[v]` is the shortest path from `src` to `v` using at most `i` edges. We need dist[dst] after K+1 rounds.

Important: use a copy of the distance array for each round to prevent cascading updates within the same round (which would correspond to using more edges than allowed).

**Optimal Solution (Modified Bellman-Ford)**:
```python
def find_cheapest_price(n, flights, src, dst, k):
    dist = [float('inf')] * n
    dist[src] = 0

    for _ in range(k + 1):  # at most k+1 edges
        prev = dist[:]  # copy to prevent cascading
        for u, v, w in flights:
            if prev[u] != float('inf') and prev[u] + w < dist[v]:
                dist[v] = prev[u] + w

    return dist[dst] if dist[dst] != float('inf') else -1
```

**Dry Run** with `n=4, flights=[[0,1,100],[1,2,100],[2,0,100],[1,3,600],[2,3,200]], src=0, dst=3, k=1`:
```
dist = [0, inf, inf, inf]

Round 1 (1 edge):
  prev = [0, inf, inf, inf]
  (0,1,100): prev[0]+100=100 < inf -> dist[1]=100
  (1,2,100): prev[1]=inf, skip
  (2,0,100): prev[2]=inf, skip
  (1,3,600): prev[1]=inf, skip
  (2,3,200): prev[2]=inf, skip
  dist = [0, 100, inf, inf]

Round 2 (2 edges, k+1=2):
  prev = [0, 100, inf, inf]
  (0,1,100): prev[0]+100=100 = dist[1], no change
  (1,2,100): prev[1]+100=200 < inf -> dist[2]=200
  (1,3,600): prev[1]+100+600... prev[1]+600=700 < inf -> dist[3]=700
  (2,3,200): prev[2]=inf, skip
  dist = [0, 100, 200, 700]

Answer: dist[3] = 700 (0->1->3 with cost 700, using 1 stop)
Note: 0->1->2->3 costs 400 but uses 2 stops, which exceeds k=1.
```

**Edge Cases**: Direct flight exists (0 stops), no path within k stops (-1), k >= n-1 (equivalent to unlimited stops).

**Complexity**: O(K * E) time, O(V) space.

**Follow-up questions**: "What if you use Dijkstra instead?" — modified Dijkstra with state (node, stops) works but is trickier to implement correctly. "What if the number of stops is unlimited?" — standard Dijkstra or Bellman-Ford.

---

### Problem: Graph Valid Tree (LC #261) — Medium
**Companies**: Google, Amazon, Meta, Microsoft
**Why it's asked**: Tests understanding of tree properties: a tree is a connected acyclic graph with exactly V-1 edges.

**Brute Force**:
```python
def valid_tree_brute(n, edges):
    """Check connectivity with BFS and acyclicity with DFS."""
    if len(edges) != n - 1:
        return False
    # Check connectivity
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    visited = set()
    queue = [0]
    visited.add(0)
    while queue:
        node = queue.pop(0)
        for neighbor in adj[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return len(visited) == n
```

**Key Insight**: A graph is a valid tree if and only if: (1) it has exactly `n - 1` edges, and (2) it is connected. With `n - 1` edges and connectivity, acyclicity is guaranteed (adding one more edge to a tree always creates a cycle). So check the edge count first (O(1)), then verify connectivity with BFS or DFS or Union-Find.

**Optimal Solution (Union-Find)**:
```python
def valid_tree(n, edges):
    if len(edges) != n - 1:
        return False

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
            return False  # cycle detected
        if rank[px] < rank[py]:
            px, py = py, px
        parent[py] = px
        if rank[px] == rank[py]:
            rank[px] += 1
        return True

    for u, v in edges:
        if not union(u, v):
            return False

    return True
```

**Dry Run** with `n=5, edges=[[0,1],[0,2],[0,3],[1,4]]`:
```
len(edges) = 4 == n-1 = 4, check passes.

union(0,1): parent[1]=0
union(0,2): parent[2]=0
union(0,3): parent[3]=0
union(1,4): find(1)->0, find(4)->4, parent[4]=0
No cycle detected.

Answer: True (it's a valid tree)
```

With `n=5, edges=[[0,1],[1,2],[2,3],[1,3],[1,4]]`:
```
len(edges) = 5 != 4, immediately return False (too many edges for a tree).
```

**Edge Cases**: Single node no edges (True), two nodes one edge (True), disconnected (False), self-loop (not valid).

**Complexity**: O(E * alpha(V)) with Union-Find (nearly O(E)). Space O(V).

**Follow-up questions**: "What if edges are added one at a time and you need to check after each addition?" — Union-Find is perfect for this incremental scenario. "What about detecting which edge creates the cycle?" — track it during union.

---

### Problem: Is Graph Bipartite? (LC #785) — Medium
**Companies**: Google, Amazon, Meta
**Why it's asked**: Tests graph coloring / 2-coloring. Bipartite testing has applications in matching problems.

**Brute Force**: The BFS/DFS coloring approach IS the standard solution. There is no simpler brute force.

**Key Insight**: A graph is bipartite if and only if it contains no odd-length cycles. Equivalently, you can 2-color the graph such that no two adjacent nodes have the same color. Use BFS or DFS to try 2-coloring: assign a color to the start node, color all neighbors the opposite color, and check for conflicts.

**Optimal Solution**:
```python
def is_bipartite(graph):
    n = len(graph)
    color = [-1] * n  # -1 = uncolored, 0 or 1 = color

    for start in range(n):
        if color[start] != -1:
            continue
        # BFS from this component
        queue = [start]
        color[start] = 0
        while queue:
            next_queue = []
            for u in queue:
                for v in graph[u]:
                    if color[v] == -1:
                        color[v] = 1 - color[u]
                        next_queue.append(v)
                    elif color[v] == color[u]:
                        return False  # same color neighbors = not bipartite
            queue = next_queue

    return True
```

**Dry Run** with `graph = [[1,3],[0,2],[1,3],[0,2]]`:
```
Adjacency: 0-1, 1-2, 2-3, 3-0 (a cycle of length 4)

Start BFS from node 0: color[0]=0
  Neighbors of 0: 1 (color 1), 3 (color 1)
  Neighbors of 1: 0 (already 0, different from 1, ok), 2 (color 0)
  Neighbors of 3: 0 (already 0, different from 1, ok), 2 (already 0, same as 3's color 1? No, 2 is color 0 and 3 is color 1, ok)

Wait, let me redo carefully:
color = [-1,-1,-1,-1]
color[0] = 0. Queue = [0]

Process 0: neighbors 1, 3
  color[1] = 1, color[3] = 1. Queue = [1, 3]

Process 1: neighbors 0, 2
  color[0] = 0, same? 0 != 1 (color[1]), ok
  color[2] = -1 -> color[2] = 0. Queue = [3, 2]

Process 3: neighbors 0, 2
  color[0] = 0, 0 != 1 (color[3]), ok
  color[2] = 0, 0 != 1 (color[3]), ok

Process 2: neighbors 1, 3
  color[1] = 1, 1 != 0 (color[2]), ok
  color[3] = 1, 1 != 0 (color[2]), ok

No conflicts! Answer: True
Coloring: {0: 0, 2: 0} and {1: 1, 3: 1}
```

**Edge Cases**: Empty graph (True), single node (True), odd cycle (False), disconnected graph (check each component).

**Complexity**: O(V + E) time and space.

**Follow-up questions**: "What if you need to find the actual two groups?" — return the color assignment. "How does this relate to matching?" — bipartite graphs have efficient maximum matching algorithms (Hopcroft-Karp).

---

### Problem: Reconstruct Itinerary (LC #332) — Hard
**Companies**: Google, Amazon, Meta
**Why it's asked**: Tests Euler path (Hierholzer's algorithm) combined with lexicographic ordering. A tricky graph problem that requires knowing this specific algorithm.

**Brute Force**:
```python
def find_itinerary_brute(tickets):
    """Backtracking: try all orderings of tickets."""
    from collections import defaultdict
    graph = defaultdict(list)
    for src, dst in tickets:
        graph[src].append(dst)
    for src in graph:
        graph[src].sort()

    route = ['JFK']

    def backtrack():
        if len(route) == len(tickets) + 1:
            return True
        src = route[-1]
        for i, dst in enumerate(graph[src]):
            if dst is not None:
                route.append(dst)
                graph[src][i] = None  # mark as used
                if backtrack():
                    return True
                route.pop()
                graph[src][i] = dst
        return False

    backtrack()
    return route
```

**Key Insight**: This is finding an Euler path (a path that uses every edge exactly once) starting from "JFK." Use Hierholzer's algorithm: greedily follow edges (in lexicographic order), and when stuck, backtrack by adding the current node to the front of the result. The key insight is that we build the itinerary in reverse: when a node has no more unused outgoing edges, it becomes the last stop in some sub-itinerary.

**Optimal Solution**:
```python
def find_itinerary(tickets):
    from collections import defaultdict

    graph = defaultdict(list)
    for src, dst in sorted(tickets, reverse=True):
        graph[src].append(dst)
    # Now each adjacency list is sorted in reverse (so we can pop from end efficiently)

    route = []

    def dfs(airport):
        while graph[airport]:
            next_airport = graph[airport].pop()
            dfs(next_airport)
        route.append(airport)

    dfs('JFK')
    return route[::-1]
```

**Dry Run** with `tickets = [["MUC","LHR"],["JFK","MUC"],["SFO","SJC"],["LHR","SFO"]]`:
```
Sorted reverse: [["SFO","SJC"],["MUC","LHR"],["LHR","SFO"],["JFK","MUC"]]
Graph: JFK->[MUC], LHR->[SFO], MUC->[LHR], SFO->[SJC]

dfs("JFK"):
  pop MUC from JFK's list
  dfs("MUC"):
    pop LHR from MUC's list
    dfs("LHR"):
      pop SFO from LHR's list
      dfs("SFO"):
        pop SJC from SFO's list
        dfs("SJC"):
          SJC has no edges -> route.append("SJC")
        route.append("SFO")
      route.append("LHR")
    route.append("MUC")
  route.append("JFK")

route = ["SJC", "SFO", "LHR", "MUC", "JFK"]
Reversed: ["JFK", "MUC", "LHR", "SFO", "SJC"]
```

**Edge Cases**: Multiple edges between same airports, all from same airport, large graphs with many branches.

**Complexity**: O(E log E) for sorting. O(E) for the DFS traversal. Space O(E).

**Follow-up questions**: "What if no Euler path exists?" — check if the graph has the Euler path property (at most one node with out_degree - in_degree = 1, at most one with in_degree - out_degree = 1). "What about Euler circuit?" — all nodes must have equal in-degree and out-degree.

---

### Problem: Swim in Rising Water (LC #778) — Hard
**Companies**: Google, Amazon
**Why it's asked**: Tests modified Dijkstra / binary search + BFS on a grid. The "bottleneck shortest path" concept.

**Brute Force**:
```python
def swim_in_water_brute(grid):
    """Binary search on time t, check if path exists with all values <= t."""
    n = len(grid)

    def can_reach(t):
        if grid[0][0] > t:
            return False
        visited = set()
        stack = [(0, 0)]
        visited.add((0, 0))
        while stack:
            r, c = stack.pop()
            if r == n - 1 and c == n - 1:
                return True
            for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                nr, nc = r + dr, c + dc
                if (0 <= nr < n and 0 <= nc < n and
                        (nr, nc) not in visited and grid[nr][nc] <= t):
                    visited.add((nr, nc))
                    stack.append((nr, nc))
        return False

    lo, hi = max(grid[0][0], grid[n-1][n-1]), n * n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if can_reach(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```
O(n^2 * log(n^2)) = O(n^2 * log n).

**Key Insight**: We want the minimum time `t` such that we can travel from (0,0) to (n-1,n-1) where the time to enter any cell is `max(t, grid[r][c])`. This is a "minimax path" problem: find the path from source to destination that minimizes the maximum edge weight. This is solved by a modified Dijkstra where the distance to a node is the maximum grid value along the best path to it.

**Optimal Solution**:
```python
import heapq

def swim_in_water(grid):
    n = len(grid)
    visited = [[False] * n for _ in range(n)]
    heap = [(grid[0][0], 0, 0)]  # (max_elevation, row, col)
    visited[0][0] = True

    while heap:
        t, r, c = heapq.heappop(heap)
        if r == n - 1 and c == n - 1:
            return t

        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and not visited[nr][nc]:
                visited[nr][nc] = True
                heapq.heappush(heap, (max(t, grid[nr][nc]), nr, nc))

    return -1  # unreachable
```

**Dry Run** with `grid = [[0,2],[1,3]]`:
```
heap = [(0, 0, 0)]
visited[0][0] = True

Pop (0, 0, 0): not destination
  (0,1): max(0,2)=2, push (2,0,1)
  (1,0): max(0,1)=1, push (1,1,0)
heap = [(1,1,0), (2,0,1)]

Pop (1, 1, 0): not destination
  (1,1): max(1,3)=3, push (3,1,1)
heap = [(2,0,1), (3,1,1)]

Pop (2, 0, 1): not destination
  (1,1): already visited? No, push (max(2,3)=3, 1, 1)
  Wait, visited[1][1] = True already from above. Skip.
heap = [(3,1,1)]

Pop (3, 1, 1): this IS destination (1,1) = (n-1, n-1)
Answer: 3
```

**Edge Cases**: 1x1 grid (return grid[0][0]), 2x2 grid, path goes through the highest value.

**Complexity**: O(n^2 * log n) for Dijkstra with heap. Space O(n^2).

**Follow-up questions**: "Can you use Union-Find?" — yes, sort all cells by value, union with neighbors, check if (0,0) and (n-1,n-1) are connected. "Binary search + BFS approach?" — also works, O(n^2 * log n).

---

### Problem: Minimum Cost to Make at Least One Valid Path in a Grid (LC #1368) — Hard
**Companies**: Google
**Why it's asked**: Tests 0-1 BFS (BFS with deque, edges have weight 0 or 1). An important shortest-path variant.

**Brute Force**: Standard Dijkstra works but is overkill for 0-1 weights.

**Key Insight**: Each cell has an arrow pointing in a direction. Following the arrow costs 0, changing direction costs 1. This creates a graph where edges have weight 0 (follow arrow) or 1 (change direction). The shortest path in a 0-1 weighted graph can be found with **0-1 BFS**: use a deque, push weight-0 edges to the front and weight-1 edges to the back. This gives O(V + E) time, better than Dijkstra's O((V+E) log V).

**Optimal Solution**:
```python
from collections import deque

def min_cost(grid):
    m, n = len(grid), len(grid[0])
    # Directions: 1=right, 2=left, 3=down, 4=up
    dirs = {1: (0, 1), 2: (0, -1), 3: (1, 0), 4: (-1, 0)}
    all_dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    dir_map = {1: (0, 1), 2: (0, -1), 3: (1, 0), 4: (-1, 0)}

    dist = [[float('inf')] * n for _ in range(m)]
    dist[0][0] = 0
    dq = deque([(0, 0, 0)])  # (cost, row, col)

    while dq:
        cost, r, c = dq.popleft()
        if cost > dist[r][c]:
            continue

        for dr, dc in all_dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n:
                # Cost is 0 if this direction matches the arrow, else 1
                arrow_dir = dir_map[grid[r][c]]
                new_cost = cost + (0 if (dr, dc) == arrow_dir else 1)

                if new_cost < dist[nr][nc]:
                    dist[nr][nc] = new_cost
                    if new_cost == cost:
                        dq.appendleft((new_cost, nr, nc))  # weight 0: front
                    else:
                        dq.append((new_cost, nr, nc))       # weight 1: back

    return dist[m - 1][n - 1]
```

**Dry Run** with `grid = [[1,1,1,1],[2,2,2,2],[1,1,1,1],[2,2,2,2]]`:
```
4x4 grid. Arrows: row 0 all right, row 1 all left, row 2 all right, row 3 all left.

Start (0,0), cost 0.
Follow arrows right: (0,0)->(0,1)->(0,2)->(0,3), all cost 0.
At (0,3), need to go down to row 1: cost 1.
(1,3): arrow points left. Follow: (1,3)->(1,2)->(1,1)->(1,0), all cost 1 (same total).
At (1,0): go down to (2,0): cost 2.
Follow right: (2,0)->(2,1)->(2,2)->(2,3), all cost 2.
At (2,3): go down to (3,3): cost 3.

Answer: 3
```

**Edge Cases**: 1x1 grid (cost 0), already pointing to destination, all arrows pointing away.

**Complexity**: O(m * n) time with 0-1 BFS. Space O(m * n).

**Follow-up questions**: "Why is 0-1 BFS faster than Dijkstra?" — Dijkstra uses a heap (log factor), 0-1 BFS uses a deque (constant time operations). "When can you use 0-1 BFS?" — only when edge weights are 0 or 1.

---

### Problem: Critical Connections in a Network (LC #1192) — Hard
**Companies**: Google, Amazon
**Why it's asked**: Direct application of Tarjan's bridge-finding algorithm. Tests understanding of DFS discovery times and low-link values.

**Brute Force**:
```python
def critical_connections_brute(n, connections):
    """Remove each edge, check if graph remains connected."""
    result = []
    for i in range(len(connections)):
        # Build graph without edge i
        adj = [[] for _ in range(n)]
        for j in range(len(connections)):
            if j == i:
                continue
            u, v = connections[j]
            adj[u].append(v)
            adj[v].append(u)
        # Check connectivity
        visited = set()
        stack = [0]
        visited.add(0)
        while stack:
            node = stack.pop()
            for nb in adj[node]:
                if nb not in visited:
                    visited.add(nb)
                    stack.append(nb)
        if len(visited) < n:
            result.append(connections[i])
    return result
```
O(E * (V + E)) time — remove each edge and check connectivity.

**Key Insight**: An edge (u, v) is a bridge if and only if there is no back edge from the subtree rooted at v (in the DFS tree) that reaches u or an ancestor of u. Tarjan's algorithm computes two values for each node: `disc[u]` (when u was first discovered) and `low[u]` (the minimum discovery time reachable from u's subtree through back edges). If `low[v] > disc[u]`, then edge (u, v) is a bridge.

**Optimal Solution**:
```python
def critical_connections(n, connections):
    adj = [[] for _ in range(n)]
    for u, v in connections:
        adj[u].append(v)
        adj[v].append(u)

    disc = [-1] * n
    low = [-1] * n
    bridges = []
    timer = [0]

    def dfs(u, parent):
        disc[u] = low[u] = timer[0]
        timer[0] += 1

        for v in adj[u]:
            if v == parent:
                continue
            if disc[v] == -1:  # unvisited
                dfs(v, u)
                low[u] = min(low[u], low[v])
                if low[v] > disc[u]:
                    bridges.append([u, v])
            else:
                # Back edge
                low[u] = min(low[u], disc[v])

    dfs(0, -1)
    return bridges
```

**Dry Run** with `n=4, connections=[[0,1],[1,2],[2,0],[1,3]]`:
```
adj: 0->[1,2], 1->[0,2,3], 2->[1,0], 3->[1]

dfs(0, -1): disc[0]=0, low[0]=0
  -> dfs(1, 0): disc[1]=1, low[1]=1
    -> dfs(2, 1): disc[2]=2, low[2]=2
      neighbor 0: disc[0]=0 (back edge), low[2]=min(2,0)=0
      return: low[1] = min(1, low[2]) = min(1, 0) = 0
      low[2]=0 > disc[1]=1? No, not a bridge.
    -> dfs(3, 1): disc[3]=3, low[3]=3
      no unvisited neighbors
      return: low[1] = min(0, low[3]) = min(0, 3) = 0
      low[3]=3 > disc[1]=1? YES -> bridge [1, 3]
  return: low[0] = min(0, low[1]) = min(0, 0) = 0

Bridges: [[1, 3]]
```

The edge [1, 3] is a bridge because removing it disconnects node 3 from the rest. The cycle 0-1-2-0 keeps those three connected even if any one edge is removed.

**Edge Cases**: No bridges (fully connected cycle), all bridges (tree), single node, two nodes one edge.

**Complexity**: O(V + E) time and space.

**Follow-up questions**: "What about articulation points (cut vertices)?" — similar algorithm, slightly different condition: for root, it is a cut vertex if it has >= 2 children in DFS tree; for others, if `low[v] >= disc[u]`. "What if edges are added/removed dynamically?" — much harder, research-level problem.

---

## Common Mistakes & Interview Tips

### Common Mistakes

1. **Using Dijkstra with negative weights.** Dijkstra assumes non-negative weights. With negative weights, it may find wrong answers. Use Bellman-Ford instead.

2. **Not handling disconnected graphs.** Many graph algorithms start from a single source. If the graph is disconnected, you need to run the algorithm from every unvisited node.

3. **Confusing directed and undirected graphs.** Cycle detection differs: undirected graphs need parent tracking (to avoid counting the edge you came from), directed graphs use the GRAY/BLACK coloring.

4. **Off-by-one in Bellman-Ford rounds.** V-1 rounds guarantee shortest paths (without negative cycles). For "at most K edges," run K rounds, not K-1.

5. **Stale entries in Dijkstra's heap.** Always check `if d > dist[u]: continue` after popping from the heap. Without this, you process nodes multiple times.

### Interview Tips

1. **Identify the graph type first.** Weighted vs unweighted, directed vs undirected, positive vs negative weights. This immediately narrows your algorithm choice.

2. **Know Dijkstra's implementation cold.** It appears in many problems, sometimes disguised (grid problems, state-space search). The template with a priority queue and stale-entry check should be memorized.

3. **Bellman-Ford for constrained shortest paths.** Whenever the problem says "at most K edges/stops," Bellman-Ford with K+1 rounds is the cleanest approach.

4. **Tarjan's algorithm is rare but high-value.** It shows up in hard Google interviews. Understand the intuition behind discovery time and low-link values.

5. **0-1 BFS is an important optimization.** When edge weights are 0 or 1, using a deque instead of a heap gives O(V + E) instead of O((V + E) log V). Mention this optimization to impress.

---

## Pattern Connections

- **Dijkstra + Grid**: Many grid problems (Swim in Rising Water, Path With Minimum Effort) are Dijkstra on an implicit grid graph. Each cell is a node, and edges connect to 4 neighbors.

- **Bellman-Ford + DP**: Bellman-Ford IS dynamic programming on graphs. The DP state is (node, number of edges used). This connection makes it natural for constrained shortest path problems.

- **Topological Sort + DP**: Many DP problems on DAGs (like longest path in a DAG) require processing nodes in topological order. Course scheduling and build systems use this pattern.

- **Union-Find vs DFS for connectivity**: Both can determine connected components. Union-Find is better for incremental edge additions. DFS is simpler for a static graph.

- **Tarjan's for SCC and bridges**: Tarjan's algorithm has two variants: one for strongly connected components (directed graphs) and one for bridges/articulation points (undirected graphs). Both use the same disc/low framework.

- **BFS/Dijkstra/0-1 BFS spectrum**: Unweighted graph -> BFS. Weights 0 and 1 -> 0-1 BFS. Non-negative weights -> Dijkstra. Any weights -> Bellman-Ford. Know which tool to reach for.
