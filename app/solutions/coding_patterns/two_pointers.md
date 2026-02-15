# Two Pointers — Complete Interview Guide

## When to Use This Pattern

**Signals that indicate Two Pointers:**
1. The input is a **sorted array or string** and you need to find pairs/triplets satisfying a condition
2. You need to compare elements from **both ends** of a sequence (palindromes, container problems)
3. The problem asks to do something **in-place** with O(1) extra space (remove duplicates, partition)
4. You see keywords like "pair", "triplet", "sorted", "two elements that sum to", "opposite ends"
5. A brute force O(n^2) nested loop checks all pairs, but the sorted property lets you prune
6. Problems involving **area/volume between boundaries** (container, trapping water)

**When NOT to use it:**
- Array is unsorted and sorting destroys needed information (original indices matter) -- use a hash map instead
- You need the shortest subarray/substring satisfying a condition -- that is sliding window
- The search space is not linear or the elements lack a monotonic relationship

## Core Mechanics

The two-pointer technique works because of one core insight: **in a sorted array, moving a pointer in one direction monotonically changes the value, letting you eliminate entire regions of the search space in O(1) time per step.**

Consider finding two numbers in a sorted array that sum to a target. The brute force checks all n*(n-1)/2 pairs. With two pointers at the ends, the sum `nums[left] + nums[right]` tells you exactly which pointer to move:
- Sum too large? Moving `right` left is the only way to decrease it.
- Sum too small? Moving `left` right is the only way to increase it.

Each step eliminates one candidate, so you converge in at most n steps.

**The invariant:** At every moment, the answer (if it exists) lies within the range `[left, right]`. Every pointer movement preserves this invariant by only discarding values that provably cannot be part of the solution.

### ASCII Walkthrough

```
Array: [1, 3, 5, 7, 9, 11], target = 12

Step 1:  L=0(1)  R=5(11)  sum=12  == target  FOUND
         ^                    ^

Array: [1, 3, 5, 7, 9, 11], target = 14

Step 1:  L=0(1)  R=5(11)  sum=12 < 14   move L right
Step 2:  L=1(3)  R=5(11)  sum=14 == 14  FOUND
              ^               ^

Array: [1, 3, 5, 7, 9, 11], target = 10

Step 1:  L=0(1)  R=5(11)  sum=12 > 10   move R left
Step 2:  L=0(1)  R=4(9)   sum=10 == 10  FOUND
         ^            ^
```

**Complexity:** O(n) time because each step moves at least one pointer, and the two pointers collectively traverse at most n positions. O(1) space.

## The Template

```python
def two_pointer_converging(nums, target):
    """Converging two pointers on sorted array."""
    left, right = 0, len(nums) - 1
    while left < right:
        current = nums[left] + nums[right]  # or whatever combination
        if current == target:
            return [left, right]
        elif current < target:
            left += 1
        else:
            right -= 1
    return [-1, -1]
```

```go
func twoPointerConverging(nums []int, target int) []int {
	left, right := 0, len(nums)-1
	for left < right {
		current := nums[left] + nums[right]
		if current == target {
			return []int{left, right}
		} else if current < target {
			left++
		} else {
			right--
		}
	}
	return []int{-1, -1}
}
```

## Variant Subpatterns

### 1. Converging Pointers (left + right moving inward)

Used when you have a sorted structure and need to find combinations from both ends.

```python
def converging_template(nums):
    left, right = 0, len(nums) - 1
    while left < right:
        # compute something with nums[left] and nums[right]
        # decide which pointer to move
        pass
```

Problems: Two Sum II, Container With Most Water, Trapping Rain Water, Valid Palindrome.

### 2. Same-Direction Pointers (slow + fast)

Used for in-place array modifications. The slow pointer marks where to write; the fast pointer scans ahead.

```python
def same_direction_template(nums):
    slow = 0
    for fast in range(len(nums)):
        if some_condition(nums[fast]):
            nums[slow] = nums[fast]
            slow += 1
    return slow  # new length
```

Problems: Remove Duplicates from Sorted Array, Move Zeroes, Remove Element.

