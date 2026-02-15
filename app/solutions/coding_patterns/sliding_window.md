# Sliding Window — Complete Interview Guide

## When to Use This Pattern

**Signals that indicate Sliding Window:**
1. The problem involves a **contiguous subarray or substring** (not subsequence)
2. You see keywords like "longest", "shortest", "minimum window", "maximum sum of subarray"
3. There is a **constraint** on the window (at most k distinct characters, sum >= target, contains all characters)
4. The brute force is O(n^2) or O(n^3) checking all subarrays, but each window's state can be updated incrementally from the previous window
5. The problem asks for **fixed-size** subarray statistics (max sum of k consecutive elements, averages)
6. There is a **monotonic relationship** between window expansion and the constraint (expanding can only add, contracting can only remove)

**When NOT to use it:**
- The problem asks for a **subsequence** (elements need not be contiguous) -- use DP instead
- You need to find pairs/triplets satisfying a condition -- use two pointers or hash map
- Elements can be rearranged -- this breaks the contiguity requirement
- The window state cannot be incrementally updated (e.g., median requires more complex data structures)

## Core Mechanics

The sliding window pattern maintains a window `[left, right]` over a sequence and updates window state incrementally as the window expands (right moves right) or contracts (left moves right).

**Why it works:** When you move the right boundary one step, you only need to account for the one new element entering the window. When you move the left boundary one step, you only remove one element. This makes each expansion/contraction O(1) amortized, instead of recomputing the entire window state from scratch.

**Two flavors:**

1. **Fixed-size window:** The window size k is given. Slide the window one position at a time, adding the new element and removing the old one.

2. **Variable-size window:** The window grows and shrinks based on a condition. Expand by moving right until the window violates or satisfies a condition, then contract by moving left to restore validity or optimize.

**The invariant for variable-size windows:** We maintain two pointers such that all subarrays shorter than our current best have been considered. The right pointer explores new territory; the left pointer prunes suboptimal starts.

### ASCII Walkthrough (Variable-Size)

```
Problem: Longest substring without repeating characters
Input: "abcabcbb"

right=0: window="a"     chars={a}         len=1  max=1
         L   R
         a b c a b c b b

right=1: window="ab"    chars={a,b}       len=2  max=2
         L R
         a b c a b c b b

right=2: window="abc"   chars={a,b,c}     len=3  max=3
         L   R
         a b c a b c b b

right=3: char 'a' already in window! Move L past previous 'a'
         window="bca"   chars={b,c,a}     len=3  max=3
           L   R
         a b c a b c b b

right=4: char 'b' already in window! Move L past previous 'b'
         window="cab"   chars={c,a,b}     len=3  max=3
             L   R
         a b c a b c b b

...continues, max stays 3
```

**Complexity:** Each element enters and leaves the window at most once, giving O(n) total work. Space depends on what you track (hash map, frequency array, etc.).

## The Template

**Variable-size window (most common):**
```python
def sliding_window_variable(s):
    """Find longest/shortest substring satisfying a condition."""
    window_state = {}  # or Counter, set, etc.
    left = 0
    best = 0  # or float('inf') for shortest

    for right in range(len(s)):
        # Expand: add s[right] to window state
        window_state[s[right]] = window_state.get(s[right], 0) + 1

        # Contract: shrink window while condition is violated
        while window_is_invalid(window_state):
            # Remove s[left] from window state
            window_state[s[left]] -= 1
            if window_state[s[left]] == 0:
                del window_state[s[left]]
            left += 1

        # Update answer
        best = max(best, right - left + 1)

    return best
```

**Fixed-size window:**
```python
def sliding_window_fixed(nums, k):
    """Compute something for all windows of size k."""
    window_sum = sum(nums[:k])
    best = window_sum

    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]  # add new, remove old
        best = max(best, window_sum)

    return best
```

```go
func slidingWindowVariable(s string) int {
	windowState := make(map[byte]int)
	left := 0
	best := 0

	for right := 0; right < len(s); right++ {
		windowState[s[right]]++

		for windowIsInvalid(windowState) {
			windowState[s[left]]--
			if windowState[s[left]] == 0 {
				delete(windowState, s[left])
			}
			left++
		}

		if right-left+1 > best {
			best = right - left + 1
		}
	}
	return best
}
```

