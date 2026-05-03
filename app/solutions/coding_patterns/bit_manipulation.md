# Bit Manipulation — Complete Interview Guide

## When to Use This Pattern

### Signals That Point to Bit Manipulation
1. **"Find the unique element"** — XOR-based problems where elements appear in pairs except one.
2. **The problem involves powers of 2** — checking, counting, or generating powers of 2.
3. **Bitmask / subset enumeration** — representing subsets as integers, iterating over all subsets.
4. **Space-constrained counting** — counting bits, reversing bits, or manipulating binary representations.
5. **"Do X without using arithmetic operators"** — add, subtract, multiply without +, -, *.
6. **Feature flags, permissions, or state encoding** — using individual bits to represent boolean states.

### When NOT to Use
- If the numbers are very large (arbitrary precision) — bit tricks rely on fixed-width integers.
- If the problem is about string patterns or graph traversal — bit manipulation is rarely the core technique.
- If a simpler mathematical solution exists — do not force bit manipulation for cleverness.

---

### ⚡ Pattern Overlap & Decision Guide

#### Bit Manipulation vs Commonly Confused Patterns

| Signal | Bit Manipulation | Math / Number Theory | Hash Map | DP (Bitmask) |
|--------|-----------------|---------------------|----------|---------------|
| "Find the unique element" (others appear k times) | **XOR cancellation** | `k*sum(set) - sum(arr)` works for k=2 | HashSet/Counter works but O(n) space | N/A |
| "Subset enumeration" with n <= 20 | **Bitmask iteration** | N/A | N/A | **Bitmask DP** if optimizing over subsets |
| "Power of 2" check | **`n & (n-1) == 0`** | `log2(n)` check (float issues) | N/A | N/A |
| "Count bits" or "manipulate binary" | **Kernighan's / bit tricks** | N/A | N/A | N/A |
| "Optimal ordering of n <= 20 items" | N/A | N/A | N/A | **Bitmask DP (TSP-style)** |
| "Add/subtract without arithmetic" | **XOR + AND for carry** | N/A | N/A | N/A |

#### Quick Signals That Point to Bit Manipulation Specifically
- "Without using extra space" + finding duplicates/unique elements
- "Every element appears twice except one" (or three times except one)
- The problem explicitly mentions binary representation, bits, or XOR
- Constraint says n <= 20 and asks for optimal subset/permutation -- bitmask DP
- "Do X without using +, -, *, /" operators

#### Common Mistakes: "You might think it is X, but it is actually Y"

1. **"Find the missing number" -- Bit Manipulation vs Math**: **LC 268 Missing Number** can be solved with XOR (XOR all indices and values, missing number remains) OR with math (`n*(n+1)/2 - sum`). Both are O(n) time, O(1) space. XOR is safer (no overflow), but math is more intuitive. The XOR approach is bit manipulation; the sum approach is pure math. Know both.

2. **"Subsets of a set" -- Bitmask vs Backtracking**: **LC 78 Subsets** can be solved with bitmask enumeration (iterate 0 to 2^n - 1, each bit represents include/exclude) or with recursive backtracking. Bitmask is iterative and elegant for n <= 20. Backtracking is more general and works for larger n. If n is small and you need ALL subsets, bitmask is cleaner. If you need to prune, use backtracking.

3. **"Partition into k subsets" -- Bitmask DP vs Regular DP**: **LC 698 Partition to K Equal Sum Subsets** can be solved with bitmask DP (state = which elements are used) or backtracking with pruning. Bitmask DP is O(2^n * n) and works for n <= 20. If n > 20, you must use backtracking. The bitmask DP approach is NOT standard DP -- it is a separate pattern that happens to use memoization.

#### Problems That LOOK Like Bit Manipulation But Are Not
- **LC 136 Single Number** IS bit manipulation (XOR). But **LC 287 Find the Duplicate Number** (array where one number repeats) looks similar but is solved with **Floyd's Cycle Detection** (linked list pattern) or **binary search on value range**, NOT XOR.
- **LC 169 Majority Element** can be solved with bit counting (check each bit position, take the majority bit), but the intended approach is **Boyer-Moore Voting** (a math/greedy technique). Bit manipulation works but is O(32n) vs O(n).
- **LC 1494 Parallel Courses II** has a bitmask DP solution, but it is fundamentally a **graph scheduling / topological sort** problem. The bitmask DP is the optimization technique, not the core pattern.

---

## Core Mechanics

### Binary Number Representation
Every integer is stored as a sequence of bits. In a 32-bit system:
```
 5 = 00000000 00000000 00000000 00000101
-5 = 11111111 11111111 11111111 11111011  (two's complement)
```

