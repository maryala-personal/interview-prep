"""Patterns 13-18: backtracking, graph traversal, topological sort, union-find,
shortest paths, tries."""

BACKTRACKING = {
    "id": "backtracking",
    "nav": "Backtracking",
    "title": "Backtracking",
    "tagline": "Build a candidate one choice at a time; undo the choice and try the next one.",
    "plain": """
<p>Backtracking is organized trial and error. You make a choice, go deeper, and when you hit a dead end (or finish a solution), you <b>undo the last choice</b> and try the next option. It explores a tree of decisions.</p>
<p>Every backtracking solution answers three questions:</p>
<ul>
<li><b>What's my current state?</b> Usually a <code>path</code> list of choices so far.</li>
<li><b>What choices can I make next?</b> The loop inside the function.</li>
<li><b>When do I stop?</b> A complete solution (record it) or an impossible one (prune, return early).</li>
</ul>
<p>Pruning is where you win time: skip a branch as soon as you know it can't work.</p>
<div class="analogy"><b>Picture it:</b> walking through a maze with a piece of chalk. At every fork you pick a path. At a dead end you walk back to the last fork and try the next path you haven't taken.</div>
""",
    "signals": [
        "\"Return <b>all</b> subsets / permutations / combinations / partitions\"",
        "Puzzles: N-Queens, Sudoku, word search in a grid",
        "n is small (usually ≤ 15 or 20)",
        "Generate every valid string (parentheses, IP addresses)",
    ],
    "pitfalls": [
        "Appending <code>path</code> itself instead of a copy <code>path[:]</code>. All results end up as the same empty list",
        "Forgetting to undo (pop, unmark visited) after the recursive call",
        "Duplicates in the output when the input has duplicates. Sort, then skip <code>nums[i] == nums[i-1]</code> at the same depth",
    ],
    "template": '''
def backtrack_template(choices: list[int]) -> list[list[int]]:
    results = []
    path = []

    def backtrack(start: int) -> None:
        results.append(path[:])            # record a COPY (here: every node)
        for i in range(start, len(choices)):
            path.append(choices[i])        # choose
            backtrack(i + 1)               # explore
            path.pop()                     # un-choose

    backtrack(0)
    return results

assert len(backtrack_template([1, 2, 3])) == 8
''',
    "complexity": "Exponential: roughly (number of solutions) × (cost to build one). Subsets: O(n · 2ⁿ). Permutations: O(n · n!).",
    "problems": [
        {
            "name": "Subsets",
            "lc": 78,
            "level": "M",
            "prompt": "<p>Return all subsets of a list of distinct integers.</p><pre>[1,2,3]  →  [[],[1],[1,2],[1,2,3],[1,3],[2],[2,3],[3]]</pre>",
            "hint": "Each element is either in or out.",
            "idea": "<p>Use the template: every node of the decision tree is a subset, so record the path on entry. Starting the loop at <code>start</code> means we only move forward, so <code>[1,2]</code> and <code>[2,1]</code> aren't both produced. A neat non-recursive alternative: start with <code>[[]]</code> and for each number, add it to every existing subset.</p>",
            "code": '''
def subsets(nums: list[int]) -> list[list[int]]:
    out, path = [], []
    def backtrack(start):
        out.append(path[:])
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1)
            path.pop()
    backtrack(0)
    return out

def subsets_iterative(nums: list[int]) -> list[list[int]]:
    out = [[]]
    for x in nums:
        out += [s + [x] for s in out]
    return out

assert subsets([1, 2, 3]) == [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
assert sorted(map(sorted, subsets_iterative([1, 2, 3]))) == sorted(map(sorted, subsets([1, 2, 3])))
''',
            "complexity": "O(n · 2ⁿ) time and space.",
            "followups": ["With duplicates (LC 90): sort, and skip <code>nums[i] == nums[i-1]</code> when <code>i &gt; start</code>."],
        },
        {
            "name": "Permutations",
            "lc": 46,
            "level": "M",
            "prompt": "<p>Return all orderings of a list of distinct integers.</p>",
            "hint": "At each position, try every number not used yet.",
            "idea": "<p>The path grows one position at a time. At each step, try every unused number, marking it used before recursing and unmarking after. When the path is full, record it.</p>",
            "code": '''
def permute(nums: list[int]) -> list[list[int]]:
    out, path = [], []
    used = [False] * len(nums)
    def backtrack():
        if len(path) == len(nums):
            out.append(path[:])
            return
        for i, x in enumerate(nums):
            if used[i]:
                continue
            used[i] = True
            path.append(x)
            backtrack()
            path.pop()
            used[i] = False
    backtrack()
    return out

assert permute([1, 2, 3]) == [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
assert permute([1]) == [[1]]
''',
            "complexity": "O(n · n!) time.",
        },
        {
            "name": "Combination Sum",
            "lc": 39,
            "level": "M",
            "prompt": "<p>Distinct positive candidates; each may be used unlimited times. Return all unique combinations that sum to <code>target</code>.</p><pre>[2,3,6,7], 7  →  [[2,2,3],[7]]</pre>",
            "hint": "Pass <code>i</code> (not <code>i + 1</code>) when recursing, so the same number can be reused.",
            "idea": "<p>Like Subsets, but track the remaining amount. Recurse with the same start index to allow reuse. Sort first so you can stop the loop as soon as a candidate is larger than what remains (pruning).</p>",
            "code": '''
def combination_sum(candidates: list[int], target: int) -> list[list[int]]:
    candidates = sorted(candidates)
    out, path = [], []
    def backtrack(start, remaining):
        if remaining == 0:
            out.append(path[:])
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remaining:
                break                     # sorted: everything after is bigger too
            path.append(c)
            backtrack(i, remaining - c)   # i, not i + 1: reuse allowed
            path.pop()
    backtrack(0, target)
    return out

assert combination_sum([2, 3, 6, 7], 7) == [[2, 2, 3], [7]]
assert combination_sum([2, 3, 5], 8) == [[2, 2, 2, 2], [2, 3, 3], [3, 5]]
assert combination_sum([2], 1) == []
''',
            "complexity": "Exponential; bounded by O(n^(target / min)).",
        },
        {
            "name": "Generate Parentheses",
            "lc": 22,
            "level": "M",
            "hot": True,
            "prompt": "<p>Generate every valid string of <code>n</code> pairs of parentheses.</p><pre>n = 3  →  [\"((()))\",\"(()())\",\"(())()\",\"()(())\",\"()()()\"]</pre>",
            "hint": "You may add '(' while you have some left; you may add ')' only if it closes an open one.",
            "idea": "<p>Track how many opens and closes you've used. Add <code>(</code> if <code>opens &lt; n</code>. Add <code>)</code> if <code>closes &lt; opens</code>. These two rules only ever build valid strings, so there's nothing to filter afterwards.</p>",
            "code": '''
def generate_parenthesis(n: int) -> list[str]:
    out, path = [], []
    def backtrack(opens, closes):
        if len(path) == 2 * n:
            out.append("".join(path))
            return
        if opens < n:
            path.append("(")
            backtrack(opens + 1, closes)
            path.pop()
        if closes < opens:
            path.append(")")
            backtrack(opens, closes + 1)
            path.pop()
    backtrack(0, 0)
    return out

assert generate_parenthesis(3) == ["((()))", "(()())", "(())()", "()(())", "()()()"]
assert generate_parenthesis(1) == ["()"]
''',
            "complexity": "O(4ⁿ / √n) results (the Catalan numbers), each of length 2n.",
        },
        {
            "name": "Word Search",
            "lc": 79,
            "level": "M",
            "hot": True,
            "prompt": "<p>Does the word exist in the grid, built from horizontally or vertically adjacent cells, each used at most once?</p><pre>board = [[\"A\",\"B\",\"C\",\"E\"],\n         [\"S\",\"F\",\"C\",\"S\"],\n         [\"A\",\"D\",\"E\",\"E\"]]\n\"ABCCED\" → True,  \"ABCB\" → False</pre>",
            "hint": "DFS from every cell. Temporarily mark the cell as used, and restore it on the way back.",
            "idea": "<p>Try every cell as a start. DFS matches one letter at a time. To stop reusing a cell, overwrite it with <code>#</code> while it's on the current path and put the letter back afterwards. Returning as soon as the letter doesn't match prunes most branches.</p>",
            "code": '''
def exist(board: list[list[str]], word: str) -> bool:
    rows, cols = len(board), len(board[0])
    def dfs(r, c, i) -> bool:
        if i == len(word):
            return True
        if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[i]:
            return False
        saved, board[r][c] = board[r][c], "#"          # mark used
        found = (dfs(r + 1, c, i + 1) or dfs(r - 1, c, i + 1) or
                 dfs(r, c + 1, i + 1) or dfs(r, c - 1, i + 1))
        board[r][c] = saved                            # restore
        return found
    return any(dfs(r, c, 0) for r in range(rows) for c in range(cols))

board = [["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]]
assert exist(board, "ABCCED")
assert exist(board, "SEE")
assert not exist(board, "ABCB")
''',
            "complexity": "O(rows · cols · 3^L) time for word length L, O(L) stack.",
            "followups": ["Many words at once: Word Search II in the Tries section."],
        },
        {
            "name": "N-Queens",
            "lc": 51,
            "level": "H",
            "prompt": "<p>Place n queens on an n × n board so no two attack each other. Return all boards.</p><pre>n = 4  →  [[\".Q..\",\"...Q\",\"Q...\",\"..Q.\"], [\"..Q.\",\"Q...\",\"...Q\",\".Q..\"]]</pre>",
            "hint": "One queen per row. Track used columns and both diagonals in sets.",
            "idea": "<p>Place one queen per row, trying each column. A square <code>(r, c)</code> is attacked if its column is taken, or its <code>r − c</code> diagonal, or its <code>r + c</code> anti-diagonal. Three sets give O(1) checks. Add on the way in, remove on the way out.</p>",
            "code": '''
def solve_n_queens(n: int) -> list[list[str]]:
    out = []
    queens = []                                   # queens[r] = column in row r
    cols, diag, anti = set(), set(), set()
    def place(r):
        if r == n:
            out.append(["." * c + "Q" + "." * (n - c - 1) for c in queens])
            return
        for c in range(n):
            if c in cols or r - c in diag or r + c in anti:
                continue
            queens.append(c); cols.add(c); diag.add(r - c); anti.add(r + c)
            place(r + 1)
            queens.pop(); cols.remove(c); diag.remove(r - c); anti.remove(r + c)
    place(0)
    return out

assert solve_n_queens(4) == [[".Q..", "...Q", "Q...", "..Q."], ["..Q.", "Q...", "...Q", ".Q.."]]
assert solve_n_queens(1) == [["Q"]]
assert len(solve_n_queens(8)) == 92
''',
            "complexity": "O(n!) time in the worst case, O(n) extra space.",
        },
    ],
}

