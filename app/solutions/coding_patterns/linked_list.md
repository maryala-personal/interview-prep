# Linked List Pattern Guide

## What is a Linked List?

### Explain Like I'm 5
Imagine a chain of boxes where each box contains a treasure and a note telling you where the next box is. You can't jump to any box you want - you have to start at the first box and follow the notes to get to the next one. If you want to find the 5th box, you have to open boxes 1, 2, 3, and 4 first!

Unlike a row of numbered lockers where you can go directly to locker #5, with our treasure boxes, you must follow the chain.

### Technical Definition
A linked list is a linear data structure where elements (nodes) are stored in non-contiguous memory locations. Each node contains:
- **Data**: The actual value stored
- **Next pointer**: A reference to the next node in the sequence

Unlike arrays which store elements in contiguous memory with direct index access, linked lists require traversal from the head (first node) to access elements.

**Types of Linked Lists:**
- **Singly Linked List**: Each node points to the next node
- **Doubly Linked List**: Each node points to both next and previous nodes
- **Circular Linked List**: The last node points back to the first node

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
```

## Real-World Analogy

### Treasure Hunt with Clues
You're on a treasure hunt where:
- Each location has a clue pointing to the next location
- You must visit locations in order - no skipping!
- To get to the 4th location, you must visit locations 1, 2, and 3
- If you lose a clue (pointer), you can't reach the rest of the hunt
- You can add new locations by updating clues
- You can remove locations by changing which clue points where

### Train Cars
A train is like a linked list:
- Each car (node) is connected to the next car (next pointer)
- The engine is the head of the list
- You can add cars anywhere by disconnecting and reconnecting
- You can't jump from car 1 to car 5 - you must walk through cars 2, 3, and 4
- If a connection breaks, the cars behind are lost

## When to Use

**You should think "Linked List" when you see:**

1. **Problem mentions "linked list" explicitly** - Obviously!
2. **Sequential access patterns** - No random access needed
3. **Frequent insertions/deletions** - Especially in the middle
4. **You need to reverse something** - Reversing linked lists is a classic pattern
5. **Detecting cycles** - Fast/slow pointer technique
6. **Finding middle element** - Fast/slow pointer technique
7. **Merging sorted sequences** - Merge two sorted linked lists
8. **LRU Cache implementation** - Combines linked list + hash map

**Advantages over Arrays:**
- O(1) insertion/deletion when you have the pointer to the location
- Dynamic size - no need to pre-allocate memory
- Efficient memory usage for sparse data

**Disadvantages:**
- O(n) random access - must traverse from head
- Extra memory for storing pointers
- Poor cache locality (nodes scattered in memory)

## The Problem: Classic Examples

### Problem 1: Reverse Linked List (LeetCode 206)

Given the head of a singly linked list, reverse the list and return the reversed list.

```
Input: 1 -> 2 -> 3 -> 4 -> 5 -> NULL
Output: 5 -> 4 -> 3 -> 2 -> 1 -> NULL
```

### Problem 2: Detect Cycle in Linked List (LeetCode 141)

Given head of a linked list, determine if the linked list has a cycle.

```
Input: 3 -> 2 -> 0 -> -4
           ^         |
           |_________|
Output: True (cycle exists)
```

## Brute Force Approach

### Reverse Linked List - Using Array

**Idea**: Convert linked list to array, reverse array, rebuild linked list.

```python
def reverseList_bruteforce(head: ListNode) -> ListNode:
    """
    Brute force: Store values in array, reverse, rebuild list
    Time: O(n) - traverse twice
    Space: O(n) - store all values in array
    """
    if not head:
        return None

    # Step 1: Extract all values into an array
    values = []
    current = head
    while current:
        values.append(current.val)
        current = current.next

    # Step 2: Reverse the array
    values.reverse()

    # Step 3: Build new linked list from reversed array
    dummy = ListNode(0)
    current = dummy
    for val in values:
        current.next = ListNode(val)
        current = current.next

    return dummy.next
