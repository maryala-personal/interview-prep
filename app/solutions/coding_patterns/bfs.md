# BFS (Breadth-First Search) — Complete Interview Guide

## When to Use This Pattern

**Signals that indicate BFS:**
1. The problem asks for the **shortest path** in an **unweighted** graph or grid
2. Keywords: "minimum number of steps/moves", "shortest distance", "fewest operations"
3. The problem involves **level-order traversal** of a tree
4. Multiple sources start simultaneously (rotting oranges, multi-source fire spread)
5. You need to find **all nodes at distance k** from a source
6. State-space search where each transition has equal cost (combination locks, word transformations)

**When NOT to use it:**
- The graph has **weighted edges** -- use Dijkstra or Bellman-Ford
- You need **all paths** or **all solutions** -- use DFS with backtracking
- You need to detect **cycles** or perform **topological sort** -- DFS is more natural
- Memory is extremely constrained -- BFS queue can be O(width) which may be huge for wide graphs

## Core Mechanics

BFS explores nodes in order of their distance from the source. It uses a **queue (FIFO)** to process nodes level by level. The first time a node is reached, it is reached via the shortest path.

**Why it finds shortest paths:** BFS processes all nodes at distance d before any node at distance d+1. So when we first encounter the target, we have found the shortest path.

**The invariant:** At any point during BFS, the queue contains nodes at distances d and d+1 from the source (for some d). All nodes at distance < d have already been processed.

**Critical rule:** Mark nodes as visited **when they are added to the queue**, not when they are removed. If you mark on removal, the same node can be added to the queue multiple times, wasting time and potentially giving wrong results.

### ASCII Walkthrough (Grid BFS)

```
Find shortest path from S to E in a grid (0=open, 1=wall)

  0 1 2 3
0 S 0 0 0
1 0 1 0 0
2 0 0 0 E

Queue processing (level by level):
Level 0: Process (0,0). Add neighbors (0,1), (1,0).
Level 1: Process (0,1) -> add (0,2). Process (1,0) -> add (2,0).
Level 2: Process (0,2) -> add (0,3). Process (2,0) -> add (2,1).
Level 3: Process (0,3) -> add (1,3? wait, (1,2) first)...
         Process (2,1) -> add (2,2).
Level 4: Process (2,2) -> add (2,3).
         (2,3) is E! Shortest path = 4 steps.
```

## The Template

```python
from collections import deque

def bfs_template(start, is_target, get_neighbors):
    """Generic BFS template."""
    queue = deque([(start, 0)])  # (node, distance)
    visited = {start}

    while queue:
        node, dist = queue.popleft()

        if is_target(node):
            return dist

        for neighbor in get_neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))

    return -1  # target not reachable
```

**Level-order BFS (when you need to process level by level):**
```python
def bfs_level_order(start, get_neighbors):
    queue = deque([start])
    visited = {start}
    level = 0

    while queue:
        level_size = len(queue)
        for _ in range(level_size):
            node = queue.popleft()
            # process node at current level

            for neighbor in get_neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        level += 1
```

```go
func bfsTemplate(start interface{}, isTarget func(interface{}) bool, getNeighbors func(interface{}) []interface{}) int {
	type Item struct {
		node interface{}
		dist int
	}
	queue := []Item{{start, 0}}
	visited := map[interface{}]bool{start: true}

	for len(queue) > 0 {
		item := queue[0]
		queue = queue[1:]

		if isTarget(item.node) {
			return item.dist
		}

		for _, neighbor := range getNeighbors(item.node) {
			if !visited[neighbor] {
				visited[neighbor] = true
				queue = append(queue, Item{neighbor, item.dist + 1})
			}
		}
	}
	return -1
}
```

## Variant Subpatterns

### 1. Standard BFS (Single Source)

Start from one node, explore level by level.

Problems: Binary Tree Level Order Traversal, Shortest Path in Binary Matrix.

