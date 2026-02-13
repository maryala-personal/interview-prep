# Two Pointers Pattern - Complete Guide

## 1. What is Two Pointers?

### Explain Like I'm 5
Imagine you have a line of toy cars arranged by color. You want to find two cars that together make your favorite color combination. Instead of picking up each car and comparing it with every other car (which would take forever!), you use your left hand to point at the first car and your right hand to point at the last car. Then you move your hands closer together, checking cars as you go. This is much faster than checking every possible pair!

### Technical Definition
The Two Pointers pattern is an algorithmic technique that uses two references (pointers/indices) to traverse a data structure, typically an array or string. These pointers move based on certain conditions to solve problems in optimal time complexity. Instead of using nested loops that result in O(n²) time complexity, two pointers can often solve the same problem in O(n) time.

**Key Characteristics:**
- Uses two indices/pointers to track positions in data structure
- Pointers move independently based on problem logic
- Often used on sorted arrays or strings
- Reduces time complexity from O(n²) to O(n)
- Typically uses O(1) extra space

## 2. Real-World Analogy

### The Wine Tasting Analogy
Imagine you're at a wine shop with bottles arranged by price from cheapest to most expensive. You want to buy exactly two bottles with a combined price of $50.

**Naive approach (like nested loops):**
- Pick the first bottle ($10)
- Walk through ALL other bottles to find if any add up to $50
- Pick the second bottle ($12)
- Walk through ALL other bottles again
- This takes FOREVER!

**Two Pointers approach:**
- Put your left hand on the cheapest bottle ($10)
- Put your right hand on the most expensive bottle ($60)
- Check: $10 + $60 = $70 (too much!)
- Move right hand left to next cheaper bottle ($55)
- Check: $10 + $55 = $65 (still too much!)
- Move right hand left again ($45)
- Check: $10 + $45 = $55 (still too much!)
- Move right hand left again ($40)
- Check: $10 + $40 = $50 (PERFECT! ✓)

You found the answer by only walking through the bottles ONCE from both ends, instead of checking every possible pair!

## 3. When to Use Two Pointers

### Clear Signals That Scream "Use Two Pointers!"

✅ **Use Two Pointers When You See:**

1. **Sorted Array/String Problems**
   - "Given a SORTED array..."
   - "In a SORTED sequence..."

2. **Finding Pairs/Triplets**
   - "Find two numbers that sum to target"
   - "Find all unique triplets that sum to zero"

3. **Palindrome-Related Problems**
   - "Check if string is a palindrome"
   - "Find longest palindromic substring"

4. **Array Partitioning**
   - "Move all zeros to the end"
   - "Partition array into even/odd"

5. **Linked List Problems**
   - "Find middle of linked list"
   - "Detect cycle in linked list"
   - "Check if linked list is palindrome"

6. **Container/Window Problems**
   - "Container with most water"
   - "Trapping rain water"

7. **Subsequence Problems**
   - "Is string a subsequence of another?"
   - "Remove duplicates from sorted array"

### Pattern Recognition Keywords
- "sorted"
- "pair"
- "palindrome"
- "in-place"
- "opposite ends"
- "two elements"
- "partition"
- "remove duplicates"

## 4. The Classic Problem: Two Sum II

### Problem Statement
Given a **1-indexed array** of integers `numbers` that is already **sorted in non-decreasing order**, find two numbers such that they add up to a specific `target` number. Return the indices of the two numbers (index1 and index2) where `index1 < index2`.

**Example:**
```
Input: numbers = [2, 7, 11, 15], target = 9
Output: [1, 2]
Explanation: The sum of 2 and 7 is 9. Therefore, index1 = 1, index2 = 2.
We return [1, 2] (1-indexed).
```

**Constraints:**
- 2 <= numbers.length <= 30,000
- -1000 <= numbers[i] <= 1000
- numbers is sorted in non-decreasing order
- There is exactly one solution

## 5. Brute Force Approach

### The Naive Solution

```python
def two_sum_brute_force(numbers, target):
    """
    Brute force approach: Check every possible pair

    Time Complexity: O(n²) - nested loops
    Space Complexity: O(1) - only using a few variables
    """
    # Get the length of the array
    n = len(numbers)

    # Outer loop: pick first number
    for i in range(n):
        # Inner loop: pick second number
        for j in range(i + 1, n):  # Start from i+1 to avoid using same element twice
            # Check if this pair sums to target
            current_sum = numbers[i] + numbers[j]

            if current_sum == target:
                # Found it! Return 1-indexed positions
                return [i + 1, j + 1]

    # No solution found (but problem guarantees one exists)
    return [-1, -1]


# Example usage
numbers = [2, 7, 11, 15]
target = 9
result = two_sum_brute_force(numbers, target)
print(f"Indices: {result}")  # Output: [1, 2]
```