GRAPHS = {
    "id": "graphs",
    "nav": "Graphs: BFS and DFS",
    "title": "Graphs and grids: BFS and DFS",
    "tagline": "Google's favorite topic. Things connected to things; walk them without visiting anything twice.",
    "plain": """
<p>A graph is a set of <b>nodes</b> (people, cities, cells) and <b>edges</b> (friendships, roads, \"is next to\"). Many Google questions are graphs in disguise: a grid is a graph where each cell connects to its 4 neighbors; words that differ by one letter form a graph; tasks with dependencies form a graph.</p>
<p>Store a graph as an <b>adjacency list</b>: a dict from each node to its neighbors. Then pick a walk:</p>
<ul>
<li><b>BFS</b> (queue) explores in rings of distance 1, then 2, then 3. Use it for <b>shortest path when every step costs the same</b>.</li>
<li><b>DFS</b> (recursion or stack) goes as deep as possible first. Use it to explore everything connected, count components, or detect cycles.</li>
</ul>
<p>Both need a <code>visited</code> set so you never process a node twice. Mark a node visited <b>when you add it to the queue</b>, not when you pop it, or the same node can be added many times.</p>
<div class="analogy"><b>Picture it:</b> BFS is a stone dropped in a pond: ripples reach nearby spots first. DFS is exploring a cave: follow one tunnel to its end before backing up.</div>
""",
    "signals": [
        "A 2D grid of cells: islands, mazes, rooms, oranges, flood fill",
        "\"Minimum number of steps / moves / transformations\" → BFS",
        "Connections, networks, friends, \"reachable from\"",
        "Words or states that change one small step at a time",
        "Several starting points at once → multi-source BFS",
    ],
    "pitfalls": [
        "Marking visited when popping instead of when pushing (queue blows up)",
        "Using DFS when the question wants the shortest path (DFS doesn't find it)",
        "Using <code>list.pop(0)</code> as a queue (O(n)). Use <code>deque.popleft()</code>",
        "Forgetting the state includes more than the position (keys held, obstacles removed, …)",
        "Recursion depth errors on big grids. Mention the iterative version",
    ],
    "template": '''
from collections import defaultdict, deque

def build_graph(edges, directed=False):
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        if not directed:
            graph[v].append(u)
    return graph

def bfs_distance(graph, start, goal) -> int:
    """Fewest edges from start to goal, or -1."""
    queue = deque([(start, 0)])
    visited = {start}
    while queue:
        node, dist = queue.popleft()
        if node == goal:
            return dist
        for nxt in graph[node]:
            if nxt not in visited:
                visited.add(nxt)             # mark when pushing
                queue.append((nxt, dist + 1))
    return -1

DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

def grid_neighbors(grid, r, c):
    for dr, dc in DIRS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
            yield nr, nc

g = build_graph([(1, 2), (2, 3), (3, 4), (1, 5)])
assert bfs_distance(g, 1, 4) == 3
assert list(grid_neighbors([[0, 0], [0, 0]], 0, 0)) == [(1, 0), (0, 1)]
''',
    "complexity": "O(V + E) time, O(V) space. On a grid: O(rows · cols).",
    "problems": [
        {
            "name": "Flood Fill",
            "lc": 733,
            "level": "E",
            "prompt": "<p>Starting from pixel <code>(sr, sc)</code>, recolor it and every connected pixel of the same original color.</p>",
            "hint": "Watch out when the new color equals the old color.",
            "idea": "<p>DFS from the start. Recolor each cell that has the original color and spread to its 4 neighbors. Recoloring doubles as marking visited. If the new color equals the old one, return immediately, or the search never ends.</p>",
            "code": '''
def flood_fill(image: list[list[int]], sr: int, sc: int, color: int) -> list[list[int]]:
    old = image[sr][sc]
    if old == color:
        return image
    rows, cols = len(image), len(image[0])
    stack = [(sr, sc)]
    image[sr][sc] = color
    while stack:
        r, c = stack.pop()
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols and image[nr][nc] == old:
                image[nr][nc] = color
                stack.append((nr, nc))
    return image

assert flood_fill([[1, 1, 1], [1, 1, 0], [1, 0, 1]], 1, 1, 2) == [[2, 2, 2], [2, 2, 0], [2, 0, 1]]
assert flood_fill([[0, 0], [0, 0]], 0, 0, 0) == [[0, 0], [0, 0]]
''',
            "complexity": "O(rows · cols) time and space.",
        },
        {
            "name": "Number of Islands",
            "lc": 200,
            "level": "M",
            "hot": True,
            "prompt": "<p>In a grid of '1' (land) and '0' (water), count the islands (groups of land connected up, down, left, right).</p>",
            "hint": "Each time you find unvisited land, that's a new island. Sink the whole island so you don't count it again.",
            "idea": "<p>Scan every cell. When you hit a '1', count one island and run BFS/DFS from it to turn all its connected land into '0'. Every cell is visited a constant number of times.</p>",
            "code": '''
from collections import deque

def num_islands(grid: list[list[str]]) -> int:
    rows, cols = len(grid), len(grid[0])
    islands = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != "1":
                continue
            islands += 1
            grid[r][c] = "0"
            queue = deque([(r, c)])
            while queue:
                cr, cc = queue.popleft()
                for nr, nc in ((cr + 1, cc), (cr - 1, cc), (cr, cc + 1), (cr, cc - 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "1":
                        grid[nr][nc] = "0"
                        queue.append((nr, nc))
    return islands

g = [list("11000"), list("11000"), list("00100"), list("00011")]
assert num_islands(g) == 3
assert num_islands([list("111"), list("010"), list("111")]) == 1
''',
            "complexity": "O(rows · cols) time, O(min(rows, cols)) queue space for BFS.",
            "followups": ["Don't modify the input: use a visited set.", "Land is added one cell at a time: Number of Islands II (union-find section).", "Count distinct island shapes (LC 694): record each island's cell offsets from its first cell."],
        },
        {
            "name": "Rotting Oranges",
            "lc": 994,
            "level": "M",
            "hot": True,
            "prompt": "<p>0 = empty, 1 = fresh orange, 2 = rotten. Each minute, rotten oranges rot their 4 neighbors. Minutes until none are fresh, or −1.</p><pre>[[2,1,1],[1,1,0],[0,1,1]]  →  4</pre>",
            "hint": "All rotten oranges spread at the same time. Put all of them in the queue at the start.",
            "idea": "<p><b>Multi-source BFS</b>: start the queue with every rotten orange at time 0. Each BFS level is one minute. Count fresh oranges up front and decrease as they rot. If some are still fresh at the end, return −1.</p>",
            "code": '''
from collections import deque

def oranges_rotting(grid: list[list[int]]) -> int:
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c))
            elif grid[r][c] == 1:
                fresh += 1
    minutes = 0
    while queue and fresh:
        minutes += 1
        for _ in range(len(queue)):               # one minute = one level
            r, c = queue.popleft()
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    queue.append((nr, nc))
    return minutes if fresh == 0 else -1

assert oranges_rotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]]) == 4
assert oranges_rotting([[2, 1, 1], [0, 1, 1], [1, 0, 1]]) == -1
assert oranges_rotting([[0, 2]]) == 0
''',
            "complexity": "O(rows · cols) time and space.",
        },
        {
            "name": "Clone Graph",
            "lc": 133,
            "level": "M",
            "prompt": "<p>Return a deep copy of a connected undirected graph given one of its nodes.</p>",
            "hint": "Keep a map from original node to its copy. It also serves as the visited set.",
            "idea": "<p>DFS or BFS through the original. The first time you see a node, create its copy and store it in <code>copies</code>. For each neighbor, make sure it has a copy, then link the copies. The map stops infinite loops on cycles.</p>",
            "code": '''
class Node:
    def __init__(self, val, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

def clone_graph(node):
    if not node:
        return None
    copies = {node: Node(node.val)}
    stack = [node]
    while stack:
        cur = stack.pop()
        for nb in cur.neighbors:
            if nb not in copies:
                copies[nb] = Node(nb.val)
                stack.append(nb)
            copies[cur].neighbors.append(copies[nb])
    return copies[node]

# square: 1-2-3-4-1
n1, n2, n3, n4 = Node(1), Node(2), Node(3), Node(4)
n1.neighbors = [n2, n4]; n2.neighbors = [n1, n3]
n3.neighbors = [n2, n4]; n4.neighbors = [n3, n1]
c1 = clone_graph(n1)
assert c1 is not n1 and c1.val == 1
assert [n.val for n in c1.neighbors] == [2, 4]
assert c1.neighbors[0].neighbors[1].val == 3 and c1.neighbors[0] is not n2
''',
            "complexity": "O(V + E) time and space.",
        },
        {
            "name": "Word Ladder",
            "lc": 127,
            "level": "H",
            "hot": True,
            "prompt": "<p>Transform <code>begin</code> into <code>end</code> changing one letter at a time, every intermediate word in <code>word_list</code>. Return the number of words in the shortest sequence, or 0.</p><pre>\"hit\" → \"cog\", [\"hot\",\"dot\",\"dog\",\"lot\",\"log\",\"cog\"]  →  5\n(hit → hot → dot → dog → cog)</pre>",
            "hint": "Words are nodes; one-letter changes are edges. Shortest path with equal costs means BFS. How do you find neighbors fast?",
            "idea": "<p>BFS from <code>begin</code>. Finding neighbors by comparing against every word is O(n · L) per word. Faster: group words by wildcard patterns, e.g. <code>hot</code> belongs to <code>*ot</code>, <code>h*t</code>, <code>ho*</code>. Two words are neighbors if they share a pattern. After using a pattern, clear it so you don't scan it again.</p>",
            "code": '''
from collections import defaultdict, deque

def ladder_length(begin: str, end: str, word_list: list[str]) -> int:
    words = set(word_list)
    if end not in words:
        return 0
    L = len(begin)
    patterns = defaultdict(list)
    for w in words:
        for i in range(L):
            patterns[w[:i] + "*" + w[i + 1:]].append(w)
    queue = deque([(begin, 1)])
    visited = {begin}
    while queue:
        word, steps = queue.popleft()
        if word == end:
            return steps
        for i in range(L):
            key = word[:i] + "*" + word[i + 1:]
            for nxt in patterns[key]:
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, steps + 1))
            patterns[key] = []            # every word here is already queued
    return 0

assert ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]) == 5
assert ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0
''',
            "complexity": "O(n · L²) time (building each pattern costs L), O(n · L²) space.",
            "followups": ["Bidirectional BFS: search from both ends and stop when they meet; much faster in practice.", "Return all shortest sequences (Word Ladder II, LC 126): BFS records parents, then backtrack."],
        },
        {
            "name": "Shortest Path in a Grid with Obstacles Elimination",
            "lc": 1293,
            "level": "H",
            "hot": True,
            "prompt": "<p>Grid of 0 (open) and 1 (wall). You may remove up to <code>k</code> walls. Return the fewest steps from top-left to bottom-right, or −1.</p><pre>[[0,0,0],[1,1,0],[0,0,0],[0,1,1],[0,0,0]], k = 1  →  6</pre>",
            "hint": "Your position alone isn't the full state. What else changes as you move?",
            "idea": "<p>The state is <code>(row, col, walls_left)</code>. BFS over states gives the fewest steps. Visiting the same cell with more walls left is strictly better, so remember the best <code>walls_left</code> seen per cell and skip worse visits. Shortcut: if <code>k ≥ rows + cols − 2</code>, walk straight there. This \"position plus extra info\" state is a very common Google twist.</p>",
            "code": '''
from collections import deque

def shortest_path(grid: list[list[int]], k: int) -> int:
    rows, cols = len(grid), len(grid[0])
    if k >= rows + cols - 2:
        return rows + cols - 2                     # can bulldoze a straight path
    best_left = [[-1] * cols for _ in range(rows)]  # most walls-left seen per cell
    best_left[0][0] = k
    queue = deque([(0, 0, k, 0)])
    while queue:
        r, c, left, steps = queue.popleft()
        if (r, c) == (rows - 1, cols - 1):
            return steps
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols:
                nleft = left - grid[nr][nc]
                if nleft > best_left[nr][nc]:
                    best_left[nr][nc] = nleft
                    queue.append((nr, nc, nleft, steps + 1))
    return -1

assert shortest_path([[0, 0, 0], [1, 1, 0], [0, 0, 0], [0, 1, 1], [0, 0, 0]], 1) == 6
assert shortest_path([[0, 1, 1], [1, 1, 1], [1, 0, 0]], 1) == -1
assert shortest_path([[0]], 0) == 0
''',
            "complexity": "O(rows · cols · k) time and space.",
        },
    ],
}

