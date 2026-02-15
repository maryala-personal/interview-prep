# Binary Search — Complete Interview Guide

## When to Use This Pattern

**Signals that indicate Binary Search:**
1. The input is a **sorted array** or has a **monotonic property** (if x works, all values beyond x also work, or vice versa)
2. You see keywords like "find minimum/maximum that satisfies", "search", "first/last occurrence"
3. The problem says "O(log n)" or you need to search in a very large space efficiently
4. The problem has a structure where you can **eliminate half the search space** with one comparison
5. "Minimize the maximum" or "maximize the minimum" -- binary search on the answer
6. A **rotated sorted array** is mentioned

**When NOT to use it:**
- Data is unsorted and sorting would destroy needed information
- You need to find ALL elements satisfying a condition (still O(n))
- The search space does not have a monotonic property (no clear way to eliminate half)
- Linked list or other structure without O(1) random access

## Core Mechanics

Binary search works because of the **decision property**: at each step, you can decide which half of the search space to eliminate based on a single comparison. This halves the search space each iteration, giving O(log n) steps.

**The invariant:** The answer (if it exists) always lies within `[left, right]`. Each iteration preserves this by only narrowing the range in a direction that cannot exclude the answer.

**Why O(log n):** Starting with n elements, after k steps you have n/2^k elements. When n/2^k = 1, k = log2(n). For 1 billion elements, that is about 30 comparisons.

**Two common templates:**

1. **`left <= right` template:** Used when searching for a specific value. Terminates when left > right (empty range). Always use `mid +/- 1` to avoid infinite loops.

2. **`left < right` template:** Used when searching for a boundary (first/last occurrence, minimum satisfying condition). Terminates when left == right, which is the answer. Be careful with `mid` calculation to avoid infinite loops.

### ASCII Walkthrough

```
Classic binary search for target=7 in [1, 3, 5, 7, 9, 11, 13]

Step 1: L=0, R=6, mid=3, nums[3]=7 == target -> FOUND

Binary search for target=5 in [1, 3, 5, 7, 9, 11, 13]

Step 1: L=0, R=6, mid=3, nums[3]=7 > 5 -> search left: R=2
         L           M               R
        [1,  3,  5,  7,  9, 11, 13]

Step 2: L=0, R=2, mid=1, nums[1]=3 < 5 -> search right: L=2
         L   M   R
        [1,  3,  5,  7,  9, 11, 13]

Step 3: L=2, R=2, mid=2, nums[2]=5 == 5 -> FOUND
                  LMR
        [1,  3,  5,  7,  9, 11, 13]
```

## The Template

**Template 1: Find exact value**
```python
def binary_search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

**Template 2: Find boundary (leftmost valid)**
```python
def binary_search_left_bound(nums, target):
    left, right = 0, len(nums)
    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left  # first index where nums[index] >= target
```

**Template 3: Binary search on answer space**
```python
def binary_search_on_answer(lo, hi, is_feasible):
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if is_feasible(mid):
            hi = mid  # mid works, try smaller
        else:
            lo = mid + 1  # mid doesn't work, try larger
    return lo
```

```go
func binarySearch(nums []int, target int) int {
	left, right := 0, len(nums)-1
	for left <= right {
		mid := left + (right-left)/2
		if nums[mid] == target {
			return mid
		} else if nums[mid] < target {
			left = mid + 1
		} else {
			right = mid - 1
		}
	}
	return -1
}

func binarySearchOnAnswer(lo, hi int, isFeasible func(int) bool) int {
	for lo < hi {
		mid := lo + (hi-lo)/2
		if isFeasible(mid) {
			hi = mid
		} else {
			lo = mid + 1
		}
	}
	return lo
}
```

## Variant Subpatterns

### 1. Classic Binary Search

Searching for a specific value in a sorted array.

```python
def search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

### 2. Modified Binary Search on Rotated Arrays

The array is sorted but rotated. At each step, at least one half is properly sorted.

```python
def search_rotated(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:  # left half sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:  # right half sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
```

### 3. Binary Search on Answer Space

Instead of searching in an array, binary search on the range of possible answers. Requires a feasibility function with a monotonic property.