## Variant Subpatterns

### 1. Fixed-Size Window

Window size is given. You slide it across the array, maintaining state incrementally.

```python
def fixed_window(nums, k):
    # Initialize first window
    window = sum(nums[:k])
    best = window
    for i in range(k, len(nums)):
        window += nums[i] - nums[i - k]
        best = max(best, window)
    return best
```

Problems: Maximum Average Subarray, Maximum Sum Subarray of Size K.

### 2. Variable-Size Window (Longest)

Expand the window as far as possible while maintaining validity. Track the maximum window size.

```python
def longest_valid_window(s):
    left = 0
    best = 0
    state = set()
    for right in range(len(s)):
        while s[right] in state:
            state.remove(s[left])
            left += 1
        state.add(s[right])
        best = max(best, right - left + 1)
    return best
```

Problems: Longest Substring Without Repeating Characters, Longest Substring with At Most K Distinct Characters.

### 3. Variable-Size Window (Shortest)

Expand the window until a condition is met, then contract to find the minimum window satisfying the condition.

```python
def shortest_valid_window(s, condition):
    left = 0
    best = float('inf')
    for right in range(len(s)):
        # expand: update state with s[right]
        while condition_is_met():
            best = min(best, right - left + 1)
            # contract: remove s[left]
            left += 1
    return best if best != float('inf') else 0
```

Problems: Minimum Window Substring, Minimum Size Subarray Sum.

### 4. Sliding Window with Monotonic Deque

For problems requiring the max/min within a sliding window, use a deque to maintain elements in monotonic order.

```python
from collections import deque

def window_max_with_deque(nums, k):
    dq = deque()  # stores indices, values in decreasing order
    result = []
    for i in range(len(nums)):
        # Remove elements outside the window
        while dq and dq[0] < i - k + 1:
            dq.popleft()
        # Maintain decreasing order
        while dq and nums[dq[-1]] <= nums[i]:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result
```

Problems: Sliding Window Maximum, Shortest Subarray with Sum at Least K.

---

## Problem Walkthroughs

---

### Problem: Best Time to Buy and Sell Stock (LC #121) — Easy

**Companies:** Meta, Amazon, Google, Microsoft, Goldman Sachs, every company
**Why it is asked:** Tests the simplest form of "track a running minimum and maximize the gap." It is a sliding window of size 2 with a running minimum.

**The Brute Force:**
```python
def maxProfit_brute(prices):
    # O(n^2) time, O(1) space
    max_profit = 0
    n = len(prices)
    for i in range(n):
        for j in range(i + 1, n):
            profit = prices[j] - prices[i]
            max_profit = max(max_profit, profit)
    return max_profit
```

Check every pair (buy day, sell day) where sell day > buy day. O(n^2).

**The Key Insight:** As you scan left to right, you only need to track the minimum price seen so far. For each day, the best profit achievable by selling on that day is `prices[day] - min_price_so_far`. This is essentially a sliding window where the left boundary is the day of minimum price.

**Optimal Solution:**
```python
def maxProfit(prices):
    min_price = float('inf')
    max_profit = 0

    for price in prices:
        min_price = min(min_price, price)
        profit = price - min_price
        max_profit = max(max_profit, profit)

    return max_profit
```

**Dry Run:**
```
Input: prices = [7, 1, 5, 3, 6, 4]

price=7: min_price=7, profit=0, max_profit=0
price=1: min_price=1, profit=0, max_profit=0
price=5: min_price=1, profit=4, max_profit=4
price=3: min_price=1, profit=2, max_profit=4
price=6: min_price=1, profit=5, max_profit=5
price=4: min_price=1, profit=3, max_profit=5

Answer: 5 (buy at 1, sell at 6)
```

**Edge Cases:**
- Prices always decrease: `[7,6,4,3,1]` -- max_profit stays 0, return 0.
- Single price: cannot sell, return 0.
- Two prices: one comparison.
- All same price: profit is 0.