```

**Why this is not optimal:**
- Uses O(n) extra space for the array
- Creates entirely new nodes instead of reusing existing ones
- Requires three passes through the data

### Detect Cycle - Using Hash Set

**Idea**: Store visited nodes in a set. If we see a node twice, there's a cycle.

```python
def hasCycle_bruteforce(head: ListNode) -> bool:
    """
    Brute force: Track all visited nodes in a set
    Time: O(n)
    Space: O(n) - store all nodes in set
    """
    if not head:
        return False

    visited = set()
    current = head

    while current:
        # If we've seen this node before, there's a cycle
        if current in visited:
            return True

        # Mark this node as visited
        visited.add(current)
        current = current.next

    # Reached the end (NULL) - no cycle
    return False
```

**Why this is not optimal:**
- Uses O(n) extra space to store node references
- Set operations have overhead
- We can solve this with O(1) space using two pointers

## Optimized Solution

### Reverse Linked List - Iterative (In-place)

**Idea**: Reverse pointers one by one while traversing the list.

```python
def reverseList(head: ListNode) -> ListNode:
    """
    Optimal iterative solution using pointer reversal
    Time: O(n) - single pass through list
    Space: O(1) - only three pointers used

    Key insight: Reverse the 'next' pointer of each node as we traverse
    """
    # prev will eventually become the new head
    prev = None
    current = head

    # Traverse the list and reverse pointers
    while current:
        # CRITICAL: Save the next node before we lose the reference
        next_node = current.next

        # Reverse the pointer: make current point backwards
        current.next = prev

        # Move prev and current one step forward
        prev = current
        current = next_node

    # When loop ends, prev is the new head (last node of original list)
    return prev


"""
Visual walkthrough:
Initial: NULL <- prev   current -> 1 -> 2 -> 3 -> NULL

Step 1:  NULL <- 1   current -> 2 -> 3 -> NULL
              prev

Step 2:  NULL <- 1 <- 2   current -> 3 -> NULL
                   prev

Step 3:  NULL <- 1 <- 2 <- 3   current -> NULL
                        prev

Final: prev points to new head (3)
"""
```

### Reverse Linked List - Recursive

```python
def reverseList_recursive(head: ListNode) -> ListNode:
    """
    Optimal recursive solution
    Time: O(n) - visit each node once
    Space: O(n) - recursive call stack

    The recursive approach reverses from the end backwards
    """
    # Base case: empty list or single node
    if not head or not head.next:
        return head

    # Recursively reverse the rest of the list
    # new_head will be the last node of the original list
    new_head = reverseList_recursive(head.next)

    # Reverse the pointer between current and next node
    # Make the next node point back to current
    head.next.next = head

    # Set current node's next to NULL (it might become the tail)
    head.next = None

    return new_head


"""
Recursive visualization for 1 -> 2 -> 3 -> NULL:

Call stack (going down):
reverseList(1) -> reverseList(2) -> reverseList(3) -> return 3

Unwinding (coming back up):
1. reverseList(3) returns 3 (base case)
2. reverseList(2): 3 -> 2, return 3
3. reverseList(1): 3 -> 2 -> 1, return 3

Result: 3 -> 2 -> 1 -> NULL
"""
```

### Detect Cycle - Fast/Slow Pointer (Floyd's Algorithm)

**Idea**: Use two pointers moving at different speeds. If there's a cycle, they'll meet.

```python
def hasCycle(head: ListNode) -> bool:
    """
    Optimal solution using Floyd's Cycle Detection (Tortoise and Hare)
    Time: O(n) - in worst case, slow traverses entire list
    Space: O(1) - only two pointers

    Key insight: In a cycle, a fast pointer will eventually catch up to a slow pointer
    Think of a circular race track - faster runner laps slower runner
    """
    if not head or not head.next:
        return False

    # Initialize two pointers
    slow = head      # Moves 1 step at a time (tortoise)
    fast = head      # Moves 2 steps at a time (hare)

    # Keep moving until fast reaches the end or they meet
    while fast and fast.next:
        slow = slow.next        # Move 1 step
        fast = fast.next.next   # Move 2 steps

        # If they meet, there's a cycle
        if slow == fast:
            return True

    # Fast reached the end (NULL) - no cycle
    return False


