"""Patterns 1-6: hashing, two pointers, sliding window, prefix sums, binary search, stacks."""

HASHING = {
    "id": "hashing",
    "nav": "Arrays and hashing",
    "title": "Arrays and hash maps",
    "tagline": "Trade a little memory for a lot of speed by remembering what you have already seen.",
    "plain": """
<p>A hash map (Python <code>dict</code>) stores key–value pairs and finds any key in constant time, no matter how many keys it holds. A <code>set</code> is the same thing without values.</p>
<p>Most brute-force solutions are slow because they search the input again and again: "for each item, look through everything else". A hash map lets you do that search in one step. That usually turns <code>O(n²)</code> into <code>O(n)</code>.</p>
<div class="analogy"><b>Picture it:</b> a coat check. You hand over your coat and get a ticket number. Later the attendant finds your coat instantly from the number instead of looking at every coat in the room.</div>
""",
    "signals": [
        "\"Find a pair / two items that…\"",
        "Counting how often things appear, or checking for duplicates",
        "Grouping items that share some property (same letters, same sum)",
        "The brute force is two nested loops where the inner loop only searches",
        "You need O(1) \"have I seen this?\" checks",
    ],
    "pitfalls": [
        "Using <code>x in some_list</code> (O(n)) instead of a set",
        "Using a list as a dict key. Convert it to a tuple first",
        "Forgetting that a pair can't use the same element twice (check before you insert)",
        "Assuming dicts are sorted by key. They keep insertion order, not sorted order",
    ],
    "template": '''
from collections import Counter, defaultdict

def seen_before(nums: list[int], target: int) -> bool:
    """One pass: for each item, ask the map about the partner we need."""
    seen = set()
    for x in nums:
        if target - x in seen:      # partner already seen?
            return True
        seen.add(x)                 # remember x for later items
    return False

def group_by_key(words: list[str]) -> list[list[str]]:
    """Put items with the same 'signature' into the same bucket."""
    groups = defaultdict(list)
    for w in words:
        groups[tuple(sorted(w))].append(w)   # signature must be hashable
    return list(groups.values())

assert seen_before([3, 8, 1], 9)
assert Counter("hello")["l"] == 2
''',
    "complexity": "O(n) time, O(n) extra space.",
    "problems": [
        {
            "name": "Two Sum",
            "lc": 1,
            "level": "E",
            "hot": True,
            "prompt": "<p>Given a list of integers <code>nums</code> and a <code>target</code>, return the indices of the two numbers that add up to <code>target</code>. Exactly one answer exists.</p><pre>nums = [2, 7, 11, 15], target = 9  →  [0, 1]</pre>",
            "hint": "For each number x, the number you need is target − x. How can you check whether you've seen it in O(1)?",
            "idea": "<p>Walk the list once. Keep a dict from value to index. For each number, check if its partner <code>target − x</code> is already in the dict. If yes, you're done. If not, store the current number and move on. Checking before storing stops a number from pairing with itself.</p>",
            "code": '''
def two_sum(nums: list[int], target: int) -> list[int]:
    index_of = {}                       # value -> index where we saw it
    for i, x in enumerate(nums):
        need = target - x
        if need in index_of:
            return [index_of[need], i]
        index_of[x] = i
    return []

assert two_sum([2, 7, 11, 15], 9) == [0, 1]
assert two_sum([3, 2, 4], 6) == [1, 2]
assert two_sum([3, 3], 6) == [0, 1]
''',
            "complexity": "O(n) time, O(n) space.",
            "followups": [
                "Input is sorted: use two pointers for O(1) space.",
                "Return all unique pairs: sort, then two pointers that skip duplicates.",
                "The data is a stream with many <code>find</code> calls: keep a Counter and trade off add-time vs find-time.",
            ],
        },
        {
            "name": "Group Anagrams",
            "lc": 49,
            "level": "M",
            "prompt": "<p>Group words that are anagrams of each other (same letters, different order).</p><pre>[\"eat\",\"tea\",\"tan\",\"ate\",\"nat\",\"bat\"]\n→ [[\"eat\",\"tea\",\"ate\"], [\"tan\",\"nat\"], [\"bat\"]]</pre>",
            "hint": "Two words are anagrams exactly when they have the same letter counts. Can you turn that into a dict key?",
            "idea": "<p>Give each word a <b>signature</b> that is identical for all its anagrams. Sorting the letters works (<code>O(k log k)</code> per word). Counting the 26 letters is faster (<code>O(k)</code>). Use the signature as a dict key and collect words in lists.</p>",
            "code": '''
from collections import defaultdict

def group_anagrams(words: list[str]) -> list[list[str]]:
    groups = defaultdict(list)
    for w in words:
        counts = [0] * 26
        for ch in w:
            counts[ord(ch) - ord("a")] += 1
        groups[tuple(counts)].append(w)      # tuple so it can be a key
    return list(groups.values())

result = group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
assert sorted(sorted(g) for g in result) == [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]
assert group_anagrams([""]) == [[""]]
''',
            "complexity": "O(n · k) time where k is the longest word; O(n · k) space.",
        },
        {
            "name": "Longest Consecutive Sequence",
            "lc": 128,
            "level": "M",
            "hot": True,
            "prompt": "<p>Given an unsorted list, return the length of the longest run of consecutive integers. It must run in O(n).</p><pre>[100, 4, 200, 1, 3, 2]  →  4   (1, 2, 3, 4)</pre>",
            "hint": "Sorting is O(n log n), too slow. Put everything in a set. Which numbers are the start of a run?",
            "idea": "<p>A number <code>x</code> starts a run only if <code>x − 1</code> is <i>not</i> in the set. From each start, count upward while the next number exists. Each number is visited at most twice (once in the outer loop, once while counting), so the total is <code>O(n)</code>.</p>",
            "code": '''
def longest_consecutive(nums: list[int]) -> int:
    values = set(nums)
    best = 0
    for x in values:
        if x - 1 in values:          # not the start of a run
            continue
        length = 1
        while x + length in values:
            length += 1
        best = max(best, length)
    return best

assert longest_consecutive([100, 4, 200, 1, 3, 2]) == 4
assert longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9
assert longest_consecutive([]) == 0
''',
            "complexity": "O(n) time, O(n) space.",
            "followups": ["Numbers arrive one at a time and you must report the answer after each: union-find over neighbors, or a dict of run boundaries."],
        },
        {
            "name": "First Missing Positive",
            "lc": 41,
            "level": "H",
            "prompt": "<p>Return the smallest positive integer missing from an unsorted list. Use O(n) time and O(1) extra space.</p><pre>[3, 4, -1, 1]  →  2\n[7, 8, 9, 11]  →  1</pre>",
            "hint": "The answer is always between 1 and n + 1. Could the list itself act as the hash map?",
            "idea": "<p>With n numbers, the answer is in <code>1..n+1</code>. Use the list as its own hash table: try to put value <code>v</code> at index <code>v − 1</code> by swapping. Ignore values outside <code>1..n</code>. After that, the first index <code>i</code> where <code>nums[i] != i + 1</code> gives the answer. Each swap puts one number in its final place, so there are at most n swaps overall.</p>",
            "code": '''
def first_missing_positive(nums: list[int]) -> int:
    n = len(nums)
    for i in range(n):
        # keep swapping until nums[i] is out of range or already home
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            home = nums[i] - 1
            nums[i], nums[home] = nums[home], nums[i]
    for i in range(n):
        if nums[i] != i + 1:
            return i + 1
    return n + 1

assert first_missing_positive([1, 2, 0]) == 3
assert first_missing_positive([3, 4, -1, 1]) == 2
assert first_missing_positive([7, 8, 9, 11, 12]) == 1
assert first_missing_positive([1, 1]) == 2
''',
            "complexity": "O(n) time, O(1) extra space.",
        },
    ],
}