**Complexity:** Time O(n), Space O(1).

**Follow-up questions interviewers might ask:**
- "What if you can buy and sell multiple times?" -- LC #122, greedy: add every positive difference.
- "What if there is a cooldown?" -- LC #309, DP with states.
- "What if there is a transaction fee?" -- LC #714, DP with fee deduction.

---

### Problem: Longest Substring Without Repeating Characters (LC #3) — Medium

**Companies:** Amazon, Meta, Google, Microsoft, Bloomberg, Uber (top-10 most asked problem ever)
**Why it is asked:** The canonical variable-size sliding window problem. Tests whether you can maintain window state with a hash map and correctly handle the left pointer advancement.

**The Brute Force:**
```python
def lengthOfLongestSubstring_brute(s):
    # O(n^3) time: O(n^2) substrings, O(n) uniqueness check each
    max_len = 0
    n = len(s)
    for i in range(n):
        seen = set()
        for j in range(i, n):
            if s[j] in seen:
                break
            seen.add(s[j])
            max_len = max(max_len, j - i + 1)
    return max_len
```

For every starting position, extend rightward until a duplicate is found. O(n^2) substrings with O(1) extension checks using a set, so O(n^2) total. (The earlier O(n^3) analysis applies if you check uniqueness from scratch each time.)

**The Key Insight:** When you find a duplicate character at position `right`, you do not need to start over from `left + 1`. Instead, jump `left` directly past the previous occurrence of that character. A hash map storing each character's last-seen index enables this O(1) jump.

**Optimal Solution:**
```python
def lengthOfLongestSubstring(s):
    char_index = {}  # char -> last seen index
    left = 0
    max_len = 0

    for right in range(len(s)):
        if s[right] in char_index and char_index[s[right]] >= left:
            left = char_index[s[right]] + 1

        char_index[s[right]] = right
        max_len = max(max_len, right - left + 1)

    return max_len
```

**Dry Run:**
```
Input: s = "abcabcbb"

right=0 'a': char_index={'a':0}, left=0, window="a",   len=1, max=1
right=1 'b': char_index={'a':0,'b':1}, left=0, window="ab",  len=2, max=2
right=2 'c': char_index={..,'c':2}, left=0, window="abc", len=3, max=3
right=3 'a': 'a' seen at 0 >= left(0), left=1. char_index={'a':3,'b':1,'c':2}
             window="bca", len=3, max=3
right=4 'b': 'b' seen at 1 >= left(1), left=2. char_index={'a':3,'b':4,'c':2}
             window="cab", len=3, max=3
right=5 'c': 'c' seen at 2 >= left(2), left=3. char_index={'a':3,'b':4,'c':5}
             window="abc", len=3, max=3
right=6 'b': 'b' seen at 4 >= left(3), left=5. char_index={'a':3,'b':6,'c':5}
             window="cb", len=2, max=3
right=7 'b': 'b' seen at 6 >= left(5), left=7. char_index={'a':3,'b':7,'c':5}
             window="b", len=1, max=3

Answer: 3
```

**Edge Cases:**
- Empty string: return 0.
- All unique characters: return len(s).
- All same character: return 1.
- String of length 1: return 1.

**Complexity:** Time O(n), Space O(min(n, charset_size)). For ASCII, space is O(128) = O(1).

**Follow-up questions interviewers might ask:**
- "What if we need the actual substring, not just the length?" -- Track start position of the best window.
- "What is the space complexity?" -- O(min(n, m)) where m is the character set size.
- "Can you use an array instead of a hash map?" -- Yes, for ASCII use `int[128]`, which is faster.
- "What about Unicode?" -- Hash map is more appropriate; array would be too large.

---

### Problem: Minimum Window Substring (LC #76) — Hard

**Companies:** Meta, Google, Amazon, Microsoft, Uber, Apple (extremely common)
**Why it is asked:** The hardest standard sliding window problem. Tests your ability to track required character frequencies with two counters and handle the contraction phase correctly.

