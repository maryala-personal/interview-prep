# Topological Sort — Complete Interview Guide

## When to Use This Pattern

Topological sort produces a linear ordering of vertices in a directed acyclic graph (DAG) such that for every directed edge `u → v`, vertex `u` appears before `v` in the ordering. Use it when you need to determine a valid processing order given dependency constraints.

**Primary signals:**
- "Prerequisites" / "dependencies" — one thing must happen before another
- "Course schedule" — can you finish all courses? In what order?
- "Build order" / "compilation order" — determine a valid build sequence
- "Alien dictionary" — determine character ordering from sorted words
- "Parallel processing" — find tasks that can run concurrently (same topological level)
- The problem describes a directed graph and asks for an ordering

**Key properties of topological sort:**
1. Only possible on DAGs (directed acyclic graphs). If there is a cycle, no valid ordering exists.
2. The ordering is not unique — there can be multiple valid topological orderings.
3. Topological sort doubles as cycle detection: if you cannot produce a complete ordering, there is a cycle.

---

## Core Mechanics

### Two Approaches: Kahn's BFS vs DFS

There are two standard algorithms for topological sort. Both produce valid orderings, but they have different strengths.

#### Kahn's Algorithm (BFS-based)

**Idea:** Repeatedly remove nodes with no incoming edges (in-degree 0). These nodes have no dependencies, so they can go first.

```
Step 1: Compute in-degree for every node
Step 2: Add all nodes with in-degree 0 to a queue
Step 3: While queue is not empty:
  - Pop a node, add it to the result
  - For each neighbor, decrement its in-degree
  - If a neighbor's in-degree becomes 0, add it to the queue
Step 4: If result has all nodes → valid ordering. Otherwise → cycle exists.
```

**Visual walkthrough:**
```
Graph: 0→1, 0→2, 1→3, 2→3

In-degrees: {0:0, 1:1, 2:1, 3:2}

Queue: [0] (only node with in-degree 0)

Pop 0: result=[0]. Neighbors 1,2.
  in-degree[1] = 0 → add to queue
  in-degree[2] = 0 → add to queue
  Queue: [1, 2]

Pop 1: result=[0,1]. Neighbor 3.
  in-degree[3] = 1 → not 0 yet.
  Queue: [2]

Pop 2: result=[0,1,2]. Neighbor 3.
  in-degree[3] = 0 → add to queue.
  Queue: [3]

Pop 3: result=[0,1,2,3].

All 4 nodes in result → valid topological ordering.
```

#### DFS-based Topological Sort

**Idea:** Perform DFS. When a node has no more unvisited neighbors (all descendants processed), add it to the result. Reverse the result at the end.

```
Step 1: For each unvisited node, run DFS
Step 2: In DFS, mark as "visiting" (gray), recurse on neighbors, then mark "visited" (black)
Step 3: When marking "visited", prepend to result (or append and reverse at end)
Step 4: If you visit a "visiting" node → back edge → cycle!
```

**Three-color scheme for cycle detection:**
- **White (unvisited):** Not yet processed
- **Gray (visiting):** Currently in the DFS stack — its descendants are being explored
- **Black (visited):** Fully processed — all descendants are explored

A cycle exists if and only if a gray node is encountered during DFS (a back edge).

```
Graph: A→B, A→C, B→D, C→D

DFS from A:
  A (gray) → B (gray) → D (gray → black, post: [D])
  Back to B (black, post: [D, B])
  Back to A → C (gray) → D (black, skip)
  C (black, post: [D, B, C])
  A (black, post: [D, B, C, A])

Reverse: [A, C, B, D] — a valid topological ordering.
```

### Kahn's vs DFS: When to Use Which

| Feature | Kahn's (BFS) | DFS |
|---------|-------------|-----|
| Implementation | In-degree array + queue | Recursion + visited set |
| Cycle detection | `len(result) < n` | Gray node revisited |
| Level-by-level processing | Natural (for parallel courses) | Requires extra tracking |
| Unique ordering check | Use priority queue | More complex |
| Space | O(V + E) | O(V + E) + recursion stack |
| Preferred when | Need levels, or need to process by in-degree | Default, or need post-order |

**Rule of thumb:** Use Kahn's when the problem involves levels/layers (parallel courses, shortest build time). Use DFS when you need post-order processing or when the problem is more naturally recursive.

### Cycle Detection: The Critical Subproblem

Cycle detection is integrated into both approaches:

**Kahn's:** If the result list has fewer than n nodes after the algorithm finishes, a cycle exists. Nodes in the cycle never reach in-degree 0, so they are never added to the queue.

**DFS:** If during DFS you encounter a node that is currently in the "visiting" (gray) state, you have found a back edge, which means a cycle.

---

## The Template

### Python — Kahn's Algorithm (BFS)

