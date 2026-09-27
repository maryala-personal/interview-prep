"""Opening sections: how Google interviews, the 45-minute plan, Big-O, Python toolkit."""

HOW = {
    "id": "how-google",
    "nav": "How Google interviews",
    "title": "How Google runs coding interviews",
    "body": """
<p>Knowing the format removes half the stress. Here is the loop for a software engineer role as reported by candidates in 2025 and 2026. Your recruiter has the final word for your level and location, so confirm the details with them.</p>
<div class="tbl"><table>
<thead><tr><th>Stage</th><th>Length</th><th>What happens</th></tr></thead>
<tbody>
<tr><td>Recruiter call</td><td class="num-col">20–30 min</td><td>Background, level (L3 new grad, L4 mid, L5 senior, L6 staff), timeline. Ask them which rounds you will get.</td></tr>
<tr><td>Online assessment</td><td class="num-col">60–90 min</td><td>Mostly for new grads and interns: two timed problems on a platform that runs your code.</td></tr>
<tr><td>Technical phone screen</td><td class="num-col">45 min</td><td>One or two coding problems in a shared doc. Usually one medium with a follow-up.</td></tr>
<tr><td>Onsite loop (virtual or in person)</td><td class="num-col">4–5 × 45 min</td><td>Two to four coding rounds, one Googleyness and Leadership round, and a system design round for L5 and above. In-person whiteboard rounds have come back in many offices.</td></tr>
<tr><td>Hiring committee</td><td class="num-col">1–3 weeks</td><td>People who never met you read your interviewers' written notes and decide. This is why clear communication matters: your interviewer has to write down what you did.</td></tr>
<tr><td>Team match</td><td class="num-col">varies</td><td>Short chats with teams that have headcount. Then the offer.</td></tr>
</tbody></table></div>

<h3>The 2026 change: a code comprehension round</h3>
<p>In May 2026 Google announced a pilot that replaces one coding round with a <b>code comprehension round</b> for junior and mid-level roles on some US teams. You get an existing codebase and use Gemini to read it, debug it and speed it up. You are graded on how well you steer the AI: clear prompts, checking what it gives back, and catching its mistakes. The pilot rolls out in the second half of 2026, so ask your recruiter whether your loop includes it. The skills in this notebook still matter there, because you cannot judge AI-written code without knowing what good code looks like.</p>

<h3>What the interviewer writes down about you</h3>
<p>Each coding interviewer scores four things. Knowing them tells you what to do out loud.</p>
<div class="cards">
  <div class="card"><h4>Algorithms</h4><p>Did you find an efficient approach, and can you explain why it is correct and what it costs in Big-O?</p></div>
  <div class="card"><h4>Coding</h4><p>Is the code clean, correct and idiomatic? Good names, small helpers, no copy-paste. It must look like code you would ship.</p></div>
  <div class="card"><h4>Communication</h4><p>Did you ask clarifying questions and explain your thinking while working? Silence gives them nothing to write.</p></div>
  <div class="card"><h4>Problem solving</h4><p>When stuck, did you break the problem down, try small examples and use hints well? Taking a hint is fine; ignoring one is not.</p></div>
</div>
<p>Each round ends with a score from <i>Strong No Hire</i> to <i>Strong Hire</i>. Across the whole loop Google also looks at general cognitive ability, role knowledge, leadership and "Googleyness", which means being humble, collaborative and comfortable with ambiguity.</p>

<h3>What Google likes to ask</h3>
<ul>
<li><b>Mostly medium problems</b>, with a hard follow-up if you finish early. Candidate reports put the mix at roughly one third easy, one half medium, and the rest hard.</li>
<li><b>Graphs and grids show up a lot</b>: BFS, DFS, topological sort, union-find, shortest paths. More than at most companies.</li>
<li><b>Questions are often disguised</b>. They rarely read like a LeetCode title. "Plan a route through a building" is a BFS problem. Your job is to spot the pattern under the story.</li>
<li><b>Follow-ups are the real test</b>: "What if the input doesn't fit in memory?", "What if it's a stream?", "What if this is called a million times?"</li>
<li><b>No code runs</b>. You write in a plain doc with no autocomplete, so you must trace your code by hand with a small example.</li>
</ul>
""",
}

