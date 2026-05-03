# String / Array Manipulation — Complete Interview Guide

## When to Use This Pattern

### Signals That Point to String/Array Techniques
1. **Character frequency or anagram problems** — grouping, comparing, or matching based on character counts.
2. **Palindrome detection or construction** — checking or building symmetric strings.
3. **Parsing expressions or structured text** — calculators, interpreters, encoding/decoding.
4. **Prefix/suffix computations** — product of array except self, prefix sums, rolling hashes.
5. **Pattern matching in strings** — finding substrings, windows, or repeated patterns.
6. **In-place array transformation** — rotating, partitioning, or rearranging without extra space.

### When NOT to Use
- If the problem involves shortest paths or graph connectivity — use graph algorithms.
- If the problem has optimal substructure with overlapping subproblems — consider DP.
- If the data is a tree or linked list — use those specific techniques.

---

### ⚡ Pattern Overlap & Decision Guide

#### String/Array vs Commonly Confused Patterns

| Signal | String/Array (this pattern) | Hash Map | Two Pointers | Sliding Window | Stack | Sorting |
|--------|---------------------------|----------|-------------- |----------------|-------|---------|
| "Group by equivalence" (anagrams) | **Frequency key** | HashMap to group | N/A | N/A | N/A | Sorted key alternative |
| "Find palindrome" | **Expand around center** | N/A | **Two-pointer from ends** | N/A | N/A | N/A |
| "Minimum window containing X" | N/A | Track char counts | N/A | **Sliding window** | N/A | N/A |
| "Evaluate expression" | **Calculator parsing** | N/A | N/A | N/A | **Operator stack** | N/A |
| "Product except self" | **Prefix/suffix two-pass** | N/A | N/A | N/A | N/A | N/A |
| "Format text to width" | **Greedy packing** | N/A | N/A | N/A | N/A | N/A |
| "Encode/decode strings" | **Length-prefix protocol** | N/A | N/A | N/A | N/A | N/A |

#### Quick Signals That Point to String/Array Specifically
- "Group anagrams" or "check if two strings are anagrams" -- frequency hashing
- "Longest palindromic substring" -- expand around center
- "Evaluate expression with +, -, *, /" -- stack-based calculator
- "Product of array except self" -- prefix/suffix decomposition
- "Encode a list of strings into one string" -- length-prefix encoding
- "Justify text to a fixed width" -- greedy packing + space distribution

#### Common Mistakes: "You might think it is X, but it is actually Y"

1. **"Find all anagrams in a string" -- String/Array vs Sliding Window**: **LC 438 Find All Anagrams in a String** looks like an anagram grouping problem (String/Array), but the optimal solution is a **Sliding Window** with a frequency counter. The key difference: LC 49 Group Anagrams is about grouping separate strings (hash map), while LC 438 is about finding substrings of fixed length in a single string (sliding window).

2. **"Longest substring without repeating characters" -- String vs Sliding Window**: **LC 3 Longest Substring Without Repeating Characters** is NOT a string manipulation problem -- it is a **Sliding Window** problem. The string is just the input format. The core technique is expand-right/shrink-left with a set tracking characters in the window.

3. **"Trapping Rain Water" -- Prefix/Suffix vs Two Pointers vs Stack**: **LC 42 Trapping Rain Water** can be solved with prefix/suffix arrays (String/Array pattern: compute left_max and right_max arrays), two pointers (O(1) space), or a monotonic stack. All three are valid. The prefix/suffix approach is the easiest to understand; the two-pointer approach is the most space-efficient.

#### Problems That LOOK Like String/Array But Are Not
- **LC 76 Minimum Window Substring** is listed in this guide but is fundamentally a **Sliding Window** problem. It uses character frequency tracking (String/Array technique) within a sliding window framework.
- **LC 5 Longest Palindromic Substring** uses expand-around-center (String/Array), but **LC 516 Longest Palindromic Subsequence** is a **Dynamic Programming** problem (2D DP on the string). "Substring" vs "subsequence" completely changes the pattern.
- **LC 56 Merge Intervals** involves arrays but is solved by **Sorting + Greedy merge**, not by any string/array-specific technique. The sorting step is the key insight.

---

## Core Mechanics

### Hashing Patterns for String Matching
Many string problems reduce to "are these two things equivalent?" — and hashing gives O(1) comparison.

**Character Frequency Hashing**: Two strings are anagrams iff they have the same character frequency map. Use `Counter` or a fixed-size array of 26 for lowercase English letters.
```python
from collections import Counter
Counter("anagram") == Counter("nagaram")  # True
```

**Sorted Key**: Another way to canonicalize strings for anagram grouping — sort the characters. `"eat"` and `"tea"` both become `"aet"`.

**Rolling Hash (Rabin-Karp)**: For substring matching, compute a hash that can be updated in O(1) as the window slides. Useful for multi-pattern matching.

### Two-Pass Techniques (Prefix + Suffix)
Compute a prefix array left-to-right, then a suffix array right-to-left, then combine them. This avoids using division (which is fragile with zeros) and handles edge cases cleanly.

**Example**: Product of Array Except Self.
```
nums =    [1, 2, 3, 4]
prefix =  [1, 1, 2, 6]   (product of everything to the left)
suffix =  [24, 12, 4, 1]  (product of everything to the right)
result =  [24, 12, 8, 6]  (prefix[i] * suffix[i])
```