TWO_POINTERS = {
    "id": "two-pointers",
    "nav": "Two pointers",
    "title": "Two pointers",
    "tagline": "Two indices walk through the data together, so one pass does the work of two nested loops.",
    "plain": """
<p>Instead of checking every pair with two nested loops, keep two indices and move them cleverly. There are two common shapes:</p>
<ul>
<li><b>Opposite ends:</b> one pointer starts at the left, one at the right, and they move toward each other. Works well on <b>sorted</b> data, because moving a pointer changes the sum in a predictable direction.</li>
<li><b>Same direction:</b> a slow pointer marks where the next "good" item goes, a fast pointer scans ahead. Great for removing items in place.</li>
</ul>
<div class="analogy"><b>Picture it:</b> two people reading a sorted guest list, one from the top and one from the bottom, looking for a couple whose ages add to 60. If the total is too big, the one at the bottom (older end) steps up. Too small, the one at the top steps down. They never need to go back.</div>
""",
    "signals": [
        "The input is sorted, or sorting it wouldn't hurt",
        "Pairs or triplets that sum to a target",
        "Palindromes, or comparing a sequence from both ends",
        "Remove or move items in place with O(1) extra space",
        "Merging two sorted lists",
    ],
    "pitfalls": [
        "Forgetting to skip duplicates when the answer must be unique triplets",
        "Using <code>&lt;=</code> vs <code>&lt;</code> in the loop condition carelessly and using the same element twice",
        "Moving the wrong pointer. Always ask: which move could possibly improve the answer?",
    ],
    "template": '''
def pair_with_sum(sorted_nums: list[int], target: int) -> tuple[int, int] | None:
    """Opposite ends on sorted input."""
    lo, hi = 0, len(sorted_nums) - 1
    while lo < hi:
        s = sorted_nums[lo] + sorted_nums[hi]
        if s == target:
            return lo, hi
        if s < target:
            lo += 1          # need bigger: move the small end up
        else:
            hi -= 1          # need smaller: move the big end down
    return None

def remove_duplicates(sorted_nums: list[int]) -> int:
    """Same direction: slow = where the next unique value goes."""
    slow = 0
    for fast in range(len(sorted_nums)):
        if fast == 0 or sorted_nums[fast] != sorted_nums[fast - 1]:
            sorted_nums[slow] = sorted_nums[fast]
            slow += 1
    return slow              # length of the unique prefix

assert pair_with_sum([1, 3, 4, 6, 9], 10) == (0, 4)
nums = [1, 1, 2, 3, 3]
assert remove_duplicates(nums) == 3 and nums[:3] == [1, 2, 3]
''',
    "complexity": "O(n) time after sorting (O(n log n) if you sort), O(1) extra space.",
    "problems": [
        {
            "name": "Valid Palindrome",
            "lc": 125,
            "level": "E",
            "prompt": "<p>After lowercasing and removing everything that isn't a letter or digit, does the string read the same both ways?</p><pre>\"A man, a plan, a canal: Panama\"  →  True</pre>",
            "hint": "Don't build a cleaned copy. Skip junk characters with the pointers themselves.",
            "idea": "<p>Put one pointer at each end. Skip characters that aren't letters or digits. Compare lowercase versions; if they differ, it's not a palindrome. Move both inward.</p>",
            "code": '''
def is_palindrome(s: str) -> bool:
    lo, hi = 0, len(s) - 1
    while lo < hi:
        if not s[lo].isalnum():
            lo += 1
        elif not s[hi].isalnum():
            hi -= 1
        elif s[lo].lower() != s[hi].lower():
            return False
        else:
            lo += 1
            hi -= 1
    return True

assert is_palindrome("A man, a plan, a canal: Panama")
assert not is_palindrome("race a car")
assert is_palindrome(" ")
''',
            "complexity": "O(n) time, O(1) space.",
            "followups": ["Valid Palindrome II (LC 680): you may delete one character. On the first mismatch, try skipping either side once."],
        },
        {
            "name": "3Sum",
            "lc": 15,
            "level": "M",
            "hot": True,
            "prompt": "<p>Find all unique triplets in the list that sum to zero.</p><pre>[-1, 0, 1, 2, -1, -4]  →  [[-1, -1, 2], [-1, 0, 1]]</pre>",
            "hint": "Sort first. Fix the first number, then the problem becomes Two Sum on a sorted suffix.",
            "idea": "<p>Sort. For each index <code>i</code>, find pairs in the rest that sum to <code>−nums[i]</code> with two pointers. Duplicates are the tricky part: skip an <code>i</code> equal to the previous one, and after finding a triplet, move the left pointer past equal values.</p>",
            "code": '''
def three_sum(nums: list[int]) -> list[list[int]]:
    nums = sorted(nums)
    out = []
    for i in range(len(nums) - 2):
        if nums[i] > 0:
            break                             # smallest is positive: no more zeros
        if i > 0 and nums[i] == nums[i - 1]:
            continue                          # same first number as before
        lo, hi = i + 1, len(nums) - 1
        while lo < hi:
            s = nums[i] + nums[lo] + nums[hi]
            if s < 0:
                lo += 1
            elif s > 0:
                hi -= 1
            else:
                out.append([nums[i], nums[lo], nums[hi]])
                lo += 1
                hi -= 1
                while lo < hi and nums[lo] == nums[lo - 1]:
                    lo += 1                   # skip duplicate second numbers
    return out

assert three_sum([-1, 0, 1, 2, -1, -4]) == [[-1, -1, 2], [-1, 0, 1]]
assert three_sum([0, 0, 0, 0]) == [[0, 0, 0]]
assert three_sum([0, 1, 1]) == []
''',
            "complexity": "O(n²) time, O(n) space for the sorted copy.",
        },
        {
            "name": "Container With Most Water",
            "lc": 11,
            "level": "M",
            "prompt": "<p><code>height[i]</code> is a vertical line at position i. Pick two lines that, with the x-axis, hold the most water. Water held = <code>min(h[i], h[j]) × (j − i)</code>.</p><pre>[1, 8, 6, 2, 5, 4, 8, 3, 7]  →  49</pre>",
            "hint": "Start with the widest container. Which side can you move without ever losing the best answer?",
            "idea": "<p>Start with pointers at both ends (the widest container). The shorter line limits the water. Moving the taller line inward can only make things worse (narrower, and still limited by the short line). So always move the <b>shorter</b> line. That rules out one line per step, giving one pass.</p>",
            "code": '''
def max_area(height: list[int]) -> int:
    lo, hi = 0, len(height) - 1
    best = 0
    while lo < hi:
        best = max(best, min(height[lo], height[hi]) * (hi - lo))
        if height[lo] < height[hi]:
            lo += 1
        else:
            hi -= 1
    return best

assert max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
assert max_area([1, 1]) == 1
''',
            "complexity": "O(n) time, O(1) space.",
        },
        {
            "name": "Trapping Rain Water",
            "lc": 42,
            "level": "H",
            "hot": True,
            "prompt": "<p>Given bar heights, how much rain water is trapped between the bars after it rains?</p><pre>[0,1,0,2,1,0,1,3,2,1,2,1]  →  6</pre>",
            "hint": "Water above bar i = min(tallest bar to its left, tallest bar to its right) − height[i]. Can you avoid precomputing both arrays?",
            "idea": "<p>Water above each bar equals <code>min(max_left, max_right) − height</code>. The simple way precomputes both max arrays (O(n) space). The two-pointer way: whichever side has the smaller max so far is the limiting side, so you already know the answer for that side's next bar. Process that bar and move inward.</p>",
            "code": '''
def trap(height: list[int]) -> int:
    lo, hi = 0, len(height) - 1
    left_max = right_max = 0
    water = 0
    while lo < hi:
        if height[lo] < height[hi]:
            left_max = max(left_max, height[lo])
            water += left_max - height[lo]    # right side is at least as tall
            lo += 1
        else:
            right_max = max(right_max, height[hi])
            water += right_max - height[hi]
            hi -= 1
    return water

assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
assert trap([4, 2, 0, 3, 2, 5]) == 9
assert trap([]) == 0
''',
            "complexity": "O(n) time, O(1) space.",
            "followups": ["2D version, Trapping Rain Water II (LC 407): a min-heap of boundary cells flooding inward, like Dijkstra."],
        },
    ],
}

