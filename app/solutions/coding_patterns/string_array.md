# String/Array Manipulation Pattern Guide

## What is String/Array Manipulation?

### Explain Like I'm 5
Imagine you have a box of colorful building blocks (an array) or a string of beads (a string). String/Array manipulation is like playing with these blocks or beads - you can:
- Rearrange them in different orders
- Find matching pairs
- Group similar ones together
- Remove some and keep others
- Make new patterns from existing ones

Just like how you can organize your toys in different ways, we organize data in strings and arrays to solve problems!

### Technical Definition
String/Array Manipulation encompasses algorithms and techniques for efficiently transforming, analyzing, and processing sequential data structures. This pattern involves operations such as:
- **Searching**: Finding elements or patterns within sequences
- **Transformation**: Modifying elements or structure (reversing, rotating, sorting)
- **Comparison**: Analyzing relationships between elements
- **Aggregation**: Combining or grouping elements based on criteria
- **In-place modifications**: Changing data without extra memory allocation

## Real-World Analogy

### 📚 Library Book Organization
Think of a library where books (array elements) need to be:
- **Sorted alphabetically** → Sorting algorithms
- **Grouped by genre** → Grouping/hashing patterns
- **Finding all books by an author** → Filtering/searching
- **Removing duplicates** → Deduplication algorithms

### 🎨 Paint Mixing
When mixing colors (array elements):
- **Combining adjacent colors** → Sliding window
- **Finding complementary pairs** → Two pointers
- **Creating new shades** → Transformation operations

## When to Use This Pattern

### Clear Signals
✅ Use String/Array Manipulation when you see:
- Problems involving contiguous sequences of data
- Need to find patterns, duplicates, or groups
- Questions about anagrams, palindromes, or string matching
- "Given an array/string..." in problem statement
- Operations on characters, words, or numeric sequences
- Requirements to modify or analyze sequential data

### Problem Keywords
- "contiguous subarray"
- "anagram"
- "palindrome"
- "rotation"
- "in-place"
- "without extra space"
- "group by..."
- "product except self"
- "valid..."
- "substring/subarray"

## The Problems

Let's explore three classic problems that demonstrate different String/Array manipulation techniques.

### Problem 1: Group Anagrams
**Difficulty**: Medium
**Category**: String Grouping/Hashing

```
Given an array of strings, group all anagrams together.

Input: strs = ["eat","tea","tan","ate","nat","bat"]
Output: [["bat"],["nat","tan"],["ate","eat","tea"]]

Explanation:
- "eat", "tea", "ate" are anagrams (same letters, different order)
- "tan", "nat" are anagrams
- "bat" is alone
```

### Problem 2: Product of Array Except Self
**Difficulty**: Medium
**Category**: Array Transformation

```
Given an integer array nums, return an array answer such that answer[i]
is equal to the product of all elements of nums except nums[i].

Input: nums = [1,2,3,4]
Output: [24,12,8,6]

Explanation:
- answer[0] = 2*3*4 = 24
- answer[1] = 1*3*4 = 12
- answer[2] = 1*2*4 = 8
- answer[3] = 1*2*3 = 6

Constraint: Cannot use division, must run in O(n) time
```

### Problem 3: Valid Palindrome
**Difficulty**: Easy
**Category**: String Validation

```
Given a string s, return true if it is a palindrome, false otherwise.
Only consider alphanumeric characters and ignore case.

Input: s = "A man, a plan, a canal: Panama"
Output: true

Explanation: "amanaplanacanalpanama" reads the same forwards and backwards
```

## Brute Force Approaches

### Problem 1: Group Anagrams - Brute Force

```python
def groupAnagrams_bruteforce(strs):
    """
    Brute Force: Compare every string with every other string
    Time: O(n² * m log m) where n = number of strings, m = average string length
    Space: O(n * m) for storing results
    """
    result = []
    used = set()  # Track which strings we've already grouped

    for i in range(len(strs)):
        # Skip if already grouped
        if i in used:
            continue

        # Start a new group with current string
        current_group = [strs[i]]
        used.add(i)

        # Compare with all remaining strings
        for j in range(i + 1, len(strs)):
            if j in used:
                continue

            # Check if strs[i] and strs[j] are anagrams
            # by sorting both and comparing
            if sorted(strs[i]) == sorted(strs[j]):
                current_group.append(strs[j])
                used.add(j)

        result.append(current_group)

    return result

# Test
print(groupAnagrams_bruteforce(["eat","tea","tan","ate","nat","bat"]))
# Output: [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
```

**Why it's inefficient:**
- We compare each string with every other string (nested loops)
- We sort strings multiple times (same string might be sorted repeatedly)
- No reuse of computed information