FRAMEWORK = {
    "id": "framework",
    "nav": "The 45-minute game plan",
    "title": "The 45-minute game plan",
    "body": """
<p>Use the same routine in every round, including the easy ones. It keeps you calm and it hands the interviewer exactly what they need to write a strong report.</p>
<ol class="steps">
<li><div><b>Restate and clarify (3–5 min)</b>Repeat the problem in your own words. Ask about input size, empty input, duplicates, negative numbers, sorted or not, and what to return when there is no answer. <span class="say">"Can the array be empty? Roughly how big can n get: thousands or billions?"</span></div></li>
<li><div><b>Work one example by hand (2–3 min)</b>Make a small example and solve it on paper. This is where you usually notice the pattern. Also make one tricky example for later.</div></li>
<li><div><b>Say the brute force (1–2 min)</b>State the slow, obvious approach and its Big-O. It proves you understand the problem and gives you a fallback. <span class="say">"Checking every pair is O(n²). I think we can do better with a hash map."</span></div></li>
<li><div><b>Optimize and agree (5–10 min)</b>Look for the pattern using the cheat sheet at the end of this notebook. Explain the plan and its complexity, and get a nod from the interviewer <i>before</i> you write code.</div></li>
<li><div><b>Write the code (15–20 min)</b>Write clean Python. Talk while you write, but not every keystroke. Use helper functions with clear names. If a detail is fiddly, leave a short comment and come back to it.</div></li>
<li><div><b>Test by hand (5 min)</b>Walk your small example through the code line by line, tracking variables. Then check edge cases: empty, one element, all the same, very large. Fix bugs calmly; finding your own bug is a good signal.</div></li>
<li><div><b>State complexity and follow-ups (2–3 min)</b>Give final time and space complexity. Mention what you would change for bigger input, streaming data or concurrency.</div></li>
</ol>
<div class="callout"><b>If you get stuck:</b> say what you know so far, go back to the brute force, and ask yourself: can sorting help? Can a hash map remember something? Can I think of this as a graph? Can I solve a smaller version (first i items) and build up? Interviewers expect to give hints; a candidate who uses a hint quickly still scores well.</div>
""",
}