SLIDING = {
    "id": "sliding-window",
    "nav": "Sliding window",
    "title": "Sliding window",
    "tagline": "For \"best contiguous stretch\" questions, grow a window on the right and shrink it on the left.",
    "plain": """
<p>Many problems ask about a <b>contiguous</b> piece of an array or string: the longest substring with some rule, the smallest subarray with some sum. Checking every start and end is O(n²) or worse.</p>
<p>A sliding window keeps a start and an end. You move the end forward one step at a time. When the window breaks the rule, you move the start forward until it's valid again. Each element enters once and leaves once, so it's O(n). You keep a small summary of the window (a count dict, a running sum) and update it as items enter and leave, instead of recomputing from scratch.</p>
<div class="analogy"><b>Picture it:</b> a caterpillar crawling along a branch. The head stretches forward; when the body is too long, the tail catches up.</div>
""",
    "signals": [
        "\"Longest / shortest / count of substring or subarray\" with a condition",
        "The word <i>contiguous</i>, or <i>consecutive</i> elements",
        "At most k distinct, at most k changes, without repeating",
        "A fixed window size k (moving averages, max of each window)",
    ],
    "pitfalls": [
        "Using a window when numbers can be negative and the rule is a sum. Shrinking no longer helps. Use prefix sums instead",
        "Updating the answer at the wrong moment: for \"longest\", update after shrinking; for \"shortest\", update while shrinking",
        "Recomputing the window's summary from scratch each step (hides an O(n²))",
    ],
    "template": '''
from collections import defaultdict

def longest_window(s: str, k: int) -> int:
    """Longest substring with at most k distinct characters."""
    count = defaultdict(int)
    left = 0
    best = 0
    for right, ch in enumerate(s):
        count[ch] += 1                        # 1. add the new item
        while len(count) > k:                 # 2. shrink until valid
            out = s[left]
            count[out] -= 1
            if count[out] == 0:
                del count[out]
            left += 1
        best = max(best, right - left + 1)    # 3. window is valid: record it
    return best

assert longest_window("eceba", 2) == 3      # "ece"
assert longest_window("aa", 1) == 2
''',
    "complexity": "O(n) time. Space is the size of the window summary (often O(alphabet)).",
    "problems": [
        {
            "name": "Best Time to Buy and Sell Stock",
            "lc": 121,
            "level": "E",
            "prompt": "<p><code>prices[i]</code> is a stock's price on day i. Buy once and sell once later. Return the maximum profit, or 0.</p><pre>[7, 1, 5, 3, 6, 4]  →  5   (buy at 1, sell at 6)</pre>",
            "hint": "If you sell today, the best buy day is the cheapest day so far.",
            "idea": "<p>Scan once, tracking the lowest price seen so far. Today's best profit is <code>price − lowest</code>. Keep the maximum. This is a window whose left edge jumps to each new low.</p>",
            "code": '''
def max_profit(prices: list[int]) -> int:
    lowest = float("inf")
    best = 0
    for p in prices:
        lowest = min(lowest, p)
        best = max(best, p - lowest)
    return best

assert max_profit([7, 1, 5, 3, 6, 4]) == 5
assert max_profit([7, 6, 4, 3, 1]) == 0
''',
            "complexity": "O(n) time, O(1) space.",
        },
        {
            "name": "Longest Substring Without Repeating Characters",
            "lc": 3,
            "level": "M",
            "hot": True,
            "prompt": "<p>Return the length of the longest substring with no repeated characters.</p><pre>\"abcabcbb\"  →  3   (\"abc\")\n\"pwwkew\"    →  3   (\"wke\")</pre>",
            "hint": "When you see a repeat, where should the window's left edge jump to?",
            "idea": "<p>Store the last index where each character appeared. When the new character was seen <i>inside</i> the current window, jump <code>left</code> to one past that old position. The <code>max</code> stops <code>left</code> from moving backwards when the old position is outside the window.</p>",
            "code": '''
def length_of_longest_substring(s: str) -> int:
    last_seen = {}
    left = 0
    best = 0
    for right, ch in enumerate(s):
        if ch in last_seen:
            left = max(left, last_seen[ch] + 1)
        last_seen[ch] = right
        best = max(best, right - left + 1)
    return best

assert length_of_longest_substring("abcabcbb") == 3
assert length_of_longest_substring("bbbbb") == 1
assert length_of_longest_substring("pwwkew") == 3
assert length_of_longest_substring("abba") == 2
assert length_of_longest_substring("") == 0
''',
            "complexity": "O(n) time, O(alphabet) space.",
        },
        {
            "name": "Longest Repeating Character Replacement",
            "lc": 424,
            "level": "M",
            "prompt": "<p>You may change at most <code>k</code> characters. Return the length of the longest substring you can make of one repeated letter.</p><pre>s = \"AABABBA\", k = 1  →  4</pre>",
            "hint": "A window is fine if (window length − count of its most common letter) ≤ k.",
            "idea": "<p>In a window, keep the most common letter and change the rest. That costs <code>length − max_count</code> changes. Grow the window; if cost exceeds k, move left by one. A neat trick: <code>max_count</code> never needs to decrease, because the answer only improves when a bigger <code>max_count</code> appears.</p>",
            "code": '''
from collections import Counter

def character_replacement(s: str, k: int) -> int:
    count = Counter()
    left = 0
    max_count = 0
    best = 0
    for right, ch in enumerate(s):
        count[ch] += 1
        max_count = max(max_count, count[ch])
        if (right - left + 1) - max_count > k:
            count[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best

assert character_replacement("ABAB", 2) == 4
assert character_replacement("AABABBA", 1) == 4
''',
            "complexity": "O(n) time, O(26) space.",
        },
        {
            "name": "Minimum Window Substring",
            "lc": 76,
            "level": "H",
            "hot": True,
            "prompt": "<p>Return the shortest substring of <code>s</code> containing every character of <code>t</code> (including duplicates). Return \"\" if none.</p><pre>s = \"ADOBECODEBANC\", t = \"ABC\"  →  \"BANC\"</pre>",
            "hint": "Grow right until the window covers t. Then shrink left as long as it still covers t, recording the best.",
            "idea": "<p>Keep <code>need</code>: how many of each character we still owe, and <code>missing</code>: total characters still owed. Moving right pays off debts. When <code>missing == 0</code> the window is valid: record it, then drop characters from the left until a debt reappears. Because we want the <i>shortest</i>, we record inside the shrinking loop.</p>",
            "code": '''
from collections import Counter

def min_window(s: str, t: str) -> str:
    need = Counter(t)
    missing = len(t)
    left = 0
    best_len, best_start = float("inf"), 0
    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1                     # may go negative: we have extra
        while missing == 0:
            if right - left + 1 < best_len:
                best_len, best_start = right - left + 1, left
            need[s[left]] += 1
            if need[s[left]] > 0:         # we just gave up a needed char
                missing += 1
            left += 1
    return "" if best_len == float("inf") else s[best_start:best_start + best_len]

assert min_window("ADOBECODEBANC", "ABC") == "BANC"
assert min_window("a", "a") == "a"
assert min_window("a", "aa") == ""
''',
            "complexity": "O(|s| + |t|) time, O(alphabet) space.",
        },
    ],
}