### 2. Multi-Source BFS

Start from multiple nodes simultaneously. Add all sources to the queue before starting.

```python
queue = deque()
for source in all_sources:
    queue.append((source, 0))
    visited.add(source)
# Then run standard BFS
```

Problems: Rotting Oranges, 01 Matrix, Walls and Gates.

### 3. State-Space BFS

The "nodes" are not physical locations but abstract states (e.g., a combination on a lock, a set of collected keys). Visited set tracks states, not just positions.

```python
# State = (position, keys_collected)
visited = set()
state = (start_pos, frozenset())
queue = deque([(state, 0)])
```

Problems: Open the Lock, Shortest Path to Get All Keys, Sliding Puzzle.

### 4. Bidirectional BFS

Search from both start and end simultaneously. When the two frontiers meet, you have the shortest path. Reduces search space from O(b^d) to O(b^(d/2)).

```python
front = {start}
back = {end}
steps = 0
while front and back:
    if len(front) > len(back):
        front, back = back, front  # expand smaller set
    next_front = set()
    for node in front:
        for neighbor in get_neighbors(node):
            if neighbor in back:
                return steps + 1
            next_front.add(neighbor)
    front = next_front
    steps += 1
```

Problems: Word Ladder, Minimum Genetic Mutation.

---

## Problem Walkthroughs

---

### Problem: Binary Tree Level Order Traversal (LC #102) — Medium

**Companies:** Meta, Amazon, Google, Microsoft, Bloomberg
**Why it is asked:** The foundational BFS problem on trees. Tests whether you can use a queue and process levels correctly.

**The Brute Force:**
```python
def levelOrder_dfs(root):
    # DFS with level tracking -- works but not the natural BFS approach
    result = []
    def dfs(node, level):
        if not node:
            return
        if level == len(result):
            result.append([])
        result[level].append(node.val)
        dfs(node.left, level + 1)
        dfs(node.right, level + 1)
    dfs(root, 0)
    return result
```

DFS with level tracking works but does not process nodes in level order (it visits the left subtree deeply first). For this specific problem both give the same output, but BFS is the natural fit.

**The Key Insight:** Use a queue. At each iteration, snapshot the queue size (that is the number of nodes at the current level), process exactly that many nodes, and their children form the next level.

**Optimal Solution:**
```python
from collections import deque

def levelOrder(root):
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        level = []
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)

    return result
```

**Dry Run:**
```
Tree:      3
          / \
         9  20
           /  \
          15   7

Queue: [3]
Level 0: process 3 -> add 9, 20. result=[[3]]
Queue: [9, 20]
Level 1: process 9 (no children), process 20 (add 15, 7). result=[[3],[9,20]]
Queue: [15, 7]
Level 2: process 15, process 7. result=[[3],[9,20],[15,7]]
Queue empty, done.
```

**Edge Cases:**
- Empty tree: return [].
- Single node: return [[val]].
- Skewed tree (linked-list shape): each level has one node.

**Complexity:** Time O(n), Space O(w) where w is the max width of the tree (up to n/2 for a complete tree).

**Follow-up questions interviewers might ask:**
- "Can you do zigzag level order?" -- LC #103. Alternate appending left-to-right and right-to-left per level.
- "Can you do bottom-up level order?" -- LC #107. Reverse the result.
- "Can you find the right-side view?" -- LC #199. Take the last element of each level.

---

### Problem: Rotting Oranges (LC #994) — Medium

**Companies:** Amazon, Google, Meta, Microsoft
**Why it is asked:** Tests multi-source BFS. You must recognize that all rotten oranges spread simultaneously (not one at a time).

