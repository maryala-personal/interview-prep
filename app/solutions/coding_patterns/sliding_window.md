# Sliding Window Pattern - Complete Guide

## 1. What is Sliding Window?

### Explain Like I'm 5
Imagine you have a long line of colored blocks on the floor, and you have a cardboard frame that can only show 3 blocks at a time. Instead of picking up the frame and moving it to a completely new spot each time, you just slide it one block to the right. You look at what's inside the frame, slide it one more block, look again, and keep going until you reach the end. That's sliding window!

### Technical Definition
The Sliding Window pattern is an algorithmic technique that processes sequential data (arrays, strings) by maintaining a "window" - a contiguous subset of elements. Instead of recalculating everything from scratch for each subset, we slide the window by adding new elements on one end and removing old elements from the other end, reusing previous calculations for efficiency.

## 2. Real-World Analogy

Think of sitting in a train looking out the window. As the train moves:
- You can only see a portion of the landscape at any moment (the window)
- The view changes continuously but smoothly (sliding)
- The left side of what you saw disappears, new scenery appears on the right
- You don't need to look at the entire landscape at once
- You process information incrementally as you move

This is exactly how sliding window works with data!

## 3. When to Use - Clear Signals

Use sliding window when you see these signals:

### Strong Indicators 🚨
- **Contiguous subarrays/substrings** - Problem mentions "consecutive", "contiguous", or "substring"
- **"In every window of size K"** - Any problem with fixed window size
- **Maximum/minimum in subarrays** - Finding optimal values in consecutive elements
- **Running calculations** - Computing sums, averages, products over sequences
- **Constraint satisfaction** - "At most K distinct characters", "contains all characters"

### Keyword Triggers
- "Longest substring..."
- "Maximum sum of subarray of size..."
- "Minimum window..."
- "Find all anagrams..."
- "Contains duplicate within range K..."
- "Average of all subarrays..."

### Problem Characteristics
- Input is iterable (array, string, linked list)
- Need to find something about **all** contiguous subarrays
- Brute force would involve nested loops checking every subarray
- Current window state can be derived from previous window state

## 4. The Problem - Classic Example

**Longest Substring Without Repeating Characters**

Given a string `s`, find the length of the longest substring without repeating characters.

```
Example 1:
Input: s = "abcabcbb"
Output: 3
Explanation: The answer is "abc", with length 3.

Example 2:
Input: s = "bbbbb"
Output: 1
Explanation: The answer is "b", with length 1.

Example 3:
Input: s = "pwwkew"
Output: 3
Explanation: The answer is "wke", with length 3.
Notice that "pwke" is a subsequence, not a substring.

Example 4:
Input: s = ""
Output: 0
```

## 5. Brute Force Approach

### The Naive Solution
Check every possible substring and verify if it has unique characters.

```python
def lengthOfLongestSubstring_bruteforce(s: str) -> int:
    """
    Brute force: Check every possible substring

    Approach:
    1. Generate all possible substrings (start from each position)
    2. For each substring, check if all characters are unique
    3. Track the maximum length found
    """
    max_length = 0
    n = len(s)

    # Try every possible starting position
    for start in range(n):
        # Try every possible ending position from this start
        for end in range(start, n):
            # Extract the substring from start to end (inclusive)
            substring = s[start:end + 1]

            # Check if this substring has all unique characters
            if has_unique_characters(substring):
                max_length = max(max_length, len(substring))
            else:
                # No point extending further from this start
                # because adding more chars won't make it unique
                break

    return max_length

def has_unique_characters(s: str) -> bool:
    """Check if all characters in string are unique"""
    # Convert to set - if lengths match, all chars are unique
    return len(s) == len(set(s))

# Example usage
print(lengthOfLongestSubstring_bruteforce("abcabcbb"))  # Output: 3
print(lengthOfLongestSubstring_bruteforce("bbbbb"))      # Output: 1
print(lengthOfLongestSubstring_bruteforce("pwwkew"))     # Output: 3
```