### 3. Fixed + Converging (k-Sum reduction)

Fix one (or more) elements with an outer loop, then use converging two pointers on the remainder. This reduces k-Sum from O(n^k) to O(n^(k-1)).

```python
def k_sum_template(nums, target):
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue  # skip duplicates
        left, right = i + 1, len(nums) - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s == target:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif s < target:
                left += 1
            else:
                right -= 1
    return result
```

Problems: 3Sum, 4Sum, 3Sum Closest.

### 4. Subsequence Matching (two independent pointers)

Two pointers scanning different sequences to check if one is a subsequence of another, or to find minimum window subsequences.

```python
def is_subsequence(s, t):
    i = 0  # pointer for s
    for j in range(len(t)):  # pointer for t
        if i < len(s) and s[i] == t[j]:
            i += 1
    return i == len(s)
```

Problems: Is Subsequence, Minimum Window Subsequence.

---

## Problem Walkthroughs

---

### Problem: Two Sum II — Input Array Is Sorted (LC #167) — Easy

**Companies:** Amazon, Google, Meta, Microsoft
**Why it is asked:** Tests whether you can exploit the sorted property to avoid a hash map and achieve O(1) space.

**The Brute Force:**
```python
def twoSum_brute(numbers, target):
    # O(n^2) time, O(1) space
    n = len(numbers)
    for i in range(n):
        for j in range(i + 1, n):
            if numbers[i] + numbers[j] == target:
                return [i + 1, j + 1]  # 1-indexed
    return [-1, -1]
```

The brute force ignores the sorted property entirely. For every element, it scans all subsequent elements looking for a complement. This is wasteful because sorting gives us directional information.

**The Key Insight:** In a sorted array, the sum of the smallest and largest remaining elements tells you which direction to search. If the sum is too small, only increasing the left value can help. If too large, only decreasing the right value can help.

**Optimal Solution:**
```python
def twoSum(numbers, target):
    left, right = 0, len(numbers) - 1
    while left < right:
        s = numbers[left] + numbers[right]
        if s == target:
            return [left + 1, right + 1]  # 1-indexed
        elif s < target:
            left += 1
        else:
            right -= 1
    return [-1, -1]
```

**Dry Run:**
```
Input: numbers = [2, 7, 11, 15], target = 9

Step 1: left=0 (val=2), right=3 (val=15), sum=17 > 9 -> move right
Step 2: left=0 (val=2), right=2 (val=11), sum=13 > 9 -> move right
Step 3: left=0 (val=2), right=1 (val=7),  sum=9 == 9 -> FOUND! Return [1, 2]
```

**Edge Cases:**
- Two elements only: `[1, 2]`, target=3 -- immediately found.
- Negative numbers: `[-3, -1, 0, 2, 4]`, target=1 -- works because array is still sorted.
- Target requires the same value twice: `[1, 3, 3, 5]`, target=6 -- left and right land on different 3s.
- Very large array: O(n) handles it fine.

**Complexity:** Time O(n), Space O(1).

**Follow-up questions interviewers might ask:**
- "What if the array is not sorted?" -- Use a hash map for O(n) time, O(n) space.
- "What if there are multiple valid pairs?" -- This approach finds one; modify to collect all by continuing after a match.
- "Can you prove you never skip the answer?" -- Yes: the invariant is that the answer pair is always within [left, right]. Each move only discards a value that provably cannot be in the answer.

---

### Problem: 3Sum (LC #15) — Medium

**Companies:** Meta, Google, Amazon, Microsoft, Uber, Apple (top-5 most-asked problem)
**Why it is asked:** Tests sorting + two pointers + duplicate handling. The duplicate-skipping logic is where most candidates fail.

**The Brute Force:**
```python
def threeSum_brute(nums):
    # O(n^3) time, O(n) for dedup set
    n = len(nums)
    result_set = set()
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if nums[i] + nums[j] + nums[k] == 0:
                    triplet = tuple(sorted([nums[i], nums[j], nums[k]]))
                    result_set.add(triplet)
    return [list(t) for t in result_set]
```