### Problem 2: Product of Array Except Self - Brute Force

```python
def productExceptSelf_bruteforce(nums):
    """
    Brute Force: For each position, multiply all other elements
    Time: O(n²) - nested loops
    Space: O(1) - excluding output array
    """
    n = len(nums)
    result = []

    for i in range(n):
        product = 1

        # Multiply all elements except nums[i]
        for j in range(n):
            if i != j:  # Skip the current index
                product *= nums[j]

        result.append(product)

    return result

# Test
print(productExceptSelf_bruteforce([1, 2, 3, 4]))
# Output: [24, 12, 8, 6]
```

**Why it's inefficient:**
- We recalculate products from scratch for each position
- O(n²) time complexity doesn't scale well
- Lots of redundant multiplications

### Problem 3: Valid Palindrome - Brute Force

```python
def isPalindrome_bruteforce(s):
    """
    Brute Force: Create cleaned string, then create reversed version
    Time: O(n)
    Space: O(n) - creating new strings
    """
    # Step 1: Remove non-alphanumeric and convert to lowercase
    cleaned = ""
    for char in s:
        if char.isalnum():
            cleaned += char.lower()

    # Step 2: Create reversed version
    reversed_str = ""
    for i in range(len(cleaned) - 1, -1, -1):
        reversed_str += cleaned[i]

    # Step 3: Compare
    return cleaned == reversed_str

# Test
print(isPalindrome_bruteforce("A man, a plan, a canal: Panama"))
# Output: True
```

**Why it's not optimal:**
- Creates two extra strings (cleaned and reversed)
- String concatenation in Python creates new strings each time (inefficient)
- Uses O(n) extra space when we could use O(1)

## Optimized Solutions

### Problem 1: Group Anagrams - Optimized (Hash Map with Sorted Key)

```python
def groupAnagrams(strs):
    """
    Optimized: Use hash map where key = sorted string (anagram signature)

    Key Insight: All anagrams produce the same sorted string
    - "eat" → "aet"
    - "tea" → "aet"  (same key!)
    - "ate" → "aet"  (same key!)

    Time: O(n * m log m) where n = number of strings, m = avg length
          - We iterate through n strings once
          - Sorting each string takes O(m log m)

    Space: O(n * m) for storing all strings in hash map
    """
    from collections import defaultdict

    # Dictionary where key = sorted string, value = list of anagrams
    anagram_map = defaultdict(list)

    for string in strs:
        # Create a canonical form (sorted) as the key
        # All anagrams will have the same sorted form
        sorted_str = ''.join(sorted(string))

        # Group strings with the same sorted form together
        anagram_map[sorted_str].append(string)

    # Return all grouped anagrams as a list
    return list(anagram_map.values())

# Test
print(groupAnagrams(["eat","tea","tan","ate","nat","bat"]))
# Output: [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
```

**Alternative: Character Count as Key (Even Better for Large Strings)**

```python
def groupAnagrams_charcount(strs):
    """
    Alternative Optimized: Use character frequency as key

    Time: O(n * m) - better than sorting approach!
          - n strings, m characters per string
          - Counting is O(m), no sorting needed

    Space: O(n * m)
    """
    from collections import defaultdict

    anagram_map = defaultdict(list)

    for string in strs:
        # Create a count array for 26 lowercase letters
        # This serves as a unique signature for each anagram group
        count = [0] * 26

        for char in string:
            # Increment count for this character
            # ord(char) - ord('a') gives position (a=0, b=1, etc.)
            count[ord(char) - ord('a')] += 1

        # Convert list to tuple (lists aren't hashable)
        # e.g., "eat" → (1,0,0,0,1,0,...,1,0,0)
        key = tuple(count)

        anagram_map[key].append(string)

    return list(anagram_map.values())

# Test
print(groupAnagrams_charcount(["eat","tea","tan","ate","nat","bat"]))
```

**Why it's better:**
- Single pass through array (O(n) instead of O(n²))
- Hash map lookup is O(1) on average
- No redundant comparisons

### Problem 2: Product of Array Except Self - Optimized (Prefix/Suffix Pattern)

