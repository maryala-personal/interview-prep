# Monotonic Stack/Queue — Complete Interview Guide

## When to Use This Pattern

A monotonic stack or queue maintains elements in sorted order (either all increasing or all decreasing). Use it when you need to efficiently find the "next greater," "next smaller," "previous greater," or "previous smaller" element for every position in an array.

**Primary signals:**
- "Next greater element" / "Next smaller element"
- "Previous greater element" / "Previous smaller element"
- "Sliding window maximum/minimum"
- "Largest rectangle in histogram"
- "Trapping rain water"
- "Daily temperatures" / "Stock span"
- For each element, find the nearest element that is larger/smaller in some direction

**Why it works:**
The brute force for "next greater element" is O(n^2) — for each element, scan right until you find something bigger. A monotonic stack does this in O(n) total because each element is pushed and popped at most once. The stack acts as a "waiting list" of elements that have not yet found their answer.

**Amortized O(n) intuition:** Although there is a while loop inside the for loop (which looks like O(n^2)), each element enters the stack exactly once and leaves the stack at most once. The total number of push + pop operations across the entire algorithm is at most 2n. This is one of the most important complexity analysis insights to know for interviews.

**Monotonic Stack vs Monotonic Queue:**
- **Stack:** Used for "next/previous greater/smaller" problems. Elements are processed in one direction.
- **Queue (Deque):** Used for "sliding window min/max" problems. Elements enter from one end, leave from both ends. The deque maintains candidates for the window's min or max.

---

### ⚡ Pattern Overlap & Decision Guide

**Monotonic Stack/Queue vs Two Pointers vs Sliding Window vs Regular Stack**

| Signal in Problem | Monotonic Stack | Two Pointers | Sliding Window | Regular Stack |
|---|---|---|---|---|
| "Next greater/smaller element" | Best choice | Not applicable | Not applicable | Works but O(n^2) |
| "Sliding window max/min" | Monotonic Deque -- O(n) | Not applicable | Heap -- O(n log k) | Not applicable |
| "Trapping rain water" | Works (layer by layer) | Best for O(1) space | Not applicable | Not applicable |
| "Largest rectangle in histogram" | Best choice | Not applicable | Not applicable | Not applicable |
| "Balanced parentheses / matching" | Not applicable | Not applicable | Not applicable | Best choice |
| "Subarray sum / product" | Not applicable | May work | Sliding window | Not applicable |
| "Stock span / price range" | Best choice | Not applicable | Not applicable | Not applicable |

**Quick signals pointing specifically to Monotonic Stack:**
- "For each element, find the nearest larger/smaller element in a direction"
- "Largest rectangle" or "maximal area" with height constraints
- "How many days until warmer/colder" (distance to next greater/smaller)
- The brute force is O(n^2) nested loops where inner loop scans for a boundary

**Common mistakes -- "You might think X, but it is actually Y":**

1. **LC 11 (Container With Most Water) -- Looks like monotonic stack, but it is Two Pointers.** You see bars and water, which screams "histogram" or "trapping rain water." But this problem maximizes area between two lines (not trapped water between bars). The two-pointer approach from outside-in is optimal. Monotonic stack does not help here.

2. **LC 209 (Minimum Size Subarray Sum) -- Looks like it needs a stack for boundaries, but it is Sliding Window.** The subarray constraint with a sum target is a sliding window problem. Monotonic stack finds "nearest greater/smaller," not "subarray with target sum."

3. **LC 20 (Valid Parentheses) -- Uses a stack, but NOT a monotonic stack.** The stack here does matching/pairing, not ordering. There is no monotonic invariant. Do not confuse "uses a stack" with "monotonic stack pattern."

4. **LC 862 (Shortest Subarray with Sum at Least K) -- Looks like sliding window, but requires Monotonic Deque.** Negative numbers break the sliding window invariant. A monotonic deque on prefix sums is needed. This is one of the trickiest overlaps between patterns.

---

## Core Mechanics

### Monotonic Decreasing Stack (for "Next Greater Element")

The invariant: elements in the stack are in decreasing order from bottom to top. When a new element `x` arrives that is greater than the stack top, it "answers" the question for all stack elements smaller than `x`.

**Visual walkthrough with array [2, 1, 5, 6, 2, 3]:**

```
Processing left to right, building a monotonic decreasing stack.
Stack stores indices. We want next_greater[i] for each i.

i=0, val=2:  Stack empty. Push 0.
  Stack: [0]  (values: [2])

i=1, val=1:  1 < 2 (stack top). Push 1.
  Stack: [0, 1]  (values: [2, 1])

i=2, val=5:  5 > 1 (stack top) → pop index 1: next_greater[1] = 5
             5 > 2 (stack top) → pop index 0: next_greater[0] = 5
             Stack empty. Push 2.
  Stack: [2]  (values: [5])

i=3, val=6:  6 > 5 → pop index 2: next_greater[2] = 6
             Push 3.
  Stack: [3]  (values: [6])

i=4, val=2:  2 < 6. Push 4.
  Stack: [3, 4]  (values: [6, 2])

i=5, val=3:  3 > 2 → pop index 4: next_greater[4] = 3
             3 < 6. Push 5.
  Stack: [3, 5]  (values: [6, 3])

Remaining in stack: indices 3, 5 → no next greater element exists.
next_greater = [5, 5, 6, -1, 3, -1]
```

**Why each element is processed at most twice:** It is pushed once and popped at most once. Therefore total work is O(n).

### Monotonic Increasing Stack (for "Next Smaller Element")

Same idea, but the stack maintains increasing order. When a new element is smaller than the top, it answers questions for elements that were waiting for something smaller.

### Choosing the Stack Direction

| Goal | Stack Order | When to Pop |
|------|------------|-------------|
| Next Greater | Decreasing (bottom to top) | New element > top |
| Next Smaller | Increasing (bottom to top) | New element < top |
| Previous Greater | Decreasing, process L→R | Pop before pushing |
| Previous Smaller | Increasing, process L→R | Pop before pushing |

**Key distinction — Next vs Previous:**
- **Next greater/smaller:** The answer for a popped element is the current element (the one that caused the pop).
- **Previous greater/smaller:** The answer for the current element is what remains on the stack top after popping.

### Monotonic Deque (for Sliding Window Min/Max)

For sliding window maximum, maintain a deque of indices in decreasing order of values. This gives O(1) access to the current window's maximum (front of deque).