"""
Why this works:

Without cycle:
Fast pointer reaches NULL first
slow: 1 -> 2 -> 3 -> 4
fast: 1 -> 3 -> NULL

With cycle:
Pointers eventually meet inside the cycle
slow: 1 -> 2 -> 3 -> 4 -> 2 -> 3 ...
fast: 1 -> 3 -> 2 -> 4 -> 3 -> 2 ...
They meet at some node!

Mathematical proof:
- Distance between pointers decreases by 1 each step
- When slow enters cycle, fast is already inside
- They MUST meet within cycle length iterations
"""
```

## Time & Space Complexity Analysis

### Reverse Linked List

| Approach | Time Complexity | Space Complexity | Notes |
|----------|----------------|------------------|-------|
| Brute Force (Array) | O(n) | O(n) | Three passes, creates new nodes |
| Iterative (In-place) | O(n) | O(1) | Single pass, reuses nodes |
| Recursive | O(n) | O(n) | Single pass, but call stack |

**Winner**: Iterative approach - O(n) time, O(1) space

### Detect Cycle

| Approach | Time Complexity | Space Complexity | Notes |
|----------|----------------|------------------|-------|
| Hash Set | O(n) | O(n) | Store all visited nodes |
| Fast/Slow Pointer | O(n) | O(1) | Floyd's algorithm |

**Winner**: Fast/Slow Pointer - O(n) time, O(1) space

## Variations & Techniques

### 1. Fast/Slow Pointer (Two-Pointer Technique)

Used for: Finding middle, detecting cycles, finding kth from end

```python
def findMiddle(head: ListNode) -> ListNode:
    """
    Find the middle node of a linked list
    If even number of nodes, return the second middle

    Time: O(n), Space: O(1)
    """
    slow = fast = head

    # When fast reaches end, slow is at middle
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    return slow


def findNthFromEnd(head: ListNode, n: int) -> ListNode:
    """
    Find the nth node from the end of the list

    Technique: Move fast pointer n steps ahead, then move both
    Time: O(n), Space: O(1)
    """
    fast = slow = head

    # Move fast pointer n steps ahead
    for _ in range(n):
        if not fast:
            return None  # List shorter than n
        fast = fast.next

    # Move both pointers until fast reaches end
    while fast:
        slow = slow.next
        fast = fast.next

    return slow
```

### 2. Dummy Head Technique

Used for: Simplifying edge cases, especially when head might change

```python
def removeElements(head: ListNode, val: int) -> ListNode:
    """
    Remove all nodes with given value

    Dummy head avoids special case handling for head removal
    Time: O(n), Space: O(1)
    """
    # Create dummy node pointing to head
    dummy = ListNode(0)
    dummy.next = head

    current = dummy

    # Traverse and remove matching nodes
    while current.next:
        if current.next.val == val:
            # Skip the node with matching value
            current.next = current.next.next
        else:
            current = current.next

    # Return the new head (might have changed if original head was removed)
    return dummy.next
```

### 3. Reversal Technique

Used for: Reverse entire list, reverse in groups, palindrome check

```python
def reverseKGroup(head: ListNode, k: int) -> ListNode:
    """
    Reverse nodes in groups of k
    Example: 1->2->3->4->5, k=2 => 2->1->4->3->5

    Time: O(n), Space: O(1)
    """
    # Count total nodes
    count = 0
    current = head
    while current:
        count += 1
        current = current.next

    dummy = ListNode(0)
    dummy.next = head
    prev_group = dummy

    # Process each group of k nodes
    while count >= k:
        # Reverse k nodes
        current = prev_group.next
        next_node = current.next

        for _ in range(k - 1):
            current.next = next_node.next
            next_node.next = prev_group.next
            prev_group.next = next_node
            next_node = current.next

        prev_group = current
        count -= k

    return dummy.next