```python
def productExceptSelf(nums):
    """
    Optimized: Use prefix and suffix products

    Key Insight:
    For any index i, result[i] = (product of all left elements) * (product of all right elements)

    Example: [1, 2, 3, 4]
    Position 2 (value=3):
    - Left product: 1 * 2 = 2
    - Right product: 4 = 4
    - Result[2] = 2 * 4 = 8 ✓

    Time: O(n) - three separate O(n) passes
    Space: O(1) - excluding output array (we use it for computation)
    """
    n = len(nums)
    result = [1] * n  # Initialize with 1s

    # Step 1: Build prefix products (left to right)
    # result[i] will contain product of all elements to the left of i
    prefix = 1
    for i in range(n):
        result[i] = prefix  # Product of all elements before i
        prefix *= nums[i]   # Update prefix to include nums[i]

    # After this loop for [1,2,3,4]:
    # result = [1, 1, 2, 6]
    #           ↑  ↑  ↑  ↑
    #           1  1  1*2  1*2*3

    # Step 2: Build suffix products (right to left) and multiply
    # We'll multiply result[i] by product of all elements to the right
    suffix = 1
    for i in range(n - 1, -1, -1):
        result[i] *= suffix  # Multiply by product of all elements after i
        suffix *= nums[i]    # Update suffix to include nums[i]

    # After this loop for [1,2,3,4]:
    # result = [24, 12, 8, 6]

    return result

# Test with detailed trace
nums = [1, 2, 3, 4]
print(productExceptSelf(nums))  # [24, 12, 8, 6]

# Detailed walkthrough:
# Index 0: left=1, right=2*3*4=24 → 1*24=24 ✓
# Index 1: left=1, right=3*4=12 → 1*12=12 ✓
# Index 2: left=1*2=2, right=4 → 2*4=8 ✓
# Index 3: left=1*2*3=6, right=1 → 6*1=6 ✓
```

**Step-by-step visualization:**

```python
def productExceptSelf_verbose(nums):
    """Same algorithm with detailed print statements"""
    n = len(nums)
    result = [1] * n

    print(f"Input: {nums}")
    print(f"Initial result: {result}\n")

    # Prefix pass
    print("=== PREFIX PASS (left to right) ===")
    prefix = 1
    for i in range(n):
        result[i] = prefix
        print(f"i={i}: result[{i}] = {prefix} (product of all left of {nums[i]})")
        prefix *= nums[i]
        print(f"      Update prefix to {prefix}")

    print(f"\nAfter prefix pass: {result}\n")

    # Suffix pass
    print("=== SUFFIX PASS (right to left) ===")
    suffix = 1
    for i in range(n - 1, -1, -1):
        print(f"i={i}: result[{i}] = {result[i]} * {suffix} (multiply by product of all right)")
        result[i] *= suffix
        print(f"      result[{i}] = {result[i]}")
        suffix *= nums[i]
        print(f"      Update suffix to {suffix}")

    print(f"\nFinal result: {result}")
    return result

productExceptSelf_verbose([1, 2, 3, 4])
```

### Problem 3: Valid Palindrome - Optimized (Two Pointers)

```python
def isPalindrome(s):
    """
    Optimized: Two pointers approach with in-place checking

    Key Insight:
    Use two pointers (left and right) moving toward each other
    Skip non-alphanumeric characters on the fly

    Time: O(n) - single pass through string
    Space: O(1) - only two pointer variables, no extra strings
    """
    left = 0
    right = len(s) - 1

    while left < right:
        # Skip non-alphanumeric characters from left
        while left < right and not s[left].isalnum():
            left += 1

        # Skip non-alphanumeric characters from right
        while left < right and not s[right].isalnum():
            right -= 1

        # Compare characters (case-insensitive)
        if s[left].lower() != s[right].lower():
            return False

        # Move both pointers toward center
        left += 1
        right -= 1

    # If we made it through without finding mismatch, it's a palindrome
    return True

# Test
print(isPalindrome("A man, a plan, a canal: Panama"))  # True
print(isPalindrome("race a car"))  # False

# Visualization for "A man, a plan, a canal: Panama"
# Step 1: left='A', right='a' → match ✓
# Step 2: left='m', right='m' → match ✓
# Step 3: left='a', right='a' → match ✓
# ... continues until left >= right
```

**Why it's better:**
- O(1) space vs O(n) in brute force
- No string creation overhead
- Single pass through data

## Time & Space Complexity Analysis

### Complexity Comparison Table

| Problem | Brute Force Time | Brute Force Space | Optimized Time | Optimized Space | Improvement |
|---------|------------------|-------------------|----------------|-----------------|-------------|
| **Group Anagrams** | O(n² × m log m) | O(n × m) | O(n × m log m) or O(n × m) | O(n × m) | Eliminated nested comparison |
| **Product Except Self** | O(n²) | O(1) | O(n) | O(1) | Linear vs quadratic |
| **Valid Palindrome** | O(n) | O(n) | O(n) | O(1) | Constant space |

### Detailed Analysis

#### Group Anagrams
```
Brute Force: O(n² × m log m)
├─ Outer loop: n iterations
├─ Inner loop: n iterations  } = n² comparisons
└─ Each comparison: sort both strings = 2 × m log m

Optimized (sorted key): O(n × m log m)
├─ Single loop: n iterations
└─ Each iteration: sort string = m log m

Optimized (char count): O(n × m)
├─ Single loop: n iterations
└─ Each iteration: count chars = m
```