**The Brute Force:**
```python
def minWindow_brute(s, t):
    # O(n^2 * m) time where n = len(s), m = len(t)
    from collections import Counter
    t_count = Counter(t)
    best = ""
    n = len(s)
    for i in range(n):
        for j in range(i + len(t), n + 1):
            window = s[i:j]
            w_count = Counter(window)
            if all(w_count[c] >= t_count[c] for c in t_count):
                if best == "" or len(window) < len(best):
                    best = window
                break  # extending further from this i only makes it longer
    return best
```

Check all substrings of s, verify each contains all characters of t with sufficient frequency. O(n^2) substrings, O(m) verification each.

**The Key Insight:** Use a variable-size window. Expand by moving `right` to include more characters. Track how many of the required characters are satisfied using a `formed` counter. When `formed` equals the number of distinct required characters, the window is valid -- contract from the left to minimize it, updating the best answer. The key data structures are:
- `need`: frequency count of characters in t
- `window_counts`: frequency count of characters in the current window
- `formed`: number of characters in `need` that are fully satisfied in the window

**Optimal Solution:**
```python
from collections import Counter

def minWindow(s, t):
    if not s or not t or len(s) < len(t):
        return ""

    need = Counter(t)
    required = len(need)  # number of unique chars we need

    window_counts = {}
    formed = 0  # how many unique chars in need are fully satisfied

    best = (float('inf'), 0, 0)  # (length, left, right)
    left = 0

    for right in range(len(s)):
        ch = s[right]
        window_counts[ch] = window_counts.get(ch, 0) + 1

        # Check if this character's requirement is now fully met
        if ch in need and window_counts[ch] == need[ch]:
            formed += 1

        # Contract the window until it ceases to be valid
        while formed == required:
            # Update best
            window_len = right - left + 1
            if window_len < best[0]:
                best = (window_len, left, right)

            # Remove leftmost character
            leaving = s[left]
            window_counts[leaving] -= 1
            if leaving in need and window_counts[leaving] < need[leaving]:
                formed -= 1
            left += 1

    return "" if best[0] == float('inf') else s[best[1]:best[2] + 1]
```

**Dry Run:**
```
Input: s = "ADOBECODEBANC", t = "ABC"
need = {'A':1, 'B':1, 'C':1}, required = 3

right=0 'A': wc={'A':1}, formed=1 (A met)
right=1 'D': wc={'A':1,'D':1}, formed=1
right=2 'O': formed=1
right=3 'B': wc={..,'B':1}, formed=2 (B met)
right=4 'E': formed=2
right=5 'C': wc={..,'C':1}, formed=3 (C met) -- VALID!
  Contract: window="ADOBEC" len=6, best=(6,0,5)
    remove 'A': wc['A']=0 < need['A']=1, formed=2, left=1
  formed < required, stop contracting.

right=6 'O': formed=2
right=7 'D': formed=2
right=8 'E': formed=2
right=9 'B': formed=2
right=10 'A': wc['A']=1, formed=3 -- VALID!
  Contract: window="DOBECODEBA" ...hmm let me track more carefully.

  Actually window is s[1:11] = "DOBECODEBANC"... let me re-count.
  left=1, right=10: window = s[1:11] = "DOBECODEBA", len=10
    remove s[1]='D': not in need, left=2
    window = s[2:11], len=9
    remove s[2]='O': not in need, left=3
    window = s[3:11], len=8
    remove s[3]='B': wc['B']=1 (had 2), 1 >= 1, still formed=3, left=4
    window = s[4:11] = "ECODEBA", len=7
    remove s[4]='E': not in need, left=5
    window = s[5:11] = "CODEBA", len=6, best stays (6,0,5)
    remove s[5]='C': wc['C']=0 < 1, formed=2, left=6
  Stop.

right=11 'N': formed=2
right=12 'C': wc['C']=1, formed=3 -- VALID!
  left=6, right=12: window = s[6:13] = "ODEBANC", len=7
    remove s[6]='O': left=7, len=6
    remove s[7]='D': left=8, len=5
    remove s[8]='E': left=9, len=4, best=(4,9,12)
    remove s[9]='B': wc['B']=0 < 1, formed=2, left=10
  Stop.

Answer: s[9:13] = "BANC"
```