### Why This is Inefficient
- We check the **same characters multiple times**
- For "abcabcbb", we check:
  - "a", "ab", "abc", "abca" (duplicate found)
  - "b", "bc", "bca", "bcab" (duplicate found)
  - "c", "ca", "cab", "cabc" (duplicate found)
  - And so on...
- We're doing redundant work - if "abc" has no duplicates, we already know "ab" and "bc" don't either!

## 6. Optimized Solution - Sliding Window

### The Smart Solution
Use a window that expands and contracts dynamically based on character uniqueness.

```python
def lengthOfLongestSubstring(s: str) -> int:
    """
    Sliding Window Approach - Variable Size Window

    Key Insight:
    - Maintain a window [left, right] with unique characters
    - Expand by moving 'right' pointer
    - Contract by moving 'left' pointer when duplicate found
    - Track maximum window size seen

    Time: O(n) - each character visited at most twice
    Space: O(min(n, m)) where m is charset size
    """
    # Dictionary to store most recent index of each character
    # Key: character, Value: index where it last appeared
    char_index_map = {}

    max_length = 0
    left = 0  # Left boundary of our window

    # Right pointer expands the window
    for right in range(len(s)):
        current_char = s[right]

        # If we've seen this character before AND it's in our current window
        if current_char in char_index_map and char_index_map[current_char] >= left:
            # Move left pointer to right after the previous occurrence
            # This effectively "slides" our window past the duplicate
            left = char_index_map[current_char] + 1

        # Update the most recent index of current character
        char_index_map[current_char] = right

        # Calculate current window size and update maximum
        current_length = right - left + 1
        max_length = max(max_length, current_length)

    return max_length

# Example walkthrough for "abcabcbb":
#
# Step-by-step visualization:
#
# right=0, char='a', left=0, window="a", length=1, max=1
# char_index_map = {'a': 0}
#
# right=1, char='b', left=0, window="ab", length=2, max=2
# char_index_map = {'a': 0, 'b': 1}
#
# right=2, char='c', left=0, window="abc", length=3, max=3
# char_index_map = {'a': 0, 'b': 1, 'c': 2}
#
# right=3, char='a', left=0, DUPLICATE! 'a' was at index 0
#   left moves to 0+1=1, window="bca", length=3, max=3
# char_index_map = {'a': 3, 'b': 1, 'c': 2}
#
# right=4, char='b', left=1, DUPLICATE! 'b' was at index 1
#   left moves to 1+1=2, window="cab", length=3, max=3
# char_index_map = {'a': 3, 'b': 4, 'c': 2}
#
# right=5, char='c', left=2, DUPLICATE! 'c' was at index 2
#   left moves to 2+1=3, window="abc", length=3, max=3
# char_index_map = {'a': 3, 'b': 4, 'c': 5}
#
# right=6, char='b', left=3, DUPLICATE! 'b' was at index 4
#   left moves to 4+1=5, window="cb", length=2, max=3
# char_index_map = {'a': 3, 'b': 6, 'c': 5}
#
# right=7, char='b', left=5, DUPLICATE! 'b' was at index 6
#   left moves to 6+1=7, window="b", length=1, max=3
# char_index_map = {'a': 3, 'b': 7, 'c': 5}
#
# Final answer: 3

print(lengthOfLongestSubstring("abcabcbb"))  # Output: 3
print(lengthOfLongestSubstring("bbbbb"))      # Output: 1
print(lengthOfLongestSubstring("pwwkew"))     # Output: 3
```

### Alternative Implementation Using Set

```python
def lengthOfLongestSubstring_set(s: str) -> int:
    """
    Alternative sliding window using a set
    More intuitive but slightly different approach
    """
    char_set = set()  # Characters currently in our window
    max_length = 0
    left = 0

    for right in range(len(s)):
        # Shrink window from left while we have duplicates
        while s[right] in char_set:
            char_set.remove(s[left])
            left += 1

        # Add current character to window
        char_set.add(s[right])

        # Update maximum length
        max_length = max(max_length, right - left + 1)

    return max_length
```