#### Product Except Self
```
Brute Force: O(n²)
├─ Outer loop: n positions
├─ Inner loop: n multiplications per position
└─ Total: n × n = n²

Optimized: O(n)
├─ Prefix pass: n iterations
├─ Suffix pass: n iterations
└─ Total: 2n = O(n)
```

#### Valid Palindrome
```
Both approaches: O(n) time
│
├─ Brute Force space: O(n)
│  ├─ Cleaned string: n characters
│  └─ Reversed string: n characters
│
└─ Optimized space: O(1)
   └─ Only two pointer variables
```

## Common Patterns

### Pattern 1: Two Pointers

**When to Use:**
- Comparing elements from both ends
- Palindrome checking
- Pair finding in sorted arrays
- In-place array manipulation

```python
def two_pointers_template(arr):
    """
    Two pointers moving toward each other
    Common in: palindromes, pair sums, array reversal
    """
    left = 0
    right = len(arr) - 1

    while left < right:
        # Process elements at both ends
        # ... do something with arr[left] and arr[right]

        # Move pointers based on condition
        if some_condition:
            left += 1
        else:
            right -= 1

    return result

# Example: Reverse array in-place
def reverse_array(arr):
    left, right = 0, len(arr) - 1
    while left < right:
        # Swap elements
        arr[left], arr[right] = arr[right], arr[left]
        left += 1
        right -= 1
    return arr

print(reverse_array([1, 2, 3, 4, 5]))  # [5, 4, 3, 2, 1]
```

**Two Pointers - Same Direction (Fast & Slow)**

```python
def fast_slow_pointers(arr):
    """
    Two pointers moving in same direction at different speeds
    Common in: removing duplicates, partitioning
    """
    slow = 0

    for fast in range(len(arr)):
        if some_condition:
            # Move element to slow position
            arr[slow] = arr[fast]
            slow += 1

    return slow

# Example: Remove duplicates from sorted array
def removeDuplicates(nums):
    """
    Given sorted array, remove duplicates in-place
    [1,1,2,2,3] → [1,2,3,_,_] return 3
    """
    if not nums:
        return 0

    # Slow pointer: position for next unique element
    slow = 1

    # Fast pointer: scan through array
    for fast in range(1, len(nums)):
        # Found a new unique element
        if nums[fast] != nums[fast - 1]:
            nums[slow] = nums[fast]
            slow += 1

    return slow

nums = [1, 1, 2, 2, 3]
length = removeDuplicates(nums)
print(nums[:length])  # [1, 2, 3]
```

### Pattern 2: Hash Maps for Grouping and Counting

**When to Use:**
- Grouping similar elements
- Frequency counting
- Finding patterns or duplicates
- Anagram detection

```python
def hashmap_template():
    """
    Hash map for grouping/counting
    Common in: anagrams, duplicates, frequency analysis
    """
    from collections import defaultdict

    # For grouping
    groups = defaultdict(list)

    for item in items:
        key = compute_key(item)  # Define what makes items similar
        groups[key].append(item)

    # For counting
    counts = defaultdict(int)

    for item in items:
        counts[item] += 1

    return groups, counts

# Example: Find all duplicates
def findDuplicates(nums):
    """Return all numbers that appear more than once"""
    from collections import defaultdict

    count = defaultdict(int)
    duplicates = []

    for num in nums:
        count[num] += 1
        # Add to duplicates only on second occurrence
        if count[num] == 2:
            duplicates.append(num)

    return duplicates

print(findDuplicates([4,3,2,7,8,2,3,1]))  # [2, 3]
```

**Character Frequency Map**

```python
def characterFrequency(s):
    """
    Count character frequencies
    Useful for: anagrams, permutations, string comparison
    """
    from collections import Counter

    # Method 1: Using Counter (easiest)
    freq = Counter(s)

    # Method 2: Manual counting
    freq_manual = {}
    for char in s:
        freq_manual[char] = freq_manual.get(char, 0) + 1

    # Method 3: defaultdict
    from collections import defaultdict
    freq_default = defaultdict(int)
    for char in s:
        freq_default[char] += 1

    return freq

print(characterFrequency("hello"))
# Counter({'l': 2, 'h': 1, 'e': 1, 'o': 1})
```

### Pattern 3: In-Place Operations

**When to Use:**
- Space constraint: O(1) extra space required
- Array modification problems
- Swapping, rotating, or reversing

