# Prefix Sum — Complete Interview Guide

## When to Use This Pattern

**Signals that indicate Prefix Sum:**
1. The problem asks for the **sum of a subarray** or **range query** on an array
2. Keywords: "subarray sum equals k", "range sum", "cumulative sum", "contiguous subarray sum"
3. You need to compute sums for **many different subarrays** efficiently
4. The brute force involves recomputing subarray sums from scratch for each query
5. The problem involves **counting subarrays** with a specific sum property
6. 2D matrix sum queries (sum of a sub-rectangle)

**When NOT to use it:**
- The problem involves **subsequences** (non-contiguous) rather than subarrays
- The array is being modified between queries -- use a segment tree or BIT instead
- The condition involves multiplication/division rather than addition/subtraction
- The problem asks for maximum/minimum subarray rather than a specific sum -- use Kadane's algorithm or sliding window

## Core Mechanics

A **prefix sum array** `P` is defined as `P[i] = nums[0] + nums[1] + ... + nums[i-1]` (with `P[0] = 0`). The sum of any subarray `nums[i..j]` can be computed in O(1) as `P[j+1] - P[i]`.

**Why it works:** Addition is associative and has an inverse (subtraction). If we know the cumulative sum up to any point, the sum of any range is the difference of two prefix sums.

**The key formula:**
```
sum(nums[i..j]) = prefix[j+1] - prefix[i]
```

**Prefix Sum + Hash Map pattern:** When counting subarrays with sum equal to k, we scan left to right maintaining a running prefix sum. If `prefix_sum - k` has been seen before (stored in a hash map), then there exists a subarray ending at the current position with sum k. The hash map counts how many times each prefix sum value has occurred.

**Why Prefix Sum + Hash Map works:** If `prefix[j] - prefix[i] = k`, then `prefix[i] = prefix[j] - k`. By storing prefix sums in a hash map as we go, we can check in O(1) whether there exists an earlier prefix sum that would make the current subarray sum equal to k.

### ASCII Walkthrough

```
Array:     [1, 2, 3, 4, 5]
Prefix:  [0, 1, 3, 6, 10, 15]
           ^  ^  ^  ^   ^   ^
          P0 P1 P2 P3  P4  P5

Sum of nums[1..3] = P[4] - P[1] = 10 - 1 = 9
  (which is 2 + 3 + 4 = 9)

Sum of nums[0..4] = P[5] - P[0] = 15 - 0 = 15
  (which is 1 + 2 + 3 + 4 + 5 = 15)

Sum of nums[2..2] = P[3] - P[2] = 6 - 3 = 3
  (which is just 3)
```

### 2D Prefix Sum

For a 2D matrix, `P[r][c]` = sum of all elements in the rectangle from `(0,0)` to `(r-1,c-1)`.

```
Sum of rectangle (r1,c1) to (r2,c2) =
  P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]
```

This uses inclusion-exclusion to compute any sub-rectangle sum in O(1).

## The Template

**1D Prefix Sum:**
```python
def build_prefix_sum(nums):
    n = len(nums)
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + nums[i]
    return prefix

def range_sum(prefix, i, j):
    """Sum of nums[i..j] inclusive."""
    return prefix[j + 1] - prefix[i]
```

**Prefix Sum + Hash Map (count subarrays with sum k):**
```python
def count_subarrays_with_sum_k(nums, k):
    count = 0
    prefix_sum = 0
    seen = {0: 1}  # prefix_sum -> count of occurrences

    for num in nums:
        prefix_sum += num
        if prefix_sum - k in seen:
            count += seen[prefix_sum - k]
        seen[prefix_sum] = seen.get(prefix_sum, 0) + 1

    return count
```

**2D Prefix Sum:**
```python
def build_2d_prefix(matrix):
    if not matrix:
        return []
    rows, cols = len(matrix), len(matrix[0])
    prefix = [[0] * (cols + 1) for _ in range(rows + 1)]
    for r in range(rows):
        for c in range(cols):
            prefix[r+1][c+1] = (matrix[r][c] + prefix[r][c+1]
                                + prefix[r+1][c] - prefix[r][c])
    return prefix

def region_sum(prefix, r1, c1, r2, c2):
    """Sum of matrix[r1..r2][c1..c2] inclusive."""
    return (prefix[r2+1][c2+1] - prefix[r1][c2+1]
            - prefix[r2+1][c1] + prefix[r1][c1])
```

