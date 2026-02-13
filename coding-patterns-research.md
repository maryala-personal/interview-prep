# Senior/Staff Software Engineer Coding Interview Preparation

## Target Companies: Meta, Uber, Microsoft, AI Companies (OpenAI, Anthropic, Google DeepMind)
## Primary Languages: Python, Go

> **Note**: This guide is compiled from extensive knowledge of interview patterns, LeetCode
> problem frequencies, and company-specific practices through mid-2025. Problem frequencies
> are rated as: **Very High** (asked repeatedly), **High** (commonly asked), **Medium**
> (occasionally asked), **Low** (rarely asked). LeetCode numbers are provided where applicable.

---

# Table of Contents

1. [All Major Coding Patterns with Variant Problems](#1-all-major-coding-patterns)
2. [Company-Specific Coding Focus Areas](#2-company-specific-focus-areas)
3. [Go Concurrency Patterns for Interviews](#3-go-concurrency-patterns)
4. [Python-Specific Patterns and Idioms](#4-python-specific-patterns)
5. [Senior/Staff Level Expectations](#5-seniorstaff-level-expectations)
6. [Study Plan and Timeline](#6-study-plan-and-timeline)

---

# 1. All Major Coding Patterns

---

## 1.1 Two Pointers

**Core Idea**: Use two pointers moving toward each other, in the same direction, or from
fixed positions to reduce brute-force O(n^2) to O(n).

**Frequency by Company**:
| Company | Frequency |
|---------|-----------|
| Meta | Very High |
| Uber | High |
| Microsoft | High |
| AI Companies | Medium |

### Variant Problems (Ranked by Difficulty)

| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Two Sum II - Input Array Is Sorted | 167 | Easy | Sorted array, converging pointers | Microsoft |
| 2 | 3Sum | 15 | Medium | Sort + skip duplicates + two pointers | Meta, Uber |
| 3 | Container With Most Water | 11 | Medium | Move the shorter side inward | Meta, Microsoft |
| 4 | Trapping Rain Water | 42 | Hard | Two pointers tracking left/right max | Meta, Uber, Microsoft |

### Python Template
```python
def two_pointer_converging(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        current = nums[left] + nums[right]
        if current == target:
            return [left, right]
        elif current < target:
            left += 1
        else:
            right -= 1
    return [-1, -1]
```

### Go Template
```go
func twoPointerConverging(nums []int, target int) []int {
    left, right := 0, len(nums)-1
    for left < right {
        current := nums[left] + nums[right]
        switch {
        case current == target:
            return []int{left, right}
        case current < target:
            left++
        default:
            right--
        }
    }
    return []int{-1, -1}
}
```

---

## 1.2 Sliding Window

**Core Idea**: Maintain a window that expands/contracts over a sequence to track a
constraint, converting O(n*k) to O(n).

**Frequency by Company**:
| Company | Frequency |
|---------|-----------|
| Meta | Very High |
| Uber | High |
| Microsoft | High |
| AI Companies | High |

### Variant Problems

| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Best Time to Buy and Sell Stock | 121 | Easy | Track min price, max profit | All |
| 2 | Longest Substring Without Repeating Characters | 3 | Medium | Hash set + shrink on duplicate | Meta, Uber, Microsoft |
| 3 | Minimum Window Substring | 76 | Hard | Two counters, expand then shrink | Meta, Microsoft |
| 4 | Sliding Window Maximum | 239 | Hard | Monotonic deque | Uber, Microsoft |

### Python Template
```python
from collections import defaultdict

def sliding_window_variable(s: str, t: str) -> str:
    need = defaultdict(int)
    for c in t:
        need[c] += 1
    missing = len(t)
    left = 0
    best = (float('inf'), 0, 0)  # (length, start, end)

    for right, char in enumerate(s):
        if need[char] > 0:
            missing -= 1
        need[char] -= 1

        while missing == 0:
            if right - left + 1 < best[0]:
                best = (right - left + 1, left, right)
            need[s[left]] += 1
            if need[s[left]] > 0:
                missing += 1
            left += 1

    return s[best[1]:best[2]+1] if best[0] != float('inf') else ""
```

### Go Template
```go
func slidingWindowVariable(s string, t string) string {
    need := make(map[byte]int)
    for i := 0; i < len(t); i++ {
        need[t[i]]++
    }
    missing := len(t)
    left, bestLen, bestStart := 0, len(s)+1, 0

    for right := 0; right < len(s); right++ {
        if need[s[right]] > 0 {
            missing--
        }
        need[s[right]]--

        for missing == 0 {
            if right-left+1 < bestLen {
                bestLen = right - left + 1
                bestStart = left
            }
            need[s[left]]++
            if need[s[left]] > 0 {
                missing++
            }
            left++
        }
    }
    if bestLen > len(s) {
        return ""
    }
    return s[bestStart : bestStart+bestLen]
}
```

---

## 1.3 Binary Search

**Core Idea**: Eliminate half the search space each iteration. Applies to sorted arrays,
search spaces, and "minimize the maximum" / "maximize the minimum" optimization problems.

**Frequency by Company**:
| Company | Frequency |
|---------|-----------|
| Meta | High |
| Uber | High |
| Microsoft | Very High |
| AI Companies | High |

### Variant Problems

| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Binary Search | 704 | Easy | Standard template | All |
| 2 | Find Minimum in Rotated Sorted Array | 153 | Medium | Compare mid with right boundary | Microsoft, Uber |
| 3 | Search in Rotated Sorted Array | 33 | Medium | Determine which half is sorted | Meta, Microsoft |
| 4 | Median of Two Sorted Arrays | 4 | Hard | Binary search on partition | Meta, Microsoft |
| 5 | Koko Eating Bananas | 875 | Medium | Binary search on answer space | Uber, Meta |
| 6 | Split Array Largest Sum | 410 | Hard | Binary search + greedy check | Microsoft |

### Python Template (Binary Search on Answer)
```python
def binary_search_on_answer(nums, condition):
    """Template for 'minimize the maximum' or 'maximize the minimum' problems."""
    lo, hi = min_possible, max_possible

    while lo < hi:
        mid = lo + (hi - lo) // 2
        if condition(mid):  # can we achieve this with constraint?
            hi = mid         # try smaller (for minimize)
        else:
            lo = mid + 1

    return lo

# Example: Koko Eating Bananas
import math
def minEatingSpeed(piles, h):
    lo, hi = 1, max(piles)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        hours = sum(math.ceil(p / mid) for p in piles)
        if hours <= h:
            hi = mid
        else:
            lo = mid + 1
    return lo
```

### Go Template
```go
func binarySearchOnAnswer(piles []int, h int) int {
    lo, hi := 1, slices.Max(piles)
    for lo < hi {
        mid := lo + (hi-lo)/2
        hours := 0
        for _, p := range piles {
            hours += (p + mid - 1) / mid // ceiling division
        }
        if hours <= h {
            hi = mid
        } else {
            lo = mid + 1
        }
    }
    return lo
}
```

---

## 1.4 BFS (Breadth-First Search)

**Core Idea**: Level-order exploration using a queue. Best for shortest path in unweighted
graphs, level-order tree traversal, and multi-source BFS.

**Frequency by Company**:
| Company | Frequency |
|---------|-----------|
| Meta | Very High |
| Uber | Very High |
| Microsoft | Very High |
| AI Companies | High |

### Variant Problems

| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Binary Tree Level Order Traversal | 102 | Medium | Queue + process level by level | All |
| 2 | Rotting Oranges | 994 | Medium | Multi-source BFS (all rotten at once) | Meta, Uber |
| 3 | Word Ladder | 127 | Hard | BFS on word transformation graph | Meta, Microsoft |
| 4 | Shortest Path in Binary Matrix | 1091 | Medium | 8-directional BFS | Meta |
| 5 | Open the Lock | 752 | Medium | BFS on state space | Microsoft |

### Python Template (Multi-Source BFS)
```python
from collections import deque

def multi_source_bfs(grid):
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    visited = set()

    # Add all starting sources
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == SOURCE:
                queue.append((r, c, 0))  # (row, col, distance)
                visited.add((r, c))

    directions = [(0,1),(0,-1),(1,0),(-1,0)]
    while queue:
        r, c, dist = queue.popleft()
        for dr, dc in directions:
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc, dist+1))
    return dist  # last distance processed
```

---

## 1.5 DFS (Depth-First Search)

**Core Idea**: Explore as deep as possible before backtracking. Used for tree/graph
traversal, connected components, cycle detection, and path finding.

**Frequency by Company**:
| Company | Frequency |
|---------|-----------|
| Meta | Very High |
| Uber | Very High |
| Microsoft | Very High |
| AI Companies | Very High |

### Variant Problems

| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Number of Islands | 200 | Medium | DFS/BFS to mark visited cells | Meta (extremely common), Uber |
| 2 | Clone Graph | 133 | Medium | DFS + hashmap for visited nodes | Meta, Microsoft |
| 3 | Course Schedule | 207 | Medium | Cycle detection in directed graph | Meta, Uber |
| 4 | Alien Dictionary | 269 | Hard | Build graph + topological DFS | Meta, Uber, Microsoft |
| 5 | Number of Connected Components | 323 | Medium | DFS or Union-Find | Meta, Microsoft |

### Python Template (Iterative DFS for Graphs)
```python
def dfs_iterative(graph, start):
    visited = set()
    stack = [start]
    result = []

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        result.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                stack.append(neighbor)
    return result

# DFS on grid (recursive)
def dfs_grid(grid, r, c, visited):
    if (r < 0 or r >= len(grid) or c < 0 or c >= len(grid[0])
            or grid[r][c] == 0 or (r, c) in visited):
        return 0
    visited.add((r, c))
    count = 1
    for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
        count += dfs_grid(grid, r+dr, c+dc, visited)
    return count
```

---

## 1.6 Dynamic Programming (DP)

**Core Idea**: Break problem into overlapping subproblems with optimal substructure.
Build solution bottom-up (tabulation) or top-down (memoization).

**Frequency by Company**:
| Company | Frequency |
|---------|-----------|
| Meta | Very High |
| Uber | High |
| Microsoft | Very High |
| AI Companies | Very High |

### Sub-Patterns

#### 1D DP
| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Climbing Stairs | 70 | Easy | dp[i] = dp[i-1] + dp[i-2] | All |
| 2 | House Robber | 198 | Medium | Take or skip, dp[i] = max(dp[i-1], dp[i-2]+nums[i]) | Meta, Uber |
| 3 | Longest Increasing Subsequence | 300 | Medium | O(n log n) with patience sorting | Microsoft, Meta |
| 4 | Word Break | 139 | Medium | dp[i] = any(dp[j] and s[j:i] in wordDict) | Meta (very common), Microsoft |

#### 2D DP
| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Unique Paths | 62 | Medium | Grid DP, dp[i][j] = dp[i-1][j] + dp[i][j-1] | Microsoft |
| 2 | Longest Common Subsequence | 1143 | Medium | Classic 2D DP on two strings | Microsoft, Uber |
| 3 | Edit Distance | 72 | Medium | Insert/Delete/Replace transitions | Meta, Microsoft |
| 4 | Regular Expression Matching | 10 | Hard | 2D DP with '.' and '*' handling | Meta |

#### Knapsack Variants
| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Partition Equal Subset Sum | 416 | Medium | 0/1 Knapsack on sum/2 | Meta |
| 2 | Coin Change | 322 | Medium | Unbounded knapsack (min coins) | Meta, Uber, Microsoft |
| 3 | Target Sum | 494 | Medium | Count subsets with given difference | Meta |

#### Interval DP / State Machine DP
| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Best Time to Buy and Sell Stock with Cooldown | 309 | Medium | State machine: hold/sold/rest | Meta |
| 2 | Burst Balloons | 312 | Hard | Think about last balloon to burst | Microsoft |

### Python Template (Bottom-Up with Space Optimization)
```python
# 1D DP - House Robber pattern
def rob(nums):
    if not nums:
        return 0
    prev2, prev1 = 0, 0
    for num in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + num)
    return prev1

# 2D DP - Edit Distance
def minDistance(word1, word2):
    m, n = len(word1), len(word2)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        new_dp = [i] + [0] * n
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                new_dp[j] = dp[j-1]
            else:
                new_dp[j] = 1 + min(dp[j], new_dp[j-1], dp[j-1])
        dp = new_dp
    return dp[n]
```

---

## 1.7 Backtracking

**Core Idea**: Build candidates incrementally, abandon ("backtrack") when a candidate
cannot lead to a valid solution.

**Frequency by Company**:
| Company | Frequency |
|---------|-----------|
| Meta | High |
| Uber | Medium |
| Microsoft | High |
| AI Companies | Medium |

### Variant Problems

| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Subsets | 78 | Medium | Include/exclude each element | Meta, Microsoft |
| 2 | Permutations | 46 | Medium | Swap or visited-set approach | Meta, Microsoft |
| 3 | Combination Sum | 39 | Medium | Unlimited reuse, start index | Meta |
| 4 | N-Queens | 51 | Hard | Column + diagonal conflict sets | Microsoft |
| 5 | Word Search | 79 | Medium | DFS grid + backtrack visited | Meta (very common) |
| 6 | Generate Parentheses | 22 | Medium | Track open/close counts | Meta, Microsoft |

### Python Template
```python
def backtrack(candidates, target):
    result = []

    def helper(start, path, remaining):
        if remaining == 0:
            result.append(path[:])
            return
        if remaining < 0:
            return

        for i in range(start, len(candidates)):
            # Skip duplicates (if candidates has duplicates and is sorted)
            if i > start and candidates[i] == candidates[i-1]:
                continue
            path.append(candidates[i])
            helper(i + 1, path, remaining - candidates[i])  # i+1 for no reuse, i for reuse
            path.pop()

    candidates.sort()
    helper(0, [], target)
    return result
```

---

## 1.8 Greedy

**Core Idea**: Make the locally optimal choice at each step, hoping it leads to a globally
optimal solution. Often requires a proof of correctness (exchange argument).

**Frequency by Company**:
| Company | Frequency |
|---------|-----------|
| Meta | High |
| Uber | High |
| Microsoft | High |
| AI Companies | Medium |

### Variant Problems

| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Maximum Subarray | 53 | Medium | Kadane's algorithm | All |
| 2 | Jump Game | 55 | Medium | Track farthest reachable index | Meta |
| 3 | Task Scheduler | 621 | Medium | Most frequent task determines idle slots | Meta (very common) |
| 4 | Merge Intervals | 56 | Medium | Sort by start, merge overlapping | Meta (extremely common), Uber, Microsoft |
| 5 | Non-overlapping Intervals | 435 | Medium | Sort by end time, greedy select | Uber |
| 6 | Gas Station | 134 | Medium | If total gas >= total cost, solution exists | Microsoft |

### Python Template (Interval Scheduling / Merge)
```python
def merge_intervals(intervals):
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
```

---

## 1.9 Graph Algorithms

**Core Idea**: Covers Dijkstra, Bellman-Ford, Floyd-Warshall, topological sort,
strongly connected components, and bipartite checking.

**Frequency by Company**:
| Company | Frequency |
|---------|-----------|
| Meta | High |
| Uber | Very High (maps/routing domain) |
| Microsoft | High |
| AI Companies | Medium |

### Variant Problems

| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Course Schedule II | 210 | Medium | Topological sort (Kahn's BFS) | Meta, Uber |
| 2 | Network Delay Time | 743 | Medium | Dijkstra's shortest path | Uber, Microsoft |
| 3 | Cheapest Flights Within K Stops | 787 | Medium | Modified Bellman-Ford or BFS with pruning | Uber |
| 4 | Graph Valid Tree | 261 | Medium | n-1 edges + connected | Meta |
| 5 | Is Graph Bipartite? | 785 | Medium | Two-color BFS/DFS | Microsoft |
| 6 | Reconstruct Itinerary | 332 | Hard | Eulerian path (Hierholzer's) | Uber |

### Python Template (Dijkstra)
```python
import heapq
from collections import defaultdict

def dijkstra(n, edges, src):
    graph = defaultdict(list)
    for u, v, w in edges:
        graph[u].append((v, w))

    dist = [float('inf')] * n
    dist[src] = 0
    heap = [(0, src)]  # (distance, node)

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))
    return dist
```

### Go Template (Dijkstra)
```go
type Edge struct {
    to, weight int
}

type Item struct {
    node, dist int
}

type MinHeap []Item

func (h MinHeap) Len() int            { return len(h) }
func (h MinHeap) Less(i, j int) bool  { return h[i].dist < h[j].dist }
func (h MinHeap) Swap(i, j int)       { h[i], h[j] = h[j], h[i] }
func (h *MinHeap) Push(x any)         { *h = append(*h, x.(Item)) }
func (h *MinHeap) Pop() any {
    old := *h
    n := len(old)
    item := old[n-1]
    *h = old[:n-1]
    return item
}

func dijkstra(n int, graph [][]Edge, src int) []int {
    dist := make([]int, n)
    for i := range dist {
        dist[i] = math.MaxInt64
    }
    dist[src] = 0
    h := &MinHeap{{src, 0}}
    heap.Init(h)

    for h.Len() > 0 {
        curr := heap.Pop(h).(Item)
        if curr.dist > dist[curr.node] {
            continue
        }
        for _, e := range graph[curr.node] {
            newDist := dist[curr.node] + e.weight
            if newDist < dist[e.to] {
                dist[e.to] = newDist
                heap.Push(h, Item{e.to, newDist})
            }
        }
    }
    return dist
}
```

---

## 1.10 Trie (Prefix Tree)

**Core Idea**: Tree-like data structure for efficient prefix-based lookups, commonly used
for autocomplete, spell checking, and word search problems.

**Frequency by Company**:
| Company | Frequency |
|---------|-----------|
| Meta | High |
| Uber | Medium |
| Microsoft | High |
| AI Companies | High (NLP-related) |

### Variant Problems

| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Implement Trie | 208 | Medium | Basic insert/search/startsWith | All |
| 2 | Design Add and Search Words | 211 | Medium | Trie + DFS for wildcard '.' | Meta |
| 3 | Word Search II | 212 | Hard | Trie + backtracking on grid | Meta (common), Microsoft |
| 4 | Search Suggestions System | 1268 | Medium | Trie + DFS or binary search | Microsoft |

### Python Template
```python
class TrieNode:
    __slots__ = ['children', 'is_end']
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self._find(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        return self._find(prefix) is not None

    def _find(self, prefix: str):
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node
```

---

## 1.11 Union-Find (Disjoint Set Union)

**Core Idea**: Track connected components efficiently with near O(1) union and find
operations using path compression and union by rank.

**Frequency by Company**:
| Company | Frequency |
|---------|-----------|
| Meta | High |
| Uber | Medium |
| Microsoft | Medium |
| AI Companies | Low |

### Variant Problems

| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Number of Connected Components in an Undirected Graph | 323 | Medium | Basic union-find | Meta |
| 2 | Redundant Connection | 684 | Medium | Edge that creates cycle | Microsoft |
| 3 | Accounts Merge | 721 | Medium | Union emails, group by root | Meta (common) |
| 4 | Smallest String With Swaps | 1202 | Medium | Union-find + sort within components | Microsoft |

### Python Template
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.components = n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        # union by rank
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.components -= 1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)
```

---

## 1.12 Monotonic Stack / Monotonic Queue

**Core Idea**: Maintain elements in increasing or decreasing order to efficiently find
next greater/smaller element, or sliding window min/max.

**Frequency by Company**:
| Company | Frequency |
|---------|-----------|
| Meta | Medium |
| Uber | Medium |
| Microsoft | High |
| AI Companies | Low |

### Variant Problems

| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Daily Temperatures | 739 | Medium | Monotonic decreasing stack | Meta |
| 2 | Next Greater Element I | 496 | Easy | Stack + hashmap | Microsoft |
| 3 | Largest Rectangle in Histogram | 84 | Hard | Monotonic increasing stack | Meta, Microsoft |
| 4 | Sliding Window Maximum | 239 | Hard | Monotonic decreasing deque | Uber, Microsoft |
| 5 | Maximal Rectangle | 85 | Hard | Build on histogram per row | Meta |

### Python Template (Next Greater Element)
```python
def next_greater_elements(nums):
    n = len(nums)
    result = [-1] * n
    stack = []  # stores indices, monotonic decreasing values

    for i in range(n):
        while stack and nums[stack[-1]] < nums[i]:
            idx = stack.pop()
            result[idx] = nums[i]
        stack.append(i)
    return result
```

---

## 1.13 Topological Sort

**Core Idea**: Linear ordering of vertices in a DAG such that for every directed edge (u,v),
u comes before v. Used for dependency resolution.

**Frequency by Company**:
| Company | Frequency |
|---------|-----------|
| Meta | High |
| Uber | High |
| Microsoft | Medium |
| AI Companies | Medium (ML pipeline scheduling) |

### Variant Problems

| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Course Schedule | 207 | Medium | Cycle detection via topo sort | Meta, Uber |
| 2 | Course Schedule II | 210 | Medium | Return the ordering | Meta, Uber |
| 3 | Alien Dictionary | 269 | Hard | Build char graph from word order | Meta, Uber |
| 4 | Parallel Courses | 1136 | Medium | Topo sort + level tracking (BFS) | Microsoft |

### Python Template (Kahn's Algorithm - BFS)
```python
from collections import deque, defaultdict

def topological_sort(n, edges):
    graph = defaultdict(list)
    in_degree = [0] * n
    for u, v in edges:
        graph[u].append(v)
        in_degree[v] += 1

    queue = deque([i for i in range(n) if in_degree[i] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return order if len(order) == n else []  # empty = cycle detected
```

---

## 1.14 Heap / Priority Queue

**Core Idea**: Efficiently retrieve min/max element. Used for top-K problems, merge-K
sorted lists, median tracking, and scheduling.

**Frequency by Company**:
| Company | Frequency |
|---------|-----------|
| Meta | Very High |
| Uber | High |
| Microsoft | High |
| AI Companies | High |

### Variant Problems

| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Kth Largest Element in an Array | 215 | Medium | Min-heap of size k, or quickselect | Meta (extremely common) |
| 2 | Top K Frequent Elements | 347 | Medium | Heap or bucket sort | Meta, Uber |
| 3 | Merge K Sorted Lists | 23 | Hard | Min-heap of list heads | Meta, Microsoft |
| 4 | Find Median from Data Stream | 295 | Hard | Two heaps (max-heap + min-heap) | Meta, Microsoft |
| 5 | Task Scheduler | 621 | Medium | Max-heap + cooldown queue | Meta |
| 6 | Reorganize String | 767 | Medium | Max-heap, alternate placement | Meta |

### Python Template (Two Heaps for Median)
```python
import heapq

class MedianFinder:
    def __init__(self):
        self.small = []  # max-heap (negate values)
        self.large = []  # min-heap

    def addNum(self, num: int) -> None:
        heapq.heappush(self.small, -num)
        # Ensure max of small <= min of large
        if self.small and self.large and -self.small[0] > self.large[0]:
            val = -heapq.heappop(self.small)
            heapq.heappush(self.large, val)
        # Balance sizes (small can have at most 1 extra)
        if len(self.small) > len(self.large) + 1:
            val = -heapq.heappop(self.small)
            heapq.heappush(self.large, val)
        elif len(self.large) > len(self.small):
            val = heapq.heappop(self.large)
            heapq.heappush(self.small, -val)

    def findMedian(self) -> float:
        if len(self.small) > len(self.large):
            return -self.small[0]
        return (-self.small[0] + self.large[0]) / 2
```

---

## 1.15 Intervals

**Core Idea**: Problems involving ranges/intervals -- merging, inserting, finding overlaps,
scheduling.

**Frequency by Company**:
| Company | Frequency |
|---------|-----------|
| Meta | Very High |
| Uber | Very High (ride scheduling) |
| Microsoft | High |
| AI Companies | Medium |

### Variant Problems

| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Merge Intervals | 56 | Medium | Sort by start, merge overlapping | Meta (top question), Uber |
| 2 | Insert Interval | 57 | Medium | Find overlap region, merge | Meta, Microsoft |
| 3 | Meeting Rooms II | 253 | Medium | Min-heap or sweep line for max overlap | Meta, Uber, Microsoft |
| 4 | Non-overlapping Intervals | 435 | Medium | Greedy: sort by end, count removals | Uber |
| 5 | Employee Free Time | 759 | Hard | Merge all busy intervals, find gaps | Uber |

### Python Template (Sweep Line)
```python
import heapq

def min_meeting_rooms(intervals):
    if not intervals:
        return 0
    intervals.sort(key=lambda x: x[0])
    heap = []  # tracks end times of ongoing meetings

    for start, end in intervals:
        if heap and heap[0] <= start:
            heapq.heappop(heap)
        heapq.heappush(heap, end)

    return len(heap)
```

---

## 1.16 Linked List

**Core Idea**: Pointer manipulation, cycle detection, reversal, merge operations.

**Frequency by Company**:
| Company | Frequency |
|---------|-----------|
| Meta | High |
| Uber | Medium |
| Microsoft | High |
| AI Companies | Low |

### Variant Problems

| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Reverse Linked List | 206 | Easy | Iterative: prev/curr pointers | All |
| 2 | Linked List Cycle | 141 | Easy | Floyd's slow/fast pointers | Microsoft |
| 3 | Merge Two Sorted Lists | 21 | Easy | Dummy head, compare and link | Meta, Microsoft |
| 4 | Reorder List | 143 | Medium | Find mid + reverse second half + merge | Meta |
| 5 | LRU Cache | 146 | Medium | Doubly linked list + hashmap | Meta (very common), Uber, Microsoft |
| 6 | Copy List with Random Pointer | 138 | Medium | HashMap clone or interleave technique | Meta |
| 7 | Reverse Nodes in k-Group | 25 | Hard | Count k, reverse segment, recurse | Meta, Microsoft |

### Python Template (LRU Cache)
```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.cap = capacity

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.cap:
            self.cache.popitem(last=False)
```

---

## 1.17 Tree Traversals and Tree Problems

**Core Idea**: Inorder, preorder, postorder traversals; BST properties; tree construction
and modification.

**Frequency by Company**:
| Company | Frequency |
|---------|-----------|
| Meta | Very High |
| Uber | High |
| Microsoft | Very High |
| AI Companies | Medium |

### Variant Problems

| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Invert Binary Tree | 226 | Easy | Swap left and right recursively | All |
| 2 | Lowest Common Ancestor of a Binary Tree | 236 | Medium | If both sides return non-null, current is LCA | Meta (extremely common) |
| 3 | Validate Binary Search Tree | 98 | Medium | Inorder must be strictly increasing | Meta, Microsoft |
| 4 | Binary Tree Right Side View | 199 | Medium | BFS level order, take last of each level | Meta |
| 5 | Serialize and Deserialize Binary Tree | 297 | Hard | Preorder with null markers | Meta, Microsoft |
| 6 | Binary Tree Maximum Path Sum | 124 | Hard | DFS returning single-path max, update global | Meta (common) |
| 7 | Diameter of Binary Tree | 543 | Easy | DFS depth, diameter = left + right | Meta |
| 8 | Construct Binary Tree from Preorder and Inorder | 105 | Medium | Recursive partition using inorder index | Microsoft |

### Python Template (Postorder DFS for Tree Max Path Sum)
```python
def maxPathSum(root):
    result = [float('-inf')]

    def dfs(node):
        if not node:
            return 0
        left = max(dfs(node.left), 0)   # ignore negative paths
        right = max(dfs(node.right), 0)
        # Update global max: path through this node
        result[0] = max(result[0], node.val + left + right)
        # Return single-path max for parent
        return node.val + max(left, right)

    dfs(root)
    return result[0]
```

---

## 1.18 Bit Manipulation

**Core Idea**: Use binary representations for efficient operations. XOR, AND, OR, shifts
for subset generation, counting, and toggling.

**Frequency by Company**:
| Company | Frequency |
|---------|-----------|
| Meta | Low-Medium |
| Uber | Low |
| Microsoft | Medium |
| AI Companies | Medium (ML quantization context) |

### Variant Problems

| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Single Number | 136 | Easy | XOR all elements: a ^ a = 0 | Microsoft |
| 2 | Number of 1 Bits | 191 | Easy | n & (n-1) drops lowest set bit | Microsoft |
| 3 | Counting Bits | 338 | Easy | dp[i] = dp[i >> 1] + (i & 1) | Microsoft |
| 4 | Reverse Bits | 190 | Easy | Shift and accumulate | Microsoft |
| 5 | Sum of Two Integers | 371 | Medium | XOR for sum, AND+shift for carry | Meta |

### Python Template
```python
# Count set bits (Brian Kernighan's algorithm)
def count_bits(n):
    count = 0
    while n:
        n &= n - 1  # clear lowest set bit
        count += 1
    return count

# Check if power of two
def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0

# Get/Set/Clear bit at position
def get_bit(n, i):    return (n >> i) & 1
def set_bit(n, i):    return n | (1 << i)
def clear_bit(n, i):  return n & ~(1 << i)
```

---

## 1.19 String / Array Manipulation

**Core Idea**: In-place operations, pattern matching, encoding/decoding, and hash-based
grouping.

**Frequency by Company**:
| Company | Frequency |
|---------|-----------|
| Meta | Very High |
| Uber | High |
| Microsoft | High |
| AI Companies | Medium |

### Variant Problems

| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | Valid Palindrome | 125 | Easy | Two pointers, skip non-alnum | Meta |
| 2 | Group Anagrams | 49 | Medium | Sort as key or tuple(count) as key | Meta (very common) |
| 3 | Longest Palindromic Substring | 5 | Medium | Expand around center | Meta |
| 4 | Encode and Decode Strings | 271 | Medium | Length prefix encoding | Meta |
| 5 | Product of Array Except Self | 238 | Medium | Prefix and suffix products | Meta (common), Microsoft |
| 6 | Basic Calculator II | 227 | Medium | Stack-based with operator precedence | Meta |

---

## 1.20 Design / Data Structure Problems

**Core Idea**: Implement a data structure with specific time complexity requirements.
Critical for senior/staff interviews.

**Frequency by Company**:
| Company | Frequency |
|---------|-----------|
| Meta | Very High |
| Uber | High |
| Microsoft | High |
| AI Companies | High |

### Variant Problems

| # | Problem | LC# | Difficulty | Key Insight | Top Askers |
|---|---------|-----|------------|-------------|------------|
| 1 | LRU Cache | 146 | Medium | OrderedDict or DLL + HashMap | Meta (#1 most asked), all |
| 2 | Min Stack | 155 | Medium | Track min at each level | Microsoft |
| 3 | Design Twitter | 355 | Medium | Merge K feeds with heap | Meta |
| 4 | Design Hit Counter | 362 | Medium | Queue or circular buffer | Meta, Uber |
| 5 | LFU Cache | 460 | Hard | DLL per frequency + HashMap | Meta |
| 6 | Time Based Key-Value Store | 981 | Medium | HashMap + binary search on timestamps | Uber |
| 7 | Random Pick with Weight | 528 | Medium | Prefix sum + binary search | Meta |
| 8 | Insert Delete GetRandom O(1) | 380 | Medium | Array + HashMap swap trick | Meta, Uber |

---

# 2. Company-Specific Focus Areas

---

## 2.1 Meta (Facebook)

### Interview Format (Senior/Staff - E5/E6)
- **2 coding rounds** (45 min each, expect 2 problems per round)
- **1 system design round**
- **1 behavioral round**
- Staff (E6) adds a deeper system design or "product architecture" round

### Top 25 Most Frequently Asked Problems (ordered by frequency)
1. **LRU Cache** (LC 146) -- nearly every loop
2. **Merge Intervals** (LC 56)
3. **Valid Palindrome II** (LC 680)
4. **Lowest Common Ancestor of Binary Tree** (LC 236)
5. **Kth Largest Element** (LC 215)
6. **Binary Tree Right Side View** (LC 199)
7. **Product of Array Except Self** (LC 238)
8. **Number of Islands** (LC 200)
9. **Group Anagrams** (LC 49)
10. **Word Break** (LC 139)
11. **Random Pick with Weight** (LC 528)
12. **Task Scheduler** (LC 621)
13. **Minimum Remove to Make Valid Parentheses** (LC 1249)
14. **Subarray Sum Equals K** (LC 560)
15. **Accounts Merge** (LC 721)
16. **Word Search** (LC 79)
17. **Longest Substring Without Repeating Characters** (LC 3)
18. **Find Median from Data Stream** (LC 295)
19. **Basic Calculator II** (LC 227)
20. **Binary Tree Maximum Path Sum** (LC 124)
21. **Serialize and Deserialize Binary Tree** (LC 297)
22. **Diameter of Binary Tree** (LC 543)
23. **Copy List with Random Pointer** (LC 138)
24. **3Sum** (LC 15)
25. **Minimum Window Substring** (LC 76)

### Key Patterns at Meta
- **Trees and Graphs**: Nearly every interview has at least one tree/graph problem
- **Hash Maps**: Grouping, counting, caching patterns
- **Intervals**: Merge, insert, overlapping intervals
- **Two problems per 45 minutes**: Speed is critical -- practice for 15-20 min per medium

### Meta-Specific Tips
- They value **clean, working code** over pseudocode
- Always **discuss time and space complexity**
- They like **follow-up questions** that increase difficulty (e.g., "now do it in O(1) space")
- Practice on a **shared editor** (no autocomplete, no syntax highlighting)
- Code must **compile and run** mentally -- interviewers trace through your code

---

## 2.2 Uber

### Interview Format (Senior/Staff - L5a/L5b)
- **2 coding rounds** (45-60 min, usually 1-2 problems each)
- **1 system design round** (often ride-sharing/location-based)
- **1 behavioral/culture fit round**
- Staff adds a **domain design** or **technical deep-dive** round

### Top Problems and Focus Areas
1. **Graph/Shortest Path** -- very common (Dijkstra, BFS) -- maps/routing domain
2. **Intervals** -- ride scheduling, time overlap
3. **Sliding Window / Two Pointers** -- streaming data
4. **Design Problems** -- rate limiter, ride matching, surge pricing
5. **Geospatial** -- nearest neighbors, grid-based search

### Frequently Asked Problems
| Problem | LC# | Pattern |
|---------|-----|---------|
| Network Delay Time | 743 | Dijkstra |
| Cheapest Flights Within K Stops | 787 | Modified Dijkstra/BFS |
| Meeting Rooms II | 253 | Intervals + Heap |
| Employee Free Time | 759 | Intervals |
| Merge Intervals | 56 | Intervals |
| Sliding Window Maximum | 239 | Monotonic Deque |
| LRU Cache | 146 | Design |
| Time Based Key-Value Store | 981 | Design + Binary Search |
| Rotting Oranges | 994 | Multi-source BFS |
| Course Schedule | 207 | Topological Sort |
| Reconstruct Itinerary | 332 | Euler Path |
| Word Ladder | 127 | BFS |
| Insert Delete GetRandom O(1) | 380 | Design |
| Trapping Rain Water | 42 | Two Pointers |
| Top K Frequent Elements | 347 | Heap |

### Uber-Specific Tips
- Problems often have a **real-world framing** (ride matching, ETAs, location tracking)
- Strong emphasis on **graph algorithms** due to maps domain
- Practice explaining **trade-offs** (accuracy vs. latency, memory vs. speed)
- **Concurrency** may come up for Go/backend roles

---

## 2.3 Microsoft

### Interview Format (Senior/Principal - L63/L64/L65)
- **3-4 coding rounds** (45 min each, usually 1 problem per round, deeper discussion)
- **1 system design round**
- **1 behavioral/hiring manager round**
- "As Appropriate" (AA) round with a senior leader

### Top Problems and Focus Areas
1. **Trees/BST** -- very heavy on tree problems
2. **Dynamic Programming** -- more DP than other companies
3. **Binary Search** -- creative applications
4. **Linked List** -- classic manipulation
5. **String manipulation** -- parsing, regex-like problems
6. **OOP Design** -- sometimes asked alongside coding

### Frequently Asked Problems
| Problem | LC# | Pattern |
|---------|-----|---------|
| LRU Cache | 146 | Design |
| Two Sum | 1 | HashMap |
| Merge Two Sorted Lists | 21 | Linked List |
| Validate BST | 98 | Tree DFS |
| Binary Tree Level Order Traversal | 102 | BFS |
| Construct Binary Tree from Preorder/Inorder | 105 | Tree |
| Serialize and Deserialize Binary Tree | 297 | Tree + Design |
| Search in Rotated Sorted Array | 33 | Binary Search |
| Longest Increasing Subsequence | 300 | DP |
| Edit Distance | 72 | DP |
| N-Queens | 51 | Backtracking |
| Largest Rectangle in Histogram | 84 | Monotonic Stack |
| Median of Two Sorted Arrays | 4 | Binary Search |
| Coin Change | 322 | DP |
| Container With Most Water | 11 | Two Pointers |

### Microsoft-Specific Tips
- **Deeper discussions**: expect thorough analysis of edge cases and complexity
- They value **object-oriented design** thinking
- **Testing mindset**: discuss test cases, edge cases, error handling
- More tolerant of **slightly slower solutions** if well-explained
- L65 (Principal) may have an **architecture** round instead of pure coding

---

## 2.4 AI Companies (OpenAI, Anthropic, Google DeepMind)

### Interview Format (varies by company)
- **OpenAI**: 2 coding rounds + 1 system design + 1 ML/AI-specific + behavioral
- **Anthropic**: 2 coding rounds + 1 system design + 1 technical deep-dive + values alignment
- **Google DeepMind**: Google-style (LC coding + ML design + research discussion)

### Common Coding Focus Areas

#### All AI Companies
- **Graph algorithms** -- computation graphs, DAGs, topological sort
- **Dynamic Programming** -- sequence problems, optimization
- **Recursion/Tree traversal** -- AST-like structures, expression evaluation
- **String/Sequence processing** -- tokenization, parsing
- **Probability/Sampling** -- weighted random selection, reservoir sampling

#### OpenAI-Specific
- Heavy on **systems programming** and **infrastructure** problems
- **Streaming/Pipeline design** -- processing token streams
- **Concurrency and parallelism** -- critical for distributed training/inference
- May include **math-heavy** problems (linear algebra, probability)

#### Anthropic-Specific
- Strong emphasis on **code quality and clarity**
- **Safety-oriented thinking** in design discussions
- **Python-heavy** -- expect Pythonic solutions
- Problems may involve **text processing** and **data pipeline** patterns
- Values alignment discussion is distinctive

#### Google DeepMind-Specific
- Standard **Google L5/L6 coding bar**
- Additional **ML system design** or **research** component
- Heavy on **graph algorithms** and **DP**
- May ask about **numerical methods** and **optimization**

### Frequently Asked Problem Types at AI Companies
| Problem | LC# | Pattern | Why |
|---------|-----|---------|-----|
| LRU Cache | 146 | Design | Caching in inference |
| Topological Sort (Course Schedule II) | 210 | Graph | Computation graph ordering |
| Word Break | 139 | DP | Tokenization analogy |
| Serialize/Deserialize Binary Tree | 297 | Tree | Model serialization |
| Merge K Sorted Lists | 23 | Heap | Merging ranked outputs |
| Random Pick with Weight | 528 | Binary Search | Sampling distributions |
| Design Hit Counter | 362 | Design | Monitoring/metrics |
| Longest Common Subsequence | 1143 | DP | Sequence alignment |
| Implement Trie | 208 | Trie | Prefix search/tokenization |
| Rate Limiter (system design) | -- | Design | API rate limiting |
| Producer-Consumer (concurrency) | -- | Concurrency | Pipeline parallelism |
| Expression Evaluation | 224/227 | Stack | Expression parsing |

---

# 3. Go Concurrency Patterns for Interviews

---

## 3.1 Goroutines Fundamentals

```go
package main

import (
    "fmt"
    "sync"
)

// Basic goroutine
func main() {
    var wg sync.WaitGroup
    for i := 0; i < 5; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            fmt.Printf("Worker %d running\n", id)
        }(i) // IMPORTANT: pass i as argument to avoid closure capture bug
    }
    wg.Wait()
}
```

**Common Interview Pitfall**: Forgetting to pass loop variable to goroutine closure.
Prior to Go 1.22, the loop variable was shared across iterations. Go 1.22+ changed
loop variable semantics, but interviewers still ask about this.

---

## 3.2 Channels (Buffered and Unbuffered)

```go
// Unbuffered channel: synchronous send/receive
ch := make(chan int)

// Buffered channel: async up to capacity
ch := make(chan int, 100)

// Directional channels in function signatures
func producer(out chan<- int) { out <- 42 }
func consumer(in <-chan int)  { val := <-in }

// Range over channel (reads until closed)
go func() {
    for i := 0; i < 10; i++ {
        ch <- i
    }
    close(ch) // MUST close to unblock range
}()
for val := range ch {
    fmt.Println(val)
}
```

**Interview Question**: "What happens if you send on a closed channel?"
Answer: **Panic**. Only the sender should close a channel, never the receiver.

---

## 3.3 Select Statement

```go
func multiplexer(ch1, ch2 <-chan string, quit <-chan struct{}) {
    for {
        select {
        case msg := <-ch1:
            fmt.Println("From ch1:", msg)
        case msg := <-ch2:
            fmt.Println("From ch2:", msg)
        case <-quit:
            fmt.Println("Shutting down")
            return
        default:
            // Non-blocking: executes if no channel is ready
            // Remove default for blocking select
        }
    }
}

// Timeout pattern
select {
case result := <-ch:
    fmt.Println(result)
case <-time.After(5 * time.Second):
    fmt.Println("Timed out")
}
```

---

## 3.4 Sync Primitives

```go
import "sync"

// Mutex (mutual exclusion)
type SafeCounter struct {
    mu    sync.Mutex
    count map[string]int
}

func (c *SafeCounter) Inc(key string) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count[key]++
}

// RWMutex (multiple readers, single writer)
type SafeMap struct {
    mu   sync.RWMutex
    data map[string]string
}

func (m *SafeMap) Get(key string) string {
    m.mu.RLock()
    defer m.mu.RUnlock()
    return m.data[key]
}

func (m *SafeMap) Set(key, value string) {
    m.mu.Lock()
    defer m.mu.Unlock()
    m.data[key] = value
}

// Once (exactly-once initialization)
var (
    instance *Singleton
    once     sync.Once
)

func GetInstance() *Singleton {
    once.Do(func() {
        instance = &Singleton{}
    })
    return instance
}

// sync.Map (concurrent map, no external locking needed)
var cache sync.Map
cache.Store("key", "value")
val, ok := cache.Load("key")

// sync.Cond (condition variable)
cond := sync.NewCond(&sync.Mutex{})
// Wait:
cond.L.Lock()
for !condition {
    cond.Wait()
}
cond.L.Unlock()
// Signal:
cond.Signal()   // wake one
cond.Broadcast() // wake all

// sync.Pool (object reuse to reduce GC pressure)
pool := sync.Pool{
    New: func() any { return make([]byte, 1024) },
}
buf := pool.Get().([]byte)
defer pool.Put(buf)
```

---

## 3.5 Worker Pool Pattern

```go
func workerPool(jobs <-chan Job, results chan<- Result, numWorkers int) {
    var wg sync.WaitGroup
    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func(workerID int) {
            defer wg.Done()
            for job := range jobs {
                result := process(job)
                results <- result
            }
        }(i)
    }

    // Close results when all workers finish
    go func() {
        wg.Wait()
        close(results)
    }()
}

// Usage
func main() {
    jobs := make(chan Job, 100)
    results := make(chan Result, 100)

    workerPool(jobs, results, 10)

    // Send jobs
    go func() {
        for _, j := range allJobs {
            jobs <- j
        }
        close(jobs)
    }()

    // Collect results
    for r := range results {
        fmt.Println(r)
    }
}
```

---

## 3.6 Fan-In / Fan-Out

```go
// Fan-Out: distribute work to multiple goroutines
func fanOut(input <-chan int, numWorkers int) []<-chan int {
    channels := make([]<-chan int, numWorkers)
    for i := 0; i < numWorkers; i++ {
        ch := make(chan int)
        channels[i] = ch
        go func(out chan<- int) {
            defer close(out)
            for val := range input {
                out <- val * val // some computation
            }
        }(ch)
    }
    return channels
}

// Fan-In: merge multiple channels into one
func fanIn(channels ...<-chan int) <-chan int {
    merged := make(chan int)
    var wg sync.WaitGroup

    for _, ch := range channels {
        wg.Add(1)
        go func(c <-chan int) {
            defer wg.Done()
            for val := range c {
                merged <- val
            }
        }(ch)
    }

    go func() {
        wg.Wait()
        close(merged)
    }()

    return merged
}
```

---

## 3.7 Context for Cancellation and Timeouts

```go
import "context"

// Timeout context
func fetchWithTimeout(url string) ([]byte, error) {
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return nil, err
    }
    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return nil, err // includes context.DeadlineExceeded
    }
    defer resp.Body.Close()
    return io.ReadAll(resp.Body)
}

// Cancellation propagation
func processWithCancellation(ctx context.Context, items []Item) error {
    for _, item := range items {
        select {
        case <-ctx.Done():
            return ctx.Err() // context.Canceled or context.DeadlineExceeded
        default:
            if err := process(item); err != nil {
                return err
            }
        }
    }
    return nil
}

// Context with values (use sparingly, for request-scoped data)
type contextKey string

func WithRequestID(ctx context.Context, id string) context.Context {
    return context.WithValue(ctx, contextKey("requestID"), id)
}

func RequestID(ctx context.Context) string {
    id, _ := ctx.Value(contextKey("requestID")).(string)
    return id
}
```

---

## 3.8 errgroup (Structured Concurrency)

```go
import "golang.org/x/sync/errgroup"

func fetchAll(ctx context.Context, urls []string) ([]string, error) {
    g, ctx := errgroup.WithContext(ctx)
    results := make([]string, len(urls))

    for i, url := range urls {
        i, url := i, url // capture loop variables (pre-Go 1.22)
        g.Go(func() error {
            body, err := fetchWithContext(ctx, url)
            if err != nil {
                return err
            }
            results[i] = body
            return nil
        })
    }

    if err := g.Wait(); err != nil {
        return nil, err // first error cancels context, other goroutines see ctx.Done()
    }
    return results, nil
}

// With concurrency limit
func fetchAllLimited(ctx context.Context, urls []string) error {
    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(10) // max 10 concurrent goroutines

    for _, url := range urls {
        url := url
        g.Go(func() error {
            return fetch(ctx, url)
        })
    }
    return g.Wait()
}
```

---

## 3.9 Pipeline Pattern

```go
// Stage 1: Generate
func generate(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            out <- n
        }
    }()
    return out
}

// Stage 2: Square
func square(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            out <- n * n
        }
    }()
    return out
}