### Parser / Calculator Pattern
Expression evaluation problems follow a consistent architecture:
1. **Tokenize**: Break the string into numbers and operators.
2. **Operator precedence**: Use a stack. Higher-precedence operators are evaluated immediately; lower-precedence ones wait on the stack.
3. **Parentheses**: Either use recursion (treat inner expression as a subproblem) or a stack of states.

The key insight: maintain a running `num`, a `sign`, and a `stack`. When you see `+` or `-`, push the current term. When you see `*` or `/`, immediately combine with the top of the stack (higher precedence).

### Complexity Notes
| Operation | Typical Complexity |
|-----------|-------------------|
| Sorting a string of length L | O(L log L) |
| Character frequency count | O(L) |
| Substring check | O(L) naive, O(L) KMP/Rabin-Karp |
| Prefix/suffix array build | O(n) |
| Stack-based parsing | O(n) |

---

## The Templates

### Python — Anagram Grouping Template
```python
from collections import defaultdict

def group_anagrams(strs: list) -> list:
    groups = defaultdict(list)
    for s in strs:
        key = tuple(sorted(s))  # or use character count tuple
        groups[key].append(s)
    return list(groups.values())
```

### Python — Prefix/Suffix Template
```python
def prefix_suffix_product(nums: list) -> list:
    n = len(nums)
    result = [1] * n
    # Left pass: result[i] = product of nums[0..i-1]
    prefix = 1
    for i in range(n):
        result[i] = prefix
        prefix *= nums[i]
    # Right pass: multiply by product of nums[i+1..n-1]
    suffix = 1
    for i in range(n - 1, -1, -1):
        result[i] *= suffix
        suffix *= nums[i]
    return result
```

### Python — Calculator Template (handles +, -, *, /)
```python
def calculate(s: str) -> int:
    stack = []
    num = 0
    sign = '+'
    s = s.strip()
    for i, ch in enumerate(s):
        if ch.isdigit():
            num = num * 10 + int(ch)
        if ch in '+-*/' or i == len(s) - 1:
            if sign == '+':
                stack.append(num)
            elif sign == '-':
                stack.append(-num)
            elif sign == '*':
                stack.append(stack.pop() * num)
            elif sign == '/':
                stack.append(int(stack.pop() / num))  # truncate toward zero
            sign = ch
            num = 0
    return sum(stack)
```

### Python — Palindrome Expansion Template
```python
def expand_around_center(s: str, left: int, right: int) -> str:
    while left >= 0 and right < len(s) and s[left] == s[right]:
        left -= 1
        right += 1
    return s[left + 1:right]
```

### Go — Core Templates
```go
import "sort"

// Group anagrams using sorted key
func groupAnagrams(strs []string) [][]string {
    groups := map[string][]string{}
    for _, s := range strs {
        key := sortString(s)
        groups[key] = append(groups[key], s)
    }
    result := make([][]string, 0, len(groups))
    for _, v := range groups {
        result = append(result, v)
    }
    return result
}

func sortString(s string) string {
    r := []byte(s)
    sort.Slice(r, func(i, j int) bool { return r[i] < r[j] })
    return string(r)
}

// Prefix-suffix product
func productExceptSelf(nums []int) []int {
    n := len(nums)
    result := make([]int, n)
    prefix := 1
    for i := 0; i < n; i++ {
        result[i] = prefix
        prefix *= nums[i]
    }
    suffix := 1
    for i := n - 1; i >= 0; i-- {
        result[i] *= suffix
        suffix *= nums[i]
    }
    return result
}
```

---

## Variant Subpatterns

### 1. Palindrome Patterns
- **Check palindrome**: Two pointers from both ends.
- **Longest palindromic substring**: Expand around each center (O(n^2)) or Manacher's algorithm (O(n)).
- **Palindrome partitioning**: Backtracking with palindrome precomputation.

### 2. Anagram / Frequency Patterns
- **Check anagram**: Compare character counts.
- **Group anagrams**: Use sorted string or frequency tuple as key.
- **Find anagram substrings**: Sliding window with frequency map.

### 3. Two-Pass Prefix/Suffix
- **Product except self**: Prefix products * suffix products.
- **Trapping rain water**: min(left_max, right_max) - height.
- **Candy distribution**: Left-to-right pass for increasing, right-to-left for decreasing.

### 4. Stack-Based Parsing
- **Basic Calculator**: Handle +, -, and parentheses.
- **Basic Calculator II**: Handle +, -, *, / (no parentheses).
- **Basic Calculator III**: Handle all operators and parentheses.
- **Decode String**: Nested bracket decoding like "3[a2[c]]".

### 5. Encoding / Decoding
- **Encode/Decode Strings**: Length-prefixed encoding for arbitrary strings.
- **Run-Length Encoding**: Compress consecutive characters.
- **Serialize complex structures**: JSON-like encoding.

---

## Problem Walkthroughs

---

### Problem: Valid Palindrome (LC #125) — Easy
**Companies**: Meta, Amazon, Microsoft, Google.

**Problem**: Given a string, determine if it is a palindrome considering only alphanumeric characters and ignoring cases.