```
Window of size 3 over [1, 3, -1, -3, 5, 3, 6, 7]:

i=0, val=1:  Deque empty. Add 0.  Deque: [0] (vals: [1])
i=1, val=3:  3 > 1, remove 0.    Deque: [1] (vals: [3])
i=2, val=-1: -1 < 3, add.        Deque: [1, 2] (vals: [3, -1])
  Window [0..2]: max = deque front = arr[1] = 3

i=3, val=-3: -3 < -1, add.       Deque: [1, 2, 3] (vals: [3, -1, -3])
  Window [1..3]: max = arr[1] = 3

i=4, val=5:  Remove all < 5.     Deque: [4] (vals: [5])
  But first, check if front (index 1) is out of window [2..4]? Yes! Remove front.
  After cleanup: Deque: [4] (vals: [5])
  Window [2..4]: max = 5

...and so on.
```

**Two cleanup steps per element:**
1. Remove from the **back** any elements smaller than current (they can never be the max while current is in the window)
2. Remove from the **front** any elements outside the window (index < i - k + 1)

---

## The Template

### Python — Monotonic Stack (Next Greater Element)

```python
def next_greater_elements(nums: list[int]) -> list[int]:
    """Find next greater element for each position. -1 if none exists."""
    n = len(nums)
    result = [-1] * n
    stack = []  # Stores indices, maintains decreasing values

    for i in range(n):
        while stack and nums[i] > nums[stack[-1]]:
            idx = stack.pop()
            result[idx] = nums[i]
        stack.append(i)

    return result
```

### Python — Monotonic Deque (Sliding Window Maximum)

```python
from collections import deque

def sliding_window_max(nums: list[int], k: int) -> list[int]:
    """Find maximum in every window of size k."""
    dq = deque()  # Stores indices, values are decreasing
    result = []

    for i in range(len(nums)):
        # Remove elements outside window
        while dq and dq[0] < i - k + 1:
            dq.popleft()

        # Remove elements smaller than current (they can never be max)
        while dq and nums[dq[-1]] <= nums[i]:
            dq.pop()

        dq.append(i)

        # Window is fully formed starting at index k-1
        if i >= k - 1:
            result.append(nums[dq[0]])

    return result
```

### Go — Monotonic Stack

```go
func nextGreaterElements(nums []int) []int {
    n := len(nums)
    result := make([]int, n)
    for i := range result {
        result[i] = -1
    }
    stack := []int{} // indices

    for i := 0; i < n; i++ {
        for len(stack) > 0 && nums[i] > nums[stack[len(stack)-1]] {
            idx := stack[len(stack)-1]
            stack = stack[:len(stack)-1]
            result[idx] = nums[i]
        }
        stack = append(stack, i)
    }
    return result
}
```

### Go — Monotonic Deque

```go
func maxSlidingWindow(nums []int, k int) []int {
    dq := []int{} // indices, decreasing values
    result := []int{}

    for i := 0; i < len(nums); i++ {
        // Remove out-of-window
        for len(dq) > 0 && dq[0] < i-k+1 {
            dq = dq[1:]
        }
        // Remove smaller elements
        for len(dq) > 0 && nums[dq[len(dq)-1]] <= nums[i] {
            dq = dq[:len(dq)-1]
        }
        dq = append(dq, i)
        if i >= k-1 {
            result = append(result, nums[dq[0]])
        }
    }
    return result
}
```

### Summary: The Four Variants at a Glance

| Problem | Stack Type | Traversal | Answer From |
|---------|-----------|-----------|-------------|
| Next Greater | Decreasing | Left → Right | Current element (what caused pop) |
| Next Smaller | Increasing | Left → Right | Current element (what caused pop) |
| Previous Greater | Decreasing | Left → Right | Stack top after pops |
| Previous Smaller | Increasing | Left → Right | Stack top after pops |

**Templates for all four variants:**

```python
def next_greater(nums):
    """Decreasing stack, answer = element that caused the pop."""
    n = len(nums)
    result = [-1] * n
    stack = []
    for i in range(n):
        while stack and nums[i] > nums[stack[-1]]:
            result[stack.pop()] = nums[i]
        stack.append(i)
    return result

def next_smaller(nums):
    """Increasing stack, answer = element that caused the pop."""
    n = len(nums)
    result = [-1] * n
    stack = []
    for i in range(n):
        while stack and nums[i] < nums[stack[-1]]:
            result[stack.pop()] = nums[i]
        stack.append(i)
    return result

def previous_greater(nums):
    """Decreasing stack, answer = stack top after pops."""
    n = len(nums)
    result = [-1] * n
    stack = []
    for i in range(n):
        while stack and nums[stack[-1]] <= nums[i]:
            stack.pop()
        if stack:
            result[i] = nums[stack[-1]]
        stack.append(i)
    return result

def previous_smaller(nums):
    """Increasing stack, answer = stack top after pops."""
    n = len(nums)
    result = [-1] * n
    stack = []
    for i in range(n):
        while stack and nums[stack[-1]] >= nums[i]:
            stack.pop()
        if stack:
            result[i] = nums[stack[-1]]
        stack.append(i)
    return result
```

**Worked example with [3, 1, 4, 1, 5, 9, 2, 6]:**
```
next_greater:     [4, 4, 5, 5, 9, -1, 6, -1]
next_smaller:     [1, -1, 1, -1, 2,  2, -1, -1]
previous_greater: [-1, 3, -1, 4, -1, -1, 9, 9]
previous_smaller: [-1, -1, 1, 1, 1,  5, -1, 2]
```

---

## Variant Subpatterns

### 1. Next Greater Element (basic)
For each element, find the first element to its right that is larger. Uses a decreasing stack.

### 2. Previous Smaller Element
For each element, find the first element to its left that is smaller. Uses an increasing stack, and the answer is the stack top after popping.

### 3. Histogram Rectangle Pattern
Find the largest rectangle in a histogram. For each bar, find the nearest shorter bar on the left and right. The width of the rectangle with that bar as height is `right_boundary - left_boundary - 1`.

### 4. Sliding Window Min/Max
Maintain a deque to track the min or max in a sliding window. Each element enters and leaves the deque at most once, giving O(n) total.

### 5. Circular Array (Next Greater Element II)
Process the array twice (or use modular indexing) to handle wrap-around.

### 6. Contribution Technique
Instead of asking "what is the answer for element i?", ask "how much does element i contribute to the total answer?" — used in Sum of Subarray Minimums, Trapping Rain Water, etc.

---

## Problem Walkthroughs

---

### Problem 1: Next Greater Element I (LC 496 — Easy)

**Problem:** Given two arrays `nums1` (a subset of `nums2` with no duplicates), for each element in `nums1`, find the next greater element in `nums2`. If none exists, return -1.

**Brute Force:**
For each element in nums1, find it in nums2, then scan right for the next greater. O(n * m).

**Key Insight:**
Precompute the next greater element for every element in nums2 using a monotonic stack. Store results in a hashmap. Then look up each element of nums1 in O(1).