**Two's complement** for negative numbers: invert all bits and add 1. This makes addition work uniformly for positive and negative numbers.

### Essential Bit Operations

| Operation | Symbol | Example | Result |
|-----------|--------|---------|--------|
| AND | `&` | `1010 & 1100` | `1000` |
| OR | `\|` | `1010 \| 1100` | `1110` |
| XOR | `^` | `1010 ^ 1100` | `0110` |
| NOT | `~` | `~1010` | `0101` (plus sign flip) |
| Left shift | `<<` | `0001 << 3` | `1000` (multiply by 2^3) |
| Right shift | `>>` | `1000 >> 2` | `0010` (divide by 2^2) |

### The Essential Bit Tricks Cheat Sheet

Every one of these should be memorized:

```python
# 1. Check if nth bit is set
(x >> n) & 1       # returns 1 if bit n is set, 0 otherwise

# 2. Set nth bit
x | (1 << n)       # force bit n to 1

# 3. Clear nth bit
x & ~(1 << n)      # force bit n to 0

# 4. Toggle nth bit
x ^ (1 << n)       # flip bit n

# 5. Clear the lowest set bit
x & (x - 1)        # turn off the rightmost 1-bit
# Example: 1100 & 1011 = 1000

# 6. Isolate the lowest set bit
x & (-x)           # keep only the rightmost 1-bit
# Example: 1100 & 0100 = 0100  (two's complement: -x = ~x + 1)

# 7. Check if power of 2
x > 0 and (x & (x - 1)) == 0

# 8. Count set bits (Kernighan's algorithm)
count = 0
while x:
    x &= x - 1     # clear lowest set bit
    count += 1

# 9. Check if all bits are set up to some position
(x & (x + 1)) == 0  # True for 0, 1, 11, 111, 1111, ...

# 10. Swap two values without temp
a ^= b; b ^= a; a ^= b
```

### XOR Properties (Critical for Interview)
```
a ^ a = 0          # XOR with itself is 0
a ^ 0 = a          # XOR with 0 is identity
a ^ b = b ^ a      # commutative
(a ^ b) ^ c = a ^ (b ^ c)  # associative
```

These properties mean: XOR of a collection cancels out duplicates. If every element appears twice except one, XOR of all elements gives that one element.

### Why `x & (x - 1)` Clears the Lowest Set Bit

Consider `x = 1010100` (binary). Then `x - 1 = 1010011` — it flips the lowest 1-bit and all bits below it. AND-ing:
```
x     = 1010100
x - 1 = 1010011
x & (x-1) = 1010000  <- lowest set bit is cleared
```

This is the basis of Kernighan's bit counting algorithm: keep clearing the lowest bit and counting until the number is 0.

### Why `x & (-x)` Isolates the Lowest Set Bit

In two's complement, `-x = ~x + 1`. For `x = 1010100`:
```
x  = 1010100
~x = 0101011
-x = 0101100
x & (-x) = 0000100  <- only the lowest set bit remains
```

### Complexity of Bit Operations
All bitwise operations on fixed-width integers (32-bit or 64-bit) are O(1). Counting bits is O(number of set bits) with Kernighan's algorithm, or O(1) with lookup tables or built-in `popcount`.

---

## The Templates

### Python — Bit Counting Template
```python
def count_bits(n: int) -> int:
    """Count the number of 1-bits in n (Kernighan's algorithm)."""
    count = 0
    while n:
        n &= n - 1  # clear lowest set bit
        count += 1
    return count
```

### Python — Subset Enumeration with Bitmask
```python
def enumerate_subsets(nums: list) -> list:
    """Generate all subsets using bitmask."""
    n = len(nums)
    subsets = []
    for mask in range(1 << n):  # 0 to 2^n - 1
        subset = []
        for i in range(n):
            if mask & (1 << i):
                subset.append(nums[i])
        subsets.append(subset)
    return subsets
```

### Python — Bitmask DP Template
```python
def bitmask_dp(n: int, cost: list) -> int:
    """Template for bitmask DP. dp[mask] = optimal value for the subset represented by mask."""
    dp = [float('inf')] * (1 << n)
    dp[0] = 0  # empty set base case

    for mask in range(1 << n):
        if dp[mask] == float('inf'):
            continue
        # Try adding each element not yet in the set
        for i in range(n):
            if mask & (1 << i):
                continue  # element i already in set
            new_mask = mask | (1 << i)
            dp[new_mask] = min(dp[new_mask], dp[mask] + cost[i])

    return dp[(1 << n) - 1]  # all elements included
```