Three nested loops check every combination. Sorting each triplet and using a set handles duplicates, but O(n^3) is far too slow for n up to 3000.

**The Key Insight:** Sort the array first. Fix one element with an outer loop, then the problem reduces to Two Sum II on the remaining subarray. Skip duplicate values for the fixed element and for the two pointers to avoid duplicate triplets.

**Optimal Solution:**
```python
def threeSum(nums):
    nums.sort()
    result = []
    n = len(nums)

    for i in range(n - 2):
        # Skip duplicate values for the first element
        if i > 0 and nums[i] == nums[i - 1]:
            continue

        # Early termination: if smallest triple > 0, no solution possible
        if nums[i] > 0:
            break

        left, right = i + 1, n - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s == 0:
                result.append([nums[i], nums[left], nums[right]])
                # Skip duplicates for second element
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                # Skip duplicates for third element
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif s < 0:
                left += 1
            else:
                right -= 1

    return result
```

**Dry Run:**
```
Input: nums = [-1, 0, 1, 2, -1, -4]
After sort: [-4, -1, -1, 0, 1, 2]

i=0, nums[i]=-4, target=4
  L=1(-1), R=5(2), sum=1 < 4 -> L++
  L=2(-1), R=5(2), sum=1 < 4 -> L++
  L=3(0),  R=5(2), sum=2 < 4 -> L++
  L=4(1),  R=5(2), sum=3 < 4 -> L++
  L=5 >= R=5, done

i=1, nums[i]=-1, target=1
  L=2(-1), R=5(2), sum=1 == 0? No, -1+(-1)+2=0 == 0 YES
  result = [[-1,-1,2]]
  skip dup L: L=3, skip dup R: R=4
  L=3(0), R=4(1), sum=1 == 0? -1+0+1=0 YES
  result = [[-1,-1,2], [-1,0,1]]
  L=4, R=3, L >= R, done

i=2, nums[i]=-1, same as nums[1], SKIP

i=3, nums[i]=0 > 0? No (0 is not > 0)
  L=4(1), R=5(2), sum=3 > 0 -> R--
  L=4, R=4, done

Result: [[-1,-1,2], [-1,0,1]]
```

**Edge Cases:**
- Array with fewer than 3 elements: return [].
- All zeros: `[0,0,0]` returns `[[0,0,0]]`.
- All positive or all negative: no triplet sums to 0, return [].
- Many duplicates: `[-1,-1,-1,2,2]` must return `[[-1,-1,2]]` only once.

**Complexity:** Time O(n^2) -- sorting is O(n log n), the outer loop with inner two-pointer is O(n^2). Space O(1) ignoring output (O(n) for sorting in some languages).

**Follow-up questions interviewers might ask:**
- "How do you handle duplicates?" -- Skip consecutive equal values for `i`, `left`, and `right`.
- "What if we want all unique quadruplets summing to a target?" -- Add another outer loop for 4Sum.
- "Can you do better than O(n^2)?" -- No, O(n^2) is optimal for 3Sum in the comparison model.

---

### Problem: Container With Most Water (LC #11) — Medium

**Companies:** Meta, Amazon, Google, Microsoft, Goldman Sachs
**Why it is asked:** Tests the greedy insight behind converging two pointers. You need to explain WHY moving the shorter line is correct.

**The Brute Force:**
```python
def maxArea_brute(height):
    # O(n^2) time
    max_water = 0
    n = len(height)
    for i in range(n):
        for j in range(i + 1, n):
            water = min(height[i], height[j]) * (j - i)
            max_water = max(max_water, water)
    return max_water
```

Check every pair of lines. Area = min(height[i], height[j]) * (j - i). This is O(n^2).

**The Key Insight:** Start with the widest container (pointers at both ends). The area is limited by the shorter line. Moving the taller line inward can only decrease width without any guarantee of increasing height. Moving the shorter line inward might find a taller line, potentially increasing the area despite reduced width. So always move the pointer pointing to the shorter line.