**Optimal Solution:**

```python
def nextGreaterElement(nums1: list[int], nums2: list[int]) -> list[int]:
    """
    LC 496: Next Greater Element I

    Time: O(n + m) where n = len(nums1), m = len(nums2)
    Space: O(m)
    """
    # Build next-greater map for nums2
    next_greater = {}
    stack = []  # Decreasing stack of values (no duplicates, so values work)

    for num in nums2:
        while stack and num > stack[-1]:
            next_greater[stack.pop()] = num
        stack.append(num)

    # Remaining in stack have no next greater
    for num in stack:
        next_greater[num] = -1

    return [next_greater[num] for num in nums1]
```

**Dry Run 1 (Basic):**
```
nums1 = [4,1,2], nums2 = [1,3,4,2]

Processing nums2:
  1: stack=[] → push. Stack: [1]
  3: 3>1, pop 1 → next_greater[1]=3. Push 3. Stack: [3]
  4: 4>3, pop 3 → next_greater[3]=4. Push 4. Stack: [4]
  2: 2<4 → push. Stack: [4, 2]

Remaining: next_greater[4]=-1, next_greater[2]=-1

Lookup nums1: [next_greater[4], next_greater[1], next_greater[2]] = [-1, 3, -1]
```

**Dry Run 2 (Tricky -- strictly decreasing nums2, all answers are -1):**
```
nums1 = [4,2], nums2 = [5,4,3,2,1]

Processing nums2:
  5: push. Stack: [5]
  4: 4<5, push. Stack: [5,4]
  3: 3<4, push. Stack: [5,4,3]
  2: 2<3, push. Stack: [5,4,3,2]
  1: 1<2, push. Stack: [5,4,3,2,1]

No pops ever happen! Every element stays on the stack → all get -1.
Result: [-1, -1]

AHA moment: In a strictly decreasing array, every element is already
"the greatest so far." No element ever finds a next greater, so the
stack just accumulates. This is the worst case for stack space: O(n).
```

**Dry Run 3 (Tricky -- nums1 element whose next greater is far away):**
```
nums1 = [2], nums2 = [2,1,1,1,1,3]

Processing nums2:
  2: push. Stack: [2]
  1: 1<2, push. Stack: [2,1]
  1: 1=1, push. Stack: [2,1,1]
  1: 1=1, push. Stack: [2,1,1,1]
  1: 1=1, push. Stack: [2,1,1,1,1]
  3: 3>1, pop→next_greater[1]=3. (repeat for all 1s and 2)
     3>1,pop. 3>1,pop. 3>1,pop. 3>2,pop→next_greater[2]=3. Push 3.

Result: next_greater[2]=3.

AHA moment: Element 2 had to "wait" through four 1s before finding
its next greater. The stack accumulated 5 elements before the big
pop cascade. This shows the amortized O(n): the cascade of pops
is paid for by the pushes that preceded it.
```

**Edge Cases:**
- nums1 = nums2: standard next greater for entire array
- Single element: return [-1]
- Strictly decreasing nums2: all -1

---

### Problem 2: Daily Temperatures (LC 739 — Medium)

**Problem:** Given an array of daily temperatures, return an array where `answer[i]` is the number of days you have to wait after day `i` for a warmer temperature. If no future day is warmer, put 0.

**Brute Force:**
For each day, scan forward until finding a warmer day. O(n^2).

**Key Insight:**
This is exactly "next greater element" but we return the index difference instead of the value. Use a monotonic decreasing stack of indices.

**Optimal Solution:**

```python
def dailyTemperatures(temperatures: list[int]) -> list[int]:
    """
    LC 739: Daily Temperatures

    Time: O(n) — each index pushed and popped at most once
    Space: O(n)
    """
    n = len(temperatures)
    answer = [0] * n
    stack = []  # Indices, maintaining decreasing temperatures

    for i in range(n):
        while stack and temperatures[i] > temperatures[stack[-1]]:
            prev_day = stack.pop()
            answer[prev_day] = i - prev_day
        stack.append(i)

    return answer
```

**Dry Run:**
```
temps = [73, 74, 75, 71, 69, 72, 76, 73]

i=0 (73): Push 0. Stack: [0]
i=1 (74): 74>73, pop 0 → answer[0]=1. Push 1. Stack: [1]
i=2 (75): 75>74, pop 1 → answer[1]=1. Push 2. Stack: [2]
i=3 (71): 71<75. Push 3. Stack: [2,3]
i=4 (69): 69<71. Push 4. Stack: [2,3,4]
i=5 (72): 72>69, pop 4 → answer[4]=1.
          72>71, pop 3 → answer[3]=2. Push 5. Stack: [2,5]
i=6 (76): 76>72, pop 5 → answer[5]=1.
          76>75, pop 2 → answer[2]=4. Push 6. Stack: [6]
i=7 (73): 73<76. Push 7. Stack: [6,7]

Remaining: answer[6]=0, answer[7]=0

answer = [1, 1, 4, 2, 1, 1, 0, 0]
```

**Dry Run 2 (Tricky -- plateau followed by spike):**
```
temps = [70, 70, 70, 70, 75]

i=0 (70): Push 0. Stack: [0]
i=1 (70): 70 is NOT > 70 (we use strict >). Push 1. Stack: [0,1]
i=2 (70): Not > 70. Push 2. Stack: [0,1,2]
i=3 (70): Not > 70. Push 3. Stack: [0,1,2,3]
i=4 (75): 75>70, pop 3→answer[3]=1.
          75>70, pop 2→answer[2]=2.
          75>70, pop 1→answer[1]=3.
          75>70, pop 0→answer[0]=4.
          Push 4. Stack: [4]

answer = [4, 3, 2, 1, 0]

AHA moment: Equal temperatures do NOT pop the stack! The condition is
strictly greater (>), not greater-or-equal (>=). If we used >=, day 1
would "answer" day 0, giving answer[0]=1, which is WRONG because
70 is not warmer than 70. This strict-vs-non-strict distinction is
a common source of bugs.
```

**Dry Run 3 (Tricky -- temperature goes up, down, then up higher):**
```
temps = [60, 80, 50, 90]

i=0 (60): Push 0. Stack: [0]
i=1 (80): 80>60, pop 0→answer[0]=1. Push 1. Stack: [1]
i=2 (50): 50<80. Push 2. Stack: [1,2]
i=3 (90): 90>50, pop 2→answer[2]=1.
          90>80, pop 1→answer[1]=2. Push 3. Stack: [3]

answer = [1, 2, 1, 0]

AHA moment: Day 1 (80) has answer=2, not 1. Even though day 2 exists,
50 < 80 so day 2 is not warmer. Day 1 must wait until day 3 (90).
The stack correctly holds day 1 while day 2 comes and goes. Day 2
gets answered immediately by day 3, but day 1 had to wait longer.
```