### Python — Add Without Arithmetic Operators
```python
def add(a: int, b: int) -> int:
    """Add two numbers using only bit operations."""
    # In Python, handle 32-bit overflow manually
    MASK = 0xFFFFFFFF
    MAX_INT = 0x7FFFFFFF
    while b & MASK:
        carry = (a & b) << 1
        a = a ^ b
        b = carry
    # If b is 0, a is the answer
    # Handle negative numbers in Python's arbitrary precision
    return a & MASK if a > MAX_INT else a
```

### Go — Bit Manipulation Templates
```go
func countBits(n int) int {
    count := 0
    for n > 0 {
        n &= n - 1
        count++
    }
    return count
}

func isPowerOfTwo(n int) bool {
    return n > 0 && n&(n-1) == 0
}

// Add two numbers without + operator
func getSum(a, b int) int {
    for b != 0 {
        carry := (a & b) << 1
        a = a ^ b
        b = carry
    }
    return a
}

// Enumerate subsets of nums
func subsets(nums []int) [][]int {
    n := len(nums)
    var result [][]int
    for mask := 0; mask < (1 << n); mask++ {
        var subset []int
        for i := 0; i < n; i++ {
            if mask&(1<<i) != 0 {
                subset = append(subset, nums[i])
            }
        }
        result = append(result, subset)
    }
    return result
}
```

---

## Variant Subpatterns

### 1. XOR Tricks (Finding Unique Elements)
- **Single unique**: XOR all elements. Duplicates cancel out.
- **Two unique (LC 260)**: XOR all to get `a ^ b`. Find a set bit (use `x & (-x)`). Split elements by that bit into two groups. XOR each group separately.
- **Three unique same frequency**: Requires bit counting per position.