**Why this is correct (proof sketch):** When `height[left] < height[right]`, every container using `left` as one boundary has already been considered at its maximum (because `right` gives the maximum width). Any container `(left, j)` for `j < right` has smaller width and is still limited by `height[left]`, so it is provably smaller. We can safely discard `left`.

**Optimal Solution:**
```python
def maxArea(height):
    left, right = 0, len(height) - 1
    max_water = 0

    while left < right:
        w = right - left
        h = min(height[left], height[right])
        max_water = max(max_water, w * h)

        if height[left] < height[right]:
            left += 1
        else:
            right -= 1

    return max_water
```

**Dry Run:**
```
Input: height = [1, 8, 6, 2, 5, 4, 8, 3, 7]

Step 1: L=0(h=1), R=8(h=7), area=min(1,7)*8=8,   max=8,  1<7 -> L++
Step 2: L=1(h=8), R=8(h=7), area=min(8,7)*7=49,  max=49, 8>7 -> R--
Step 3: L=1(h=8), R=7(h=3), area=min(8,3)*6=18,  max=49, 8>3 -> R--
Step 4: L=1(h=8), R=6(h=8), area=min(8,8)*5=40,  max=49, 8==8 -> R--
Step 5: L=1(h=8), R=5(h=4), area=min(8,4)*4=16,  max=49, 8>4 -> R--
Step 6: L=1(h=8), R=4(h=5), area=min(8,5)*3=15,  max=49, 8>5 -> R--
Step 7: L=1(h=8), R=3(h=2), area=min(8,2)*2=4,   max=49, 8>2 -> R--
Step 8: L=1(h=8), R=2(h=6), area=min(8,6)*1=6,   max=49, L+1>=R, done

Answer: 49
```

**Edge Cases:**
- Two elements: only one container possible.
- All same height: area = height * (n-1), found on the first step.
- Strictly increasing: optimal is always the widest pair involving the last element.
- One line is 0: that side contributes nothing, move past it immediately.

**Complexity:** Time O(n), Space O(1).

**Follow-up questions interviewers might ask:**
- "Prove that moving the shorter pointer is correct." -- See proof sketch above.
- "What if you could move either pointer?" -- You would miss the optimal. The greedy choice is provably correct.
- "How does this differ from Trapping Rain Water?" -- Container uses two lines as boundaries; Trapping Rain Water sums water above each bar constrained by the max heights on both sides.

---

### Problem: Trapping Rain Water (LC #42) — Hard

**Companies:** Meta, Google, Amazon, Microsoft, Goldman Sachs, Uber, Apple (extremely common at all top companies)
**Why it is asked:** A classic hard problem that tests multiple approaches (DP, two pointers, stack). Interviewers want to see you reason about the invariant.

**The Brute Force:**
```python
def trap_brute(height):
    # O(n^2) time, O(1) space
    n = len(height)
    total = 0
    for i in range(n):
        left_max = 0
        right_max = 0
        # Find max height to the left
        for j in range(i + 1):
            left_max = max(left_max, height[j])
        # Find max height to the right
        for j in range(i, n):
            right_max = max(right_max, height[j])
        # Water at position i
        total += min(left_max, right_max) - height[i]
    return total
```

For each position, scan left and right to find the tallest bars. The water level at position i is `min(max_left, max_right) - height[i]`. This is O(n^2) because of the inner scans.

**The DP Approach (intermediate step):**
```python
def trap_dp(height):
    # O(n) time, O(n) space
    n = len(height)
    if n == 0:
        return 0

    left_max = [0] * n
    right_max = [0] * n

    left_max[0] = height[0]
    for i in range(1, n):
        left_max[i] = max(left_max[i - 1], height[i])

    right_max[n - 1] = height[n - 1]
    for i in range(n - 2, -1, -1):
        right_max[i] = max(right_max[i + 1], height[i])

    total = 0
    for i in range(n):
        total += min(left_max[i], right_max[i]) - height[i]
    return total
```

This precomputes left_max and right_max arrays. O(n) time but O(n) space. The two-pointer approach eliminates the extra space.

