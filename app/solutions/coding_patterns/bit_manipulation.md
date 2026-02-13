# Bit Manipulation Pattern Guide

## 1. What is Bit Manipulation?

### Explain Like I'm 5
Imagine you have a row of light switches. Each switch can be either ON (1) or OFF (0). Bit manipulation is like playing with these switches - you can flip them, check if they're on, or do special tricks like "turn on all switches that are off" or "find the one switch that's different from all others."

When you count in regular numbers (1, 2, 3, 4...), computers actually count using only 0s and 1s:
- 0 = `0000`
- 1 = `0001`
- 2 = `0010`
- 3 = `0011`
- 4 = `0100`
- 5 = `0101`

Bit manipulation lets you work directly with these 0s and 1s to solve problems super fast!

### Technical Definition
Bit manipulation involves performing operations directly on the binary representation of numbers. Instead of treating numbers as decimal values, we work with their underlying binary bits using bitwise operators. This allows for extremely efficient algorithms with O(1) space complexity and often O(1) or O(log n) time complexity for operations that would otherwise require more complex data structures.

## 2. Real-World Analogy

### The Permission Flags System
Think of Unix file permissions (read, write, execute):
- **Read = 4** (binary: `100`)
- **Write = 2** (binary: `010`)
- **Execute = 1** (binary: `001`)

To give read and write permissions: `4 + 2 = 6` (binary: `110`)
To check if someone has write permission: Check if the 2nd bit is set
To remove write permission: Use bit masking

This is exactly how operating systems, game engines, and embedded systems manage flags and states efficiently!

### Another Example: Network Subnet Masks
IP addresses use bit manipulation for subnet masks:
- IP: `192.168.1.100`
- Mask: `255.255.255.0`
- Bitwise AND gives you the network address

## 3. When to Use Bit Manipulation

### Clear Signals
✅ **Use bit manipulation when you see:**
1. **XOR properties needed** - Finding unique elements, missing numbers
2. **Power of 2 operations** - Checking if a number is a power of 2
3. **Set operations** - Union, intersection, difference on sets
4. **Optimization requirements** - Space O(1), very fast operations
5. **Counting bits** - Hamming weight, counting set bits
6. **Even/odd checks** - Quick parity checking
7. **Swapping without temp variable**
8. **Range of numbers is small** - Using bitmasks (e.g., 26 letters)
9. **Multiple boolean flags** - Compact storage
10. **Binary representation matters** - Bit reversal, Gray code

### Keywords to Watch For
- "Find the single/unique element"
- "All elements appear twice except one"
- "Power of two"
- "Count number of 1s/0s"
- "Missing number in sequence"
- "XOR properties"
- "Subset generation"
- "Minimal space complexity"

## 4. The Problems

### Problem 1: Single Number (LeetCode #136)
**Given:** Array where every element appears twice except one
**Find:** The single element
**Example:** `[4, 1, 2, 1, 2]` → `4`

### Problem 2: Number of 1 Bits (LeetCode #191)
**Given:** An integer
**Find:** Number of '1' bits (Hamming weight)
**Example:** `11` (binary: `1011`) → `3`

### Problem 3: Power of Two (LeetCode #231)
**Given:** An integer n
**Find:** Is it a power of 2?
**Example:** `16` → `true`, `18` → `false`

## 5. Brute Force Approaches

### Problem 1: Single Number - Using HashMap
```python
def singleNumber_bruteforce(nums):
    """
    Time: O(n), Space: O(n)
    Uses extra space to count occurrences
    """
    count = {}

    # Count occurrences of each number
    for num in nums:
        count[num] = count.get(num, 0) + 1

    # Find the number that appears once
    for num, freq in count.items():
        if freq == 1:
            return num

    return -1

# Example
nums = [4, 1, 2, 1, 2]
print(singleNumber_bruteforce(nums))  # Output: 4
```