**The Brute Force:**
```python
def orangesRotting_brute(grid):
    # Simulate minute by minute: O((m*n)^2) worst case
    rows, cols = len(grid), len(grid[0])
    minutes = 0
    changed = True
    while changed:
        changed = False
        new_rotten = []
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 2:
                    for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                            new_rotten.append((nr, nc))
                            changed = True
        for r, c in new_rotten:
            grid[r][c] = 2
        if changed:
            minutes += 1
    return minutes if all(grid[r][c] != 1 for r in range(rows) for c in range(cols)) else -1
```

Simulate each minute by scanning the entire grid. O((m*n)^2) worst case.

**The Key Insight:** Add ALL initially rotten oranges to the queue before starting BFS. This makes them all spread simultaneously. Each "level" of BFS represents one minute.

**Optimal Solution:**
```python
from collections import deque

def orangesRotting(grid):
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c))
            elif grid[r][c] == 1:
                fresh += 1

    if fresh == 0:
        return 0

    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    minutes = 0

    while queue and fresh > 0:
        minutes += 1
        for _ in range(len(queue)):
            r, c = queue.popleft()
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    queue.append((nr, nc))

    return minutes if fresh == 0 else -1
```

**Dry Run:**
```
Input: grid = [[2,1,1],[1,1,0],[0,1,1]]

Initial: queue=[(0,0)], fresh=6

Minute 1: process (0,0) -> rot (0,1) and (1,0). fresh=4
  queue=[(0,1),(1,0)]

Minute 2: process (0,1) -> rot (0,2) and (1,1). Process (1,0) -> (1,1) already rotten. fresh=2
  queue=[(0,2),(1,1)]

Minute 3: process (0,2) -> no fresh neighbors. Process (1,1) -> rot (2,1). fresh=1
  queue=[(2,1)]

Minute 4: process (2,1) -> rot (2,2). fresh=0
  queue=[(2,2)]

fresh==0, return 4
```

**Edge Cases:**
- No fresh oranges: return 0.
- Fresh oranges unreachable (surrounded by empty cells): return -1.
- No rotten oranges but fresh exist: return -1.
- Single cell grid.

**Complexity:** Time O(m * n), Space O(m * n) for the queue.

**Follow-up questions interviewers might ask:**
- "What if rotting spreads in 8 directions?" -- Add 4 diagonal directions.
- "What if some oranges are immune?" -- Skip immune cells in the BFS.
- "Why multi-source BFS and not running BFS from each rotten orange separately?" -- Separate BFS would be O(k * m * n) where k is the number of initially rotten oranges. Multi-source BFS is O(m * n).

---

### Problem: Open the Lock (LC #752) — Medium

**Companies:** Google, Amazon, Meta
**Why it is asked:** Tests state-space BFS where the "graph" is implicit (states are lock combinations, edges are single-digit turns).

**The Brute Force:** There is no natural brute force beyond BFS -- the state space is the graph. A DFS would work but would not give shortest path.

**The Key Insight:** Each lock state is a 4-digit string. From each state, you can reach 8 neighbors (turn each of 4 wheels up or down). BFS from "0000" finds the minimum turns. Deadends are walls in the graph -- add them to the visited set before starting.

**Optimal Solution:**
```python
from collections import deque

def openLock(deadends, target):
    dead = set(deadends)
    if "0000" in dead:
        return -1

    visited = set(dead)  # treat deadends as already visited
    visited.add("0000")
    queue = deque([("0000", 0)])

    while queue:
        state, turns = queue.popleft()

        if state == target:
            return turns

        for i in range(4):
            digit = int(state[i])
            for delta in (-1, 1):
                new_digit = (digit + delta) % 10
                new_state = state[:i] + str(new_digit) + state[i + 1:]
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, turns + 1))

    return -1
```

**Dry Run:**
```
Input: deadends = ["0201","0101","0102","1212","2002"], target = "0202"

Start: "0000", turns=0
  Neighbors: 1000,9000,0100,0900,0010,0090,0001,0009

turns=1: process 1000 -> neighbors include 2000,0000(visited),1100,...
         process 0100 -> neighbors include 0200,0000(visited),...
         (0101 is dead, skip)
         process 0010 -> ...
         ...

turns=2: eventually reach 0200 -> neighbors include 0201(dead), 0209, 0300, 0100(visited), 0210, 0290

... continues until 0202 is reached.

Answer: 6
```