TOPO = {
    "id": "topological-sort",
    "nav": "Topological sort",
    "title": "Topological sort",
    "tagline": "Order tasks so every task comes after the tasks it depends on.",
    "plain": """
<p>When things depend on other things (courses with prerequisites, build steps, spreadsheet cells), you need an order where every item comes after everything it depends on. That order is a <b>topological order</b>. It exists only if there's no cycle: if A needs B and B needs A, nothing can go first.</p>
<p><b>Kahn's algorithm</b> is the easiest version to get right in an interview:</p>
<ol>
<li>Count each node's <b>in-degree</b>: how many unmet dependencies it has.</li>
<li>Put every node with in-degree 0 in a queue. They're ready now.</li>
<li>Pop a node, add it to the order, and \"complete\" it: decrease the in-degree of each node that depended on it. Any that hit 0 join the queue.</li>
<li>If the order has fewer nodes than the graph, there was a cycle.</li>
</ol>
<div class="analogy"><b>Picture it:</b> getting dressed. Socks before shoes, underwear before trousers, trousers before shoes. At each moment you put on anything whose \"before\" items are already on.</div>
""",
    "signals": [
        "Prerequisites, dependencies, \"must happen before\"",
        "Build order, course schedule, task ordering",
        "Detect a cycle in a <b>directed</b> graph",
        "Derive an ordering from examples (alien dictionary)",
        "Longest path in a DAG (process in topological order)",
    ],
    "pitfalls": [
        "Getting the edge direction backwards. Say it out loud: \"to take 1 you need 0, so the edge is 0 → 1\"",
        "Forgetting nodes that have no edges at all",
        "Returning a partial order without checking for a cycle",
    ],
    "template": '''
from collections import defaultdict, deque

def topo_sort(n: int, edges: list[tuple[int, int]]) -> list[int]:
    """edges are (before, after). Returns [] if there is a cycle."""
    graph = defaultdict(list)
    indegree = [0] * n
    for before, after in edges:
        graph[before].append(after)
        indegree[after] += 1
    queue = deque(i for i in range(n) if indegree[i] == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return order if len(order) == n else []

assert topo_sort(3, [(0, 1), (1, 2)]) == [0, 1, 2]
assert topo_sort(2, [(0, 1), (1, 0)]) == []
''',
    "complexity": "O(V + E) time and space.",
    "problems": [
        {
            "name": "Find the Town Judge",
            "lc": 997,
            "level": "E",
            "prompt": "<p>In a town of n people, <code>trust[i] = [a, b]</code> means a trusts b. The judge trusts nobody and is trusted by everyone else. Return the judge's label or −1.</p>",
            "hint": "Think in terms of in-degree and out-degree.",
            "idea": "<p>The judge has in-degree n − 1 and out-degree 0. Keep one score per person: +1 for being trusted, −1 for trusting someone. The judge is the only person who can reach n − 1.</p>",
            "code": '''
def find_judge(n: int, trust: list[list[int]]) -> int:
    score = [0] * (n + 1)
    for a, b in trust:
        score[a] -= 1
        score[b] += 1
    for person in range(1, n + 1):
        if score[person] == n - 1:
            return person
    return -1

assert find_judge(2, [[1, 2]]) == 2
assert find_judge(3, [[1, 3], [2, 3]]) == 3
assert find_judge(3, [[1, 3], [2, 3], [3, 1]]) == -1
assert find_judge(1, []) == 1
''',
            "complexity": "O(n + trust) time, O(n) space.",
        },
        {
            "name": "Course Schedule",
            "lc": 207,
            "level": "M",
            "hot": True,
            "prompt": "<p><code>prerequisites[i] = [a, b]</code> means take b before a. Can you finish all <code>n</code> courses?</p><pre>n = 2, [[1,0],[0,1]]  →  False</pre>",
            "hint": "You can finish them all exactly when there's no cycle.",
            "idea": "<p>Run Kahn's algorithm. If every course gets processed, there's no cycle. The edge for <code>[a, b]</code> goes from b to a.</p>",
            "code": '''
from collections import deque

def can_finish(n: int, prerequisites: list[list[int]]) -> bool:
    after = [[] for _ in range(n)]
    indegree = [0] * n
    for course, pre in prerequisites:
        after[pre].append(course)
        indegree[course] += 1
    queue = deque(i for i in range(n) if indegree[i] == 0)
    taken = 0
    while queue:
        c = queue.popleft()
        taken += 1
        for nxt in after[c]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return taken == n

assert can_finish(2, [[1, 0]])
assert not can_finish(2, [[1, 0], [0, 1]])
assert can_finish(3, [])
''',
            "complexity": "O(V + E) time and space.",
        },
        {
            "name": "Course Schedule II",
            "lc": 210,
            "level": "M",
            "prompt": "<p>Same setup; return one valid order to take all courses, or [] if impossible.</p>",
            "hint": "Record the order Kahn's algorithm pops things.",
            "idea": "<p>Identical to Course Schedule, but keep the list of popped courses. For a DFS alternative: a node is added after all its descendants finish; reverse that list. Track three colors (unvisited, in progress, done) to detect cycles.</p>",
            "code": '''
def find_order(n: int, prerequisites: list[list[int]]) -> list[int]:
    """DFS version with three colors, to show the alternative."""
    after = [[] for _ in range(n)]
    for course, pre in prerequisites:
        after[pre].append(course)
    WHITE, GRAY, BLACK = 0, 1, 2            # unvisited, on the stack, finished
    color = [WHITE] * n
    order = []
    def dfs(u) -> bool:                     # False if a cycle is found
        color[u] = GRAY
        for v in after[u]:
            if color[v] == GRAY:
                return False
            if color[v] == WHITE and not dfs(v):
                return False
        color[u] = BLACK
        order.append(u)                     # all dependents are done
        return True
    for u in range(n):
        if color[u] == WHITE and not dfs(u):
            return []
    return order[::-1]

def is_valid_order(order, prerequisites):
    pos = {c: i for i, c in enumerate(order)}
    return all(pos[pre] < pos[c] for c, pre in prerequisites)

res = find_order(4, [[1, 0], [2, 0], [3, 1], [3, 2]])
assert len(res) == 4 and is_valid_order(res, [[1, 0], [2, 0], [3, 1], [3, 2]])
assert find_order(2, [[1, 0], [0, 1]]) == []
''',
            "complexity": "O(V + E) time and space.",
        },
        {
            "name": "Alien Dictionary",
            "lc": 269,
            "level": "H",
            "hot": True,
            "prompt": "<p>Words from an alien language are sorted by its alphabet. Return any valid letter order, or \"\" if the input is contradictory.</p><pre>[\"wrt\",\"wrf\",\"er\",\"ett\",\"rftt\"]  →  \"wertf\"</pre>",
            "hint": "Compare each pair of neighboring words. The first differing letter gives you one rule.",
            "idea": "<p>Each adjacent pair of words tells you one fact: at the first position they differ, the first word's letter comes before the second's. Build a graph of those facts over all letters that appear, then topologically sort. Two traps: a word followed by its own prefix (<code>\"abc\"</code> before <code>\"ab\"</code>) is invalid, and a cycle means no valid order.</p>",
            "code": '''
from collections import deque

def alien_order(words: list[str]) -> str:
    graph = {ch: set() for w in words for ch in w}
    indegree = {ch: 0 for ch in graph}
    for w1, w2 in zip(words, words[1:]):
        for a, b in zip(w1, w2):
            if a != b:
                if b not in graph[a]:
                    graph[a].add(b)
                    indegree[b] += 1
                break
        else:                                   # no difference found
            if len(w1) > len(w2):
                return ""                       # "abc" before "ab" is invalid
    queue = deque(ch for ch in graph if indegree[ch] == 0)
    order = []
    while queue:
        ch = queue.popleft()
        order.append(ch)
        for nxt in graph[ch]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return "".join(order) if len(order) == len(graph) else ""

assert alien_order(["wrt", "wrf", "er", "ett", "rftt"]) == "wertf"
assert alien_order(["z", "x"]) == "zx"
assert alien_order(["z", "x", "z"]) == ""
assert alien_order(["abc", "ab"]) == ""
''',
            "complexity": "O(total characters) time, O(unique letters²) space for edges.",
        },
    ],
}