PREFIX = {
    "id": "prefix-sums",
    "nav": "Prefix sums",
    "title": "Prefix sums",
    "tagline": "Precompute running totals once, then answer any range-sum question by subtracting two numbers.",
    "plain": """
<p>A prefix sum array stores running totals: <code>P[i]</code> is the sum of the first <code>i</code> numbers. Then the sum of any range <code>nums[a..b]</code> is just <code>P[b+1] − P[a]</code>. One O(n) pass of setup, then every range query is O(1).</p>
<p>The big trick: combine prefix sums with a hash map. "A subarray sums to k" means two prefix sums differ by k. So as you walk, ask the map: "how many earlier prefixes equal <code>current − k</code>?" This works even with negative numbers, where sliding windows fail.</p>
<div class="analogy"><b>Picture it:</b> a car's odometer. To know how far you drove between two towns, you don't re-drive the road; you subtract the two odometer readings.</div>
""",
    "signals": [
        "Many range-sum queries on data that doesn't change",
        "\"Count subarrays whose sum equals / is divisible by k\"",
        "Negative numbers in a subarray-sum problem (sliding window won't work)",
        "Equal numbers of two things in a subarray (map one to +1 and the other to −1)",
        "2D grid region sums",
    ],
    "pitfalls": [
        "Off-by-one: use a leading 0 so <code>P</code> has length n + 1",
        "Forgetting to seed the map with <code>{0: 1}</code> (the empty prefix), which misses subarrays starting at index 0",
        "Using prefix sums when values change often. Use a Fenwick or segment tree instead",
    ],
    "template": '''
from collections import defaultdict
from itertools import accumulate

nums = [3, -1, 4, 1, 5]
P = [0] + list(accumulate(nums))      # P[i] = sum(nums[:i])

def range_sum(a: int, b: int) -> int:
    """Sum of nums[a..b] inclusive."""
    return P[b + 1] - P[a]

assert range_sum(1, 3) == 4

def count_subarrays_with_sum(nums: list[int], k: int) -> int:
    seen = defaultdict(int)
    seen[0] = 1                       # the empty prefix
    total = count = 0
    for x in nums:
        total += x
        count += seen[total - k]      # earlier prefixes that make a sum of k
        seen[total] += 1
    return count

assert count_subarrays_with_sum([1, 1, 1], 2) == 2
''',
    "complexity": "O(n) setup, O(1) per range query; O(n) space.",
    "problems": [
        {
            "name": "Range Sum Query – Immutable",
            "lc": 303,
            "level": "E",
            "prompt": "<p>Build a class that answers <code>sum_range(left, right)</code> many times on a fixed array.</p>",
            "hint": "Pay once in the constructor so each query is O(1).",
            "idea": "<p>Store the prefix array with a leading 0 in the constructor. Each query subtracts two entries.</p>",
            "code": '''
class NumArray:
    def __init__(self, nums: list[int]):
        self.prefix = [0]
        for x in nums:
            self.prefix.append(self.prefix[-1] + x)

    def sum_range(self, left: int, right: int) -> int:
        return self.prefix[right + 1] - self.prefix[left]

arr = NumArray([-2, 0, 3, -5, 2, -1])
assert arr.sum_range(0, 2) == 1
assert arr.sum_range(2, 5) == -1
assert arr.sum_range(0, 5) == -3
''',
            "complexity": "O(n) build, O(1) per query.",
            "followups": ["The array also gets updates: Fenwick tree (see Advanced structures) for O(log n) both ways."],
        },
        {
            "name": "Subarray Sum Equals K",
            "lc": 560,
            "level": "M",
            "hot": True,
            "prompt": "<p>Count the contiguous subarrays whose sum equals <code>k</code>. Numbers may be negative.</p><pre>nums = [1, 2, 3], k = 3  →  2   ([1,2] and [3])</pre>",
            "hint": "sum(i..j) = P[j+1] − P[i]. For each j, how many earlier P values equal P[j+1] − k?",
            "idea": "<p>Walk once with a running total. A subarray ending here sums to k when some earlier running total equals <code>total − k</code>. A dict counts how many times each total has appeared. Seed it with <code>{0: 1}</code> for subarrays that start at index 0.</p>",
            "code": '''
from collections import defaultdict

def subarray_sum(nums: list[int], k: int) -> int:
    seen = defaultdict(int)
    seen[0] = 1
    total = count = 0
    for x in nums:
        total += x
        count += seen[total - k]
        seen[total] += 1
    return count

assert subarray_sum([1, 1, 1], 2) == 2
assert subarray_sum([1, 2, 3], 3) == 2
assert subarray_sum([1, -1, 0], 0) == 3
''',
            "complexity": "O(n) time, O(n) space.",
            "followups": ["Divisible by k (LC 974): key the map on <code>total % k</code>.", "Longest such subarray: store the first index of each total instead of a count."],
        },
        {
            "name": "Product of Array Except Self",
            "lc": 238,
            "level": "M",
            "prompt": "<p>Return an array where <code>out[i]</code> is the product of every element except <code>nums[i]</code>. No division, O(n) time.</p><pre>[1, 2, 3, 4]  →  [24, 12, 8, 6]</pre>",
            "hint": "out[i] = (product of everything to the left) × (product of everything to the right).",
            "idea": "<p>This is prefix sums with multiplication. First pass left to right: <code>out[i]</code> = product of everything before i. Second pass right to left with a running product of everything after i, multiplied in. Using the output array for the first pass keeps extra space at O(1).</p>",
            "code": '''
def product_except_self(nums: list[int]) -> list[int]:
    n = len(nums)
    out = [1] * n
    left = 1
    for i in range(n):
        out[i] = left
        left *= nums[i]
    right = 1
    for i in range(n - 1, -1, -1):
        out[i] *= right
        right *= nums[i]
    return out

assert product_except_self([1, 2, 3, 4]) == [24, 12, 8, 6]
assert product_except_self([-1, 1, 0, -3, 3]) == [0, 0, 9, 0, 0]
''',
            "complexity": "O(n) time, O(1) extra space (not counting the output).",
        },
        {
            "name": "Range Sum Query 2D – Immutable",
            "lc": 304,
            "level": "M",
            "prompt": "<p>Answer many queries for the sum of a rectangle <code>(r1, c1)</code> to <code>(r2, c2)</code> in a fixed matrix.</p>",
            "hint": "P[r][c] = sum of the rectangle from (0,0) to (r−1,c−1). Use inclusion–exclusion.",
            "idea": "<p>Build a 2D prefix table with an extra row and column of zeros. A rectangle's sum is the big rectangle, minus the strip above, minus the strip to the left, plus the corner that was subtracted twice.</p>",
            "code": '''
class NumMatrix:
    def __init__(self, matrix: list[list[int]]):
        rows, cols = len(matrix), len(matrix[0])
        self.P = [[0] * (cols + 1) for _ in range(rows + 1)]
        for r in range(rows):
            for c in range(cols):
                self.P[r + 1][c + 1] = (matrix[r][c] + self.P[r][c + 1]
                                        + self.P[r + 1][c] - self.P[r][c])

    def sum_region(self, r1: int, c1: int, r2: int, c2: int) -> int:
        P = self.P
        return P[r2 + 1][c2 + 1] - P[r1][c2 + 1] - P[r2 + 1][c1] + P[r1][c1]

m = NumMatrix([[3, 0, 1, 4, 2], [5, 6, 3, 2, 1], [1, 2, 0, 1, 5],
               [4, 1, 0, 1, 7], [1, 0, 3, 0, 5]])
assert m.sum_region(2, 1, 4, 3) == 8
assert m.sum_region(1, 1, 2, 2) == 11
assert m.sum_region(1, 2, 2, 4) == 12
''',
            "complexity": "O(rows · cols) build, O(1) per query.",
        },
        {
            "name": "Number of Submatrices That Sum to Target",
            "lc": 1074,
            "level": "H",
            "prompt": "<p>Count the non-empty submatrices whose elements sum to <code>target</code>.</p><pre>[[0,1,0],[1,1,1],[0,1,0]], target = 0  →  4</pre>",
            "hint": "Fix a top row and a bottom row. Squash the rows between them into one array of column sums. Now it's Subarray Sum Equals K.",
            "idea": "<p>Pick every pair of rows (top, bottom). For that pair, keep an array where each entry is the sum of one column between those rows. Any submatrix spanning exactly those rows is a subarray of that array. Count subarrays equal to target with the prefix-sum-plus-dict trick. Adding one row at a time to the column sums keeps each pair O(cols).</p>",
            "code": '''
from collections import defaultdict

def num_submatrix_sum_target(matrix: list[list[int]], target: int) -> int:
    rows, cols = len(matrix), len(matrix[0])
    count = 0
    for top in range(rows):
        col_sums = [0] * cols
        for bottom in range(top, rows):
            for c in range(cols):
                col_sums[c] += matrix[bottom][c]
            seen = defaultdict(int)
            seen[0] = 1
            total = 0
            for x in col_sums:                # Subarray Sum Equals K
                total += x
                count += seen[total - target]
                seen[total] += 1
    return count

assert num_submatrix_sum_target([[0, 1, 0], [1, 1, 1], [0, 1, 0]], 0) == 4
assert num_submatrix_sum_target([[1, -1], [-1, 1]], 0) == 5
assert num_submatrix_sum_target([[904]], 0) == 0
''',
            "complexity": "O(rows² · cols) time, O(cols) space. Loop over the smaller dimension squared.",
        },
    ],
}

