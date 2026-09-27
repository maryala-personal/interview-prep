"""Closing sections: pattern finder, extra Google practice, study plan, glossary."""

FINDER = {
    "id": "pattern-finder",
    "nav": "Pattern finder cheat sheet",
    "title": "Pattern finder: from clue to technique",
    "body": """
<p>When a new problem looks unfamiliar, scan this table for a clue that matches. Most problems match one or two rows.</p>
<div class="tbl"><table>
<thead><tr><th>If the problem says or shows…</th><th>Try first</th><th>Section</th></tr></thead>
<tbody>
<tr><td>Find a pair, duplicates, counts, \"have I seen it\"</td><td>Hash map or set</td><td><a href="#hashing">Hashing</a></td></tr>
<tr><td>Sorted array, pair or triplet sums, palindrome</td><td>Two pointers</td><td><a href="#two-pointers">Two pointers</a></td></tr>
<tr><td>Longest or shortest <i>contiguous</i> substring/subarray with a rule</td><td>Sliding window</td><td><a href="#sliding-window">Sliding window</a></td></tr>
<tr><td>Subarray sum equals k, negatives allowed, many range sums</td><td>Prefix sum + hash map</td><td><a href="#prefix-sums">Prefix sums</a></td></tr>
<tr><td>Sorted or rotated input; \"minimum X such that…\"; huge value range</td><td>Binary search (on index or on answer)</td><td><a href="#binary-search">Binary search</a></td></tr>
<tr><td>Brackets, nesting, next greater element, histogram</td><td>Stack / monotonic stack</td><td><a href="#stacks">Stacks</a></td></tr>
<tr><td>Linked list: middle, cycle, reverse, k-th from end</td><td>Fast/slow pointers, dummy head</td><td><a href="#linked-lists">Linked lists</a></td></tr>
<tr><td>Tree: heights, paths, ancestors</td><td>Recursive DFS returning a value</td><td><a href="#trees">Trees</a></td></tr>
<tr><td>Tree: levels, views, nearest</td><td>BFS with a queue</td><td><a href="#trees">Trees</a></td></tr>
<tr><td>BST, k-th smallest, sorted order in a tree</td><td>In-order traversal</td><td><a href="#bst">BST</a></td></tr>
<tr><td>Top k, k-th largest, merge k sorted, running median</td><td>Heap</td><td><a href="#heaps">Heaps</a></td></tr>
<tr><td>Meetings, ranges, bookings, overlaps</td><td>Sort by start, sweep; heap of ends</td><td><a href="#intervals">Intervals</a></td></tr>
<tr><td>Schedule the most, fewest jumps, a local choice that's provably safe</td><td>Greedy (sort + one pass)</td><td><a href="#greedy">Greedy</a></td></tr>
<tr><td>All subsets / permutations / combinations; n ≤ 15</td><td>Backtracking</td><td><a href="#backtracking">Backtracking</a></td></tr>
<tr><td>Grid, islands, maze, fewest steps, spreading</td><td>BFS / DFS; multi-source BFS</td><td><a href="#graphs">Graphs</a></td></tr>
<tr><td>Dependencies, prerequisites, ordering from rules</td><td>Topological sort</td><td><a href="#topological-sort">Topo sort</a></td></tr>
<tr><td>Groups merging over time, \"connected?\" after each edge</td><td>Union-find</td><td><a href="#union-find">Union-find</a></td></tr>
<tr><td>Weighted edges, cheapest route, minimize the maximum on a path</td><td>Dijkstra (0-1 BFS for 0/1 weights)</td><td><a href="#shortest-paths">Shortest paths</a></td></tr>
<tr><td>Prefixes, autocomplete, many words in one grid</td><td>Trie</td><td><a href="#tries">Tries</a></td></tr>
<tr><td>\"Number of ways\", \"min/max cost\", choices affect the future</td><td>Dynamic programming</td><td><a href="#dp-1d">DP 1</a>, <a href="#dp-2d">DP 2</a></td></tr>
<tr><td>Subset under a budget; modes like holding/sold; n ≤ 20 \"visit all\"</td><td>Knapsack / state machine / bitmask DP</td><td><a href="#dp-advanced">DP 3</a></td></tr>
<tr><td>Appears twice except one; power of two; huge exponents</td><td>XOR and bit tricks</td><td><a href="#bits-math">Bits</a></td></tr>
<tr><td>\"Design a class with O(1) operations\"</td><td>Hash map + list/linked list</td><td><a href="#design">Design</a></td></tr>
<tr><td>Range queries with updates; substring repeats</td><td>Fenwick / segment tree; rolling hash</td><td><a href="#advanced">Advanced</a></td></tr>
</tbody></table></div>

<h3>When you are stuck, ask these in order</h3>
<ol>
<li>What does the brute force do, and which part of it repeats work?</li>
<li>Would sorting the input make it easier?</li>
<li>Could a hash map remember something useful as I scan?</li>
<li>Is this secretly a graph? What are the nodes and edges?</li>
<li>Can I solve it for the first i items and extend to i + 1? (DP)</li>
<li>Can I guess the answer and check it quickly? (Binary search on the answer)</li>
</ol>
""",
}