// Stage 3: Filter
func filter(in <-chan int, predicate func(int) bool) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            if predicate(n) {
                out <- n
            }
        }
    }()
    return out
}

// Compose pipeline
func main() {
    ch := generate(1, 2, 3, 4, 5)
    ch = square(ch)
    ch = filter(ch, func(n int) bool { return n > 10 })
    for v := range ch {
        fmt.Println(v) // 16, 25
    }
}
```

---

## 3.10 Common Go Concurrency Interview Questions

1. **Implement a concurrent-safe cache with TTL expiry**
   - Use `sync.RWMutex` or `sync.Map`
   - Background goroutine for cleanup with `time.Ticker`
   - Context-based shutdown

2. **Implement rate limiter (token bucket)**
   - `time.Ticker` to add tokens
   - Buffered channel as token bucket
   - `select` with `default` for non-blocking try-acquire

3. **Implement producer-consumer with graceful shutdown**
   - Context cancellation
   - WaitGroup for drain
   - Close channels to signal completion

4. **Implement parallel web crawler with deduplication**
   - Worker pool + visited set (sync.Map or mutex-protected map)
   - Bounded concurrency with semaphore (buffered channel or errgroup.SetLimit)
   - Context for timeout

5. **Detect and prevent goroutine leaks**
   - Always ensure goroutines can exit (use context, done channels)
   - runtime.NumGoroutine() for debugging
   - `goleak` package for testing

```go
// Rate Limiter (Token Bucket)
type RateLimiter struct {
    tokens chan struct{}
    quit   chan struct{}
}