```go
func buildPrefixSum(nums []int) []int {
	prefix := make([]int, len(nums)+1)
	for i, num := range nums {
		prefix[i+1] = prefix[i] + num
	}
	return prefix
}

func countSubarraysWithSumK(nums []int, k int) int {
	count := 0
	prefixSum := 0
	seen := map[int]int{0: 1}

	for _, num := range nums {
		prefixSum += num
		if v, ok := seen[prefixSum-k]; ok {
			count += v
		}
		seen[prefixSum]++
	}
	return count
}
```

## Variant Subpatterns

### 1. Basic Prefix Sum (Range Queries)

Precompute prefix sums, answer range sum queries in O(1).

Problems: Range Sum Query (Immutable), Running Sum of 1D Array.

### 2. Prefix Sum + Hash Map (Count/Find Subarrays)

Maintain running prefix sum and a hash map of previously seen prefix sums. When `prefix - k` exists in the map, we have found a subarray with sum k.

Problems: Subarray Sum Equals K, Max Size Subarray Sum Equals k, Continuous Subarray Sum.

### 3. 2D Prefix Sum

Extend prefix sums to 2D matrices for O(1) sub-rectangle queries.

Problems: Range Sum Query 2D, Number of Submatrices That Sum to Target.

### 4. Prefix Sum + Binary Search / Sorted Structure

When the condition involves inequalities (sum <= k, count of range sums), combine prefix sums with sorted containers or binary search.

Problems: Count of Range Sum, Max Sum of Rectangle No Larger Than K.

---

## Problem Walkthroughs

---

### Problem: Subarray Sum Equals K (LC #560) — Medium

**Companies:** Meta, Google, Amazon, Microsoft (one of the most asked medium problems)
**Why it is asked:** Tests the prefix sum + hash map technique. Simple to state, but the hash map insight is not obvious.

**The Brute Force:**
```python
def subarraySum_brute(nums, k):
    # O(n^2) time, O(1) space
    count = 0
    n = len(nums)
    for i in range(n):
        total = 0
        for j in range(i, n):
            total += nums[j]
            if total == k:
                count += 1
    return count
```

For each starting index, extend the subarray and check the sum. O(n^2).

**The Key Insight:** If the prefix sum at index j is `P[j]` and we want a subarray ending at j with sum k, we need `P[j] - P[i] = k` for some i < j, i.e., `P[i] = P[j] - k`. Using a hash map to store prefix sum frequencies lets us count valid `i` values in O(1).

**Optimal Solution:**
```python
def subarraySum(nums, k):
    count = 0
    prefix_sum = 0
    seen = {0: 1}  # base case: empty prefix has sum 0

    for num in nums:
        prefix_sum += num
        target = prefix_sum - k
        if target in seen:
            count += seen[target]
        seen[prefix_sum] = seen.get(prefix_sum, 0) + 1

    return count
```

**Dry Run:**
```
Input: nums = [1, 1, 1], k = 2

prefix=0: seen={0:1}
num=1: prefix=1, target=1-2=-1, not in seen. seen={0:1, 1:1}
num=1: prefix=2, target=2-2=0, 0 in seen with count 1 -> count=1. seen={0:1, 1:1, 2:1}
num=1: prefix=3, target=3-2=1, 1 in seen with count 1 -> count=2. seen={0:1, 1:1, 2:1, 3:1}

Answer: 2 (subarrays [1,1] at indices 0-1 and 1-2)

Input: nums = [1, 2, 3], k = 3

prefix=0: seen={0:1}
num=1: prefix=1, target=-2, not in seen. seen={0:1, 1:1}
num=2: prefix=3, target=0, in seen -> count=1. seen={0:1, 1:1, 3:1}
num=3: prefix=6, target=3, in seen -> count=2. seen={0:1, 1:1, 3:1, 6:1}

Answer: 2 (subarrays [1,2] and [3])
```

**Edge Cases:**
- k = 0: counts subarrays with sum 0 (e.g., [1, -1]).
- Negative numbers: the hash map approach handles them correctly.
- Single element equal to k: count = 1.
- All zeros, k = 0: every subarray sums to 0, count = n*(n+1)/2.

**Complexity:** Time O(n), Space O(n) for the hash map.

**Follow-up questions interviewers might ask:**
- "Why do we initialize seen with {0: 1}?" -- To handle the case where a prefix sum itself equals k (subarray from index 0).
- "Does this work with negative numbers?" -- Yes, unlike sliding window which requires non-negative numbers.
- "Can you find the actual subarrays, not just count?" -- Store indices in the hash map instead of counts.
- "Why not sliding window?" -- Sliding window requires a monotonic property (expanding always increases sum). Negative numbers break this.

---