MORE = {
    "id": "more-practice",
    "nav": "More Google-tagged practice",
    "title": "More Google-tagged problems to practice",
    "body": """
<p>Once you can solve the problems in this notebook cold, work through these. They are commonly reported for Google and each one reuses a pattern from above. Search the number on LeetCode.</p>
<div class="tbl"><table>
<thead><tr><th>LC</th><th>Problem</th><th>Level</th><th>Pattern</th></tr></thead>
<tbody>
<tr><td class="num-col">482</td><td>License Key Formatting</td><td><span class="chip easy">Easy</span></td><td>Strings</td></tr>
<tr><td class="num-col">359</td><td>Logger Rate Limiter</td><td><span class="chip easy">Easy</span></td><td>Hash map design</td></tr>
<tr><td class="num-col">346</td><td>Moving Average from Data Stream</td><td><span class="chip easy">Easy</span></td><td>Queue design</td></tr>
<tr><td class="num-col">66</td><td>Plus One</td><td><span class="chip easy">Easy</span></td><td>Arrays</td></tr>
<tr><td class="num-col">809</td><td>Expressive Words</td><td><span class="chip med">Medium</span></td><td>Two pointers, run-length groups</td></tr>
<tr><td class="num-col">833</td><td>Find And Replace in String</td><td><span class="chip med">Medium</span></td><td>Sorting, strings</td></tr>
<tr><td class="num-col">681</td><td>Next Closest Time</td><td><span class="chip med">Medium</span></td><td>Enumeration</td></tr>
<tr><td class="num-col">1048</td><td>Longest String Chain</td><td><span class="chip med">Medium</span></td><td>DP over sorted words</td></tr>
<tr><td class="num-col">1423</td><td>Maximum Points You Can Obtain from Cards</td><td><span class="chip med">Medium</span></td><td>Sliding window</td></tr>
<tr><td class="num-col">939</td><td>Minimum Area Rectangle</td><td><span class="chip med">Medium</span></td><td>Hash set of points</td></tr>
<tr><td class="num-col">399</td><td>Evaluate Division</td><td><span class="chip med">Medium</span></td><td>Weighted graph DFS / union-find</td></tr>
<tr><td class="num-col">947</td><td>Most Stones Removed with Same Row or Column</td><td><span class="chip med">Medium</span></td><td>Union-find</td></tr>
<tr><td class="num-col">2096</td><td>Step-By-Step Directions From a Binary Tree Node to Another</td><td><span class="chip med">Medium</span></td><td>LCA, paths</td></tr>
<tr><td class="num-col">2101</td><td>Detonate the Maximum Bombs</td><td><span class="chip med">Medium</span></td><td>Directed graph BFS</td></tr>
<tr><td class="num-col">2034</td><td>Stock Price Fluctuation</td><td><span class="chip med">Medium</span></td><td>Heaps with lazy deletion</td></tr>
<tr><td class="num-col">418</td><td>Sentence Screen Fitting</td><td><span class="chip med">Medium</span></td><td>Simulation, DP</td></tr>
<tr><td class="num-col">843</td><td>Guess the Word</td><td><span class="chip hard">Hard</span></td><td>Minimax heuristics</td></tr>
<tr><td class="num-col">815</td><td>Bus Routes</td><td><span class="chip hard">Hard</span></td><td>BFS over routes</td></tr>
<tr><td class="num-col">403</td><td>Frog Jump</td><td><span class="chip hard">Hard</span></td><td>DP with sets</td></tr>
<tr><td class="num-col">975</td><td>Odd Even Jump</td><td><span class="chip hard">Hard</span></td><td>Monotonic stack + DP</td></tr>
<tr><td class="num-col">715</td><td>Range Module</td><td><span class="chip hard">Hard</span></td><td>Intervals with sorted list</td></tr>
<tr><td class="num-col">1032</td><td>Stream of Characters</td><td><span class="chip hard">Hard</span></td><td>Reversed trie</td></tr>
<tr><td class="num-col">489</td><td>Robot Room Cleaner</td><td><span class="chip hard">Hard</span></td><td>Backtracking DFS with orientation</td></tr>
</tbody></table></div>
""",
}