**The Key Insight:** We do not need both left_max and right_max at every position simultaneously. If `left_max < right_max`, the water at the left pointer is determined by left_max regardless of what happens further right (because right_max is at least as large). So we can process from whichever side has the smaller known maximum, maintaining running maxima from both sides.

**Optimal Solution (Two Pointers):**
```python
def trap(height):
    if not height:
        return 0

    left, right = 0, len(height) - 1
    left_max, right_max = height[left], height[right]
    total = 0

    while left < right:
        if left_max < right_max:
            left += 1
            left_max = max(left_max, height[left])
            total += left_max - height[left]
        else:
            right -= 1
            right_max = max(right_max, height[right])
            total += right_max - height[right]

    return total
```

**Why `left_max - height[left]` works when `left_max < right_max`:** The water level at position `left` is `min(left_max, actual_right_max_for_this_position)`. We know `actual_right_max >= right_max >= left_max` (because right_max only increases as we move inward, and actual_right_max includes right_max). So `min(left_max, actual_right_max) = left_max`. The water trapped is `left_max - height[left]`.

**Dry Run:**
```
Input: height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]

L=0, R=11, lmax=0, rmax=1
  lmax(0) < rmax(1): L++ -> L=1, lmax=max(0,1)=1, water+=1-1=0, total=0
  lmax(1) >= rmax(1): R-- -> R=10, rmax=max(1,2)=2, water+=2-2=0, total=0
  lmax(1) < rmax(2): L++ -> L=2, lmax=max(1,0)=1, water+=1-0=1, total=1
  lmax(1) < rmax(2): L++ -> L=3, lmax=max(1,2)=2, water+=2-2=0, total=1
  lmax(2) >= rmax(2): R-- -> R=9, rmax=max(2,1)=2, water+=2-1=1, total=2
  lmax(2) >= rmax(2): R-- -> R=8, rmax=max(2,2)=2, water+=2-2=0, total=2
  lmax(2) >= rmax(2): R-- -> R=7, rmax=max(2,3)=3, water+=3-3=0, total=2
  lmax(2) < rmax(3): L++ -> L=4, lmax=max(2,1)=2, water+=2-1=1, total=3
  lmax(2) < rmax(3): L++ -> L=5, lmax=max(2,0)=2, water+=2-0=2, total=5
  lmax(2) < rmax(3): L++ -> L=6, lmax=max(2,1)=2, water+=2-1=1, total=6
  L=6, R=7, lmax(2) < rmax(3): L++ -> L=7, L>=R, done

Answer: 6
```

**Edge Cases:**
- Empty array or length < 3: return 0 (cannot trap water).
- Monotonically increasing or decreasing: no water trapped.
- All same height: no water trapped.
- Single peak (mountain): water trapped on both sides.

**Complexity:** Time O(n), Space O(1).

**Follow-up questions interviewers might ask:**
- "Can you solve it with a stack?" -- Yes, monotonic stack approach, O(n) time and space.
- "Can you solve it with DP?" -- Yes, precompute left_max[] and right_max[], O(n) time and space.
- "How does this generalize to 2D?" -- LC #407, Trapping Rain Water II uses a min-heap BFS approach.
- "What is the invariant in the two-pointer approach?" -- When processing from the side with the smaller max, the water level at that position is determined solely by that max.

---

### Problem: 4Sum (LC #18) — Hard

**Companies:** Amazon, Google, Meta, Microsoft
**Why it is asked:** Tests whether you can generalize 3Sum and handle edge cases/duplicates at multiple levels.

**The Brute Force:**
```python
def fourSum_brute(nums, target):
    # O(n^4) time
    n = len(nums)
    result_set = set()
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                for l in range(k + 1, n):
                    if nums[i] + nums[j] + nums[k] + nums[l] == target:
                        quad = tuple(sorted([nums[i], nums[j], nums[k], nums[l]]))
                        result_set.add(quad)
    return [list(q) for q in result_set]
```

Four nested loops with set-based deduplication. O(n^4) is impractical for n up to 200.