**Brute Force**: Filter non-alphanumeric, convert to lowercase, compare with reverse.
```python
def is_palindrome_brute(s: str) -> bool:
    filtered = ''.join(ch.lower() for ch in s if ch.isalnum())
    return filtered == filtered[::-1]
```
Time: O(n), Space: O(n) for the filtered string.

**Key Insight**: Use two pointers from both ends. Skip non-alphanumeric characters. Compare characters case-insensitively.

**Optimal Solution**:
```python
def is_palindrome(s: str) -> bool:
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True
```
Time: O(n), Space: O(1).

**Dry Run** with `"A man, a plan, a canal: Panama"`:
```
left=0 ('A'), right=29 ('a'): 'a' == 'a' ✓
left=1 (' '), skip -> left=2 ('m'); right=28 ('m'): 'm' == 'm' ✓
left=3 ('a'), right=27 ('a'): 'a' == 'a' ✓
... (continues matching)
All match -> True
```

**Edge Cases**: Empty string (true), single character (true), all non-alphanumeric (true), "0P" (false — '0' != 'p').

**Follow-up Questions**:
- What if you can delete at most one character? (LC 680 — try both options when mismatch found.)
- What about checking if any permutation is a palindrome? (At most one character with odd count.)

---

### Problem: Group Anagrams (LC #49) — Medium
**Companies**: Meta, Amazon, Google, Microsoft, Bloomberg.

**Problem**: Given an array of strings, group the anagrams together.

**Brute Force**: Compare every pair of strings to check if they are anagrams. O(n^2 * L).

**Key Insight**: Two strings are anagrams iff they have the same sorted form OR the same character frequency tuple. Use this as a hashmap key.

**Optimal Solution — Sorted Key**:
```python
from collections import defaultdict

def group_anagrams(strs: list) -> list:
    groups = defaultdict(list)
    for s in strs:
        key = tuple(sorted(s))
        groups[key].append(s)
    return list(groups.values())
```
Time: O(n * L log L) where L = max string length. Space: O(n * L).

**Optimal Solution — Frequency Key** (avoids sorting):
```python
from collections import defaultdict

def group_anagrams_freq(strs: list) -> list:
    groups = defaultdict(list)
    for s in strs:
        count = [0] * 26
        for ch in s:
            count[ord(ch) - ord('a')] += 1
        key = tuple(count)
        groups[key].append(s)
    return list(groups.values())
```
Time: O(n * L) — no sorting needed. Space: O(n * L).

**Dry Run** with `["eat", "tea", "tan", "ate", "nat", "bat"]`:
```
Sorted key approach:
  "eat" -> ('a','e','t') -> group 1
  "tea" -> ('a','e','t') -> group 1
  "tan" -> ('a','n','t') -> group 2
  "ate" -> ('a','e','t') -> group 1
  "nat" -> ('a','n','t') -> group 2
  "bat" -> ('a','b','t') -> group 3

Result: [["eat","tea","ate"], ["tan","nat"], ["bat"]]
```

**Edge Cases**: Empty strings (all group together), single character strings, all strings are anagrams, no anagrams.

**Follow-up Questions**:
- What if the strings can contain Unicode? (Use Counter/dict instead of 26-element array.)
- What is the most efficient key? (Frequency tuple is O(L) vs O(L log L) for sorted.)
- What if we want to find anagram substrings? (Sliding window — LC 438.)

---

### Problem: Longest Palindromic Substring (LC #5) — Medium
**Companies**: Meta, Amazon, Microsoft, Google.

**Problem**: Given a string, find the longest substring that is a palindrome.

**Brute Force**: Check every substring.
```python
def longest_palindrome_brute(s: str) -> str:
    def is_palindrome(sub):
        return sub == sub[::-1]

    best = ""
    for i in range(len(s)):
        for j in range(i, len(s)):
            if is_palindrome(s[i:j+1]) and j - i + 1 > len(best):
                best = s[i:j+1]
    return best
```
Time: O(n^3), Space: O(n).

**Key Insight — Expand Around Center**: Every palindrome has a center. For odd-length palindromes, the center is a single character. For even-length, the center is between two characters. Expand from each possible center outward while characters match. There are 2n-1 possible centers.

**Optimal Solution**:
```python
def longest_palindrome(s: str) -> str:
    if not s:
        return ""
    start, max_len = 0, 1

    def expand(left, right):
        nonlocal start, max_len
        while left >= 0 and right < len(s) and s[left] == s[right]:
            if right - left + 1 > max_len:
                start = left
                max_len = right - left + 1
            left -= 1
            right += 1

    for i in range(len(s)):
        expand(i, i)      # odd-length palindromes
        expand(i, i + 1)  # even-length palindromes

    return s[start:start + max_len]
```
Time: O(n^2), Space: O(1).

**DP Solution** (useful for understanding but expand-around-center is preferred):
```python
def longest_palindrome_dp(s: str) -> str:
    n = len(s)
    if n < 2:
        return s
    dp = [[False] * n for _ in range(n)]
    start, max_len = 0, 1

    # All single chars are palindromes
    for i in range(n):
        dp[i][i] = True

    # Check length 2
    for i in range(n - 1):
        if s[i] == s[i + 1]:
            dp[i][i + 1] = True
            start, max_len = i, 2

    # Check length 3+
    for length in range(3, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j] and dp[i + 1][j - 1]:
                dp[i][j] = True
                if length > max_len:
                    start, max_len = i, length

    return s[start:start + max_len]
```
Time: O(n^2), Space: O(n^2).

