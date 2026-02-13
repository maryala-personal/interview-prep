# Monotonic Stack/Queue Pattern

## 1. What is Monotonic Stack/Queue?

### Explain Like I'm 5
Imagine you're standing in a line of kids of different heights. You want to find, for each kid, who is the next taller kid behind them. Instead of checking every single person behind each kid (which takes forever), you can use a smart trick: keep a special line where kids are always arranged from tallest to shortest. When a new tall kid comes, all the shorter kids in your special line just found their "next taller person"!

### Technical Definition
A **Monotonic Stack** is a stack data structure where elements are maintained in either strictly increasing or strictly decreasing order. When a new element violates this order, elements are popped from the stack until the monotonic property is restored.

A **Monotonic Queue** (often implemented as a deque) extends this concept to support operations on both ends, commonly used for sliding window problems where you need to maintain min/max values efficiently.

**Key Properties:**
- **Monotonic Increasing Stack**: Elements increase from bottom to top (e.g., [1, 3, 5, 7])
- **Monotonic Decreasing Stack**: Elements decrease from bottom to top (e.g., [9, 6, 4, 2])
- **Time Complexity**: O(n) for processing n elements (each element pushed/popped at most once)
- **Space Complexity**: O(n) worst case

## 2. Real-World Analogy

### Temperature Waiting Time
Imagine you're checking the weather forecast for the next week. For each day, you want to know: "How many days until a warmer day?"

**Without Monotonic Stack (Brute Force):**
For Day 1, check Day 2, Day 3, Day 4... until you find a warmer day.
For Day 2, check Day 3, Day 4, Day 5... until you find a warmer day.
This is like asking everyone individually about everyone else.

**With Monotonic Stack (Optimized):**
Keep a stack of days with decreasing temperatures. When a warmer day arrives, it answers the question for all cooler days in the stack. It's like having a smart system that automatically matches people with their answers as new information comes in.

### Next Taller Building
You're standing at different buildings in a city, and for each building, you want to know which is the next taller building you'll encounter as you walk forward.

The monotonic stack lets you solve this in one pass, answering questions for multiple buildings simultaneously when a tall building appears.

## 3. When to Use

### Clear Signals (Pattern Recognition Keywords):
- ✅ "**Next Greater Element**"
- ✅ "**Next Smaller Element**"
- ✅ "**Previous Greater Element**"
- ✅ "**Previous Smaller Element**"
- ✅ "**Sliding Window Maximum/Minimum**"
- ✅ "**Largest Rectangle**" (in histogram, matrix)
- ✅ "**Trapping Rain Water**"
- ✅ "**Daily Temperatures**"
- ✅ "**Stock Span Problem**"

### Problem Characteristics:
1. You need to find the next/previous greater/smaller element for each element
2. You're dealing with a linear scan (array/list)
3. The brute force approach involves nested loops (O(n²))
4. You need to maintain a sliding window with min/max queries
5. The problem involves relationships between elements based on their relative values

## 4. The Problem: Daily Temperatures

### Problem Statement
Given an array of integers `temperatures` representing the daily temperatures, return an array `answer` such that `answer[i]` is the number of days you have to wait after the `i-th` day to get a warmer temperature. If there is no future day for which this is possible, keep `answer[i] == 0`.

**Example 1:**
```
Input: temperatures = [73,74,75,71,69,72,76,73]
Output: [1,1,4,2,1,1,0,0]
```

**Explanation:**
- Day 0 (73°): Day 1 is warmer (74°) → wait 1 day
- Day 1 (74°): Day 2 is warmer (75°) → wait 1 day
- Day 2 (75°): Day 6 is warmer (76°) → wait 4 days
- Day 3 (71°): Day 5 is warmer (72°) → wait 2 days
- Day 4 (69°): Day 5 is warmer (72°) → wait 1 day
- Day 5 (72°): Day 6 is warmer (76°) → wait 1 day
- Day 6 (76°): No warmer day → 0
- Day 7 (73°): No warmer day → 0

**Example 2:**
```
Input: temperatures = [30,40,50,60]
Output: [1,1,1,0]
```

**Example 3:**
```
Input: temperatures = [30,60,90]
Output: [1,1,0]
```