### Problem: Continuous Subarray Sum (LC #523) — Medium

**Companies:** Meta (very frequently asked), Google, Amazon
**Why it is asked:** Tests prefix sum with modular arithmetic. The key trick is that if two prefix sums have the same remainder mod k, the subarray between them has a sum divisible by k.

**The Brute Force:**
```python
def checkSubarraySum_brute(nums, k):
    # O(n^2) time
    n = len(nums)
    for i in range(n):
        total = 0
        for j in range(i, n):
            total += nums[j]
            if j - i >= 1 and total % k == 0:  # length >= 2
                return True
    return False
```

**The Key Insight:** If `prefix[j] % k == prefix[i] % k`, then `(prefix[j] - prefix[i]) % k == 0`, meaning the subarray `nums[i..j-1]` has a sum divisible by k. We need the subarray to have length >= 2, so we check that `j - i >= 2`. Store the **first** occurrence of each remainder in a hash map.

**Optimal Solution:**
```python
def checkSubarraySum(nums, k):
    remainder_map = {0: -1}  # remainder -> earliest index
    prefix_sum = 0

    for i, num in enumerate(nums):
        prefix_sum += num
        remainder = prefix_sum % k

        if remainder in remainder_map:
            if i - remainder_map[remainder] >= 2:
                return True
        else:
            remainder_map[remainder] = i

    return False
```

**Dry Run:**
```
Input: nums = [23, 2, 4, 6, 7], k = 6

prefix=0: remainder_map={0:-1}
i=0, num=23: prefix=23, rem=23%6=5. Not in map. map={0:-1, 5:0}
i=1, num=2:  prefix=25, rem=25%6=1. Not in map. map={0:-1, 5:0, 1:1}
i=2, num=4:  prefix=29, rem=29%6=5. In map at index 0. 2-0=2 >= 2 -> True!

Subarray [2, 4] has sum 6, divisible by 6.

Wait, let me verify: the subarray is nums[1..2] = [2, 4], sum = 6. Yes!
Actually prefix[3] - prefix[1] = 29 - 23 = 6. Correct.
```

**Edge Cases:**
- k = 1: any subarray of length >= 2 works (every integer is divisible by 1).
- Two consecutive zeros: `[0, 0]` sum = 0, which is divisible by any k. Return True.
- Subarray must have length >= 2 (problem constraint).
- All elements are multiples of k.

**Complexity:** Time O(n), Space O(min(n, k)) for the hash map (at most k distinct remainders).

**Follow-up questions interviewers might ask:**
- "Why store the first index, not the last?" -- We want the longest possible subarray to maximize the chance of length >= 2. Storing the first index of each remainder gives us the longest subarray with that remainder difference.
- "What if k is 0?" -- The problem guarantees k >= 1 in recent versions, but if k = 0, we look for subarrays with sum exactly 0.
- "How does modular arithmetic help?" -- Two prefix sums with the same remainder mod k means their difference is divisible by k.

---

### Problem: Range Sum Query 2D — Immutable (LC #304) — Medium

**Companies:** Meta, Google, Amazon
**Why it is asked:** Tests 2D prefix sum construction and the inclusion-exclusion formula for rectangle queries.

**The Brute Force:**
```python
class NumMatrix_brute:
    def __init__(self, matrix):
        self.matrix = matrix

    def sumRegion(self, r1, c1, r2, c2):
        # O(m * n) per query
        total = 0
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                total += self.matrix[r][c]
        return total
```

Each query iterates over the entire rectangle. O(m * n) per query.

**The Key Insight:** Precompute a 2D prefix sum matrix. `P[r][c]` = sum of all elements in `matrix[0..r-1][0..c-1]`. Any rectangle sum can be computed in O(1) using inclusion-exclusion:

```
sum(r1,c1,r2,c2) = P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]
```

**Optimal Solution:**
```python
class NumMatrix:
    def __init__(self, matrix):
        if not matrix or not matrix[0]:
            self.prefix = []
            return

        rows, cols = len(matrix), len(matrix[0])
        self.prefix = [[0] * (cols + 1) for _ in range(rows + 1)]

        for r in range(rows):
            for c in range(cols):
                self.prefix[r+1][c+1] = (matrix[r][c]
                    + self.prefix[r][c+1]
                    + self.prefix[r+1][c]
                    - self.prefix[r][c])

    def sumRegion(self, r1, c1, r2, c2):
        return (self.prefix[r2+1][c2+1]
                - self.prefix[r1][c2+1]
                - self.prefix[r2+1][c1]
                + self.prefix[r1][c1])
```

