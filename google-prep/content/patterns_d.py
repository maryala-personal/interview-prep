"""Patterns 19-24: dynamic programming (three parts), bits and math, design,
advanced data structures."""

DP_STEPS = """
<h3>The four questions that write any DP solution</h3>
<ol class="steps">
<li><div><b>What is the state?</b>Finish the sentence \"<code>dp[i]</code> means …\" in plain words. Example: \"<code>dp[i]</code> is the most money I can rob from the first i houses.\"</div></li>
<li><div><b>What is the recurrence?</b>How does <code>dp[i]</code> follow from smaller states? Usually: look at the last decision. \"Either I rob house i, or I don't.\"</div></li>
<li><div><b>What are the base cases?</b>The smallest states you know without thinking: empty prefix, zero amount, first row.</div></li>
<li><div><b>What order fills the table?</b>Every state must be computed after the states it depends on. Then read off the answer.</div></li>
</ol>
<p>Start top-down (a recursive function with <code>@cache</code>) if that's easier to think about; it's accepted at Google. Then offer to convert it to a bottom-up table, and if each row only depends on the previous row, shrink the table to one or two rows.</p>
"""

DP_1D = {
    "id": "dp-1d",
    "nav": "DP 1: one dimension",
    "title": "Dynamic programming, part 1: one dimension",
    "tagline": "Solve each small version of the problem once, write the answer down, and build up to the full problem.",
    "plain": """
<p>Dynamic programming (DP) is <b>recursion plus a notebook</b>. Many problems break into smaller versions of themselves, and those smaller versions overlap: the plain recursion solves the same subproblem again and again. DP stores each answer the first time, so each subproblem is solved once.</p>
<p>Two ways to write it:</p>
<ul>
<li><b>Top-down (memoization):</b> write the natural recursion and add <code>@cache</code>. Easy to get right.</li>
<li><b>Bottom-up (tabulation):</b> fill an array from the smallest case upward with a loop. No recursion limit, and often easy to shrink to O(1) memory.</li>
</ul>
<div class="analogy"><b>Picture it:</b> someone asks you what 1+1+1+1+1 is. You count: 5. They add another \"+1\". You don't recount; you say 6 because you remembered 5. That's DP.</div>
""",
    "signals": [
        "\"Number of ways to …\"",
        "\"Minimum / maximum cost / profit / length\" where choices affect later choices",
        "\"Is it possible to …\" with overlapping choices (word break, partition)",
        "A greedy approach has a counterexample",
        "The brute force is a recursion that repeats the same calls",
    ],
    "pitfalls": [
        "Not being able to say in words what <code>dp[i]</code> means. Say it first",
        "Off-by-one between \"first i items\" and \"index i\". Using size n + 1 with <code>dp[0]</code> as the empty case avoids most of them",
        "Using a mutable default or a global cache that leaks between test cases",
        "Jumping to DP when greedy or a formula is enough",
    ],
    "template": '''
from functools import cache

def house_robber_top_down(nums: list[int]) -> int:
    @cache
    def best(i: int) -> int:               # best from houses i..end
        if i >= len(nums):
            return 0
        return max(best(i + 1),            # skip house i
                   nums[i] + best(i + 2))  # rob house i
    return best(0)

def house_robber_bottom_up(nums: list[int]) -> int:
    # dp[i] = best from the first i houses; only the last two values matter
    prev2, prev1 = 0, 0
    for x in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1

assert house_robber_top_down([2, 7, 9, 3, 1]) == 12
assert house_robber_bottom_up([2, 7, 9, 3, 1]) == 12
''',
    "complexity": "(number of states) × (work per state). Here O(n) time; O(1) space bottom-up.",
    "extra": DP_STEPS,
    "problems": [
        {
            "name": "Climbing Stairs",
            "lc": 70,
            "level": "E",
            "prompt": "<p>You climb 1 or 2 steps at a time. How many distinct ways reach step n?</p><pre>n = 3  →  3   (1+1+1, 1+2, 2+1)</pre>",
            "hint": "The last move was either a 1-step or a 2-step.",
            "idea": "<p>Ways to reach step n = ways to reach n − 1 (then take 1) + ways to reach n − 2 (then take 2). That's the Fibonacci sequence. Keep just the last two values.</p>",
            "code": '''
def climb_stairs(n: int) -> int:
    a, b = 1, 1               # ways to reach step 0 and step 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b

assert climb_stairs(1) == 1
assert climb_stairs(2) == 2
assert climb_stairs(3) == 3
assert climb_stairs(5) == 8
''',
            "complexity": "O(n) time, O(1) space.",
        },
        {
            "name": "House Robber",
            "lc": 198,
            "level": "M",
            "prompt": "<p>You can't rob two adjacent houses. Maximize the money.</p><pre>[2,7,9,3,1]  →  12   (2 + 9 + 1)</pre>",
            "hint": "At house i: rob it (and add the best up to i − 2) or skip it (best up to i − 1).",
            "idea": "<p><code>dp[i] = max(dp[i−1], dp[i−2] + nums[i])</code>. Only the last two values are needed. See the template above.</p>",
            "code": '''
def rob(nums: list[int]) -> int:
    prev2 = prev1 = 0
    for x in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1

def rob_circle(nums: list[int]) -> int:
    """House Robber II (LC 213): houses in a circle. First and last can't both be robbed."""
    if len(nums) == 1:
        return nums[0]
    return max(rob(nums[1:]), rob(nums[:-1]))

assert rob([1, 2, 3, 1]) == 4
assert rob([2, 7, 9, 3, 1]) == 12
assert rob_circle([2, 3, 2]) == 3
assert rob_circle([1, 2, 3, 1]) == 4
''',
            "complexity": "O(n) time, O(1) space.",
        },
        {
            "name": "Coin Change",
            "lc": 322,
            "level": "M",
            "hot": True,
            "prompt": "<p>Fewest coins to make <code>amount</code> using unlimited coins of the given values, or −1.</p><pre>coins = [1,2,5], amount = 11  →  3   (5 + 5 + 1)</pre>",
            "hint": "dp[a] = fewest coins for amount a. The last coin used could be any coin c.",
            "idea": "<p>Greedy (largest coin first) fails for some coin sets. Instead, <code>dp[a] = 1 + min(dp[a − c])</code> over all coins c that fit. <code>dp[0] = 0</code>. Fill amounts from 0 up. Unreachable amounts stay at infinity.</p>",
            "code": '''
def coin_change(coins: list[int], amount: int) -> int:
    INF = float("inf")
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] != INF else -1

assert coin_change([1, 2, 5], 11) == 3
assert coin_change([2], 3) == -1
assert coin_change([1], 0) == 0
assert coin_change([1, 3, 4], 6) == 2          # greedy would give 3
''',
            "complexity": "O(amount · coins) time, O(amount) space.",
        },
        {
            "name": "Decode Ways",
            "lc": 91,
            "level": "M",
            "hot": True,
            "prompt": "<p>Letters map to numbers A=1 … Z=26. How many ways can a digit string be decoded?</p><pre>\"226\"  →  3   (2 2 6, 22 6, 2 26)\n\"06\"   →  0</pre>",
            "hint": "The last piece is either one digit (1–9) or two digits (10–26).",
            "idea": "<p><code>dp[i]</code> = ways to decode the first i characters. Add <code>dp[i−1]</code> if the last digit is 1–9. Add <code>dp[i−2]</code> if the last two digits form 10–26. Zeros are the trap: \"0\" alone is invalid, and \"06\" isn't 6.</p>",
            "code": '''
def num_decodings(s: str) -> int:
    prev2, prev1 = 0, 1                     # dp[i-2], dp[i-1]; dp[0] = 1
    for i in range(1, len(s) + 1):
        cur = 0
        if s[i - 1] != "0":
            cur += prev1
        if i >= 2 and 10 <= int(s[i - 2:i]) <= 26:
            cur += prev2
        prev2, prev1 = prev1, cur
    return prev1

assert num_decodings("12") == 2
assert num_decodings("226") == 3
assert num_decodings("06") == 0
assert num_decodings("11106") == 2
''',
            "complexity": "O(n) time, O(1) space.",
        },
        {
            "name": "Word Break",
            "lc": 139,
            "level": "M",
            "hot": True,
            "prompt": "<p>Can <code>s</code> be split into a sequence of dictionary words?</p><pre>\"applepenapple\", [\"apple\",\"pen\"]  →  True\n\"catsandog\", [\"cats\",\"dog\",\"sand\",\"and\",\"cat\"]  →  False</pre>",
            "hint": "dp[i] = can the first i characters be split? Look at what the last word could be.",
            "idea": "<p><code>dp[0]</code> is True (the empty string). <code>dp[i]</code> is True if some <code>j &lt; i</code> has <code>dp[j]</code> True and <code>s[j:i]</code> is a word. Only check lengths up to the longest word to save time.</p>",
            "code": '''
def word_break(s: str, word_dict: list[str]) -> bool:
    words = set(word_dict)
    longest = max(map(len, words), default=0)
    dp = [True] + [False] * len(s)
    for i in range(1, len(s) + 1):
        for j in range(max(0, i - longest), i):
            if dp[j] and s[j:i] in words:
                dp[i] = True
                break
    return dp[len(s)]

assert word_break("leetcode", ["leet", "code"])
assert word_break("applepenapple", ["apple", "pen"])
assert not word_break("catsandog", ["cats", "dog", "sand", "and", "cat"])
''',
            "complexity": "O(n · L²) time with L = longest word (slicing costs L), O(n) space.",
            "followups": ["Return all sentences (LC 140): memoized DFS returning lists; output can be exponential."],
        },
        {
            "name": "Longest Increasing Subsequence",
            "lc": 300,
            "level": "M",
            "hot": True,
            "prompt": "<p>Length of the longest strictly increasing subsequence (not necessarily contiguous).</p><pre>[10,9,2,5,3,7,101,18]  →  4   (2, 3, 7, 18)</pre>",
            "hint": "O(n²): dp[i] = longest ending at i. O(n log n): keep the smallest possible tail for each length.",
            "idea": "<p><b>O(n²) DP:</b> <code>dp[i] = 1 + max(dp[j])</code> for <code>j &lt; i</code> with <code>nums[j] &lt; nums[i]</code>.</p><p><b>O(n log n) \"patience\":</b> keep <code>tails[k]</code> = the smallest tail value of any increasing subsequence of length k + 1. For each number, binary-search the first tail ≥ it and replace it (or append if none). The length of <code>tails</code> is the answer. Smaller tails leave more room to grow.</p>",
            "code": '''
from bisect import bisect_left

def length_of_lis(nums: list[int]) -> int:
    tails = []
    for x in nums:
        i = bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)          # extends the longest subsequence
        else:
            tails[i] = x             # a smaller tail for length i + 1
    return len(tails)

def length_of_lis_quadratic(nums: list[int]) -> int:
    dp = [1] * len(nums)
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp, default=0)

for f in (length_of_lis, length_of_lis_quadratic):
    assert f([10, 9, 2, 5, 3, 7, 101, 18]) == 4
    assert f([0, 1, 0, 3, 2, 3]) == 4
    assert f([7, 7, 7, 7]) == 1
''',
            "complexity": "O(n log n) time, O(n) space.",
            "followups": ["Russian Doll Envelopes (LC 354): sort by width ascending and height descending, then LIS on heights."],
        },
        {
            "name": "Maximum Profit in Job Scheduling",
            "lc": 1235,
            "level": "H",
            "hot": True,
            "prompt": "<p>Jobs have start, end and profit. Pick non-overlapping jobs (a job may start exactly when another ends) to maximize total profit.</p><pre>start = [1,2,3,3], end = [3,4,5,6], profit = [50,10,40,70]  →  120</pre>",
            "hint": "Sort by end time. For each job: skip it, or take it plus the best answer among jobs that end by its start.",
            "idea": "<p>Sort jobs by end time. <code>dp[i]</code> = best profit using the first i jobs. For job i: skip it (<code>dp[i−1]</code>), or take it: its profit plus <code>dp[j]</code>, where j is the number of jobs ending at or before this job's start. Binary search finds j. This is weighted interval scheduling: DP plus binary search.</p>",
            "code": '''
from bisect import bisect_right

def job_scheduling(start: list[int], end: list[int], profit: list[int]) -> int:
    jobs = sorted(zip(end, start, profit))
    ends = [e for e, _, _ in jobs]
    dp = [0] * (len(jobs) + 1)
    for i, (e, s, p) in enumerate(jobs, 1):
        j = bisect_right(ends, s, 0, i - 1)     # jobs ending by time s
        dp[i] = max(dp[i - 1], dp[j] + p)
    return dp[-1]

assert job_scheduling([1, 2, 3, 3], [3, 4, 5, 6], [50, 10, 40, 70]) == 120
assert job_scheduling([1, 2, 3, 4, 6], [3, 5, 10, 6, 9], [20, 20, 100, 70, 60]) == 150
assert job_scheduling([1, 1, 1], [2, 3, 4], [5, 6, 4]) == 6
''',
            "complexity": "O(n log n) time, O(n) space.",
        },
    ],
}

