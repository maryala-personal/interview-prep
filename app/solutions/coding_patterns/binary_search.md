# Binary Search Pattern Guide

## What is Binary Search?

### Explain Like I'm 5
Imagine you're playing a guessing game where I pick a number between 1 and 100, and you need to guess it. I'll tell you if your guess is too high or too low. The smart way to play is to always guess the middle number! If I say "too high," you know the answer is in the lower half. If I say "too low," it's in the upper half. Each guess eliminates half of the possibilities. That's binary search!

Instead of checking every single number one by one (which could take 100 guesses), you can find any number in just 7 guesses maximum!

### Technical Definition
Binary Search is a divide-and-conquer algorithm that efficiently finds a target value within a **sorted** array or search space by repeatedly dividing the search interval in half. It has a time complexity of O(log n), making it vastly superior to linear search O(n) for large datasets.

**Key Requirements:**
- The data must be sorted (or the search space must have monotonic properties)
- Direct access to elements (array-like structure)

## Real-World Analogies

### 1. Phone Book Search
Imagine finding "Smith, John" in a physical phone book:
- You don't start at page 1 and flip through every page
- You open somewhere in the middle
- If you see "Martinez," you know Smith comes after, so you look in the right half
- You keep cutting your search area in half until you find the exact page

### 2. Dictionary Lookup
Looking up the word "python" in a dictionary:
- Open to the middle → see "M"
- "P" comes after "M" → look in right half
- Open middle of right half → see "S"
- "P" comes before "S" → look in left portion of this section
- Continue until you land on "P" section

### 3. Finding a Birthday
Your friend was born in 1995. You ask: "Before or after 1990?" They say "after." Then you ask: "Before or after 2000?" They say "before." You've already narrowed it down to 1990-2000 in just 2 questions!

## When to Use Binary Search

Binary Search should be your go-to when you see these signals:

### Clear Signals:
1. **Sorted Data** - Array is sorted (ascending or descending)
2. **"Find in O(log n)"** - Problem explicitly asks for logarithmic time
3. **Keywords** - "search", "find first", "find last", "find peak", "minimum", "maximum"
4. **Rotated Sorted Arrays** - Array was sorted then rotated
5. **Search Space** - Answer lies in a range [min, max] with monotonic property
6. **"Minimize the maximum"** or **"Maximize the minimum"** - Binary search on answer space

### Pattern Recognition:
- "Find the first/last position of element"
- "Find the smallest element greater than X"
- "Find peak element in mountain array"
- "Allocate pages/painter's partition" type problems
- "Koko eating bananas" style problems
- "Search in 2D matrix" (sorted rows/columns)

### When NOT to Use:
- ❌ Unsorted data (unless you can sort it first, adding O(n log n))
- ❌ Need to find ALL occurrences (might still need O(n))
- ❌ Small datasets (linear search might be faster due to simplicity)
- ❌ Linked lists (no random access - O(1) element access required)

## The Problem: Search in Rotated Sorted Array

**Problem Statement:**
You are given a sorted array that has been rotated at some unknown pivot point. Find the index of a target value. If not found, return -1.

**Example:**
```
Input: nums = [4,5,6,7,0,1,2], target = 0
Output: 4

Input: nums = [4,5,6,7,0,1,2], target = 3
Output: -1

Input: nums = [1], target = 0
Output: -1
```

**Constraints:**
- Array has distinct values
- Array was originally sorted in ascending order
- 1 ≤ nums.length ≤ 5000

## Brute Force Approach

### Strategy
The simplest approach is to scan through the entire array linearly and check each element.

### Code
```python
def search_rotated_brute_force(nums, target):
    """
    Brute force: Check every element one by one

    Args:
        nums: Rotated sorted array
        target: Value to find

    Returns:
        Index of target, or -1 if not found
    """
    # Iterate through every element
    for i in range(len(nums)):
        # If we find the target, return its index
        if nums[i] == target:
            return i

    # Target not found in array
    return -1


# Test cases
print(search_rotated_brute_force([4,5,6,7,0,1,2], 0))  # Output: 4
print(search_rotated_brute_force([4,5,6,7,0,1,2], 3))  # Output: -1
print(search_rotated_brute_force([1], 0))               # Output: -1
```

### Analysis
- **Time Complexity:** O(n) - We potentially check every element
- **Space Complexity:** O(1) - Only using a loop variable
- **Problem:** For large arrays (millions of elements), this is too slow

## Optimized Solution: Binary Search

### Strategy
Even though the array is rotated, **at least one half is always properly sorted**. We can use this property:

1. Find the middle element
2. Determine which half is sorted (left or right)
3. Check if target is in the sorted half
4. If yes, search that half; if no, search the other half
5. Repeat until found or search space exhausted