BIGO = {
    "id": "big-o",
    "nav": "Big-O in plain English",
    "title": "Big-O in plain English",
    "body": """
<p>Big-O answers one question: <b>when the input gets 10× bigger, how much slower does my code get?</b> We ignore constants and small terms because only the growth rate matters for big inputs.</p>
<div class="tbl"><table>
<thead><tr><th>Big-O</th><th>Name</th><th>Everyday picture</th><th>Example</th></tr></thead>
<tbody>
<tr><td><code>O(1)</code></td><td>Constant</td><td>Opening a book to a page you bookmarked.</td><td>dict lookup, list index</td></tr>
<tr><td><code>O(log n)</code></td><td>Logarithmic</td><td>Finding a word in a dictionary by opening it in the middle, then the middle of the half, and so on.</td><td>binary search, heap push/pop</td></tr>
<tr><td><code>O(n)</code></td><td>Linear</td><td>Reading every page once.</td><td>one loop over the input</td></tr>
<tr><td><code>O(n log n)</code></td><td>Linearithmic</td><td>Sorting a deck of cards efficiently.</td><td><code>sorted()</code>, merge sort</td></tr>
<tr><td><code>O(n²)</code></td><td>Quadratic</td><td>Everyone in a room shaking hands with everyone else.</td><td>two nested loops</td></tr>
<tr><td><code>O(2ⁿ)</code></td><td>Exponential</td><td>Trying every possible combination of toppings.</td><td>all subsets</td></tr>
<tr><td><code>O(n!)</code></td><td>Factorial</td><td>Trying every seating order at a dinner table.</td><td>all permutations</td></tr>
</tbody></table></div>

<h3>Read the constraints to guess the target</h3>
<p>A computer does roughly 10⁷ to 10⁸ simple Python operations per second. So the input size tells you which complexity the interviewer expects. If they don't say, ask.</p>
<div class="tbl"><table>
<thead><tr><th>n up to</th><th>Aim for</th><th>Likely technique</th></tr></thead>
<tbody>
<tr><td class="num-col">10</td><td><code>O(n!)</code>, <code>O(2ⁿ)</code></td><td>Backtracking, try everything</td></tr>
<tr><td class="num-col">20</td><td><code>O(2ⁿ · n)</code></td><td>Bitmask DP, subsets</td></tr>
<tr><td class="num-col">500</td><td><code>O(n³)</code></td><td>Interval DP, Floyd–Warshall</td></tr>
<tr><td class="num-col">5,000</td><td><code>O(n²)</code></td><td>2D DP, nested loops</td></tr>
<tr><td class="num-col">10⁶</td><td><code>O(n log n)</code> or <code>O(n)</code></td><td>Sorting, heap, two pointers, hash map, sliding window</td></tr>
<tr><td class="num-col">10⁹ or more</td><td><code>O(log n)</code> or <code>O(1)</code></td><td>Binary search, math</td></tr>
</tbody></table></div>

<h3>Four rules that cover most cases</h3>
<ul>
<li><b>Loops in a row add:</b> an <code>O(n)</code> loop followed by another <code>O(n)</code> loop is still <code>O(n)</code>.</li>
<li><b>Loops inside loops multiply:</b> a loop over <code>n</code> inside a loop over <code>m</code> is <code>O(n·m)</code>.</li>
<li><b>Recursion costs (number of calls) × (work per call):</b> a function that calls itself twice, n levels deep, makes about 2ⁿ calls. With memoization, the number of calls drops to the number of distinct inputs.</li>
<li><b>Space counts what you store</b>, including the recursion stack. Recursing n levels deep uses <code>O(n)</code> space even with no extra lists.</li>
</ul>
<p><b>Amortized</b> means "on average over many operations". Appending to a Python list is <code>O(1)</code> amortized: once in a while the list resizes and copies everything, but that cost spreads thinly over all the cheap appends.</p>

<h3>Hidden costs in Python</h3>
<div class="tbl"><table>
<thead><tr><th>Operation</th><th>Cost</th><th>Note</th></tr></thead>
<tbody>
<tr><td><code>x in list</code></td><td><code>O(n)</code></td><td>Use a <code>set</code> for <code>O(1)</code> lookups.</td></tr>
<tr><td><code>list.pop(0)</code>, <code>list.insert(0, x)</code></td><td><code>O(n)</code></td><td>Use <code>collections.deque</code> for queues.</td></tr>
<tr><td><code>s[a:b]</code>, <code>lst[a:b]</code></td><td><code>O(b−a)</code></td><td>Slicing copies. Slicing inside a loop can turn O(n) into O(n²).</td></tr>
<tr><td><code>s1 + s2</code> in a loop</td><td><code>O(n²)</code> total</td><td>Strings are immutable. Collect pieces in a list and use <code>"".join()</code>.</td></tr>
<tr><td><code>sorted(x)</code></td><td><code>O(n log n)</code></td><td>Also <code>O(n)</code> extra space.</td></tr>
<tr><td><code>min(lst)</code>, <code>max(lst)</code>, <code>sum(lst)</code></td><td><code>O(n)</code></td><td>Calling these inside a loop is a common hidden O(n²).</td></tr>
<tr><td><code>heapq.heappush</code> / <code>heappop</code></td><td><code>O(log n)</code></td><td><code>heapify</code> is <code>O(n)</code>.</td></tr>
</tbody></table></div>
""",
}