func NewRateLimiter(rate int, interval time.Duration) *RateLimiter {
    rl := &RateLimiter{
        tokens: make(chan struct{}, rate),
        quit:   make(chan struct{}),
    }
    // Fill initial tokens
    for i := 0; i < rate; i++ {
        rl.tokens <- struct{}{}
    }
    // Refill
    go func() {
        ticker := time.NewTicker(interval / time.Duration(rate))
        defer ticker.Stop()
        for {
            select {
            case <-ticker.C:
                select {
                case rl.tokens <- struct{}{}:
                default: // bucket full
                }
            case <-rl.quit:
                return
            }
        }
    }()
    return rl
}

func (rl *RateLimiter) Allow() bool {
    select {
    case <-rl.tokens:
        return true
    default:
        return false
    }
}

func (rl *RateLimiter) Wait(ctx context.Context) error {
    select {
    case <-rl.tokens:
        return nil
    case <-ctx.Done():
        return ctx.Err()
    }
}

func (rl *RateLimiter) Stop() {
    close(rl.quit)
}
```

---

# 4. Python-Specific Patterns and Idioms for Interviews

---

## 4.1 collections Module

### Counter
```python
from collections import Counter

# Frequency counting
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
freq = Counter(words)
# Counter({'apple': 3, 'banana': 2, 'cherry': 1})