### Problem 2: Number of 1 Bits - Division Method
```python
def hammingWeight_bruteforce(n):
    """
    Time: O(log n), Space: O(1)
    Converts to binary string and counts '1's
    """
    count = 0
    while n > 0:
        if n % 2 == 1:  # Check if last digit is 1
            count += 1
        n = n // 2  # Remove last digit
    return count

# Example
print(hammingWeight_bruteforce(11))  # Binary: 1011 → Output: 3
```

### Problem 3: Power of Two - Repeated Division
```python
def isPowerOfTwo_bruteforce(n):
    """
    Time: O(log n), Space: O(1)
    Keep dividing by 2 until we can't
    """
    if n <= 0:
        return False

    while n > 1:
        if n % 2 != 0:  # Not divisible by 2
            return False
        n = n // 2

    return True

# Examples
print(isPowerOfTwo_bruteforce(16))  # Output: True
print(isPowerOfTwo_bruteforce(18))  # Output: False
```

## 6. Optimized Solutions with Bit Manipulation

### Problem 1: Single Number - XOR Trick
```python
def singleNumber(nums):
    """
    Time: O(n), Space: O(1)

    XOR Properties:
    - a ^ a = 0 (any number XOR itself is 0)
    - a ^ 0 = a (any number XOR 0 is itself)
    - XOR is commutative and associative

    Example: [4, 1, 2, 1, 2]
    Step by step:
    0 ^ 4 = 4     (binary: 0000 ^ 0100 = 0100)
    4 ^ 1 = 5     (binary: 0100 ^ 0001 = 0101)
    5 ^ 2 = 7     (binary: 0101 ^ 0010 = 0111)
    7 ^ 1 = 6     (binary: 0111 ^ 0001 = 0110)
    6 ^ 2 = 4     (binary: 0110 ^ 0010 = 0100)

    All pairs cancel out (1^1=0, 2^2=0), leaving only 4!
    """
    result = 0
    for num in nums:
        result ^= num  # XOR all numbers together
    return result

# Example
nums = [4, 1, 2, 1, 2]
print(singleNumber(nums))  # Output: 4

# Visual breakdown:
#   4: 0100
#   1: 0001
#   2: 0010
#   1: 0001
#   2: 0010
# XOR: 0100 (which is 4)
```

### Problem 2: Number of 1 Bits - Brian Kernighan's Algorithm
```python
def hammingWeight(n):
    """
    Time: O(k) where k = number of 1 bits, Space: O(1)

    Key Insight: n & (n-1) removes the rightmost 1 bit

    Example with n = 11 (binary: 1011):

    Iteration 1:
    n     = 1011 (11)
    n-1   = 1010 (10)
    n&(n-1) = 1010 (10)  → Removed rightmost 1

    Iteration 2:
    n     = 1010 (10)
    n-1   = 1001 (9)
    n&(n-1) = 1000 (8)   → Removed rightmost 1

    Iteration 3:
    n     = 1000 (8)
    n-1   = 0111 (7)
    n&(n-1) = 0000 (0)   → Removed rightmost 1

    Count = 3 (three 1 bits)
    """
    count = 0
    while n:
        n &= (n - 1)  # Remove the rightmost 1 bit
        count += 1
    return count

# Alternative method - checking each bit
def hammingWeight_alternative(n):
    """
    Check each bit position using bit mask
    """
    count = 0
    while n:
        count += n & 1  # Check if rightmost bit is 1
        n >>= 1         # Right shift to check next bit
    return count

# Example
print(hammingWeight(11))  # Output: 3
print(hammingWeight_alternative(11))  # Output: 3
```