### How It Works (Step by Step)
```
numbers = [2, 7, 11, 15], target = 9

i=0, j=1: 2 + 7 = 9  ✓ FOUND! Return [1, 2]

Total comparisons: 1 (got lucky!)

Worst case (target not at beginning):
i=0, j=1: 2 + 7  ✗
i=0, j=2: 2 + 11 ✗
i=0, j=3: 2 + 15 ✗
i=1, j=2: 7 + 11 ✗
i=1, j=3: 7 + 15 ✗
i=2, j=3: 11 + 15 ✗

Total possible comparisons: 6 = n*(n-1)/2
For n=4: 4*3/2 = 6 comparisons
For n=100: 100*99/2 = 4,950 comparisons!
For n=30,000: 30,000*29,999/2 = 449,985,000 comparisons! 😱
```

### Why This Is Bad
- **Slow:** Checks every possible pair
- **Wasteful:** Ignores the fact that array is sorted
- **Doesn't Scale:** For 30,000 elements, makes 450 million comparisons!

## 6. Optimized Solution: Two Pointers

### The Smart Solution

```python
def two_sum_two_pointers(numbers, target):
    """
    Two pointers approach: Use sorted property to eliminate possibilities

    Time Complexity: O(n) - single pass through array
    Space Complexity: O(1) - only using two pointer variables
    """
    # Initialize two pointers
    left = 0              # Points to smallest number (beginning)
    right = len(numbers) - 1  # Points to largest number (end)

    # Keep moving pointers until they meet
    while left < right:
        # Calculate sum of numbers at both pointers
        current_sum = numbers[left] + numbers[right]

        # Check three cases:

        if current_sum == target:
            # FOUND IT! Return 1-indexed positions
            return [left + 1, right + 1]

        elif current_sum < target:
            # Sum is too small, need bigger number
            # Array is sorted, so move LEFT pointer right to get bigger number
            left += 1

        else:  # current_sum > target
            # Sum is too large, need smaller number
            # Move RIGHT pointer left to get smaller number
            right -= 1

    # No solution found (but problem guarantees one exists)
    return [-1, -1]


# Example usage
numbers = [2, 7, 11, 15]
target = 9
result = two_sum_two_pointers(numbers, target)
print(f"Indices: {result}")  # Output: [1, 2]
```

### How It Works (Detailed Walkthrough)

```
numbers = [2, 7, 11, 15], target = 9

Initial state:
         L              R
Index:   0    1    2    3
Value:  [2,   7,  11,  15]

Step 1:
  left = 0, right = 3
  current_sum = 2 + 15 = 17
  17 > 9 (too large!)
  → Move right pointer left to get smaller number

         L         R
Index:   0    1    2    3
Value:  [2,   7,  11,  15]

Step 2:
  left = 0, right = 2
  current_sum = 2 + 11 = 13
  13 > 9 (still too large!)
  → Move right pointer left again

         L    R
Index:   0    1    2    3
Value:  [2,   7,  11,  15]

Step 3:
  left = 0, right = 1
  current_sum = 2 + 7 = 9
  9 == 9 ✓ FOUND!
  → Return [1, 2] (1-indexed)

Total comparisons: 3 (instead of up to 6 in brute force!)
```

### Why This Works (The Logic)

**Key Insight:** Because the array is SORTED, we can make intelligent decisions:

1. **If sum is too small:**
   - We need a bigger number
   - The left pointer is at the smallest available number
   - Moving left pointer RIGHT gives us the next bigger number

2. **If sum is too large:**
   - We need a smaller number
   - The right pointer is at the largest available number
   - Moving right pointer LEFT gives us the next smaller number

3. **If sum is perfect:**
   - We found it! Return the answer.

**Why we don't miss the answer:**
- We start with the smallest and largest numbers
- We systematically eliminate impossible combinations
- We're guaranteed to check the correct pair before pointers cross

### Visual Representation