**Edge Cases:**
- t longer than s: return "".
- t has duplicate characters: `t = "AA"` means we need two A's in the window.
- s == t: return s.
- No valid window exists: return "".
- Single character: `s = "a"`, `t = "a"` returns "a".

**Complexity:** Time O(n + m) where n = len(s), m = len(t). Each character in s is added and removed at most once. Building `need` takes O(m). Space O(n + m) for the hash maps.

**Follow-up questions interviewers might ask:**
- "Can you optimize using a filtered s?" -- Yes, remove characters not in t from s (store as list of (index, char)), then apply the same algorithm. Helps when len(s) >> len(t) and s has many irrelevant characters.
- "What if there are multiple minimum windows of the same length?" -- Return the first one found (leftmost).
- "How does this differ from Minimum Window Subsequence?" -- This checks for character frequency (multiset containment); that checks for subsequence ordering.
- "What is the `formed` counter tracking?" -- The number of distinct characters in `t` whose count in the window meets or exceeds the required count.

---

### Problem: Sliding Window Maximum (LC #239) — Hard

**Companies:** Google, Amazon, Meta, Microsoft, Uber
**Why it is asked:** Tests the monotonic deque technique. Naive O(nk) solutions are not acceptable; you must demonstrate knowledge of the deque optimization.

**The Brute Force:**
```python
def maxSlidingWindow_brute(nums, k):
    # O(n * k) time
    n = len(nums)
    if n == 0:
        return []
    result = []
    for i in range(n - k + 1):
        result.append(max(nums[i:i + k]))
    return result
```

For each window position, scan all k elements to find the max. O(n * k).

**The Key Insight:** Maintain a **monotonic decreasing deque** of indices. The front of the deque always holds the index of the current window's maximum. When a new element enters:
1. Remove from the back any indices whose values are less than the new element (they can never be the max while the new element is in the window).
2. Add the new index to the back.
3. Remove from the front any indices that are outside the current window.
4. The front of the deque is the current window's maximum.

This works because the deque maintains a decreasing sequence of "potential maximums." When a larger element arrives, all smaller elements in the deque become irrelevant.

**Optimal Solution:**
```python
from collections import deque

def maxSlidingWindow(nums, k):
    dq = deque()  # stores indices; values at these indices are in decreasing order
    result = []

    for i in range(len(nums)):
        # Remove indices outside the window
        while dq and dq[0] < i - k + 1:
            dq.popleft()

        # Remove indices whose values are less than nums[i]
        # (they can never be the max while nums[i] is in the window)
        while dq and nums[dq[-1]] <= nums[i]:
            dq.pop()

        dq.append(i)

        # Window is fully formed when i >= k - 1
        if i >= k - 1:
            result.append(nums[dq[0]])

    return result
```

**Dry Run:**
```
Input: nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 3

i=0 (val=1):  dq=[0]                       (window not full yet)
i=1 (val=3):  pop 0 (1<=3), dq=[1]         (window not full yet)
i=2 (val=-1): dq=[1,2]                     window [1,3,-1], max=nums[1]=3
i=3 (val=-3): dq=[1,2,3]                   window [3,-1,-3], max=nums[1]=3
i=4 (val=5):  pop 3(-3<=5), pop 2(-1<=5), pop 1(3<=5), dq=[4]
              but first check: dq[0]=1 < 4-3+1=2, so pop 1 first.
              Actually let me redo step by step:

              Remove out-of-window: dq[0]=1 < 4-2=2? 1 < 2, yes, popleft. dq=[2,3]
              dq[0]=2 < 2? No. Stop.
              Remove smaller: nums[3]=-3 <= 5? pop. dq=[2]. nums[2]=-1 <= 5? pop. dq=[].
              Append 4: dq=[4]
              window [−1,−3,5], max=nums[4]=5

i=5 (val=3):  Out-of-window: dq[0]=4 >= 5-2=3, ok.
              Smaller: nums[4]=5 > 3, stop. dq=[4,5]
              window [−3,5,3], max=nums[4]=5

i=6 (val=6):  Out-of-window: dq[0]=4 >= 6-2=4, ok.
              Smaller: nums[5]=3 <= 6, pop. nums[4]=5 <= 6, pop. dq=[6]
              window [5,3,6], max=nums[6]=6

i=7 (val=7):  Out-of-window: dq[0]=6 >= 7-2=5, ok.
              Smaller: nums[6]=6 <= 7, pop. dq=[7]
              window [3,6,7], max=nums[7]=7

Result: [3, 3, 5, 5, 6, 7]
```