**Dry Run:**
```
Matrix:
  3 0 1 4 2
  5 6 3 2 1
  1 2 0 1 5
  4 1 0 1 7
  1 0 3 0 5

Prefix (1-indexed):
    0  0  0  0  0  0
    0  3  3  4  8 10
    0  8 14 18 24 27
    0  9 17 21 28 36
    0 13 22 26 34 49
    0 14 23 30 38 58

sumRegion(2, 1, 4, 3):
  = P[5][4] - P[2][4] - P[5][1] - P[2][1]
  Wait, let me use the formula correctly:
  = P[4+1][3+1] - P[2][3+1] - P[4+1][1] + P[2][1]
  = P[5][4] - P[2][4] - P[5][1] + P[2][1]
  = 38 - 24 - 14 + 14 = 14? Hmm let me verify.

  Actually: matrix[2][1]+matrix[2][2]+matrix[2][3] = 2+0+1 = 3
            matrix[3][1]+matrix[3][2]+matrix[3][3] = 1+0+1 = 2
            matrix[4][1]+matrix[4][2]+matrix[4][3] = 0+3+0 = 3
  Total = 3+2+3 = 8.

  Let me recompute prefix more carefully:
  P[3][2] = 3+0+5+6+1+2 = 17. P[3][4] = sum of first 3 rows, 4 cols = 3+0+1+4+5+6+3+2+1+2+0+1=28.
  P[5][4] = 38, P[2][4] = 24, P[5][1] = 14, P[2][1] = 8.
  38 - 24 - 14 + 8 = 8. Correct!
```

**Edge Cases:**
- 1x1 matrix.
- Query for single element: r1==r2, c1==c2.
- Query for entire matrix.
- Matrix with all zeros.

**Complexity:** O(m * n) preprocessing, O(1) per query. Space O(m * n) for prefix matrix.

**Follow-up questions interviewers might ask:**
- "What if the matrix is mutable?" -- Use a 2D Binary Indexed Tree (Fenwick Tree) or 2D Segment Tree. O(log m * log n) per update and query.
- "Explain the inclusion-exclusion." -- The rectangle (r1,c1)-(r2,c2) = everything up to (r2,c2) minus the region above (0,0)-(r1-1,c2) minus the region to the left (0,0)-(r2,c1-1) plus the doubly-subtracted corner (0,0)-(r1-1,c1-1).

---

### Problem: Maximum Size Subarray Sum Equals k (LC #325) — Medium

**Companies:** Meta, Google
**Why it is asked:** Combines prefix sum + hash map with tracking the earliest occurrence for maximum length.

**The Brute Force:**
```python
def maxSubArrayLen_brute(nums, k):
    # O(n^2) time
    max_len = 0
    n = len(nums)
    for i in range(n):
        total = 0
        for j in range(i, n):
            total += nums[j]
            if total == k:
                max_len = max(max_len, j - i + 1)
    return max_len
```

**The Key Insight:** Same prefix sum + hash map technique as Subarray Sum Equals K, but instead of counting, we want the maximum length. Store the **first** occurrence of each prefix sum. When `prefix_sum - k` exists in the map, the subarray length is `current_index - first_occurrence_index`. By storing the first occurrence, we maximize the length.

**Optimal Solution:**
```python
def maxSubArrayLen(nums, k):
    prefix_sum = 0
    first_seen = {0: -1}  # prefix_sum -> first index where this sum occurred
    max_len = 0

    for i, num in enumerate(nums):
        prefix_sum += num

        if prefix_sum - k in first_seen:
            max_len = max(max_len, i - first_seen[prefix_sum - k])

        if prefix_sum not in first_seen:
            first_seen[prefix_sum] = i  # only store first occurrence

    return max_len
```

**Dry Run:**
```
Input: nums = [1, -1, 5, -2, 3], k = 3

prefix=0: first_seen={0:-1}
i=0, num=1:  prefix=1, target=1-3=-2, not in map. first_seen={0:-1, 1:0}
i=1, num=-1: prefix=0, target=0-3=-3, not in map. 0 already in map, don't overwrite.
i=2, num=5:  prefix=5, target=5-3=2, not in map. first_seen={0:-1, 1:0, 5:2}
i=3, num=-2: prefix=3, target=3-3=0, in map at -1. len=3-(-1)=4. max_len=4.
             first_seen[3]=3.
i=4, num=3:  prefix=6, target=6-3=3, in map at 3. len=4-3=1. max_len stays 4.

Answer: 4 (subarray [1, -1, 5, -2] sums to 3)
```