**Edge Cases:**
- "0000" is a deadend: return -1 immediately.
- target is "0000": return 0.
- All paths to target are blocked: return -1.

**Complexity:** Time O(10^4 * 8) = O(1) since the state space is bounded. Space O(10^4) for visited set.

**Follow-up questions interviewers might ask:**
- "Can you use bidirectional BFS?" -- Yes, search from both "0000" and target. Reduces exploration significantly.
- "What if the lock has n wheels instead of 4?" -- State space becomes 10^n, BFS is the same approach but exponentially larger.

---

### Problem: Shortest Path in Binary Matrix (LC #1091) — Medium

**Companies:** Meta, Google, Amazon
**Why it is asked:** Standard grid BFS with 8-directional movement. Tests whether you handle diagonal movement and boundary checks correctly.

**The Brute Force:** DFS exploring all paths would find the shortest, but at O(8^(n^2)) cost. BFS is the only reasonable approach.

**The Key Insight:** Standard BFS on a grid where each cell connects to 8 neighbors (including diagonals). Start from (0,0), target is (n-1,n-1). Mark visited immediately when enqueuing.

**Optimal Solution:**
```python
from collections import deque

def shortestPathBinaryMatrix(grid):
    n = len(grid)
    if grid[0][0] == 1 or grid[n - 1][n - 1] == 1:
        return -1

    directions = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    queue = deque([(0, 0, 1)])  # (row, col, path_length)
    grid[0][0] = 1  # mark visited

    while queue:
        r, c, dist = queue.popleft()

        if r == n - 1 and c == n - 1:
            return dist

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 0:
                grid[nr][nc] = 1  # mark visited
                queue.append((nr, nc, dist + 1))

    return -1
```

**Dry Run:**
```
Input: grid = [[0,1],[1,0]]

Start (0,0), dist=1. Mark visited.
Neighbors: (-1,-1) OOB, (-1,0) OOB, (-1,1) OOB, (0,-1) OOB,
           (0,1) wall, (1,-1) OOB, (1,0) wall, (1,1) = grid[1][1]=0 -> enqueue (1,1,2)

Process (1,1,2): it is the target! Return 2.
```

**Edge Cases:**
- Start or end is blocked (value 1): return -1.
- 1x1 grid with 0: return 1.
- No path exists: return -1.

**Complexity:** Time O(n^2), Space O(n^2).

---

### Problem: Word Ladder (LC #127) — Hard

**Companies:** Amazon, Google, Meta, Microsoft, Uber
**Why it is asked:** Classic BFS on an implicit graph. Nodes are words, edges connect words that differ by one letter. Tests graph construction and optimization skills.

**The Brute Force:**
```python
def ladderLength_brute(beginWord, endWord, wordList):
    # BFS with O(n^2 * m) neighbor check per level
    from collections import deque
    wordSet = set(wordList)
    if endWord not in wordSet:
        return 0

    queue = deque([(beginWord, 1)])
    visited = {beginWord}

    while queue:
        word, length = queue.popleft()
        # Check all words in wordList for one-letter difference
        for candidate in wordList:
            if candidate not in visited:
                diff = sum(1 for a, b in zip(word, candidate) if a != b)
                if diff == 1:
                    if candidate == endWord:
                        return length + 1
                    visited.add(candidate)
                    queue.append((candidate, length + 1))

    return 0
```

Comparing each word with all other words for one-letter difference: O(n * m) per word, total O(n^2 * m). Too slow for large word lists.

**The Key Insight:** Instead of comparing with all words, generate all possible one-letter transformations (26 * m possibilities) and check if each exists in the word set. This is O(26 * m) per word instead of O(n * m). For large n, this is much faster. Bidirectional BFS further speeds it up.