**Edge Cases:**
- k == 1: every element is its own max, return the input array.
- k == n: single window, return [max(nums)].
- All elements equal: every window max is the same value.
- Strictly decreasing: deque always has all k elements, front is always the leftmost.
- Strictly increasing: deque always has just one element (the rightmost).

**Complexity:** Time O(n) -- each element is added and removed from the deque at most once. Space O(k) for the deque.

**Follow-up questions interviewers might ask:**
- "Why does the deque give O(n)?" -- Each element is pushed and popped at most once, so total operations across all iterations is O(n).
- "Can you use a heap?" -- Yes, but lazy deletion makes it O(n log n). The deque is O(n).
- "What about Sliding Window Minimum?" -- Same approach but maintain a monotonically increasing deque.
- "Can you handle Sliding Window Median?" -- Yes, but requires two heaps (max-heap for lower half, min-heap for upper half) with lazy deletion. That is a different problem (LC #480).

---

## Common Mistakes and Interview Tips

### Top 5 Mistakes

1. **Off-by-one in window size:** Window size is `right - left + 1`, not `right - left`. This consistently trips up candidates.

2. **Using `if` instead of `while` to contract:** When the window becomes invalid, you often need to keep contracting until it is valid again. Using `if` instead of `while` only removes one element and can leave the window invalid.

3. **Not updating state correctly on both expand and contract:** When expanding, you add the right element. When contracting, you must properly remove the left element. Forgetting to decrement counts or remove from sets causes bugs.

4. **Recomputing window state from scratch:** The whole point of sliding window is incremental updates. Calling `sum(nums[left:right+1])` inside the loop defeats the purpose and makes it O(n^2).

5. **Confusing "longest" vs "shortest" window logic:** For "longest," you contract only when the window becomes invalid, then update the answer when valid. For "shortest," you update the answer when the window becomes valid, then contract to try to find something shorter.

### How to Recognize This Pattern in 30 Seconds

Ask: "Am I looking for a contiguous subarray/substring, and can I update the window state incrementally by adding one element and removing one element?" If yes, it is sliding window.

### What Senior/Staff Interviewers Look For

- **Correct handling of the `formed` / `satisfied` counter** in problems like Minimum Window Substring. Many candidates get this wrong.
- **Choosing the right data structure for window state:** Hash map for character frequencies, deque for monotonic window max/min, set for uniqueness.
- **Clean separation of expand and contract phases.** The code should clearly show "expand right" and "contract left" as distinct steps.
- **Correct complexity analysis:** Explaining why the two-pointer traversal is O(n) even though there is a while loop inside a for loop (amortized argument: each element enters and leaves at most once).

### Communication Tips

1. Identify the problem type: "This is asking for the shortest/longest contiguous substring/subarray with a condition, which is a sliding window problem."
2. Define what the window tracks: "I will maintain a frequency count of characters in the window."
3. Define the validity condition: "The window is valid when all characters of t are present with sufficient frequency."
4. Explain the expand/contract strategy: "I expand by moving right, and contract from the left whenever the window is valid to find the minimum."
5. State the complexity with the amortized argument.

## Pattern Connections

- **Sliding Window** is a specialized form of **Two Pointers** where both pointers move in the same direction.
- When the window needs max/min tracking, combine with **Monotonic Deque** (Sliding Window Maximum).
- When the window needs median tracking, combine with **Two Heaps** (Sliding Window Median).
- **Prefix Sum** can sometimes replace sliding window for fixed-size window sum queries, but sliding window is more natural for the "maintain and update" pattern.
- Problems that say "subsequence" instead of "substring" are usually **DP**, not sliding window.
- **Sliding Window + Hash Map** covers most medium-difficulty string problems at top companies.