```python
def binary_search_answer(lo, hi, feasible):
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

Problems: Koko Eating Bananas, Split Array Largest Sum, Capacity to Ship Packages.

### 4. Binary Search on Two Sorted Arrays

Partition-based binary search to find the median by ensuring equal-sized halves with correct boundary conditions.

Problems: Median of Two Sorted Arrays.

---

## Problem Walkthroughs

---

### Problem: Binary Search (LC #704) — Easy

**Companies:** Every company (foundational)
**Why it is asked:** Tests whether you can implement binary search correctly without off-by-one errors. Surprisingly, many candidates fail this.

**The Brute Force:**
```python
def search_brute(nums, target):
    # O(n) time
    for i in range(len(nums)):
        if nums[i] == target:
            return i
    return -1
```

Linear scan. O(n).

**The Key Insight:** The array is sorted, so each comparison eliminates half of the remaining candidates.

**Optimal Solution:**
```python
def search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

**Dry Run:**
```
Input: nums = [-1, 0, 3, 5, 9, 12], target = 9

Step 1: L=0, R=5, mid=2, nums[2]=3 < 9 -> L=3
Step 2: L=3, R=5, mid=4, nums[4]=9 == 9 -> return 4
```

**Edge Cases:**
- Single element, target matches: return 0.
- Single element, target does not match: return -1.
- Target smaller than all elements: left moves past right, return -1.
- Target larger than all elements: right moves past left, return -1.

**Complexity:** Time O(log n), Space O(1).

**Follow-up questions interviewers might ask:**
- "Why `left + (right - left) // 2` instead of `(left + right) // 2`?" -- Prevents integer overflow in Java/C++.
- "When does the loop terminate?" -- When `left > right`, meaning the search space is empty.

---

### Problem: Find Minimum in Rotated Sorted Array (LC #153) — Medium

**Companies:** Meta, Google, Amazon, Microsoft
**Why it is asked:** Tests your ability to adapt binary search to non-standard sorted arrays. The key challenge is determining which half contains the minimum.

**The Brute Force:**
```python
def findMin_brute(nums):
    # O(n) time
    return min(nums)
```

**The Key Insight:** In a rotated sorted array, the minimum is at the "rotation point" -- the place where a large value is followed by a small value. Compare `nums[mid]` with `nums[right]`: if `nums[mid] > nums[right]`, the rotation point (and hence the minimum) is in the right half. Otherwise, it is in the left half (including mid).

**Optimal Solution:**
```python
def findMin(nums):
    left, right = 0, len(nums) - 1

    while left < right:
        mid = left + (right - left) // 2

        if nums[mid] > nums[right]:
            # Minimum is in the right half (excluding mid)
            left = mid + 1
        else:
            # Minimum is in the left half (including mid)
            right = mid

    return nums[left]
```

**Dry Run:**
```
Input: nums = [3, 4, 5, 1, 2]

Step 1: L=0, R=4, mid=2, nums[2]=5 > nums[4]=2 -> L=3
Step 2: L=3, R=4, mid=3, nums[3]=1 <= nums[4]=2 -> R=3
L==R==3, return nums[3] = 1

Input: nums = [4, 5, 6, 7, 0, 1, 2]

Step 1: L=0, R=6, mid=3, nums[3]=7 > nums[6]=2 -> L=4
Step 2: L=4, R=6, mid=5, nums[5]=1 <= nums[6]=2 -> R=5
Step 3: L=4, R=5, mid=4, nums[4]=0 <= nums[5]=1 -> R=4
L==R==4, return nums[4] = 0
```

**Edge Cases:**
- Not rotated (already sorted): `[1,2,3,4,5]` -- min is at index 0.
- Rotated by 1: `[5,1,2,3,4]` -- min is at index 1.
- Two elements: `[2,1]` -- straightforward.
- Single element: `[1]` -- return it.

**Complexity:** Time O(log n), Space O(1).

**Follow-up questions interviewers might ask:**
- "What if there are duplicates?" -- LC #154. When `nums[mid] == nums[right]`, you cannot determine which half to search. Decrement `right` by 1. This makes worst case O(n) but average case O(log n).
- "Why compare with `nums[right]` and not `nums[left]`?" -- Comparing with `nums[left]` requires more case analysis. Comparing with `nums[right]` cleanly separates the two cases.