**Edge Cases:**
- No subarray sums to k: return 0.
- Negative numbers in array.
- k = 0: find longest subarray summing to 0.
- Entire array sums to k.

**Complexity:** Time O(n), Space O(n).

**Follow-up questions interviewers might ask:**
- "Why store only the first occurrence?" -- We want the longest subarray, so the earlier the start, the longer the subarray.
- "How does this differ from LC #560?" -- LC #560 counts all subarrays; this finds the maximum length. 560 stores counts; this stores first indices.

---

### Problem: Count of Range Sum (LC #327) — Hard

**Companies:** Google, Amazon
**Why it is asked:** Combines prefix sum with divide-and-conquer (merge sort) or a balanced BST. Tests advanced algorithmic thinking.

**The Brute Force:**
```python
def countRangeSum_brute(nums, lower, upper):
    # O(n^2) time
    n = len(nums)
    count = 0
    for i in range(n):
        total = 0
        for j in range(i, n):
            total += nums[j]
            if lower <= total <= upper:
                count += 1
    return count
```

Check all O(n^2) subarrays. For each, compute the sum and check bounds.

**The Key Insight:** Build prefix sums. The condition `lower <= prefix[j] - prefix[i] <= upper` for `i < j` is equivalent to `prefix[j] - upper <= prefix[i] <= prefix[j] - lower`. We need to count, for each j, how many prefix[i] values (with i < j) fall in the range `[prefix[j] - upper, prefix[j] - lower]`.

This can be solved efficiently using **merge sort** on the prefix sum array. During the merge step, the left half contains prefix sums with smaller indices and the right half contains prefix sums with larger indices. For each element in the right half, count elements in the left half that fall in the required range using two pointers. The merge sort ensures sorted order for the counting step.

**Optimal Solution (Merge Sort):**
```python
def countRangeSum(nums, lower, upper):
    prefix = [0]
    for num in nums:
        prefix.append(prefix[-1] + num)

    def merge_count(arr, lo, hi):
        if hi - lo <= 1:
            return 0

        mid = (lo + hi) // 2
        count = merge_count(arr, lo, mid) + merge_count(arr, mid, hi)

        # Count valid pairs: left[i] in [right[j] - upper, right[j] - lower]
        # For each j in [mid, hi), find range in [lo, mid) using two pointers
        p = q = lo
        for j in range(mid, hi):
            while p < mid and arr[p] < arr[j] - upper:
                p += 1
            while q < mid and arr[q] <= arr[j] - lower:
                q += 1
            count += q - p

        # Merge (standard merge sort merge)
        arr[lo:hi] = sorted(arr[lo:hi])

        return count

    return merge_count(prefix, 0, len(prefix))
```

**Dry Run:**
```
Input: nums = [-2, 5, -1], lower = -2, upper = 2
Prefix: [0, -2, 3, 2]

merge_count([0, -2, 3, 2], 0, 4):
  merge_count([0, -2], 0, 2):
    merge_count([0], 0, 1): return 0
    merge_count([-2], 1, 2): return 0
    Count: for j=1 (val=-2): range = [-2-2, -2-(-2)] = [-4, 0]
      p=0, q=0: arr[0]=0, 0 < -4? No. 0 <= 0? Yes, q=1. count += 1-0 = 1.
    Merge: [-2, 0]. count=1.

  merge_count([3, 2], 2, 4):
    merge_count([3], 2, 3): return 0
    merge_count([2], 3, 4): return 0
    Count: for j=3 (val=2): range = [2-2, 2-(-2)] = [0, 4]
      p=2, q=2: arr[2]=3, 3 < 0? No. 3 <= 4? Yes, q=3. count += 3-2 = 1.
    Merge: [2, 3]. count=1.

  Now merge_count([-2, 0, 2, 3], 0, 4):
    Left: [-2, 0], Right: [2, 3]
    For j=2 (val=2): range = [2-2, 2-(-2)] = [0, 4]
      p=0: arr[0]=-2 < 0, p=1. arr[1]=0 >= 0. q=1: arr[1]=0 <= 4, q=2. count += 2-1 = 1.
    For j=3 (val=3): range = [3-2, 3-(-2)] = [1, 5]
      p=1: arr[1]=0 < 1, p=2. q=2: (already past mid). count += 2-2 = 0.
    count = 1. Merge: [-2, 0, 2, 3].

  Total: 1 + 1 + 1 = 3.

Verify: subarrays and sums:
  [-2]: -2 (in range)
  [-2,5]: 3 (not in range)
  [-2,5,-1]: 2 (in range)
  [5]: 5 (not in range)
  [5,-1]: 4 (not in range)
  [-1]: -1 (in range)

  Count = 3. Correct!
```