def isPalindrome(head: ListNode) -> bool:
    """
    Check if linked list is a palindrome
    Technique: Find middle, reverse second half, compare

    Time: O(n), Space: O(1)
    """
    if not head or not head.next:
        return True

    # Find middle using slow/fast pointers
    slow = fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next

    # Reverse second half
    second_half = reverseList(slow.next)

    # Compare first half with reversed second half
    first = head
    second = second_half
    is_palindrome = True

    while second:  # Second half might be shorter
        if first.val != second.val:
            is_palindrome = False
            break
        first = first.next
        second = second.next

    # Optional: Restore the list
    slow.next = reverseList(second_half)

    return is_palindrome
```

### 4. Multiple Pointers Technique

Used for: Merging lists, partitioning, reordering

```python
def mergeTwoLists(l1: ListNode, l2: ListNode) -> ListNode:
    """
    Merge two sorted linked lists

    Time: O(n + m), Space: O(1)
    """
    dummy = ListNode(0)
    current = dummy

    # Compare and merge
    while l1 and l2:
        if l1.val <= l2.val:
            current.next = l1
            l1 = l1.next
        else:
            current.next = l2
            l2 = l2.next
        current = current.next

    # Attach remaining nodes
    current.next = l1 if l1 else l2

    return dummy.next


def partition(head: ListNode, x: int) -> ListNode:
    """
    Partition list so all nodes < x come before nodes >= x

    Time: O(n), Space: O(1)
    """
    # Two separate lists: less than x, greater or equal to x
    less_dummy = ListNode(0)
    greater_dummy = ListNode(0)
    less = less_dummy
    greater = greater_dummy

    # Partition nodes into two lists
    current = head
    while current:
        if current.val < x:
            less.next = current
            less = less.next
        else:
            greater.next = current
            greater = greater.next
        current = current.next

    # Connect the two lists
    greater.next = None  # Important: terminate the list
    less.next = greater_dummy.next

    return less_dummy.next
```

### 5. Runner Technique (K-width Gap)

Used for: Finding kth from end, removing nth node

```python
def removeNthFromEnd(head: ListNode, n: int) -> ListNode:
    """
    Remove the nth node from the end

    Technique: Maintain n-node gap between two pointers
    Time: O(L), Space: O(1) where L is list length
    """
    dummy = ListNode(0)
    dummy.next = head
    fast = slow = dummy

    # Move fast pointer n+1 steps ahead
    for _ in range(n + 1):
        fast = fast.next

    # Move both until fast reaches end
    while fast:
        slow = slow.next
        fast = fast.next

    # Remove the nth node from end
    slow.next = slow.next.next

    return dummy.next
```

## Pro Tips for Senior Engineers

### 1. Always Draw It Out

Before writing code, draw the linked list transformation on paper/whiteboard:
- Draw initial state
- Draw intermediate states
- Draw final state
- Mark where pointers move

This prevents losing references and clarifies the algorithm.

### 2. Handle Edge Cases First

**Always consider:**
```python
def solution(head: ListNode) -> ListNode:
    # Empty list
    if not head:
        return None

    # Single node
    if not head.next:
        return head

    # Your main logic here
    pass
```

**Common edge cases:**
- Empty list (`head = None`)
- Single node (`head.next = None`)
- Two nodes
- All nodes have same value
- Cycle at first node
- Very long list (performance)

### 3. Use Dummy Nodes for Head Changes

When the head might be removed or changed:
```python
dummy = ListNode(0)
dummy.next = head
# Work with dummy, return dummy.next
```

This eliminates special case handling for head removal.

### 4. Save References Before Modifying

```python
# WRONG - loses reference
current.next = current.next.next