---

### Problem: Search in Rotated Sorted Array (LC #33) — Medium

**Companies:** Meta, Google, Amazon, Microsoft, Uber, Apple
**Why it is asked:** Combines rotation detection with binary search. Tests your ability to determine which half is sorted and whether the target lies within it.

**The Brute Force:**
```python
def search_brute(nums, target):
    # O(n) time
    for i in range(len(nums)):
        if nums[i] == target:
            return i
    return -1
```

**The Key Insight:** In a rotated sorted array, at least one half (left or right of mid) is always properly sorted. By checking if the target falls within the sorted half's range, you can decide which half to search. This gives a clear binary decision at each step.

**Optimal Solution:**
```python
def search(nums, target):
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = left + (right - left) // 2

        if nums[mid] == target:
            return mid

        # Left half is sorted
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1  # target is in sorted left half
            else:
                left = mid + 1   # target is in right half
        # Right half is sorted
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1   # target is in sorted right half
            else:
                right = mid - 1  # target is in left half

    return -1
```

**Dry Run:**
```
Input: nums = [4, 5, 6, 7, 0, 1, 2], target = 0

Step 1: L=0, R=6, mid=3, nums[3]=7 != 0
        nums[0]=4 <= nums[3]=7 -> left half [4,5,6,7] is sorted
        Is 4 <= 0 < 7? No -> search right: L=4

Step 2: L=4, R=6, mid=5, nums[5]=1 != 0
        nums[4]=0 <= nums[5]=1 -> left half [0,1] is sorted
        Is 0 <= 0 < 1? Yes -> search left: R=4

Step 3: L=4, R=4, mid=4, nums[4]=0 == 0 -> return 4
```

**Edge Cases:**
- Target not in array: return -1.
- Single element: either matches or does not.
- Array is not rotated (fully sorted): standard binary search works.
- Target at the rotation point.

**Complexity:** Time O(log n), Space O(1).

**Follow-up questions interviewers might ask:**
- "What if there are duplicates?" -- LC #81. When `nums[left] == nums[mid]`, you cannot determine which half is sorted. Increment `left` by 1. Worst case becomes O(n).
- "Can you solve it by first finding the rotation point?" -- Yes, find min index with LC #153, then binary search on the correct half. Two binary searches, still O(log n).

---

### Problem: Koko Eating Bananas (LC #875) — Medium

**Companies:** Google, Meta, Amazon, DoorDash, Uber
**Why it is asked:** The canonical "binary search on answer space" problem. Tests whether you can identify the monotonic property and write a feasibility function.

**The Brute Force:**
```python
import math

def minEatingSpeed_brute(piles, h):
    # O(max(piles) * n) time
    for speed in range(1, max(piles) + 1):
        hours = sum(math.ceil(p / speed) for p in piles)
        if hours <= h:
            return speed
    return max(piles)
```

Try every possible speed from 1 to max(piles). For each speed, calculate total hours. Return the first speed that works. O(max(piles) * n).

**The Key Insight:** The feasibility function is monotonic: if speed k allows finishing within h hours, then any speed > k also allows finishing within h hours. This means we can binary search on the speed. The search space is `[1, max(piles)]`.

**Optimal Solution:**
```python
import math

def minEatingSpeed(piles, h):
    def can_finish(speed):
        hours = 0
        for pile in piles:
            hours += math.ceil(pile / speed)
        return hours <= h

    left, right = 1, max(piles)

    while left < right:
        mid = left + (right - left) // 2
        if can_finish(mid):
            right = mid  # mid works, try slower
        else:
            left = mid + 1  # too slow, need faster

    return left
```