## 7. Time & Space Complexity Analysis

### Brute Force Approach
- **Time Complexity: O(n³)**
  - Outer loop: O(n) - all starting positions
  - Inner loop: O(n) - all ending positions
  - Checking uniqueness: O(n) - converting to set
  - Total: O(n) × O(n) × O(n) = O(n³)

- **Space Complexity: O(min(n, m))**
  - Where m is the character set size (256 for ASCII, 26 for lowercase letters)
  - Set for checking uniqueness can have at most min(n, m) characters

### Sliding Window Approach
- **Time Complexity: O(n)**
  - Each character is visited at most twice (once by right, once by left)
  - In the worst case, left pointer goes from 0 to n-1
  - Right pointer goes from 0 to n-1
  - Total operations: 2n = O(n)

- **Space Complexity: O(min(n, m))**
  - HashMap/Set stores at most min(n, m) characters
  - Where m is the size of the character set

### Performance Comparison

| Input Size | Brute Force | Sliding Window |
|------------|-------------|----------------|
| n = 10     | ~1,000 ops  | ~20 ops        |
| n = 100    | ~1,000,000  | ~200 ops       |
| n = 1,000  | ~1 billion  | ~2,000 ops     |

**Speedup: ~500,000x for n=1,000!**

## 8. Variations - Fixed vs Variable Window

### Fixed-Size Window
Window size is predetermined and constant.

**Example: Maximum Sum of Subarray of Size K**

```python
def max_sum_subarray_size_k(arr: list[int], k: int) -> int:
    """
    Find maximum sum of any contiguous subarray of size k

    Example: arr = [2, 1, 5, 1, 3, 2], k = 3
    Output: 9 (subarray [5, 1, 3])
    """
    if len(arr) < k:
        return -1

    # Calculate sum of first window
    window_sum = sum(arr[:k])
    max_sum = window_sum

    # Slide the window: remove leftmost, add rightmost
    for i in range(k, len(arr)):
        # Slide: remove arr[i-k], add arr[i]
        window_sum = window_sum - arr[i - k] + arr[i]
        max_sum = max(max_sum, window_sum)

    return max_sum

# Example
print(max_sum_subarray_size_k([2, 1, 5, 1, 3, 2], 3))  # Output: 9
```

**Characteristics:**
- Window size never changes
- Simple: just slide by 1 each time
- Add one element, remove one element
- Common in problems with "size K" or "every K elements"

### Variable-Size Window
Window size changes based on conditions.

**Example: Smallest Subarray with Sum ≥ Target**

```python
def min_subarray_sum(arr: list[int], target: int) -> int:
    """
    Find length of smallest contiguous subarray with sum ≥ target

    Example: arr = [2, 3, 1, 2, 4, 3], target = 7
    Output: 2 (subarray [4, 3])
    """
    min_length = float('inf')
    window_sum = 0
    left = 0

    for right in range(len(arr)):
        # Expand window
        window_sum += arr[right]

        # Contract window while condition is met
        while window_sum >= target:
            min_length = min(min_length, right - left + 1)
            window_sum -= arr[left]
            left += 1

    return min_length if min_length != float('inf') else 0

# Example
print(min_subarray_sum([2, 3, 1, 2, 4, 3], 7))  # Output: 2
```

**Characteristics:**
- Window expands and contracts dynamically
- Two pointers move independently based on conditions
- More complex logic
- Common in "minimum/maximum length" problems

## 9. Pro Tips for Senior Engineers

### Edge Cases to Handle
```python
# 1. Empty input
s = ""  # Should return 0, not crash

# 2. Single character
s = "a"  # Should return 1

# 3. All unique characters
s = "abcdefg"  # Should return len(s)

# 4. All same characters
s = "aaaaaaa"  # Should return 1

# 5. Very large inputs
s = "a" * 1000000  # Should not timeout

# 6. Special characters
s = "!@#$%^&*()"  # Should handle non-alphanumeric

# 7. Unicode characters
s = "你好世界"  # Should handle multi-byte characters
```