## 5. Brute Force Approach

### Algorithm
For each day, scan forward through all subsequent days until finding a warmer temperature.

```python
def dailyTemperatures_bruteforce(temperatures):
    """
    Brute Force: For each day, check all future days.

    Time Complexity: O(n²) - nested loops
    Space Complexity: O(1) - only output array (not counting result)
    """
    n = len(temperatures)
    answer = [0] * n

    # For each day
    for i in range(n):
        # Check all future days
        for j in range(i + 1, n):
            # If we found a warmer day
            if temperatures[j] > temperatures[i]:
                answer[i] = j - i
                break  # Stop searching for this day

    return answer


# Test
temps = [73, 74, 75, 71, 69, 72, 76, 73]
print(dailyTemperatures_bruteforce(temps))  # [1, 1, 4, 2, 1, 1, 0, 0]
```

### Why It's Inefficient
- For each of n days, we potentially scan n-1 future days
- In the worst case (decreasing temperatures like [100, 90, 80, 70]), we make n*(n-1)/2 comparisons
- We're solving the same subproblems repeatedly

## 6. Optimized Solution: Monotonic Decreasing Stack

### Key Insight
**We can solve this in ONE pass** by maintaining a stack of indices where temperatures are in decreasing order. When we encounter a warmer temperature, it answers the question for all cooler temperatures in the stack.

### Algorithm
1. Iterate through temperatures with their indices
2. While the current temperature is warmer than the temperature at the top of the stack:
   - Pop the index from the stack
   - The answer for that popped index is (current_index - popped_index)
3. Push the current index onto the stack
4. After iteration, any remaining indices in the stack have no warmer day (answer = 0)

### Implementation

```python
def dailyTemperatures(temperatures):
    """
    Monotonic Decreasing Stack Solution

    The stack stores indices of days with decreasing temperatures.
    When a warmer day arrives, it resolves all cooler days in the stack.

    Time Complexity: O(n) - each index pushed and popped at most once
    Space Complexity: O(n) - stack can hold all indices in worst case

    Args:
        temperatures: List[int] - daily temperatures

    Returns:
        List[int] - days to wait for warmer temperature
    """
    n = len(temperatures)
    answer = [0] * n  # Initialize all to 0 (no warmer day found yet)
    stack = []  # Monotonic decreasing stack (stores indices)

    # Process each day
    for curr_day in range(n):
        curr_temp = temperatures[curr_day]

        # While current temp is warmer than temp at top of stack
        # This means we found the answer for days in the stack
        while stack and temperatures[stack[-1]] < curr_temp:
            prev_day = stack.pop()
            # Calculate days to wait
            answer[prev_day] = curr_day - prev_day

        # Add current day to stack
        # It's waiting to find its warmer day
        stack.append(curr_day)

    # Any days remaining in stack have no warmer day (already initialized to 0)
    return answer


# Detailed walkthrough example
def dailyTemperatures_verbose(temperatures):
    """Same algorithm with detailed print statements for learning"""
    n = len(temperatures)
    answer = [0] * n
    stack = []

    print("Processing temperatures:", temperatures)
    print()

    for curr_day in range(n):
        curr_temp = temperatures[curr_day]
        print(f"Day {curr_day}: Temperature = {curr_temp}")
        print(f"  Stack before: {stack}")

        # Pop all days that are cooler than current day
        popped_days = []
        while stack and temperatures[stack[-1]] < curr_temp:
            prev_day = stack.pop()
            answer[prev_day] = curr_day - prev_day
            popped_days.append(prev_day)
            print(f"    Found answer for Day {prev_day}: wait {answer[prev_day]} days")

        stack.append(curr_day)
        print(f"  Stack after: {stack}")
        print(f"  Answer so far: {answer}")
        print()

    print(f"Final answer: {answer}")
    return answer


# Test cases
print("=" * 60)
print("Test 1:")
temps1 = [73, 74, 75, 71, 69, 72, 76, 73]
result1 = dailyTemperatures(temps1)
print(f"Input: {temps1}")
print(f"Output: {result1}")
print()

print("=" * 60)
print("Test 2 (Detailed walkthrough):")
temps2 = [73, 74, 75, 71, 69, 72, 76, 73]
dailyTemperatures_verbose(temps2)
```