**Edge Cases:**
- All prefix sums are the same: many valid pairs.
- lower == upper: count exact matches.
- Very large values (use long in Java/C++).
- Empty array: return 0.

**Complexity:** Time O(n log n), Space O(n) for the merge sort.

**Follow-up questions interviewers might ask:**
- "Can you use a balanced BST instead?" -- Yes, use a sorted list or BIT. For each prefix sum, query the number of existing prefix sums in the range.
- "What is the merge sort doing conceptually?" -- It counts inversions-like pairs where the difference falls in a range, leveraging the sorted property of each half.

---

### Problem: Number of Submatrices That Sum to Target (LC #1074) — Hard

**Companies:** Google, Amazon
**Why it is asked:** Combines 2D prefix sum with the 1D subarray sum technique. Tests your ability to reduce a 2D problem to 1D.

**The Brute Force:**
```python
def numSubmatrixSumTarget_brute(matrix, target):
    # O(m^2 * n^2) time with prefix sum, O(m^2 * n^2 * m * n) without
    rows, cols = len(matrix), len(matrix[0])
    count = 0
    # Build 2D prefix sum
    prefix = [[0]*(cols+1) for _ in range(rows+1)]
    for r in range(rows):
        for c in range(cols):
            prefix[r+1][c+1] = matrix[r][c] + prefix[r][c+1] + prefix[r+1][c] - prefix[r][c]
    # Check all sub-rectangles
    for r1 in range(rows):
        for c1 in range(cols):
            for r2 in range(r1, rows):
                for c2 in range(c1, cols):
                    s = prefix[r2+1][c2+1] - prefix[r1][c2+1] - prefix[r2+1][c1] + prefix[r1][c1]
                    if s == target:
                        count += 1
    return count
```

O(m^2 * n^2) with precomputed prefix sums. Can we do better?

**The Key Insight:** Fix two row boundaries (r1 and r2). For each column c, compute the sum of the column slice `matrix[r1..r2][c]`. This gives a 1D array of column sums. Now the problem reduces to "count 1D subarrays with sum equal to target" -- which is LC #560. This reduces the complexity from O(m^2 * n^2) to O(m^2 * n).

**Optimal Solution:**
```python
def numSubmatrixSumTarget(matrix, target):
    rows, cols = len(matrix), len(matrix[0])

    # Precompute prefix sums along each row
    for r in range(rows):
        for c in range(1, cols):
            matrix[r][c] += matrix[r][c - 1]

    count = 0

    for c1 in range(cols):
        for c2 in range(c1, cols):
            # For fixed column boundaries c1..c2, compute running row sums
            prefix_sum = 0
            seen = {0: 1}

            for r in range(rows):
                # Sum of matrix[r][c1..c2]
                col_sum = matrix[r][c2] - (matrix[r][c1 - 1] if c1 > 0 else 0)
                prefix_sum += col_sum

                if prefix_sum - target in seen:
                    count += seen[prefix_sum - target]
                seen[prefix_sum] = seen.get(prefix_sum, 0) + 1

    return count
```

**Dry Run:**
```
Input: matrix = [[0,1,0],[1,1,1],[0,1,0]], target = 0

Row prefix sums:
  [0, 1, 1]
  [1, 2, 3]
  [0, 1, 1]

For c1=0, c2=0:
  col sums: [0, 1, 0]
  Prefix sum + hash map for target=0:
    prefix=0, seen={0:1}
    r=0: prefix=0, 0-0=0 in seen(count 1) -> count=1. seen={0:2}
    r=1: prefix=1, 1-0=1 not in seen. seen={0:2, 1:1}
    r=2: prefix=1, 1-0=1 in seen(count 1) -> count=2. seen={0:2, 1:2}

For c1=0, c2=1:
  col sums: [1, 2, 1]
  r=0: prefix=1, 1-0=1 not in seen. seen={0:1, 1:1}
  r=1: prefix=3, 3-0=3 not in seen. seen={0:1, 1:1, 3:1}
  r=2: prefix=4, 4-0=4 not in seen.

...continuing for all column pairs...
The final count includes all sub-matrices summing to 0.
```

**Edge Cases:**
- 1x1 matrix: check if the single element equals target.
- All zeros, target=0: many sub-matrices.
- Target not achievable: return 0.

**Complexity:** Time O(n^2 * m) where n = cols, m = rows (or O(m^2 * n) if iterating over row pairs). Space O(m) for the hash map.