UNION_FIND = {
    "id": "union-find",
    "nav": "Union-find",
    "title": "Union-find (disjoint set union)",
    "tagline": "Keep track of which items are in the same group while groups keep merging.",
    "plain": """
<p>Union-find answers two questions very fast: <b>\"are these two in the same group?\"</b> (<code>find</code>) and <b>\"merge these two groups\"</b> (<code>union</code>). Each group has one representative, its \"root\". Two items are in the same group if they have the same root.</p>
<p>Two small tricks make both operations almost O(1):</p>
<ul>
<li><b>Path compression:</b> after finding a root, point everything you passed directly at it, so the next lookup is instant.</li>
<li><b>Union by size:</b> attach the smaller group under the bigger one, so trees stay flat.</li>
</ul>
<p>Use it instead of BFS/DFS when edges arrive <b>over time</b> and you need the answer after each one.</p>
<div class="analogy"><b>Picture it:</b> companies merging. Every employee knows who their boss is; the CEO has no boss. To check if two people work for the same company, follow the chain of bosses up to the CEO. When two companies merge, one CEO starts reporting to the other.</div>
""",
    "signals": [
        "\"Connected components\" with edges added one by one",
        "Is adding this edge going to create a cycle? (undirected)",
        "Grouping by shared properties: accounts with a shared email, similar strings",
        "Kruskal's minimum spanning tree",
    ],
    "pitfalls": [
        "Forgetting path compression (can degrade to O(n) per call)",
        "Using it for directed graphs (it only models undirected connectivity)",
        "Counting components without decrementing the count on successful unions only",
    ],
    "template": '''
class DSU:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.size = [1] * n
        self.groups = n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]   # path halving
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                                   # already together
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra                               # small under big
        self.size[ra] += self.size[rb]
        self.groups -= 1
        return True

d = DSU(5)
d.union(0, 1); d.union(3, 4)
assert d.find(0) == d.find(1) and d.find(1) != d.find(3)
assert d.groups == 3
''',
    "complexity": "Nearly O(1) per operation (inverse Ackermann, α(n) ≤ 4 in practice).",
    "problems": [
        {
            "name": "Find if Path Exists in Graph",
            "lc": 1971,
            "level": "E",
            "prompt": "<p>Undirected graph with n nodes and an edge list. Is there a path from <code>source</code> to <code>destination</code>?</p>",
            "hint": "Same group means connected.",
            "idea": "<p>Union every edge, then check whether both endpoints share a root. BFS works too; union-find is shorter here.</p>",
            "code": '''
def valid_path(n: int, edges: list[list[int]], source: int, destination: int) -> bool:
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in edges:
        parent[find(a)] = find(b)
    return find(source) == find(destination)

assert valid_path(3, [[0, 1], [1, 2], [2, 0]], 0, 2)
assert not valid_path(6, [[0, 1], [0, 2], [3, 5], [5, 4], [4, 3]], 0, 5)
''',
            "complexity": "O((n + E) · α(n)) time, O(n) space.",
        },
        {
            "name": "Redundant Connection",
            "lc": 684,
            "level": "M",
            "prompt": "<p>A tree with one extra edge added. Return the edge that can be removed to make it a tree again (the last such edge in the input).</p><pre>[[1,2],[1,3],[2,3]]  →  [2,3]</pre>",
            "hint": "Add edges one by one. Which edge connects two nodes that are already connected?",
            "idea": "<p>Process edges in order. If both ends already have the same root, this edge closes a cycle; return it. Otherwise union them.</p>",
            "code": '''
def find_redundant_connection(edges: list[list[int]]) -> list[int]:
    parent = list(range(len(edges) + 1))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra == rb:
            return [a, b]
        parent[ra] = rb
    return []

assert find_redundant_connection([[1, 2], [1, 3], [2, 3]]) == [2, 3]
assert find_redundant_connection([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]) == [1, 4]
''',
            "complexity": "O(n · α(n)) time, O(n) space.",
        },
        {
            "name": "Accounts Merge",
            "lc": 721,
            "level": "M",
            "hot": True,
            "prompt": "<p>Each account is <code>[name, email1, email2, …]</code>. Accounts sharing any email belong to the same person. Merge them; return each person's name followed by their sorted emails.</p>",
            "hint": "Union every email in an account with the account's first email.",
            "idea": "<p>Treat emails as nodes. For each account, union all its emails with its first one, and remember which name each email belongs to. Then group emails by root, sort each group, and put the name in front.</p>",
            "code": '''
from collections import defaultdict

def accounts_merge(accounts: list[list[str]]) -> list[list[str]]:
    parent = {}
    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        parent[find(a)] = find(b)

    owner = {}
    for name, *emails in accounts:
        for e in emails:
            owner[e] = name
            union(e, emails[0])
    groups = defaultdict(list)
    for e in owner:
        groups[find(e)].append(e)
    return [[owner[root]] + sorted(es) for root, es in groups.items()]

accts = [["John", "johnsmith@mail.com", "john_newyork@mail.com"],
         ["John", "johnsmith@mail.com", "john00@mail.com"],
         ["Mary", "mary@mail.com"],
         ["John", "johnnybravo@mail.com"]]
assert sorted(accounts_merge(accts)) == sorted([
    ["John", "john00@mail.com", "john_newyork@mail.com", "johnsmith@mail.com"],
    ["Mary", "mary@mail.com"],
    ["John", "johnnybravo@mail.com"]])
''',
            "complexity": "O(E log E) time for sorting E emails, O(E) space.",
        },
        {
            "name": "Number of Islands II",
            "lc": 305,
            "level": "H",
            "hot": True,
            "prompt": "<p>An m × n grid starts as all water. <code>positions</code> turns cells into land one at a time. After each addition, return the number of islands.</p><pre>m = 3, n = 3, [[0,0],[0,1],[1,2],[2,1]]  →  [1,1,2,3]</pre>",
            "hint": "Each new land cell is a new island, until you union it with land neighbors.",
            "idea": "<p>Re-running BFS after every addition is too slow. Instead: a new land cell adds one island. Then for each of its 4 land neighbors, a successful union means two islands merged, so subtract one. Skip positions that are already land. Map cell <code>(r, c)</code> to index <code>r · n + c</code>.</p>",
            "code": '''
def num_islands2(m: int, n: int, positions: list[list[int]]) -> list[int]:
    parent = {}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    islands = 0
    out = []
    for r, c in positions:
        cell = r * n + c
        if cell in parent:
            out.append(islands)                  # already land
            continue
        parent[cell] = cell
        islands += 1
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            nb = nr * n + nc
            if 0 <= nr < m and 0 <= nc < n and nb in parent:
                ra, rb = find(cell), find(nb)
                if ra != rb:
                    parent[ra] = rb
                    islands -= 1
        out.append(islands)
    return out

assert num_islands2(3, 3, [[0, 0], [0, 1], [1, 2], [2, 1]]) == [1, 1, 2, 3]
assert num_islands2(3, 3, [[0, 0], [0, 1], [1, 2], [1, 2], [1, 1]]) == [1, 1, 2, 2, 1]
''',
            "complexity": "O(k · α(mn)) time for k additions, O(k) space.",
        },
    ],
}