### Code
```python
def search_rotated_binary_search(nums, target):
    """
    Binary search on rotated sorted array

    Key Insight: At least one half is always sorted.
    We can determine which half is sorted, then check if target
    lies in that range.

    Args:
        nums: Rotated sorted array
        target: Value to find

    Returns:
        Index of target, or -1 if not found
    """
    left = 0
    right = len(nums) - 1

    while left <= right:
        # Calculate middle index (avoiding overflow in other languages)
        mid = left + (right - left) // 2

        # Check if we found the target
        if nums[mid] == target:
            return mid

        # Determine which half is properly sorted
        # If left half is sorted (left element <= mid element)
        if nums[left] <= nums[mid]:
            # Check if target is within sorted left half
            if nums[left] <= target < nums[mid]:
                # Target is in left half, move right pointer
                right = mid - 1
            else:
                # Target is in right half, move left pointer
                left = mid + 1

        # Right half must be sorted
        else:
            # Check if target is within sorted right half
            if nums[mid] < target <= nums[right]:
                # Target is in right half, move left pointer
                left = mid + 1
            else:
                # Target is in left half, move right pointer
                right = mid - 1

    # Target not found
    return -1


# Test cases
print(search_rotated_binary_search([4,5,6,7,0,1,2], 0))  # Output: 4
print(search_rotated_binary_search([4,5,6,7,0,1,2], 3))  # Output: -1
print(search_rotated_binary_search([1], 0))               # Output: -1
print(search_rotated_binary_search([3,1], 1))             # Output: 1
```

### Step-by-Step Example
Let's trace through `nums = [4,5,6,7,0,1,2]`, `target = 0`:

```
Initial: left=0, right=6, array=[4,5,6,7,0,1,2]

Iteration 1:
  mid = 0 + (6-0)//2 = 3
  nums[mid] = 7 (not target)
  nums[left]=4 <= nums[mid]=7 → left half sorted
  Is target in [4,7)? No (0 is not in this range)
  Search right half: left = 4

Iteration 2: left=4, right=6
  mid = 4 + (6-4)//2 = 5
  nums[mid] = 1 (not target)
  nums[left]=0 > nums[mid]=1 → right half sorted
  Is target in (1,2]? No (0 is not in this range)
  Search left half: right = 4

Iteration 3: left=4, right=4
  mid = 4 + (4-4)//2 = 4
  nums[mid] = 0 → FOUND!
  return 4
```

## Time & Space Complexity Analysis

### Brute Force
- **Time:** O(n) - Must potentially check all n elements
- **Space:** O(1) - No extra space needed

### Binary Search
- **Time:** O(log n) - Cut search space in half each iteration
  - Example: Array of 1,000,000 elements needs max 20 comparisons
  - log₂(1,000,000) ≈ 20
- **Space:** O(1) - Only a few pointer variables

### Comparison
| Array Size | Linear Search (worst) | Binary Search (worst) |
|------------|----------------------|----------------------|
| 10         | 10                   | 4                    |
| 100        | 100                  | 7                    |
| 1,000      | 1,000                | 10                   |
| 1,000,000  | 1,000,000            | 20                   |
| 1,000,000,000 | 1,000,000,000     | 30                   |

**Binary search scales beautifully!** When you double the input size, you only need one more comparison.

## Variations of Binary Search

### 1. Classic Binary Search (Sorted Array)

```python
def binary_search_classic(nums, target):
    """Find target in sorted array"""
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = left + (right - left) // 2

        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1  # Search right half
        else:
            right = mid - 1  # Search left half

    return -1
```

### 2. Find First Occurrence (Leftmost)

```python
def find_first_occurrence(nums, target):
    """
    Find the leftmost (first) occurrence of target
    Example: [1,2,2,2,3], target=2 → return 1
    """
    left, right = 0, len(nums) - 1
    result = -1

    while left <= right:
        mid = left + (right - left) // 2

        if nums[mid] == target:
            result = mid        # Store potential answer
            right = mid - 1     # Continue searching left for first occurrence
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return result
```

### 3. Find Last Occurrence (Rightmost)

```python
def find_last_occurrence(nums, target):
    """
    Find the rightmost (last) occurrence of target
    Example: [1,2,2,2,3], target=2 → return 3
    """
    left, right = 0, len(nums) - 1
    result = -1

    while left <= right:
        mid = left + (right - left) // 2

        if nums[mid] == target:
            result = mid        # Store potential answer
            left = mid + 1      # Continue searching right for last occurrence
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return result
```

### 4. Binary Search on Answer Space

This is powerful! Instead of searching in an array, we search for the answer itself.