```python
from collections import deque, defaultdict

def topological_sort_kahn(n: int, edges: list[list[int]]) -> list[int]:
    """
    Kahn's BFS topological sort.
    edges[i] = [u, v] means u must come before v.
    Returns topological order, or [] if cycle exists.
    """
    graph = defaultdict(list)
    in_degree = [0] * n

    for u, v in edges:
        graph[u].append(v)
        in_degree[v] += 1

    queue = deque(i for i in range(n) if in_degree[i] == 0)
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return order if len(order) == n else []  # Empty = cycle
```

### Python — DFS Topological Sort

```python
from collections import defaultdict

def topological_sort_dfs(n: int, edges: list[list[int]]) -> list[int]:
    """
    DFS-based topological sort with cycle detection.
    Returns topological order, or [] if cycle exists.
    """
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)

    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n
    order = []

    def dfs(node: int) -> bool:
        """Returns False if cycle detected."""
        color[node] = GRAY
        for neighbor in graph[node]:
            if color[neighbor] == GRAY:
                return False  # Cycle!
            if color[neighbor] == WHITE and not dfs(neighbor):
                return False
        color[node] = BLACK
        order.append(node)
        return True

    for i in range(n):
        if color[i] == WHITE:
            if not dfs(i):
                return []

    return order[::-1]  # Reverse post-order
```

### Go — Kahn's Algorithm

```go
func topologicalSort(n int, edges [][]int) []int {
    graph := make([][]int, n)
    inDegree := make([]int, n)

    for _, e := range edges {
        graph[e[0]] = append(graph[e[0]], e[1])
        inDegree[e[1]]++
    }

    queue := []int{}
    for i := 0; i < n; i++ {
        if inDegree[i] == 0 {
            queue = append(queue, i)
        }
    }

    order := []int{}
    for len(queue) > 0 {
        node := queue[0]
        queue = queue[1:]
        order = append(order, node)
        for _, nei := range graph[node] {
            inDegree[nei]--
            if inDegree[nei] == 0 {
                queue = append(queue, nei)
            }
        }
    }

    if len(order) != n {
        return nil // Cycle
    }
    return order
}
```

### Go — DFS Topological Sort

```go
func topologicalSortDFS(n int, edges [][]int) []int {
    graph := make([][]int, n)
    for _, e := range edges {
        graph[e[0]] = append(graph[e[0]], e[1])
    }

    const (WHITE, GRAY, BLACK = 0, 1, 2)
    color := make([]int, n)
    order := []int{}
    hasCycle := false

    var dfs func(int)
    dfs = func(node int) {
        if hasCycle { return }
        color[node] = GRAY
        for _, nei := range graph[node] {
            if color[nei] == GRAY {
                hasCycle = true
                return
            }
            if color[nei] == WHITE {
                dfs(nei)
            }
        }
        color[node] = BLACK
        order = append(order, node)
    }

    for i := 0; i < n; i++ {
        if color[i] == WHITE {
            dfs(i)
        }
    }

    if hasCycle { return nil }
    // Reverse
    for i, j := 0, len(order)-1; i < j; i, j = i+1, j-1 {
        order[i], order[j] = order[j], order[i]
    }
    return order
}
```

---

## Variant Subpatterns

### 1. Basic Ordering / Feasibility
Can a valid ordering be produced? (Is the graph a DAG?) Return any valid order or detect a cycle.

### 2. Level-by-Level Processing (Parallel Courses)
Process all nodes at the same topological level simultaneously. In Kahn's, all nodes in the queue at the same "round" are at the same level — they have no dependencies on each other.

### 3. Lexicographically Smallest Ordering
Replace the queue in Kahn's with a min-heap. This always processes the smallest available node first, producing the lexicographically smallest valid ordering.

### 4. Ordering from Comparisons (Alien Dictionary)
Build the graph from pairwise comparisons between elements, then topologically sort.

### 5. All Topological Orderings
Use backtracking: at each step, try all nodes with in-degree 0, recurse, then restore. Exponential time.

### 6. Longest Path in DAG
Use topological sort, then relax edges in topological order. This finds the longest (or shortest) path in a DAG in O(V + E).

**Longest Path in DAG Template:**

```python
from collections import defaultdict, deque

def longest_path_dag(n, edges, weights):
    """
    Find longest path from any source to any sink in a weighted DAG.
    edges: [(u, v)], weights: {(u,v): w}
    """
    graph = defaultdict(list)
    in_degree = [0] * n
    for u, v in edges:
        graph[u].append(v)
        in_degree[v] += 1

    # Topological sort (Kahn's)
    queue = deque(i for i in range(n) if in_degree[i] == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # DP: relax edges in topological order
    dist = [0] * n  # Longest distance to reach each node
    for node in order:
        for neighbor in graph[node]:
            w = weights.get((node, neighbor), 1)
            dist[neighbor] = max(dist[neighbor], dist[node] + w)

    return max(dist)
```