**The Key Insight:** Reduce to 3Sum, which itself reduces to 2Sum. Fix the first element, fix the second element, then use two pointers on the remainder. This gives O(n^3). Duplicate skipping at every level prevents duplicate quadruplets.

**Optimal Solution:**
```python
def fourSum(nums, target):
    nums.sort()
    result = []
    n = len(nums)

    for i in range(n - 3):
        # Skip duplicate first element
        if i > 0 and nums[i] == nums[i - 1]:
            continue

        # Pruning: if minimum possible sum > target, stop
        if nums[i] + nums[i + 1] + nums[i + 2] + nums[i + 3] > target:
            break
        # Pruning: if maximum possible sum with nums[i] < target, skip
        if nums[i] + nums[n - 3] + nums[n - 2] + nums[n - 1] < target:
            continue

        for j in range(i + 1, n - 2):
            # Skip duplicate second element
            if j > i + 1 and nums[j] == nums[j - 1]:
                continue

            # Pruning
            if nums[i] + nums[j] + nums[j + 1] + nums[j + 2] > target:
                break
            if nums[i] + nums[j] + nums[n - 2] + nums[n - 1] < target:
                continue

            left, right = j + 1, n - 1
            while left < right:
                s = nums[i] + nums[j] + nums[left] + nums[right]
                if s == target:
                    result.append([nums[i], nums[j], nums[left], nums[right]])
                    while left < right and nums[left] == nums[left + 1]:
                        left += 1
                    while left < right and nums[right] == nums[right - 1]:
                        right -= 1
                    left += 1
                    right -= 1
                elif s < target:
                    left += 1
                else:
                    right -= 1

    return result
```

**Dry Run:**
```
Input: nums = [1, 0, -1, 0, -2, 2], target = 0
After sort: [-2, -1, 0, 0, 1, 2]

i=0, nums[0]=-2
  j=1, nums[1]=-1, need two that sum to 3
    L=2(0), R=5(2), s=-2-1+0+2=-1 < 0 -> L++
    L=3(0), R=5(2), s=-2-1+0+2=-1 < 0 -> L++
    L=4(1), R=5(2), s=-2-1+1+2=0 == 0 -> FOUND [-2,-1,1,2]
    L=5, R=4, done

  j=2, nums[2]=0, need two that sum to 2
    L=3(0), R=5(2), s=-2+0+0+2=0 == 0 -> FOUND [-2,0,0,2]
    skip dup L, skip dup R: L=4, R=4, done

  j=3, nums[3]=0 == nums[2]=0, SKIP

i=1, nums[1]=-1
  j=2, nums[2]=0, need two that sum to 1
    L=3(0), R=5(2), s=-1+0+0+2=1 == 0? No, 1 > 0 -> R--
    L=3(0), R=4(1), s=-1+0+0+1=0 == 0 -> FOUND [-1,0,0,1]
    L=4, R=3, done

  j=3, nums[3]=0 == nums[2], SKIP

i=2, nums[2]=0, min sum=0+0+1+2=3 > 0, BREAK

Result: [[-2,-1,1,2], [-2,0,0,2], [-1,0,0,1]]
```

**Edge Cases:**
- Less than 4 elements: return [].
- All elements equal: `[0,0,0,0]`, target=0 returns `[[0,0,0,0]]`.
- Large target requiring all four largest: pruning catches this early.
- Integer overflow: In Python this is not an issue, but in Java/C++ use `long`.

**Complexity:** Time O(n^3), Space O(1) ignoring output. The pruning significantly helps in practice.

**Follow-up questions interviewers might ask:**
- "Can you generalize to k-Sum?" -- Yes, recursively reduce k-Sum to (k-1)-Sum until 2Sum.
- "Can you do better than O(n^3)?" -- With a hash map of pair sums, O(n^2) time O(n^2) space is possible, but handling duplicates becomes much harder.
- "What are the pruning conditions?" -- If the minimum possible sum exceeds target, break. If the maximum possible sum is less than target, continue to the next iteration.

---

### Problem: Minimum Window Subsequence (LC #727) — Hard