**Dry Run:**
```
Input: piles = [3, 6, 7, 11], h = 8

Search space: [1, 11]

mid=6: hours = ceil(3/6)+ceil(6/6)+ceil(7/6)+ceil(11/6) = 1+1+2+2 = 6 <= 8 -> R=6
mid=3: hours = ceil(3/3)+ceil(6/3)+ceil(7/3)+ceil(11/3) = 1+2+3+4 = 10 > 8 -> L=4
mid=5: hours = ceil(3/5)+ceil(6/5)+ceil(7/5)+ceil(11/5) = 1+2+2+3 = 8 <= 8 -> R=5
mid=4: hours = ceil(3/4)+ceil(6/4)+ceil(7/4)+ceil(11/4) = 1+2+2+3 = 8 <= 8 -> R=4
L==R==4, return 4
```

**Edge Cases:**
- h == len(piles): must eat each pile in one hour, speed = max(piles).
- h is very large: speed = 1 always works.
- Single pile: speed = ceil(pile / h).
- All piles of size 1: speed = 1.

**Complexity:** Time O(n * log(max(piles))), Space O(1). Binary search does O(log(max(piles))) iterations, each calling can_finish which is O(n).

**Follow-up questions interviewers might ask:**
- "How do you know the feasibility function is monotonic?" -- Increasing speed can only decrease or maintain the number of hours needed.
- "What is the search space?" -- `[1, max(piles)]`. Speed of 1 is the minimum possible; max(piles) always works because each pile takes exactly 1 hour.
- "Can you avoid floating point?" -- Use `(pile + speed - 1) // speed` for ceiling division instead of `math.ceil`.

---

### Problem: Median of Two Sorted Arrays (LC #4) — Hard

**Companies:** Google, Amazon, Meta, Microsoft, Goldman Sachs, Apple
**Why it is asked:** One of the hardest binary search problems. Tests deep understanding of partition-based binary search and edge case handling.

**The Brute Force:**
```python
def findMedianSortedArrays_brute(nums1, nums2):
    # O(n + m) time, O(n + m) space
    merged = []
    i = j = 0
    while i < len(nums1) and j < len(nums2):
        if nums1[i] <= nums2[j]:
            merged.append(nums1[i])
            i += 1
        else:
            merged.append(nums2[j])
            j += 1
    merged.extend(nums1[i:])
    merged.extend(nums2[j:])

    n = len(merged)
    if n % 2 == 1:
        return merged[n // 2]
    else:
        return (merged[n // 2 - 1] + merged[n // 2]) / 2
```

Merge the two arrays and find the median. O(n + m) time and space. The problem asks for O(log(n + m)).

**The Key Insight:** We need to find a partition of the two arrays into a "left half" and "right half" such that:
1. The left half has exactly `(n + m + 1) // 2` elements.
2. Every element in the left half <= every element in the right half.

Binary search on the partition point in the shorter array. If we partition nums1 at index i, then we must partition nums2 at index j = `(n + m + 1) // 2 - i`. The partition is valid when `nums1[i-1] <= nums2[j]` and `nums2[j-1] <= nums1[i]`.

**Optimal Solution:**
```python
def findMedianSortedArrays(nums1, nums2):
    # Ensure nums1 is the shorter array
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    n, m = len(nums1), len(nums2)
    half = (n + m + 1) // 2

    left, right = 0, n  # binary search on partition in nums1

    while left <= right:
        i = left + (right - left) // 2  # partition in nums1
        j = half - i                     # partition in nums2

        # Edge values (use -inf and +inf for out-of-bounds)
        nums1_left = nums1[i - 1] if i > 0 else float('-inf')
        nums1_right = nums1[i] if i < n else float('inf')
        nums2_left = nums2[j - 1] if j > 0 else float('-inf')
        nums2_right = nums2[j] if j < m else float('inf')

        if nums1_left <= nums2_right and nums2_left <= nums1_right:
            # Valid partition found
            if (n + m) % 2 == 1:
                return max(nums1_left, nums2_left)
            else:
                return (max(nums1_left, nums2_left) +
                        min(nums1_right, nums2_right)) / 2
        elif nums1_left > nums2_right:
            # nums1 partition is too far right
            right = i - 1
        else:
            # nums1 partition is too far left
            left = i + 1

    return 0  # should never reach here with valid input
```