This is the technique behind Parallel Courses III (LC 2050), where each course has a duration and you need the minimum total time to complete all courses.

---

## Problem Walkthroughs

---

### Problem 1: Course Schedule (LC 207 — Medium)

**Problem:** There are `numCourses` courses labeled 0 to numCourses-1. You are given an array of prerequisites where `prerequisites[i] = [a, b]` means you must take course `b` before course `a`. Return true if you can finish all courses.

**Brute Force:**
Try all permutations of courses and check if any ordering satisfies all prerequisites. O(n!).

**Key Insight:**
This is cycle detection in a directed graph. If the prerequisite graph has a cycle (e.g., A requires B, B requires C, C requires A), it is impossible to complete all courses. Use topological sort — if a valid ordering exists, return true.

**Optimal Solution:**

```python
from collections import deque, defaultdict

def canFinish(numCourses: int, prerequisites: list[list[int]]) -> bool:
    """
    LC 207: Course Schedule

    Time: O(V + E)
    Space: O(V + E)
    """
    graph = defaultdict(list)
    in_degree = [0] * numCourses

    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1

    queue = deque(i for i in range(numCourses) if in_degree[i] == 0)
    count = 0

    while queue:
        node = queue.popleft()
        count += 1
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return count == numCourses
```

**Dry Run:**
```
numCourses = 4, prerequisites = [[1,0],[2,0],[3,1],[3,2]]
Graph: 0→1, 0→2, 1→3, 2→3
In-degrees: [0, 1, 1, 2]

Queue: [0]. count=0
Pop 0: count=1. Neighbors 1,2.
  in_degree[1]=0 → queue. in_degree[2]=0 → queue.
  Queue: [1, 2]

Pop 1: count=2. Neighbor 3.
  in_degree[3]=1. Queue: [2]

Pop 2: count=3. Neighbor 3.
  in_degree[3]=0 → queue. Queue: [3]

Pop 3: count=4. No neighbors.

count == 4 == numCourses → return True
```

**Cycle example:**
```
numCourses = 2, prerequisites = [[0,1],[1,0]]
Graph: 1→0, 0→1
In-degrees: [1, 1]

Queue: [] (no node has in-degree 0)
count = 0 != 2 → return False
```

**Edge Cases:**
- No prerequisites: always true (every course is independent)
- Single course: always true
- Self-loop `[0, 0]`: cycle, return false
- Disconnected components: each component checked independently

---

### Problem 2: Course Schedule II (LC 210 — Medium)

**Problem:** Same as Course Schedule, but return one valid ordering of courses. Return empty array if impossible.

**Key Insight:**
This is literally topological sort — return the ordering produced by Kahn's algorithm.

**Optimal Solution:**

```python
from collections import deque, defaultdict

def findOrder(numCourses: int, prerequisites: list[list[int]]) -> list[int]:
    """
    LC 210: Course Schedule II

    Time: O(V + E)
    Space: O(V + E)
    """
    graph = defaultdict(list)
    in_degree = [0] * numCourses

    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1

    queue = deque(i for i in range(numCourses) if in_degree[i] == 0)
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return order if len(order) == numCourses else []
```

**Dry Run:** Same as Course Schedule, but collect the order: [0, 1, 2, 3] (or [0, 2, 1, 3] — both valid).

**Edge Cases:** Same as Course Schedule. Note that the ordering is not unique.

**DFS Alternative:**

```python
def findOrder_dfs(numCourses, prerequisites):
    """DFS-based Course Schedule II."""
    from collections import defaultdict
    graph = defaultdict(list)
    for course, prereq in prerequisites:
        graph[prereq].append(course)

    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * numCourses
    order = []

    def dfs(node):
        color[node] = GRAY
        for neighbor in graph[node]:
            if color[neighbor] == GRAY:
                return False
            if color[neighbor] == WHITE and not dfs(neighbor):
                return False
        color[node] = BLACK
        order.append(node)
        return True

    for i in range(numCourses):
        if color[i] == WHITE:
            if not dfs(i):
                return []

    return order[::-1]
```

**Comparing Kahn's and DFS for this problem:**
- Kahn's: More intuitive for interview communication. Easy to explain "process nodes with no remaining prerequisites."
- DFS: More natural if you are comfortable with recursion. Uses post-order to get reverse topological order.

Both are O(V + E). I recommend Kahn's for interviews unless the problem naturally fits DFS (like Alien Dictionary where the graph is built implicitly).

**Follow-up:** What if you want the lexicographically smallest ordering? Use a min-heap instead of a regular queue:

```python
import heapq

def findOrder_lex(numCourses, prerequisites):
    graph = defaultdict(list)
    in_degree = [0] * numCourses
    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1

    heap = [i for i in range(numCourses) if in_degree[i] == 0]
    heapq.heapify(heap)
    order = []

    while heap:
        node = heapq.heappop(heap)
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    return order if len(order) == numCourses else []
```