DP_2D = {
    "id": "dp-2d",
    "nav": "DP 2: grids and strings",
    "title": "Dynamic programming, part 2: grids and two strings",
    "tagline": "When the state needs two numbers (a row and a column, or a position in each of two strings), the table becomes 2D.",
    "plain": """
<p>Some problems need two indices to describe a subproblem. The most common cases:</p>
<ul>
<li><b>Grids:</b> <code>dp[r][c]</code> = answer for reaching or starting from cell <code>(r, c)</code>.</li>
<li><b>Two strings:</b> <code>dp[i][j]</code> = answer for the first i characters of one string and the first j of the other. Look at the last characters: do they match or not?</li>
<li><b>One string, a range:</b> <code>dp[i][j]</code> = answer for the substring <code>s[i..j]</code> (palindromes).</li>
</ul>
<p>Draw the table for a tiny example. Seeing which neighboring cells each cell uses tells you the loop order, and whether you can keep just one row.</p>
<div class="analogy"><b>Picture it:</b> comparing two DNA strands letter by letter in a spreadsheet. Each cell answers \"how similar are these two prefixes?\" using the cell above, to the left, and diagonally up-left.</div>
""",
    "signals": [
        "Paths in a grid moving only right/down",
        "Two strings: common subsequence, edit distance, interleaving, matching with wildcards",
        "Palindromic substrings or subsequences",
        "The 1D state doesn't carry enough information",
    ],
    "pitfalls": [
        "Mixing up <code>dp[i][j]</code> (prefix lengths) with <code>s[i]</code> (a character index). With prefix lengths, the characters are <code>s[i−1]</code> and <code>t[j−1]</code>",
        "Filling in the wrong order: range DP must go by increasing length, not by i",
        "Wasting memory: say you could reduce to O(n) once the O(n²) version works",
    ],
    "template": '''
def lcs(a: str, b: str) -> int:
    """dp[i][j] = LCS of a[:i] and b[:j]."""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]   # row 0 and col 0: empty prefixes
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1           # use both characters
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])  # drop one of them
    return dp[m][n]

assert lcs("abcde", "ace") == 3
''',
    "complexity": "O(m · n) time, O(m · n) space (often reducible to O(n)).",
    "problems": [
        {
            "name": "Pascal's Triangle",
            "lc": 118,
            "level": "E",
            "prompt": "<p>Return the first <code>num_rows</code> rows of Pascal's triangle.</p><pre>5  →  [[1],[1,1],[1,2,1],[1,3,3,1],[1,4,6,4,1]]</pre>",
            "hint": "Each inner value is the sum of the two values above it.",
            "idea": "<p>The simplest 2D table: each row is built from the previous one. A gentle way to practice thinking about table cells.</p>",
            "code": '''
def generate(num_rows: int) -> list[list[int]]:
    rows = [[1]]
    for _ in range(num_rows - 1):
        prev = rows[-1]
        rows.append([1] + [prev[i] + prev[i + 1] for i in range(len(prev) - 1)] + [1])
    return rows[:num_rows]

assert generate(5) == [[1], [1, 1], [1, 2, 1], [1, 3, 3, 1], [1, 4, 6, 4, 1]]
assert generate(1) == [[1]]
''',
            "complexity": "O(n²) time and space.",
        },
        {
            "name": "Unique Paths",
            "lc": 62,
            "level": "M",
            "prompt": "<p>A robot at the top-left of an m × n grid moves only right or down. How many paths reach the bottom-right?</p><pre>m = 3, n = 7  →  28</pre>",
            "hint": "Paths into a cell = paths into the cell above + paths into the cell to the left.",
            "idea": "<p><code>dp[r][c] = dp[r−1][c] + dp[r][c−1]</code>, with the first row and column all 1. Each row only needs the row above, so one array updated in place is enough: <code>row[c] += row[c−1]</code>.</p>",
            "code": '''
def unique_paths(m: int, n: int) -> int:
    row = [1] * n
    for _ in range(1, m):
        for c in range(1, n):
            row[c] += row[c - 1]      # above (old row[c]) + left (new row[c-1])
    return row[-1]

def unique_paths_with_obstacles(grid: list[list[int]]) -> int:
    """LC 63: cells with 1 are blocked."""
    n = len(grid[0])
    row = [0] * n
    row[0] = 1
    for r in grid:
        for c in range(n):
            if r[c] == 1:
                row[c] = 0
            elif c > 0:
                row[c] += row[c - 1]
    return row[-1]

assert unique_paths(3, 7) == 28
assert unique_paths(3, 2) == 3
assert unique_paths_with_obstacles([[0, 0, 0], [0, 1, 0], [0, 0, 0]]) == 2
''',
            "complexity": "O(m · n) time, O(n) space.",
        },
        {
            "name": "Longest Common Subsequence",
            "lc": 1143,
            "level": "M",
            "prompt": "<p>Length of the longest subsequence common to both strings.</p><pre>\"abcde\", \"ace\"  →  3</pre>",
            "hint": "If the last characters match, use them both. If not, drop one or the other.",
            "idea": "<p>The template above. Here is the space-saving version with two rows. This recurrence is the basis for diff tools and DNA alignment.</p>",
            "code": '''
def longest_common_subsequence(a: str, b: str) -> int:
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = max(prev[j], cur[j - 1])
        prev = cur
    return prev[-1]

assert longest_common_subsequence("abcde", "ace") == 3
assert longest_common_subsequence("abc", "abc") == 3
assert longest_common_subsequence("abc", "def") == 0
''',
            "complexity": "O(m · n) time, O(n) space.",
        },
        {
            "name": "Longest Palindromic Substring",
            "lc": 5,
            "level": "M",
            "hot": True,
            "prompt": "<p>Return the longest palindromic substring.</p><pre>\"babad\"  →  \"bab\" (or \"aba\")\n\"cbbd\"   →  \"bb\"</pre>",
            "hint": "Every palindrome has a center: one character, or the gap between two.",
            "idea": "<p>The DP version fills <code>dp[i][j]</code> = is <code>s[i..j]</code> a palindrome, in O(n²) space. The simpler interview answer: <b>expand around each center</b>. There are 2n − 1 centers; from each, grow outward while both ends match. Same O(n²) time, O(1) space.</p>",
            "code": '''
def longest_palindrome(s: str) -> str:
    def expand(lo: int, hi: int) -> tuple[int, int]:
        while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
            lo -= 1
            hi += 1
        return lo + 1, hi                  # s[lo+1:hi] is the palindrome
    best = (0, 0)
    for center in range(len(s)):
        for lo, hi in (expand(center, center), expand(center, center + 1)):
            if hi - lo > best[1] - best[0]:
                best = (lo, hi)
    return s[best[0]:best[1]]

assert longest_palindrome("babad") in ("bab", "aba")
assert longest_palindrome("cbbd") == "bb"
assert longest_palindrome("a") == "a"
''',
            "complexity": "O(n²) time, O(1) space. (Manacher's algorithm is O(n) but rarely expected.)",
        },
        {
            "name": "Edit Distance",
            "lc": 72,
            "level": "M",
            "hot": True,
            "prompt": "<p>Minimum insertions, deletions, or replacements to turn <code>word1</code> into <code>word2</code>.</p><pre>\"horse\" → \"ros\"  →  3</pre>",
            "hint": "Compare the last characters. If equal, no cost. Otherwise try each of the three operations.",
            "idea": "<p><code>dp[i][j]</code> = edits to turn the first i letters of word1 into the first j of word2. Base cases: turning i letters into nothing takes i deletions; nothing into j letters takes j insertions. If the last letters match, <code>dp[i][j] = dp[i−1][j−1]</code>. Otherwise 1 + the min of: replace (<code>dp[i−1][j−1]</code>), delete (<code>dp[i−1][j]</code>), insert (<code>dp[i][j−1]</code>).</p>",
            "code": '''
def min_distance(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j - 1],   # replace
                                   dp[i - 1][j],       # delete
                                   dp[i][j - 1])       # insert
    return dp[m][n]

assert min_distance("horse", "ros") == 3
assert min_distance("intention", "execution") == 5
assert min_distance("", "abc") == 3
''',
            "complexity": "O(m · n) time and space (O(n) with two rows).",
            "followups": ["One Edit Distance (LC 161): just check in O(n) whether the distance is exactly 1."],
        },
        {
            "name": "Regular Expression Matching",
            "lc": 10,
            "level": "H",
            "prompt": "<p>Match string <code>s</code> against pattern <code>p</code> where <code>.</code> matches any character and <code>x*</code> matches zero or more of x. The match must cover all of s.</p><pre>\"aab\", \"c*a*b\"  →  True\n\"mississippi\", \"mis*is*p*.\"  →  False</pre>",
            "hint": "dp[i][j] = does s[i:] match p[j:]? The star case has two choices: use zero copies, or use one and stay on the star.",
            "idea": "<p>Work from the ends backwards. <code>first</code> = does <code>s[i]</code> match <code>p[j]</code>? If <code>p[j+1]</code> is a star, either skip the <code>x*</code> entirely (<code>dp[i][j+2]</code>), or if the first character matches, consume one character of s and keep the star (<code>dp[i+1][j]</code>). Otherwise both advance by one.</p>",
            "code": '''
def is_match(s: str, p: str) -> bool:
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[m][n] = True                                   # empty matches empty
    for i in range(m, -1, -1):
        for j in range(n - 1, -1, -1):
            first = i < m and p[j] in (s[i], ".")
            if j + 1 < n and p[j + 1] == "*":
                dp[i][j] = dp[i][j + 2] or (first and dp[i + 1][j])
            else:
                dp[i][j] = first and dp[i + 1][j + 1]
    return dp[0][0]

assert not is_match("aa", "a")
assert is_match("aa", "a*")
assert is_match("ab", ".*")
assert is_match("aab", "c*a*b")
assert not is_match("mississippi", "mis*is*p*.")
''',
            "complexity": "O(m · n) time and space.",
            "followups": ["Wildcard Matching (LC 44): <code>?</code> and <code>*</code> where * matches any sequence; very similar table."],
        },
    ],
}