PLAN = {
    "id": "study-plan",
    "nav": "8-week study plan",
    "title": "An 8-week study plan",
    "body": """
<p>About 1.5 to 2 hours on weekdays and a longer session on weekends. If you have less time, stretch it; don't skip the review days. Spaced repetition beats cramming: re-solve old problems from memory every weekend.</p>
<div class="tbl"><table>
<thead><tr><th>Week</th><th>Learn</th><th>Practice goal</th></tr></thead>
<tbody>
<tr><td class="num-col">1</td><td>Format, 45-minute plan, Big-O, Python toolkit, hashing, two pointers</td><td>All easy problems in those sections. Write the templates from memory by Sunday.</td></tr>
<tr><td class="num-col">2</td><td>Sliding window, prefix sums, binary search</td><td>All mediums in those sections. Time yourself: 25 minutes per medium.</td></tr>
<tr><td class="num-col">3</td><td>Stacks, linked lists, trees, BST</td><td>All problems except the hards. Say your approach out loud before coding.</td></tr>
<tr><td class="num-col">4</td><td>Heaps, intervals, greedy, backtracking</td><td>Mediums plus one hard. First mock interview with a friend or a mock-interview service.</td></tr>
<tr><td class="num-col">5</td><td>Graphs (BFS/DFS), topological sort, union-find</td><td>All problems. Google loves this week's material; go slowly.</td></tr>
<tr><td class="num-col">6</td><td>Shortest paths, tries, DP part 1</td><td>All mediums, two hards. Re-solve five problems from weeks 1–3 cold.</td></tr>
<tr><td class="num-col">7</td><td>DP parts 2 and 3, bits and math, design</td><td>All mediums. Two mock interviews, 45 minutes each, in a plain Google Doc.</td></tr>
<tr><td class="num-col">8</td><td>Advanced structures (skim), the Google-tagged list above</td><td>One mock a day. Review every problem you haven't ticked. Rest the day before.</td></tr>
</tbody></table></div>

<h3>How to practice so it sticks</h3>
<ul>
<li><b>Use a plain editor.</b> No autocomplete, no running code until you've traced it by hand. That's the real interview.</li>
<li><b>Talk out loud</b> even when alone. It feels odd at first and makes a big difference on the day.</li>
<li><b>After a solution, write one sentence:</b> \"The key idea was …\". Reread those sentences before interviews.</li>
<li><b>If you're stuck for 25 minutes</b>, read the hint. After 35, read the solution, then close it and write it yourself from scratch the next day.</li>
<li><b>Review mistakes</b>, not just successes. Keep a list of bugs you made (off-by-one, forgot visited, etc.) and check for them when testing.</li>
</ul>

<h3>Don't forget the other rounds</h3>
<p>The Googleyness and Leadership round asks about times you handled ambiguity, disagreed with a teammate, helped others, or made a mistake. Prepare 6 to 8 stories in the STAR format (Situation, Task, Action, Result) and practice them aloud. For L5 and above, prepare system design as well; this repo's <code>system-design-research.md</code> covers it.</p>
""",
}