**Problem:** Koko Eating Bananas
```python
def min_eating_speed(piles, h):
    """
    Koko wants to eat all bananas within h hours.
    Find minimum eating speed k (bananas/hour).

    Key insight: If speed k works, any speed > k also works.
    This monotonic property allows binary search!
    """
    def can_finish(speed):
        """Check if Koko can finish with this speed"""
        hours = 0
        for pile in piles:
            # Ceiling division: how many hours for this pile
            hours += (pile + speed - 1) // speed
        return hours <= h

    # Binary search on the answer (speed)
    left = 1                    # Minimum possible speed
    right = max(piles)          # Maximum needed speed

    while left < right:
        mid = left + (right - left) // 2

        if can_finish(mid):
            right = mid         # This speed works, try slower
        else:
            left = mid + 1      # Too slow, need faster

    return left


# Example
print(min_eating_speed([3,6,7,11], 8))  # Output: 4
```

### 5. Binary Search Template (Lower Bound)

```python
def lower_bound(nums, target):
    """
    Find smallest index where nums[index] >= target
    This is the insertion position for target
    """
    left, right = 0, len(nums)

    while left < right:
        mid = left + (right - left) // 2

        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid

    return left
```

### 6. Binary Search in 2D Matrix

```python
def search_matrix(matrix, target):
    """
    Search in 2D matrix where:
    - Each row is sorted
    - First element of each row > last element of previous row

    Treat as 1D sorted array!
    """
    if not matrix or not matrix[0]:
        return False

    rows, cols = len(matrix), len(matrix[0])
    left, right = 0, rows * cols - 1

    while left <= right:
        mid = left + (right - left) // 2

        # Convert 1D index to 2D coordinates
        row = mid // cols
        col = mid % cols
        mid_value = matrix[row][col]

        if mid_value == target:
            return True
        elif mid_value < target:
            left = mid + 1
        else:
            right = mid - 1

    return False
```

## Pro Tips for Senior Engineers

### 1. Off-by-One Errors (The Eternal Struggle)

**The Loop Condition:**
- `while left <= right` vs `while left < right`
  - Use `left <= right` when you want to check every element
  - Use `left < right` when finding insertion points or bounds

**The Pointer Update:**
- `left = mid + 1` vs `left = mid`
- `right = mid - 1` vs `right = mid`

**Rule of thumb:**
- If you use `left <= right`, you must use `mid ± 1` to avoid infinite loops
- If you use `left < right`, you can use `mid` without `± 1`

### 2. Integer Overflow Prevention

```python
# Bad (can overflow in Java/C++)
mid = (left + right) // 2

# Good (prevents overflow)
mid = left + (right - left) // 2
```

In Python, integers can be arbitrarily large, but this is good practice for interviews.

### 3. When NOT to Use Binary Search

```python
# DON'T: Binary search on unsorted data
def bad_example(nums, target):
    # nums is NOT sorted
    nums = [3, 1, 4, 1, 5, 9, 2, 6]
    # Binary search will give WRONG results!
```

**Exception:** You can sort first if allowed:
```python
nums.sort()  # O(n log n)
# Now binary search is valid: O(log n)
# Total: O(n log n)
```

### 4. The Invariant Pattern

Always maintain a loop invariant:
- "The answer (if exists) is always in [left, right]"
- Each iteration should preserve this invariant
- When loop exits, left and right converge to the answer

### 5. Debugging Binary Search

Add print statements to trace:
```python
while left <= right:
    mid = left + (right - left) // 2
    print(f"left={left}, mid={mid}, right={right}, nums[mid]={nums[mid]}")
    # ... rest of logic
```

### 6. Edge Cases Checklist

Always test:
- ✅ Empty array: `[]`
- ✅ Single element: `[1]`
- ✅ Two elements: `[1, 2]`
- ✅ Target at start: `[target, ...]`
- ✅ Target at end: `[..., target]`
- ✅ Target not in array
- ✅ All elements same: `[5, 5, 5, 5]`
- ✅ Duplicate targets: `[1, 2, 2, 2, 3]`

## Problem Recognition: Spotting Binary Search in Disguise

### Pattern Recognition Framework

| If you see... | Think Binary Search because... |
|--------------|-------------------------------|
| "Sorted array" | Direct application |
| "Rotated sorted array" | Modified binary search |
| "Find minimum/maximum that satisfies..." | Binary search on answer |
| "Minimize the maximum" | Binary search on answer space |
| "Maximize the minimum" | Binary search on answer space |
| "Find first/last occurrence" | Binary search with tracking |
| "Search in O(log n)" | Explicit hint |
| Range of possible answers with monotonic property | Binary search on answer |

### Hard Problems Where Binary Search is Hidden

1. **Capacity to Ship Packages within D Days**
   - Not obvious, but you binary search on the capacity
   - Monotonic: if capacity C works, any C' > C also works