DP_MORE = {
    "id": "dp-advanced",
    "nav": "DP 3: knapsack, states, masks",
    "title": "Dynamic programming, part 3: knapsack, state machines, intervals, bitmasks",
    "tagline": "The remaining DP shapes. Recognize the family and the state almost writes itself.",
    "plain": """
<p>Most harder DP problems belong to one of a few families. Learn to name the family and you'll know the state:</p>
<div class="tbl"><table>
<thead><tr><th>Family</th><th>State</th><th>Sounds like</th></tr></thead>
<tbody>
<tr><td><b>0/1 knapsack</b></td><td><code>dp[capacity]</code>, loop capacity <i>downward</i> so each item is used once</td><td>\"pick a subset with sum/weight exactly or at most X\"</td></tr>
<tr><td><b>Unbounded knapsack</b></td><td><code>dp[capacity]</code>, loop capacity <i>upward</i> so items can repeat</td><td>\"unlimited coins\", \"ways to make change\"</td></tr>
<tr><td><b>State machine</b></td><td><code>dp[i][state]</code> for a few named states</td><td>\"holding / not holding a stock\", \"cooldown\"</td></tr>
<tr><td><b>Interval</b></td><td><code>dp[i][j]</code> over a range, try every split point k</td><td>\"burst\", \"merge stones\", \"cut a stick\", palindrome partitioning</td></tr>
<tr><td><b>Bitmask</b></td><td><code>dp[mask][i]</code>, mask = set of items used</td><td>n ≤ 20, \"visit all\", \"assign each person a task\"</td></tr>
</tbody></table></div>
<div class="analogy"><b>Picture it:</b> packing a suitcase with a weight limit. For each item you decide: take it or leave it. The notebook records \"the best value I can pack with this much weight left\".</div>
""",
    "signals": [
        "Choose a subset under a budget → knapsack",
        "A few modes you switch between (holding, sold, resting) → state machine",
        "The order of operations inside a range matters → interval DP",
        "n ≤ 20 and \"all items / visit everything\" → bitmask",
    ],
    "pitfalls": [
        "Looping capacity upward in 0/1 knapsack (accidentally reuses items)",
        "For counting combinations, putting the coin loop inside the amount loop (counts orderings instead)",
        "In interval DP, iterating by start index instead of by length",
    ],
    "template": '''
def knapsack_01(weights: list[int], values: list[int], cap: int) -> int:
    dp = [0] * (cap + 1)                  # dp[c] = best value with capacity c
    for w, v in zip(weights, values):
        for c in range(cap, w - 1, -1):   # downward: each item once
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[cap]

def count_ways_unbounded(coins: list[int], amount: int) -> int:
    dp = [1] + [0] * amount               # dp[a] = combinations making a
    for coin in coins:                    # coins outer: combinations, not orders
        for a in range(coin, amount + 1): # upward: coins can repeat
            dp[a] += dp[a - coin]
    return dp[amount]

assert knapsack_01([1, 3, 4], [15, 20, 30], 4) == 35
assert count_ways_unbounded([1, 2, 5], 5) == 4
''',
    "complexity": "Knapsack O(n · capacity). Interval O(n³). Bitmask O(2ⁿ · n²).",
    "problems": [
        {
            "name": "Min Cost Climbing Stairs",
            "lc": 746,
            "level": "E",
            "prompt": "<p><code>cost[i]</code> is paid when you step on stair i. Start at stair 0 or 1, climb 1 or 2 at a time. Minimum cost to get past the top?</p><pre>[10,15,20]  →  15</pre>",
            "hint": "Cost to stand on stair i = cost[i] + cheaper of the two stairs below.",
            "idea": "<p>A warm-up for thinking in states: <code>dp[i] = cost[i] + min(dp[i−1], dp[i−2])</code>. The top is reached from either of the last two stairs.</p>",
            "code": '''
def min_cost_climbing_stairs(cost: list[int]) -> int:
    a, b = 0, 0                       # cheapest to stand on the two previous stairs
    for c in cost:
        a, b = b, c + min(a, b)
    return min(a, b)

assert min_cost_climbing_stairs([10, 15, 20]) == 15
assert min_cost_climbing_stairs([1, 100, 1, 1, 1, 100, 1, 1, 100, 1]) == 6
''',
            "complexity": "O(n) time, O(1) space.",
        },
        {
            "name": "Partition Equal Subset Sum",
            "lc": 416,
            "level": "M",
            "hot": True,
            "prompt": "<p>Can the list be split into two subsets with equal sums?</p><pre>[1,5,11,5]  →  True   ([1,5,5] and [11])</pre>",
            "hint": "Find a subset summing to half the total. That's 0/1 knapsack with booleans.",
            "idea": "<p>If the total is odd, no. Otherwise, can some subset reach <code>total / 2</code>? <code>dp[s]</code> = some subset sums to s. For each number, go through sums downward: <code>dp[s] |= dp[s − x]</code>. A Python trick: a big integer used as a bitset, <code>bits |= bits &lt;&lt; x</code>, does the same thing very quickly.</p>",
            "code": '''
def can_partition(nums: list[int]) -> bool:
    total = sum(nums)
    if total % 2:
        return False
    target = total // 2
    dp = [True] + [False] * target
    for x in nums:
        for s in range(target, x - 1, -1):
            dp[s] = dp[s] or dp[s - x]
    return dp[target]

def can_partition_bitset(nums: list[int]) -> bool:
    total = sum(nums)
    bits = 1                              # bit s set = sum s reachable
    for x in nums:
        bits |= bits << x
    return total % 2 == 0 and bool(bits >> (total // 2) & 1)

for f in (can_partition, can_partition_bitset):
    assert f([1, 5, 11, 5])
    assert not f([1, 2, 3, 5])
''',
            "complexity": "O(n · sum) time, O(sum) space.",
        },
        {
            "name": "Coin Change II",
            "lc": 518,
            "level": "M",
            "prompt": "<p>Number of combinations (not orderings) of coins that make <code>amount</code>.</p><pre>amount = 5, coins = [1,2,5]  →  4</pre>",
            "hint": "Put the coin loop on the outside so each combination is counted once.",
            "idea": "<p>Unbounded knapsack counting. With coins in the outer loop, you decide how many of coin 1 to use, then coin 2, and so on, so <code>1+2</code> and <code>2+1</code> are the same combination. Swapping the loops would count orderings instead (that's LC 377, Combination Sum IV).</p>",
            "code": '''
def change(amount: int, coins: list[int]) -> int:
    dp = [1] + [0] * amount
    for coin in coins:
        for a in range(coin, amount + 1):
            dp[a] += dp[a - coin]
    return dp[amount]

assert change(5, [1, 2, 5]) == 4
assert change(3, [2]) == 0
assert change(10, [10]) == 1
''',
            "complexity": "O(amount · coins) time, O(amount) space.",
        },
        {
            "name": "Best Time to Buy and Sell Stock with Cooldown",
            "lc": 309,
            "level": "M",
            "prompt": "<p>Unlimited transactions, but after selling you must wait one day before buying again. Maximize profit.</p><pre>[1,2,3,0,2]  →  3   (buy, sell, cooldown, buy, sell)</pre>",
            "hint": "Each day you're in one of three states: holding a share, just sold, or resting.",
            "idea": "<p>Track the best profit in each state at the end of each day:</p><ul><li><b>hold</b>: keep holding, or buy today from <b>rest</b>.</li><li><b>sold</b>: sell today from <b>hold</b>.</li><li><b>rest</b>: stay resting, or come off yesterday's cooldown from <b>sold</b>.</li></ul><p>Drawing these three states as circles with arrows is the whole solution. All stock problems (k transactions, fees) are variations of this state machine.</p>",
            "code": '''
def max_profit_cooldown(prices: list[int]) -> int:
    hold, sold, rest = float("-inf"), 0, 0
    for p in prices:
        hold, sold, rest = max(hold, rest - p), hold + p, max(rest, sold)
    return max(sold, rest)

assert max_profit_cooldown([1, 2, 3, 0, 2]) == 3
assert max_profit_cooldown([1]) == 0
''',
            "complexity": "O(n) time, O(1) space.",
        },
        {
            "name": "Burst Balloons",
            "lc": 312,
            "level": "H",
            "prompt": "<p>Bursting balloon i earns <code>left × nums[i] × right</code>, using its current neighbors (1 beyond the edges). Maximize the total.</p><pre>[3,1,5,8]  →  167</pre>",
            "hint": "Instead of which balloon to burst first, ask which balloon in a range is burst <b>last</b>.",
            "idea": "<p>Pad with 1 on both ends. <code>dp[i][j]</code> = best coins from bursting everything strictly between i and j. If k is the <b>last</b> balloon burst in that gap, its neighbors at that moment are exactly i and j, and the two sides are independent: <code>dp[i][k] + nums[i]·nums[k]·nums[j] + dp[k][j]</code>. Fill by increasing gap length. \"Think about the last step\" is the key to interval DP.</p>",
            "code": '''
def max_coins(nums: list[int]) -> int:
    vals = [1] + nums + [1]
    n = len(vals)
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n):                 # distance between i and j
        for i in range(n - length):
            j = i + length
            dp[i][j] = max(dp[i][k] + vals[i] * vals[k] * vals[j] + dp[k][j]
                           for k in range(i + 1, j))
    return dp[0][n - 1]

assert max_coins([3, 1, 5, 8]) == 167
assert max_coins([1, 5]) == 10
''',
            "complexity": "O(n³) time, O(n²) space.",
        },
        {
            "name": "Shortest Path Visiting All Nodes",
            "lc": 847,
            "level": "H",
            "prompt": "<p>An undirected connected graph with n ≤ 12 nodes. Return the length of the shortest walk that visits every node (you may start and end anywhere and revisit nodes).</p><pre>[[1,2,3],[0],[0],[0]]  →  4</pre>",
            "hint": "The state is (current node, set of nodes visited). Encode the set as a bitmask.",
            "idea": "<p>n ≤ 12 is the clue for bitmasks: a set of visited nodes fits in an integer, bit i set meaning node i was visited. BFS over states <code>(node, mask)</code>, starting from every node at once. The first time any state has all bits set, that's the answer. There are n · 2ⁿ states.</p>",
            "code": '''
from collections import deque

def shortest_path_length(graph: list[list[int]]) -> int:
    n = len(graph)
    full = (1 << n) - 1
    queue = deque((i, 1 << i, 0) for i in range(n))
    seen = {(i, 1 << i) for i in range(n)}
    while queue:
        node, mask, dist = queue.popleft()
        if mask == full:
            return dist
        for nxt in graph[node]:
            state = (nxt, mask | (1 << nxt))
            if state not in seen:
                seen.add(state)
                queue.append((nxt, state[1], dist + 1))
    return 0

assert shortest_path_length([[1, 2, 3], [0], [0], [0]]) == 4
assert shortest_path_length([[1], [0, 2, 4], [1, 3, 4], [2], [1, 2]]) == 4
assert shortest_path_length([[]]) == 0
''',
            "complexity": "O(2ⁿ · n²) time, O(2ⁿ · n) space.",
        },
    ],
}