### Step-by-Step Walkthrough

For `temperatures = [73, 74, 75, 71, 69, 72, 76, 73]`:

```
Day 0 (73°):
  Stack: []
  Action: Push index 0
  Stack: [0]
  Answer: [0, 0, 0, 0, 0, 0, 0, 0]

Day 1 (74°):
  Stack: [0]
  74 > 73, so pop index 0
  answer[0] = 1 - 0 = 1 (Day 0 waits 1 day)
  Push index 1
  Stack: [1]
  Answer: [1, 0, 0, 0, 0, 0, 0, 0]

Day 2 (75°):
  Stack: [1]
  75 > 74, so pop index 1
  answer[1] = 2 - 1 = 1 (Day 1 waits 1 day)
  Push index 2
  Stack: [2]
  Answer: [1, 1, 0, 0, 0, 0, 0, 0]

Day 3 (71°):
  Stack: [2]
  71 < 75, no popping
  Push index 3
  Stack: [2, 3]
  Answer: [1, 1, 0, 0, 0, 0, 0, 0]

Day 4 (69°):
  Stack: [2, 3]
  69 < 71, no popping
  Push index 4
  Stack: [2, 3, 4]
  Answer: [1, 1, 0, 0, 0, 0, 0, 0]

Day 5 (72°):
  Stack: [2, 3, 4]
  72 > 69, pop index 4: answer[4] = 5 - 4 = 1
  72 > 71, pop index 3: answer[3] = 5 - 3 = 2
  72 < 75, stop popping
  Push index 5
  Stack: [2, 5]
  Answer: [1, 1, 0, 2, 1, 0, 0, 0]

Day 6 (76°):
  Stack: [2, 5]
  76 > 72, pop index 5: answer[5] = 6 - 5 = 1
  76 > 75, pop index 2: answer[2] = 6 - 2 = 4
  Push index 6
  Stack: [6]
  Answer: [1, 1, 4, 2, 1, 1, 0, 0]

Day 7 (73°):
  Stack: [6]
  73 < 76, no popping
  Push index 7
  Stack: [6, 7]
  Answer: [1, 1, 4, 2, 1, 1, 0, 0]

Final: Indices 6 and 7 remain in stack (no warmer day found)
```

## 7. Time & Space Complexity Analysis

### Brute Force
- **Time Complexity**: O(n²)
  - Outer loop: n iterations
  - Inner loop: up to n iterations for each
  - Worst case: decreasing temperatures [100, 90, 80, ...] requires checking all remaining elements