GLOSSARY = {
    "id": "glossary",
    "nav": "Glossary",
    "title": "Glossary in plain English",
    "body": """
<dl class="gloss">
<dt>Adjacency list</dt><dd>A dict from each node to the list of nodes it connects to. The standard way to store a graph.</dd>
<dt>Amortized</dt><dd>Average cost per operation over a long run, even if one operation is occasionally expensive.</dd>
<dt>Backtracking</dt><dd>Try a choice, explore further, undo it, try the next. Systematic trial and error.</dd>
<dt>BFS</dt><dd>Breadth-first search. Explore nearest first, level by level, with a queue. Finds the fewest steps.</dd>
<dt>Big-O</dt><dd>How running time or memory grows as input grows, ignoring constants.</dd>
<dt>Binary search</dt><dd>Halve the search range each step. Needs sorted data or a yes/no test that flips once.</dd>
<dt>Bitmask</dt><dd>An integer used as a set of small items: bit i is 1 if item i is in the set.</dd>
<dt>Cycle</dt><dd>A path that returns to where it started.</dd>
<dt>DAG</dt><dd>Directed acyclic graph: arrows between nodes and no cycles. Has a topological order.</dd>
<dt>DFS</dt><dd>Depth-first search. Go as deep as possible before backing up. Uses recursion or a stack.</dd>
<dt>Dijkstra</dt><dd>Shortest paths with non-negative weights, always expanding the cheapest known place next (with a heap).</dd>
<dt>Dynamic programming</dt><dd>Solve each subproblem once and store its answer, building up to the full problem.</dd>
<dt>Greedy</dt><dd>Always take the best-looking option now. Correct only when you can argue it never hurts later.</dd>
<dt>Hash map</dt><dd>Key–value storage with O(1) average lookup. Python's <code>dict</code>.</dd>
<dt>Heap</dt><dd>A structure that always gives you the smallest item fast. Python's <code>heapq</code>.</dd>
<dt>In-degree</dt><dd>How many arrows point into a node. In topological sort, how many unmet prerequisites it has.</dd>
<dt>Invariant</dt><dd>Something that stays true every loop iteration, like \"the window has no repeated characters\". Stating it helps you prove correctness.</dd>
<dt>Memoization</dt><dd>Caching a function's results so repeated calls are free. <code>@cache</code> in Python.</dd>
<dt>Monotonic stack</dt><dd>A stack kept in sorted order; popping reveals \"next greater/smaller\" answers.</dd>
<dt>Prefix sum</dt><dd>Running totals, so any range sum is one subtraction.</dd>
<dt>Pruning</dt><dd>Skipping branches of a search that can't lead to a valid or better answer.</dd>
<dt>Sentinel</dt><dd>A fake item (dummy node, extra 0, infinity) that removes edge cases.</dd>
<dt>Sliding window</dt><dd>A range that grows on one side and shrinks on the other as you scan.</dd>
<dt>Stable sort</dt><dd>Equal items keep their original order. Python's sort is stable.</dd>
<dt>Topological order</dt><dd>An order where every item comes after the items it depends on.</dd>
<dt>Trie</dt><dd>A tree of characters where each path spells a prefix. Fast prefix lookups.</dd>
<dt>Union-find</dt><dd>Tracks groups that merge over time; tells you if two items are in the same group.</dd>
</dl>
""",
}

SECTIONS = [FINDER, MORE, PLAN, GLOSSARY]