### Problem 3: Power of Two - Single Bit Check
```python
def isPowerOfTwo(n):
    """
    Time: O(1), Space: O(1)

    Key Insight: Power of 2 has exactly one 1 bit
    - 1  = 0001 (2^0)
    - 2  = 0010 (2^1)
    - 4  = 0100 (2^2)
    - 8  = 1000 (2^3)
    - 16 = 10000 (2^4)

    For power of 2:
    n     = 1000 (8)
    n-1   = 0111 (7)
    n&(n-1) = 0000 (0)  → Result is 0!

    For non-power of 2:
    n     = 1010 (10)
    n-1   = 1001 (9)
    n&(n-1) = 1000 (8)  → Result is NOT 0

    Also check n > 0 to handle negative numbers and zero
    """
    return n > 0 and (n & (n - 1)) == 0

# Examples with binary visualization
test_cases = [1, 2, 4, 8, 16, 3, 6, 10, 0, -4]
for num in test_cases:
    result = isPowerOfTwo(num)
    binary = bin(num) if num > 0 else "N/A"
    print(f"{num:3d} ({binary:>8s}): {result}")

# Output:
#   1 (   0b1): True
#   2 (  0b10): True
#   4 ( 0b100): True
#   8 (0b1000): True
#  16 (0b10000): True
#   3 (  0b11): False
#   6 ( 0b110): False
#  10 (0b1010): False
#   0 (    N/A): False
#  -4 (    N/A): False
```

### Bonus Problem: Reverse Bits (LeetCode #190)
```python
def reverseBits(n):
    """
    Time: O(32) = O(1), Space: O(1)

    Reverse the bits of a 32-bit unsigned integer

    Example: n = 43261596 (binary: 00000010100101000001111010011100)
    Reversed: 964176192 (binary: 00111001011110000010100101000000)

    Strategy: Extract each bit from right, add to result from left
    """
    result = 0
    for i in range(32):
        # Extract the rightmost bit of n
        bit = n & 1

        # Add this bit to the leftmost position of result
        result = (result << 1) | bit

        # Move to next bit in n
        n >>= 1

    return result

# Example with smaller number for visualization
def reverseBits_visual(n, num_bits=8):
    """8-bit example for clarity"""
    print(f"Original: {n:3d} = {bin(n)[2:].zfill(num_bits)}")
    result = 0
    for i in range(num_bits):
        bit = n & 1
        result = (result << 1) | bit
        n >>= 1
        print(f"Step {i+1}: bit={bit}, result={bin(result)[2:].zfill(i+1)}")
    print(f"Reversed: {result:3d} = {bin(result)[2:].zfill(num_bits)}")
    return result

# Example: reverse 8-bit number 29 (00011101)
# Expected result: 184 (10111000)
reverseBits_visual(29, 8)
```

## 7. Time & Space Complexity Analysis

### Comparison Table

| Problem | Brute Force Time | Brute Force Space | Optimized Time | Optimized Space | Improvement |
|---------|------------------|-------------------|----------------|-----------------|-------------|
| Single Number | O(n) | O(n) | O(n) | O(1) | Space: n → 1 |
| Hamming Weight | O(log n) | O(1) | O(k)* | O(1) | Time: log n → k |
| Power of Two | O(log n) | O(1) | O(1) | O(1) | Time: log n → 1 |
| Reverse Bits | O(n) | O(1) | O(1) | O(1) | Time: n → 32 |

*k = number of set bits (1s), k ≤ log n

### Detailed Analysis

#### Single Number
- **Brute Force**: HashMap stores all unique numbers → O(n) space
- **Optimized**: XOR operation accumulates in single variable → O(1) space
- **Why Better**: No extra memory, same linear time, cache-friendly

#### Hamming Weight
- **Brute Force**: Checks every bit position (32 iterations for 32-bit int)
- **Optimized**: Only iterates for each 1 bit (sparse numbers are faster)
- **Example**: Number with 3 set bits → only 3 iterations instead of 32

#### Power of Two
- **Brute Force**: Repeatedly divides by 2 until reaching 1 or odd number
- **Optimized**: Single bitwise AND operation
- **Why Better**: O(1) constant time vs O(log n) divisions

## 8. Bit Operations Cheat Sheet

### Basic Bitwise Operators