**Edge Cases:**
- All same temperature: all zeros
- Strictly increasing: [1, 1, 1, ..., 0]
- Strictly decreasing: all zeros
- Single day: [0]

**Follow-up:** What if we wanted to answer "how many days until a COOLER temperature?" Same approach but with a monotonic increasing stack.

**Complexity Analysis:**
Although there is a while loop inside the for loop, the total number of pop operations across the entire run is at most n (each index is pushed once and popped at most once). Therefore the amortized cost per element is O(1), and the total time is O(n). This is a critical point to explain in interviews.

---

### Problem 3: Largest Rectangle in Histogram (LC 84 — Hard)

This is one of the most important monotonic stack problems. It appears directly in interviews and is a building block for LC 85 (Maximal Rectangle).

**Problem:** Given an array of bar heights representing a histogram, find the area of the largest rectangle that can be formed.

**Brute Force:**
For each bar, expand left and right while heights are >= current height. Area = height * width. O(n^2).

**Key Insight:**
For each bar of height h, the maximum rectangle with that bar as the shortest bar extends from the nearest shorter bar on the left to the nearest shorter bar on the right. We can find both boundaries for all bars in one pass using a monotonic increasing stack.

When we pop a bar from the stack, the current index is its right boundary (first shorter bar to the right), and the new stack top is its left boundary (first shorter bar to the left).

**Optimal Solution:**

```python
def largestRectangleArea(heights: list[int]) -> int:
    """
    LC 84: Largest Rectangle in Histogram

    Time: O(n)
    Space: O(n)
    """
    stack = []  # Monotonic increasing stack of indices
    max_area = 0
    heights.append(0)  # Sentinel to force all bars to be popped

    for i in range(len(heights)):
        while stack and heights[i] < heights[stack[-1]]:
            h = heights[stack.pop()]
            # Width: from (new stack top + 1) to (i - 1)
            w = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, h * w)
        stack.append(i)

    heights.pop()  # Restore the input array
    return max_area
```

**Why the sentinel works:** Appending height 0 guarantees every bar gets popped. Without it, bars remaining in the stack after the loop would need separate handling.

**Dry Run:**
```
heights = [2, 1, 5, 6, 2, 3] + [0] (sentinel)

i=0 (h=2): Push 0. Stack: [0]
i=1 (h=1): 1<2, pop 0. h=2, w=1 (stack empty, w=i=1). Area=2. Push 1. Stack: [1]
i=2 (h=5): Push 2. Stack: [1,2]
i=3 (h=6): Push 3. Stack: [1,2,3]
i=4 (h=2): 2<6, pop 3. h=6, w=4-2-1=1. Area=6.
            2<5, pop 2. h=5, w=4-1-1=2. Area=10.
            2>=1, stop. Push 4. Stack: [1,4]
i=5 (h=3): Push 5. Stack: [1,4,5]
i=6 (h=0): 0<3, pop 5. h=3, w=6-4-1=1. Area=3.
            0<2, pop 4. h=2, w=6-1-1=4. Area=8.
            0<1, pop 1. h=1, w=6 (stack empty). Area=6.

max_area = 10 (height 5, width 2, spanning indices 2-3)
```

**Dry Run 2 (Tricky -- all bars same height):**
```
heights = [3, 3, 3, 3] + [0] (sentinel)

i=0 (3): Push 0. Stack: [0]
i=1 (3): 3 is NOT < 3 (we pop when current < top). Push 1. Stack: [0,1]
i=2 (3): Push 2. Stack: [0,1,2]
i=3 (3): Push 3. Stack: [0,1,2,3]
i=4 (0): 0<3, pop 3. h=3, w=4-2-1=1. Area=3.
         0<3, pop 2. h=3, w=4-1-1=2. Area=6.
         0<3, pop 1. h=3, w=4-0-1=3. Area=9.
         0<3, pop 0. h=3, w=4 (stack empty). Area=12.

max_area = 12 = 3 * 4

AHA moment: No pops happen until the sentinel! All bars accumulate
on the stack because equal heights do NOT trigger pops (< not <=).
The sentinel forces all bars out. When a bar is popped with an empty
stack, its width extends to the ENTIRE left side (w=i), meaning it
was the smallest bar across the whole histogram. This is the key case
where the "stack empty → w=i" rule matters.
```

**Dry Run 3 (Tricky -- V-shape where answer involves non-adjacent bars):**
```
heights = [4, 1, 4] + [0]

i=0 (4): Push 0. Stack: [0]
i=1 (1): 1<4, pop 0. h=4, w=1. Area=4. Push 1. Stack: [1]
i=2 (4): Push 2. Stack: [1,2]
i=3 (0): 0<4, pop 2. h=4, w=3-1-1=1. Area=4.
         0<1, pop 1. h=1, w=3. Area=3.

max_area = 4

AHA moment: The two bars of height 4 are separated by height 1, so
you CANNOT form a rectangle of height 4 spanning width 3. Each bar
of height 4 only contributes area 4 (4*1). The height-1 bar spans
the full width (3) but only contributes area 3. The algorithm correctly
computes each bar's maximal rectangle based on where shorter bars
actually are, not where tall bars are.
```

**Edge Cases:**
- All bars same height: area = height * n
- Single bar: area = height
- Strictly increasing: largest rectangle involves the last few bars
- Strictly decreasing: each bar's rectangle is limited to itself

**Follow-up:** This is a building block for Maximal Rectangle (LC 85) — treat each row as the base of a histogram.

---

### Problem 4: Sliding Window Maximum (LC 239 — Hard)

**Problem:** Given an array `nums` and a window size `k`, return the maximum value in each window as it slides from left to right.

**Brute Force:**
For each window position, scan all k elements to find the max. O(n * k).

**Key Insight:**
Use a monotonic decreasing deque. The front of the deque is always the index of the maximum element in the current window. We maintain two invariants:
1. Indices in the deque are within the current window
2. Values at those indices are in decreasing order

When a new element arrives, elements in the back of the deque that are smaller will never be the maximum (the new element is both larger and newer), so remove them.

**Optimal Solution:**

```python
from collections import deque

def maxSlidingWindow(nums: list[int], k: int) -> list[int]:
    """
    LC 239: Sliding Window Maximum

    Time: O(n) — each element enters and leaves deque at most once
    Space: O(k) for the deque
    """
    dq = deque()  # Indices, values in decreasing order
    result = []

    for i in range(len(nums)):
        # Remove indices outside the window
        while dq and dq[0] < i - k + 1:
            dq.popleft()

        # Remove indices whose values are smaller than current
        # (they can never be the max while nums[i] is in the window)
        while dq and nums[dq[-1]] <= nums[i]:
            dq.pop()

        dq.append(i)

        # Record the maximum once the first window is fully formed
        if i >= k - 1:
            result.append(nums[dq[0]])

    return result
```