BINARY_SEARCH = {
    "id": "binary-search",
    "nav": "Binary search",
    "title": "Binary search",
    "tagline": "Halve the search space every step. Works on sorted arrays and on any yes/no question that flips once.",
    "plain": """
<p>Classic binary search finds a value in a sorted array by checking the middle and throwing away the half that can't contain it. After about 30 steps you've searched a billion items.</p>
<p>The more powerful idea is <b>binary search on the answer</b>. Many problems ask for "the minimum X such that something is possible". If being possible at X means it's also possible at every bigger X, then the answers look like <code>no no no no yes yes yes</code>. Binary search finds the first <i>yes</i>. You only need to write a function <code>feasible(x)</code>.</p>
<div class="analogy"><b>Picture it:</b> guessing a number between 1 and 100 when someone says "higher" or "lower". You always guess the middle, so you never need more than 7 guesses.</div>
""",
    "signals": [
        "The input is sorted, or rotated sorted",
        "\"Minimum capacity / speed / time such that…\" or \"maximize the minimum\"",
        "n up to 10⁹ or a huge value range: you can't try every value",
        "A check that is easy to verify for a given answer but hard to compute directly",
    ],
    "pitfalls": [
        "Infinite loops from <code>lo = mid</code> with <code>mid = (lo + hi) // 2</code>. Use one template and stick to it",
        "Wrong search bounds: make sure the true answer is inside <code>[lo, hi]</code>",
        "A <code>feasible</code> function that isn't monotonic (then binary search is wrong)",
    ],
    "template": '''
def first_true(lo: int, hi: int, feasible) -> int:
    """Smallest x in [lo, hi] with feasible(x) True.
    Assumes feasible looks like F F F T T T. Returns hi + 1 if all False."""
    hi += 1
    while lo < hi:
        mid = (lo + hi) // 2
        if feasible(mid):
            hi = mid          # mid might be the answer: keep it
        else:
            lo = mid + 1      # mid is too small: discard it
    return lo

# Classic search expressed with the same template:
a = [1, 3, 5, 7, 9]
i = first_true(0, len(a) - 1, lambda m: a[m] >= 7)
assert i == 3

# Answer search: smallest integer whose square is >= 50
assert first_true(0, 50, lambda x: x * x >= 50) == 8
''',
    "complexity": "O(log(range)) checks. With an O(n) feasibility check: O(n log range).",
    "problems": [
        {
            "name": "Binary Search",
            "lc": 704,
            "level": "E",
            "prompt": "<p>Return the index of <code>target</code> in a sorted list, or −1.</p>",
            "hint": "Keep an inclusive range [lo, hi] and shrink it around mid.",
            "idea": "<p>Look at the middle. If it's the target, done. If it's smaller, the target must be to the right; otherwise to the left. Stop when the range is empty.</p>",
            "code": '''
def search(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

assert search([-1, 0, 3, 5, 9, 12], 9) == 4
assert search([-1, 0, 3, 5, 9, 12], 2) == -1
assert search([], 1) == -1
''',
            "complexity": "O(log n) time, O(1) space.",
        },
        {
            "name": "Find First and Last Position of Element",
            "lc": 34,
            "level": "M",
            "prompt": "<p>In a sorted list, return <code>[first, last]</code> index of <code>target</code>, or <code>[-1, -1]</code>. O(log n).</p><pre>[5, 7, 7, 8, 8, 10], 8  →  [3, 4]</pre>",
            "hint": "Two binary searches: the first index ≥ target, and the first index > target.",
            "idea": "<p>The first position is the first index where <code>a[i] ≥ target</code>. The last position is one before the first index where <code>a[i] &gt; target</code>. Python's <code>bisect</code> does both; be ready to write it yourself too.</p>",
            "code": '''
from bisect import bisect_left, bisect_right

def search_range(nums: list[int], target: int) -> list[int]:
    lo = bisect_left(nums, target)
    if lo == len(nums) or nums[lo] != target:
        return [-1, -1]
    return [lo, bisect_right(nums, target) - 1]

def lower_bound(nums: list[int], target: int) -> int:
    """Hand-written bisect_left, in case the interviewer asks."""
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

assert search_range([5, 7, 7, 8, 8, 10], 8) == [3, 4]
assert search_range([5, 7, 7, 8, 8, 10], 6) == [-1, -1]
assert search_range([], 0) == [-1, -1]
assert lower_bound([5, 7, 7, 8], 7) == 1
''',
            "complexity": "O(log n) time, O(1) space.",
        },
        {
            "name": "Search in Rotated Sorted Array",
            "lc": 33,
            "level": "M",
            "hot": True,
            "prompt": "<p>A sorted list of distinct values was rotated at an unknown point, like <code>[4,5,6,7,0,1,2]</code>. Find <code>target</code>'s index in O(log n), or −1.</p>",
            "hint": "At any mid, at least one half (left or right) is properly sorted. Is the target inside that sorted half?",
            "idea": "<p>Compare <code>nums[lo]</code> with <code>nums[mid]</code>. If <code>nums[lo] ≤ nums[mid]</code>, the left half is sorted: if the target lies within its range, search left, else right. Otherwise the right half is sorted; do the mirror check. Each step still throws away half.</p>",
            "code": '''
def search_rotated(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:                  # left half sorted
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                                      # right half sorted
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1

assert search_rotated([4, 5, 6, 7, 0, 1, 2], 0) == 4
assert search_rotated([4, 5, 6, 7, 0, 1, 2], 3) == -1
assert search_rotated([3, 1], 1) == 1
assert search_rotated([1], 0) == -1
''',
            "complexity": "O(log n) time, O(1) space.",
            "followups": ["With duplicates (LC 81): when <code>nums[lo] == nums[mid] == nums[hi]</code> you can't tell which half is sorted; shrink both ends by one. Worst case O(n)."],
        },
        {
            "name": "Koko Eating Bananas",
            "lc": 875,
            "level": "M",
            "prompt": "<p>Piles of bananas; each hour Koko eats up to <code>k</code> bananas from one pile. Find the minimum <code>k</code> to finish all piles within <code>h</code> hours.</p><pre>piles = [3, 6, 7, 11], h = 8  →  4</pre>",
            "hint": "If speed k works, every faster speed works too. That's monotonic.",
            "idea": "<p>Binary search on the speed between 1 and the largest pile. <code>feasible(k)</code>: total hours = sum of <code>ceil(pile / k)</code>; is it ≤ h? Find the smallest feasible k. Integer ceiling in Python: <code>(p + k − 1) // k</code> or <code>-(-p // k)</code>.</p>",
            "code": '''
def min_eating_speed(piles: list[int], h: int) -> int:
    def feasible(k: int) -> bool:
        return sum((p + k - 1) // k for p in piles) <= h

    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo

assert min_eating_speed([3, 6, 7, 11], 8) == 4
assert min_eating_speed([30, 11, 23, 4, 20], 5) == 30
assert min_eating_speed([30, 11, 23, 4, 20], 6) == 23
''',
            "complexity": "O(n log max(piles)) time, O(1) space.",
        },
        {
            "name": "Split Array Largest Sum",
            "lc": 410,
            "level": "H",
            "prompt": "<p>Split <code>nums</code> (non-negative) into <code>k</code> contiguous parts to minimize the largest part's sum.</p><pre>[7, 2, 5, 10, 8], k = 2  →  18   ([7,2,5] and [10,8])</pre>",
            "hint": "Guess the answer X. Can you greedily cut the array into ≤ k parts, each with sum ≤ X?",
            "idea": "<p>The answer is between <code>max(nums)</code> (each part at least holds its biggest item) and <code>sum(nums)</code> (one part). For a guess X, fill parts greedily left to right, starting a new part when adding the next number would exceed X. If that uses ≤ k parts, X works. Binary search the smallest X that works. This \"minimize the maximum\" shape shows up often (ship packages in D days, painters partition).</p>",
            "code": '''
def split_array(nums: list[int], k: int) -> int:
    def parts_needed(cap: int) -> int:
        parts, current = 1, 0
        for x in nums:
            if current + x > cap:
                parts += 1
                current = 0
            current += x
        return parts

    lo, hi = max(nums), sum(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if parts_needed(mid) <= k:
            hi = mid
        else:
            lo = mid + 1
    return lo

assert split_array([7, 2, 5, 10, 8], 2) == 18
assert split_array([1, 2, 3, 4, 5], 2) == 9
assert split_array([1, 4, 4], 3) == 4
''',
            "complexity": "O(n log(sum)) time, O(1) space.",
        },
        {
            "name": "Median of Two Sorted Arrays",
            "lc": 4,
            "level": "H",
            "hot": True,
            "prompt": "<p>Return the median of two sorted arrays in O(log(min(m, n))).</p><pre>[1, 3], [2]     →  2.0\n[1, 2], [3, 4]  →  2.5</pre>",
            "hint": "Binary search how many elements the left half takes from the shorter array. The rest come from the longer one.",
            "idea": "<p>The median splits all numbers into a left half and a right half of equal size. Choose <code>i</code> items from array A for the left half; then <code>j = half − i</code> come from B. The split is correct when everything on the left is ≤ everything on the right: <code>A[i−1] ≤ B[j]</code> and <code>B[j−1] ≤ A[i]</code>. If A's left part is too big, take fewer from A; otherwise take more. Use ±infinity for missing neighbors at the edges.</p>",
            "code": '''
def find_median_sorted_arrays(a: list[int], b: list[int]) -> float:
    if len(a) > len(b):
        a, b = b, a                       # binary search the shorter array
    m, n = len(a), len(b)
    half = (m + n + 1) // 2
    lo, hi = 0, m
    INF = float("inf")
    while lo <= hi:
        i = (lo + hi) // 2                # items taken from a
        j = half - i                      # items taken from b
        a_left = a[i - 1] if i > 0 else -INF
        a_right = a[i] if i < m else INF
        b_left = b[j - 1] if j > 0 else -INF
        b_right = b[j] if j < n else INF
        if a_left <= b_right and b_left <= a_right:
            if (m + n) % 2:
                return float(max(a_left, b_left))
            return (max(a_left, b_left) + min(a_right, b_right)) / 2
        if a_left > b_right:
            hi = i - 1                    # took too many from a
        else:
            lo = i + 1
    raise ValueError("inputs must be sorted")

assert find_median_sorted_arrays([1, 3], [2]) == 2.0
assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5
assert find_median_sorted_arrays([], [1]) == 1.0
assert find_median_sorted_arrays([2], []) == 2.0
''',
            "complexity": "O(log min(m, n)) time, O(1) space.",
        },
    ],
}