SHORTEST = {
    "id": "shortest-paths",
    "nav": "Shortest paths",
    "title": "Weighted shortest paths",
    "tagline": "When steps have different costs, BFS isn't enough. Dijkstra always expands the cheapest place first.",
    "plain": """
<p>BFS finds the fewest <i>steps</i>. When edges have different costs (minutes, dollars, effort), use <b>Dijkstra's algorithm</b>: a BFS where the queue is a min-heap ordered by total cost so far. The first time you pop a node, you've found its cheapest cost, as long as no edge is negative.</p>
<p>Know when to use which:</p>
<div class="tbl"><table>
<thead><tr><th>Situation</th><th>Algorithm</th><th>Cost</th></tr></thead>
<tbody>
<tr><td>All edges cost the same</td><td>BFS</td><td><code>O(V + E)</code></td></tr>
<tr><td>Edges cost 0 or 1</td><td>0-1 BFS (deque: 0-cost to the front, 1-cost to the back)</td><td><code>O(V + E)</code></td></tr>
<tr><td>Non-negative weights</td><td>Dijkstra</td><td><code>O(E log V)</code></td></tr>
<tr><td>Negative weights, or \"at most k edges\"</td><td>Bellman-Ford</td><td><code>O(k · E)</code></td></tr>
<tr><td>All pairs, small V (≤ 400)</td><td>Floyd–Warshall</td><td><code>O(V³)</code></td></tr>
</tbody></table></div>
<div class="analogy"><b>Picture it:</b> water spreading from a source through pipes of different lengths. It reaches the nearest junction first, then the next nearest, and so on. Dijkstra simulates that order with a heap.</div>
""",
    "signals": [
        "\"Minimum cost / time / effort\" to get from A to B with different edge costs",
        "Network delay, flight prices, travel times",
        "\"Minimize the maximum\" along a path (Dijkstra with max instead of +)",
        "A limit on the number of stops (Bellman-Ford or BFS by levels)",
    ],
    "pitfalls": [
        "Not skipping stale heap entries: <code>if d &gt; dist[node]: continue</code>",
        "Using Dijkstra with negative edges",
        "Marking visited when pushing (correct for BFS, wrong for Dijkstra)",
    ],
    "template": '''
import heapq
from collections import defaultdict

def dijkstra(n: int, edges: list[tuple[int, int, int]], src: int) -> list[float]:
    graph = defaultdict(list)
    for u, v, w in edges:
        graph[u].append((v, w))
    dist = [float("inf")] * n
    dist[src] = 0
    heap = [(0, src)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue                        # stale entry; a cheaper one was used
        for v, w in graph[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return dist

assert dijkstra(4, [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1)], 0) == [0, 3, 1, 4]
''',
    "complexity": "O((V + E) log V) time, O(V + E) space.",
    "problems": [
        {
            "name": "Shortest Path in Binary Matrix",
            "lc": 1091,
            "level": "M",
            "prompt": "<p>Grid of 0 (open) and 1 (blocked). Move in 8 directions. Return the length (cells visited) of the shortest clear path from top-left to bottom-right, or −1.</p><pre>[[0,0,0],[1,1,0],[1,1,0]]  →  4</pre>",
            "hint": "Every move costs 1, so this is plain BFS, just with 8 neighbors.",
            "idea": "<p>Warm-up to confirm the rule: unweighted means BFS. Check that the start and end are open. The distance counts cells, so start at 1.</p>",
            "code": '''
from collections import deque

def shortest_path_binary_matrix(grid: list[list[int]]) -> int:
    n = len(grid)
    if grid[0][0] or grid[n - 1][n - 1]:
        return -1
    queue = deque([(0, 0, 1)])
    grid[0][0] = 1                                # mark visited
    while queue:
        r, c, d = queue.popleft()
        if (r, c) == (n - 1, n - 1):
            return d
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 0:
                    grid[nr][nc] = 1
                    queue.append((nr, nc, d + 1))
    return -1

assert shortest_path_binary_matrix([[0, 1], [1, 0]]) == 2
assert shortest_path_binary_matrix([[0, 0, 0], [1, 1, 0], [1, 1, 0]]) == 4
assert shortest_path_binary_matrix([[1, 0, 0], [1, 1, 0], [1, 1, 0]]) == -1
''',
            "complexity": "O(n²) time and space.",
        },
        {
            "name": "Network Delay Time",
            "lc": 743,
            "level": "M",
            "hot": True,
            "prompt": "<p><code>times[i] = (u, v, w)</code>: a signal takes w to go from u to v. Send a signal from node <code>k</code>. How long until all n nodes (labeled 1..n) receive it? −1 if some never do.</p>",
            "hint": "The answer is the largest shortest-path distance from k.",
            "idea": "<p>Run Dijkstra from k. If any node is unreachable, return −1. Otherwise the answer is the maximum distance, because every node receives the signal along its own shortest path.</p>",
            "code": '''
import heapq
from collections import defaultdict

def network_delay_time(times: list[list[int]], n: int, k: int) -> int:
    graph = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))
    dist = {}
    heap = [(0, k)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in dist:
            continue                              # already finalized
        dist[u] = d
        for v, w in graph[u]:
            if v not in dist:
                heapq.heappush(heap, (d + w, v))
    return max(dist.values()) if len(dist) == n else -1

assert network_delay_time([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2) == 2
assert network_delay_time([[1, 2, 1]], 2, 2) == -1
''',
            "complexity": "O(E log E) time, O(V + E) space.",
        },
        {
            "name": "Cheapest Flights Within K Stops",
            "lc": 787,
            "level": "M",
            "hot": True,
            "prompt": "<p>Flights <code>(from, to, price)</code>. Find the cheapest price from <code>src</code> to <code>dst</code> with at most <code>k</code> stops (k + 1 flights), or −1.</p>",
            "hint": "Plain Dijkstra ignores the stop limit. Bellman-Ford naturally counts edges: round i allows i edges.",
            "idea": "<p>Run Bellman-Ford for <code>k + 1</code> rounds. In each round, relax every flight, but read prices from a <b>copy</b> of the previous round, so one round can only add one flight. After k + 1 rounds, <code>prices[dst]</code> is the cheapest trip with at most k + 1 flights.</p>",
            "code": '''
def find_cheapest_price(n: int, flights: list[list[int]], src: int, dst: int, k: int) -> int:
    INF = float("inf")
    prices = [INF] * n
    prices[src] = 0
    for _ in range(k + 1):
        nxt = prices[:]                          # use last round's prices only
        for u, v, w in flights:
            if prices[u] + w < nxt[v]:
                nxt[v] = prices[u] + w
        prices = nxt
    return -1 if prices[dst] == INF else prices[dst]

flights = [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]]
assert find_cheapest_price(4, flights, 0, 3, 1) == 700
assert find_cheapest_price(3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 1) == 200
assert find_cheapest_price(3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 0) == 500
''',
            "complexity": "O(k · E) time, O(V) space.",
        },
        {
            "name": "Path With Minimum Effort",
            "lc": 1631,
            "level": "M",
            "prompt": "<p>A hiker crosses a height grid from top-left to bottom-right. A route's effort is its <b>largest</b> height difference between consecutive cells. Minimize the effort.</p><pre>[[1,2,2],[3,8,2],[5,3,5]]  →  2</pre>",
            "hint": "Dijkstra still works if a path's cost is the max edge instead of the sum.",
            "idea": "<p>Run Dijkstra where extending a path to a neighbor costs <code>max(current_effort, |height difference|)</code>. The cost never decreases along a path, which is all Dijkstra needs. (Binary search on the answer plus BFS also works.)</p>",
            "code": '''
import heapq

def minimum_effort_path(heights: list[list[int]]) -> int:
    rows, cols = len(heights), len(heights[0])
    best = [[float("inf")] * cols for _ in range(rows)]
    best[0][0] = 0
    heap = [(0, 0, 0)]
    while heap:
        effort, r, c = heapq.heappop(heap)
        if (r, c) == (rows - 1, cols - 1):
            return effort
        if effort > best[r][c]:
            continue
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols:
                e = max(effort, abs(heights[nr][nc] - heights[r][c]))
                if e < best[nr][nc]:
                    best[nr][nc] = e
                    heapq.heappush(heap, (e, nr, nc))
    return 0

assert minimum_effort_path([[1, 2, 2], [3, 8, 2], [5, 3, 5]]) == 2
assert minimum_effort_path([[1, 2, 3], [3, 8, 4], [5, 3, 5]]) == 1
assert minimum_effort_path([[7]]) == 0
''',
            "complexity": "O(rows · cols · log(rows · cols)) time.",
        },
        {
            "name": "Swim in Rising Water",
            "lc": 778,
            "level": "H",
            "prompt": "<p>At time t the water level is t, and you can swim between adjacent cells whose heights are both ≤ t. What's the earliest time you can reach the bottom-right from the top-left?</p><pre>[[0,2],[1,3]]  →  3</pre>",
            "hint": "The answer for a route is the highest cell on it. Minimize that.",
            "idea": "<p>Same shape as minimum effort: a path's cost is the <b>maximum height</b> on it. Dijkstra with a min-heap on that maximum: always expand the lowest reachable cell next. The first time you pop the target, its value is the answer.</p>",
            "code": '''
import heapq

def swim_in_water(grid: list[list[int]]) -> int:
    n = len(grid)
    heap = [(grid[0][0], 0, 0)]
    seen = {(0, 0)}
    while heap:
        t, r, c = heapq.heappop(heap)
        if (r, c) == (n - 1, n - 1):
            return t
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in seen:
                seen.add((nr, nc))
                heapq.heappush(heap, (max(t, grid[nr][nc]), nr, nc))
    return -1

assert swim_in_water([[0, 2], [1, 3]]) == 3
assert swim_in_water([[0, 1, 2, 3, 4], [24, 23, 22, 21, 5], [12, 13, 14, 15, 16],
                      [11, 17, 18, 19, 20], [10, 9, 8, 7, 6]]) == 16
''',
            "complexity": "O(n² log n) time, O(n²) space.",
        },
        {
            "name": "Minimum Cost to Make at Least One Valid Path",
            "lc": 1368,
            "level": "H",
            "prompt": "<p>Each cell has an arrow: 1 right, 2 left, 3 down, 4 up. Following an arrow is free; changing a cell's arrow costs 1. Minimum cost to get from top-left to bottom-right?</p><pre>[[1,1,1,1],[2,2,2,2],[1,1,1,1],[2,2,2,2]]  →  3</pre>",
            "hint": "Moves cost 0 or 1. There's a faster tool than Dijkstra for that.",
            "idea": "<p><b>0-1 BFS</b>: use a deque. Moving the way the arrow points costs 0, so push that neighbor to the <b>front</b>. Any other direction costs 1, so push it to the <b>back</b>. The deque stays sorted by cost, like a heap, but every operation is O(1).</p>",
            "code": '''
from collections import deque

def min_cost(grid: list[list[int]]) -> int:
    rows, cols = len(grid), len(grid[0])
    moves = {1: (0, 1), 2: (0, -1), 3: (1, 0), 4: (-1, 0)}
    dist = [[float("inf")] * cols for _ in range(rows)]
    dist[0][0] = 0
    dq = deque([(0, 0)])
    while dq:
        r, c = dq.popleft()
        for arrow, (dr, dc) in moves.items():
            nr, nc = r + dr, c + dc
            if not (0 <= nr < rows and 0 <= nc < cols):
                continue
            cost = 0 if grid[r][c] == arrow else 1
            if dist[r][c] + cost < dist[nr][nc]:
                dist[nr][nc] = dist[r][c] + cost
                if cost == 0:
                    dq.appendleft((nr, nc))
                else:
                    dq.append((nr, nc))
    return dist[rows - 1][cols - 1]

assert min_cost([[1, 1, 1, 1], [2, 2, 2, 2], [1, 1, 1, 1], [2, 2, 2, 2]]) == 3
assert min_cost([[1, 1, 3], [3, 2, 2], [1, 1, 4]]) == 0
assert min_cost([[1, 2], [4, 3]]) == 1
''',
            "complexity": "O(rows · cols) time and space.",
        },
    ],
}