**Follow-up questions interviewers might ask:**
- "Why fix columns and not rows?" -- You can fix either. Fix the smaller dimension for better performance.
- "How does this reduce to 1D?" -- For fixed column boundaries, each row contributes a single number (the sum across those columns), forming a 1D array.

---

### Problem: Max Sum of Rectangle No Larger Than K (LC #363) — Hard

**Companies:** Google, Amazon
**Why it is asked:** Combines 2D prefix sum reduction with a sorted container (or binary search) to find the closest prefix sum below a threshold. Tests multiple advanced techniques.

**The Brute Force:**
```python
def maxSumSubmatrix_brute(matrix, k):
    # Same as numSubmatrixSumTarget brute force but track max <= k
    rows, cols = len(matrix), len(matrix[0])
    prefix = [[0]*(cols+1) for _ in range(rows+1)]
    for r in range(rows):
        for c in range(cols):
            prefix[r+1][c+1] = matrix[r][c] + prefix[r][c+1] + prefix[r+1][c] - prefix[r][c]
    best = float('-inf')
    for r1 in range(rows):
        for c1 in range(cols):
            for r2 in range(r1, rows):
                for c2 in range(c1, cols):
                    s = prefix[r2+1][c2+1] - prefix[r1][c2+1] - prefix[r2+1][c1] + prefix[r1][c1]
                    if s <= k:
                        best = max(best, s)
    return best
```

O(m^2 * n^2).

**The Key Insight:** Fix two row (or column) boundaries. Reduce to 1D: find the max subarray sum <= k. For the 1D problem, use prefix sums with a sorted container (like a `SortedList` from `sortedcontainers` or a balanced BST). For each prefix sum P, find the smallest prefix sum S in the sorted set such that `S >= P - k` (this means `P - S <= k`). Then `P - S` is a valid subarray sum. Use `bisect_left` for this.

**Optimal Solution:**
```python
from sortedcontainers import SortedList
# If sortedcontainers not available, use bisect with a list (O(n) insert)

def maxSumSubmatrix(matrix, k):
    rows, cols = len(matrix), len(matrix[0])

    # Precompute row prefix sums
    for r in range(rows):
        for c in range(1, cols):
            matrix[r][c] += matrix[r][c - 1]

    best = float('-inf')

    for c1 in range(cols):
        for c2 in range(c1, cols):
            # 1D problem: find max subarray sum <= k
            sorted_prefix = SortedList([0])
            prefix_sum = 0

            for r in range(rows):
                col_sum = matrix[r][c2] - (matrix[r][c1 - 1] if c1 > 0 else 0)
                prefix_sum += col_sum

                # Find smallest S in sorted_prefix where S >= prefix_sum - k
                # Then prefix_sum - S <= k
                target = prefix_sum - k
                idx = sorted_prefix.bisect_left(target)

                if idx < len(sorted_prefix):
                    best = max(best, prefix_sum - sorted_prefix[idx])
                    if best == k:
                        return k  # can't do better

                sorted_prefix.add(prefix_sum)

    return best
```

**Without sortedcontainers (using bisect):**
```python
import bisect

def maxSumSubmatrix_bisect(matrix, k):
    rows, cols = len(matrix), len(matrix[0])

    for r in range(rows):
        for c in range(1, cols):
            matrix[r][c] += matrix[r][c - 1]

    best = float('-inf')

    for c1 in range(cols):
        for c2 in range(c1, cols):
            sorted_prefix = [0]
            prefix_sum = 0

            for r in range(rows):
                col_sum = matrix[r][c2] - (matrix[r][c1 - 1] if c1 > 0 else 0)
                prefix_sum += col_sum

                target = prefix_sum - k
                idx = bisect.bisect_left(sorted_prefix, target)

                if idx < len(sorted_prefix):
                    best = max(best, prefix_sum - sorted_prefix[idx])

                bisect.insort(sorted_prefix, prefix_sum)

    return best
```