```
Target = 9

Start:  [2,   7,  11,  15]
         ↑              ↑
        left          right
        Sum = 17 (too big, move right left)

Step 2: [2,   7,  11,  15]
         ↑         ↑
        left     right
        Sum = 13 (too big, move right left)

Step 3: [2,   7,  11,  15]
         ↑    ↑
        left right
        Sum = 9 ✓ FOUND!
```

## 7. Time & Space Complexity Analysis

### Comparison Table

| Approach | Time Complexity | Space Complexity | Comparisons (n=100) | Comparisons (n=30,000) |
|----------|----------------|------------------|---------------------|------------------------|
| Brute Force | O(n²) | O(1) | ~4,950 | ~450,000,000 |
| Two Pointers | O(n) | O(1) | ~100 | ~30,000 |

### Detailed Analysis

#### Brute Force
- **Time:** O(n²)
  - Outer loop: n iterations
  - Inner loop: n-1, n-2, ..., 1 iterations
  - Total: n*(n-1)/2 = O(n²)
- **Space:** O(1)
  - Only uses variables i, j, current_sum
  - No extra data structures

#### Two Pointers
- **Time:** O(n)
  - While loop runs at most n times
  - Each iteration, either left increases or right decreases
  - Total possible moves: left can go from 0 to n-1, right can go from n-1 to 0
  - Maximum iterations = n
- **Space:** O(1)
  - Only uses variables left, right, current_sum
  - No extra data structures

### Why O(n) is MUCH Better

```
For n = 10:
  O(n²) = 100 operations
  O(n)  = 10 operations
  Improvement: 10x faster

For n = 1,000:
  O(n²) = 1,000,000 operations
  O(n)  = 1,000 operations
  Improvement: 1,000x faster!

For n = 30,000:
  O(n²) = 900,000,000 operations (15 minutes at 1M ops/sec)
  O(n)  = 30,000 operations (0.03 seconds at 1M ops/sec)
  Improvement: 30,000x faster! 🚀
```

## 8. Variations of Two Pointers Pattern

### 8.1 Opposite Direction (Converging Pointers)

**Pattern:** Start from both ends, move toward middle

**Use Cases:**
- Two Sum (sorted array)
- Container with Most Water
- Trapping Rain Water
- Valid Palindrome

```python
def is_palindrome(s):
    """Check if string is palindrome using two pointers"""
    left = 0
    right = len(s) - 1

    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1

    return True

# Example
print(is_palindrome("racecar"))  # True
print(is_palindrome("hello"))    # False
```

### 8.2 Same Direction (Fast & Slow Pointers)

**Pattern:** Both pointers move in same direction at different speeds