**Dry Run:**
```
nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 3

i=0 (1):  dq=[0]
i=1 (3):  3>1, pop 0. dq=[1]
i=2 (-1): -1<3. dq=[1,2]. Window [0..2]: max=nums[1]=3
i=3 (-3): -3<-1. dq=[1,2,3]. Window [1..3]: max=nums[1]=3
i=4 (5):  5>-3, pop 3. 5>-1, pop 2. 5>3, pop 1. dq=[4].
          But first check: index 1 < 4-3+1=2? Yes, would have been removed.
          Window [2..4]: max=nums[4]=5
i=5 (3):  3<5. dq=[4,5]. Window [3..5]: max=nums[4]=5
i=6 (6):  6>3, pop 5. 6>5, pop 4. dq=[6]. Window [4..6]: max=6
i=7 (7):  7>6, pop 6. dq=[7]. Window [5..7]: max=7

Result: [3, 3, 5, 5, 6, 7]
```

**Edge Cases:**
- k = 1: return nums itself
- k = len(nums): return [max(nums)]
- All same elements: return array of that element
- Strictly decreasing: deque is always full

**Follow-up:** What about sliding window minimum? Same approach but maintain an increasing deque. What about sliding window median? Use two heaps (see Heap guide).

---

### Problem 5: Maximal Rectangle (LC 85 — Hard)

**Problem:** Given a 2D binary matrix filled with '0's and '1's, find the largest rectangle containing only '1's and return its area.

**Brute Force:**
For every possible top-left and bottom-right corner pair, check if the rectangle is all 1's. O(m^2 * n^2 * m * n).

**Key Insight:**
Reduce to the histogram problem (LC 84). Treat each row as the base of a histogram. For row `r`, the height of bar at column `c` is the number of consecutive '1's above (and including) row `r` in column `c`. Then apply Largest Rectangle in Histogram for each row.

```
Matrix:          Histogram heights by row:
1 0 1 0 0        Row 0: [1, 0, 1, 0, 0]
1 0 1 1 1        Row 1: [2, 0, 2, 1, 1]
1 1 1 1 1        Row 2: [3, 1, 3, 2, 2]
1 0 0 1 0        Row 3: [4, 0, 0, 3, 0]
```

For each row, compute the largest rectangle in that histogram. The answer is the maximum across all rows.

**Optimal Solution:**

```python
def maximalRectangle(matrix: list[list[str]]) -> int:
    """
    LC 85: Maximal Rectangle

    Time: O(m * n) — O(n) per row for histogram, m rows
    Space: O(n) for heights array
    """
    if not matrix or not matrix[0]:
        return 0

    n = len(matrix[0])
    heights = [0] * n
    max_area = 0

    for row in matrix:
        # Update histogram heights
        for j in range(n):
            heights[j] = heights[j] + 1 if row[j] == '1' else 0

        # Apply largest rectangle in histogram
        max_area = max(max_area, largestRectangleArea(heights))

    return max_area


def largestRectangleArea(heights: list[int]) -> int:
    """Helper: LC 84 solution."""
    stack = []
    max_area = 0
    heights_copy = heights + [0]  # Don't modify the original

    for i in range(len(heights_copy)):
        while stack and heights_copy[i] < heights_copy[stack[-1]]:
            h = heights_copy[stack.pop()]
            w = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, h * w)
        stack.append(i)

    return max_area
```

**Dry Run:**
```
Matrix:
["1","0","1","0","0"]
["1","0","1","1","1"]
["1","1","1","1","1"]
["1","0","0","1","0"]

Row 0: heights = [1,0,1,0,0] → largest rect = 1
Row 1: heights = [2,0,2,1,1] → largest rect = 3 (height 1, width 3: cols 2-4)
Row 2: heights = [3,1,3,2,2] → largest rect = 6 (height 2, width 3: cols 2-4)
                                 or (height 1, width 5: cols 0-4) = 5. So 6.

Wait, let me recheck row 2: [3,1,3,2,2]
Using histogram algorithm:
  i=0 (3): push. Stack: [0]
  i=1 (1): 1<3, pop 0. h=3, w=1. Area=3. Push 1. Stack: [1]
  i=2 (3): push. Stack: [1,2]
  i=3 (2): 2<3, pop 2. h=3, w=3-1-1=1. Area=3. Push 3. Stack: [1,3]
  i=4 (2): 2>=2, push. Stack: [1,3,4]
  i=5 (0): pop 4. h=2, w=5-3-1=1. Area=2.
           pop 3. h=2, w=5-1-1=3. Area=6.
           pop 1. h=1, w=5. Area=5.
  max_area for row 2 = 6

Row 3: heights = [4,0,0,3,0] → largest rect = 4 (single bar of height 4)
                                 or 3 (single bar of height 3). So 4.

Overall max = 6
```

**Edge Cases:**
- Empty matrix: return 0
- All zeros: return 0
- All ones: return m * n
- Single row or single column

**Follow-up:** What about maximal square? Use DP instead (see Matrix/Grid guide). What about counting the number of rectangles? Different approach entirely.

---

### Problem 6: Trapping Rain Water (LC 42 — Hard)

**Problem:** Given an elevation map where the width of each bar is 1, compute how much water it can trap after raining.

**Brute Force:**
For each position i, the water level is `min(max_left, max_right) - height[i]`. Compute max_left and max_right by scanning in both directions for each position. O(n^2).

**Better approach — prefix max arrays:**
Precompute max_left[i] and max_right[i] arrays. O(n) time, O(n) space.

**Key Insight (Monotonic Stack approach):**
Use a monotonic decreasing stack. When we encounter a bar taller than the stack top, we have found a "valley" — the popped bar is the bottom of a trapped water region, bounded by the current bar on the right and the new stack top on the left.

The water trapped at this valley is:
- width = current_index - stack_top_index - 1
- height = min(current_height, stack_top_height) - valley_height
- water += width * height

**Optimal Solution (Stack approach):**

```python
def trap_stack(height: list[int]) -> int:
    """
    LC 42: Trapping Rain Water — Monotonic Stack

    Time: O(n)
    Space: O(n)
    """
    stack = []  # Monotonic decreasing stack of indices
    water = 0

    for i in range(len(height)):
        while stack and height[i] > height[stack[-1]]:
            bottom = stack.pop()
            if not stack:
                break  # No left boundary
            left = stack[-1]
            w = i - left - 1
            h = min(height[i], height[left]) - height[bottom]
            water += w * h
        stack.append(i)

    return water
```