# Most common
freq.most_common(2)  # [('apple', 3), ('banana', 2)]

# Subtract / intersection / union
c1 = Counter("aabbc")
c2 = Counter("abccc")
c1 & c2  # Counter({'a': 1, 'b': 1, 'c': 1}) -- min of each
c1 | c2  # Counter({'a': 2, 'b': 2, 'c': 3}) -- max of each

# Check if one is subset of another (anagram check)
def is_anagram(s, t):
    return Counter(s) == Counter(t)

# Sliding window with Counter
def findAnagrams(s, p):
    """LC 438: Find All Anagrams in a String"""
    result = []
    p_count = Counter(p)
    s_count = Counter()
    for i, ch in enumerate(s):
        s_count[ch] += 1
        if i >= len(p):
            left_ch = s[i - len(p)]
            s_count[left_ch] -= 1
            if s_count[left_ch] == 0:
                del s_count[left_ch]
        if s_count == p_count:
            result.append(i - len(p) + 1)
    return result
```

### defaultdict
```python
from collections import defaultdict

# Graph adjacency list
graph = defaultdict(list)
for u, v in edges:
    graph[u].append(v)
    graph[v].append(u)

# Group by pattern
def groupAnagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        key = tuple(sorted(s))
        groups[key].append(s)
    return list(groups.values())