```python
# AND (&) - Both bits must be 1
#   1010 (10)
# & 1100 (12)
# ------
#   1000 (8)
print(10 & 12)  # Output: 8

# OR (|) - At least one bit must be 1
#   1010 (10)
# | 1100 (12)
# ------
#   1110 (14)
print(10 | 12)  # Output: 14

# XOR (^) - Bits must be different
#   1010 (10)
# ^ 1100 (12)
# ------
#   0110 (6)
print(10 ^ 12)  # Output: 6

# NOT (~) - Flip all bits (includes sign bit)
# ~1010 = ...11110101 (two's complement)
print(~10)  # Output: -11

# Left Shift (<<) - Multiply by 2^n
#   0101 (5)
# << 2
# ------
#   010100 (20)
print(5 << 2)  # Output: 20 (5 * 2^2 = 5 * 4)

# Right Shift (>>) - Divide by 2^n (integer division)
#   1010 (10)
# >> 2
# ------
#   0010 (2)
print(10 >> 2)  # Output: 2 (10 // 2^2 = 10 // 4)
```

### Essential Bit Manipulation Tricks

```python
# 1. Check if bit at position i is set (1)
def is_bit_set(num, i):
    """Check if i-th bit from right is 1"""
    return (num & (1 << i)) != 0

# Example: Is 3rd bit of 10 (1010) set?
print(is_bit_set(10, 3))  # True (1010 has 1 at position 3)
print(is_bit_set(10, 2))  # False (1010 has 0 at position 2)


# 2. Set bit at position i to 1
def set_bit(num, i):
    """Set i-th bit to 1"""
    return num | (1 << i)

# Example: Set 2nd bit of 10 (1010) → 1110 (14)
print(set_bit(10, 2))  # Output: 14


# 3. Clear bit at position i (set to 0)
def clear_bit(num, i):
    """Set i-th bit to 0"""
    return num & ~(1 << i)

# Example: Clear 3rd bit of 10 (1010) → 0010 (2)
print(clear_bit(10, 3))  # Output: 2


# 4. Toggle bit at position i
def toggle_bit(num, i):
    """Flip i-th bit"""
    return num ^ (1 << i)

# Example: Toggle 2nd bit of 10 (1010) → 1110 (14)
print(toggle_bit(10, 2))  # Output: 14


# 5. Get rightmost set bit
def rightmost_set_bit(num):
    """Get position of rightmost 1 bit"""
    return num & -num

# Example: 12 (1100) → rightmost set bit is at position 2 → 0100 (4)
print(rightmost_set_bit(12))  # Output: 4


# 6. Clear rightmost set bit
def clear_rightmost_set_bit(num):
    """Remove rightmost 1"""
    return num & (num - 1)

# Example: 12 (1100) → 8 (1000)
print(clear_rightmost_set_bit(12))  # Output: 8


# 7. Check if even or odd
def is_even(num):
    """Check if number is even using bit check"""
    return (num & 1) == 0

print(is_even(10))  # True
print(is_even(11))  # False


# 8. Multiply by power of 2
def multiply_by_power_of_2(num, power):
    """Multiply num by 2^power"""
    return num << power

print(multiply_by_power_of_2(5, 3))  # 5 * 8 = 40


# 9. Divide by power of 2
def divide_by_power_of_2(num, power):
    """Divide num by 2^power"""
    return num >> power

print(divide_by_power_of_2(40, 3))  # 40 // 8 = 5


# 10. Swap two numbers without temp variable
def swap(a, b):
    """Swap using XOR"""
    print(f"Before: a={a}, b={b}")
    a = a ^ b  # a now contains XOR of both
    b = a ^ b  # b = (a^b)^b = a
    a = a ^ b  # a = (a^b)^a = b
    print(f"After: a={a}, b={b}")
    return a, b

swap(5, 10)


# 11. Get all subsets using bits
def get_all_subsets(nums):
    """
    Generate all subsets using bit manipulation
    For n elements, there are 2^n subsets
    Each bit pattern represents a subset
    """
    n = len(nums)
    subsets = []

    # Iterate through all possible bit patterns
    for i in range(1 << n):  # 2^n combinations
        subset = []
        for j in range(n):
            # Check if j-th bit is set
            if i & (1 << j):
                subset.append(nums[j])
        subsets.append(subset)

    return subsets

# Example: [1, 2, 3]
# 000 → []
# 001 → [1]
# 010 → [2]
# 011 → [1, 2]
# 100 → [3]
# 101 → [1, 3]
# 110 → [2, 3]
# 111 → [1, 2, 3]
print(get_all_subsets([1, 2, 3]))


# 12. Count bits needed to convert A to B
def bits_to_flip(a, b):
    """
    Count how many bits differ between two numbers
    Strategy: XOR gives different bits, then count 1s
    """
    xor = a ^ b
    count = 0
    while xor:
        count += xor & 1
        xor >>= 1
    return count

# Example: 29 (11101) vs 15 (01111)
# XOR:     10010 → 2 bits different
print(bits_to_flip(29, 15))  # Output: 2


# 13. Check if number is power of 4
def is_power_of_4(n):
    """
    Power of 4 conditions:
    1. Must be power of 2: n & (n-1) == 0
    2. The single 1 bit must be at even position (0, 2, 4, 6...)
    3. Use mask 0x55555555 = 01010101... (1s at even positions)
    """
    return n > 0 and (n & (n - 1)) == 0 and (n & 0x55555555) != 0

# Examples:
# 4  = 0100 (bit at position 2) → True
# 8  = 1000 (bit at position 3) → False
# 16 = 10000 (bit at position 4) → True
print(is_power_of_4(4))   # True
print(is_power_of_4(8))   # False
print(is_power_of_4(16))  # True


# 14. Get absolute value without branching
def absolute(n):
    """
    Get absolute value using bit manipulation
    Works by creating mask from sign bit
    """
    mask = n >> 31  # All 1s if negative, all 0s if positive
    return (n + mask) ^ mask

print(absolute(-10))  # Output: 10
print(absolute(10))   # Output: 10


# 15. Find missing number in sequence 0 to n
def missingNumber(nums):
    """
    XOR all numbers 0 to n with array elements
    All pairs cancel out, leaving missing number
    """
    missing = len(nums)
    for i, num in enumerate(nums):
        missing ^= i ^ num
    return missing

# Example: [0, 1, 3] → missing 2
print(missingNumber([0, 1, 3]))  # Output: 2
```