**Optimal Solution (Two pointers — O(1) space):**

```python
def trap(height: list[int]) -> int:
    """
    LC 42: Trapping Rain Water — Two Pointers

    Time: O(n)
    Space: O(1)
    """
    left, right = 0, len(height) - 1
    left_max, right_max = 0, 0
    water = 0

    while left < right:
        if height[left] < height[right]:
            if height[left] >= left_max:
                left_max = height[left]
            else:
                water += left_max - height[left]
            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else:
                water += right_max - height[right]
            right -= 1

    return water
```

**Why two pointers works:** At each step, we process the side with the smaller height. Since we know the other side has a taller (or equal) bar, the water level at the current position is determined solely by the max on the current side. We do not need to know the exact max on the other side — we just need to know it exists and is at least as tall.

**Dry Run (Stack approach):**
```
height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]

i=0 (0): Push. Stack: [0]
i=1 (1): 1>0, pop 0. Stack empty, no left boundary. Push 1. Stack: [1]
i=2 (0): 0<1. Push. Stack: [1,2]
i=3 (2): 2>0, pop 2. bottom=0, left=1(h=1), right=3(h=2).
          w=3-1-1=1, h=min(2,1)-0=1. water+=1. Water=1.
          2>1, pop 1. Stack empty, no left boundary. Push 3. Stack: [3]
i=4 (1): Push. Stack: [3,4]
i=5 (0): Push. Stack: [3,4,5]
i=6 (1): 1>0, pop 5. bottom=0, left=4(h=1), right=6(h=1).
          w=6-4-1=1, h=min(1,1)-0=1. water+=1. Water=2.
          1>=1, stop. Push 6. Stack: [3,4,6]
i=7 (3): 3>1, pop 6. bottom=1, left=4(h=1), right=7(h=3).
          w=7-4-1=2, h=min(3,1)-1=0. water+=0.
          3>1, pop 4. bottom=1, left=3(h=2), right=7(h=3).
          w=7-3-1=3, h=min(3,2)-1=1. water+=3. Water=5.
          3>2, pop 3. Stack empty. Push 7. Stack: [7]
i=8 (2): Push. Stack: [7,8]
i=9 (1): Push. Stack: [7,8,9]
i=10 (2): 2>1, pop 9. bottom=1, left=8(h=2), right=10(h=2).
           w=10-8-1=1, h=min(2,2)-1=1. water+=1. Water=6.
           2>=2, stop. Push 10. Stack: [7,8,10]
i=11 (1): Push. Stack: [7,8,10,11]

Total water = 6
```

**Edge Cases:**
- Empty array or length < 3: return 0
- Flat surface: return 0
- V-shape: simple triangle of water
- Decreasing then increasing: single pool

**Follow-up:**
- Trapping Rain Water II (LC 407) — 3D version on a 2D grid, uses a min-heap (priority queue) BFS approach.
- What if bars have different widths? Adjust width calculation.

**All three approaches compared:**

| Approach | Time | Space | Intuition |
|----------|------|-------|-----------|
| Prefix max arrays | O(n) | O(n) | Water at i = min(max_left, max_right) - height[i] |
| Monotonic stack | O(n) | O(n) | Fill water layer by layer in valleys |
| Two pointers | O(n) | O(1) | Process from the smaller side inward |

In an interview, I recommend starting with the prefix max approach (easiest to explain), then optimizing to two pointers if asked. Mention the stack approach to show breadth.

---

## Additional Problem: Sum of Subarray Minimums (LC 907 — Medium)

**Problem:** Given an integer array `arr`, find the sum of `min(b)` for every (contiguous) subarray `b` of `arr`. Return the answer modulo 10^9 + 7.

**Key Insight (Contribution Technique):**
Instead of computing the minimum of every subarray, ask: "How many subarrays have `arr[i]` as their minimum?" If arr[i] is the minimum for `count` subarrays, its contribution to the total sum is `arr[i] * count`.

For arr[i] to be the minimum of subarray [l, r], arr[i] must be the smallest element in that range. This means:
- l can extend left until we hit an element < arr[i] (previous smaller element)
- r can extend right until we hit an element <= arr[i] (next smaller-or-equal element)

Use both "previous smaller" and "next smaller or equal" to find boundaries. The number of subarrays where arr[i] is the minimum = `left_count * right_count` where left_count = i - prev_smaller_idx and right_count = next_smaller_idx - i.

**Why "strictly smaller" on one side and "smaller or equal" on the other?** To avoid double-counting when there are duplicate values.

```python
def sumSubarrayMins(arr: list[int]) -> int:
    """
    LC 907: Sum of Subarray Minimums

    Time: O(n)
    Space: O(n)
    """
    MOD = 10**9 + 7
    n = len(arr)

    # Previous smaller element (strictly smaller)
    prev_smaller = [-1] * n
    stack = []
    for i in range(n):
        while stack and arr[stack[-1]] >= arr[i]:
            stack.pop()
        prev_smaller[i] = stack[-1] if stack else -1
        stack.append(i)

    # Next smaller or equal element
    next_smaller = [n] * n
    stack = []
    for i in range(n - 1, -1, -1):
        while stack and arr[stack[-1]] > arr[i]:
            stack.pop()
        next_smaller[i] = stack[-1] if stack else n
        stack.append(i)

    # Calculate contribution of each element
    total = 0
    for i in range(n):
        left = i - prev_smaller[i]   # Number of choices for left boundary
        right = next_smaller[i] - i  # Number of choices for right boundary
        total = (total + arr[i] * left * right) % MOD

    return total
```

**Dry Run:**
```
arr = [3, 1, 2, 4]

prev_smaller: [-1, -1, 1, 2]  (indices of previous strictly smaller)
next_smaller: [1, 4, 4, 4]    (indices of next smaller-or-equal)

Contributions:
  i=0: left=0-(-1)=1, right=1-0=1. contrib = 3*1*1 = 3
  i=1: left=1-(-1)=2, right=4-1=3. contrib = 1*2*3 = 6
  i=2: left=2-1=1, right=4-2=2. contrib = 2*1*2 = 4
  i=3: left=3-2=1, right=4-3=1. contrib = 4*1*1 = 4

Total = 3+6+4+4 = 17

Verify: subarrays and their mins:
  [3]=3, [1]=1, [2]=2, [4]=4, [3,1]=1, [1,2]=1, [2,4]=2, [3,1,2]=1, [1,2,4]=1, [3,1,2,4]=1
  Sum = 3+1+2+4+1+1+2+1+1+1 = 17 ✓
```

---

## Common Mistakes & Interview Tips

### Common Mistakes

1. **Storing values vs indices in the stack:** Almost always store indices. You can look up values from the array, but you need indices for position calculations (distances, widths).