# Nested defaultdict (for complex groupings)
nested = defaultdict(lambda: defaultdict(int))
nested["user1"]["page_views"] += 1

# defaultdict(int) for counting (simpler than Counter for single use)
count = defaultdict(int)
for item in items:
    count[item] += 1
```

### deque
```python
from collections import deque

# BFS queue (O(1) popleft vs list's O(n))
queue = deque([start])
queue.append(item)       # add to right
item = queue.popleft()   # remove from left

# Sliding window (fixed size)
def maxSlidingWindow(nums, k):
    """LC 239: Sliding Window Maximum using monotonic deque"""
    dq = deque()  # stores indices
    result = []
    for i, num in enumerate(nums):
        # Remove elements outside window
        while dq and dq[0] < i - k + 1:
            dq.popleft()
        # Maintain decreasing order
        while dq and nums[dq[-1]] < num:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result

# Deque as bounded buffer
class BoundedBuffer:
    def __init__(self, maxlen):
        self.buffer = deque(maxlen=maxlen)  # auto-evicts oldest

    def add(self, item):
        self.buffer.append(item)

    def get_all(self):
        return list(self.buffer)
```

### OrderedDict
```python
from collections import OrderedDict

# LRU Cache (most Pythonic implementation)
class LRUCache:
    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.cap = capacity

    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.cap:
            self.cache.popitem(last=False)  # remove oldest (FIFO end)