### Bitmask Patterns for Sets

```python
# Using integers as sets (for small ranges, e.g., lowercase letters)

class BitSet:
    """Set operations using bit manipulation"""

    def __init__(self):
        self.bits = 0

    def add(self, x):
        """Add element x to set"""
        self.bits |= (1 << x)

    def remove(self, x):
        """Remove element x from set"""
        self.bits &= ~(1 << x)

    def contains(self, x):
        """Check if x is in set"""
        return (self.bits & (1 << x)) != 0

    def union(self, other):
        """Union of two sets"""
        result = BitSet()
        result.bits = self.bits | other.bits
        return result

    def intersection(self, other):
        """Intersection of two sets"""
        result = BitSet()
        result.bits = self.bits & other.bits
        return result

    def difference(self, other):
        """Elements in this set but not in other"""
        result = BitSet()
        result.bits = self.bits & ~other.bits
        return result

    def size(self):
        """Count elements in set"""
        count = 0
        bits = self.bits
        while bits:
            count += bits & 1
            bits >>= 1
        return count

    def to_list(self):
        """Convert to list of elements"""
        elements = []
        for i in range(32):
            if self.bits & (1 << i):
                elements.append(i)
        return elements

# Example usage
s1 = BitSet()
s1.add(1)
s1.add(3)
s1.add(5)
print(s1.to_list())  # [1, 3, 5]

s2 = BitSet()
s2.add(3)
s2.add(5)
s2.add(7)

s3 = s1.union(s2)
print(s3.to_list())  # [1, 3, 5, 7]

s4 = s1.intersection(s2)
print(s4.to_list())  # [3, 5]
```

## 9. Pro Tips for Senior Engineers

### When to Use Bit Manipulation

✅ **Good Use Cases:**
1. **Performance-critical code** - Game engines, embedded systems
2. **Space-constrained environments** - Mobile apps, IoT devices
3. **Algorithmic competitions** - LeetCode, Codeforces
4. **Low-level system programming** - Device drivers, kernel code
5. **Cryptography** - Hashing, encoding operations
6. **Network programming** - IP address manipulation, protocol flags
7. **Compression algorithms** - Huffman coding, run-length encoding