### When NOT to Use Sliding Window

❌ **Don't use when:**
1. **Non-contiguous elements** - Need to skip elements or use non-adjacent items
   - Example: "Find maximum sum of K non-adjacent elements" → Use DP instead

2. **Need to revisit elements** - Algorithm requires backtracking
   - Example: "Find all permutations" → Use backtracking instead

3. **Global optimization** - Need to compare all possible combinations
   - Example: "Find maximum product of any 3 elements" → Just sort and check ends

4. **2D problems** - Unless specifically adapting for matrices
   - Example: "Find largest rectangle in matrix" → Needs modified approach

5. **Order doesn't matter** - Elements can be rearranged
   - Example: "Check if anagram exists" → Use frequency counting instead

### Interview Gotchas

1. **Clarify "substring" vs "subsequence"**
   - Substring: continuous → use sliding window
   - Subsequence: can skip elements → use DP

2. **Ask about character set**
   - ASCII (256 chars) vs Unicode vs lowercase only (26 chars)
   - Affects space complexity

3. **Confirm "at most" vs "exactly"**
   - "At most K distinct" vs "Exactly K distinct" → different window shrinking logic

4. **Handle integer overflow** (for sum problems)
   ```python
   # Use long or check for overflow in languages like Java/C++
   # Python handles big integers automatically
   ```

5. **Off-by-one errors**
   ```python
   # Window size = right - left + 1  (inclusive)
   # NOT right - left (exclusive)
   ```

### Performance Optimizations

```python
# 1. Early termination
def optimized_search(s: str, k: int) -> int:
    if len(s) < k:
        return -1  # Impossible, return early

    # If already found best possible, return
    if result == theoretical_max:
        return result

# 2. Use array instead of dict for limited charset
def using_array(s: str) -> int:
    # For lowercase letters only
    char_count = [0] * 26
    # Access: char_count[ord(c) - ord('a')]
    # Faster than dictionary for small fixed sets

# 3. Avoid repeated calculations
# Bad: recalculating every time
window_sum = sum(arr[left:right+1])  # O(window_size)

# Good: maintain running sum
window_sum = window_sum - arr[left] + arr[right]  # O(1)
```

## 10. Problem Recognition - Spotting the Pattern

### Decision Tree

```
Is the data sequential (array/string)?
    ├─ NO → Not sliding window
    └─ YES
        │
        Does it mention "contiguous" or "substring"?
        ├─ NO → Check other signals
        └─ YES
            │
            Is there a fixed window size K?
            ├─ YES → FIXED-SIZE SLIDING WINDOW
            └─ NO
                │
                Looking for min/max length with condition?
                ├─ YES → VARIABLE-SIZE SLIDING WINDOW
                └─ NO → Check for other patterns
```

### Pattern Recognition Examples

**Example 1:** "Find the maximum sum of any contiguous subarray of size K"
- ✅ Sequential data (array)
- ✅ Contiguous subarray
- ✅ Fixed size K
- **Pattern: Fixed-Size Sliding Window**

**Example 2:** "Longest substring with at most K distinct characters"
- ✅ Sequential data (string)
- ✅ Substring (contiguous)
- ✅ Finding length (min/max)
- ✅ Condition (at most K distinct)
- **Pattern: Variable-Size Sliding Window**

**Example 3:** "Find two numbers that sum to target"
- ✅ Sequential data
- ❌ Not about contiguous elements
- **Pattern: Two Pointers or Hash Map, NOT sliding window**

### Red Flags (Not Sliding Window)

- "Find pair/triplet that sums to..." → Two Pointers
- "Maximum product of K elements (any K)" → Sorting + Greedy
- "All possible combinations" → Backtracking
- "Can rearrange elements" → Sorting or Hash Map
- "Non-contiguous" or "subsequence" → DP

## 11. Practice Problems

### Easy
1. **Maximum Average Subarray I** (LeetCode 643)
   - Fixed-size window
   - Find average of subarray of size K