BITS = {
    "id": "bits-math",
    "nav": "Bits and math",
    "title": "Bit manipulation and math",
    "tagline": "A handful of tricks with binary numbers and arithmetic that turn some problems into one-liners.",
    "plain": """
<p>Computers store numbers in binary. A few operators let you work on individual bits:</p>
<div class="tbl"><table>
<thead><tr><th>Trick</th><th>Python</th><th>Why it works</th></tr></thead>
<tbody>
<tr><td>Is bit i set?</td><td><code>(x &gt;&gt; i) &amp; 1</code></td><td>Shift bit i to the end, then keep only it</td></tr>
<tr><td>Set bit i</td><td><code>x | (1 &lt;&lt; i)</code></td><td>OR with a single 1 in position i</td></tr>
<tr><td>Clear the lowest set bit</td><td><code>x &amp; (x − 1)</code></td><td>Subtracting 1 flips the lowest 1 and the 0s after it</td></tr>
<tr><td>Is x a power of two?</td><td><code>x &gt; 0 and x &amp; (x − 1) == 0</code></td><td>Powers of two have exactly one 1 bit</td></tr>
<tr><td>Cancel pairs</td><td><code>a ^ a == 0</code>, <code>a ^ 0 == a</code></td><td>XOR of equal numbers is zero, so pairs cancel</td></tr>
<tr><td>Count 1 bits</td><td><code>x.bit_count()</code> (3.10+) or <code>bin(x).count("1")</code></td><td></td></tr>
</tbody></table></div>
<p>Math tools worth knowing: <code>math.gcd</code>, modular arithmetic (<code>pow(a, b, mod)</code> is fast), the sieve of Eratosthenes for primes, and fast exponentiation by squaring.</p>
<div class="analogy"><b>Picture it:</b> XOR is a light switch. Flip it twice and it's back where it started. So if every number appears twice except one, XOR-ing everything leaves only the odd one out.</div>
""",
    "signals": [
        "\"Every element appears twice except one\"",
        "Sets of up to ~20 items (represent the set as bits)",
        "\"Without using + or *\", power of two, counting bits",
        "Very large exponents, primes, gcd, answers \"modulo 10⁹ + 7\"",
    ],
    "pitfalls": [
        "Python integers never overflow and negative numbers have infinite leading 1s. Mask with <code>&amp; 0xFFFFFFFF</code> if the problem assumes 32 bits",
        "Operator precedence: <code>x &amp; 1 == 0</code> means <code>x &amp; (1 == 0)</code>. Use parentheses",
        "Forgetting to take the modulo at every step in counting problems (fine in Python, but mention it)",
    ],
    "template": '''
def bit_tricks_demo():
    x = 0b10110
    assert (x >> 1) & 1 == 1            # bit 1 is set
    assert x | (1 << 0) == 0b10111      # set bit 0
    assert x & (x - 1) == 0b10100       # drop the lowest set bit
    assert bin(x).count("1") == 3

    # iterate over all subsets of n items
    n = 3
    subsets = [[i for i in range(n) if mask >> i & 1] for mask in range(1 << n)]
    assert len(subsets) == 8 and subsets[5] == [0, 2]

def fast_pow(base: int, exp: int, mod: int) -> int:
    """Exponentiation by squaring: O(log exp). Same as pow(base, exp, mod)."""
    result = 1
    base %= mod
    while exp:
        if exp & 1:
            result = result * base % mod
        base = base * base % mod
        exp >>= 1
    return result

bit_tricks_demo()
assert fast_pow(3, 200, 10**9 + 7) == pow(3, 200, 10**9 + 7)
''',
    "complexity": "Bit operations are O(1). Exponentiation by squaring is O(log n).",
    "problems": [
        {
            "name": "Single Number",
            "lc": 136,
            "level": "E",
            "prompt": "<p>Every element appears twice except one. Find it in O(n) time and O(1) space.</p>",
            "hint": "x ^ x = 0.",
            "idea": "<p>XOR everything together. Pairs cancel to 0, leaving the single number.</p>",
            "code": '''
from functools import reduce
from operator import xor

def single_number(nums: list[int]) -> int:
    return reduce(xor, nums)

assert single_number([4, 1, 2, 1, 2]) == 4
assert single_number([1]) == 1
''',
            "complexity": "O(n) time, O(1) space.",
        },
        {
            "name": "Counting Bits",
            "lc": 338,
            "level": "E",
            "prompt": "<p>For each i from 0 to n, count the 1 bits in i. Do it in O(n).</p><pre>5  →  [0,1,1,2,1,2]</pre>",
            "hint": "i has the same bits as i // 2, plus its last bit.",
            "idea": "<p>A tiny DP over bits: <code>bits[i] = bits[i &gt;&gt; 1] + (i &amp; 1)</code>. Shifting right drops the last bit, and we already know the answer for the smaller number.</p>",
            "code": '''
def count_bits(n: int) -> list[int]:
    bits = [0] * (n + 1)
    for i in range(1, n + 1):
        bits[i] = bits[i >> 1] + (i & 1)
    return bits

assert count_bits(2) == [0, 1, 1]
assert count_bits(5) == [0, 1, 1, 2, 1, 2]
''',
            "complexity": "O(n) time, O(n) space.",
        },
        {
            "name": "Missing Number",
            "lc": 268,
            "level": "E",
            "prompt": "<p>n distinct numbers from 0..n; one is missing. Find it.</p><pre>[3,0,1]  →  2</pre>",
            "hint": "Sum formula, or XOR indices with values.",
            "idea": "<p>The numbers 0..n sum to <code>n(n+1)/2</code>; subtract the actual sum. The XOR version avoids big sums in other languages: XOR every index and every value, and everything cancels except the missing number.</p>",
            "code": '''
def missing_number(nums: list[int]) -> int:
    n = len(nums)
    return n * (n + 1) // 2 - sum(nums)

def missing_number_xor(nums: list[int]) -> int:
    result = len(nums)
    for i, x in enumerate(nums):
        result ^= i ^ x
    return result

for f in (missing_number, missing_number_xor):
    assert f([3, 0, 1]) == 2
    assert f([9, 6, 4, 2, 3, 5, 7, 0, 1]) == 8
''',
            "complexity": "O(n) time, O(1) space.",
        },
        {
            "name": "Pow(x, n)",
            "lc": 50,
            "level": "M",
            "hot": True,
            "prompt": "<p>Compute x raised to the integer power n (n may be negative) in O(log n).</p>",
            "hint": "x¹⁰ = (x⁵)². Square and halve.",
            "idea": "<p>Exponentiation by squaring: look at n's bits. Whenever the lowest bit is 1, multiply the result by the current power of x. Square x and shift n right each step. For negative n, compute with 1/x and −n.</p>",
            "code": '''
def my_pow(x: float, n: int) -> float:
    if n < 0:
        x, n = 1 / x, -n
    result = 1.0
    while n:
        if n & 1:
            result *= x
        x *= x
        n >>= 1
    return result

assert my_pow(2.0, 10) == 1024.0
assert abs(my_pow(2.1, 3) - 9.261) < 1e-9
assert my_pow(2.0, -2) == 0.25
assert my_pow(5.0, 0) == 1.0
''',
            "complexity": "O(log n) time, O(1) space.",
        },
        {
            "name": "Count Primes",
            "lc": 204,
            "level": "M",
            "prompt": "<p>Count primes strictly less than n.</p><pre>10  →  4   (2, 3, 5, 7)</pre>",
            "hint": "Sieve of Eratosthenes: cross out multiples of each prime.",
            "idea": "<p>Start with everything marked prime. For each p from 2 while <code>p² &lt; n</code>, if p is still marked, cross out <code>p², p² + p, …</code>. Smaller multiples were already crossed out by smaller primes. Python slice assignment makes the crossing out fast.</p>",
            "code": '''
def count_primes(n: int) -> int:
    if n < 3:
        return 0
    is_prime = [True] * n
    is_prime[0] = is_prime[1] = False
    p = 2
    while p * p < n:
        if is_prime[p]:
            is_prime[p * p::p] = [False] * len(range(p * p, n, p))
        p += 1
    return sum(is_prime)

assert count_primes(10) == 4
assert count_primes(0) == 0
assert count_primes(2) == 0
assert count_primes(100) == 25
''',
            "complexity": "O(n log log n) time, O(n) space.",
        },
        {
            "name": "Maximum XOR of Two Numbers",
            "lc": 421,
            "level": "M",
            "prompt": "<p>Return the maximum of <code>nums[i] XOR nums[j]</code>.</p><pre>[3,10,5,25,2,8]  →  28   (5 ^ 25)</pre>",
            "hint": "Build the answer bit by bit from the top. Can you make this bit 1?",
            "idea": "<p>Greedy on bits from high to low. Suppose the best answer's higher bits are known. Try setting the current bit too: collect every number's prefix (its top bits), and check if two prefixes XOR to the candidate. Because <code>a ^ b = c</code> means <code>a ^ c = b</code>, that's a set lookup. (A binary trie of the numbers is the other standard solution.)</p>",
            "code": '''
def find_maximum_xor(nums: list[int]) -> int:
    best = 0
    for bit in range(max(nums).bit_length() - 1, -1, -1):
        prefixes = {x >> bit for x in nums}
        candidate = (best << 1) | 1           # try to make this bit 1
        if any((candidate ^ p) in prefixes for p in prefixes):
            best = candidate
        else:
            best <<= 1
    return best

assert find_maximum_xor([3, 10, 5, 25, 2, 8]) == 28
assert find_maximum_xor([14, 70, 53, 83, 49, 91, 36, 80, 92, 51, 66, 70]) == 127
assert find_maximum_xor([0]) == 0
''',
            "complexity": "O(n · bits) time, O(n) space.",
        },
    ],
}