**Companies:** Google, Meta, Amazon
**Why it is asked:** Tests a less common two-pointer variant: forward scan to find a match, then backward scan to minimize the window. This is a common follow-up after "Is Subsequence" (LC #392).

**The Brute Force:**
```python
def minWindow_brute(s1, s2):
    # O(n^2 * m) time where n = len(s1), m = len(s2)
    best = ""
    n = len(s1)
    for i in range(n):
        for j in range(i + len(s2), n + 1):
            window = s1[i:j]
            # Check if s2 is a subsequence of window
            k = 0
            for ch in window:
                if k < len(s2) and ch == s2[k]:
                    k += 1
            if k == len(s2):
                if best == "" or len(window) < len(best):
                    best = window
                break  # No need to extend further from this i
    return best
```

For every starting position, find the shortest substring that contains s2 as a subsequence. O(n^2 * m) in the worst case.

**The Key Insight:** Use a two-phase approach:
1. **Forward scan:** Use a pointer on s2 to find a window in s1 that contains s2 as a subsequence (by matching characters left to right).
2. **Backward scan:** Once a complete match is found, scan backwards from the end of the match to find the latest possible start, which gives the shortest window ending at this position.
3. Restart the forward scan from `start + 1` to find potentially shorter windows.

**Optimal Solution:**
```python
def minWindow(s1, s2):
    m, n = len(s1), len(s2)
    best_start = -1
    best_len = float('inf')

    i = 0  # pointer in s1
    while i < m:
        # Phase 1: Forward scan -- find a window containing s2 as subsequence
        j = 0  # pointer in s2
        start = i
        while i < m and j < n:
            if s1[i] == s2[j]:
                j += 1
            i += 1

        if j < n:
            break  # Could not match all of s2, done

        # Phase 2: Backward scan -- shrink the window from the right
        # i is now one past the last matched character
        end = i - 1
        j = n - 1
        while j >= 0:
            if s1[end] == s2[j]:
                j -= 1
            end -= 1
        end += 1  # end is now the start of the minimum window

        window_len = i - end
        if window_len < best_len:
            best_len = window_len
            best_start = end

        # Restart search from end + 1
        i = end + 1

    return "" if best_start == -1 else s1[best_start:best_start + best_len]
```

**Dry Run:**
```
Input: s1 = "abcdebdde", s2 = "bde"

Forward scan from i=0:
  i=0 'a' != 'b', i=1 'b' == 'b' j=1, i=2 'c' != 'd', i=3 'd' == 'd' j=2,
  i=4 'e' == 'e' j=3, j==n, match found. i=5.

Backward scan from end=4:
  end=4 'e' == 'e' j=1, end=3 'd' == 'd' j=0, end=2 skip 'c',
  end=1 'b' == 'b' j=-1, done. end=2.
  Window = s1[2:5] = "cde"? Wait: end+1=2, window = s1[2:5] = "cde", len=3.
  Actually end was decremented to 1, then end+1 = 2.
  s1[2:5] = "cde" -- but let me re-check.
  After backward: end goes 4->3->2->1, then end+1=2. i=5, window_len=5-2=3.
  s1[2:5] = "cde". But is "bde" a subsequence of "cde"? No!

Let me re-trace more carefully:
  Backward scan: j starts at n-1 = 2 (s2[2]='e')
  end=4: s1[4]='e' == s2[2], j=1, end=3
  end=3: s1[3]='d' == s2[1], j=0, end=2
  end=2: s1[2]='c' != s2[0]='b', end=1
  end=1: s1[1]='b' == s2[0], j=-1, end=0
  j < 0, exit. end += 1 = 1.
  Window = s1[1:5] = "bcde", len=4.

Restart from i = 1 + 1 = 2.

Forward scan from i=2:
  i=2 'c' skip, i=3 'd' skip, i=4 'e' skip, i=5 'b' == 'b' j=1,
  i=6 'd' == 'd' j=2, i=7 'd' skip, i=8 'e' == 'e' j=3, match. i=9.

Backward scan from end=8:
  end=8 'e'=='e' j=1, end=7 'd' skip (s2[1]='d') wait s2[1]='d', s1[7]='d'=='d' j=0,
  end=6 'd' skip (s2[0]='b'), end=5 'b'=='b' j=-1, end=4.
  end+1=5. window = s1[5:9] = "bdde", len=4.

Restart from i=6. Forward scan:
  i=6 'd' skip, i=7 'd'=='d'? No, s2[0]='b'. i=8 'e' skip. i=9, j=0 < n, break.

best = "bcde" (len 4). Answer: "bcde"
```

**Edge Cases:**
- s2 longer than s1: return "".
- s2 not a subsequence of s1 at all: return "".
- s1 == s2: return s1.
- Single character s2: find first occurrence in s1.

**Complexity:** Time O(n * m) worst case where n=len(s1), m=len(s2). Each character in s1 is visited at most 2*m times across all forward and backward scans. Space O(1).

**Follow-up questions interviewers might ask:**
- "Can you improve to O(n * m) guaranteed with DP?" -- Yes, use a DP table where dp[i][j] stores the largest index in s1 such that s2[0..j] is a subsequence starting from that index, ending at i. This is cleaner but uses O(n * m) space.
- "What if s2 can have wildcards?" -- Modify the matching condition in both forward and backward scans.
- "How does this differ from Minimum Window Substring?" -- Minimum Window Substring checks for character frequency containment (a multiset problem using sliding window), not subsequence ordering.

---

## Common Mistakes and Interview Tips

### Top 5 Mistakes

1. **Moving the wrong pointer:** When the sum is too small, you need to increase it (move left pointer right). When too large, decrease it (move right pointer left). Drawing a quick example prevents this.

2. **Not skipping duplicates in k-Sum problems:** After finding a valid triplet/quadruplet, you must skip duplicate values for ALL pointers. Forgetting this is the number one source of wrong answers on 3Sum.

3. **Using `<=` instead of `<` for the loop condition:** For converging pointers looking for pairs, `while left < right` is correct. Using `<=` would compare an element with itself.

4. **Forgetting to sort:** Two-pointer converging only works on sorted arrays. Always sort first unless the array is given sorted. But watch out -- if sorting destroys needed information (e.g., original indices), use a hash map approach instead.

5. **Integer overflow in other languages:** When summing multiple numbers, the intermediate sum can overflow in Java/C++. Use `long` or restructure the comparison as subtraction.

### How to Recognize This Pattern in 30 Seconds

Ask yourself: "Is the input sorted (or can I sort it), and am I looking for pairs/triplets satisfying a sum or comparison condition?" If yes, two pointers. If the input is unsorted and you need original indices, use a hash map instead.

### What Senior/Staff Interviewers Look For

- **Can you articulate the invariant?** Not just "we use two pointers" but "we maintain the invariant that the answer lies within [left, right], and each pointer move discards values that cannot be part of any answer."
- **Do you handle duplicates correctly and explain why?**
- **Can you prove the greedy choice is correct?** Especially for Container With Most Water and Trapping Rain Water.
- **Do you discuss the time/space tradeoff vs. hash map approaches?**
- **Clean, bug-free code on the first attempt.** Off-by-one errors and wrong pointer movements are red flags.

### Communication Tips

1. Start by stating the brute force and its complexity.
2. Identify the key insight that enables optimization ("since the array is sorted, we can...").
3. State the invariant before writing code.
4. Walk through a small example as you code.
5. After coding, explicitly state time and space complexity with brief justification.

## Pattern Connections

- **Two Pointers + Sorting** naturally leads to **k-Sum** problems (3Sum, 4Sum).
- **Two Pointers on strings** connects to **Sliding Window** when the window is defined by character conditions rather than sum conditions.
- **Converging pointers** on heights connects to **Monotonic Stack** (another way to solve Trapping Rain Water).
- **Subsequence matching with two pointers** connects to **DP** for more complex subsequence problems (edit distance, LCS).
- When an array is not sorted, **Hash Map** often replaces two pointers (unsorted Two Sum).
- **Binary Search** can be viewed as a special case of two pointers where one pointer (mid) is computed rather than advanced linearly.