# RIGHT - save reference first
next_node = current.next
current.next = next_node.next
```

### 5. Fast/Slow Pointer Template

```python
def fast_slow_template(head: ListNode):
    slow = fast = head

    # Pattern 1: Find middle (fast goes to end)
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    # Pattern 2: Detect cycle (check if they meet)
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True  # Cycle detected

    return False
```

### 6. Check Loop Conditions Carefully

```python
# For single-step movement
while current:
    current = current.next

# For two-step movement (need both checks!)
while fast and fast.next:
    fast = fast.next.next

# Accessing current.next? Check current first!
while current and current.next:
    # Safe to access current.next here
```

### 7. Visualize with Concrete Example

Test mentally with: `1 -> 2 -> 3 -> NULL`
- Shows normal case
- Small enough to trace
- Not too trivial (more than 2 nodes)

### 8. Time Complexity Rules of Thumb

- Single pass: O(n)
- Nested loops: Usually O(n²), but not always in linked lists
- Fast/slow pointers: Still O(n) - fast does at most 2n steps
- Recursive: O(n) time, O(n) space for call stack

## Problem Recognition Patterns

| Pattern Signal | Technique to Use | Example Problems |
|----------------|------------------|------------------|
| "Reverse" | Pointer reversal | Reverse Linked List, Reverse in Groups |
| "Cycle" / "Loop" | Fast/slow pointers | Detect Cycle, Find Cycle Start |
| "Middle" | Fast/slow pointers | Middle of Linked List, Palindrome Check |
| "Nth from end" | Two pointers with gap | Remove Nth From End |
| "Merge" sorted lists | Two pointers | Merge Two Sorted Lists, Merge K Lists |
| "Partition" / "Separate" | Multiple pointers/lists | Partition List, Odd Even Linked List |
| "Remove" nodes | Dummy head | Remove Elements, Remove Duplicates |
| "Palindrome" | Reverse + compare | Palindrome Linked List |
| "Intersection" | Two pointers | Intersection of Two Linked Lists |
| "Sort" | Merge sort | Sort List |
| "Clone" / "Deep copy" | Hash map | Copy List with Random Pointer |

## Practice Problems

### Beginner Level
1. **Reverse Linked List** (LeetCode 206)
   - Classic reversal problem
   - Master both iterative and recursive solutions

2. **Merge Two Sorted Lists** (LeetCode 21)
   - Two pointer technique
   - Good for understanding pointer manipulation

3. **Remove Duplicates from Sorted List** (LeetCode 83)
   - Simple traversal with deletion
   - Practice pointer updates

### Intermediate Level
4. **Linked List Cycle II** (LeetCode 142)
   - Find where cycle begins
   - Advanced fast/slow pointer technique

5. **Reorder List** (LeetCode 143)
   - Combines: find middle, reverse, merge
   - Tests multiple techniques

6. **Remove Nth Node From End** (LeetCode 19)
   - Two-pointer with gap
   - Dummy head technique

7. **Copy List with Random Pointer** (LeetCode 138)
   - Deep copy with extra pointer
   - Hash map or interweaving technique

### Advanced Level
8. **LRU Cache** (LeetCode 146)
   - Doubly linked list + hash map
   - Most common asked linked list problem
   - Tests design skills

9. **Merge K Sorted Lists** (LeetCode 23)
   - Extension of merge two lists
   - Use heap for optimization

10. **Reverse Nodes in k-Group** (LeetCode 25)
    - Complex reversal logic
    - Edge case handling

## Common Mistakes to Avoid

### 1. Null Pointer Errors

```python
# WRONG - will crash if current is None
def buggy_code(head):
    current = head
    while current.next:  # What if head is None?
        current = current.next

# RIGHT - check for None first
def correct_code(head):
    if not head:
        return None
    current = head
    while current and current.next:
        current = current.next
```

### 2. Losing References

```python
# WRONG - loses reference to rest of list
def delete_node_wrong(node):
    node = node.next  # Just reassigns local variable!