---

### Problem 3: Alien Dictionary (LC 269 — Hard)

**Problem:** Given a list of words sorted in an alien language's lexicographic order, derive the order of characters in the alien alphabet. Return the order as a string. If no valid order exists, return `""`. If multiple valid orders exist, return any.

**Brute Force:**
Try all permutations of the alphabet and check if any produces the given word ordering. O(26!).

**Key Insight:**
Compare adjacent words to extract ordering constraints. If word[i] = "abc" and word[i+1] = "abd", the first difference is at position 2: `c < d` in the alien alphabet. This gives us a directed edge `c → d`. After extracting all edges, perform topological sort.

**Important edge case:** If a word is a prefix of the next word but longer (e.g., "abc" before "ab"), this is invalid — it contradicts the definition of lexicographic order.

**Optimal Solution:**

```python
from collections import defaultdict, deque

def alienOrder(words: list[str]) -> str:
    """
    LC 269: Alien Dictionary

    Time: O(C) where C = total characters in all words
    Space: O(1) since alphabet size is bounded (26)
    """
    # Step 1: Initialize graph with all unique characters
    graph = defaultdict(set)
    in_degree = {ch: 0 for word in words for ch in word}

    # Step 2: Build graph from adjacent word comparisons
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i + 1]
        min_len = min(len(w1), len(w2))

        # Check for invalid case: "abc" before "ab"
        if len(w1) > len(w2) and w1[:min_len] == w2[:min_len]:
            return ""

        for j in range(min_len):
            if w1[j] != w2[j]:
                if w2[j] not in graph[w1[j]]:
                    graph[w1[j]].add(w2[j])
                    in_degree[w2[j]] += 1
                break  # Only the first difference matters

    # Step 3: Topological sort (Kahn's)
    queue = deque(ch for ch in in_degree if in_degree[ch] == 0)
    order = []

    while queue:
        ch = queue.popleft()
        order.append(ch)
        for neighbor in graph[ch]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # If not all characters are in the order, there is a cycle
    if len(order) != len(in_degree):
        return ""

    return ''.join(order)
```

**Dry Run:**
```
words = ["wrt", "wrf", "er", "ett", "rftt"]

Compare adjacent pairs:
  "wrt" vs "wrf": first diff at index 2: t→f. Edge: t→f
  "wrf" vs "er":  first diff at index 0: w→e. Edge: w→e
  "er" vs "ett":  first diff at index 1: r→t. Edge: r→t
  "ett" vs "rftt": first diff at index 0: e→r. Edge: e→r

Graph: t→f, w→e, r→t, e→r
In-degrees: w:0, e:1, r:1, t:1, f:1

Queue: [w]
Pop w: order=[w]. Neighbor e: in_degree[e]=0 → queue=[e]
Pop e: order=[w,e]. Neighbor r: in_degree[r]=0 → queue=[r]
Pop r: order=[w,e,r]. Neighbor t: in_degree[t]=0 → queue=[t]
Pop t: order=[w,e,r,t]. Neighbor f: in_degree[f]=0 → queue=[f]
Pop f: order=[w,e,r,t,f].

Result: "wertf"
```

**Edge Cases:**
- Single word: return characters in any order (or sorted)
- Two identical words: no constraints, return characters in any order
- Invalid prefix: `["abc", "ab"]` → return `""`
- Duplicate edges: use a set for graph edges to avoid double-counting in-degree
- Characters that appear but have no ordering constraints: valid, place anywhere

**Follow-up:** What if you want to verify that a given ordering is consistent with the word list? Just check each adjacent pair against the proposed ordering.

**Common mistakes specific to Alien Dictionary:**

1. Not checking the prefix case: `["abc", "ab"]` is invalid because a longer word cannot come before its prefix in lexicographic order.

2. Using a list instead of a set for graph edges: If the same edge `c → d` appears from multiple adjacent word pairs, you might increment in-degree multiple times, leading to incorrect in-degree counts.

3. Not including characters that appear in words but have no ordering constraints: These characters must still appear in the output (in any position).

4. Assuming all 26 letters appear: Only characters that appear in the input words should be in the result.

**Edge case handling code:**
```python
# Check: words = ["abc", "ab"] → invalid
for i in range(len(words) - 1):
    w1, w2 = words[i], words[i + 1]
    if len(w1) > len(w2) and w1[:len(w2)] == w2:
        return ""  # Invalid: longer prefix-matching word comes first
```

---

### Problem 4: Parallel Courses (LC 1136 — Medium)

**Problem:** You have `n` courses numbered 1 to n. Given prerequisite pairs, find the minimum number of semesters to take all courses (you can take multiple courses per semester if their prerequisites are met). Return -1 if impossible.