```python
def inplace_template(arr):
    """
    Modify array without extra space
    Common in: rotation, reversal, partitioning
    """
    # Technique 1: Swapping
    def swap(i, j):
        arr[i], arr[j] = arr[j], arr[i]

    # Technique 2: Reversal for rotation
    def reverse(start, end):
        while start < end:
            arr[start], arr[end] = arr[end], arr[start]
            start += 1
            end -= 1

    return arr

# Example: Rotate array right by k steps
def rotate(nums, k):
    """
    [1,2,3,4,5,6,7] k=3 → [5,6,7,1,2,3,4]

    Trick: Three reversals
    1. Reverse entire array: [7,6,5,4,3,2,1]
    2. Reverse first k: [5,6,7,4,3,2,1]
    3. Reverse remaining: [5,6,7,1,2,3,4]
    """
    n = len(nums)
    k = k % n  # Handle k > n

    def reverse(start, end):
        while start < end:
            nums[start], nums[end] = nums[end], nums[start]
            start += 1
            end -= 1

    # Reverse entire array
    reverse(0, n - 1)
    # Reverse first k elements
    reverse(0, k - 1)
    # Reverse remaining elements
    reverse(k, n - 1)

    return nums

print(rotate([1,2,3,4,5,6,7], 3))  # [5,6,7,1,2,3,4]
```

### Pattern 4: String Building (Efficient Concatenation)

**When to Use:**
- Building strings character by character
- Multiple concatenations needed

```python
def string_building():
    """
    Efficient string construction
    AVOID: string += char (creates new string each time in Python)
    USE: List append + join
    """
    # ❌ BAD: O(n²) due to string immutability
    def build_string_bad(chars):
        result = ""
        for char in chars:
            result += char  # Creates new string each time!
        return result

    # ✅ GOOD: O(n) using list
    def build_string_good(chars):
        result = []
        for char in chars:
            result.append(char)  # O(1) append
        return ''.join(result)  # Single O(n) join

    return build_string_good

# Example: Compress string
def compressString(s):
    """
    "aaabbcccc" → "a3b2c4"
    """
    if not s:
        return ""

    result = []  # Use list for efficient building
    count = 1

    for i in range(1, len(s)):
        if s[i] == s[i-1]:
            count += 1
        else:
            result.append(s[i-1] + str(count))
            count = 1

    # Don't forget last group
    result.append(s[-1] + str(count))

    compressed = ''.join(result)
    # Return original if compressed isn't shorter
    return compressed if len(compressed) < len(s) else s

print(compressString("aaabbcccc"))  # "a3b2c4"
```

### Pattern 5: Prefix/Suffix Arrays

**When to Use:**
- Need products/sums excluding current element
- Range queries
- Cumulative computations

```python
def prefix_suffix_pattern(arr):
    """
    Build prefix and suffix arrays for O(1) range queries
    Common in: product/sum calculations, range queries
    """
    n = len(arr)

    # Prefix array: prefix[i] = arr[0] + arr[1] + ... + arr[i]
    prefix = [0] * n
    prefix[0] = arr[0]
    for i in range(1, n):
        prefix[i] = prefix[i-1] + arr[i]

    # Suffix array: suffix[i] = arr[i] + arr[i+1] + ... + arr[n-1]
    suffix = [0] * n
    suffix[n-1] = arr[n-1]
    for i in range(n-2, -1, -1):
        suffix[i] = suffix[i+1] + arr[i]

    return prefix, suffix

# Example: Range sum query
class RangeSumQuery:
    """
    Given array, answer sum queries for range [i, j] in O(1)
    """
    def __init__(self, nums):
        self.prefix = [0]  # Pad with 0 for easier calculation
        for num in nums:
            self.prefix.append(self.prefix[-1] + num)

    def sumRange(self, i, j):
        """Sum of elements from index i to j inclusive"""
        return self.prefix[j + 1] - self.prefix[i]

# Test
rsq = RangeSumQuery([1, 2, 3, 4, 5])
print(rsq.sumRange(1, 3))  # 2+3+4 = 9
print(rsq.sumRange(0, 4))  # 1+2+3+4+5 = 15
```

## Pro Tips for Senior Engineers

### 1. Python String Immutability Gotchas

```python
# ❌ AVOID: String concatenation in loops (O(n²))
def bad_string_building(n):
    result = ""
    for i in range(n):
        result += str(i)  # Creates new string each time!
    return result

# ✅ PREFER: List + join (O(n))
def good_string_building(n):
    result = []
    for i in range(n):
        result.append(str(i))
    return ''.join(result)

# Benchmark difference:
# n=10000: bad=0.5s, good=0.001s (500x faster!)
```

### 2. List Slicing Creates Copies