❌ **When to Avoid:**
1. **Business logic** - Readability matters more than microseconds
2. **Maintainability concerns** - Team unfamiliar with bit tricks
3. **No performance bottleneck** - Premature optimization is evil
4. **Complex operations** - When high-level abstractions are clearer

### Readability Considerations

```python
# ❌ BAD: Cryptic one-liner
def mystery(n):
    return n & -n

# ✅ GOOD: Documented and clear
def get_rightmost_set_bit(num):
    """
    Returns a number with only the rightmost set bit of num.

    Example: 12 (1100) → 4 (0100)

    How it works:
    - -num in two's complement flips all bits and adds 1
    - ANDing with original preserves only rightmost 1 bit
    """
    return num & -num

# ✅ BETTER: Provide alternative for clarity
def get_rightmost_set_bit_verbose(num):
    """Alternative implementation for understanding"""
    if num == 0:
        return 0

    position = 0
    while (num & 1) == 0:
        num >>= 1
        position += 1

    return 1 << position
```

### Performance Notes

1. **Bit operations are fast but not magic**
   - Modern compilers optimize regular operations too
   - CPU cache misses matter more than bit tricks
   - Profile before optimizing!

2. **Integer size matters**
   - Python integers are arbitrary precision (slower than C)
   - For performance, consider using `numpy` or `ctypes`
   - JavaScript only has 53-bit safe integers

3. **Use bit manipulation for:**
   - Flags and permissions (32+ booleans in one int)
   - Fast modulo by power of 2: `n % 8 == n & 7`
   - Quick multiply/divide by power of 2
   - Set operations on small domains

### Code Review Red Flags

```python
# 🚩 RED FLAG: No comments on complex bit operations
def weird_func(x):
    return x & (x - 1)

# ✅ BETTER: Explain the trick
def is_power_of_two_or_zero(x):
    """
    Returns True if x is 0 or a power of 2.
    Uses the property that x & (x-1) clears the rightmost set bit.
    Powers of 2 have only one bit set, so result is 0.
    """
    return x & (x - 1) == 0


# 🚩 RED FLAG: Bit manipulation when there's a clearer way
def is_odd_bitwise(n):
    return n & 1

# ✅ BETTER: Use clear idiom for simple operations
def is_odd(n):
    return n % 2 == 1  # Everyone understands this


# 🚩 RED FLAG: Platform-dependent bit operations
def some_func(x):
    return x >> 32  # Assumes 64-bit integers

# ✅ BETTER: Document assumptions
def extract_upper_32_bits(x):
    """
    Extracts upper 32 bits of a 64-bit integer.
    Requires: Python 3 (arbitrary precision) or 64-bit system.
    """
    return (x >> 32) & 0xFFFFFFFF
```

## 10. Problem Recognition

### Instant Recognition Keywords

When you see these phrases in a problem, think bit manipulation:

1. **"All elements appear twice except one"** → XOR pattern
2. **"Power of two"** → Single bit check: `n & (n-1) == 0`
3. **"Count the number of 1 bits"** → Brian Kernighan's algorithm
4. **"Missing number in sequence"** → XOR all numbers
5. **"Subsets"** → Bit masking for all combinations
6. **"O(1) space"** + "linear time" → Likely needs bit tricks
7. **"Without using extra space"** → XOR or bit flags
8. **"Swap without temp variable"** → XOR swap
9. **"Check if bit is set"** → Bit masking
10. **"Count differences between numbers"** → XOR + count bits

### Pattern Matching

| Problem Pattern | Bit Technique | Time | Space |
|----------------|---------------|------|-------|
| Find unique in duplicates | XOR all elements | O(n) | O(1) |
| Count set bits | Brian Kernighan | O(k) | O(1) |
| Power of 2/4 check | `n & (n-1)` | O(1) | O(1) |
| Missing number | XOR with indices | O(n) | O(1) |
| All subsets | Iterate 2^n masks | O(n·2^n) | O(1) |
| Even/odd check | Check LSB: `n & 1` | O(1) | O(1) |
| Multiply by 2^k | Left shift: `n << k` | O(1) | O(1) |
| Divide by 2^k | Right shift: `n >> k` | O(1) | O(1) |
| Reverse bits | Shift and build | O(32) | O(1) |
| Bit difference count | XOR + count bits | O(k) | O(1) |