TOOLKIT = {
    "id": "python-toolkit",
    "nav": "Python interview toolkit",
    "title": "Your Python interview toolkit",
    "body": """
<p>Python is a great interview language because it is short to write. These are the tools you will use in almost every problem. Know them well enough to write them without looking anything up.</p>
<h3>Collections you will use every day</h3>
{{code0}}
<h3>Heaps: Python only has a min-heap</h3>
<p>A heap always gives you the smallest item in <code>O(log n)</code>. For a max-heap, push negative numbers. To store extra data, push tuples; Python compares them item by item.</p>
{{code1}}
<h3>Sorting, binary search, and useful built-ins</h3>
{{code2}}
<h3>Recursion and memoization</h3>
{{code3}}
<div class="callout"><b>Python traps interviewers notice:</b>
<ul>
<li><code>[[0] * n] * m</code> makes m references to the <i>same</i> row. Use <code>[[0] * n for _ in range(m)]</code>.</li>
<li><code>-7 // 2</code> is <code>-4</code> in Python (it rounds down, toward negative infinity). Use <code>int(-7 / 2)</code> to round toward zero.</li>
<li>Default arguments like <code>def f(x, seen=[])</code> are shared between calls. Use <code>None</code> and create the list inside.</li>
<li>Recursion depth defaults to 1000. For deep recursion, raise it or rewrite with an explicit stack.</li>
<li>Don't change a list or dict while looping over it. Loop over a copy, or build a new one.</li>
</ul></div>
""",
    "code": [
        '''
from collections import Counter, defaultdict, deque

# Counter: count things in one line
counts = Counter("banana")          # {'a': 3, 'n': 2, 'b': 1}
assert counts["a"] == 3 and counts["z"] == 0   # missing keys read as 0
assert counts.most_common(1) == [("a", 3)]

# defaultdict: a dict that creates a default value on first access
graph = defaultdict(list)
for u, v in [(1, 2), (1, 3), (2, 3)]:
    graph[u].append(v)              # no "if u not in graph" needed
assert graph[1] == [2, 3]

# deque: fast append and pop at BOTH ends (use it for every BFS queue)
q = deque([1, 2, 3])
q.appendleft(0)
q.append(4)
assert q.popleft() == 0 and q.pop() == 4

# set: O(1) membership test
seen = {1, 2, 3}
assert 2 in seen and 5 not in seen

# tuples are hashable, so they can be dict keys or set items (lists cannot)
visited = {(0, 0), (0, 1)}
assert (0, 1) in visited
''',
        '''
import heapq

nums = [5, 1, 8, 3]
heapq.heapify(nums)                 # O(n), turns the list into a heap in place
assert heapq.heappop(nums) == 1     # smallest comes out first

# Max-heap trick: store negatives
max_heap = []
for x in [5, 1, 8, 3]:
    heapq.heappush(max_heap, -x)
assert -heapq.heappop(max_heap) == 8

# Tuples: (priority, tie_breaker, item)
tasks = []
heapq.heappush(tasks, (2, "write code"))
heapq.heappush(tasks, (1, "clarify problem"))
assert heapq.heappop(tasks)[1] == "clarify problem"

# Top-k helpers
assert heapq.nlargest(2, [4, 9, 1, 7]) == [9, 7]
assert heapq.nsmallest(2, [4, 9, 1, 7]) == [1, 4]
''',
        '''
import bisect
from itertools import accumulate, combinations, permutations, product

people = [("ann", 31), ("bob", 25), ("cy", 31)]
# Sort by age descending, then name ascending
people.sort(key=lambda p: (-p[1], p[0]))
assert people[0] == ("ann", 31)

# bisect finds insertion points in a SORTED list in O(log n)
a = [1, 3, 3, 3, 7]
assert bisect.bisect_left(a, 3) == 1    # first index where a[i] >= 3
assert bisect.bisect_right(a, 3) == 4   # first index where a[i] > 3
count_of_3 = bisect.bisect_right(a, 3) - bisect.bisect_left(a, 3)
assert count_of_3 == 3

# Prefix sums in one line
assert list(accumulate([1, 2, 3, 4])) == [1, 3, 6, 10]

# Combinatorics
assert len(list(combinations([1, 2, 3], 2))) == 3     # choose 2 of 3
assert len(list(permutations([1, 2, 3]))) == 6       # all orders
assert len(list(product([0, 1], repeat=3))) == 8     # all 3-bit strings

# Handy built-ins
INF = float("inf")
for i, (x, y) in enumerate(zip("abc", [1, 2, 3])):
    pass
assert divmod(17, 5) == (3, 2)
assert ord("c") - ord("a") == 2 and chr(ord("a") + 2) == "c"
assert "a,b,c".split(",") == ["a", "b", "c"] and "-".join(["x", "y"]) == "x-y"
assert "Hello".lower() == "hello" and "abc123".isalnum() and "7".isdigit()
''',
        '''
import sys
from functools import lru_cache, cache

sys.setrecursionlimit(10_000)       # default is 1000

@cache                              # same as lru_cache(maxsize=None)
def fib(n: int) -> int:
    """Each distinct n is computed once, so this is O(n) instead of O(2^n)."""
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

assert fib(80) == 23416728348467685

# Inside a solution, define the cached helper INSIDE the method so the
# cache is fresh for each test case:
def count_paths(rows: int, cols: int) -> int:
    @lru_cache(maxsize=None)
    def go(r, c):
        if r == rows - 1 or c == cols - 1:
            return 1
        return go(r + 1, c) + go(r, c + 1)
    return go(0, 0)

assert count_paths(3, 7) == 28
''',
    ],
}

SECTIONS = [HOW, FRAMEWORK, BIGO, TOOLKIT]