**Use Cases:**
- Remove duplicates from sorted array
- Move zeros to end
- Linked list cycle detection (Floyd's algorithm)

```python
def remove_duplicates(nums):
    """
    Remove duplicates in-place from sorted array
    Returns new length
    """
    if not nums:
        return 0

    # Slow pointer: position to place next unique element
    slow = 0

    # Fast pointer: scan through array
    for fast in range(1, len(nums)):
        # Found a new unique element
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]

    # Length of unique elements
    return slow + 1

# Example
nums = [1, 1, 2, 2, 2, 3, 4, 4]
length = remove_duplicates(nums)
print(nums[:length])  # [1, 2, 3, 4]
```

### 8.3 Sliding Window (Special Two Pointers)

**Pattern:** Window defined by two pointers, expand/contract window

**Use Cases:**
- Longest substring without repeating characters
- Minimum window substring
- Maximum sum subarray of size k

```python
def max_sum_subarray(arr, k):
    """
    Find maximum sum of any subarray of size k
    """
    if len(arr) < k:
        return -1

    # Calculate sum of first window
    window_sum = sum(arr[:k])
    max_sum = window_sum

    # Slide window: add next element, remove first element
    for i in range(k, len(arr)):
        window_sum = window_sum + arr[i] - arr[i - k]
        max_sum = max(max_sum, window_sum)

    return max_sum

# Example
arr = [2, 1, 5, 1, 3, 2]
k = 3
print(max_sum_subarray(arr, k))  # 9 (subarray [5,1,3])
```

### 8.4 Fast & Slow (Tortoise & Hare)

**Pattern:** One pointer moves twice as fast as the other

**Use Cases:**
- Find middle of linked list
- Detect cycle in linked list
- Find cycle start point

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def find_middle(head):
    """
    Find middle node of linked list
    When fast reaches end, slow is at middle
    """
    slow = head
    fast = head

    # Fast moves 2 steps, slow moves 1 step
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    return slow

def has_cycle(head):
    """
    Detect if linked list has a cycle
    If fast catches slow, there's a cycle
    """
    slow = head
    fast = head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

        if slow == fast:
            return True

    return False
```

### 8.5 Three Pointers

**Pattern:** Extension of two pointers for more complex problems

**Use Cases:**
- 3Sum problem
- Sort colors (Dutch National Flag)

```python
def three_sum(nums):
    """
    Find all unique triplets that sum to zero
    Uses one fixed pointer + two pointers for remaining elements
    """
    nums.sort()  # Must sort first!
    result = []

    for i in range(len(nums) - 2):
        # Skip duplicates for first number
        if i > 0 and nums[i] == nums[i - 1]:
            continue

        # Use two pointers for remaining two numbers
        left = i + 1
        right = len(nums) - 1
        target = -nums[i]  # We want nums[left] + nums[right] = -nums[i]

        while left < right:
            current_sum = nums[left] + nums[right]

            if current_sum == target:
                result.append([nums[i], nums[left], nums[right]])

                # Skip duplicates for second number
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                # Skip duplicates for third number
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1

                left += 1
                right -= 1

            elif current_sum < target:
                left += 1
            else:
                right -= 1

    return result

# Example
nums = [-1, 0, 1, 2, -1, -4]
print(three_sum(nums))  # [[-1, -1, 2], [-1, 0, 1]]
```

## 9. Pro Tips for Senior Engineers

### Edge Cases to Always Consider

1. **Empty or Single Element Arrays**
   ```python
   # Always check array length
   if not nums or len(nums) < 2:
       return []
   ```

2. **Duplicate Values**
   ```python
   # Skip duplicates to avoid duplicate results
   while left < right and nums[left] == nums[left + 1]:
       left += 1
   ```

3. **Integer Overflow (in languages like C++/Java)**
   ```python
   # In Python, not an issue, but in Java/C++:
   # Use: (nums[i] > target - nums[j]) instead of (nums[i] + nums[j] > target)
   ```

4. **Boundary Conditions**
   ```python
   # Always ensure pointers don't go out of bounds
   while left < right:  # Not <=
   while fast and fast.next:  # Check both
   ```

### When NOT to Use Two Pointers

❌ **Don't Use When:**

1. **Array is NOT sorted** (and sorting would destroy information)
   - Example: Finding pairs in unsorted array where order matters
   - Use hash map instead

2. **Need to check ALL pairs** (not just find one)
   - Example: Count all pairs with difference k
   - Might still need O(n²) approach or hash map

3. **Random Access Not Available**
   - Example: Stream of data, can't access both ends
   - Use sliding window or other techniques

4. **Complexity is not improved**
   - If sorting costs O(n log n) and saves nothing, don't sort

### Interview Gotchas

1. **0-indexed vs 1-indexed**
   ```python
   # Problem says return 1-indexed positions
   return [left + 1, right + 1]  # Don't forget the +1!
   ```

2. **Including vs Excluding Same Element**
   ```python
   # Can't use same element twice
   left = i + 1  # Start AFTER current element

   # Can use same element
   left = i  # Start FROM current element
   ```

3. **Sorted vs Unsorted**
   ```python
   # If problem doesn't say sorted, ask:
   # "Can I sort the array first?"
   # Sorting changes indices - might break solution!
   ```

4. **Multiple Solutions vs Single Solution**
   ```python
   # Single solution: return as soon as found
   if current_sum == target:
       return [left, right]

   # All solutions: collect all and continue
   if current_sum == target:
       result.append([left, right])
       left += 1
       right -= 1
   ```

### Performance Optimizations

1. **Early Termination**
   ```python
   # If smallest two numbers > target, impossible
   if nums[0] + nums[1] > target:
       return []

   # If largest two numbers < target, impossible
   if nums[-1] + nums[-2] < target:
       return []
   ```

2. **Skip Impossible Ranges**
   ```python
   # If current number too large, skip rest
   if nums[i] > target and nums[i] > 0:
       break
   ```

3. **Use Multiple Pointers Wisely**
   ```python
   # For 4Sum, reduce to 3Sum, reduce to 2Sum
   # Each reduction uses two pointers
   ```

## 10. Problem Recognition - Spotting the Pattern

### Decision Tree for Two Pointers

```
Is the data structure linear (array/string/linked list)?
│
├─ NO → Consider tree/graph algorithms
│
└─ YES → Is it sorted (or can be sorted)?
    │
    ├─ YES → Strong candidate for two pointers!
    │   │
    │   ├─ Finding pairs/triplets? → Opposite direction pointers
    │   ├─ Palindrome check? → Opposite direction pointers
    │   └─ Container/water problems? → Opposite direction pointers
    │
    └─ NO → Can still use two pointers for:
        │
        ├─ In-place modifications? → Same direction (fast/slow)
        ├─ Linked list problems? → Fast/slow (tortoise/hare)
        ├─ Substring problems? → Sliding window (two pointers)
        └─ Partitioning? → Same direction
```

### Pattern Recognition in Hard Problems

**Problem:** "Given an array, find closest three elements that sum to target"

**Signals:**
- ✅ Array (linear structure)
- ✅ Finding sum of elements (pair/triplet)
- ✅ Can sort (order doesn't matter for sum)
- ✅ "Closest" means we can eliminate ranges

**Approach:**
1. Sort array: O(n log n)
2. Fix one element: O(n)
3. Use two pointers for other two: O(n)
4. Total: O(n²) - much better than O(n³) brute force

**Problem:** "Find longest substring with at most k distinct characters"

**Signals:**
- ✅ Substring (contiguous elements)
- ✅ "Longest" suggests optimization
- ✅ Need to track window of elements

**Approach:**
- Use sliding window (two pointers)
- Expand right until k distinct characters exceeded
- Contract left to restore validity
- Track maximum length

## 11. Practice Problems

### Easy Level

1. **Valid Palindrome** (LeetCode 125)
   - Check if string is palindrome ignoring non-alphanumeric
   - Pattern: Opposite direction pointers
   - Key: Skip invalid characters while moving pointers

2. **Remove Duplicates from Sorted Array** (LeetCode 26)
   - Remove duplicates in-place, return new length
   - Pattern: Same direction (fast/slow)
   - Key: Slow pointer marks position for unique elements

3. **Move Zeroes** (LeetCode 283)
   - Move all zeros to end, maintain relative order
   - Pattern: Same direction (fast/slow)
   - Key: Slow pointer marks position for non-zero elements

### Medium Level

4. **3Sum** (LeetCode 15)
   - Find all unique triplets that sum to zero
   - Pattern: Fixed pointer + two pointers
   - Key: Sort first, skip duplicates

5. **Container With Most Water** (LeetCode 11)
   - Find two lines that contain most water
   - Pattern: Opposite direction pointers
   - Key: Always move pointer with shorter height

6. **Sort Colors** (LeetCode 75)
   - Sort array of 0s, 1s, and 2s in one pass
   - Pattern: Three pointers (Dutch National Flag)
   - Key: Low, mid, high pointers partition array

7. **Trapping Rain Water** (LeetCode 42)
   - Calculate how much rain water can be trapped
   - Pattern: Opposite direction with max tracking
   - Key: Track max heights from both sides

### Hard Level

8. **Minimum Window Substring** (LeetCode 76)
   - Find minimum window containing all characters
   - Pattern: Sliding window (expanding/contracting)
   - Key: Expand right, contract left when valid

9. **Longest Substring with At Most K Distinct Characters** (LeetCode 340)
   - Find longest substring with at most k distinct chars
   - Pattern: Sliding window with hash map
   - Key: Expand until k exceeded, contract to restore

10. **Substring with Concatenation of All Words** (LeetCode 30)
    - Find starting indices of concatenated substrings
    - Pattern: Sliding window with word matching
    - Key: Window size = total length of all words

### Linked List Problems (Two Pointers)

11. **Middle of Linked List** (LeetCode 876)
    - Find middle node of linked list
    - Pattern: Fast/slow (tortoise/hare)
    - Key: Fast moves 2x, slow at middle when fast ends

12. **Linked List Cycle** (LeetCode 141)
    - Detect if linked list has cycle
    - Pattern: Fast/slow (tortoise/hare)
    - Key: If fast catches slow, there's a cycle

13. **Palindrome Linked List** (LeetCode 234)
    - Check if linked list values form palindrome
    - Pattern: Fast/slow + reverse + compare
    - Key: Find middle, reverse second half, compare

## 12. Common Mistakes

### Mistake #1: Not Checking Boundary Conditions

**❌ Wrong:**
```python
while left <= right:  # Will compare same element with itself!
    if nums[left] + nums[right] == target:
        return [left, right]
```

**✅ Correct:**
```python
while left < right:  # Pointers must be different
    if nums[left] + nums[right] == target:
        return [left, right]
```

### Mistake #2: Forgetting Array is Sorted

**❌ Wrong:**
```python
# Using hash map when array is sorted
seen = {}
for i, num in enumerate(nums):
    if target - num in seen:
        return [seen[target - num], i]
    seen[num] = i
# O(n) space - wasteful!
```

**✅ Correct:**
```python
# Use two pointers - array is sorted!
left, right = 0, len(nums) - 1
while left < right:
    # ... two pointer logic
# O(1) space
```

### Mistake #3: Not Handling Duplicates

**❌ Wrong:**
```python
# 3Sum without skipping duplicates
result.append([nums[i], nums[left], nums[right]])
left += 1
right -= 1
# Will include duplicate triplets like [-1,-1,2] multiple times
```

**✅ Correct:**
```python
# Skip duplicates after finding solution
result.append([nums[i], nums[left], nums[right]])

while left < right and nums[left] == nums[left + 1]:
    left += 1
while left < right and nums[right] == nums[right - 1]:
    right -= 1

left += 1
right -= 1
```

### Mistake #4: Moving Wrong Pointer

**❌ Wrong:**
```python
if current_sum < target:
    right -= 1  # Moving wrong pointer!
elif current_sum > target:
    left += 1   # Moving wrong pointer!
```

**✅ Correct:**
```python
if current_sum < target:
    left += 1   # Need bigger sum, move left right
elif current_sum > target:
    right -= 1  # Need smaller sum, move right left
```

### Mistake #5: Not Considering Integer Overflow

**❌ Wrong (in Java/C++):**
```java
if (nums[left] + nums[right] == target) {
    // Can overflow for large integers!
}
```

**✅ Correct (in Java/C++):**
```java
// Rewrite to avoid overflow
if (nums[left] == target - nums[right]) {
    // No overflow risk
}
```

### Mistake #6: Using Two Pointers on Unsorted Array

**❌ Wrong:**
```python
# Array is NOT sorted
nums = [3, 1, 4, 2, 5]
target = 6

left, right = 0, len(nums) - 1
while left < right:
    if nums[left] + nums[right] == target:
        return [left, right]  # Might miss valid pairs!
```

**✅ Correct:**
```python
# Either sort first (if allowed)
nums.sort()
# Then use two pointers

# Or use hash map for unsorted
seen = {}
for i, num in enumerate(nums):
    if target - num in seen:
        return [seen[target - num], i]
    seen[num] = i
```

### Mistake #7: Infinite Loop Due to Not Moving Pointers

**❌ Wrong:**
```python
while left < right:
    if nums[left] + nums[right] == target:
        return [left, right]
    elif nums[left] + nums[right] < target:
        left += 1
    # Forgot the else case! If sum > target, infinite loop!
```

**✅ Correct:**
```python
while left < right:
    if nums[left] + nums[right] == target:
        return [left, right]
    elif nums[left] + nums[right] < target:
        left += 1
    else:
        right -= 1  # Always move at least one pointer!
```

### Mistake #8: Confusing 0-indexed and 1-indexed

**❌ Wrong:**
```python
# Problem asks for 1-indexed result
left, right = 0, 4
# Found answer at indices 0 and 2
return [left, right]  # Returns [0, 2] but should be [1, 3]!
```

**✅ Correct:**
```python
# Problem asks for 1-indexed result
left, right = 0, 4
# Found answer
return [left + 1, right + 1]  # Convert to 1-indexed
```

---

## Summary Cheat Sheet

| Aspect | Key Points |
|--------|------------|
| **Core Idea** | Use 2 pointers to reduce O(n²) to O(n) |
| **When to Use** | Sorted arrays, pairs, palindromes, in-place ops |
| **Patterns** | Opposite direction, same direction, sliding window, fast/slow |
| **Time Complexity** | Usually O(n) vs O(n²) brute force |
| **Space Complexity** | Usually O(1) |
| **Key Insight** | Sorted data lets us eliminate ranges intelligently |
| **Common Errors** | Boundary conditions, duplicates, wrong pointer movement |
| **Pro Tip** | Always ask if array is sorted! |

---

**Remember:** Two pointers is like using both hands to solve a puzzle - it's twice as efficient! When you see a sorted array and need to find pairs or check properties from both ends, think TWO POINTERS! 🚀