2. **Off-by-one in width calculation:** For the histogram problem, the width when the stack is empty is `i` (the bar extends all the way to the left edge), not `i - 1`. When the stack is not empty, it is `i - stack[-1] - 1`.

3. **Forgetting the sentinel:** In the histogram problem, appending a 0-height bar at the end forces all remaining bars to be processed. Without it, you need extra code to handle bars remaining in the stack.

4. **Confusing increasing vs decreasing:**
   - Next Greater → decreasing stack (bigger elements cause pops)
   - Next Smaller → increasing stack (smaller elements cause pops)
   Draw it out if unsure.

5. **Deque direction confusion:** For sliding window max, pop from the back (elements smaller than current) and check the front for window validity. Getting these backwards breaks everything.

6. **Not restoring the input:** If you use a sentinel (append to the array), either pop it afterward or work on a copy. Modifying the input is a bad habit in interviews.

### Interview Tips

1. **Start with the brute force:** "The brute force is O(n^2) — for each element, scan for the next greater. But notice that we are doing redundant work because many elements share the same answer."

2. **Explain the invariant:** "I maintain a monotonic decreasing stack. At any point, elements in the stack are still waiting for their next greater element. When a larger element arrives, it answers the question for all smaller elements at the top of the stack."

3. **Prove O(n) time:** "Each element is pushed once and popped at most once, so the total number of operations is 2n = O(n), even though there is a while loop inside the for loop."

4. **Draw it:** Sketch the stack state for 3-4 iterations. This helps both you and the interviewer follow the logic.

5. **Know multiple approaches for Trapping Rain Water:** This is a very common interview question. Being able to discuss prefix arrays, monotonic stack, and two pointers shows depth.

6. **Histogram as a building block:** Knowing that LC 84 (histogram) unlocks LC 85 (maximal rectangle) shows pattern recognition that interviewers love.

---

## Pattern Connections

| From Monotonic Stack/Queue | Connect To | How |
|---------------------------|-----------|-----|
| Next Greater Element | Stack fundamentals | Core stack application |
| Largest Rectangle in Histogram | Maximal Rectangle (LC 85) | Each row becomes a histogram |
| Sliding Window Maximum | Sliding Window pattern | Deque optimizes window max queries |
| Trapping Rain Water | Two Pointers | Alternative O(1) space approach |
| Daily Temperatures | Stack + index arithmetic | Distance = index difference |
| Sum of Subarray Minimums (LC 907) | Contribution technique | Count how many subarrays each element is the min of |
| Stock Span (LC 901) | Previous Greater Element | How many consecutive days was price lower? |

### Decision Framework

```
Need next/previous greater/smaller for each element?
├── Single array, one-time query
│   └── Monotonic Stack — O(n)
├── Sliding window min/max?
│   └── Monotonic Deque — O(n)
├── Rectangle areas in histogram?
│   └── Monotonic Increasing Stack — find boundaries
├── Trapping water between bars?
│   ├── Monotonic Decreasing Stack — layer by layer
│   ├── Prefix max arrays — O(n) time, O(n) space
│   └── Two pointers — O(n) time, O(1) space
└── 2D matrix rectangle problems?
    └── Build histograms row by row + LC 84
```

---

## Additional Problem: Stock Span Problem (LC 901 — Medium)

**Problem:** Design a class `StockSpanner` that collects daily price quotes and returns the span for each day. The span is the maximum number of consecutive days (starting from today going backward) for which the stock price was <= today's price.

**Key Insight:**
This is "previous greater element" — the span equals `current_index - index_of_previous_greater_element`. Use a monotonic decreasing stack of (price, index).

```python
class StockSpanner:
    """
    LC 901: Online Stock Span

    push: O(1) amortized
    Space: O(n)
    """
    def __init__(self):
        self.stack = []  # (price, index)
        self.index = 0

    def next(self, price: int) -> int:
        while self.stack and self.stack[-1][0] <= price:
            self.stack.pop()

        span = self.index - self.stack[-1][1] if self.stack else self.index + 1
        self.stack.append((price, self.index))
        self.index += 1
        return span
```

**Dry Run:**
```
next(100): stack=[(100,0)]. span=1 (just today). Return 1.
next(80):  80<100, push. stack=[(100,0),(80,1)]. span=1. Return 1.
next(60):  60<80, push. stack=[(100,0),(80,1),(60,2)]. span=1. Return 1.
next(70):  70>60, pop. 70<80, stop. stack=[(100,0),(80,1),(70,3)]. span=3-1=2. Return 2.
next(60):  60<70, push. stack=[(100,0),(80,1),(70,3),(60,4)]. span=1. Return 1.
next(75):  75>60,pop. 75>70,pop. 75<80,stop. stack=[(100,0),(80,1),(75,5)]. span=5-1=4. Return 4.
next(85):  85>75,pop. 85>80,pop. 85<100,stop. stack=[(100,0),(85,6)]. span=6-0=6. Return 6.
```

---

## Additional Problem: Next Greater Element II (LC 503 — Medium)

**Problem:** Given a circular integer array, find the next greater element for each index. The array wraps around.

**Key Insight:**
Process the array twice (indices 0 to 2n-1, using `i % n`). Elements in the second pass handle the wrap-around. Only push during the first pass.

```python
def nextGreaterElements(nums: list[int]) -> list[int]:
    """
    LC 503: Next Greater Elements II (Circular)

    Time: O(n)
    Space: O(n)
    """
    n = len(nums)
    result = [-1] * n
    stack = []

    for i in range(2 * n):
        while stack and nums[i % n] > nums[stack[-1]]:
            result[stack.pop()] = nums[i % n]
        if i < n:
            stack.append(i)

    return result
```

**Dry Run:**
```
nums = [1, 2, 1]

First pass (i=0,1,2):
  i=0 (1): push 0. Stack: [0]
  i=1 (2): 2>1, pop 0→result[0]=2. Push 1. Stack: [1]
  i=2 (1): 1<2. Push 2. Stack: [1, 2]

Second pass (i=3,4,5):
  i=3 (nums[0]=1): 1<1. (no pops, no push)
  i=4 (nums[1]=2): 2>1, pop 2→result[2]=2. (no push, i>=n)
  i=5 (nums[2]=1): 1<2. Done.

Remaining: index 1 → result[1]=-1 (no next greater in circular array)

Result: [2, -1, 2]
```

---

## Interview Cheat Sheet

**When the interviewer says these words, think monotonic stack:**
- "Next greater" → decreasing stack
- "Next smaller" → increasing stack
- "Largest rectangle" → increasing stack (find boundaries)
- "Trapping water" → decreasing stack (or two pointers)
- "Sliding window max" → monotonic deque
- "Stock span" → decreasing stack
- "Sum of subarray minimums" → contribution technique with two stacks