# RIGHT - modify the node's data and pointer
def delete_node_correct(node):
    node.val = node.next.val
    node.next = node.next.next
```

### 3. Not Using Dummy Head When Needed

```python
# WRONG - complex head handling
def remove_elements_wrong(head, val):
    # Special case for head
    while head and head.val == val:
        head = head.next

    if not head:
        return None

    current = head
    while current.next:
        if current.next.val == val:
            current.next = current.next.next
        else:
            current = current.next
    return head

# RIGHT - dummy head simplifies
def remove_elements_correct(head, val):
    dummy = ListNode(0)
    dummy.next = head
    current = dummy

    while current.next:
        if current.next.val == val:
            current.next = current.next.next
        else:
            current = current.next

    return dummy.next
```

### 4. Wrong Loop Condition for Fast Pointer

```python
# WRONG - will crash
def find_middle_wrong(head):
    slow = fast = head
    while fast:  # fast.next might be None!
        slow = slow.next
        fast = fast.next.next  # Crashes here if fast.next is None

# RIGHT - check both fast and fast.next
def find_middle_correct(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow
```

### 5. Not Terminating List Properly

```python
# WRONG - creates unexpected cycle
def split_list_wrong(head, k):
    current = head
    for _ in range(k - 1):
        current = current.next
    second_half = current.next
    # Forgot to set current.next = None!
    return head, second_half

# RIGHT - terminate first half
def split_list_correct(head, k):
    current = head
    for _ in range(k - 1):
        current = current.next
    second_half = current.next
    current.next = None  # Terminate first half
    return head, second_half
```

### 6. Off-by-One Errors in K-Gap Problems

```python
# WRONG - off by one
def remove_nth_wrong(head, n):
    fast = slow = head
    for _ in range(n):  # Should be n+1 for removal
        fast = fast.next
    while fast:
        slow = slow.next
        fast = fast.next
    slow.next = slow.next.next  # Removes wrong node!
    return head

# RIGHT - move fast n+1 steps when using dummy
def remove_nth_correct(head, n):
    dummy = ListNode(0)
    dummy.next = head
    fast = slow = dummy
    for _ in range(n + 1):  # n+1 steps
        fast = fast.next
    while fast:
        slow = slow.next
        fast = fast.next
    slow.next = slow.next.next
    return dummy.next
```

### 7. Modifying List While Traversing

```python
# WRONG - loses track during modification
def reverse_wrong(head):
    current = head
    while current:
        temp = current.next
        current.next = ???  # We lost prev!
        current = temp

# RIGHT - maintain prev pointer
def reverse_correct(head):
    prev = None
    current = head
    while current:
        next_node = current.next
        current.next = prev
        prev = current
        current = next_node
    return prev
```

### 8. Assuming List is Non-Circular

```python
# WRONG - infinite loop if cycle exists
def get_length_wrong(head):
    count = 0
    current = head
    while current:  # Never ends if there's a cycle!
        count += 1
        current = current.next
    return count

# RIGHT - detect cycle first
def get_length_correct(head):
    if has_cycle(head):
        return -1  # or handle appropriately
    count = 0
    current = head
    while current:
        count += 1
        current = current.next
    return count
```

---

## Quick Reference Cheat Sheet

```python
# 1. Basic traversal
current = head
while current:
    # Process current
    current = current.next

# 2. Two-pointer (find middle/cycle)
slow = fast = head
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next

# 3. Dummy head for modifications
dummy = ListNode(0)
dummy.next = head
# ... work with dummy
return dummy.next

# 4. Reversal template
prev = None
current = head
while current:
    next_node = current.next
    current.next = prev
    prev = current
    current = next_node
return prev

# 5. K-gap for nth from end
fast = slow = dummy
for _ in range(n + 1):
    fast = fast.next
while fast:
    slow = slow.next
    fast = fast.next
```

Remember: **Draw it out, handle edge cases, save references!**