```python
# ❌ EXPENSIVE: Slicing creates new list
def expensive_operation(arr):
    while len(arr) > 1:
        arr = arr[1:]  # O(n) copy each iteration!

# ✅ BETTER: Use indices
def better_operation(arr):
    i = 0
    while i < len(arr) - 1:
        i += 1  # O(1)
```

### 3. Array Reversal Tricks

```python
# Multiple ways to reverse
arr = [1, 2, 3, 4, 5]

# Method 1: Built-in (in-place, O(n) time, O(1) space)
arr.reverse()

# Method 2: Slicing (creates new list, O(n) space)
reversed_arr = arr[::-1]

# Method 3: Manual two-pointer (in-place, educational)
def reverse_manual(arr):
    left, right = 0, len(arr) - 1
    while left < right:
        arr[left], arr[right] = arr[right], arr[left]
        left += 1
        right -= 1

# For interviews: explain trade-offs!
```

### 4. Counter and defaultdict Power Moves

```python
from collections import Counter, defaultdict

# Counter tricks
s = "aabbbcccc"
freq = Counter(s)

# Most common elements
print(freq.most_common(2))  # [('c', 4), ('b', 3)]

# Arithmetic operations on Counters
c1 = Counter(['a', 'b', 'c'])
c2 = Counter(['a', 'b', 'd'])
print(c1 + c2)  # Counter({'a': 2, 'b': 2, 'c': 1, 'd': 1})
print(c1 - c2)  # Counter({'c': 1})
print(c1 & c2)  # Intersection: Counter({'a': 1, 'b': 1})

# defaultdict for grouping
from collections import defaultdict

# Group numbers by their last digit
nums = [12, 23, 34, 45, 56, 67, 78]
groups = defaultdict(list)
for num in nums:
    groups[num % 10].append(num)
print(dict(groups))
# {2: [12], 3: [23], 4: [34], 5: [45], 6: [56], 7: [67], 8: [78]}
```

### 5. Pythonic Array Manipulation

```python
# Enumerate for index + value
arr = ['a', 'b', 'c']
for i, val in enumerate(arr):
    print(f"{i}: {val}")

# Zip for parallel iteration
names = ['Alice', 'Bob', 'Charlie']
scores = [85, 92, 88]
for name, score in zip(names, scores):
    print(f"{name}: {score}")

# List comprehensions for transformations
nums = [1, 2, 3, 4, 5]
squares = [x**2 for x in nums]
evens = [x for x in nums if x % 2 == 0]

# Dict comprehension for frequency
chars = "hello"
freq = {char: chars.count(char) for char in set(chars)}

# All/any for checking conditions
nums = [2, 4, 6, 8]
all_even = all(x % 2 == 0 for x in nums)  # True
any_odd = any(x % 2 == 1 for x in nums)   # False
```

### 6. Space-Time Trade-offs

```python
"""
Always consider the trade-off:

1. More Space → Less Time
   Example: Hash maps for O(1) lookup instead of O(n) search

2. Less Space → More Time
   Example: In-place algorithms that make multiple passes

3. Ask interviewer about constraints:
   - "Should I optimize for time or space?"
   - "What's the expected input size?"
   - "Are there memory constraints?"
"""

# Example: Two Sum

# ✅ Time-optimized: O(n) time, O(n) space
def twoSum_fast(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i

# ✅ Space-optimized: O(n²) time, O(1) space
def twoSum_space_efficient(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]

# Interview: Start with fast solution, mention space alternative
```

### 7. Edge Cases Checklist

```python
"""
Always test these edge cases for string/array problems:

1. Empty input: [], ""
2. Single element: [1], "a"
3. All same elements: [1,1,1,1], "aaaa"
4. Already sorted/optimal: [1,2,3]
5. Reverse sorted: [3,2,1]
6. Duplicates: [1,2,2,3]
7. Negative numbers: [-1,-2,3]
8. Large inputs: 10^5 elements
"""

def robust_function(arr):
    # Guard against empty
    if not arr:
        return []

    # Guard against single element
    if len(arr) == 1:
        return arr

    # Main logic
    # ...

    return result
```

## Problem Recognition

### Keywords That Signal String/Array Manipulation

| Keyword/Phrase | Likely Pattern | Example Problem |
|----------------|----------------|-----------------|
| "anagram" | Hash map (character frequency) | Group Anagrams |
| "palindrome" | Two pointers | Valid Palindrome |
| "subarray" | Sliding window or prefix sum | Max Subarray Sum |
| "in-place" | Two pointers or swapping | Rotate Array |
| "without extra space" | In-place manipulation | Product Except Self |
| "group by" | Hash map for grouping | Group Anagrams |
| "except self" | Prefix/suffix arrays | Product Except Self |
| "consecutive" | Sliding window | Longest Consecutive Sequence |
| "rotate" | Reversal or modular arithmetic | Rotate Array |
| "compress" | String building | String Compression |
| "duplicate" | Hash set or sorting | Find Duplicates |
| "contiguous" | Prefix sum or sliding window | Subarray Sum Equals K |