**Dry Run:**
```
Input: nums1 = [1, 3], nums2 = [2]
n=2, m=1, half=2

L=0, R=2, i=1, j=2-1=1
  nums1_left=nums1[0]=1, nums1_right=nums1[1]=3
  nums2_left=nums2[0]=2, nums2_right=inf
  1 <= inf? Yes. 2 <= 3? Yes. Valid partition!
  Total length=3 (odd). Median = max(1, 2) = 2.0

Input: nums1 = [1, 2], nums2 = [3, 4]
n=2, m=2, half=2

L=0, R=2, i=1, j=2-1=1
  nums1_left=1, nums1_right=2
  nums2_left=3, nums2_right=4
  1 <= 4? Yes. 3 <= 2? No -> left = 2

L=2, R=2, i=2, j=2-2=0
  nums1_left=nums1[1]=2, nums1_right=inf
  nums2_left=-inf, nums2_right=nums2[0]=3
  2 <= 3? Yes. -inf <= inf? Yes. Valid!
  Total length=4 (even). Median = (max(2,-inf) + min(inf,3))/2 = (2+3)/2 = 2.5
```

**Edge Cases:**
- One array is empty: partition entirely from the other array.
- Arrays of very different sizes: binary search on the shorter one ensures O(log(min(n,m))).
- All elements of one array are smaller than all elements of the other.
- Single element in each array.
- Both arrays have one element.

**Complexity:** Time O(log(min(n, m))), Space O(1).

**Follow-up questions interviewers might ask:**
- "Why binary search on the shorter array?" -- Reduces the number of iterations to O(log(min(n,m))).
- "What do the -inf and +inf sentinels represent?" -- When the partition is at the boundary (all elements from one array go to one side), sentinels ensure the comparison always succeeds on that boundary.
- "Can you explain the partition concept?" -- We split the combined array into two halves. The left half contains i elements from nums1 and j elements from nums2. The right half contains the rest. For a valid split, every element in the left half must be <= every element in the right half.

---

### Problem: Split Array Largest Sum (LC #410) — Hard

**Companies:** Google, Amazon, Meta, Microsoft
**Why it is asked:** A classic "binary search on answer space" problem that also has a DP solution. Interviewers want to see you identify the monotonic property and write a clean feasibility check.

**The Brute Force:**
```python
def splitArray_brute(nums, k):
    # DP approach: O(n^2 * k) time, O(n * k) space
    n = len(nums)
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + nums[i]

    # dp[i][j] = minimum largest sum when splitting nums[0:i] into j groups
    dp = [[float('inf')] * (k + 1) for _ in range(n + 1)]
    dp[0][0] = 0

    for i in range(1, n + 1):
        for j in range(1, min(i, k) + 1):
            for m in range(j - 1, i):
                # last group is nums[m:i], sum = prefix[i] - prefix[m]
                dp[i][j] = min(dp[i][j], max(dp[m][j - 1], prefix[i] - prefix[m]))

    return dp[n][k]
```

DP with three loops. O(n^2 * k) time.

**The Key Insight:** Binary search on the answer (the largest sum). The feasibility function checks: "Can we split the array into at most k subarrays such that each subarray sum <= mid?" This function is monotonic: if mid works, then any value > mid also works. Greedy approach: scan left to right, start a new subarray whenever adding the next element would exceed mid.

**Optimal Solution:**
```python
def splitArray(nums, k):
    def can_split(max_sum):
        """Can we split nums into <= k groups, each with sum <= max_sum?"""
        groups = 1
        current_sum = 0
        for num in nums:
            if current_sum + num > max_sum:
                groups += 1
                current_sum = num
                if groups > k:
                    return False
            else:
                current_sum += num
        return True

    left = max(nums)       # minimum possible: each element is its own group
    right = sum(nums)      # maximum possible: one group

    while left < right:
        mid = left + (right - left) // 2
        if can_split(mid):
            right = mid    # mid works, try smaller
        else:
            left = mid + 1 # mid too small, need larger

    return left
```

**Dry Run:**
```
Input: nums = [7, 2, 5, 10, 8], k = 2

Search space: [10, 32]

mid=21: groups: [7,2,5] sum=14, [10,8] sum=18. 2 groups <= 2. Works -> R=21
mid=15: groups: [7,2,5] sum=14, [10] sum=10, [8] sum=8. 3 groups > 2. Fails -> L=16
mid=18: groups: [7,2,5] sum=14, [10,8] sum=18. 2 groups <= 2. Works -> R=18
mid=17: groups: [7,2,5] sum=14, [10] sum=10, but 10+8=18 > 17, so [10],[8]. 3 groups > 2. Fails -> L=18
L==R==18, return 18
```