### 2. Bit Counting and Manipulation
- Count set bits (Kernighan's).
- Reverse bits (swap halves, then quarters, etc.).
- Find the highest/lowest set bit.

### 3. Bitmask DP
Represent the "set of items chosen" as a bitmask. The state space is 2^n, so this works for n <= 20-23.
- Traveling Salesman Problem (TSP).
- Partition into equal-sum subsets.
- Find Shortest Superstring.
- Assignment problems (who does what task).

### 4. Arithmetic with Bits
- Addition: XOR for sum without carry, AND shifted left for carry.
- Subtraction: a - b = a + (~b + 1).
- Multiplication: shift-and-add.

### 5. Bit-Level System Design Concepts
- **Bloom Filters**: Probabilistic set membership using bit arrays and hash functions.
- **Feature Flags**: Use individual bits in an integer to represent on/off features.
- **Bitmask Permissions**: Unix file permissions (rwxrwxrwx = 9 bits).
- **Compact Set Representation**: When the universe is small, use bits instead of hash sets.

---

## Problem Walkthroughs

---

### Problem: Single Number (LC #136) — Easy
**Companies**: Amazon, Microsoft, Google, Apple.

**Problem**: Given a non-empty array where every element appears twice except one, find the single element that appears once.

**Brute Force**: Use a hash set — add if not present, remove if present.
```python
def single_number_brute(nums: list) -> int:
    seen = set()
    for n in nums:
        if n in seen:
            seen.remove(n)
        else:
            seen.add(n)
    return seen.pop()
```
Time: O(n), Space: O(n).

**Key Insight**: XOR of all elements cancels out the pairs. `a ^ a = 0` and `0 ^ b = b`. So XOR of the entire array gives the unique element.

**Optimal Solution**:
```python
def single_number(nums: list) -> int:
    result = 0
    for n in nums:
        result ^= n
    return result
```
Time: O(n), Space: O(1).

One-liner: `return reduce(lambda a, b: a ^ b, nums)` or `return reduce(operator.xor, nums)`.

**Dry Run** with `[4, 1, 2, 1, 2]`:
```
result = 0
0 ^ 4 = 4
4 ^ 1 = 5  (binary: 100 ^ 001 = 101)
5 ^ 2 = 7  (101 ^ 010 = 111)
7 ^ 1 = 6  (111 ^ 001 = 110)
6 ^ 2 = 4  (110 ^ 010 = 100)
Result: 4
```

**Edge Cases**: Array of size 1, negative numbers (XOR works on two's complement), all same elements except one.

**Follow-up Questions**:
- What if every element appears THREE times except one? (Count bits at each position mod 3.)
- What if TWO elements appear once? (LC 260 — XOR all, split by a differing bit.)
- Can you solve it without XOR? (Math: `2 * sum(set) - sum(nums)`.)

---

### Problem: Number of 1 Bits (LC #191) — Easy
**Companies**: Amazon, Microsoft, Apple.

**Problem**: Write a function that takes an unsigned integer and returns the number of '1' bits (Hamming weight).

**Brute Force**: Check each of the 32 bits.
```python
def hamming_weight_brute(n: int) -> int:
    count = 0
    for i in range(32):
        if n & (1 << i):
            count += 1
    return count
```
Time: O(32) = O(1), Space: O(1). Always checks all 32 bits even if most are 0.

**Key Insight**: Use Kernighan's algorithm — `n & (n - 1)` clears the lowest set bit. Loop until n is 0, counting iterations. Only loops as many times as there are set bits.

**Optimal Solution**:
```python
def hamming_weight(n: int) -> int:
    count = 0
    while n:
        n &= n - 1  # clear lowest set bit
        count += 1
    return count
```
Time: O(k) where k = number of set bits. Space: O(1).

**Dry Run** with `n = 11 (binary: 1011)`:
```
n = 1011, count = 0
n & (n-1) = 1011 & 1010 = 1010, count = 1  (cleared bit 0)
n & (n-1) = 1010 & 1001 = 1000, count = 2  (cleared bit 1)
n & (n-1) = 1000 & 0111 = 0000, count = 3  (cleared bit 3)
n = 0, stop. Answer: 3
```

**Edge Cases**: n = 0 (return 0), n = all 1s (return 32), n = power of 2 (return 1).

**Follow-up Questions**:
- If this function is called many times, how to optimize? (Use a lookup table for each byte. Precompute popcount for 0-255.)
- What is the Hamming distance between two numbers? (popcount of a XOR b.)

---

### Problem: Counting Bits (LC #338) — Easy
**Companies**: Amazon, Google, Microsoft.

**Problem**: Given an integer n, return an array where `ans[i]` is the number of 1 bits in i, for 0 <= i <= n.

**Brute Force**: For each number, count bits individually.
```python
def count_bits_brute(n: int) -> list:
    result = []
    for i in range(n + 1):
        count = 0
        x = i
        while x:
            x &= x - 1
            count += 1
        result.append(count)
    return result
```
Time: O(n * 32) worst case. Space: O(n) for output.

**Key Insight**: Use the DP relation `bits[i] = bits[i & (i-1)] + 1`. Since `i & (i-1)` clears the lowest set bit of i, the result has one fewer 1-bit, and we already computed its popcount.

Alternative DP: `bits[i] = bits[i >> 1] + (i & 1)`. The number i has the same bits as i/2, plus potentially one more if the last bit is 1.

**Optimal Solution**:
```python
def count_bits(n: int) -> list:
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i & (i - 1)] + 1  # clear lowest bit, add 1
    return dp
```
Time: O(n), Space: O(n) for the output.

**Alternative DP approach**:
```python
def count_bits_alt(n: int) -> list:
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i >> 1] + (i & 1)
    return dp
```

**Dry Run** for n=5:
```
dp = [0, 0, 0, 0, 0, 0]
i=1: dp[1] = dp[1 & 0] + 1 = dp[0] + 1 = 1
i=2: dp[2] = dp[2 & 1] + 1 = dp[0] + 1 = 1
i=3: dp[3] = dp[3 & 2] + 1 = dp[2] + 1 = 2
i=4: dp[4] = dp[4 & 3] + 1 = dp[0] + 1 = 1
i=5: dp[5] = dp[5 & 4] + 1 = dp[4] + 1 = 2
Result: [0, 1, 1, 2, 1, 2]
```

**Edge Cases**: n = 0 (return [0]).

**Follow-up Questions**:
- Can you do it in O(n) time without using any built-in function? (Yes, as shown.)
- How does this relate to the mathematical concept of binary entropy?

---

### Problem: Reverse Bits (LC #190) — Easy
**Companies**: Amazon, Apple, Microsoft.

**Problem**: Reverse bits of a given 32-bit unsigned integer.

**Brute Force**: Convert to binary string, reverse, convert back.
```python
def reverse_bits_brute(n: int) -> int:
    binary = bin(n)[2:].zfill(32)
    return int(binary[::-1], 2)
```

**Key Insight**: Extract bits from right to left, build the result from left to right. For each of 32 bits, check the lowest bit of n, shift it into the correct position in the result.

**Optimal Solution**:
```python
def reverse_bits(n: int) -> int:
    result = 0
    for i in range(32):
        result = (result << 1) | (n & 1)  # shift result left, add lowest bit of n
        n >>= 1                            # shift n right
    return result
```
Time: O(32) = O(1), Space: O(1).

**Divide and Conquer approach** (bit-parallel, O(log 32) = O(1)):
```python
def reverse_bits_dc(n: int) -> int:
    n = ((n & 0xFFFF0000) >> 16) | ((n & 0x0000FFFF) << 16)  # swap 16-bit halves
    n = ((n & 0xFF00FF00) >> 8)  | ((n & 0x00FF00FF) << 8)   # swap 8-bit halves
    n = ((n & 0xF0F0F0F0) >> 4)  | ((n & 0x0F0F0F0F) << 4)  # swap 4-bit halves
    n = ((n & 0xCCCCCCCC) >> 2)  | ((n & 0x33333333) << 2)   # swap 2-bit halves
    n = ((n & 0xAAAAAAAA) >> 1)  | ((n & 0x55555555) << 1)   # swap individual bits
    return n
```
This is how hardware and optimized libraries actually reverse bits.

**Dry Run** with `n = 43261596`:
```
n in binary: 00000010 10010100 00011110 10011100

Bit-by-bit reversal:
Position 0 (rightmost): bit = 0, goes to position 31
Position 1: bit = 0, goes to position 30
...
After full reversal:
00111001 01111000 00101001 01000000 = 964176192
```

**Edge Cases**: n = 0 (return 0), n = all 1s (return all 1s), n = 1 (return 2^31).

**Follow-up Questions**:
- If called many times, how to optimize? (Cache results for each byte. Reverse each of the 4 bytes using a 256-entry lookup table, then reassemble in reverse order.)
- How does the divide-and-conquer approach work? (Swap halves at decreasing granularity.)

---

### Problem: Sum of Two Integers (LC #371) — Medium
**Companies**: Meta, Amazon, Google.

**Problem**: Calculate the sum of two integers without using + or -.

**Key Insight**: XOR gives the sum without carry. AND gives the carry bits. Shift carry left by 1 (carry propagates to the next position). Repeat until there is no carry.

```
  a = 5  (101)
  b = 3  (011)

  Step 1: sum_no_carry = 101 ^ 011 = 110 (6)
          carry = (101 & 011) << 1 = (001) << 1 = 010 (2)

  Step 2: a = 110, b = 010
          sum_no_carry = 110 ^ 010 = 100 (4)
          carry = (110 & 010) << 1 = (010) << 1 = 100 (4)

  Step 3: a = 100, b = 100
          sum_no_carry = 100 ^ 100 = 000 (0)
          carry = (100 & 100) << 1 = (100) << 1 = 1000 (8)

  Step 4: a = 000, b = 1000
          sum_no_carry = 000 ^ 1000 = 1000 (8)
          carry = (000 & 1000) << 1 = 0

  b = 0, done. Answer: 8 = 5 + 3 ✓
```

**Optimal Solution**:
```python
def get_sum(a: int, b: int) -> int:
    # Python integers have arbitrary precision, so we need to mask to 32 bits
    MASK = 0xFFFFFFFF      # 32-bit mask
    MAX_INT = 0x7FFFFFFF   # max positive 32-bit int

    while b & MASK:
        carry = (a & b) << 1
        a = a ^ b
        b = carry

    # If a fits in 32 bits, return it
    # If it overflows (negative in 32-bit), convert from unsigned to signed
    a = a & MASK
    return a if a <= MAX_INT else ~(a ^ MASK)
```

**Why the Python version is tricky**: Python integers are arbitrary precision — they do not overflow. In languages like Java/C++, the natural 32-bit overflow handles negative numbers automatically. In Python, we need to manually mask to 32 bits and convert back to signed representation.

**Go version** (cleaner due to fixed-width integers):
```go
func getSum(a, b int) int {
    for b != 0 {
        carry := (a & b) << 1
        a = a ^ b
        b = carry
    }
    return a
}
```

**Dry Run** with `a=1, b=2`:
```
a=001, b=010:
  carry = (001 & 010) << 1 = 0
  a = 001 ^ 010 = 011 (3)
  b = 0 -> stop
Answer: 3
```

**Edge Cases**: One or both operands are 0, negative numbers, adding -1 + 1.

**Follow-up Questions**:
- How would you implement subtraction? (`a - b = a + (~b + 1)`, but you need getSum for the +1.)
- How would you implement multiplication? (Shift-and-add.)
- Why does this always terminate? (Each iteration, the carry has strictly fewer bits — the lowest set bit moves left.)

---

### Problem: Maximum XOR of Two Numbers in an Array (LC #421) — Medium (labeled Hard-adjacent)
**Companies**: Google, Amazon, Microsoft.

**Problem**: Given an integer array, find the maximum XOR of any two elements.

**Brute Force**: Check all pairs.
```python
def find_max_xor_brute(nums: list) -> int:
    max_xor = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            max_xor = max(max_xor, nums[i] ^ nums[j])
    return max_xor
```
Time: O(n^2), Space: O(1).

**Key Insight — Greedy Bit-by-Bit using Hash Set**:
Build the answer bit by bit, from the most significant bit down. At each bit position, we check if it is possible to set this bit to 1 in the XOR result. We use the property: if `a ^ b = target`, then `a ^ target = b`. So we check if any pair of prefixes can produce the desired target.

**Optimal Solution — Hash Set**:
```python
def find_max_xor(nums: list) -> int:
    max_xor = 0
    mask = 0

    for i in range(31, -1, -1):  # from bit 31 down to bit 0
        mask |= (1 << i)  # consider bits from MSB down to bit i

        # Collect all prefixes up to bit i
        prefixes = set()
        for n in nums:
            prefixes.add(n & mask)

        # Greedily try to set bit i in the answer
        candidate = max_xor | (1 << i)

        # Check if any two prefixes produce this candidate
        for prefix in prefixes:
            # If prefix ^ candidate is also a prefix, then candidate is achievable
            if prefix ^ candidate in prefixes:
                max_xor = candidate
                break

    return max_xor
```
Time: O(32 * n) = O(n), Space: O(n).

**Alternative — Trie Solution**:
```python
class TrieNode:
    def __init__(self):
        self.children = {}  # 0 or 1

def find_max_xor_trie(nums: list) -> int:
    # Build trie of all numbers (bit by bit from MSB)
    root = TrieNode()
    for num in nums:
        node = root
        for i in range(31, -1, -1):
            bit = (num >> i) & 1
            if bit not in node.children:
                node.children[bit] = TrieNode()
            node = node.children[bit]

    # For each number, find the number that maximizes XOR
    max_xor = 0
    for num in nums:
        node = root
        curr_xor = 0
        for i in range(31, -1, -1):
            bit = (num >> i) & 1
            # To maximize XOR, we want the opposite bit
            want = 1 - bit
            if want in node.children:
                curr_xor |= (1 << i)
                node = node.children[want]
            else:
                node = node.children[bit]
        max_xor = max(max_xor, curr_xor)

    return max_xor
```
Time: O(32 * n) = O(n), Space: O(32 * n) = O(n).

**Dry Run (Hash Set)** with `nums = [3, 10, 5, 25, 2, 8]`:
```
Binary representations:
3  = 00011
10 = 01010
5  = 00101
25 = 11001
2  = 00010
8  = 01000

Bit 4 (16): mask=10000, prefixes={00000, 00000, 00000, 10000, 00000, 00000} = {0, 16}
  candidate = 10000 (16). Check: 0 ^ 16 = 16, 16 in prefixes? Yes -> max_xor = 16

Bit 3 (8): mask=11000, prefixes={00000, 01000, 00000, 11000, 00000, 01000} = {0, 8, 24}
  candidate = 11000 (24). Check: 0 ^ 24 = 24, in prefixes? Yes -> max_xor = 24

Bit 2 (4): mask=11100, prefixes={00000, 01000, 00100, 11000, 00000, 01000} = {0, 8, 4, 24}
  candidate = 11100 (28). Check: 0^28=28? No. 8^28=20? No. 4^28=24? Yes -> max_xor = 28

Final answer: 28 (from 5 ^ 25 = 00101 ^ 11001 = 11100 = 28)
```

**Edge Cases**: Array with two elements, all elements the same (XOR = 0), numbers with many leading zeros.

**Follow-up Questions**:
- Can you do it in O(n) time? (Yes, both approaches above are O(32n) = O(n).)
- How does the trie approach extend to finding max XOR subarray?
- What if you need the maximum XOR of k elements instead of 2? (Much harder — Gaussian elimination over GF(2).)

---

### Problem: Find the Shortest Superstring (LC #943) — Hard
**Companies**: Google, Amazon.

**Problem**: Given an array of strings, find the shortest string that contains each string as a substring. Return any valid answer.

**Brute Force**: Try all permutations of strings, greedily overlapping each pair.
```python
def shortest_superstring_brute(words: list) -> str:
    from itertools import permutations

    def overlap(a, b):
        """Max overlap: suffix of a that is prefix of b."""
        for i in range(min(len(a), len(b)), 0, -1):
            if a.endswith(b[:i]):
                return i
        return 0

    def merge_all(perm):
        result = perm[0]
        for i in range(1, len(perm)):
            ov = overlap(result, perm[i])
            result += perm[i][ov:]
        return result

    best = None
    for perm in permutations(words):
        merged = merge_all(perm)
        if best is None or len(merged) < len(best):
            best = merged
    return best
```
Time: O(n! * n * L) where L is max string length. Completely impractical for n > 10.

**Key Insight — Bitmask DP**: This is essentially the Traveling Salesman Problem (TSP). Each "city" is a word. The "distance" from word i to word j is `len(words[j]) - overlap(words[i], words[j])` (the extra characters j adds). We want to visit all cities with minimum total distance.

Use bitmask DP where `dp[mask][i]` = minimum total length when we have used the words in `mask` and the last word is `i`.

**Optimal Solution — Bitmask DP**:
```python
def shortest_superstring(words: list) -> str:
    n = len(words)

    # Precompute overlap[i][j] = max suffix of words[i] matching prefix of words[j]
    overlap = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            max_ov = min(len(words[i]), len(words[j]))
            for k in range(max_ov, 0, -1):
                if words[i].endswith(words[j][:k]):
                    overlap[i][j] = k
                    break

    # dp[mask][i] = min extra chars when words in mask are used, last word is i
    INF = float('inf')
    dp = [[INF] * n for _ in range(1 << n)]
    parent = [[-1] * n for _ in range(1 << n)]

    # Base case: start with each word alone
    for i in range(n):
        dp[1 << i][i] = len(words[i])

    # Fill DP
    for mask in range(1 << n):
        for last in range(n):
            if dp[mask][last] == INF:
                continue
            if not (mask & (1 << last)):
                continue
            for nxt in range(n):
                if mask & (1 << nxt):
                    continue  # already used
                new_mask = mask | (1 << nxt)
                new_cost = dp[mask][last] + len(words[nxt]) - overlap[last][nxt]
                if new_cost < dp[new_mask][nxt]:
                    dp[new_mask][nxt] = new_cost
                    parent[new_mask][nxt] = last

    # Find the optimal ending word
    full_mask = (1 << n) - 1
    best_last = min(range(n), key=lambda i: dp[full_mask][i])

    # Reconstruct the order
    order = []
    mask = full_mask
    last = best_last
    while last != -1:
        order.append(last)
        prev = parent[mask][last]
        mask ^= (1 << last)
        last = prev
    order.reverse()

    # Build the result string
    result = words[order[0]]
    for i in range(1, len(order)):
        ov = overlap[order[i - 1]][order[i]]
        result += words[order[i]][ov:]

    return result
```
Time: O(2^n * n^2 + n^2 * L), Space: O(2^n * n).

This is feasible because n <= 12 in the constraints, so 2^12 * 12^2 = about 590,000 operations.

**Dry Run** with `words = ["abc", "bcd", "cde"]`:
```
Overlaps:
  overlap[0][1] = 2 ("abc" -> "bcd", "bc" overlaps)
  overlap[1][2] = 2 ("bcd" -> "cde", "cd" overlaps)
  overlap[0][2] = 1 ("abc" -> "cde", "c" overlaps)
  overlap[2][0] = 0, overlap[1][0] = 0, overlap[2][1] = 0

Best order: 0 -> 1 -> 2
  Start with "abc"
  Add "bcd" with overlap 2: "abc" + "d" = "abcd"
  Add "cde" with overlap 2: "abcd" + "e" = "abcde"

Result: "abcde" (length 5 vs sum of lengths 9)
```

**Edge Cases**: Single word, no overlaps between any words, one word is a substring of another (preprocess to remove contained words).

**Follow-up Questions**:
- What is the time complexity? Why is bitmask DP feasible here?
- How is this related to TSP? (Same structure — minimum cost Hamiltonian path.)
- What if n is larger (n > 20)? (Approximate algorithms: greedy overlap, or shortest common supersequence heuristics.)

---

## Bitmask DP — Deeper Explanation

Bitmask DP is one of the most powerful techniques for problems involving subsets of a small set (n <= 20-23).

**Core Idea**: Represent the "set of items chosen so far" as a bitmask (integer). Bit `i` is set if item `i` has been chosen.

**State**: `dp[mask]` = optimal value when the items in `mask` have been processed.

**Transitions**: For each mask, try adding each item not yet in the mask.

```python
for mask in range(1 << n):
    for i in range(n):
        if mask & (1 << i):
            continue  # already in set
        new_mask = mask | (1 << i)
        dp[new_mask] = optimize(dp[new_mask], dp[mask] + cost_of_adding(i, mask))
```

**When to use**:
- The problem asks for an optimal ordering or subset of <= 20 items.
- The cost of adding an item depends on which items have already been chosen.
- Examples: TSP, scheduling with dependencies, shortest superstring, Hamiltonian path.

**Complexity**: O(2^n * n) states and transitions, times the cost of each transition.

---

## Bit Manipulation in System Design

### Bloom Filters
A probabilistic data structure that can tell you "definitely not in set" or "probably in set".
- Uses a bit array of m bits.
- k hash functions map each element to k positions.
- Insert: set bits at all k positions.
- Query: check if all k bits are set. False positives possible, false negatives impossible.
- Used in: database query optimization, spam filtering, cache checking.

### Feature Flags
```python
FEATURE_DARK_MODE = 1 << 0   # bit 0
FEATURE_NEW_UI    = 1 << 1   # bit 1
FEATURE_BETA      = 1 << 2   # bit 2

user_features = FEATURE_DARK_MODE | FEATURE_BETA  # bits 0 and 2 set

# Check if user has feature
if user_features & FEATURE_DARK_MODE:
    enable_dark_mode()

# Add a feature
user_features |= FEATURE_NEW_UI

# Remove a feature
user_features &= ~FEATURE_BETA
```

### Compact Set Operations
When the universe is small (< 64 elements), use a single integer as a set:
```python
# Union
a | b
# Intersection
a & b
# Difference
a & ~b
# Symmetric difference
a ^ b
# Is subset
(a & b) == a
# Is empty
a == 0
# Size (popcount)
bin(a).count('1')
```

---

## Common Mistakes & Interview Tips

### Mistakes to Avoid
1. **Python's arbitrary precision integers** — Python ints do not overflow, so bit tricks that rely on 32-bit overflow need manual masking (`& 0xFFFFFFFF`).
2. **Signed vs unsigned confusion** — Be clear about whether the problem expects 32-bit unsigned or signed. Python's `>>` is arithmetic (preserves sign bit); use masking for logical right shift.
3. **Off-by-one in bit positions** — Bit 0 is the rightmost (least significant). Bit 31 is the leftmost for 32-bit integers.
4. **Forgetting that `~x` in Python gives `-(x+1)`** — Because Python integers are arbitrary precision, `~5` is `-6`, not the bitwise complement you might expect. Use `x ^ 0xFFFFFFFF` for 32-bit complement.
5. **Modifying the loop variable** — In Kernighan's algorithm, `n &= n - 1` modifies n. Make sure this is intentional.
6. **Bitmask DP with n > 23** — 2^23 is about 8 million. Beyond that, bitmask DP becomes too slow.

### Interview Tips
1. **Know the 10 essential bit tricks by heart** — the ones listed in the cheat sheet above.
2. **Explain the XOR trick** — When you use XOR to find a unique element, explain WHY it works (associativity and self-cancellation).
3. **Draw binary representations** — For bit manipulation problems, write out the binary and trace through the operations step by step.
4. **Mention Kernighan's algorithm by name** — It shows you know the classic techniques.
5. **For bitmask DP, immediately identify the constraint** — If n <= 20, bitmask DP is likely the intended approach.
6. **Connect to practical applications** — Mention bloom filters, feature flags, or Unix permissions to show breadth.
7. **Know the language-specific quirks** — Python's arbitrary precision, Java's `>>>` for unsigned right shift, etc.

---

## Pattern Connections

| Pattern | Connection to Bit Manipulation |
|---------|-------------------------------|
| **Math** | Many number theory problems use bit properties (power of 2, GCD with shifts). |
| **Dynamic Programming** | Bitmask DP is a subset of DP where state is a bitmask. |
| **Backtracking** | Bitmask enumeration is an alternative to recursive subset generation. |
| **Trie** | Bit-level tries are used for maximum XOR problems. |
| **Hash Set** | XOR-based uniqueness detection is an alternative to hash set tracking. |
| **Greedy** | Building XOR results bit by bit (MSB to LSB) is a greedy strategy. |
| **System Design** | Bloom filters, feature flags, compact set encoding. |

### Progression Path
```
Single Number (136) -> Single Number II (137) -> Single Number III (260)
Number of 1 Bits (191) -> Counting Bits (338) -> Reverse Bits (190)
Sum of Two Integers (371) -> Divide Two Integers (29)
Maximum XOR (421) -> Maximum XOR Subarray (via trie)
Subsets (78, bitmask approach) -> Shortest Superstring (943, bitmask DP)
Power of 2 (231) -> Power of 4 (342) -> Bitwise AND of Range (201)
```