```

---

## 4.2 itertools Module

```python
import itertools

# Permutations and Combinations
list(itertools.permutations([1,2,3]))       # all orderings
list(itertools.permutations([1,2,3], 2))    # P(3,2)
list(itertools.combinations([1,2,3], 2))    # C(3,2) = [(1,2),(1,3),(2,3)]
list(itertools.combinations_with_replacement([1,2,3], 2))  # with repetition

# Product (Cartesian product, replaces nested loops)
list(itertools.product([0,1], repeat=3))    # all 3-bit binary numbers
list(itertools.product("abc", "12"))        # [('a','1'),('a','2'),...]

# Chain (flatten iterables)
list(itertools.chain([1,2], [3,4], [5]))    # [1,2,3,4,5]
list(itertools.chain.from_iterable([[1,2],[3,4]]))  # [1,2,3,4]

# Groupby (consecutive groups - must be sorted first!)
data = sorted(items, key=lambda x: x.category)
for key, group in itertools.groupby(data, key=lambda x: x.category):
    print(key, list(group))

# Accumulate (prefix sums and more)
list(itertools.accumulate([1,2,3,4]))       # [1,3,6,10]
list(itertools.accumulate([3,1,4,1,5], max))  # running max: [3,3,4,4,5]

# Zip_longest
list(itertools.zip_longest([1,2], [3,4,5], fillvalue=0))  # [(1,3),(2,4),(0,5)]