DESIGN = {
    "id": "design",
    "nav": "Design data structures",
    "title": "Designing data structures",
    "tagline": "Build a small class with several operations, each hitting a target Big-O. Usually by combining two simple structures.",
    "plain": """
<p>\"Design\" coding questions ask you to write a class: an LRU cache, a key-value store with timestamps, a hit counter. The trick is almost always to <b>combine two basic structures</b>, each covering the other's weakness:</p>
<ul>
<li>Hash map + doubly linked list → O(1) lookup <i>and</i> O(1) move-to-front (LRU cache).</li>
<li>Hash map + array → O(1) lookup <i>and</i> O(1) random pick.</li>
<li>Hash map + sorted list per key → O(log n) \"latest value at or before time t\".</li>
</ul>
<p>Start by listing the operations and their required costs, then ask what each operation needs to find quickly. Talk through the design before writing code, and keep the methods short.</p>
<div class="analogy"><b>Picture it:</b> a library. The catalog (hash map) tells you where a book is instantly; the returns cart (linked list) keeps the most recently used books at the front.</div>
""",
    "signals": [
        "\"Design a class that supports … in O(1)\"",
        "Caches, rate limiters, hit counters, versioned stores, iterators",
        "Several operations with different cost requirements",
    ],
    "pitfalls": [
        "Forgetting to update <b>both</b> structures on every change",
        "Not handling capacity 0, missing keys, or updating an existing key",
        "Writing one giant method. Small helpers like <code>_remove(node)</code> and <code>_add_front(node)</code> make it readable and easier to check",
    ],
    "template": '''
from collections import OrderedDict

class LRUCacheShort:
    """The 10-line version. Mention it, but be ready to build the linked list yourself."""
    def __init__(self, capacity: int):
        self.cap = capacity
        self.data = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.data:
            return -1
        self.data.move_to_end(key)          # mark most recently used
        return self.data[key]

    def put(self, key: int, value: int) -> None:
        self.data[key] = value
        self.data.move_to_end(key)
        if len(self.data) > self.cap:
            self.data.popitem(last=False)   # evict least recently used

c = LRUCacheShort(1)
c.put(1, 1); c.put(2, 2)
assert c.get(1) == -1 and c.get(2) == 2
''',
    "complexity": "Target is usually O(1) or O(log n) per operation.",
    "problems": [
        {
            "name": "Design HashMap",
            "lc": 706,
            "level": "E",
            "prompt": "<p>Implement <code>put</code>, <code>get</code> and <code>remove</code> without using the built-in dict.</p>",
            "hint": "An array of buckets; each bucket is a small list of (key, value) pairs.",
            "idea": "<p>Hash the key to a bucket index (<code>key % size</code>). Collisions go in the same bucket as a list (\"chaining\"). With a good size, buckets stay short, so operations are O(1) on average. Mention resizing when the load factor gets high.</p>",
            "code": '''
class MyHashMap:
    def __init__(self, size: int = 1009):
        self.size = size
        self.buckets = [[] for _ in range(size)]

    def _bucket(self, key: int) -> list:
        return self.buckets[key % self.size]

    def put(self, key: int, value: int) -> None:
        bucket = self._bucket(key)
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))

    def get(self, key: int) -> int:
        for k, v in self._bucket(key):
            if k == key:
                return v
        return -1

    def remove(self, key: int) -> None:
        bucket = self._bucket(key)
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                return

m = MyHashMap()
m.put(1, 1); m.put(2, 2); m.put(1010, 5)      # 1 and 1010 collide
assert m.get(1) == 1 and m.get(1010) == 5 and m.get(3) == -1
m.put(2, 1); assert m.get(2) == 1
m.remove(2); assert m.get(2) == -1
''',
            "complexity": "O(1) average per operation, O(n) worst case.",
        },
        {
            "name": "Min Stack",
            "lc": 155,
            "level": "M",
            "prompt": "<p>A stack that also returns its minimum in O(1).</p>",
            "hint": "Store, with each item, the minimum at the time it was pushed.",
            "idea": "<p>Push pairs <code>(value, min_so_far)</code>. The top pair always knows the current minimum, and popping restores the previous minimum automatically.</p>",
            "code": '''
class MinStack:
    def __init__(self):
        self.items = []                      # (value, min at this depth)

    def push(self, val: int) -> None:
        current_min = min(val, self.items[-1][1]) if self.items else val
        self.items.append((val, current_min))

    def pop(self) -> None:
        self.items.pop()

    def top(self) -> int:
        return self.items[-1][0]

    def get_min(self) -> int:
        return self.items[-1][1]

s = MinStack()
s.push(-2); s.push(0); s.push(-3)
assert s.get_min() == -3
s.pop()
assert s.top() == 0 and s.get_min() == -2
''',
            "complexity": "O(1) per operation, O(n) space.",
        },
        {
            "name": "LRU Cache",
            "lc": 146,
            "level": "M",
            "hot": True,
            "prompt": "<p>A fixed-capacity cache with O(1) <code>get</code> and <code>put</code> that evicts the least recently used key when full.</p>",
            "hint": "A dict finds nodes; a doubly linked list keeps them in usage order.",
            "idea": "<p>Keep a doubly linked list with the most recent item at the front and the least recent at the back, plus a dict from key to node. <code>get</code>: find the node, move it to the front. <code>put</code>: update or insert at the front; if over capacity, remove the node at the back and delete its key from the dict. Two sentinel nodes (head and tail) remove all edge cases.</p>",
            "code": '''
class Node:
    __slots__ = ("key", "val", "prev", "next")
    def __init__(self, key=0, val=0):
        self.key, self.val = key, val
        self.prev = self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.map = {}
        self.head, self.tail = Node(), Node()      # sentinels
        self.head.next, self.tail.prev = self.tail, self.head

    def _remove(self, node: Node) -> None:
        node.prev.next, node.next.prev = node.next, node.prev

    def _add_front(self, node: Node) -> None:
        node.prev, node.next = self.head, self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        node = self.map.get(key)
        if not node:
            return -1
        self._remove(node)
        self._add_front(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.map:
            self._remove(self.map[key])
        node = Node(key, value)
        self.map[key] = node
        self._add_front(node)
        if len(self.map) > self.cap:
            lru = self.tail.prev
            self._remove(lru)
            del self.map[lru.key]

c = LRUCache(2)
c.put(1, 1); c.put(2, 2)
assert c.get(1) == 1
c.put(3, 3)                    # evicts 2
assert c.get(2) == -1
c.put(4, 4)                    # evicts 1
assert c.get(1) == -1 and c.get(3) == 3 and c.get(4) == 4
''',
            "complexity": "O(1) per operation, O(capacity) space.",
            "followups": ["Make it thread-safe: one lock around each method, or sharded caches with a lock each.", "Add expiry times: store a timestamp per node and check on get, plus a heap for cleanup."],
        },
        {
            "name": "Time Based Key-Value Store",
            "lc": 981,
            "level": "M",
            "hot": True,
            "prompt": "<p><code>set(key, value, timestamp)</code> with strictly increasing timestamps per key. <code>get(key, t)</code> returns the value with the largest timestamp ≤ t, or \"\".</p>",
            "hint": "Timestamps arrive sorted, so each key's history is a sorted list. Binary search it.",
            "idea": "<p>Map each key to two parallel lists: timestamps and values. Appending keeps them sorted. For <code>get</code>, <code>bisect_right(times, t) − 1</code> is the index of the latest timestamp ≤ t.</p>",
            "code": '''
from bisect import bisect_right
from collections import defaultdict

class TimeMap:
    def __init__(self):
        self.times = defaultdict(list)
        self.values = defaultdict(list)

    def set(self, key: str, value: str, timestamp: int) -> None:
        self.times[key].append(timestamp)
        self.values[key].append(value)

    def get(self, key: str, timestamp: int) -> str:
        i = bisect_right(self.times[key], timestamp) - 1
        return self.values[key][i] if i >= 0 else ""

tm = TimeMap()
tm.set("foo", "bar", 1)
assert tm.get("foo", 1) == "bar" and tm.get("foo", 3) == "bar"
tm.set("foo", "bar2", 4)
assert tm.get("foo", 4) == "bar2" and tm.get("foo", 5) == "bar2"
assert tm.get("foo", 0) == "" and tm.get("nope", 9) == ""
''',
            "complexity": "O(1) set, O(log n) get.",
        },
        {
            "name": "Snapshot Array",
            "lc": 1146,
            "level": "M",
            "hot": True,
            "prompt": "<p>An array of length n supporting <code>set(i, val)</code>, <code>snap()</code> (returns a snapshot id) and <code>get(i, snap_id)</code>.</p>",
            "hint": "Copying the whole array on every snap is too slow. Store only the changes per index.",
            "idea": "<p>For each index keep a list of <code>(snap_id, value)</code> changes. <code>set</code> writes to the current snap id (overwriting if already set in this snap). <code>get</code> binary-searches that index's history for the last change at or before <code>snap_id</code>. Memory grows only with the number of <code>set</code> calls.</p>",
            "code": '''
from bisect import bisect_right

class SnapshotArray:
    def __init__(self, length: int):
        self.history = [[(-1, 0)] for _ in range(length)]   # (snap_id, value)
        self.snap_id = 0

    def set(self, index: int, val: int) -> None:
        h = self.history[index]
        if h[-1][0] == self.snap_id:
            h[-1] = (self.snap_id, val)
        else:
            h.append((self.snap_id, val))

    def snap(self) -> int:
        self.snap_id += 1
        return self.snap_id - 1

    def get(self, index: int, snap_id: int) -> int:
        h = self.history[index]
        i = bisect_right(h, (snap_id, float("inf"))) - 1
        return h[i][1]

sa = SnapshotArray(3)
sa.set(0, 5)
assert sa.snap() == 0
sa.set(0, 6)
assert sa.get(0, 0) == 5
assert sa.snap() == 1 and sa.get(0, 1) == 6 and sa.get(1, 1) == 0
''',
            "complexity": "O(1) set and snap, O(log s) get.",
        },
        {
            "name": "LFU Cache",
            "lc": 460,
            "level": "H",
            "prompt": "<p>A cache that evicts the <b>least frequently</b> used key; ties go to the least recently used. O(1) <code>get</code> and <code>put</code>.</p>",
            "hint": "Group keys by frequency. Inside each group, keep usage order. Track the minimum frequency.",
            "idea": "<p>Three maps: <code>key → value</code>, <code>key → frequency</code>, and <code>frequency → OrderedDict of keys</code> (oldest first). Touching a key moves it from its frequency group to the next one. <code>min_freq</code> only changes in two ways: a new key resets it to 1, and emptying the current minimum group bumps it by one. Evict the oldest key in the <code>min_freq</code> group.</p>",
            "code": '''
from collections import defaultdict, OrderedDict

class LFUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.val = {}
        self.freq = {}
        self.groups = defaultdict(OrderedDict)    # freq -> keys, oldest first
        self.min_freq = 0

    def _touch(self, key: int) -> None:
        f = self.freq[key]
        del self.groups[f][key]
        if not self.groups[f]:
            del self.groups[f]
            if self.min_freq == f:
                self.min_freq = f + 1
        self.freq[key] = f + 1
        self.groups[f + 1][key] = None

    def get(self, key: int) -> int:
        if key not in self.val:
            return -1
        self._touch(key)
        return self.val[key]

    def put(self, key: int, value: int) -> None:
        if self.cap == 0:
            return
        if key in self.val:
            self.val[key] = value
            self._touch(key)
            return
        if len(self.val) == self.cap:
            old, _ = self.groups[self.min_freq].popitem(last=False)
            if not self.groups[self.min_freq]:
                del self.groups[self.min_freq]
            del self.val[old], self.freq[old]
        self.val[key] = value
        self.freq[key] = 1
        self.groups[1][key] = None
        self.min_freq = 1

c = LFUCache(2)
c.put(1, 1); c.put(2, 2)
assert c.get(1) == 1
c.put(3, 3)                          # evicts 2 (freq 1)
assert c.get(2) == -1 and c.get(3) == 3
c.put(4, 4)                          # 1 and 3 both freq 2; 1 is older
assert c.get(1) == -1 and c.get(3) == 3 and c.get(4) == 4
''',
            "complexity": "O(1) per operation, O(capacity) space.",
        },
    ],
}