**Optimal Solution:**
```python
from collections import deque

def ladderLength(beginWord, endWord, wordList):
    word_set = set(wordList)
    if endWord not in word_set:
        return 0

    queue = deque([(beginWord, 1)])
    visited = {beginWord}

    while queue:
        word, length = queue.popleft()

        for i in range(len(word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                if c == word[i]:
                    continue
                next_word = word[:i] + c + word[i + 1:]
                if next_word == endWord:
                    return length + 1
                if next_word in word_set and next_word not in visited:
                    visited.add(next_word)
                    queue.append((next_word, length + 1))

    return 0
```

**Bidirectional BFS (optimal):**
```python
def ladderLength_bidirectional(beginWord, endWord, wordList):
    word_set = set(wordList)
    if endWord not in word_set:
        return 0

    front = {beginWord}
    back = {endWord}
    visited = set()
    length = 1

    while front and back:
        # Always expand the smaller frontier
        if len(front) > len(back):
            front, back = back, front

        next_front = set()
        for word in front:
            for i in range(len(word)):
                for c in 'abcdefghijklmnopqrstuvwxyz':
                    next_word = word[:i] + c + word[i + 1:]
                    if next_word in back:
                        return length + 1
                    if next_word in word_set and next_word not in visited:
                        visited.add(next_word)
                        next_front.add(next_word)

        front = next_front
        length += 1

    return 0
```

**Dry Run:**
```
Input: beginWord="hit", endWord="cog", wordList=["hot","dot","dog","lot","log","cog"]

BFS from "hit":
Level 1 (len=1): "hit"
  Neighbors: try all 1-letter changes of "hit"
  "hot" is in wordSet -> enqueue (length=2)

Level 2 (len=2): "hot"
  "dot" -> enqueue (length=3)
  "lot" -> enqueue (length=3)

Level 3 (len=3): "dot", "lot"
  "dot" -> "dog" -> enqueue (length=4)
  "lot" -> "log" -> enqueue (length=4)

Level 4 (len=4): "dog", "log"
  "dog" -> "cog" == endWord! return 5

Answer: 5
```

**Edge Cases:**
- endWord not in wordList: return 0.
- beginWord == endWord: return 1 (or 0 depending on interpretation; LC says 0).
- No transformation sequence exists: return 0.

**Complexity:** Standard BFS: O(n * m * 26) where n = words, m = word length. Bidirectional: O(sqrt(n) * m * 26) in practice.

**Follow-up questions interviewers might ask:**
- "Why bidirectional BFS?" -- Reduces search space exponentially. If BFS explores b^d states (b = branching factor, d = depth), bidirectional explores 2 * b^(d/2).
- "Can you find ALL shortest paths?" -- LC #126 (Word Ladder II). Use BFS to find distances, then DFS/backtrack to reconstruct all shortest paths. Much harder.

---

### Problem: Shortest Path to Get All Keys (LC #864) — Hard

**Companies:** Google, Amazon, Meta
**Why it is asked:** Tests state-space BFS with bitmask state encoding. The state is not just position but (position, keys_collected).

**The Brute Force:** No efficient brute force exists. BFS is the standard approach; the question is how to define the state.

**The Key Insight:** Standard BFS would revisit the same cell but with different keys. The state must include which keys have been collected. Use a bitmask to represent the key set. State = (row, col, keys_bitmask). Visited set stores these tuples.