## 11. Practice Problems

### Beginner Level
1. **Reverse Bits** (LeetCode #190)
   - Reverse bits of a 32-bit unsigned integer
   - Good for: Understanding bit shifting and building

2. **Missing Number** (LeetCode #268)
   - Find missing number in array containing 0 to n
   - Good for: XOR properties

3. **Power of Four** (LeetCode #342)
   - Check if number is power of four
   - Good for: Combining bit tricks

### Intermediate Level
4. **Single Number II** (LeetCode #137)
   - Every element appears 3 times except one
   - Good for: Advanced bit counting

5. **Sum of Two Integers** (LeetCode #371)
   - Add two integers without using + or - operators
   - Good for: Understanding carry with XOR and AND

6. **Bitwise AND of Numbers Range** (LeetCode #201)
   - Find bitwise AND of all numbers in range [left, right]
   - Good for: Bit pattern recognition

7. **Counting Bits** (LeetCode #338)
   - Count set bits for all numbers 0 to n
   - Good for: Dynamic programming + bits

### Advanced Level
8. **Maximum XOR of Two Numbers** (LeetCode #421)
   - Find maximum XOR of two numbers in array
   - Good for: Trie + bit manipulation

9. **Single Number III** (LeetCode #260)
   - Two elements appear once, others appear twice
   - Good for: Complex XOR partitioning

10. **Minimum Flips to Make a OR b Equal c** (LeetCode #1318)
    - Bit manipulation with conditions
    - Good for: Practical bit operations

### Expert Level
11. **Gray Code** (LeetCode #89)
    - Generate n-bit Gray code sequence
    - Good for: Bit sequence patterns

12. **UTF-8 Validation** (LeetCode #393)
    - Validate UTF-8 encoding using bit patterns
    - Good for: Real-world bit manipulation

## 12. Common Mistakes

### Mistake 1: Forgetting Negative Numbers
```python
# ❌ WRONG: Doesn't handle negatives
def count_bits_wrong(n):
    count = 0
    while n > 0:  # Infinite loop if n is negative!
        count += n & 1
        n >>= 1
    return count

# ✅ CORRECT: Handle negatives or specify unsigned
def count_bits(n):
    """Count set bits in 32-bit unsigned integer"""
    if n < 0:
        # In Python, convert to 32-bit unsigned
        n = n & 0xFFFFFFFF

    count = 0
    while n:
        count += n & 1
        n >>= 1
    return count
```

### Mistake 2: Operator Precedence
```python
# ❌ WRONG: Precedence issue
if n & 1 == 0:  # Parsed as: n & (1 == 0) → n & False → 0
    print("Even")

# ✅ CORRECT: Use parentheses
if (n & 1) == 0:
    print("Even")

# Common precedence errors:
# Comparison operators (==, <, >) have HIGHER precedence than bitwise (&, |, ^)
# Always use parentheses with bit operations in conditions!
```

### Mistake 3: Integer Overflow (Language-Dependent)
```python
# Python: No overflow (arbitrary precision)
x = 1 << 100  # Works fine in Python

# JavaScript: Only 53-bit safe integers
# C/C++/Java: Fixed-width integers overflow

# ✅ GOOD: Document integer size assumptions
def safe_left_shift(n, shift):
    """
    Left shift with overflow check for 32-bit integers.
    Returns None if result would overflow.
    """
    if shift >= 32 or n >= (1 << (32 - shift)):
        return None  # Would overflow
    return n << shift
```

### Mistake 4: Not Considering All Bits
```python
# ❌ WRONG: Only checks lower bits
def is_power_of_two_wrong(n):
    return (n & (n - 1)) == 0  # True for 0 too!

# ✅ CORRECT: Check positive first
def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0
```

### Mistake 5: Overcomplicating Simple Operations
```python
# ❌ WRONG: Bit manipulation for the sake of it
def is_even_complicated(n):
    return ~n & 1  # Confusing!

# ✅ CORRECT: Use clear idioms
def is_even(n):
    return n % 2 == 0  # Everyone understands this

# Use bit manipulation when there's a REAL benefit:
# - Performance critical code
# - Space optimization needed
# - Algorithm inherently requires bits (XOR for unique element)
```

### Mistake 6: Not Testing Edge Cases
```python
# Common edge cases to test:
test_cases = [
    0,           # Zero
    1,           # Smallest positive
    -1,          # All bits set (two's complement: 11111111...)
    2**31 - 1,   # Max 32-bit signed int
    -2**31,      # Min 32-bit signed int
    2**32 - 1,   # Max 32-bit unsigned int
]

def test_function(func):
    for test in test_cases:
        try:
            result = func(test)
            print(f"{func.__name__}({test}) = {result}")
        except Exception as e:
            print(f"{func.__name__}({test}) raised {e}")
```

### Mistake 7: Mixing Signed and Unsigned
```python
# ❌ WRONG: Confusion about sign
def reverse_bits_wrong(n):
    # Python right shift (>>) is arithmetic for negatives
    # May not work as expected
    result = 0
    for _ in range(32):
        result <<= 1
        result |= n & 1
        n >>= 1  # Problem if n is negative!
    return result

# ✅ CORRECT: Ensure unsigned behavior
def reverse_bits(n):
    # Mask to ensure 32-bit unsigned
    n = n & 0xFFFFFFFF
    result = 0
    for _ in range(32):
        result <<= 1
        result |= n & 1
        n >>= 1
    return result
```

### Mistake 8: Not Documenting Bit Tricks
```python
# ❌ WRONG: No explanation
def solve(n):
    return (n & -n).bit_length() - 1

# ✅ CORRECT: Explain the magic
def get_rightmost_set_bit_position(n):
    """
    Returns the 0-indexed position of the rightmost set bit.

    Example: 12 (binary: 1100)
    - n & -n = 4 (binary: 0100) isolates rightmost bit
    - bit_length() = 3 (needs 3 bits to represent 4)
    - Subtract 1 to get 0-indexed position = 2

    Args:
        n: Positive integer

    Returns:
        Position of rightmost 1 bit (0-indexed from right)
    """
    if n == 0:
        return -1  # No set bits
    return (n & -n).bit_length() - 1

# Example: 12 (1100) has rightmost bit at position 2
print(get_rightmost_set_bit_position(12))  # Output: 2
```

---

## Summary

Bit manipulation is a powerful technique for writing efficient, space-optimized algorithms. The key is recognizing when to use it:

1. **XOR** for finding unique elements and canceling pairs
2. **AND** with powers of 2 for checking specific bits
3. **n & (n-1)** for removing rightmost 1 bit
4. **Shifts** for fast multiplication/division by powers of 2
5. **Bitmasks** for compact set operations

Remember: **Clarity beats cleverness.** Use bit manipulation when it provides clear benefits, but always prioritize readable, maintainable code. Document your bit tricks thoroughly!

### Quick Reference Card

| Operation | Code | Use Case |
|-----------|------|----------|
| Check bit | `n & (1 << i)` | Test if i-th bit is set |
| Set bit | `n \| (1 << i)` | Set i-th bit to 1 |
| Clear bit | `n & ~(1 << i)` | Set i-th bit to 0 |
| Toggle bit | `n ^ (1 << i)` | Flip i-th bit |
| Check power of 2 | `n > 0 and n & (n-1) == 0` | Single bit set |
| Get rightmost 1 | `n & -n` | Isolate lowest bit |
| Clear rightmost 1 | `n & (n-1)` | Remove lowest bit |
| Check even/odd | `n & 1` | LSB tells parity |
| Multiply by 2^k | `n << k` | Fast multiplication |
| Divide by 2^k | `n >> k` | Fast division |

Happy bit hacking! 🚀