**Dry Run:**
```
Input: matrix = [[1,0,1],[0,-2,3]], k = 2

Row prefix sums:
  [1, 1, 2]
  [0, -2, 1]

c1=0, c2=0:
  sorted_prefix=[0], prefix=0
  r=0: col_sum=1, prefix=1. target=1-2=-1. bisect_left([0], -1)=0.
       best = max(-inf, 1-0) = 1. insort: [0, 1]
  r=1: col_sum=0, prefix=1. target=1-2=-1. bisect_left([0,1], -1)=0.
       best = max(1, 1-0) = 1. insort: [0, 1, 1]

c1=0, c2=1:
  sorted_prefix=[0], prefix=0
  r=0: col_sum=1, prefix=1. target=-1. idx=0. best=max(1, 1-0)=1. [0,1]
  r=1: col_sum=-2, prefix=-1. target=-3. idx=0. best=max(1, -1-0)=1. [-1,0,1]

c1=0, c2=2:
  sorted_prefix=[0], prefix=0
  r=0: col_sum=2, prefix=2. target=0. bisect_left([0], 0)=0.
       best = max(1, 2-0) = 2 == k, return 2!

Answer: 2 (the sub-rectangle [[1,0,1]] has sum 2)
```

**Edge Cases:**
- k is very large: answer is the maximum submatrix sum (Kadane's 2D).
- k is very negative: might return a large negative number.
- 1x1 matrix: check if element <= k.

**Complexity:** Time O(min(m,n)^2 * max(m,n) * log(max(m,n))). The outer loops fix two boundaries O(min^2), inner loop is O(max), and bisect is O(log(max)). Space O(max(m,n)).

**Follow-up questions interviewers might ask:**
- "Why use a sorted container?" -- To efficiently find the smallest prefix sum >= target. Hash map only supports exact lookup, not range queries.
- "What if k >= maximum submatrix sum?" -- The answer is the maximum submatrix sum, computable with Kadane's 2D in O(m^2 * n).
- "Can you iterate over rows instead of columns?" -- Yes, pick the smaller dimension to iterate over pairs for better performance.

---

## Common Mistakes and Interview Tips

### Top 5 Mistakes

1. **Forgetting to initialize the hash map with `{0: 1}` (or `{0: -1}`):** This handles the case where a prefix sum itself equals the target. Without it, you miss subarrays starting from index 0.

2. **Off-by-one in prefix sum indexing:** `prefix[i]` represents the sum of `nums[0..i-1]`, not `nums[0..i]`. The sum of `nums[i..j]` is `prefix[j+1] - prefix[i]`, not `prefix[j] - prefix[i]`.

3. **Confusing "first occurrence" vs "count" in the hash map:** For counting subarrays (LC #560), store counts. For maximum length (LC #325), store first occurrence. For existence check (LC #523), store first occurrence.

4. **Not handling the modulo operation correctly:** In Continuous Subarray Sum, the remainder can be negative in some languages. In Python, `%` always returns non-negative, but in Java/C++, you may need `((prefix % k) + k) % k`.

5. **Applying sliding window when prefix sum + hash map is needed:** Sliding window requires non-negative numbers for the "expand increases sum" property. When negative numbers are present, use prefix sum + hash map.

### How to Recognize This Pattern in 30 Seconds

Ask: "Am I looking for the sum of a contiguous subarray, and does the problem involve counting, finding max length, or checking existence of subarrays with a specific sum?" If yes, prefix sum + hash map.

### What Senior/Staff Interviewers Look For

- **Clean reduction from 2D to 1D** for matrix problems. Can you explain the reduction clearly?
- **Correct hash map initialization and update order.** The hash map must be updated AFTER checking, not before.
- **Understanding when prefix sum + hash map beats sliding window:** Negative numbers, divisibility conditions, exact sum targets.
- **Ability to combine prefix sum with other techniques:** merge sort (Count of Range Sum), sorted containers (Max Sum Rectangle <= K).

### Communication Tips

1. State the prefix sum formula: "prefix[j+1] - prefix[i] gives the sum of nums[i..j]."
2. Explain the hash map technique: "I store prefix sums I have seen so far. For each new prefix sum, I check if prefix_sum - k has been seen before."
3. For 2D problems, explain the reduction: "I fix two row boundaries and reduce to a 1D problem on column sums."
4. Explicitly state the hash map initialization: "I initialize with {0: 1} to handle subarrays starting from index 0."

## Pattern Connections

- **Prefix Sum + Hash Map** is the go-to for subarray sum problems with negative numbers. **Sliding Window** handles the same problems only when all numbers are non-negative.
- **Prefix Sum + Merge Sort** handles range-count queries (Count of Range Sum).
- **Prefix Sum + Sorted Container** handles "closest to target" queries (Max Sum Rectangle <= K).
- **2D Prefix Sum** extends naturally to problems on matrices and connects to **dynamic programming** on grids.
- **Difference Array** is the inverse of prefix sum: apply range updates in O(1) and reconstruct the array with a prefix sum pass.
- **Binary Indexed Tree (Fenwick Tree)** and **Segment Tree** are generalizations that support both updates and queries.