TRIES = {
    "id": "tries",
    "nav": "Tries",
    "title": "Tries (prefix trees)",
    "tagline": "Store many words so that every shared prefix is stored once. Instant prefix lookups.",
    "plain": """
<p>A trie is a tree of letters. The root is empty; each edge adds one letter; a path from the root spells a prefix. A flag on a node says \"a whole word ends here\". Words that start the same way share the same path, like <i>car</i>, <i>cart</i> and <i>care</i>.</p>
<p>Looking up a word or prefix costs O(length of the word), no matter how many words are stored. That's why tries power autocomplete and spell-checkers, and they fit Google well (think of the search box).</p>
<div class="analogy"><b>Picture it:</b> a phone's contact search. Type \"J\", and it narrows to names starting with J. Type \"Jo\", and it narrows further. Each letter moves you one step down the tree.</div>
<p>In Python, a node is simply a dict of children. You can even use nested dicts with a special end-marker key.</p>
""",
    "signals": [
        "Autocomplete, search suggestions, \"starts with\"",
        "Many words searched in the same grid or text",
        "Wildcard search like <code>b.d</code>",
        "Longest common prefix, word squares, replacing words by roots",
        "XOR maximization (a trie over bits)",
    ],
    "pitfalls": [
        "Forgetting the end-of-word flag (\"app\" is a prefix of \"apple\" but may not be a word)",
        "Rebuilding the trie for every query",
        "In Word Search II, not pruning found words, which repeats work",
    ],
    "template": '''
class TrieNode:
    __slots__ = ("children", "is_word")
    def __init__(self):
        self.children = {}
        self.is_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_word = True

    def _walk(self, s: str):
        node = self.root
        for ch in s:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    def search(self, word: str) -> bool:
        node = self._walk(word)
        return node is not None and node.is_word

    def starts_with(self, prefix: str) -> bool:
        return self._walk(prefix) is not None

t = Trie()
t.insert("apple")
assert t.search("apple") and not t.search("app") and t.starts_with("app")
t.insert("app")
assert t.search("app")
''',
    "complexity": "O(L) per insert or lookup for a word of length L. Space O(total characters).",
    "problems": [
        {
            "name": "Longest Common Prefix",
            "lc": 14,
            "level": "E",
            "prompt": "<p>Return the longest prefix shared by all strings.</p><pre>[\"flower\",\"flow\",\"flight\"]  →  \"fl\"</pre>",
            "hint": "Compare column by column, or sort and compare only the first and last strings.",
            "idea": "<p>After sorting, the first and last strings are the most different, so their common prefix is everyone's common prefix. (In a trie, it's the path from the root while each node has exactly one child and isn't a word end.)</p>",
            "code": '''
def longest_common_prefix(strs: list[str]) -> str:
    if not strs:
        return ""
    first, last = min(strs), max(strs)
    i = 0
    while i < len(first) and first[i] == last[i]:
        i += 1
    return first[:i]

assert longest_common_prefix(["flower", "flow", "flight"]) == "fl"
assert longest_common_prefix(["dog", "racecar", "car"]) == ""
assert longest_common_prefix(["a"]) == "a"
''',
            "complexity": "O(n · L) time, O(1) extra space.",
        },
        {
            "name": "Design Add and Search Words",
            "lc": 211,
            "level": "M",
            "hot": True,
            "prompt": "<p>Support <code>add_word(w)</code> and <code>search(w)</code>, where <code>.</code> in the search matches any one letter.</p>",
            "hint": "At a '.', try every child.",
            "idea": "<p>A normal trie for adding. Searching is a DFS over the trie: a letter follows one child; a dot branches into all children. Return True as soon as any branch reaches a word end at the last character.</p>",
            "code": '''
class WordDictionary:
    def __init__(self):
        self.root = {}

    def add_word(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node["$"] = True                          # end-of-word marker

    def search(self, word: str) -> bool:
        def dfs(node, i) -> bool:
            if i == len(word):
                return "$" in node
            ch = word[i]
            if ch == ".":
                return any(dfs(child, i + 1) for key, child in node.items() if key != "$")
            return ch in node and dfs(node[ch], i + 1)
        return dfs(self.root, 0)

wd = WordDictionary()
for w in ["bad", "dad", "mad"]:
    wd.add_word(w)
assert not wd.search("pad")
assert wd.search("bad") and wd.search(".ad") and wd.search("b..")
assert not wd.search("b...")
''',
            "complexity": "O(L) add; search O(L) without dots, up to O(26^dots · L) with them.",
        },
        {
            "name": "Search Suggestions System",
            "lc": 1268,
            "level": "M",
            "hot": True,
            "prompt": "<p>After each typed character of <code>search_word</code>, return up to 3 products (alphabetically smallest) that start with what's been typed.</p><pre>products = [\"mobile\",\"mouse\",\"moneypot\",\"monitor\",\"mousepad\"], \"mouse\"\n→ [[\"mobile\",\"moneypot\",\"monitor\"], [\"mobile\",\"moneypot\",\"monitor\"],\n   [\"mouse\",\"mousepad\"], [\"mouse\",\"mousepad\"], [\"mouse\",\"mousepad\"]]</pre>",
            "hint": "Insert products in sorted order and let each trie node keep its first 3 words.",
            "idea": "<p>Sort the products, then insert them into a trie. Each node stores up to 3 words that pass through it; because we insert in sorted order, those are the 3 smallest. Answering is a walk down the trie, one node per typed letter. (A sorted list with <code>bisect</code> also works and is shorter; mention both.)</p>",
            "code": '''
def suggested_products(products: list[str], search_word: str) -> list[list[str]]:
    root = {"#": []}
    for p in sorted(products):
        node = root
        for ch in p:
            node = node.setdefault(ch, {"#": []})
            if len(node["#"]) < 3:
                node["#"].append(p)
    out, node = [], root
    for ch in search_word:
        node = node.get(ch) if node else None
        out.append(node["#"] if node else [])
    return out

products = ["mobile", "mouse", "moneypot", "monitor", "mousepad"]
assert suggested_products(products, "mouse") == [
    ["mobile", "moneypot", "monitor"], ["mobile", "moneypot", "monitor"],
    ["mouse", "mousepad"], ["mouse", "mousepad"], ["mouse", "mousepad"]]
assert suggested_products(["havana"], "tatiana") == [[], [], [], [], [], [], []]
''',
            "complexity": "O(total characters) to build, O(L) to answer.",
        },
        {
            "name": "Word Search II",
            "lc": 212,
            "level": "H",
            "hot": True,
            "prompt": "<p>Find all words from a list that can be formed in a letter grid (adjacent cells, each used once per word).</p><pre>board = [[\"o\",\"a\",\"a\",\"n\"],[\"e\",\"t\",\"a\",\"e\"],\n         [\"i\",\"h\",\"k\",\"r\"],[\"i\",\"f\",\"l\",\"v\"]]\nwords = [\"oath\",\"pea\",\"eat\",\"rain\"]  →  [\"eat\",\"oath\"]</pre>",
            "hint": "Running Word Search once per word repeats work. Put all words in a trie and DFS the grid once, walking the trie alongside.",
            "idea": "<p>Build a trie of all words, storing the full word at its end node. DFS from every cell, moving down the trie as you move through the grid; stop as soon as the trie has no child for the current letter. When you reach a node with a word, record it and remove the marker so it's found once. Pruning empty trie branches after use keeps later searches fast.</p>",
            "code": '''
def find_words(board: list[list[str]], words: list[str]) -> list[str]:
    root = {}
    for w in words:
        node = root
        for ch in w:
            node = node.setdefault(ch, {})
        node["$"] = w
    rows, cols = len(board), len(board[0])
    found = []

    def dfs(r, c, parent):
        ch = board[r][c]
        node = parent[ch]
        if "$" in node:
            found.append(node.pop("$"))          # record once
        board[r][c] = "#"
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] in node:
                dfs(nr, nc, node)
        board[r][c] = ch
        if not node:
            parent.pop(ch)                       # prune dead branch

    for r in range(rows):
        for c in range(cols):
            if board[r][c] in root:
                dfs(r, c, root)
    return found

board = [["o", "a", "a", "n"], ["e", "t", "a", "e"], ["i", "h", "k", "r"], ["i", "f", "l", "v"]]
assert sorted(find_words(board, ["oath", "pea", "eat", "rain"])) == ["eat", "oath"]
assert find_words([["a", "b"], ["c", "d"]], ["abcb"]) == []
''',
            "complexity": "O(rows · cols · 3^L) worst case, much less in practice with pruning.",
        },
    ],
}

PATTERNS = [BACKTRACKING, GRAPHS, TOPO, UNION_FIND, SHORTEST, TRIES]