**Edge Cases:**
- k == 1: answer is sum(nums).
- k == len(nums): answer is max(nums).
- k > len(nums): impossible per constraints, but answer would be max(nums).
- All elements equal: answer is ceil(n/k) * element_value.
- Single element: answer is that element.

**Complexity:** Time O(n * log(sum - max)), Space O(1). Binary search does O(log(sum - max)) iterations, each calling can_split which is O(n).

**Follow-up questions interviewers might ask:**
- "Can you solve it with DP?" -- Yes, O(n^2 * k) DP as shown in brute force. Binary search is better.
- "How is this related to Capacity to Ship Packages?" -- Same pattern: binary search on the capacity with a feasibility greedy check.
- "Is the greedy feasibility check provably correct?" -- Yes, greedy is optimal for this feasibility test because it minimizes the number of groups for a given max sum.

---

## Common Mistakes and Interview Tips

### Top 5 Mistakes

1. **Infinite loops from wrong mid update:** When using `while left < right`, if you set `left = mid` (instead of `mid + 1`) and `mid = left + (right - left) // 2`, you get an infinite loop when `right - left == 1`. Use `mid = left + (right - left + 1) // 2` (round up) when `left = mid`.

2. **Wrong comparison direction in rotated array:** Comparing with `nums[left]` vs `nums[right]` changes the logic. Be consistent. For find-minimum, compare with `nums[right]`. For search, compare with `nums[left]`.

3. **Confusing the search space for answer-space binary search:** Do not binary search on array indices when you should be searching on the answer value. For Koko Eating Bananas, the search space is `[1, max(piles)]`, not indices.

4. **Not handling the `<=` boundary in rotated array search:** When the left half check uses `<` vs `<=`, it changes behavior on edges. `nums[left] <= nums[mid]` (with `=`) is needed to handle the case where `left == mid`.

5. **Off-by-one in the initial search bounds:** For boundary problems, `right = len(nums)` (exclusive) vs `right = len(nums) - 1` (inclusive) changes the template. Match the bounds to the loop condition.

### How to Recognize This Pattern in 30 Seconds

Ask: "Can I phrase this as 'find the minimum/maximum value such that a condition holds, where the condition is monotonic'?" If yes, binary search on the answer. If the array is sorted, direct binary search.

### What Senior/Staff Interviewers Look For

- **Correct template choice:** Know when to use `left <= right` vs `left < right` and the corresponding mid updates.
- **Can you identify the monotonic property?** For answer-space problems, articulate WHY the feasibility is monotonic.
- **Clean feasibility function:** The binary search skeleton is simple; the feasibility check is where the complexity lives. Write it cleanly.
- **Edge case handling:** Especially for Median of Two Sorted Arrays, handling empty partitions with sentinels.
- **Complexity analysis:** Why is binary search on answer O(n log S) and not just O(log S)?

### Communication Tips

1. Identify whether it is "search in sorted array" or "binary search on answer space."
2. For answer-space: state the search range and the monotonic property.
3. Write the feasibility function first, test it mentally, then wrap it in binary search.
4. Walk through one complete binary search iteration showing how the range narrows.
5. Explicitly address off-by-one: state your loop condition and mid update formula.

## Pattern Connections

- **Binary Search on Answer** often combines with a **Greedy** feasibility check (Split Array, Koko Bananas, Ship Packages).
- **Binary Search** on sorted arrays is a prerequisite for **Merge Sort** based problems and **Divide and Conquer**.
- **Rotated Array** problems are binary search combined with **array rotation** properties.
- **Median of Two Sorted Arrays** connects to **partition/selection** algorithms and is a precursor to **kth element** problems.
- When the search space is a tree/graph rather than an array, consider **BFS** (shortest path) or **DFS** (all paths) instead.
- **Binary Search + Prefix Sum** appears in problems like Count of Range Sum and Split Array Largest Sum.