2. **Contains Duplicate II** (LeetCode 219)
   - Fixed-size window with condition
   - Check if duplicate exists within window of size K

3. **Defanging an IP Address** (LeetCode 1108)
   - Simple string window manipulation

### Medium
4. **Longest Substring Without Repeating Characters** (LeetCode 3)
   - Variable-size window
   - Classic problem covered in this guide

5. **Longest Substring with At Most K Distinct Characters** (LeetCode 340)
   - Variable-size window
   - Track distinct characters with hash map

6. **Fruit Into Baskets** (LeetCode 904)
   - Variable-size window disguised as real-world problem
   - Same as "at most 2 distinct characters"

7. **Minimum Window Substring** (LeetCode 76)
   - Variable-size window with complex condition
   - Find smallest window containing all characters of target

### Hard
8. **Sliding Window Maximum** (LeetCode 239)
   - Fixed-size window with deque optimization
   - Find maximum in each window efficiently

9. **Substring with Concatenation of All Words** (LeetCode 30)
   - Fixed-size window with word-level sliding
   - Combines sliding window with hash map matching

10. **Longest Substring with At Most Two Distinct Characters** (LeetCode 159)
    - Variable-size window
    - Good stepping stone to K distinct version

## 12. Common Mistakes

### Mistake 1: Not Updating Window State Correctly
```python
# WRONG: Forgetting to remove left element
for right in range(len(arr)):
    window_sum += arr[right]
    # Forgot to subtract arr[left] when sliding!

# CORRECT:
window_sum = window_sum - arr[left] + arr[right]
```

### Mistake 2: Off-By-One Errors
```python
# WRONG: Window size calculation
window_size = right - left  # Incorrect for inclusive range

# CORRECT:
window_size = right - left + 1  # When both pointers are inclusive
```

### Mistake 3: Not Handling Edge Cases
```python
# WRONG: Assuming input is always valid
def max_sum(arr, k):
    window_sum = sum(arr[:k])  # Crashes if len(arr) < k!

# CORRECT:
def max_sum(arr, k):
    if not arr or len(arr) < k:
        return 0  # or raise exception
    window_sum = sum(arr[:k])
```

### Mistake 4: Incorrect Window Shrinking Logic
```python
# WRONG: Using if instead of while
if condition_violated:
    left += 1  # Might not be enough!

# CORRECT: Keep shrinking until valid
while condition_violated:
    left += 1
```

### Mistake 5: Mutating Input
```python
# WRONG: Modifying original data
for right in range(len(arr)):
    arr[right] = 0  # Don't modify unless explicitly asked!

# CORRECT: Use separate variables
for right in range(len(arr)):
    current_val = arr[right]
    # Work with current_val
```

### Mistake 6: Not Considering Character Set Size
```python
# WRONG: Using dict for simple ASCII
char_map = {}  # Overkill for known small set

# BETTER: For lowercase letters only
char_count = [0] * 26  # Faster access, less memory
```

### Mistake 7: Nested Loops (Defeating the Purpose)
```python
# WRONG: Checking entire window every iteration
for right in range(len(arr)):
    for i in range(left, right + 1):  # O(n²) - not sliding window!
        # process arr[i]

# CORRECT: Maintain state incrementally
for right in range(len(arr)):
    # Update state in O(1)
    state = update_state(state, arr[right])
```

### Mistake 8: Confusing Index Tracking
```python
# WRONG: Mixing up what pointers mean
if char_map[c] >= left:  # Is this index or count? Be clear!

# CORRECT: Use clear variable names
if last_seen_index[c] >= window_start:
    window_start = last_seen_index[c] + 1
```

---

## Summary

The Sliding Window pattern is your go-to solution for:
- ✅ Contiguous subarray/substring problems
- ✅ Optimizing nested loops from O(n²) or O(n³) to O(n)
- ✅ Problems with "every K elements" or "longest/shortest substring"

**Key Takeaway:** Instead of recalculating everything, maintain state and update incrementally!

**Master this pattern and you'll solve dozens of interview problems with confidence!**