**Key insight to communicate:**
"Each element is pushed and popped at most once across the entire algorithm, so despite the nested loop, the total time is O(n)."

**Common mistake to avoid:**
Storing values instead of indices in the stack. Always store indices — you can look up values from the array, but index differences are needed for distance/width calculations.

---

## Detailed Complexity Analysis

### Why Monotonic Stack is O(n)

The key insight is the **amortized analysis**. Consider what happens to each element:

1. Each element is **pushed exactly once** (when we process it in the for loop)
2. Each element is **popped at most once** (when a later element causes it to be popped from the while loop)

Total operations: at most n pushes + n pops = 2n operations = O(n)

The while loop inside the for loop does NOT make this O(n^2). The while loop's total work across all iterations of the for loop is bounded by n (total pops <= n pushes).

### When Monotonic Stack is O(n log n)

If you need to maintain a sorted structure with arbitrary insertions (not just at one end), you need a balanced BST or sorted container, which is O(n log n). The monotonic stack is O(n) precisely because elements only flow in one direction (LIFO — push and pop from the same end).

### Space Complexity

- **Worst case:** O(n) — all elements pushed, none popped (e.g., strictly decreasing array for a decreasing stack)
- **Best case:** O(1) — every element causes all previous elements to be popped (e.g., strictly increasing array for a decreasing stack)
- **Average case:** O(n) — stack size fluctuates but can hold up to n elements

### Monotonic Deque Complexity

For sliding window max/min with a deque:
- Each element enters the deque once (from the right) and leaves at most once (from either end)
- Total: O(n) across all operations
- Space: O(k) where k is the window size (at most k elements in the deque at any time)

---

## Problem Difficulty Progression

For interview preparation, practice these problems in this order:

**Tier 1 — Foundation (must solve easily):**
1. Next Greater Element I (LC 496) — template application
2. Daily Temperatures (LC 739) — index difference variant
3. Next Greater Element II (LC 503) — circular array extension

**Tier 2 — Core Patterns (should solve within 20 min):**
4. Stock Span Problem (LC 901) — previous greater element
5. Sum of Subarray Minimums (LC 907) — contribution technique
6. Sliding Window Maximum (LC 239) — monotonic deque

**Tier 3 — Hard Applications (stretch goals):**
7. Largest Rectangle in Histogram (LC 84) — boundary finding
8. Trapping Rain Water (LC 42) — multiple approaches
9. Maximal Rectangle (LC 85) — combines histogram + row processing
10. Maximum Width Ramp (LC 962) — reverse thinking with monotonic stack

---

## Common Variations in Interviews

### Variation 1: "Can you solve this without a stack?"
For next greater element: yes, you can use a brute force O(n^2) scan. But the stack approach is O(n) and demonstrates algorithmic maturity. For trapping rain water, the two-pointer approach avoids both stack and prefix arrays.

### Variation 2: "What about a circular array?"
Process the array twice (indices 0 to 2n-1) using `i % n`. Only push indices from the first pass to avoid duplicates. See Next Greater Element II (LC 503).

### Variation 3: "What if we need both next greater AND previous smaller?"
Run two separate monotonic stack passes — one for next greater (left to right, decreasing stack) and one for previous smaller (left to right, increasing stack). Each pass is O(n), so total is still O(n).

### Variation 4: "How would you handle ties?"
For strict greater: use `>` in the pop condition. For greater-or-equal: use `>=`. The choice affects whether equal elements are treated as "greater" or not. This matters for avoiding double-counting in contribution problems (LC 907).

### Variation 5: "Can you explain why the while loop is not O(n) per iteration?"
"Yes. Consider the total pushes and pops across ALL iterations. Each of the n elements is pushed at most once and popped at most once. So the total work from all while-loop iterations combined is at most n. The amortized cost per outer-loop iteration is O(1)."

This is one of the most important complexity analysis insights for FAANG interviews.

---

## Thinking Framework: How to Approach a New Monotonic Stack Problem

When you see a new problem that might involve monotonic stack/queue, work through this mental framework:

### Step 1: Identify the question being asked for each element
- "What is the next/previous element that is greater/smaller?"
- "For each element, what is the maximum range where it is the min/max?"
- "What is the max/min in a sliding window?"

### Step 2: Determine the stack direction
- If you need elements that are **greater** to answer the question → the stack holds elements in **decreasing** order (a greater element pops the stack)
- If you need elements that are **smaller** to answer the question → the stack holds elements in **increasing** order (a smaller element pops the stack)

### Step 3: Determine what the answer is
- **Next greater/smaller:** The answer for a popped element is the current element (what caused the pop)
- **Previous greater/smaller:** The answer for the current element is the stack top after pops
- **Boundaries for rectangles:** Both left and right boundaries come from the stack state at pop time

### Step 4: Determine the traversal direction
- Forward (left to right) for most problems
- Backward (right to left) for some "previous" variants
- Twice for circular arrays

### Step 5: Handle edge cases
- What is the default answer for elements that are never popped? (usually -1 or n)
- Should ties be treated as "greater" or not? (affects `>` vs `>=` in the pop condition)
- Should you append a sentinel value (like 0 in histogram) to force all elements to be processed?

### Example: Applying the Framework to a New Problem

**Problem:** "For each element in an array, find the distance to the nearest smaller element to its left."

Step 1: We need the "previous smaller element" and the distance to it.
Step 2: Looking for smaller elements → use an increasing stack (smaller pops the stack).
Step 3: Previous smaller → answer is stack top after pops. Distance = current index - stack top index.
Step 4: Forward traversal (left to right).
Step 5: Default answer for elements with no previous smaller = -1 (or infinity).

```python
def nearest_smaller_distance(nums):
    n = len(nums)
    dist = [-1] * n
    stack = []  # Increasing stack of indices
    for i in range(n):
        while stack and nums[stack[-1]] >= nums[i]:
            stack.pop()
        if stack:
            dist[i] = i - stack[-1]
        stack.append(i)
    return dist
```

This systematic approach prevents the common mistake of guessing the stack direction and getting it wrong.

### Quick Reference: Pop Condition Cheat Sheet

| Goal | Pop when `nums[i]` is... | Stack order (bottom→top) |
|------|--------------------------|--------------------------|
| Next Greater | `> stack top` | Decreasing |
| Next Greater or Equal | `>= stack top` | Strictly decreasing |
| Next Smaller | `< stack top` | Increasing |
| Next Smaller or Equal | `<= stack top` | Strictly increasing |
| Previous Greater | `> stack top` (same direction) | Decreasing |
| Previous Smaller | `< stack top` (same direction) | Increasing |