**Dry Run (Expand)** with `"babad"`:
```
i=0 ('b'):
  Odd expand(0,0): "b" (len 1)
  Even expand(0,1): 'b' != 'a', stop

i=1 ('a'):
  Odd expand(1,1): "a" -> expand(0,2) 'b'=='b' -> "bab" (len 3, start=0)
  Even expand(1,2): 'a' != 'b', stop

i=2 ('b'):
  Odd expand(2,2): "b" -> expand(1,3) 'a'=='a' -> "aba" (len 3, no update)
  Even expand(2,3): 'b' != 'a', stop

i=3 ('a'):
  Odd expand(3,3): "a" (len 1)
  Even expand(3,4): 'a' != 'd', stop

i=4 ('d'):
  Odd expand(4,4): "d" (len 1)

Result: "bab" (or "aba" — both valid)
```

**Edge Cases**: Single character, all same characters, no palindrome longer than 1.

**Follow-up Questions**:
- Can you do it in O(n)? (Manacher's algorithm.)
- What about longest palindromic subsequence? (DP on the string and its reverse.)
- Count the total number of palindromic substrings? (LC 647 — same expand technique, count instead of track longest.)

---

### Problem: Encode and Decode Strings (LC #271) — Medium
**Companies**: Meta, Google, Amazon.

**Problem**: Design an algorithm to encode a list of strings to a single string, and decode it back. The strings can contain any character.

**Key Insight**: Use length-prefixed encoding. For each string, prepend its length followed by a delimiter. This handles all edge cases including empty strings and strings containing the delimiter.

**Optimal Solution**:
```python
class Codec:
    def encode(self, strs: list) -> str:
        """Encodes a list of strings to a single string.
        Format: length#string for each string.
        Example: ["hello","world"] -> "5#hello5#world"
        """
        result = []
        for s in strs:
            result.append(f"{len(s)}#{s}")
        return "".join(result)

    def decode(self, s: str) -> list:
        """Decodes a single string to a list of strings."""
        result = []
        i = 0
        while i < len(s):
            # Find the '#' delimiter
            j = i
            while s[j] != '#':
                j += 1
            length = int(s[i:j])
            result.append(s[j + 1:j + 1 + length])
            i = j + 1 + length
        return result
```
Time: O(total characters), Space: O(total characters).

**Why length-prefix is robust**: The string `"5#hello"` tells us to read exactly 5 characters after the `#`. Even if one of those characters is `#` or a digit, we know exactly when the string ends. No escaping needed.

**Dry Run** with `["hello", "wor#ld", ""]`:
```
Encode:
  "hello" -> "5#hello"
  "wor#ld" -> "6#wor#ld"
  "" -> "0#"
  Encoded: "5#hello6#wor#ld0#"

Decode "5#hello6#wor#ld0#":
  i=0: find # at j=1, length=5, read "hello", i=7
  i=7: find # at j=8, length=6, read "wor#ld", i=15
  i=15: find # at j=16, length=0, read "", i=17
  Result: ["hello", "wor#ld", ""]
```

**Edge Cases**: Empty list, list with empty strings, strings containing `#`, strings containing numbers.

**Follow-up Questions**:
- What if you cannot use `#` as delimiter? (Use any character, but the key is length-prefix, not the delimiter.)
- What if we need to handle Unicode? (Length is in bytes or characters — be explicit.)
- How would you handle this in a binary protocol? (4-byte length prefix for each string, then raw bytes.)

---

### Problem: Product of Array Except Self (LC #238) — Medium
**Companies**: Meta, Amazon, Google, Microsoft, Apple.

**Problem**: Given an integer array, return an array where `output[i]` equals the product of all elements except `nums[i]`. You must solve it without division and in O(n) time.

**Brute Force**: For each element, multiply all others.
```python
def product_except_self_brute(nums: list) -> list:
    n = len(nums)
    result = []
    for i in range(n):
        product = 1
        for j in range(n):
            if i != j:
                product *= nums[j]
        result.append(product)
    return result
```
Time: O(n^2), Space: O(n).

**With division** (not allowed by constraints, but good to mention):
```python
def product_except_self_division(nums: list) -> list:
    total = 1
    zeros = nums.count(0)
    if zeros > 1:
        return [0] * len(nums)
    for n in nums:
        if n != 0:
            total *= n
    return [0 if (n != 0 and zeros) or (n == 0 and zeros > 1) else
            (total if n == 0 else total // n) for n in nums]
```
This is fragile with zeros. The two-pass approach is much cleaner.

**Key Insight**: For each position `i`, the answer is `(product of everything to the left of i) * (product of everything to the right of i)`. Compute prefix products left-to-right, then multiply by suffix products right-to-left.

**Optimal Solution**:
```python
def product_except_self(nums: list) -> list:
    n = len(nums)
    result = [1] * n

    # Left pass: result[i] = product of nums[0..i-1]
    prefix = 1
    for i in range(n):
        result[i] = prefix
        prefix *= nums[i]

    # Right pass: multiply by product of nums[i+1..n-1]
    suffix = 1
    for i in range(n - 1, -1, -1):
        result[i] *= suffix
        suffix *= nums[i]

    return result
```
Time: O(n), Space: O(1) extra (output array does not count).

**Dry Run** with `[1, 2, 3, 4]`:
```
Left pass (prefix products):
  i=0: result[0]=1, prefix=1*1=1
  i=1: result[1]=1, prefix=1*2=2
  i=2: result[2]=2, prefix=2*3=6
  i=3: result[3]=6, prefix=6*4=24
  result = [1, 1, 2, 6]

Right pass (multiply by suffix products):
  i=3: result[3]=6*1=6, suffix=1*4=4
  i=2: result[2]=2*4=8, suffix=4*3=12
  i=1: result[1]=1*12=12, suffix=12*2=24
  i=0: result[0]=1*24=24, suffix=24*1=24
  result = [24, 12, 8, 6]
```

**Edge Cases**: Contains zero (only the position with zero gets a non-zero result), contains multiple zeros (all results are zero), two elements.

**Follow-up Questions**:
- What if division is allowed? (Handle zeros carefully.)
- Can you do it in O(1) space? (The solution above uses only the output array — that counts as O(1) extra.)
- What if the numbers can overflow? (Use modular arithmetic or BigInteger.)

---

### Problem: Basic Calculator II (LC #227) — Medium
**Companies**: Meta, Amazon, Microsoft, Google.

**Problem**: Implement a basic calculator to evaluate a simple expression string containing `+`, `-`, `*`, `/` and non-negative integers. Integer division truncates toward zero. No parentheses.

**Key Insight**: Process character by character. Maintain the current number being built, the previous operator, and a stack. When you encounter an operator (or end of string):
- If previous operator was `+`: push `+num` onto stack.
- If previous operator was `-`: push `-num` onto stack.
- If previous operator was `*`: pop top, multiply with num, push result.
- If previous operator was `/`: pop top, divide by num (truncate toward zero), push result.

At the end, sum everything in the stack.

**Why this works for precedence**: Multiplication and division are evaluated immediately (by operating on the stack top). Addition and subtraction are deferred by just pushing values onto the stack. At the end, summing the stack resolves all the additions and subtractions.

**Optimal Solution**:
```python
def calculate(s: str) -> int:
    stack = []
    num = 0
    prev_op = '+'

    for i, ch in enumerate(s):
        if ch.isdigit():
            num = num * 10 + int(ch)

        if ch in '+-*/' or i == len(s) - 1:
            if prev_op == '+':
                stack.append(num)
            elif prev_op == '-':
                stack.append(-num)
            elif prev_op == '*':
                stack.append(stack.pop() * num)
            elif prev_op == '/':
                # Truncate toward zero (Python's // rounds toward -inf)
                top = stack.pop()
                stack.append(int(top / num))
            prev_op = ch
            num = 0

    return sum(stack)
```
Time: O(n), Space: O(n) for the stack.

**Dry Run** with `"3+2*2"`:
```
i=0, ch='3': num=3
i=1, ch='+': prev_op='+', push 3. stack=[3]. prev_op='+', num=0
i=2, ch='2': num=2
i=3, ch='*': prev_op='+', push 2. stack=[3,2]. prev_op='*', num=0
i=4, ch='2': num=2. Last char -> prev_op='*', pop 2, push 2*2=4. stack=[3,4]
sum(stack) = 7
```

**Dry Run** with `" 3/2 "`:
```
i=0 ' ': skip
i=1 '3': num=3
i=2 '/': prev_op='+', push 3. stack=[3]. prev_op='/', num=0
i=3 '2': num=2
i=4 ' ': skip. But it is the last char, so: prev_op='/', pop 3, push int(3/2)=1. stack=[1]
sum(stack) = 1
```

**Edge Cases**: Single number, all additions, leading/trailing spaces, division truncation with negative intermediate results.

**Follow-up Questions**:
- What about parentheses? (Basic Calculator — LC 224, see below.)
- What about unary minus? (E.g., "-2+3".)
- Can you do it with O(1) space? (Track `prev_val` instead of using a stack — multiply/divide immediately, add the running `prev_val` when you see + or -.)

---

### Problem: Basic Calculator (LC #224) — Hard
**Companies**: Meta, Google, Amazon, Microsoft.

**Problem**: Implement a basic calculator to evaluate a string expression with `+`, `-`, parentheses, and non-negative integers.

**Brute Force**: Convert to postfix (Reverse Polish Notation) using the shunting-yard algorithm, then evaluate. This works but is overkill for just `+`, `-`, and parentheses.

**Key Insight**: Use a stack to handle parentheses. When we see `(`, push the current result and sign onto the stack, then reset. When we see `)`, pop the saved sign and result, combine. The stack saves the "context" before entering each parenthesized subexpression.

**Optimal Solution**:
```python
def calculate(s: str) -> int:
    stack = []
    num = 0
    result = 0
    sign = 1  # 1 for positive, -1 for negative

    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch == '+':
            result += sign * num
            num = 0
            sign = 1
        elif ch == '-':
            result += sign * num
            num = 0
            sign = -1
        elif ch == '(':
            # Save current result and sign, start fresh
            stack.append(result)
            stack.append(sign)
            result = 0
            sign = 1
        elif ch == ')':
            result += sign * num
            num = 0
            # Pop sign and previous result
            result *= stack.pop()  # sign before the parenthesis
            result += stack.pop()  # result before the parenthesis

    result += sign * num  # handle last number
    return result
```
Time: O(n), Space: O(n) for the stack (nested parentheses).

**Dry Run** with `"(1+(4+5+2)-3)+(6+8)"`:
```
'(': push result=0, sign=1. stack=[0,1]. result=0, sign=1
'1': num=1
'+': result=0+1*1=1, sign=1, num=0
'(': push result=1, sign=1. stack=[0,1,1,1]. result=0, sign=1
'4': num=4
'+': result=0+1*4=4, sign=1, num=0
'5': num=5
'+': result=4+1*5=9, sign=1, num=0
'2': num=2
')': result=9+1*2=11. Pop sign=1, prev_result=1. result=11*1+1=12
'-': result=12+... wait, let me redo this more carefully:

After ')': result=11, num=0. Pop sign=1 -> result=11*1=11. Pop prev=1 -> result=11+1=12.
'-': result=12+1*0=12, sign=-1, num=0
'3': num=3
')': result=12+(-1)*3=9. Pop sign=1 -> result=9*1=9. Pop prev=0 -> result=9+0=9.
'+': result=9+1*0=9, sign=1, num=0
'(': push result=9, sign=1. stack=[9,1]. result=0, sign=1
'6': num=6
'+': result=0+1*6=6, sign=1, num=0
'8': num=8
')': result=6+1*8=14. Pop sign=1 -> result=14*1=14. Pop prev=9 -> result=14+9=23.

Final: result=23+1*0=23
```

**Edge Cases**: Negative result, deeply nested parentheses, "- (3)" (unary minus before parenthesis), single number, spaces everywhere.

**Follow-up Questions**:
- Add multiplication and division? (Combine with Calculator II approach.)
- Handle exponentiation? (Right-to-left associativity — needs careful stack management.)
- How would you build a full expression parser? (Recursive descent parser or Pratt parser.)

---

### Problem: Text Justification (LC #68) — Hard
**Companies**: Google, Meta, Amazon, Microsoft, Uber — a notoriously precise implementation problem.

**Problem**: Given an array of words and a max width, format the text such that each line has exactly `maxWidth` characters and is fully justified. Extra spaces should be distributed as evenly as possible, with leftover spaces going to the left slots.

**Key Insight**: This is a greedy packing problem followed by careful space distribution.
1. **Pack**: Greedily fit as many words as possible into each line.
2. **Justify**: Distribute spaces evenly. For a line with `k` words, there are `k-1` gaps. Divide extra spaces evenly; leftover goes to leftmost gaps.
3. **Last line**: Left-justify (spaces on the right).

**Optimal Solution**:
```python
def full_justify(words: list, maxWidth: int) -> list:
    result = []
    i = 0

    while i < len(words):
        # Step 1: Determine how many words fit on this line
        line_words = [words[i]]
        line_len = len(words[i])
        i += 1

        while i < len(words) and line_len + 1 + len(words[i]) <= maxWidth:
            line_len += 1 + len(words[i])  # +1 for the space between words
            line_words.append(words[i])
            i += 1

        # Step 2: Build the justified line
        if i == len(words) or len(line_words) == 1:
            # Last line or single word: left-justify
            line = " ".join(line_words)
            line += " " * (maxWidth - len(line))
        else:
            # Middle line: distribute spaces evenly
            total_spaces = maxWidth - sum(len(w) for w in line_words)
            gaps = len(line_words) - 1
            space_per_gap = total_spaces // gaps
            extra_spaces = total_spaces % gaps

            line = ""
            for j, word in enumerate(line_words):
                line += word
                if j < gaps:
                    spaces = space_per_gap + (1 if j < extra_spaces else 0)
                    line += " " * spaces

        result.append(line)

    return result
```
Time: O(total characters), Space: O(total characters).

**Dry Run** with `words=["This","is","an","example","of","text","justification."], maxWidth=16`:
```
Line 1: "This", "is", "an" (4+1+2+1+2=10 <= 16, next "example" would be 10+1+7=18 > 16)
  3 words, 2 gaps, total_spaces = 16 - (4+2+2) = 8, space_per_gap = 4, extra = 0
  "This    is    an"

Line 2: "example", "of", "text" (7+1+2+1+4=15 <= 16, next "justification." would be 15+1+14=30 > 16)
  3 words, 2 gaps, total_spaces = 16 - (7+2+4) = 3, space_per_gap = 1, extra = 1
  "example of  text"  (first gap gets extra space)
  Wait: space_per_gap=3//2=1, extra=3%2=1. Gap 0: 1+1=2 spaces. Gap 1: 1 space.
  "example  of text"

Line 3: "justification." (last line, single word)
  Left justify: "justification.  "

Result: ["This    is    an", "example  of text", "justification.  "]
```

**Edge Cases**: Single word per line, single word in entire input, words exactly filling the line, very long words.

**Follow-up Questions**:
- How would you handle hyphenation?
- What about CJK characters (different width)?
- How does this relate to the Knuth-Plass line-breaking algorithm? (That minimizes a global "badness" metric using DP instead of greedy.)

---

### Problem: Minimum Window Substring (LC #76) — Hard
**Companies**: Meta, Amazon, Google, Microsoft, Uber.

**Problem**: Given strings `s` and `t`, find the minimum window in `s` that contains all characters of `t` (including duplicates).

**Brute Force**: Check every substring of s.
```python
from collections import Counter

def min_window_brute(s: str, t: str) -> str:
    if not t or not s:
        return ""
    t_count = Counter(t)
    best = ""
    for i in range(len(s)):
        for j in range(i + len(t), len(s) + 1):
            window = s[i:j]
            w_count = Counter(window)
            if all(w_count[ch] >= t_count[ch] for ch in t_count):
                if not best or len(window) < len(best):
                    best = window
    return best
```
Time: O(n^2 * m), Space: O(n).

**Key Insight**: Sliding window with character frequency tracking. Expand the right pointer until the window contains all characters of t. Then shrink the left pointer to find the minimum valid window. Use a `have` counter to track how many distinct characters meet the required count.

**Optimal Solution**:
```python
from collections import Counter

def min_window(s: str, t: str) -> str:
    if not t or not s:
        return ""

    t_count = Counter(t)
    required = len(t_count)  # number of unique chars in t

    window_counts = {}
    have = 0  # number of unique chars in window that meet required count
    left = 0
    min_len = float('inf')
    min_start = 0

    for right in range(len(s)):
        ch = s[right]
        window_counts[ch] = window_counts.get(ch, 0) + 1

        # Check if this character's count now meets the requirement
        if ch in t_count and window_counts[ch] == t_count[ch]:
            have += 1

        # Try to shrink from the left
        while have == required:
            # Update minimum
            if right - left + 1 < min_len:
                min_len = right - left + 1
                min_start = left

            # Remove leftmost character
            left_ch = s[left]
            window_counts[left_ch] -= 1
            if left_ch in t_count and window_counts[left_ch] < t_count[left_ch]:
                have -= 1
            left += 1

    return "" if min_len == float('inf') else s[min_start:min_start + min_len]
```
Time: O(|s| + |t|), Space: O(|s| + |t|).

**Dry Run** with `s="ADOBECODEBANC", t="ABC"`:
```
t_count = {A:1, B:1, C:1}, required=3

right=0 'A': window={A:1}, have=1 (A met)
right=1 'D': window={A:1,D:1}, have=1
right=2 'O': have=1
right=3 'B': window={...,B:1}, have=2 (B met)
right=4 'E': have=2
right=5 'C': window={...,C:1}, have=3 (C met) -> VALID

  Shrink: window="ADOBEC" len=6, min_len=6, min_start=0
  Remove 'A': window={A:0,...}, have=2 (A no longer met). left=1
  Stop shrinking.

right=6 'O': have=2
...
right=9 'A': window={A:1,...}, check: have might become 3
  Actually: window_counts[A] was 0, now 1, equals t_count[A]=1, so have=3

  Shrink from left=1:
  Remove 'D': have=3. Window shrinks.
  Remove 'O': have=3.
  Remove 'B': window_counts[B] goes from 1 to 0 < t_count[B]=1, have=2. left=4
  Before removing B, window was "CODEBA" len=6 (right=9, left=3)?
  Let me recount more carefully...

  The key point: the algorithm finds "BANC" (length 4) as the minimum window.

Answer: "BANC"
```

**Edge Cases**: t longer than s (impossible, return ""), t equals s, s and t are single characters, t has duplicate characters.

**Follow-up Questions**:
- What if you need to find all minimum windows? (Track all windows with the same minimum length.)
- What if character order matters? (Different problem — subsequence matching.)
- How would you handle this with a stream? (Cannot shrink from left — different approach needed.)

---

### Problem: Substring with Concatenation of All Words (LC #30) — Hard
**Companies**: Google, Amazon, Microsoft.

**Problem**: Given a string `s` and an array of words (all same length), find all starting indices where a concatenation of all words (in any order) forms a substring.

**Brute Force**: For each starting position, check if the next `total_len` characters form a valid concatenation.
```python
from collections import Counter

def find_substring_brute(s: str, words: list) -> list:
    if not s or not words:
        return []
    word_len = len(words[0])
    total_len = word_len * len(words)
    word_count = Counter(words)
    result = []

    for i in range(len(s) - total_len + 1):
        seen = {}
        j = 0
        while j < len(words):
            word = s[i + j * word_len:i + (j + 1) * word_len]
            if word not in word_count:
                break
            seen[word] = seen.get(word, 0) + 1
            if seen[word] > word_count[word]:
                break
            j += 1
        if j == len(words):
            result.append(i)

    return result
```
Time: O(n * m * k) where n = len(s), m = number of words, k = word length.

**Key Insight — Sliding Window with Word-Level Tokens**: Since all words have the same length, we can treat the string as a sequence of fixed-length tokens. Use a sliding window of size `total_len` that moves by one word at a time. There are `word_len` possible starting offsets.

**Optimal Solution**:
```python
from collections import Counter

def find_substring(s: str, words: list) -> list:
    if not s or not words:
        return []

    word_len = len(words[0])
    num_words = len(words)
    total_len = word_len * num_words
    word_count = Counter(words)
    result = []

    # Try each starting offset (0 to word_len-1)
    for offset in range(word_len):
        left = offset
        window = {}
        count = 0  # number of valid words in window

        for right in range(offset, len(s) - word_len + 1, word_len):
            word = s[right:right + word_len]

            if word in word_count:
                window[word] = window.get(word, 0) + 1
                count += 1

                # If we have too many of this word, shrink from left
                while window[word] > word_count[word]:
                    left_word = s[left:left + word_len]
                    window[left_word] -= 1
                    count -= 1
                    left += word_len

                if count == num_words:
                    result.append(left)
                    # Shrink by one word to look for next match
                    left_word = s[left:left + word_len]
                    window[left_word] -= 1
                    count -= 1
                    left += word_len
            else:
                # Invalid word — reset window
                window.clear()
                count = 0
                left = right + word_len

    return result
```
Time: O(n * k) where k = word_len. Space: O(m) for the counter.

**Dry Run** with `s="barfoothefoobarman", words=["foo","bar"]`:
```
word_len=3, num_words=2, total_len=6
word_count = {"foo":1, "bar":1}

offset=0: check positions 0,3,6,9,12,15
  right=0: word="bar" in word_count. window={"bar":1}, count=1
  right=3: word="foo" in word_count. window={"bar":1,"foo":1}, count=2
    count==2! result=[0]. Shrink: remove "bar", left=3, count=1
  right=6: word="the" NOT in word_count. Reset. left=9, count=0
  right=9: word="foo" -> window={"foo":1}, count=1
  right=12: word="bar" -> window={"foo":1,"bar":1}, count=2
    count==2! result=[0,9]. Shrink.
  right=15: word="man" NOT in word_count. Reset.

offset=1: check positions 1,4,7,...
  right=1: "arf" not in word_count, reset
  ...

offset=2: similar, no matches

Result: [0, 9]
```

**Edge Cases**: Empty words array, single word, all words are the same, no match possible.

**Follow-up Questions**:
- What if words have different lengths? (Much harder — need Aho-Corasick or hash-based matching.)
- What is the time complexity of the optimized approach? (O(n * word_len) since we have word_len offsets, each processing n/word_len words.)

---

## Common Mistakes & Interview Tips

### Mistakes to Avoid
1. **String immutability** — In Python and Java, strings are immutable. Concatenating in a loop is O(n^2). Use `"".join(list)` or `StringBuilder`.
2. **Integer overflow in products** — Python handles this natively, but in Java/C++, the product of array elements can overflow.
3. **Division truncation toward zero** — Python's `//` truncates toward negative infinity, not toward zero. Use `int(a / b)` for truncation toward zero.
4. **Off-by-one in substring indices** — `s[i:j]` includes index i but excludes j. Be precise.
5. **Not handling spaces in calculator problems** — Skip whitespace explicitly.
6. **Forgetting the last number in parsing** — When the string ends with a digit, process the accumulated number after the loop.

### Interview Tips
1. **For anagram problems, state your key choice upfront** — "I will use the sorted string as a hashmap key because two anagrams sort to the same string."
2. **For prefix/suffix problems, draw the arrays** — Show the prefix and suffix arrays side by side, then show how they combine.
3. **For calculator problems, explain operator precedence** — "Multiplication and division have higher precedence, so I evaluate them immediately. Addition and subtraction are deferred to the stack."
4. **For hard string problems, start with brute force** — For Text Justification and Minimum Window Substring, stating the brute force clearly shows you understand the problem before optimizing.
5. **Practice Text Justification implementation** — It is pure implementation with no algorithmic trick, but getting the spacing logic right under time pressure is challenging.
6. **Know the complexity of string operations** — Sorting a string is O(L log L). Building a frequency array is O(L). Comparing two strings is O(L).

---

## Pattern Connections

| Pattern | Connection to String/Array |
|---------|---------------------------|
| **Sliding Window** | Minimum window substring, anagram substrings, all use sliding window on strings. |
| **Two Pointers** | Valid palindrome, two-sum on sorted arrays. |
| **Hash Map** | Anagram grouping, character frequency tracking, two-sum. |
| **Stack** | Calculator problems, parentheses matching, decoding strings. |
| **Prefix Sum** | Product except self is the multiplicative version of prefix sum. |
| **Greedy** | Text justification packs words greedily. |
| **Dynamic Programming** | Longest palindromic substring (DP approach), edit distance, regex matching. |
| **Trie** | String matching with common prefixes, autocomplete. |

### Progression Path
```
Valid Palindrome (125) -> Longest Palindromic Substring (5) -> Palindrome Partitioning (131)
Group Anagrams (49) -> Find All Anagrams (438) -> Minimum Window Substring (76)
Product Except Self (238) -> Trapping Rain Water (42) -> Candy (135)
Basic Calculator II (227) -> Basic Calculator (224) -> Basic Calculator III (772)
Encode/Decode (271) -> Serialize/Deserialize (297)
Text Justification (68) — standalone implementation problem
```