### Problem Pattern Recognition Flow

```
Given a problem, ask:

1. Does it involve sequential data (array/string)?
   YES → Consider String/Array patterns

2. Do I need to compare elements?
   - From both ends? → Two Pointers (opposite direction)
   - Adjacent elements? → Single pass
   - All pairs? → Hash map or sorting

3. Do I need to group/count?
   → Hash map (Counter/defaultdict)

4. Are there space constraints?
   "In-place" or "O(1) space" → In-place manipulation

5. Do I need cumulative values?
   → Prefix/suffix arrays

6. Is it about patterns in strings?
   - Same letters, different order → Anagram (hash map)
   - Reads same forwards/backwards → Palindrome (two pointers)
   - Substring matching → Sliding window
```

## Practice Problems

### Beginner Level
1. **Two Sum** (Easy)
   - Pattern: Hash map
   - Key Learning: Trading space for time
   - LeetCode #1

2. **Reverse String** (Easy)
   - Pattern: Two pointers
   - Key Learning: In-place manipulation
   - LeetCode #344

3. **Valid Anagram** (Easy)
   - Pattern: Hash map (frequency counting)
   - Key Learning: Character frequency comparison
   - LeetCode #242

### Intermediate Level
4. **Longest Substring Without Repeating Characters** (Medium)
   - Pattern: Sliding window + hash set
   - Key Learning: Dynamic window sizing
   - LeetCode #3

5. **Container With Most Water** (Medium)
   - Pattern: Two pointers
   - Key Learning: Greedy pointer movement
   - LeetCode #11

6. **3Sum** (Medium)
   - Pattern: Two pointers + sorting
   - Key Learning: Handling duplicates
   - LeetCode #15

### Advanced Level
7. **Minimum Window Substring** (Hard)
   - Pattern: Sliding window + hash map
   - Key Learning: Complex window conditions
   - LeetCode #76

8. **Trapping Rain Water** (Hard)
   - Pattern: Two pointers or prefix/suffix
   - Key Learning: Multiple approaches to same problem
   - LeetCode #42

9. **Longest Palindromic Substring** (Medium)
   - Pattern: Expand around center or DP
   - Key Learning: String pattern recognition
   - LeetCode #5

### Practice Strategy

```python
"""
Recommended Practice Order:

Week 1: Foundation
- Two Sum (hash map basics)
- Valid Palindrome (two pointers)
- Valid Anagram (frequency counting)

Week 2: Core Patterns
- Group Anagrams (hash map grouping)
- Product Except Self (prefix/suffix)
- Rotate Array (in-place manipulation)

Week 3: Advanced
- Longest Substring Without Repeating Characters
- 3Sum
- Minimum Window Substring

For each problem:
1. Solve brute force first
2. Identify bottleneck
3. Optimize with appropriate pattern
4. Analyze time/space complexity
5. Code clean solution with edge cases
"""
```

## Common Mistakes

### Mistake 1: Forgetting String Immutability

```python
# ❌ WRONG: Trying to modify string directly
def wrong_approach(s):
    for i in range(len(s)):
        s[i] = s[i].upper()  # TypeError: str doesn't support item assignment

# ✅ CORRECT: Convert to list or build new string
def correct_approach(s):
    # Method 1: List
    chars = list(s)
    for i in range(len(chars)):
        chars[i] = chars[i].upper()
    return ''.join(chars)

    # Method 2: List comprehension
    return ''.join([char.upper() for char in s])
```

### Mistake 2: Off-by-One Errors in Two Pointers

```python
# ❌ WRONG: Missing last comparison
def wrong_palindrome(s):
    left, right = 0, len(s) - 1
    while left <= right:  # Should be left < right
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True

# Problem: When left == right, we compare same character with itself
# For "aba": compares 'a'=='a' twice unnecessarily

# ✅ CORRECT
def correct_palindrome(s):
    left, right = 0, len(s) - 1
    while left < right:  # Stop before they meet
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True
```

### Mistake 3: Not Handling Empty Input

```python
# ❌ WRONG: Crashes on empty input
def wrong_max_element(arr):
    max_val = arr[0]  # IndexError if arr is empty!
    for num in arr[1:]:
        max_val = max(max_val, num)
    return max_val

# ✅ CORRECT: Check for empty first
def correct_max_element(arr):
    if not arr:
        return None  # or raise ValueError("Empty array")

    max_val = arr[0]
    for num in arr[1:]:
        max_val = max(max_val, num)
    return max_val
```

### Mistake 4: Inefficient String Concatenation