# Pairwise (Python 3.10+)
list(itertools.pairwise([1,2,3,4]))         # [(1,2),(2,3),(3,4)]

# Batched (Python 3.12+)
list(itertools.batched([1,2,3,4,5], 2))     # [(1,2),(3,4),(5,)]
```

---

## 4.3 heapq Module

```python
import heapq

# Min-heap operations
heap = []
heapq.heappush(heap, 5)
heapq.heappush(heap, 1)
heapq.heappush(heap, 3)
smallest = heapq.heappop(heap)  # 1
peek = heap[0]                   # peek without removing

# Max-heap (negate values)
max_heap = []
heapq.heappush(max_heap, -5)
heapq.heappush(max_heap, -1)
largest = -heapq.heappop(max_heap)  # 5

# Heapify (O(n) vs O(n log n) for repeated push)
nums = [5, 1, 3, 7, 2]
heapq.heapify(nums)  # in-place, modifies nums

# Top K elements
def topKFrequent(nums, k):
    count = Counter(nums)
    return heapq.nlargest(k, count.keys(), key=count.get)

# nlargest / nsmallest (efficient for small k)
heapq.nlargest(3, nums)   # top 3
heapq.nsmallest(3, nums)  # bottom 3

# Merge K sorted lists
def mergeKLists(lists):
    merged = list(heapq.merge(*lists))  # heapq.merge returns iterator

# Custom comparison (use tuples)
heap = []
heapq.heappush(heap, (priority, index, item))  # index as tiebreaker
# For custom objects, use __lt__ or wrapper class

# Push and pop simultaneously (more efficient)
heapq.heapreplace(heap, new_val)  # pop then push
heapq.heappushpop(heap, new_val)  # push then pop
```

---

## 4.4 bisect Module (Binary Search)

```python
import bisect

# Find insertion point (maintains sorted order)
sorted_list = [1, 3, 5, 7, 9]
bisect.bisect_left(sorted_list, 5)   # 2 (leftmost position for 5)
bisect.bisect_right(sorted_list, 5)  # 3 (rightmost position after 5)

# Insert while maintaining sorted order
bisect.insort_left(sorted_list, 4)   # [1, 3, 4, 5, 7, 9]
bisect.insort_right(sorted_list, 6)  # [1, 3, 4, 5, 6, 7, 9]

# Binary search (find exact element)
def binary_search(sorted_list, target):
    i = bisect.bisect_left(sorted_list, target)
    if i < len(sorted_list) and sorted_list[i] == target:
        return i
    return -1

# Count occurrences in sorted array
def count_occurrences(sorted_list, target):
    left = bisect.bisect_left(sorted_list, target)
    right = bisect.bisect_right(sorted_list, target)
    return right - left

# Find floor and ceiling
def floor(sorted_list, target):
    i = bisect.bisect_right(sorted_list, target) - 1
    return sorted_list[i] if i >= 0 else None

def ceiling(sorted_list, target):
    i = bisect.bisect_left(sorted_list, target)
    return sorted_list[i] if i < len(sorted_list) else None

# SortedList alternative (for dynamic sorted container)
# pip install sortedcontainers
from sortedcontainers import SortedList
sl = SortedList([3, 1, 4])
sl.add(2)           # O(log n) insert
sl.remove(3)        # O(log n) remove
sl.bisect_left(2)   # O(log n) search
```

---

## 4.5 Python Interview Idioms and Tricks

### Sorting
```python
# Sort with custom key
intervals.sort(key=lambda x: (x[0], -x[1]))  # by start asc, end desc

# Sort dictionary by value
sorted_items = sorted(d.items(), key=lambda x: x[1], reverse=True)

# Stable sort (preserves relative order of equal elements)
# Python's sort is stable -- Timsort guarantees this
```

### List Comprehensions and Generators
```python
# Matrix transpose
matrix = [[1,2,3],[4,5,6],[7,8,9]]
transposed = list(zip(*matrix))  # [(1,4,7),(2,5,8),(3,6,9)]

# Flatten 2D list
flat = [x for row in matrix for x in row]

# Generator for memory efficiency
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Conditional expression
result = value_if_true if condition else value_if_false
```

### Useful Built-ins
```python
# any / all
any(x > 5 for x in nums)  # True if any element > 5
all(x > 0 for x in nums)  # True if all elements > 0

# enumerate (with start index)
for i, val in enumerate(items, start=1):
    pass

# zip (parallel iteration)
for a, b in zip(list1, list2):
    pass

# map / filter (prefer comprehensions in interviews for clarity)
squares = list(map(lambda x: x**2, nums))
evens = list(filter(lambda x: x % 2 == 0, nums))

# min / max with key
longest = max(strings, key=len)
closest = min(points, key=lambda p: p[0]**2 + p[1]**2)

# divmod (quotient and remainder)
q, r = divmod(17, 5)  # (3, 2)

# pow with modulo (for modular arithmetic)
pow(base, exp, mod)  # efficient modular exponentiation
```

### String Methods
```python
# Quick checks
s.isalnum()    # alphanumeric
s.isalpha()    # alphabetic
s.isdigit()    # digits
s.islower()    # lowercase
s.isupper()    # uppercase

# Split and join
words = s.split()           # split on whitespace
parts = s.split(",", 1)    # split on first comma only
result = " ".join(words)

# Strip
s.strip()    # both sides
s.lstrip()   # left
s.rstrip()   # right

# Translation table (for character replacement)
table = str.maketrans("aeiou", "AEIOU")
s.translate(table)

# Count occurrences
s.count("abc")
```

### Set Operations
```python
a = {1, 2, 3}
b = {2, 3, 4}

a | b  # union: {1, 2, 3, 4}
a & b  # intersection: {2, 3}
a - b  # difference: {1}
a ^ b  # symmetric difference: {1, 4}
a <= b # subset check
a >= b # superset check

# Frozenset (hashable, usable as dict key or set element)
fs = frozenset([1, 2, 3])
seen = set()
seen.add(fs)
```

### functools and Other Utilities
```python
from functools import lru_cache, reduce, cache

# Memoization (top-down DP)
@lru_cache(maxsize=None)  # or @cache in Python 3.9+
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)

# Reduce
total = reduce(lambda a, b: a * b, nums)

# cmp_to_key (custom sorting with comparison function)
from functools import cmp_to_key

def compare(x, y):
    # For LC 179: Largest Number
    if x + y > y + x:
        return -1
    elif x + y < y + x:
        return 1
    return 0

nums_str = sorted(map(str, nums), key=cmp_to_key(compare))
```

### Math Tricks
```python
import math

math.gcd(12, 18)       # 6
math.lcm(12, 18)       # 36 (Python 3.9+)
math.ceil(7 / 3)       # 3
math.floor(7 / 3)      # 2
math.isqrt(17)         # 4 (integer square root, Python 3.8+)
math.comb(10, 3)       # 120 (combinations, Python 3.8+)
math.perm(10, 3)       # 720 (permutations, Python 3.8+)
math.inf               # float infinity
-math.inf              # negative infinity

# Integer ceiling division without importing math
def ceil_div(a, b):
    return (a + b - 1) // b
    # or: -(-a // b)