**Optimal Solution:**
```python
from collections import deque

def shortestPathAllKeys(grid):
    rows, cols = len(grid), len(grid[0])
    total_keys = 0
    start = None

    for r in range(rows):
        for c in range(cols):
            ch = grid[r][c]
            if ch == '@':
                start = (r, c)
            elif 'a' <= ch <= 'f':
                total_keys += 1

    all_keys = (1 << total_keys) - 1  # bitmask with all keys collected

    # State: (row, col, keys_bitmask)
    queue = deque([(start[0], start[1], 0, 0)])  # r, c, keys, steps
    visited = set()
    visited.add((start[0], start[1], 0))

    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while queue:
        r, c, keys, steps = queue.popleft()

        if keys == all_keys:
            return steps

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                ch = grid[nr][nc]
                new_keys = keys

                if ch == '#':  # wall
                    continue
                if 'A' <= ch <= 'F':  # lock
                    key_needed = 1 << (ord(ch) - ord('A'))
                    if not (keys & key_needed):  # don't have the key
                        continue
                if 'a' <= ch <= 'f':  # key
                    new_keys = keys | (1 << (ord(ch) - ord('a')))

                state = (nr, nc, new_keys)
                if state not in visited:
                    visited.add(state)
                    queue.append((nr, nc, new_keys, steps + 1))

    return -1
```

**Dry Run:**
```
Input: grid = ["@.a..","###.#","b.A.B"]

Grid visualization:
  @ . a . .
  # # # . #
  b . A . B

Start at (0,0). Keys: a at (0,2), b at (2,0). total_keys=2, all_keys=0b11=3.

BFS explores with state (row, col, keys):
Step 0: (0,0,0b00)
Step 1: (0,1,0b00) -- moved right
Step 2: (0,2,0b01) -- picked up key 'a' (bit 0)
Step 3: (0,3,0b01), also explore back
...
Eventually reach (2,0) to pick up key 'b':
  Need to go (0,0)->(0,1)->(0,2) pick a, then backtrack down...
  The grid forces specific paths around walls.

When keys == 0b11 == 3, return steps.
```

**Edge Cases:**
- Start already has all keys (total_keys == 0): return 0.
- Some keys are unreachable: return -1.
- Locks without corresponding keys in the grid: those paths are permanently blocked.

**Complexity:** Time O(rows * cols * 2^k) where k = number of keys (up to 6, so 64). Space O(rows * cols * 2^k).

**Follow-up questions interviewers might ask:**
- "Why bitmask instead of a set?" -- Bitmask is hashable and much more efficient. Set would need frozenset, adding overhead.
- "What if there were more than 6 keys?" -- Bitmask still works but state space grows exponentially. For many keys, consider approximation or A* search.
- "Can you use A* instead of BFS?" -- Yes, with a heuristic like Manhattan distance to nearest uncollected key. But BFS is simpler and correct.

---

### Problem: Cut Off Trees for Golf Event (LC #675) — Hard

**Companies:** Amazon (classic Amazon problem)
**Why it is asked:** Tests your ability to decompose a problem: sort the trees by height, then BFS between consecutive trees.

**The Brute Force:** There is no simpler approach than the decomposition + BFS strategy.

**The Key Insight:** You must cut trees in order of ascending height. So sort all trees by height. Then the problem reduces to: find the shortest path from your current position to the next tree, for each consecutive pair. Each shortest path computation is a standard BFS on the grid.

**Optimal Solution:**
```python
from collections import deque

def cutOffTree(forest):
    rows, cols = len(forest), len(forest[0])

    # Collect all trees with height > 1, sorted by height
    trees = []
    for r in range(rows):
        for c in range(cols):
            if forest[r][c] > 1:
                trees.append((forest[r][c], r, c))
    trees.sort()

    def bfs(sr, sc, tr, tc):
        """Shortest path from (sr,sc) to (tr,tc) on the grid."""
        if sr == tr and sc == tc:
            return 0
        visited = set()
        visited.add((sr, sc))
        queue = deque([(sr, sc, 0)])
        directions = [(0,1),(0,-1),(1,0),(-1,0)]

        while queue:
            r, c, dist = queue.popleft()
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if (0 <= nr < rows and 0 <= nc < cols and
                    (nr, nc) not in visited and forest[nr][nc] > 0):
                    if nr == tr and nc == tc:
                        return dist + 1
                    visited.add((nr, nc))
                    queue.append((nr, nc, dist + 1))
        return -1

    total_steps = 0
    cur_r, cur_c = 0, 0

    for height, tr, tc in trees:
        steps = bfs(cur_r, cur_c, tr, tc)
        if steps == -1:
            return -1
        total_steps += steps
        cur_r, cur_c = tr, tc

    return total_steps
```