- **Space Complexity**: O(1)
  - Only using the output array (if we don't count it)

### Monotonic Stack
- **Time Complexity**: O(n)
  - Each element is pushed onto the stack exactly once: O(n)
  - Each element is popped from the stack at most once: O(n)
  - Total operations: O(n + n) = O(n)
  - Even though we have a while loop, amortized cost is O(1) per element

- **Space Complexity**: O(n)
  - Stack can contain all n indices in worst case (e.g., decreasing temperatures)
  - Output array is O(n) but typically not counted

### Comparison

| Approach | Time | Space | Best Case | Worst Case |
|----------|------|-------|-----------|------------|
| Brute Force | O(n²) | O(1) | O(n) - all increasing | O(n²) - all decreasing |
| Monotonic Stack | O(n) | O(n) | O(n) | O(n) |

**Key Insight**: Monotonic stack trades space for time, achieving linear time complexity.

## 8. Variations

### 8.1 Monotonic Increasing vs Decreasing Stack

#### Monotonic Decreasing Stack
**Elements decrease from bottom to top**
- Used for: "Next Greater Element" problems
- When new element is **greater**, pop smaller elements

```python
def next_greater_element(nums):
    """
    Find next greater element for each element.
    Uses monotonic decreasing stack.
    """
    n = len(nums)
    result = [-1] * n
    stack = []  # Stores indices

    for i in range(n):
        # Pop all smaller elements (current is their next greater)
        while stack and nums[stack[-1]] < nums[i]:
            idx = stack.pop()
            result[idx] = nums[i]
        stack.append(i)

    return result

# Example
print(next_greater_element([2, 1, 2, 4, 3]))  # [4, 2, 4, -1, -1]
```

#### Monotonic Increasing Stack
**Elements increase from bottom to top**
- Used for: "Next Smaller Element" problems
- When new element is **smaller**, pop larger elements

```python
def next_smaller_element(nums):
    """
    Find next smaller element for each element.
    Uses monotonic increasing stack.
    """
    n = len(nums)
    result = [-1] * n
    stack = []  # Stores indices

    for i in range(n):
        # Pop all larger elements (current is their next smaller)
        while stack and nums[stack[-1]] > nums[i]:
            idx = stack.pop()
            result[idx] = nums[i]
        stack.append(i)

    return result

# Example
print(next_smaller_element([4, 2, 1, 5, 3]))  # [2, 1, -1, 3, -1]
```

### 8.2 Previous Greater/Smaller Elements

#### Previous Greater Element

```python
def previous_greater_element(nums):
    """
    Find previous greater element for each element.
    Monotonic decreasing stack (scan left to right).
    """
    n = len(nums)
    result = [-1] * n
    stack = []  # Stores actual values (or indices if needed)

    for i in range(n):
        # Pop all smaller or equal elements
        while stack and stack[-1] <= nums[i]:
            stack.pop()

        # Top of stack is previous greater element
        if stack:
            result[i] = stack[-1]

        stack.append(nums[i])

    return result

# Example
print(previous_greater_element([4, 5, 2, 10, 8]))  # [-1, -1, 5, -1, 10]
```

### 8.3 Monotonic Queue (Deque) for Sliding Window

**Problem**: Sliding Window Maximum

```python
from collections import deque

def maxSlidingWindow(nums, k):
    """
    Find maximum in each sliding window of size k.
    Uses monotonic decreasing deque.

    Deque stores indices in decreasing order of their values.
    Front of deque always has index of maximum element in current window.

    Time: O(n) - each element added/removed at most once
    Space: O(k) - deque size at most k
    """
    if not nums or k == 0:
        return []

    result = []
    dq = deque()  # Stores indices in decreasing order of values

    for i in range(len(nums)):
        # Remove indices outside current window
        while dq and dq[0] < i - k + 1:
            dq.popleft()

        # Remove indices with smaller values (they can't be max)
        while dq and nums[dq[-1]] < nums[i]:
            dq.pop()

        dq.append(i)

        # Add to result once we have a full window
        if i >= k - 1:
            result.append(nums[dq[0]])

    return result

# Example
print(maxSlidingWindow([1,3,-1,-3,5,3,6,7], k=3))  # [3,3,5,5,6,7]
```

**Why Deque instead of Stack?**
- Need to remove from **both ends**: front (expired indices), back (smaller values)
- Stack only allows removal from one end

### 8.4 Circular Array Problems

**Problem**: Next Greater Element in Circular Array

```python
def nextGreaterElements_circular(nums):
    """
    Find next greater element in circular array.
    Trick: Process array twice (simulate circular).
    """
    n = len(nums)
    result = [-1] * n
    stack = []

    # Process array twice (circular behavior)
    for i in range(2 * n):
        idx = i % n  # Wrap around

        while stack and nums[stack[-1]] < nums[idx]:
            result[stack.pop()] = nums[idx]

        # Only push in first pass to avoid duplicates
        if i < n:
            stack.append(idx)

    return result

# Example
print(nextGreaterElements_circular([1,2,1]))  # [2,-1,2]
```

## 9. Pro Tips for Senior Engineers

### When to Use Monotonic Stack
1. **Pattern Recognition**: If brute force involves nested loops comparing elements, consider monotonic stack
2. **One-Pass Optimization**: When you need to find relationships between elements in linear time
3. **Space-Time Tradeoff**: Acceptable to use O(n) space to achieve O(n) time

### Edge Cases to Consider
1. **Empty array**: Return empty result
2. **Single element**: Usually returns [0] or [-1]
3. **All identical elements**: No next greater/smaller
4. **Strictly increasing**: Each element's answer is immediate next (for next greater)
5. **Strictly decreasing**: No elements have next greater (all 0 or -1)

```python
def dailyTemperatures_robust(temperatures):
    """Production-ready with edge case handling"""
    # Edge case: empty or single element
    if not temperatures or len(temperatures) <= 1:
        return [0] * len(temperatures)

    n = len(temperatures)
    answer = [0] * n
    stack = []

    for curr_day in range(n):
        while stack and temperatures[stack[-1]] < temperatures[curr_day]:
            prev_day = stack.pop()
            answer[prev_day] = curr_day - prev_day
        stack.append(curr_day)

    return answer
```

### Common Optimizations

#### 1. Store Values vs Indices
```python
# Store indices (more flexible - can compute distances, access original array)
stack = []  # indices
stack.append(i)

# Store values (simpler if you only need value comparisons)
stack = []  # values
stack.append(nums[i])
```

#### 2. Early Termination
```python
# If you only need to find one element's next greater, can break early
def find_next_greater_for_index(nums, target_idx):
    for i in range(target_idx + 1, len(nums)):
        if nums[i] > nums[target_idx]:
            return i
    return -1
```

#### 3. Reverse Iteration
```python
# Sometimes processing right to left is cleaner
def next_greater_reverse(nums):
    n = len(nums)
    result = [-1] * n
    stack = []

    for i in range(n - 1, -1, -1):
        while stack and stack[-1] <= nums[i]:
            stack.pop()
        if stack:
            result[i] = stack[-1]
        stack.append(nums[i])

    return result
```

### Performance Considerations
1. **Amortized O(1)**: Each element pushed/popped at most once across all iterations
2. **Cache Locality**: Stack operations are cache-friendly (accessing top elements)
3. **Early Exit**: While loop exits quickly when monotonic property maintained

## 10. Problem Recognition Checklist

Use monotonic stack/queue when you see:

- [ ] Keywords: "next", "previous", "greater", "smaller", "warmer", "taller"
- [ ] Need to find nearest element satisfying a condition
- [ ] Brute force would use nested loops (O(n²))
- [ ] Processing elements sequentially (array/list)
- [ ] Comparing elements based on their values
- [ ] Need to maintain max/min in sliding window
- [ ] Problem involves "span" or "range" of elements
- [ ] Histogram or area problems

**Immediate Red Flags for Monotonic Stack:**
- ✅ "Daily Temperatures" - next warmer day
- ✅ "Stock Span" - consecutive days with lower prices
- ✅ "Largest Rectangle in Histogram"
- ✅ "Trapping Rain Water"
- ✅ "Next Greater Element"
- ✅ "Sliding Window Maximum"

## 11. Practice Problems

### Beginner Level
1. **LeetCode 496**: Next Greater Element I
   - Simple next greater element lookup
   - Good for understanding basic concept

2. **LeetCode 739**: Daily Temperatures
   - Classic monotonic stack problem
   - Highly recommended for learning

### Intermediate Level
3. **LeetCode 503**: Next Greater Element II (Circular Array)
   - Introduces circular array handling
   - Requires processing array twice

4. **LeetCode 239**: Sliding Window Maximum
   - Uses monotonic deque instead of stack
   - Important variation

5. **LeetCode 901**: Online Stock Span
   - Classic application of monotonic stack
   - Real-world problem

6. **LeetCode 1475**: Final Prices With a Special Discount
   - Next smaller element variation
   - Good for practicing monotonic increasing stack

### Advanced Level
7. **LeetCode 84**: Largest Rectangle in Histogram
   - Complex application of monotonic stack
   - Requires finding both prev/next smaller elements

8. **LeetCode 85**: Maximal Rectangle
   - Extension of histogram problem to 2D
   - Combines multiple techniques

9. **LeetCode 42**: Trapping Rain Water
   - Can be solved with monotonic stack
   - Multiple solution approaches possible

10. **LeetCode 456**: 132 Pattern
    - Advanced pattern matching with stack
    - Tests deep understanding

### Expert Level
11. **LeetCode 1776**: Car Fleet II
    - Complex monotonic stack application
    - Requires mathematical reasoning

12. **LeetCode 2334**: Subarray With Elements Greater Than Varying Threshold
    - Combines monotonic stack with binary search concepts

## 12. Common Mistakes

### Mistake 1: Confusing Increasing vs Decreasing Stack
```python
# WRONG: Using increasing stack for next greater element
# This will give you PREVIOUS smaller, not next greater!
def wrong_next_greater(nums):
    stack = []
    for i in range(len(nums)):
        while stack and nums[stack[-1]] > nums[i]:  # Wrong direction!
            stack.pop()
        stack.append(i)
```

**Fix**: For next **greater**, use **decreasing** stack (pop when current is greater)

### Mistake 2: Storing Values When You Need Indices
```python
# WRONG: Can't compute distance without indices
def wrong_daily_temps(temps):
    stack = []
    for temp in temps:
        while stack and stack[-1] < temp:
            stack.pop()  # Lost index information!
        stack.append(temp)
```

**Fix**: Store indices when you need to compute positions or distances

### Mistake 3: Not Initializing Result Array
```python
# WRONG: Missing initialization
def wrong_solution(nums):
    result = []  # Should be [0] * n or [-1] * n
    stack = []
    for i in range(len(nums)):
        while stack and nums[stack[-1]] < nums[i]:
            prev = stack.pop()
            result[prev] = i - prev  # Index error!
```

**Fix**: Initialize result array to default values (0 or -1)

### Mistake 4: Forgetting to Handle Stack Remainder
```python
# WRONG: Elements left in stack are ignored
def incomplete_solution(nums):
    result = [-1] * len(nums)
    stack = []
    for i in range(len(nums)):
        while stack and nums[stack[-1]] < nums[i]:
            result[stack.pop()] = nums[i]
        stack.append(i)
    # Missing: stack may still have elements (no next greater found)
    return result
```

**Fix**: Either initialize to default (0/-1) or explicitly handle remaining elements

### Mistake 5: Off-by-One Errors in Sliding Window
```python
# WRONG: Window boundary calculation
def wrong_sliding_max(nums, k):
    dq = deque()
    result = []
    for i in range(len(nums)):
        # WRONG: Should be i - k + 1, not i - k
        while dq and dq[0] <= i - k:
            dq.popleft()
```

**Fix**: Carefully calculate window boundaries: `[i - k + 1, i]`

### Mistake 6: Not Removing Outdated Elements First
```python
# WRONG: Order of operations in sliding window
def wrong_order(nums, k):
    dq = deque()
    for i in range(len(nums)):
        # WRONG: Should remove outdated elements BEFORE processing current
        while dq and nums[dq[-1]] < nums[i]:
            dq.pop()
        while dq and dq[0] < i - k + 1:  # Too late!
            dq.popleft()
```

**Fix**: Remove outdated elements from front before processing current element

### Mistake 7: Using Wrong Comparison Operator
```python
# WRONG: Using <= when you need <
def wrong_comparison(nums):
    stack = []
    result = [-1] * len(nums)
    for i in range(len(nums)):
        # If you want STRICTLY greater, use <, not <=
        while stack and nums[stack[-1]] <= nums[i]:  # Depends on problem!
            result[stack.pop()] = nums[i]
```

**Fix**: Read problem carefully - does it say "greater" or "greater or equal"?

### Debugging Checklist
When your monotonic stack solution doesn't work:

1. ✅ Am I using the right type of stack (increasing vs decreasing)?
2. ✅ Am I storing indices or values (which do I actually need)?
3. ✅ Did I initialize my result array?
4. ✅ Am I using the correct comparison operator (< vs <=)?
5. ✅ For sliding window: Am I removing outdated elements first?
6. ✅ For sliding window: Is my window boundary calculation correct?
7. ✅ Did I test edge cases (empty, single element, all same)?

---

## Summary

**Monotonic Stack/Queue is your go-to pattern for:**
- Finding next/previous greater/smaller elements in O(n) time
- Maintaining sliding window min/max efficiently
- Solving histogram and area-related problems

**Key Takeaway**: When you see nested loops comparing array elements, think monotonic stack. Trade O(n) space for O(n²) → O(n) time improvement.

**Master these problems**: Daily Temperatures (739), Sliding Window Maximum (239), Largest Rectangle in Histogram (84)

Happy coding! 🚀