ADVANCED = {
    "id": "advanced",
    "nav": "Advanced structures",
    "title": "Advanced structures: Fenwick trees, segment trees, string hashing",
    "tagline": "Less common, but Google does ask them at L4+ as follow-ups. Know what they do and have one template ready.",
    "plain": """
<p>These show up when a simpler approach almost works but one operation is too slow.</p>
<ul>
<li><b>Fenwick tree (binary indexed tree):</b> prefix sums that stay correct while values change. Update and query are both O(log n). About 15 lines.</li>
<li><b>Segment tree:</b> like a Fenwick tree, but works for any combine function (min, max, gcd), and range updates with lazy propagation. O(log n) per operation.</li>
<li><b>Rolling hash (Rabin–Karp):</b> a fingerprint of a substring that can be slid one character in O(1). Compare substrings by comparing numbers.</li>
<li><b>KMP:</b> find a pattern in text in O(n + m) by never re-reading text characters.</li>
</ul>
<div class="analogy"><b>Picture it:</b> a Fenwick tree is a company's reporting chain for expenses. Each manager keeps the total for a block of teams under them. To get the total up to team i, you add a few managers' totals instead of every team's. When one team spends money, only the few managers above it update their totals.</div>
""",
    "signals": [
        "Range sums or mins <b>with updates</b> mixed in",
        "\"Count smaller elements to the right\", inversions, rank queries",
        "Booking systems with overlapping ranges",
        "Find repeated or duplicate substrings; substring search",
    ],
    "pitfalls": [
        "Fenwick trees are 1-indexed. Off-by-one is the classic bug",
        "Hash collisions: verify a hash match by comparing the actual strings, or use two moduli",
        "Reaching for these first. Say the simpler approach and its cost before upgrading",
    ],
    "template": '''
class Fenwick:
    """Prefix sums with point updates. Internally 1-indexed."""
    def __init__(self, n: int):
        self.tree = [0] * (n + 1)

    def add(self, i: int, delta: int) -> None:      # i is 0-indexed
        i += 1
        while i < len(self.tree):
            self.tree[i] += delta
            i += i & -i                              # jump to the next responsible node

    def prefix(self, i: int) -> int:                # sum of items [0, i)
        total = 0
        while i > 0:
            total += self.tree[i]
            i -= i & -i                              # drop the lowest set bit
        return total

class SegmentTree:
    """Iterative segment tree for range-min (swap min for any associative op)."""
    def __init__(self, data: list[int]):
        self.n = len(data)
        self.tree = [float("inf")] * self.n + data
        for i in range(self.n - 1, 0, -1):
            self.tree[i] = min(self.tree[2 * i], self.tree[2 * i + 1])

    def update(self, i: int, value: int) -> None:
        i += self.n
        self.tree[i] = value
        while i > 1:
            i //= 2
            self.tree[i] = min(self.tree[2 * i], self.tree[2 * i + 1])

    def query(self, lo: int, hi: int) -> int:       # min of data[lo:hi]
        result = float("inf")
        lo += self.n
        hi += self.n
        while lo < hi:
            if lo & 1:
                result = min(result, self.tree[lo]); lo += 1
            if hi & 1:
                hi -= 1; result = min(result, self.tree[hi])
            lo //= 2
            hi //= 2
        return result

f = Fenwick(5)
for i, x in enumerate([3, 1, 4, 1, 5]):
    f.add(i, x)
assert f.prefix(3) == 8
f.add(1, 10)
assert f.prefix(3) == 18

st = SegmentTree([5, 2, 8, 6, 3])
assert st.query(0, 3) == 2 and st.query(2, 5) == 3
st.update(1, 9)
assert st.query(0, 3) == 5
''',
    "complexity": "O(log n) per update or query, O(n) space.",
    "problems": [
        {
            "name": "Find the Index of the First Occurrence (KMP)",
            "lc": 28,
            "level": "E",
            "prompt": "<p>Return the first index where <code>needle</code> occurs in <code>haystack</code>, or −1.</p><pre>\"sadbutsad\", \"sad\"  →  0</pre>",
            "hint": "The easy answer is <code>haystack.find(needle)</code>. The interview answer builds KMP's failure table.",
            "idea": "<p>Say the O(n·m) brute force first. KMP precomputes, for each prefix of the needle, the length of its longest proper prefix that is also a suffix (<code>lps</code>). On a mismatch, instead of restarting, jump back to <code>lps[j−1]</code>: that part is already known to match. The text pointer never moves backwards, so it's O(n + m).</p>",
            "code": '''
def str_str(haystack: str, needle: str) -> int:
    if not needle:
        return 0
    lps = [0] * len(needle)           # longest proper prefix that is also a suffix
    k = 0
    for i in range(1, len(needle)):
        while k and needle[i] != needle[k]:
            k = lps[k - 1]
        if needle[i] == needle[k]:
            k += 1
        lps[i] = k
    j = 0                             # characters of needle matched so far
    for i, ch in enumerate(haystack):
        while j and ch != needle[j]:
            j = lps[j - 1]
        if ch == needle[j]:
            j += 1
            if j == len(needle):
                return i - j + 1
    return -1

assert str_str("sadbutsad", "sad") == 0
assert str_str("leetcode", "leeto") == -1
assert str_str("aaaaab", "aab") == 3
assert str_str("abc", "") == 0
''',
            "complexity": "O(n + m) time, O(m) space.",
        },
        {
            "name": "Range Sum Query – Mutable",
            "lc": 307,
            "level": "M",
            "prompt": "<p>Support <code>update(i, val)</code> and <code>sum_range(l, r)</code>, both fast.</p>",
            "hint": "Plain prefix sums make updates O(n). A Fenwick tree makes both O(log n).",
            "idea": "<p>Store the array in a Fenwick tree. An update adds the difference between the new and old value. A range sum is <code>prefix(r + 1) − prefix(l)</code>.</p>",
            "code": '''
class NumArray:
    def __init__(self, nums: list[int]):
        self.nums = nums[:]
        self.tree = [0] * (len(nums) + 1)
        for i, x in enumerate(nums):
            self._add(i, x)

    def _add(self, i: int, delta: int) -> None:
        i += 1
        while i < len(self.tree):
            self.tree[i] += delta
            i += i & -i

    def _prefix(self, i: int) -> int:
        s = 0
        while i > 0:
            s += self.tree[i]
            i -= i & -i
        return s

    def update(self, index: int, val: int) -> None:
        self._add(index, val - self.nums[index])
        self.nums[index] = val

    def sum_range(self, left: int, right: int) -> int:
        return self._prefix(right + 1) - self._prefix(left)

na = NumArray([1, 3, 5])
assert na.sum_range(0, 2) == 9
na.update(1, 2)
assert na.sum_range(0, 2) == 8 and na.sum_range(1, 1) == 2
''',
            "complexity": "O(n log n) build (O(n) possible), O(log n) per update and query.",
        },
        {
            "name": "My Calendar I",
            "lc": 729,
            "level": "M",
            "hot": True,
            "prompt": "<p><code>book(start, end)</code> adds the half-open interval <code>[start, end)</code> if it doesn't overlap an existing booking, returning True/False.</p>",
            "hint": "Keep bookings sorted by start. A new booking only needs to be checked against its two neighbors.",
            "idea": "<p>Keep a sorted list of bookings. Binary-search where the new one would go; it only conflicts if the previous booking ends after it starts, or the next booking starts before it ends. Inserting into a Python list is O(n); mention that a balanced tree (or <code>sortedcontainers.SortedList</code>) makes it O(log n).</p>",
            "code": '''
from bisect import bisect_left, insort

class MyCalendar:
    def __init__(self):
        self.bookings = []                       # sorted (start, end)

    def book(self, start: int, end: int) -> bool:
        i = bisect_left(self.bookings, (start, end))
        if i > 0 and self.bookings[i - 1][1] > start:
            return False                         # previous one runs into us
        if i < len(self.bookings) and self.bookings[i][0] < end:
            return False                         # we run into the next one
        insort(self.bookings, (start, end))
        return True

cal = MyCalendar()
assert cal.book(10, 20)
assert not cal.book(15, 25)
assert cal.book(20, 30)
assert not cal.book(5, 11)
''',
            "complexity": "O(log n) search + O(n) list insert.",
            "followups": ["My Calendar II and III (LC 731, 732): allow double bookings / count the max overlap; a sweep-line map or a segment tree."],
        },
        {
            "name": "Count of Smaller Numbers After Self",
            "lc": 315,
            "level": "H",
            "hot": True,
            "prompt": "<p>For each element, count how many elements to its right are smaller.</p><pre>[5,2,6,1]  →  [2,1,1,0]</pre>",
            "hint": "Walk from the right. Keep a count of values seen so far in a Fenwick tree indexed by value rank.",
            "idea": "<p>Replace values by their rank among the sorted distinct values (coordinate compression). Walk from right to left. For each value, the answer is the number of already-seen values with a smaller rank: a Fenwick prefix query. Then add this value's rank to the tree. (Merge sort counting inversions is the other classic solution.)</p>",
            "code": '''
def count_smaller(nums: list[int]) -> list[int]:
    rank = {v: i + 1 for i, v in enumerate(sorted(set(nums)))}   # 1-based ranks
    tree = [0] * (len(rank) + 1)

    def add(i):
        while i < len(tree):
            tree[i] += 1
            i += i & -i

    def prefix(i):                                  # count of ranks <= i
        s = 0
        while i > 0:
            s += tree[i]
            i -= i & -i
        return s

    out = []
    for x in reversed(nums):
        out.append(prefix(rank[x] - 1))             # strictly smaller
        add(rank[x])
    return out[::-1]

assert count_smaller([5, 2, 6, 1]) == [2, 1, 1, 0]
assert count_smaller([-1]) == [0]
assert count_smaller([-1, -1]) == [0, 0]
''',
            "complexity": "O(n log n) time, O(n) space.",
        },
        {
            "name": "Longest Duplicate Substring",
            "lc": 1044,
            "level": "H",
            "prompt": "<p>Return any longest substring that occurs at least twice (occurrences may overlap), or \"\".</p><pre>\"banana\"  →  \"ana\"</pre>",
            "hint": "If a duplicate of length L exists, one of length L − 1 does too. Binary search L; check with a rolling hash.",
            "idea": "<p>Two ideas combined. (1) Binary search on the length, because \"has a duplicate of length L\" is monotonic. (2) To check one length in O(n), slide a rolling hash across the string: remove the leading character's contribution, shift, add the new character. Store hashes in a dict; on a hash match, compare the real substrings to rule out collisions.</p>",
            "code": '''
def longest_dup_substring(s: str) -> str:
    MOD = (1 << 61) - 1
    BASE = 131
    n = len(s)
    codes = [ord(c) for c in s]

    def find_dup(length: int) -> int:
        """Start index of a repeated substring of this length, or -1."""
        if length == 0:
            return 0
        h = 0
        for c in codes[:length]:
            h = (h * BASE + c) % MOD
        power = pow(BASE, length, MOD)            # weight of the char leaving
        seen = {h: [0]}
        for start in range(1, n - length + 1):
            h = (h * BASE + codes[start + length - 1] - codes[start - 1] * power) % MOD
            for other in seen.get(h, []):
                if s[other:other + length] == s[start:start + length]:
                    return start
            seen.setdefault(h, []).append(start)
        return -1

    lo, hi = 0, n - 1                              # largest length that works
    best_start = 0
    while lo < hi:
        mid = (lo + hi + 1) // 2
        start = find_dup(mid)
        if start != -1:
            lo, best_start = mid, start
        else:
            hi = mid - 1
    return s[best_start:best_start + lo]

assert longest_dup_substring("banana") == "ana"
assert longest_dup_substring("abcd") == ""
assert longest_dup_substring("aaaa") == "aaa"
''',
            "complexity": "O(n log n) expected time, O(n) space.",
        },
    ],
}

PATTERNS = [DP_1D, DP_2D, DP_MORE, BITS, DESIGN, ADVANCED]