2. **Split Array Largest Sum**
   - Binary search on the "largest sum"
   - Check if we can split array into m parts with max sum ≤ mid

3. **Find K-th Smallest Pair Distance**
   - Binary search on the distance value
   - Count pairs with distance ≤ mid

4. **Median of Two Sorted Arrays**
   - Binary search on partition point
   - Requires deep understanding of binary search

**Recognition Tip:** If you can write a function `isValid(x)` that checks if value `x` works, and this function has monotonic behavior (if x works, all values > x or < x also work), you can binary search!

## Practice Problems

### Easy (Learn the Basics)
1. **Binary Search (LeetCode 704)**
   - Classic implementation
   - Master the template first

2. **Search Insert Position (LeetCode 35)**
   - Find insertion point
   - Practice lower_bound template

3. **First Bad Version (LeetCode 278)**
   - Binary search with API calls
   - Minimize API calls

### Medium (Apply the Pattern)
4. **Find First and Last Position of Element (LeetCode 34)**
   - Two binary searches
   - Practice finding boundaries

5. **Search in Rotated Sorted Array (LeetCode 33)**
   - The classic problem from this guide
   - Understand the sorted half concept

6. **Find Peak Element (LeetCode 162)**
   - Binary search on unsorted array
   - Use comparison with neighbors

7. **Koko Eating Bananas (LeetCode 875)**
   - Binary search on answer space
   - Practice the `canFinish()` pattern

### Hard (Master the Technique)
8. **Median of Two Sorted Arrays (LeetCode 4)**
   - Complex binary search
   - Requires careful partition logic

9. **Split Array Largest Sum (LeetCode 410)**
   - Binary search on answer
   - Tricky validation function

10. **Capacity to Ship Packages (LeetCode 1011)**
    - Similar to split array
    - Good practice for answer space search

## Common Mistakes

### 1. Wrong Loop Termination

```python
# WRONG: Infinite loop risk
while left < right:
    mid = left + (right - left) // 2
    if nums[mid] < target:
        left = mid      # Should be mid + 1
    else:
        right = mid - 1

# When left = 5, right = 6:
# mid = 5, if nums[5] < target, left = 5 again → INFINITE LOOP
```

### 2. Forgetting Mid ± 1

```python
# WRONG: Can miss the answer
while left <= right:
    mid = left + (right - left) // 2
    if nums[mid] < target:
        left = mid      # Should be mid + 1
    else:
        right = mid     # Should be mid - 1
```

### 3. Integer Overflow (Other Languages)

```python
# In Python this is fine, but in Java/C++:
mid = (left + right) // 2  # Can overflow

# Better:
mid = left + (right - left) // 2
```

### 4. Not Handling Edge Cases

```python
# WRONG: Doesn't handle empty array
def search(nums, target):
    left, right = 0, len(nums) - 1
    # If nums is empty, right = -1, but we don't check!

# RIGHT: Add validation
def search(nums, target):
    if not nums:
        return -1
    left, right = 0, len(nums) - 1
```

### 5. Confusing Conditions in Rotated Array

```python
# WRONG: Using strict inequality
if nums[left] < nums[mid]:  # Should be <=
    # This fails when left == mid (small array)

# RIGHT:
if nums[left] <= nums[mid]:
    # Handles all cases correctly
```

### 6. Returning Wrong Value

```python
# WRONG: Returning mid instead of answer variable
def find_first(nums, target):
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            right = mid - 1
        # ... other conditions

    return mid  # WRONG: mid might not be the first occurrence

# RIGHT: Track the result
def find_first(nums, target):
    left, right = 0, len(nums) - 1
    result = -1

    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            result = mid        # Save it
            right = mid - 1
        # ... other conditions

    return result  # Return the tracked result
```

### 7. Search Space Mistakes in Answer Binary Search

```python
# WRONG: Using array indices when searching for value
def min_eating_speed(piles, h):
    left, right = 0, len(piles) - 1  # WRONG!
    # We're searching for speed (value), not index

# RIGHT:
def min_eating_speed(piles, h):
    left, right = 1, max(piles)  # Search speed range
```

---

## Summary

Binary Search is your best friend when:
- Data is sorted (or has monotonic properties)
- You need O(log n) performance
- You're searching in a large dataset

**Remember:**
1. Sorted data = think binary search
2. "Minimize maximum" or "maximize minimum" = binary search on answer
3. Watch out for off-by-one errors (loop conditions!)
4. Test edge cases religiously
5. When in doubt, trace through with a small example

**The Binary Search Mindset:**
> "Can I eliminate half of the search space based on a comparison?"

If yes, binary search is your answer! 🎯

---

*Master binary search, and you'll have a powerful tool for 30% of coding interview problems!*