**Dry Run:**
```
Input: forest = [[1,2,3],[0,0,4],[7,6,5]]

Trees sorted by height: [(2,0,1), (3,0,2), (4,1,2), (5,2,2), (6,2,1), (7,2,0)]

Start at (0,0).
BFS (0,0) -> (0,1): 1 step. total=1
BFS (0,1) -> (0,2): 1 step. total=2
BFS (0,2) -> (1,2): 1 step. total=3
BFS (1,2) -> (2,2): 1 step. total=4
BFS (2,2) -> (2,1): 1 step. total=5
BFS (2,1) -> (2,0): 1 step. total=6

Answer: 6
```

**Edge Cases:**
- Start position (0,0) is 0 (blocked): return -1.
- A tree is unreachable: return -1.
- Single tree: just find path from start to it.
- No trees (all values are 0 or 1): return 0.

**Complexity:** Time O(T * m * n) where T = number of trees. Each BFS is O(m * n). Space O(m * n) for each BFS.

**Follow-up questions interviewers might ask:**
- "Can you optimize the BFS?" -- Use A* with Manhattan distance heuristic for each BFS call. Or use Hadlock's algorithm.
- "Why not a single BFS for the whole problem?" -- Because you must visit trees in a specific order (ascending height).

---

### Problem: Minimum Moves to Reach Target with Rotations (LC #1210) — Hard

**Companies:** Google
**Why it is asked:** Tests BFS with complex state transitions. The snake occupies two cells and can move/rotate in specific ways.

**The Brute Force:** BFS is the only feasible approach. The challenge is defining the state and transitions.

**The Key Insight:** State = (tail_row, tail_col, orientation) where orientation is 0 (horizontal) or 1 (vertical). The snake occupies the tail cell and the cell in the direction of orientation. From each state, you can: move right, move down, or rotate (clockwise/counterclockwise), but only if the destination cells are empty.

**Optimal Solution:**
```python
from collections import deque

def minimumMoves(grid):
    n = len(grid)

    # State: (row, col, direction) where direction 0=horizontal, 1=vertical
    # Horizontal: snake at (r,c) and (r,c+1)
    # Vertical: snake at (r,c) and (r+1,c)

    start = (0, 0, 0)  # horizontal at top-left
    target = (n - 1, n - 2, 0)  # horizontal at bottom-right

    queue = deque([(start, 0)])
    visited = {start}

    while queue:
        (r, c, d), moves = queue.popleft()

        if (r, c, d) == target:
            return moves

        next_states = []

        if d == 0:  # horizontal: snake at (r,c) and (r,c+1)
            # Move right: (r,c+1) and (r,c+2) must be empty
            if c + 2 < n and grid[r][c + 2] == 0:
                next_states.append((r, c + 1, 0))
            # Move down: (r+1,c) and (r+1,c+1) must be empty
            if r + 1 < n and grid[r + 1][c] == 0 and grid[r + 1][c + 1] == 0:
                next_states.append((r + 1, c, 0))
            # Rotate clockwise: become vertical. Need (r+1,c) and (r+1,c+1) empty
            if r + 1 < n and grid[r + 1][c] == 0 and grid[r + 1][c + 1] == 0:
                next_states.append((r, c, 1))
        else:  # vertical: snake at (r,c) and (r+1,c)
            # Move right: (r,c+1) and (r+1,c+1) must be empty
            if c + 1 < n and grid[r][c + 1] == 0 and grid[r + 1][c + 1] == 0:
                next_states.append((r, c + 1, 1))
            # Move down: (r+2,c) must be empty
            if r + 2 < n and grid[r + 2][c] == 0:
                next_states.append((r + 1, c, 1))
            # Rotate counterclockwise: become horizontal. Need (r,c+1) and (r+1,c+1) empty
            if c + 1 < n and grid[r][c + 1] == 0 and grid[r + 1][c + 1] == 0:
                next_states.append((r, c, 0))

        for state in next_states:
            if state not in visited:
                visited.add(state)
                queue.append((state, moves + 1))

    return -1
```