**Brute Force:**
BFS level-by-level, where each level is a semester. Nodes with in-degree 0 at each step can be taken in the current semester.

**Key Insight:**
This is the longest path in a DAG, which equals the number of levels in a topological BFS (Kahn's). Each "level" of the BFS corresponds to one semester — all nodes at the same level can be taken simultaneously because they have no dependencies on each other.

**Optimal Solution:**

```python
from collections import deque, defaultdict

def minimumSemesters(n: int, relations: list[list[int]]) -> int:
    """
    LC 1136: Parallel Courses

    Time: O(V + E)
    Space: O(V + E)
    """
    graph = defaultdict(list)
    in_degree = [0] * (n + 1)  # 1-indexed

    for prev_course, next_course in relations:
        graph[prev_course].append(next_course)
        in_degree[next_course] += 1

    queue = deque(i for i in range(1, n + 1) if in_degree[i] == 0)
    semesters = 0
    courses_taken = 0

    while queue:
        semesters += 1
        next_queue = deque()
        for _ in range(len(queue)):  # Process entire current level
            course = queue.popleft()
            courses_taken += 1
            for neighbor in graph[course]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    next_queue.append(neighbor)
        queue = next_queue

    return semesters if courses_taken == n else -1
```

**Dry Run:**
```
n=6, relations=[[1,2],[1,3],[2,4],[3,4],[4,5],[5,6]]

Graph: 1→2, 1→3, 2→4, 3→4, 4→5, 5→6
In-degrees: [-, 0, 1, 1, 2, 1, 1]

Semester 1: Queue=[1]. Take course 1. courses_taken=1.
  Unlock: 2 (in_degree=0), 3 (in_degree=0)

Semester 2: Queue=[2,3]. Take 2 and 3. courses_taken=3.
  Unlock: 4 (in_degree=0 after both decrements)

Semester 3: Queue=[4]. Take 4. courses_taken=4.
  Unlock: 5 (in_degree=0)

Semester 4: Queue=[5]. Take 5. courses_taken=5.
  Unlock: 6 (in_degree=0)

Semester 5: Queue=[6]. Take 6. courses_taken=6.

6 == n → return 5 semesters
```

**Edge Cases:**
- No prerequisites: all courses in 1 semester
- Linear chain: n semesters (no parallelism)
- Cycle: return -1
- Disconnected components: components are processed in parallel

**Follow-up:** Parallel Courses III (LC 2050) — each course has a duration. Find the minimum total time. Use topological sort with DP: `time[v] = max(time[u] + duration[u]) for all prerequisites u`.

---

### Problem 5: Sort Items by Groups Respecting Dependencies (LC 1203 — Hard)

**Problem:** You have n items, each belonging to a group (or no group, group = -1). Given dependencies between items, sort them such that:
1. Items within the same group are contiguous in the output
2. All dependency constraints are satisfied

Return any valid ordering, or an empty array if impossible.

**Brute Force:**
Try all orderings of groups and items within groups. Exponential.

**Key Insight:**
This requires two levels of topological sort:
1. **Inter-group ordering:** Build a graph of group dependencies and topologically sort groups.
2. **Intra-group ordering:** For each group, topologically sort the items within it.

Items with group = -1 are each in their own unique "group."

Dependencies between items in different groups create group-level dependencies.

**Optimal Solution:**

```python
from collections import defaultdict, deque

def sortItems(n: int, m: int, group: list[int], beforeItems: list[list[int]]) -> list[int]:
    """
    LC 1203: Sort Items by Groups Respecting Dependencies

    Time: O(V + E)
    Space: O(V + E)
    """
    # Step 1: Assign unique group IDs to ungrouped items
    next_group = m
    for i in range(n):
        if group[i] == -1:
            group[i] = next_group
            next_group += 1

    total_groups = next_group

    # Step 2: Build item-level and group-level graphs
    item_graph = defaultdict(list)
    item_in_degree = [0] * n
    group_graph = defaultdict(set)
    group_in_degree = defaultdict(int)

    for i in range(n):
        for dep in beforeItems[i]:
            item_graph[dep].append(i)
            item_in_degree[i] += 1

            if group[dep] != group[i]:
                if i not in group_graph.get(group[dep], set()):
                    # This check prevents duplicate edges
                    if group[i] not in group_graph[group[dep]]:
                        group_graph[group[dep]].add(group[i])
                        group_in_degree[group[i]] += 1

    # Step 3: Topological sort of groups
    group_queue = deque()
    for g in range(total_groups):
        if group_in_degree.get(g, 0) == 0:
            group_queue.append(g)

    group_order = []
    while group_queue:
        g = group_queue.popleft()
        group_order.append(g)
        for neighbor in group_graph.get(g, set()):
            group_in_degree[neighbor] -= 1
            if group_in_degree[neighbor] == 0:
                group_queue.append(neighbor)

    if len(group_order) != total_groups:
        return []  # Cycle in group dependencies

    # Step 4: Topological sort items within each group
    group_to_items = defaultdict(list)
    for i in range(n):
        group_to_items[group[i]].append(i)

    def topo_sort_items(items):
        """Topological sort a subset of items using only intra-group edges."""
        in_deg = {item: 0 for item in items}
        item_set = set(items)
        for item in items:
            for neighbor in item_graph[item]:
                if neighbor in item_set:
                    in_deg[neighbor] += 1

        q = deque(item for item in items if in_deg[item] == 0)
        order = []
        while q:
            node = q.popleft()
            order.append(node)
            for neighbor in item_graph[node]:
                if neighbor in item_set:
                    in_deg[neighbor] -= 1
                    if in_deg[neighbor] == 0:
                        q.append(neighbor)

        return order if len(order) == len(items) else None

    # Step 5: Assemble final result in group order
    result = []
    for g in group_order:
        if g in group_to_items:
            sorted_items = topo_sort_items(group_to_items[g])
            if sorted_items is None:
                return []  # Cycle within group
            result.extend(sorted_items)

    return result
```

**Dry Run (simplified):**
```
n=8, m=2
group = [0, 0, 1, 1, -1, -1, -1, -1]  → after assignment: [0,0,1,1,2,3,4,5]
beforeItems = [[], [0], [], [2], [3], [4], [5], [6]]

Item edges: 0→1, 2→3, 3→4, 4→5, 5→6, 6→7
Group edges: group(2)=1→group(3)=1 (same, skip)
             group(3)=1→group(4)=2 (cross-group!)
             ...etc.

Group sort determines group ordering: e.g., [0, 1, 2, 3, 4, 5]
Within group 0: sort [0, 1] → [0, 1]
Within group 1: sort [2, 3] → [2, 3]
Singles: 4, 5, 6, 7 each in own group

Result: [0, 1, 2, 3, 4, 5, 6, 7]
```

**Edge Cases:**
- All items in one group: just topological sort all items
- All items ungrouped: each is its own group, standard topo sort
- Cycle within a group: return []
- Cycle between groups: return []
- No dependencies: any ordering with groups contiguous

---

### Problem 6: Sequence Reconstruction (LC 444 — Medium/Hard)

**Problem:** Given original sequence `org` and a list of shorter sequences `seqs`, determine if `org` is the only sequence that can be reconstructed from `seqs`. A reconstructed sequence is a shortest common supersequence of all sequences in `seqs`.

This is equivalent to: Is `org` the unique topological ordering of the graph defined by `seqs`?

**Brute Force:**
Generate all possible topological orderings, check if `org` is the only one. Exponential.

**Key Insight:**
A topological ordering is unique if and only if at every step, there is exactly one node with in-degree 0 in the queue. If the queue ever has 2+ elements, there are multiple valid orderings.

Build a graph from the sequences: for consecutive elements `a, b` in a sequence, add edge `a → b`. Then run Kahn's algorithm. If the queue size is always 1, the ordering is unique.

**Optimal Solution:**

```python
from collections import deque, defaultdict

def sequenceReconstruction(org: list[int], seqs: list[list[int]]) -> bool:
    """
    LC 444: Sequence Reconstruction

    Time: O(V + E)
    Space: O(V + E)
    """
    # Collect all nodes and build graph
    graph = defaultdict(set)
    in_degree = {}

    # Initialize all nodes from seqs
    for seq in seqs:
        for val in seq:
            if val not in in_degree:
                in_degree[val] = 0

    # Build edges from consecutive elements in sequences
    for seq in seqs:
        for i in range(len(seq) - 1):
            if seq[i + 1] not in graph[seq[i]]:
                graph[seq[i]].add(seq[i + 1])
                in_degree[seq[i + 1]] += 1

    # Check node count matches
    if len(in_degree) != len(org):
        return False

    queue = deque(node for node in in_degree if in_degree[node] == 0)
    idx = 0

    while queue:
        if len(queue) > 1:
            return False  # Multiple valid orderings possible

        node = queue.popleft()
        if idx >= len(org) or node != org[idx]:
            return False  # Ordering doesn't match org
        idx += 1

        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return idx == len(org)
```

**Dry Run:**
```
org = [1,2,3], seqs = [[1,2],[1,3],[2,3]]

Graph: 1→2, 1→3, 2→3
In-degrees: {1:0, 2:1, 3:2}

Queue: [1] (size 1, ok). Pop 1, matches org[0]=1. idx=1.
  in_degree[2]=0, in_degree[3]=1. Queue: [2]

Queue: [2] (size 1, ok). Pop 2, matches org[1]=2. idx=2.
  in_degree[3]=0. Queue: [3]

Queue: [3] (size 1, ok). Pop 3, matches org[2]=3. idx=3.

idx == 3 == len(org) → return True. The ordering is unique.
```

**Non-unique example:**
```
org = [1,2,3], seqs = [[1,2],[1,3]]

Graph: 1→2, 1→3
In-degrees: {1:0, 2:1, 3:1}

Queue: [1]. Pop 1. idx=1.
  in_degree[2]=0, in_degree[3]=0. Queue: [2, 3]

Queue size = 2 → return False. Both [1,2,3] and [1,3,2] are valid.
```

**Edge Cases:**
- Empty seqs: False (cannot reconstruct anything)
- Single element in org: check if it appears in seqs
- Seqs contain values not in org: return False

---

## Common Mistakes & Interview Tips

### Common Mistakes

1. **Direction of edges:** In "Course Schedule," `[a, b]` means b is a prerequisite for a, i.e., edge goes from b to a. Getting this backwards is extremely common and causes wrong answers.

2. **Not handling disconnected components:** Nodes with no edges still need to be included in the ordering. Initialize all nodes in the in-degree map.

3. **Forgetting to check for cycles:** Always verify that the number of nodes in the result equals the total number of nodes. If fewer, there is a cycle.

4. **Alien Dictionary — not initializing all characters:** Characters that appear in words but have no ordering constraints still need to be in the result. Initialize in-degree for all characters found in any word.

5. **Alien Dictionary — wrong edge extraction:** Only the first difference between adjacent words matters. After finding it, break. Do not continue comparing characters.

6. **Modifying in-degree of nodes not in the current subset:** In multi-level topological sorts (LC 1203), be careful to only count edges within the relevant subset when sorting items within a group.

### Interview Tips

1. **Start by identifying it is a topo sort problem:** "This problem has dependency constraints, so I will model it as a directed graph and perform topological sort."

2. **Draw the graph:** Sketch 3-4 nodes with edges. This clarifies the edge direction and helps catch mistakes early.

3. **State the cycle detection mechanism:** "If the result has fewer nodes than expected, there is a cycle, and I return false / empty array."

4. **Know both Kahn's and DFS:** Be ready to switch approaches if the interviewer asks. Kahn's is usually simpler to implement correctly.

5. **Mention the level-by-level variant:** For Parallel Courses, explain: "In Kahn's algorithm, all nodes in the queue at the same round are at the same topological level and can be processed in parallel."

6. **Alien Dictionary is a classic Hard:** It tests graph construction (from word comparisons) + topological sort + edge cases (prefix, single words, disconnected characters). Practice the edge cases.

---

## Pattern Connections

| From Topological Sort | Connect To | How |
|----------------------|-----------|-----|
| Course Schedule | Cycle Detection (DFS) | Alternative approach with back edges |
| Alien Dictionary | Graph Construction | Build graph from pairwise comparisons |
| Parallel Courses | BFS Level-Order | Levels = semesters |
| Longest Path in DAG | Dynamic Programming | DP on topological order |
| Build System (make) | Dependency Resolution | Real-world application |
| Task Scheduling | Heap + Topo Sort | Priority among available tasks |
| Kruskal's MST | Union-Find | Different graph algorithm, same "process edges" pattern |

### Decision Framework

```
Dependency ordering problem?
├── Can all tasks be completed? (cycle detection)
│   └── Topological sort — check if result has all nodes
├── What is a valid ordering?
│   └── Kahn's BFS or DFS post-order
├── What is the MINIMUM time / semesters?
│   └── Kahn's BFS, count levels
├── Is the ordering UNIQUE?
│   └── Kahn's BFS, check queue size is always 1
├── Lexicographically smallest ordering?
│   └── Kahn's with min-heap instead of queue
└── Multi-level dependencies (groups + items)?
    └── Two-level topological sort
```

---

## Additional Problem: Parallel Courses III (LC 2050 — Hard)

**Problem:** You have n courses, each with a given `time[i]` to complete. Given prerequisite pairs, find the minimum number of months to complete all courses. You can take multiple courses simultaneously if prerequisites are met.

**Key Insight:**
This is the longest path in a DAG, where the path length is the sum of node weights (course durations). Process nodes in topological order. For each node, its earliest completion time is `time[node] + max(completion_time[prereq] for all prereqs)`.

```python
from collections import defaultdict, deque

def minimumTime(n: int, relations: list[list[int]], time: list[int]) -> int:
    """
    LC 2050: Parallel Courses III

    Time: O(V + E)
    Space: O(V + E)
    """
    graph = defaultdict(list)
    in_degree = [0] * (n + 1)

    for prev_course, next_course in relations:
        graph[prev_course].append(next_course)
        in_degree[next_course] += 1

    # completion[i] = earliest time course i finishes
    completion = [0] * (n + 1)
    queue = deque()

    for i in range(1, n + 1):
        if in_degree[i] == 0:
            queue.append(i)
            completion[i] = time[i - 1]

    while queue:
        course = queue.popleft()
        for neighbor in graph[course]:
            # neighbor can't start until course is done
            completion[neighbor] = max(completion[neighbor], completion[course] + time[neighbor - 1])
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return max(completion)
```

**Dry Run:**
```
n=5, relations=[[1,5],[2,5],[3,5],[3,4],[4,5]]
time=[1,2,3,4,5]

Completion starts: [0, 1, 2, 3, 0, 0]  (courses 1,2,3 have no prereqs)
Process 1: neighbor 5. completion[5] = max(0, 1+5) = 6.
Process 2: neighbor 5. completion[5] = max(6, 2+5) = 7.
Process 3: neighbors 5, 4.
  completion[5] = max(7, 3+5) = 8.
  completion[4] = max(0, 3+4) = 7. in_degree[4]=0, add to queue.
Process 4: neighbor 5. completion[5] = max(8, 7+5) = 12.

Max = 12. (Critical path: 3→4→5 with times 3+4+5=12)
```

This is essentially a **critical path analysis** — a fundamental technique in project management and interview problems.

---

## Additional Problem: Build Order (Classic Interview Question)

**Problem:** Given a list of projects and a list of dependencies (project, dependent), find a build order that allows the projects to be built. If there is no valid build order, return an error.

This is Course Schedule II in disguise. Map project names to indices, build the dependency graph, and topologically sort.

```python
def find_build_order(projects: list[str], dependencies: list[tuple[str, str]]) -> list[str]:
    """
    Given dependencies (a, b) meaning a must be built before b,
    find a valid build order.
    """
    from collections import defaultdict, deque

    name_to_idx = {p: i for i, p in enumerate(projects)}
    n = len(projects)
    graph = defaultdict(list)
    in_degree = [0] * n

    for a, b in dependencies:
        graph[name_to_idx[a]].append(name_to_idx[b])
        in_degree[name_to_idx[b]] += 1

    queue = deque(i for i in range(n) if in_degree[i] == 0)
    order = []

    while queue:
        node = queue.popleft()
        order.append(projects[node])
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return order if len(order) == n else []  # Empty = cycle
```

This is a common interview question at Amazon, Microsoft, and Google. The key is recognizing it as topological sort.

---

## Interview Cheat Sheet

**Kahn's Algorithm in 6 lines:**
```python
def topo(n, edges):
    g, ind = defaultdict(list), [0]*n
    for u, v in edges: g[u].append(v); ind[v] += 1
    q = deque(i for i in range(n) if ind[i]==0)
    res = []
    while q:
        u = q.popleft(); res.append(u)
        for v in g[u]:
            ind[v] -= 1
            if ind[v]==0: q.append(v)
    return res if len(res)==n else []
```

**Five things to say when using topological sort in an interview:**
1. "This is a dependency ordering problem, so I will model it as a directed graph and topologically sort."
2. "I use Kahn's algorithm (BFS with in-degree tracking) because [I need levels / it is easier to implement / cycle detection is straightforward]."
3. "If the result contains fewer nodes than expected, there is a cycle."
4. "The time complexity is O(V + E) — we process each node and edge exactly once."
5. For parallel courses: "Each BFS level represents one semester — all nodes at the same level can be processed simultaneously."

---

## Problem Difficulty Progression

**Tier 1 — Foundation (must solve easily):**
1. Course Schedule (LC 207) — cycle detection
2. Course Schedule II (LC 210) — produce valid ordering

**Tier 2 — Core Patterns (should solve within 20 min):**
3. Alien Dictionary (LC 269) — graph construction from comparisons
4. Parallel Courses (LC 1136) — level-by-level processing

**Tier 3 — Hard Applications (stretch goals):**
5. Sort Items by Groups (LC 1203) — two-level topo sort
6. Sequence Reconstruction (LC 444) — uniqueness check
7. Parallel Courses III (LC 2050) — longest path in DAG
8. Minimum Height Trees (LC 310) — related topological peeling

---

## Common Variations in Interviews

### Variation 1: "Can you detect which nodes are in the cycle?"
With Kahn's: nodes not in the result are in cycles (their in-degree never reaches 0). With DFS: track the recursion path and record when you find a back edge.

### Variation 2: "What if there are multiple valid orderings?"
Topological orderings are not unique for most DAGs. If the problem requires a specific one (lexicographically smallest), use a min-heap. If it requires all orderings, use backtracking.

### Variation 3: "What about topological sort on weighted DAGs?"
Process nodes in topological order and relax edges (similar to Dijkstra but without re-ordering). This gives O(V + E) shortest/longest path in a DAG — faster than Dijkstra's O((V + E) log V).

### Variation 4: "How do you handle disconnected components?"
Both Kahn's and DFS handle disconnected components naturally. Kahn's starts with all in-degree-0 nodes (from all components). DFS iterates over all unvisited nodes.