```

---

# 5. Senior/Staff Level Expectations

---

## 5.1 What Differentiates Senior/Staff Coding Interviews

| Aspect | Junior/Mid | Senior (L5/E5/63) | Staff (L6/E6/65) |
|--------|-----------|-------------------|-------------------|
| **Problems** | 1 medium | 1-2 medium or 1 hard | 1 hard with extensions |
| **Code Quality** | Working | Clean, modular, tested | Production-ready, extensible |
| **Complexity Analysis** | State it | Derive and compare alternatives | Prove optimality |
| **Edge Cases** | Handle when asked | Proactively identify | Exhaustive coverage |
| **Follow-ups** | Handle 1 | Handle 2-3 naturally | Drive extensions yourself |
| **Communication** | Answer questions | Explain thinking | Lead the discussion |
| **Trade-offs** | Acknowledge | Analyze | Quantify with real numbers |

## 5.2 How to Approach Problems at Senior/Staff Level

### The UMPIRE Framework
1. **U**nderstand: Clarify inputs, outputs, constraints, edge cases
2. **M**atch: Map to known patterns/data structures
3. **P**lan: Describe approach before coding, discuss alternatives
4. **I**mplement: Write clean, modular code
5. **R**eview: Walk through with test cases, check edge cases
6. **E**valuate: Analyze time/space complexity, discuss optimizations

### Senior/Staff Communication Patterns
- "Before I code, let me discuss two approaches..."
- "The trade-off here is time vs. space..."
- "This handles the general case; let me also consider..."
- "In production, I would also want to handle..."
- "The amortized complexity is O(1) because..."

---

## 5.3 Meta-Patterns: Recognizing Problem Types

| If you see... | Think... | Pattern |
|---------------|----------|---------|
| "Sorted array" | Binary Search, Two Pointers | Binary Search |
| "All permutations/subsets" | Backtracking | Backtracking |
| "Top/Kth/Least K" | Heap | Heap |
| "Common ancestor" | DFS on tree | Tree DFS |
| "Level-by-level" | BFS | BFS |
| "Contiguous subarray" | Sliding Window, Prefix Sum | Sliding Window |
| "Shortest path" | BFS (unweighted), Dijkstra (weighted) | Graph |
| "Connected components" | DFS, BFS, Union-Find | Graph/Union-Find |
| "Dependency ordering" | Topological Sort | Graph |
| "DP" clues: min/max, count ways, true/false | Dynamic Programming | DP |
| "Can you do it in-place?" | Two Pointers, Swap | Two Pointers |
| "Stream/online" | Heap, Design | Heap/Design |
| "Prefix/autocomplete" | Trie | Trie |
| "Intervals/ranges" | Sort + Sweep/Merge | Intervals |
| "Min/Max of sliding window" | Monotonic Deque | Monotonic Queue |
| "Next greater/smaller" | Monotonic Stack | Monotonic Stack |
| "Matrix/grid" | BFS/DFS, DP | Graph/DP |
| "Palindrome" | Two Pointers, DP | Two Pointers/DP |
| "Parentheses" | Stack | Stack |
| "Design a data structure" | HashMap + Other (DLL, Heap, etc.) | Design |

---

# 6. Study Plan and Timeline

---

## 6.1 Recommended 8-Week Study Plan

### Week 1-2: Fundamentals
- [ ] Two Pointers (5 problems)
- [ ] Sliding Window (5 problems)
- [ ] Binary Search (5 problems)
- [ ] Linked List (4 problems)
- [ ] Stack/Queue basics (3 problems)

### Week 3-4: Trees and Graphs
- [ ] Binary Tree DFS/BFS (8 problems)
- [ ] BST operations (3 problems)
- [ ] Graph BFS/DFS (5 problems)
- [ ] Topological Sort (3 problems)
- [ ] Union-Find (3 problems)

### Week 5-6: DP and Advanced
- [ ] 1D DP (5 problems)
- [ ] 2D DP (4 problems)
- [ ] Knapsack variants (3 problems)
- [ ] Backtracking (5 problems)
- [ ] Heap/Priority Queue (5 problems)
- [ ] Trie (3 problems)

### Week 7: Company-Specific Prep
- [ ] Meta top 25 problems (review/solve)
- [ ] Uber graph + interval problems
- [ ] Microsoft tree + DP problems
- [ ] AI company design + concurrency problems

### Week 8: Mock Interviews and Review
- [ ] 2-3 timed mock interviews
- [ ] Review weak areas
- [ ] Practice communication and edge case analysis
- [ ] Go concurrency patterns review (for Go roles)

## 6.2 Daily Practice Routine
- **Morning** (1 hour): Solve 2 medium problems timed (20 min each)
- **Evening** (1 hour): Review solutions, study one pattern in depth
- **Weekend** (2-3 hours): Mock interview + hard problems

## 6.3 Essential Problem List (80 Problems)

### Must-Do Across All Companies (Sorted by Priority)

**Tier 1 - Absolute Must (solve first)**:
1. Two Sum (LC 1)
2. Best Time to Buy and Sell Stock (LC 121)
3. Valid Parentheses (LC 20)
4. Merge Intervals (LC 56)
5. LRU Cache (LC 146)
6. Number of Islands (LC 200)
7. Lowest Common Ancestor (LC 236)
8. Product of Array Except Self (LC 238)
9. Group Anagrams (LC 49)
10. Coin Change (LC 322)
11. Course Schedule (LC 207)
12. Word Break (LC 139)
13. 3Sum (LC 15)
14. Binary Tree Level Order Traversal (LC 102)
15. Kth Largest Element (LC 215)

**Tier 2 - Very Important**:
16. Longest Substring Without Repeating Characters (LC 3)
17. Container With Most Water (LC 11)
18. Validate BST (LC 98)
19. Clone Graph (LC 133)
20. Top K Frequent Elements (LC 347)
21. Merge K Sorted Lists (LC 23)
22. Word Search (LC 79)
23. Combination Sum (LC 39)
24. Subsets (LC 78)
25. Search in Rotated Sorted Array (LC 33)
26. Find Median from Data Stream (LC 295)
27. Task Scheduler (LC 621)
28. Minimum Window Substring (LC 76)
29. Serialize/Deserialize Binary Tree (LC 297)
30. Reverse Linked List (LC 206)

**Tier 3 - Important**:
31. Meeting Rooms II (LC 253)
32. Edit Distance (LC 72)
33. Longest Increasing Subsequence (LC 300)
34. Binary Tree Maximum Path Sum (LC 124)
35. Trapping Rain Water (LC 42)
36. Accounts Merge (LC 721)
37. Longest Palindromic Substring (LC 5)
38. Implement Trie (LC 208)
39. Daily Temperatures (LC 739)
40. Insert Delete GetRandom O(1) (LC 380)
41. Random Pick with Weight (LC 528)
42. Alien Dictionary (LC 269)
43. Longest Common Subsequence (LC 1143)
44. Network Delay Time (LC 743)
45. Rotting Oranges (LC 994)
46. Copy List with Random Pointer (LC 138)
47. Reorder List (LC 143)
48. Generate Parentheses (LC 22)
49. Subarray Sum Equals K (LC 560)
50. Minimum Remove to Make Valid Parentheses (LC 1249)

**Tier 4 - For Thorough Preparation**:
51. Word Search II (LC 212)
52. Sliding Window Maximum (LC 239)
53. Largest Rectangle in Histogram (LC 84)
54. Regular Expression Matching (LC 10)
55. Median of Two Sorted Arrays (LC 4)
56. N-Queens (LC 51)
57. Burst Balloons (LC 312)
58. Koko Eating Bananas (LC 875)
59. Split Array Largest Sum (LC 410)
60. Cheapest Flights Within K Stops (LC 787)
61. Employee Free Time (LC 759)
62. Reconstruct Itinerary (LC 332)
63. Time Based Key-Value Store (LC 981)
64. LFU Cache (LC 460)
65. Reverse Nodes in k-Group (LC 25)
66. Partition Equal Subset Sum (LC 416)
67. Target Sum (LC 494)
68. Binary Tree Right Side View (LC 199)
69. Diameter of Binary Tree (LC 543)
70. Redundant Connection (LC 684)
71. Basic Calculator II (LC 227)
72. Word Ladder (LC 127)
73. Search Suggestions System (LC 1268)
74. Smallest String With Swaps (LC 1202)
75. House Robber (LC 198)
76. Jump Game (LC 55)
77. Non-overlapping Intervals (LC 435)
78. Is Graph Bipartite? (LC 785)
79. Design Hit Counter (LC 362)
80. Maximal Rectangle (LC 85)

---

## Appendix A: Quick Reference - Complexity Cheat Sheet

| Data Structure | Access | Search | Insert | Delete | Space |
|---------------|--------|--------|--------|--------|-------|
| Array | O(1) | O(n) | O(n) | O(n) | O(n) |
| Hash Table | - | O(1) avg | O(1) avg | O(1) avg | O(n) |
| BST (balanced) | - | O(log n) | O(log n) | O(log n) | O(n) |
| Heap | - | O(n) | O(log n) | O(log n) | O(n) |
| Trie | - | O(L) | O(L) | O(L) | O(ALPHABET * L * N) |
| Union-Find | - | O(alpha(n)) | O(alpha(n)) | - | O(n) |

| Algorithm | Time | Space | Notes |
|-----------|------|-------|-------|
| Binary Search | O(log n) | O(1) | Sorted input |
| BFS/DFS | O(V+E) | O(V) | Graph traversal |
| Dijkstra | O((V+E) log V) | O(V) | With binary heap |
| Topological Sort | O(V+E) | O(V) | DAG only |
| Merge Sort | O(n log n) | O(n) | Stable |
| Quick Sort | O(n log n) avg | O(log n) | In-place, unstable |
| Heap Sort | O(n log n) | O(1) | In-place, unstable |
| Counting Sort | O(n+k) | O(k) | Integer keys |

## Appendix B: Go vs Python Interview Trade-offs

| Factor | Python | Go |
|--------|--------|----|
| **Speed to code** | Faster (less boilerplate) | Slower (explicit types) |
| **Built-in DS** | Rich (Counter, deque, heapq) | Minimal (need to implement) |
| **Heap** | heapq module | Must implement heap.Interface |
| **Sorting** | sorted() with key/cmp | sort.Slice with less function |
| **Concurrency** | Show in system design only | First-class (goroutines, channels) |
| **When to use Python** | Most coding interviews | When concurrency is the focus |
| **When to use Go** | Concurrency/systems questions | Backend-focused roles |

**Recommendation**: Use **Python** for general coding interviews (faster to write, richer
standard library). Switch to **Go** when the problem specifically involves concurrency,
systems programming, or when interviewing for a Go-focused role.

---

*Last updated: February 2025. Based on LeetCode problem frequencies, Blind/Glassdoor
interview reports, and community interview experiences through mid-2025.*