STACKS = {
    "id": "stacks",
    "nav": "Stacks and monotonic stacks",
    "title": "Stacks and monotonic stacks",
    "tagline": "Last in, first out. Perfect for nesting, undo, and \"next bigger element\" questions.",
    "plain": """
<p>A stack is a pile of plates: you add and remove from the top. In Python it's a plain list with <code>append</code> and <code>pop</code>. Use it whenever the most recent unfinished thing must be handled first, like matching brackets or nested expressions.</p>
<p>A <b>monotonic stack</b> keeps its items in sorted order (always increasing or always decreasing). When a new item breaks the order, you pop items off, and each pop is a moment where you learn something: "the item I just popped has finally found its next bigger element". Each item is pushed and popped once, so it's O(n) even though there's a loop inside a loop.</p>
<div class="analogy"><b>Picture it:</b> people standing in a line facing right, each wanting to know who is the first taller person ahead of them. When a tall person arrives, everyone shorter at the back of the line gets their answer and leaves the line.</div>
""",
    "signals": [
        "Matching or nested structures: brackets, tags, <code>3[a2[c]]</code>",
        "\"Next greater / smaller element\", \"how many days until warmer\"",
        "Largest rectangle, visible buildings, stock span",
        "Evaluating expressions, or simplifying paths like <code>/a/./b/../c</code>",
        "Max or min of every window of size k (monotonic <i>deque</i>)",
    ],
    "pitfalls": [
        "Calling <code>stack[-1]</code> or <code>pop()</code> on an empty stack. Always check <code>if stack</code>",
        "Storing values when you need distances. Store indices; you can always look up the value",
        "Forgetting the items still in the stack after the loop ends (flush them, or add a sentinel)",
    ],
    "template": '''
def next_greater(nums: list[int]) -> list[int]:
    """For each item, the next item to its right that is bigger (-1 if none)."""
    out = [-1] * len(nums)
    stack = []                       # indices; their values are decreasing
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            out[stack.pop()] = x     # x is the answer for the popped index
        stack.append(i)
    return out

assert next_greater([2, 1, 2, 4, 3]) == [4, 2, 4, -1, -1]
''',
    "complexity": "O(n) time (each index pushed and popped once), O(n) space.",
    "problems": [
        {
            "name": "Valid Parentheses",
            "lc": 20,
            "level": "E",
            "prompt": "<p>Given a string of <code>()[]{}</code>, is every bracket closed in the right order?</p><pre>\"([]{})\"  →  True\n\"(]\"      →  False</pre>",
            "hint": "Each closing bracket must match the most recent unmatched opening bracket.",
            "idea": "<p>Push opening brackets. On a closing bracket, the top of the stack must be its partner; pop it. At the end the stack must be empty.</p>",
            "code": '''
def is_valid(s: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:
            stack.append(ch)
    return not stack

assert is_valid("([]{})")
assert not is_valid("(]")
assert not is_valid("((")
assert not is_valid("]")
''',
            "complexity": "O(n) time, O(n) space.",
            "followups": ["Minimum removals to make it valid (LC 1249): stack of indices of unmatched brackets."],
        },
        {
            "name": "Daily Temperatures",
            "lc": 739,
            "level": "M",
            "hot": True,
            "prompt": "<p>For each day, how many days until a warmer temperature? 0 if never.</p><pre>[73,74,75,71,69,72,76,73]  →  [1,1,4,2,1,1,0,0]</pre>",
            "hint": "This is \"next greater element\", but you want the distance, so store indices.",
            "idea": "<p>Keep a stack of days still waiting for a warmer day; their temperatures are decreasing from bottom to top. A warmer day pops every cooler day on top and fills in the distance.</p>",
            "code": '''
def daily_temperatures(temps: list[int]) -> list[int]:
    out = [0] * len(temps)
    waiting = []                                  # indices, decreasing temps
    for today, t in enumerate(temps):
        while waiting and temps[waiting[-1]] < t:
            day = waiting.pop()
            out[day] = today - day
        waiting.append(today)
    return out

assert daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]
assert daily_temperatures([30, 60, 90]) == [1, 1, 0]
''',
            "complexity": "O(n) time, O(n) space.",
        },
        {
            "name": "Decode String",
            "lc": 394,
            "level": "M",
            "hot": True,
            "prompt": "<p>Decode strings of the form <code>k[encoded]</code>, which may nest.</p><pre>\"3[a2[c]]\"  →  \"accaccacc\"</pre>",
            "hint": "On '[' save what you've built so far and the repeat count. On ']' restore and repeat.",
            "idea": "<p>Keep the string being built and the number being read. On <code>[</code>, push <code>(string so far, count)</code> and start fresh. On <code>]</code>, pop and set <code>current = saved + current × count</code>. Digits can be more than one character long, like <code>12[a]</code>.</p>",
            "code": '''
def decode_string(s: str) -> str:
    stack = []
    current = ""
    num = 0
    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch == "[":
            stack.append((current, num))
            current, num = "", 0
        elif ch == "]":
            before, times = stack.pop()
            current = before + current * times
        else:
            current += ch
    return current

assert decode_string("3[a]2[bc]") == "aaabcbc"
assert decode_string("3[a2[c]]") == "accaccacc"
assert decode_string("2[abc]3[cd]ef") == "abcabccdcdcdef"
assert decode_string("10[x]") == "x" * 10
''',
            "complexity": "O(output length) time and space.",
        },
        {
            "name": "Largest Rectangle in Histogram",
            "lc": 84,
            "level": "H",
            "prompt": "<p>Bars of width 1 with given heights. Return the area of the largest rectangle inside the histogram.</p><pre>[2, 1, 5, 6, 2, 3]  →  10</pre>",
            "hint": "For each bar, the widest rectangle of that height stretches until the first shorter bar on each side.",
            "idea": "<p>Keep a stack of indices with increasing heights. When a shorter bar arrives, the bar on top can't extend further right. Pop it: its right edge is the current index, and its left edge is the new top of the stack (the previous shorter bar). Area = height × width. A 0-height sentinel at the end flushes everything.</p>",
            "code": '''
def largest_rectangle_area(heights: list[int]) -> int:
    bars = heights + [0]                      # sentinel flushes the stack
    stack = []                                # indices, increasing heights
    best = 0
    for i, h in enumerate(bars):
        while stack and bars[stack[-1]] > h:
            height = bars[stack.pop()]
            left = stack[-1] if stack else -1
            best = max(best, height * (i - left - 1))
        stack.append(i)
    return best

assert largest_rectangle_area([2, 1, 5, 6, 2, 3]) == 10
assert largest_rectangle_area([2, 4]) == 4
assert largest_rectangle_area([]) == 0
''',
            "complexity": "O(n) time, O(n) space.",
            "followups": ["Maximal Rectangle in a 0/1 matrix (LC 85): build a histogram per row and reuse this function."],
        },
        {
            "name": "Sliding Window Maximum",
            "lc": 239,
            "level": "H",
            "hot": True,
            "prompt": "<p>Return the maximum of every window of size <code>k</code>.</p><pre>[1,3,-1,-3,5,3,6,7], k = 3  →  [3,3,5,5,6,7]</pre>",
            "hint": "If a newer item is bigger than an older one, the older one can never be a window max again. Throw it away.",
            "idea": "<p>Keep a deque of indices whose values are decreasing. When a new value arrives, pop smaller values from the back (they're useless now). Pop the front if it has slid out of the window. The front is always the current max.</p>",
            "code": '''
from collections import deque

def max_sliding_window(nums: list[int], k: int) -> list[int]:
    dq = deque()                          # indices, values decreasing
    out = []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()                  # front fell out of the window
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out

assert max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
assert max_sliding_window([1], 1) == [1]
assert max_sliding_window([9, 8, 7, 6], 2) == [9, 8, 7]
''',
            "complexity": "O(n) time, O(k) space.",
        },
    ],
}

PATTERNS = [HASHING, TWO_POINTERS, SLIDING, PREFIX, BINARY_SEARCH, STACKS]