**Dry Run:**
```
Input: grid = [[0,0,0,0,0,1],
               [1,1,0,0,1,0],
               [0,0,0,0,1,1],
               [0,0,1,0,1,0],
               [0,1,1,0,0,0],
               [0,1,1,0,0,0]]

Start: (0,0,0) = horizontal at (0,0)-(0,1)
Target: (5,4,0) = horizontal at (5,4)-(5,5)

BFS explores states (row, col, direction) with 3 possible moves each.
The solution requires a specific sequence of moves and rotations to navigate
around the obstacles.

Answer: 11
```

**Edge Cases:**
- Start or target blocked: return -1.
- 2x2 grid: limited moves.
- No rotations needed: straight path.

**Complexity:** Time O(n^2), Space O(n^2). Each cell has 2 possible states (horizontal/vertical), so total states = 2 * n^2.

---

## Common Mistakes and Interview Tips

### Top 5 Mistakes

1. **Marking visited on dequeue instead of enqueue:** This causes duplicate processing and sometimes wrong shortest path. ALWAYS mark visited when you ADD to the queue.

2. **Using a list as a queue:** `list.pop(0)` is O(n). Use `collections.deque` with `popleft()` for O(1).

3. **Forgetting boundary checks in grid BFS:** Always check `0 <= nr < rows and 0 <= nc < cols` BEFORE accessing `grid[nr][nc]`.

4. **Not handling the "no path" case:** Always check if BFS completes without finding the target and return -1.

5. **Incorrect state representation in state-space BFS:** For problems like "Shortest Path to Get All Keys," the state must include ALL relevant information (position + keys). Using just position causes incorrect results.

### How to Recognize This Pattern in 30 Seconds

Ask: "Am I looking for the shortest path in an unweighted graph?" or "Do I need to process things level by level?" If yes, BFS.

### What Senior/Staff Interviewers Look For

- **Correct state definition** for state-space BFS problems. Can you identify what information defines a unique state?
- **Multi-source BFS** when multiple entities start simultaneously.
- **Bidirectional BFS** optimization for Word Ladder type problems.
- **Complexity analysis** that accounts for the state space size, not just graph size.

### Communication Tips

1. Identify the graph: "The nodes are X, the edges connect states that differ by Y."
2. State the BFS variant: "This is multi-source BFS / state-space BFS / bidirectional BFS."
3. Define the state tuple: "My state is (row, col, keys_bitmask)."
4. Walk through one level of BFS showing the queue state.
5. Discuss optimizations if time permits (bidirectional, A*).

## Pattern Connections

- **BFS** finds shortest paths in unweighted graphs; **Dijkstra's** extends this to weighted graphs.
- **Multi-source BFS** is equivalent to adding a virtual source node connected to all real sources with weight 0.
- **BFS on trees** gives level-order traversal; **DFS on trees** gives pre/in/post-order traversals.
- **State-space BFS** connects to **dynamic programming** -- both explore states, but DP uses optimal substructure while BFS uses shortest-path property.
- **Bidirectional BFS** connects to **meet-in-the-middle** techniques used in combinatorics.
- When edges have weights 0 and 1, use **0-1 BFS** with a deque (weight-0 edges add to front, weight-1 edges add to back).