```python
# ❌ WRONG: O(n²) due to string immutability
def wrong_join_strings(words):
    result = ""
    for word in words:
        result += word + " "  # Creates new string each iteration!
    return result.strip()

# ✅ CORRECT: O(n) using join
def correct_join_strings(words):
    return " ".join(words)

# Benchmark for 10000 words:
# Wrong: ~2.5 seconds
# Correct: ~0.001 seconds (2500x faster!)
```

### Mistake 5: Modifying Array While Iterating

```python
# ❌ WRONG: Modifying list during iteration
def wrong_remove_evens(nums):
    for num in nums:
        if num % 2 == 0:
            nums.remove(num)  # Skips elements!
    return nums

# Test: wrong_remove_evens([1,2,3,4,5,6])
# Expected: [1,3,5]
# Actual: [1,3,5,6]  # Missed 6 because indices shifted!

# ✅ CORRECT: Iterate backwards or use list comprehension
def correct_remove_evens(nums):
    # Method 1: List comprehension (creates new list)
    return [num for num in nums if num % 2 != 0]

    # Method 2: Backwards iteration (in-place)
    for i in range(len(nums) - 1, -1, -1):
        if nums[i] % 2 == 0:
            nums.pop(i)
    return nums
```

### Mistake 6: Not Considering Duplicates

```python
# ❌ WRONG: Doesn't handle duplicates in 3Sum
def wrong_three_sum(nums):
    result = []
    nums.sort()

    for i in range(len(nums) - 2):
        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                result.append([nums[i], nums[left], nums[right]])
                left += 1
                right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1

    return result

# Test: wrong_three_sum([-1,0,1,0,1])
# Returns: [[-1,0,1], [-1,0,1]]  # Duplicate!

# ✅ CORRECT: Skip duplicates
def correct_three_sum(nums):
    result = []
    nums.sort()

    for i in range(len(nums) - 2):
        # Skip duplicate values for i
        if i > 0 and nums[i] == nums[i - 1]:
            continue

        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                result.append([nums[i], nums[left], nums[right]])

                # Skip duplicates for left and right
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1

                left += 1
                right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1

    return result
```

### Mistake 7: Integer Overflow (Less Common in Python)

```python
"""
While Python handles big integers automatically, be aware for:
- Other languages (Java, C++)
- Understanding constraints
- Optimizing space
"""

# ❌ WRONG in languages with fixed integer sizes
def product_of_array(nums):
    product = 1
    for num in nums:
        product *= num  # Can overflow in Java/C++!
    return product

# ✅ CORRECT: Consider modulo or explain overflow handling
def product_of_array_safe(nums):
    MOD = 10**9 + 7
    product = 1
    for num in nums:
        product = (product * num) % MOD
    return product

# In interviews: Mention "In languages with fixed integers,
# I'd use modulo or check for overflow"
```

### Mistake 8: Wrong Hash Map Key Type

```python
# ❌ WRONG: Using list as hash map key
def wrong_grouping(arrays):
    groups = {}
    for arr in arrays:
        groups[arr] = groups.get(arr, [])  # TypeError: list is not hashable!

# ✅ CORRECT: Convert to tuple
def correct_grouping(arrays):
    groups = {}
    for arr in arrays:
        key = tuple(arr)  # Tuples are hashable
        if key not in groups:
            groups[key] = []
        groups[key].append(arr)
    return groups

# Test
arrays = [[1,2], [3,4], [1,2]]
print(correct_grouping(arrays))
# {(1,2): [[1,2], [1,2]], (3,4): [[3,4]]}
```

## Summary

String/Array Manipulation is foundational to coding interviews. Master these patterns:

1. **Two Pointers**: For palindromes, pairs, in-place operations
2. **Hash Maps**: For grouping, counting, frequency analysis
3. **Prefix/Suffix**: For cumulative calculations
4. **In-Place**: For space-constrained problems
5. **String Building**: Use lists, not concatenation

### Quick Decision Tree

```
Problem involves array/string?
│
├─ Need to compare from both ends?
│  → Two Pointers (opposite direction)
│
├─ Need to group or count?
│  → Hash Map
│
├─ Need cumulative values?
│  → Prefix/Suffix Arrays
│
├─ Space constraint (O(1))?
│  → In-Place Manipulation
│
└─ Building strings?
   → List + join (not concatenation)
```

### Key Takeaways

- **Always analyze time/space complexity** before coding
- **Start with brute force**, then optimize
- **Consider edge cases**: empty, single element, duplicates
- **Python-specific**: strings are immutable, use lists for building
- **Ask clarifying questions** about constraints and expected input size

Practice these patterns until they become second nature. They appear in 60%+ of coding interviews!
