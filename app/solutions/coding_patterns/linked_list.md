# Linked List — Complete Interview Guide

## When to Use This Pattern

### Signals That Point to Linked List Techniques
1. **Sequential access with O(1) insertion/deletion** — you need to add or remove elements from the middle without shifting everything else.
2. **In-place reordering** — the problem asks you to rearrange nodes (reverse, reorder, rotate) without extra space.
3. **Cycle or intersection detection** — you need to detect loops, find meeting points, or determine if two sequences converge.
4. **Merge or split sorted sequences** — combine or partition ordered linked lists efficiently.
5. **Ordered eviction / caching** — maintain an access-ordered collection where the least-recently-used element can be evicted in O(1).
6. **K-way merge** — merge K sorted streams where each stream is a linked list.

### When NOT to Use
- If you need random access by index — use an array.
- If the problem is about subsequences, subsets, or permutations — consider DP or backtracking.
- If elements need to be sorted frequently — a heap or balanced BST is better.

---

## Core Mechanics

### Why Linked Lists Work the Way They Do
A linked list is a chain of nodes where each node holds a value and a pointer to the next node. The key **invariant** is that you can only reach a node by traversing from the head. This constraint makes random access O(n) but gives you O(1) insertion/deletion once you have a reference to the predecessor.

**Singly Linked List**: Each node points to the next. You can only traverse forward.
```
[1] -> [2] -> [3] -> [4] -> None
```

**Doubly Linked List**: Each node points to both next and prev. You can traverse in both directions. Essential for LRU Cache.
```
None <- [1] <-> [2] <-> [3] <-> [4] -> None
```

### Key Techniques

**1. Dummy Node (Sentinel)**
A dummy node before the real head simplifies edge cases. Instead of special-casing "what if the head changes?", you always return `dummy.next`.

```
dummy -> [1] -> [2] -> [3] -> None
          ^head
```

**2. Two Pointers (Slow/Fast)**
Move one pointer 1 step at a time, another 2 steps. When fast reaches the end, slow is at the middle. If there is a cycle, they will meet inside the cycle.

**3. In-Place Reversal**
Use three pointers (prev, curr, next_node) to reverse links one at a time. This is the most fundamental linked list operation.

**4. Recursive Decomposition**
Many linked list problems have elegant recursive solutions where you solve for `head.next` first, then handle `head`.

### Complexity Analysis
| Operation | Singly | Doubly |
|-----------|--------|--------|
| Access by index | O(n) | O(n) |
| Insert at head | O(1) | O(1) |
| Insert at tail (with tail ptr) | O(1) | O(1) |
| Delete given node | O(n)* | O(1) |
| Search | O(n) | O(n) |

*O(1) if you have the predecessor; O(n) to find it in a singly linked list.

---

## The Templates

### Python — Singly Linked List Node
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
```

### Python — In-Place Reversal Template
```python
def reverse_list(head: ListNode) -> ListNode:
    prev = None
    curr = head
    while curr:
        next_node = curr.next   # save next
        curr.next = prev        # reverse link
        prev = curr             # advance prev
        curr = next_node        # advance curr
    return prev                 # prev is new head
```

### Python — Slow/Fast Template
```python
def find_middle(head: ListNode) -> ListNode:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow  # middle node (for even length, second middle)
```

### Python — Dummy Node Template
```python
def merge_two_lists(l1: ListNode, l2: ListNode) -> ListNode:
    dummy = ListNode(0)
    tail = dummy
    while l1 and l2:
        if l1.val <= l2.val:
            tail.next = l1
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next
    tail.next = l1 or l2
    return dummy.next
```

### Go — Singly Linked List Node and Core Templates
```go
type ListNode struct {
    Val  int
    Next *ListNode
}

func reverseList(head *ListNode) *ListNode {
    var prev *ListNode
    curr := head
    for curr != nil {
        next := curr.Next
        curr.Next = prev
        prev = curr
        curr = next
    }
    return prev
}

func findMiddle(head *ListNode) *ListNode {
    slow, fast := head, head
    for fast != nil && fast.Next != nil {
        slow = slow.Next
        fast = fast.Next.Next
    }
    return slow
}

func mergeTwoLists(l1, l2 *ListNode) *ListNode {
    dummy := &ListNode{}
    tail := dummy
    for l1 != nil && l2 != nil {
        if l1.Val <= l2.Val {
            tail.Next = l1
            l1 = l1.Next
        } else {
            tail.Next = l2
            l2 = l2.Next
        }
        tail = tail.Next
    }
    if l1 != nil {
        tail.Next = l1
    } else {
        tail.Next = l2
    }
    return dummy.Next
}
```

---

## Variant Subpatterns

### 1. In-Place Reversal Variants
- **Full reversal**: Reverse the entire list.
- **Partial reversal**: Reverse between positions m and n (LC 92).
- **K-group reversal**: Reverse in groups of k (LC 25).
- **Alternating reversal**: Reverse every other group.

### 2. Floyd's Cycle Detection (Tortoise and Hare)
**Why it works — mathematical proof**:

Suppose the list has a "tail" of length `a` before the cycle starts, and the cycle has length `C`. When slow enters the cycle, fast is already `a` steps into the cycle. The gap between them (from slow's perspective) is `C - (a mod C)`. Each step, fast gains 1 on slow, so they meet after `C - (a mod C)` more steps.

At the meeting point, slow has traveled `a + (C - (a mod C))` steps. To find the cycle start: reset one pointer to head. Move both one step at a time. They meet at the cycle entrance because the distance from head to cycle start equals the distance from meeting point to cycle start (modulo cycle length).

**Formal proof for finding cycle start**: Let the distance from head to cycle start be `a`, distance from cycle start to meeting point be `b`, and the remaining cycle length be `c` (so cycle length = `b + c`). At the meeting point, slow traveled `a + b` steps. Fast traveled `a + b + k(b + c)` for some integer k >= 1. Since fast moves at 2x speed: `2(a + b) = a + b + k(b + c)`, which gives `a + b = k(b + c)`, so `a = k(b + c) - b = (k-1)(b + c) + c`. This means: starting from the meeting point and walking `a` steps lands you at the cycle start (after going around the cycle k-1 times and then walking c more steps to the start). So two pointers — one from head, one from meeting point — both moving one step at a time, will meet at the cycle start after `a` steps.

### 3. Dummy Node Technique
When the head might change (deletion, merge, partition), create a dummy node to avoid special cases:
```python
dummy = ListNode(0)
dummy.next = head
# ... modify list ...
return dummy.next  # actual new head
```

### 4. The "Runner" Technique
Use fast/slow to split the list in half, then process each half differently. Classic use: reorder list (interleave first and reversed second half).

### 5. Doubly Linked List + HashMap (LRU Cache Pattern)
The most important linked list pattern for interviews. A DLL maintains access order; a hashmap provides O(1) lookup. Together they give O(1) get and O(1) put with LRU eviction. This is the foundational "combine two data structures" technique.

---

## Problem Walkthroughs

---

### Problem: Reverse Linked List (LC #206) — Easy
**Companies**: Meta, Google, Amazon, Microsoft, Apple — asked in virtually every company's phone screen.

**Problem**: Given the head of a singly linked list, reverse the list and return the reversed list.

**Brute Force**: Copy values to array, reverse array, create new list.
```python
def reverse_list_brute(head: ListNode) -> ListNode:
    vals = []
    curr = head
    while curr:
        vals.append(curr.val)
        curr = curr.next
    vals.reverse()
    dummy = ListNode(0)
    curr = dummy
    for v in vals:
        curr.next = ListNode(v)
        curr = curr.next
    return dummy.next
```
Time: O(n), Space: O(n). Works but wastes space and creates new nodes.

**Key Insight**: We do not need extra space. At each node, redirect the `next` pointer to point backward. We need three pointers: `prev` (the already-reversed portion), `curr` (current node), and `next_node` (saved so we do not lose the rest of the list).

**Optimal Solution — Iterative**:
```python
def reverse_list(head: ListNode) -> ListNode:
    prev = None
    curr = head
    while curr:
        next_node = curr.next   # 1. save next
        curr.next = prev        # 2. reverse link
        prev = curr             # 3. advance prev
        curr = next_node        # 4. advance curr
    return prev
```
Time: O(n), Space: O(1).

**Optimal Solution — Recursive**:
```python
def reverse_list_recursive(head: ListNode) -> ListNode:
    if not head or not head.next:
        return head
    new_head = reverse_list_recursive(head.next)
    head.next.next = head  # the node after head points back to head
    head.next = None       # head now points to None (end of reversed portion)
    return new_head
```
Time: O(n), Space: O(n) call stack.

**Dry Run** with `1 -> 2 -> 3 -> None`:
```
Step 0: prev=None, curr=1
Step 1: next_node=2, 1->None, prev=1, curr=2
Step 2: next_node=3, 2->1, prev=2, curr=3
Step 3: next_node=None, 3->2, prev=3, curr=None
Return prev=3: 3 -> 2 -> 1 -> None
```

**Edge Cases**: Empty list (return None), single node (return node), two nodes.

**Follow-up Questions**:
- Can you reverse a sublist from position m to n? (LC 92)
- Can you do it recursively? What is the space complexity of the recursive version?
- Reverse in groups of k? (LC 25)

---

### Problem: Linked List Cycle (LC #141) — Easy
**Companies**: Meta, Amazon, Microsoft, Bloomberg.

**Problem**: Given head, determine if the linked list has a cycle.

**Brute Force**: Use a hash set to track visited nodes.
```python
def has_cycle_brute(head: ListNode) -> bool:
    visited = set()
    curr = head
    while curr:
        if id(curr) in visited:
            return True
        visited.add(id(curr))
        curr = curr.next
    return False
```
Time: O(n), Space: O(n).

**Key Insight**: Floyd's Cycle Detection — use two pointers moving at different speeds. If there is a cycle, the fast pointer will eventually lap the slow pointer and they will meet. If there is no cycle, fast reaches the end. Think of two runners on a circular track: the faster one always catches the slower one.

**Optimal Solution**:
```python
def has_cycle(head: ListNode) -> bool:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
```
Time: O(n), Space: O(1).

**Dry Run** with `1 -> 2 -> 3 -> 4 -> 2 (cycle back to node 2)`:
```
Step 0: slow=1, fast=1
Step 1: slow=2, fast=3
Step 2: slow=3, fast=2 (fast went 4->2 via cycle)
Step 3: slow=4, fast=4 => slow == fast, return True
```

**Finding the cycle start (LC #142)**:
After slow and fast meet, reset one pointer to head. Move both one step at a time. Where they meet is the cycle start.
```python
def detect_cycle(head: ListNode) -> ListNode:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            # Found cycle, now find entrance
            slow = head
            while slow != fast:
                slow = slow.next
                fast = fast.next
            return slow
    return None
```

**Why finding the start works**: Let the distance from head to cycle start be `a`, distance from cycle start to meeting point be `b`, and the remaining cycle be `c` (cycle length = `b + c`). At meeting: slow traveled `a + b`, fast traveled `a + b + k(b + c)`. Since fast = 2 * slow: `2(a + b) = a + b + k(b + c)`, giving `a + b = k(b + c)`, so `a = (k-1)(b + c) + c`. Starting from the meeting point (which is `b` into the cycle), walking `a` more steps goes around the cycle `k-1` complete times plus `c` more steps, landing exactly at the cycle start.

**Edge Cases**: Empty list, single node, single node with self-loop, no cycle.

**Follow-up Questions**:
- What is the length of the cycle? (After finding the meeting point, keep one pointer still and advance the other until they meet again; count the steps.)
- Can you find the start of the cycle? Explain the math.
- What if you cannot modify the list and cannot use extra space?

---

### Problem: Merge Two Sorted Lists (LC #21) — Easy
**Companies**: Meta, Amazon, Google, Microsoft, Apple.

**Problem**: Merge two sorted linked lists and return it as a sorted list.

**Brute Force**: Collect all values, sort, create new list.
```python
def merge_brute(l1: ListNode, l2: ListNode) -> ListNode:
    vals = []
    while l1:
        vals.append(l1.val)
        l1 = l1.next
    while l2:
        vals.append(l2.val)
        l2 = l2.next
    vals.sort()
    dummy = ListNode(0)
    curr = dummy
    for v in vals:
        curr.next = ListNode(v)
        curr = curr.next
    return dummy.next
```
Time: O((m+n) log(m+n)), Space: O(m+n).

**Key Insight**: Both lists are already sorted. Use a dummy node and a tail pointer. At each step, compare the heads of both lists and append the smaller one. This is exactly the merge step of merge sort.

**Optimal Solution**:
```python
def merge_two_lists(l1: ListNode, l2: ListNode) -> ListNode:
    dummy = ListNode(0)
    tail = dummy
    while l1 and l2:
        if l1.val <= l2.val:
            tail.next = l1
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next
    tail.next = l1 if l1 else l2
    return dummy.next
```
Time: O(m + n), Space: O(1) — we reuse existing nodes.

**Recursive version**:
```python
def merge_two_lists_recursive(l1: ListNode, l2: ListNode) -> ListNode:
    if not l1:
        return l2
    if not l2:
        return l1
    if l1.val <= l2.val:
        l1.next = merge_two_lists_recursive(l1.next, l2)
        return l1
    else:
        l2.next = merge_two_lists_recursive(l1, l2.next)
        return l2
```

**Dry Run** with `l1: 1->3->5, l2: 2->4->6`:
```
dummy -> ?
Step 1: 1 <= 2, tail.next = 1, l1 = 3. List: dummy -> 1
Step 2: 3 > 2,  tail.next = 2, l2 = 4. List: dummy -> 1 -> 2
Step 3: 3 <= 4, tail.next = 3, l1 = 5. List: dummy -> 1 -> 2 -> 3
Step 4: 5 > 4,  tail.next = 4, l2 = 6. List: dummy -> 1 -> 2 -> 3 -> 4
Step 5: 5 <= 6, tail.next = 5, l1 = None. List: dummy -> 1->2->3->4->5
Append remaining: tail.next = 6. Final: 1->2->3->4->5->6
```

**Edge Cases**: One or both lists empty, lists of different lengths, duplicate values.

**Follow-up Questions**:
- Merge K sorted lists? (LC 23 — see below)
- What if lists have duplicates and you want to deduplicate?
- Can you do it recursively? What is the stack depth?

---

### Problem: Reorder List (LC #143) — Medium
**Companies**: Meta, Amazon, Microsoft, Bloomberg.

**Problem**: Given `L0 -> L1 -> ... -> Ln-1 -> Ln`, reorder to `L0 -> Ln -> L1 -> Ln-1 -> L2 -> Ln-2 -> ...`. Do it in-place.

**Brute Force**: Store nodes in an array, then rewire using two pointers from both ends.
```python
def reorder_list_brute(head: ListNode) -> None:
    if not head:
        return
    nodes = []
    curr = head
    while curr:
        nodes.append(curr)
        curr = curr.next
    left, right = 0, len(nodes) - 1
    while left < right:
        nodes[left].next = nodes[right]
        left += 1
        if left == right:
            break
        nodes[right].next = nodes[left]
        right -= 1
    nodes[left].next = None
```
Time: O(n), Space: O(n).

**Key Insight**: This is a three-step process that avoids extra space:
1. Find the middle using slow/fast pointers.
2. Reverse the second half.
3. Merge the two halves by alternating nodes.

This is the "runner" technique at its best — it composes three fundamental operations.

**Optimal Solution**:
```python
def reorder_list(head: ListNode) -> None:
    if not head or not head.next:
        return

    # Step 1: Find middle (slow stops at the end of first half)
    slow, fast = head, head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next

    # Step 2: Reverse second half
    prev = None
    curr = slow.next
    slow.next = None  # cut the list in two
    while curr:
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node
    # prev is the head of the reversed second half

    # Step 3: Merge/interleave the two halves
    first, second = head, prev
    while second:
        tmp1 = first.next
        tmp2 = second.next
        first.next = second
        second.next = tmp1
        first = tmp1
        second = tmp2
```
Time: O(n), Space: O(1).

**Dry Run** with `1 -> 2 -> 3 -> 4 -> 5`:
```
Step 1 (find middle): slow stops at 3. Cut: first = 1->2->3, second = 4->5
Step 2 (reverse second): 5->4->None
Step 3 (merge):
  first=1, second=5: 1->5->2, first=2, second=4
  first=2, second=4: 2->4->3, first=3, second=None
  second is None, stop.
Result: 1->5->2->4->3->None
```

**Edge Cases**: Single node, two nodes, odd vs even length lists.

**Follow-up Questions**:
- What if you need to return a new list instead of modifying in place?
- How would you generalize this to interleave every k-th node from the end?
- Can you do this with a stack instead of reversing?

---

### Problem: LRU Cache (LC #146) — Medium
**Companies**: Meta (#1 most asked), Amazon, Google, Microsoft, Bloomberg, Apple, Uber.

This is the single most important linked list problem for FAANG interviews. At Meta, it appears in a large fraction of coding rounds. You must be able to implement it from scratch, explain every design decision, and handle follow-ups.

**Problem**: Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.
- `LRUCache(int capacity)` — Initialize the cache with positive size capacity.
- `int get(int key)` — Return the value if key exists, otherwise return -1.
- `void put(int key, int value)` — Update the value if key exists. Otherwise, add the key-value pair. If the number of keys exceeds capacity, evict the least recently used key.

Both operations must be O(1) average time.

**Why O(1) is hard — the design reasoning**:
- A **hashmap** gives O(1) lookup but does not track access order.
- A **queue/deque** tracks insertion order but does not give O(1) arbitrary removal.
- An **array** could track order, but deletion from the middle is O(n).
- We need O(1) lookup AND O(1) arbitrary removal AND O(1) insertion at a specific position. The only data structure that gives O(1) removal when you have a reference to the node is a **doubly linked list**.

**Key Insight**: Combine a **doubly linked list** (for O(1) removal and move-to-front) with a **hashmap** (for O(1) key-to-node lookup). The DLL maintains access order: most recently used at the head, least recently used at the tail. The hashmap maps keys directly to DLL nodes.

**Architecture**:
```
HashMap: key -> DLL Node
DLL:    HEAD <-> [most recent] <-> ... <-> [least recent] <-> TAIL
         ^sentinel                                           ^sentinel
```

Why doubly linked? Because when we access a node, we need to:
1. Remove it from its current position (need prev pointer for O(1) removal).
2. Insert it right after head (O(1)).
With a singly linked list, removal would require finding the predecessor — O(n).

Why sentinel nodes (dummy head and tail)? They eliminate ALL edge cases for empty list, single element, removing from head or tail. Without sentinels, every pointer update needs a conditional check.

**Optimal Solution — Step by Step Build**:
```python
class DLLNode:
    """Doubly linked list node storing key-value pair."""
    def __init__(self, key: int = 0, val: int = 0):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> DLLNode

        # Sentinel nodes — head.next is MRU, tail.prev is LRU
        self.head = DLLNode()
        self.tail = DLLNode()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: DLLNode) -> None:
        """Remove a node from its current position in the DLL.
        O(1) because we have direct access to prev and next."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node: DLLNode) -> None:
        """Insert a node right after head (most recently used position).
        Four pointer updates — draw this out on paper to see why."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _move_to_front(self, node: DLLNode) -> None:
        """Move existing node to the front (mark as most recently used)."""
        self._remove(node)
        self._add_to_front(node)

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._move_to_front(node)  # Mark as recently used
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Update existing entry
            node = self.cache[key]
            node.val = value
            self._move_to_front(node)
        else:
            # Add new entry
            if len(self.cache) >= self.capacity:
                # Evict LRU (node just before tail sentinel)
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]  # WHY we store key in the node!
            new_node = DLLNode(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
```
Time: O(1) for both get and put. Space: O(capacity).

**Critical design detail — why we store `key` in the DLL node**: When evicting the LRU entry, we walk to `tail.prev` to get the node to evict. But we also need to remove its entry from the hashmap, which requires the key. If the key were not stored in the node, we would need to search the hashmap for the matching node — O(n). Storing the key in the node makes eviction O(1).

**Detailed Dry Run** with capacity=2:
```
Initial state:
  cache = {}, DLL: HEAD <-> TAIL

put(1, 1):
  Key 1 not in cache. Cache not full (0 < 2).
  Create Node(key=1, val=1), add to front, add to cache.
  cache = {1: Node(1,1)}
  DLL: HEAD <-> (1,1) <-> TAIL

put(2, 2):
  Key 2 not in cache. Cache not full (1 < 2).
  Create Node(key=2, val=2), add to front, add to cache.
  cache = {1: Node(1,1), 2: Node(2,2)}
  DLL: HEAD <-> (2,2) <-> (1,1) <-> TAIL
                ^MRU       ^LRU

get(1) -> returns 1:
  Key 1 in cache. Move Node(1,1) to front.
  DLL: HEAD <-> (1,1) <-> (2,2) <-> TAIL
                ^MRU       ^LRU

put(3, 3):
  Key 3 not in cache. Cache IS full (2 >= 2).
  Evict LRU: tail.prev = Node(2,2). Remove from DLL and delete cache[2].
  Create Node(key=3, val=3), add to front.
  cache = {1: Node(1,1), 3: Node(3,3)}
  DLL: HEAD <-> (3,3) <-> (1,1) <-> TAIL

get(2) -> returns -1:
  Key 2 not in cache (it was evicted).

put(4, 4):
  Key 4 not in cache. Cache IS full (2 >= 2).
  Evict LRU: tail.prev = Node(1,1). Remove from DLL and delete cache[1].
  Create Node(key=4, val=4), add to front.
  cache = {3: Node(3,3), 4: Node(4,4)}
  DLL: HEAD <-> (4,4) <-> (3,3) <-> TAIL
```

**Alternative — Python OrderedDict** (know this but do NOT use in interview):
```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # Remove oldest (front)
```

**WARNING**: Most interviewers at Meta/Google will NOT accept the OrderedDict solution. They want you to implement the DLL + hashmap from scratch. Mention OrderedDict as "in production I would use this", then implement the full version.

**Edge Cases**: Capacity of 1, updating an existing key's value, getting a key that was evicted, putting the same key multiple times with different values.

**Follow-up Questions**:
- **Thread safety**: Wrap get/put with a mutex. For higher throughput, use a read-write lock (reads can be concurrent if we separate the "move to front" concern) or sharded LRU caches.
- **What if capacity can change dynamically?** Evict entries from the tail until size <= new capacity.
- **Implement LFU Cache** (LC 460). Frequency-based eviction — much harder, requires frequency buckets.
- **How does Redis implement LRU?** Redis uses approximated LRU with random sampling (pick N random keys, evict the one with the oldest access time). This is O(1) without maintaining a DLL.
- **What is the time complexity of each operation? Prove it.** Each operation does a constant number of hashmap lookups (O(1) average) and DLL pointer manipulations (O(1)), so everything is O(1) amortized.
- **What about cache stampede?** When a popular key is evicted and many requests try to recompute it simultaneously. Solutions: locking per key, "stale-while-revalidate".

---

### Problem: Copy List with Random Pointer (LC #138) — Medium
**Companies**: Meta, Amazon, Microsoft, Bloomberg.

**Problem**: A linked list has nodes with a `next` pointer and a `random` pointer that can point to any node or null. Make a deep copy.

```python
class Node:
    def __init__(self, val=0, next=None, random=None):
        self.val = val
        self.next = next
        self.random = random
```

**Brute Force / Hashmap Approach** (this is actually clean and preferred in interviews):
```python
def copy_random_list_hashmap(head: 'Node') -> 'Node':
    if not head:
        return None
    old_to_new = {}
    # First pass: create all new nodes
    curr = head
    while curr:
        old_to_new[curr] = Node(curr.val)
        curr = curr.next
    # Second pass: set next and random pointers
    curr = head
    while curr:
        old_to_new[curr].next = old_to_new.get(curr.next)
        old_to_new[curr].random = old_to_new.get(curr.random)
        curr = curr.next
    return old_to_new[head]
```
Time: O(n), Space: O(n) for the hashmap.

**Key Insight for O(1) space**: Interleave copied nodes with originals. For each original node A, insert A' (the copy) right after A. Now `A.random.next` gives us A's copy's random target. After setting random pointers, separate the lists.

**Optimal Solution — O(1) Space (Interleaving)**:
```python
def copy_random_list(head: 'Node') -> 'Node':
    if not head:
        return None

    # Step 1: Interleave copies after originals
    # A -> B -> C  becomes  A -> A' -> B -> B' -> C -> C'
    curr = head
    while curr:
        copy = Node(curr.val)
        copy.next = curr.next
        curr.next = copy
        curr = copy.next

    # Step 2: Set random pointers for copies
    curr = head
    while curr:
        if curr.random:
            curr.next.random = curr.random.next
        curr = curr.next.next

    # Step 3: Separate the two interleaved lists
    new_head = head.next
    curr = head
    while curr:
        copy = curr.next
        curr.next = copy.next
        copy.next = copy.next.next if copy.next else None
        curr = curr.next

    return new_head
```
Time: O(n), Space: O(1) (not counting the output list).

**Dry Run** with `A(random->C) -> B(random->A) -> C(random->B)`:
```
Step 1 (interleave): A -> A' -> B -> B' -> C -> C' -> None
Step 2 (random pointers):
  A.random = C, so A'.random = C.next = C'
  B.random = A, so B'.random = A.next = A'
  C.random = B, so C'.random = B.next = B'
Step 3 (separate):
  Original: A -> B -> C -> None
  Copy:     A'(random=C') -> B'(random=A') -> C'(random=B') -> None
```

**Edge Cases**: Empty list, single node with random = None, single node with random = self, all random pointers are null.

**Follow-up Questions**:
- What if the structure is a general graph? (BFS/DFS clone with hashmap.)
- Can you do this recursively? (Yes, with a hashmap to track already-cloned nodes.)
- How would you handle this in a language without garbage collection? (Careful memory management — who owns the old_to_new map?)

---

### Problem: Reverse Nodes in k-Group (LC #25) — Hard
**Companies**: Meta, Amazon, Google, Microsoft.

**Problem**: Given a linked list, reverse the nodes k at a time. If the remaining nodes are fewer than k, leave them as-is.

**Brute Force**: Store nodes in an array, reverse in chunks, rewire.
```python
def reverse_k_group_brute(head: ListNode, k: int) -> ListNode:
    if not head or k == 1:
        return head
    nodes = []
    curr = head
    while curr:
        nodes.append(curr)
        curr = curr.next
    for i in range(0, len(nodes) - k + 1, k):
        left, right = i, i + k - 1
        while left < right:
            nodes[left], nodes[right] = nodes[right], nodes[left]
            left += 1
            right -= 1
    for i in range(len(nodes) - 1):
        nodes[i].next = nodes[i + 1]
    nodes[-1].next = None
    return nodes[0]
```
Time: O(n), Space: O(n).

**Key Insight**: Process k nodes at a time. For each group: (1) check if k nodes remain, (2) reverse them using the standard reversal technique, (3) connect the reversed group to the previous group's tail. A dummy node handles the first group cleanly.

**Optimal Solution**:
```python
def reverse_k_group(head: ListNode, k: int) -> ListNode:
    # First count total nodes
    count = 0
    curr = head
    while curr:
        count += 1
        curr = curr.next

    dummy = ListNode(0)
    dummy.next = head
    prev_group_end = dummy

    while count >= k:
        # Reverse k nodes starting from prev_group_end.next
        prev = None
        curr = prev_group_end.next
        group_start = curr  # this node will become the tail after reversal
        for _ in range(k):
            next_node = curr.next
            curr.next = prev
            prev = curr
            curr = next_node
        # Now: prev = new head of reversed group
        #      curr = start of next group (or None)
        #      group_start = tail of reversed group
        prev_group_end.next = prev       # connect previous part to new head
        group_start.next = curr          # connect tail to next group
        prev_group_end = group_start     # advance for next iteration
        count -= k

    return dummy.next
```
Time: O(n), Space: O(1).

**Recursive Solution** (elegant but O(n/k) stack space):
```python
def reverse_k_group_recursive(head: ListNode, k: int) -> ListNode:
    # Check if we have k nodes left
    curr = head
    for _ in range(k):
        if not curr:
            return head  # fewer than k nodes, return as-is
        curr = curr.next

    # Reverse first k nodes
    prev = None
    curr = head
    for _ in range(k):
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node

    # head is now the tail of the reversed group
    # Recursively process remaining and connect
    head.next = reverse_k_group_recursive(curr, k)
    return prev  # prev is the new head of this group
```

**Dry Run** with `1->2->3->4->5, k=3`:
```
count = 5, dummy->1->2->3->4->5

Group 1 (count=5 >= 3):
  Reverse 1->2->3:
    prev=None, curr=1: next=2, 1->None, prev=1, curr=2
    prev=1, curr=2: next=3, 2->1, prev=2, curr=3
    prev=2, curr=3: next=4, 3->2, prev=3, curr=4
  Connect: dummy->3->2->1->4->5
  prev_group_end = node(1), count = 2

Group 2 (count=2 < 3): stop.

Result: 3->2->1->4->5
```

**Edge Cases**: k=1 (no change), k equals list length (full reversal), single node, k > list length (no change).

**Follow-up Questions**:
- What if you should also reverse the last partial group?
- Can you solve it iteratively with O(1) space? (Yes, as shown above.)
- What about alternating: reverse k, skip k, reverse k, skip k?

---

### Problem: Merge K Sorted Lists (LC #23) — Hard
**Companies**: Meta, Amazon, Google, Microsoft, Uber.

**Problem**: Given an array of k linked lists, each sorted in ascending order, merge all into one sorted list.

**Brute Force**: Collect all values, sort, build new list.
```python
def merge_k_lists_brute(lists):
    vals = []
    for l in lists:
        curr = l
        while curr:
            vals.append(curr.val)
            curr = curr.next
    vals.sort()
    dummy = ListNode(0)
    curr = dummy
    for v in vals:
        curr.next = ListNode(v)
        curr = curr.next
    return dummy.next
```
Time: O(N log N) where N = total nodes. Space: O(N).

**Approach 2 — Min Heap**: Maintain a min-heap of size k with the current head of each list. Extract min, append to result, push that list's next node.

```python
import heapq

def merge_k_lists_heap(lists):
    heap = []
    for i, l in enumerate(lists):
        if l:
            heapq.heappush(heap, (l.val, i, l))

    dummy = ListNode(0)
    tail = dummy
    while heap:
        val, i, node = heapq.heappop(heap)
        tail.next = node
        tail = tail.next
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next
```
Time: O(N log k) — each of the N nodes is pushed/popped once, each operation is O(log k).
Space: O(k) for the heap.

Note: The `i` (index) tiebreaker is critical — without it, Python will try to compare ListNode objects when values are equal, causing an error.

**Key Insight for Divide and Conquer**: Pair up lists and merge each pair using the merge-two-sorted-lists algorithm. Repeat until one list remains. This is the merge phase of merge sort applied to the list-of-lists level.

**Optimal Solution — Divide and Conquer**:
```python
def merge_k_lists(lists):
    if not lists:
        return None

    def merge_two(l1, l2):
        dummy = ListNode(0)
        tail = dummy
        while l1 and l2:
            if l1.val <= l2.val:
                tail.next = l1
                l1 = l1.next
            else:
                tail.next = l2
                l2 = l2.next
            tail = tail.next
        tail.next = l1 or l2
        return dummy.next

    while len(lists) > 1:
        merged = []
        for i in range(0, len(lists), 2):
            l1 = lists[i]
            l2 = lists[i + 1] if i + 1 < len(lists) else None
            merged.append(merge_two(l1, l2))
        lists = merged

    return lists[0]
```
Time: O(N log k) — log k rounds of merging, each touching all N nodes.
Space: O(1) extra beyond the result (we reuse existing nodes).

**Dry Run** with `lists = [[1,4,5], [1,3,4], [2,6]]`:
```
Round 1:
  Merge [1,4,5] + [1,3,4] = [1,1,3,4,4,5]
  Carry [2,6] (odd one out)
  lists = [[1,1,3,4,4,5], [2,6]]

Round 2:
  Merge [1,1,3,4,4,5] + [2,6] = [1,1,2,3,4,4,5,6]
  lists = [[1,1,2,3,4,4,5,6]]

Result: 1->1->2->3->4->4->5->6
```

**Heap vs Divide-and-Conquer Trade-offs**:
| Aspect | Heap | D&C |
|--------|------|-----|
| Time | O(N log k) | O(N log k) |
| Space | O(k) | O(1) extra |
| Streaming | Yes — handles new lists arriving | No — needs all lists upfront |
| Implementation | Need custom comparison | Simpler if you have merge-two |

**Edge Cases**: Empty lists array, lists containing empty lists, single list, all lists are single nodes, k = 0.

**Follow-up Questions**:
- When would you prefer heap over divide-and-conquer? (Streaming scenario — lists arrive over time.)
- What if lists are not sorted? (Sort each first: O(N log(N/k)) + O(N log k) = O(N log N).)
- How does this relate to external sorting of large files that do not fit in memory? (External merge sort uses the same k-way merge pattern with a heap.)
- What is the optimal k for external sorting? (Depends on disk I/O and memory — typically k = memory / block_size.)

---

## Common Mistakes & Interview Tips

### Mistakes to Avoid
1. **Forgetting to save `next` before overwriting** — In reversal, always save `curr.next` before setting `curr.next = prev`.
2. **Not handling None/null** — Always check `node is not None` before accessing `node.next` or `node.val`.
3. **Losing the head** — After modifying a list, ensure you still reference the correct head. Dummy nodes prevent this.
4. **Creating accidental cycles** — When rewiring `next` pointers, ensure the list terminates with `None`. Draw the state after each step.
5. **Off-by-one in slow/fast** — For finding the middle:
   - `while fast and fast.next` → slow lands on second middle (even length).
   - `while fast.next and fast.next.next` → slow lands on first middle (even length).
   Pick the right one for your problem.
6. **Not storing key in LRU node** — Without the key in the DLL node, you cannot delete from the hashmap during eviction.
7. **Forgetting sentinel-to-sentinel connection** — In LRU Cache, head.next must start as tail, and tail.prev must start as head.

### Interview Tips
1. **Draw pictures** — Linked list problems are visual. Draw boxes and arrows on the whiteboard at every step.
2. **Use dummy nodes liberally** — They eliminate 90% of edge cases for free.
3. **State your approach before coding** — "I will use the fast/slow pointer technique to find the middle, then reverse the second half, then interleave."
4. **Handle edge cases explicitly** — Empty list, single node, two nodes. Mention these even if your code already handles them.
5. **Know the time and space complexity** — Be prepared to explain why Floyd's is O(n), not O(n^2).
6. **For LRU Cache, practice drawing the DLL state** — Interviewers love to see you trace through put/get operations step by step on the whiteboard.
7. **Recursive vs iterative** — Know both for every problem. Recursive is often cleaner but uses O(n) stack space. Iterative is O(1) space. Be ready to discuss the trade-off.
8. **Practice the 4-line reversal until it is muscle memory**: save next, reverse link, advance prev, advance curr.

---

## Pattern Connections

| Pattern | Connection to Linked Lists |
|---------|---------------------------|
| **Two Pointers** | Slow/fast is a two-pointer technique. Same mental model as array two pointers. |
| **Merge Sort** | Merge two sorted lists is the merge step. Linked list merge sort is a classic D&C problem. |
| **Design Patterns** | LRU/LFU Cache uses DLL + HashMap. Many OOD problems use linked lists internally. |
| **Stack/Queue** | Both can be implemented with linked lists. Recursion on linked lists is essentially using the call stack. |
| **Divide and Conquer** | Merge K sorted lists, sort list (merge sort on linked list). |
| **Heap** | Alternative for merge K sorted lists. Min-heap over list heads for streaming merge. |
| **Hash Map** | Used alongside linked lists in LRU Cache, Copy Random Pointer, and cycle detection (brute). |
| **Recursion** | Many linked list problems have elegant recursive solutions (reverse, merge, k-group). |

### Progression Path
```
Reverse List (206) -> Reverse Between (92) -> Reverse K-Group (25)
Merge Two (21) -> Merge K (23) -> Sort List (148)
Cycle Detection (141) -> Cycle Start (142) -> Happy Number (202)
Reorder List (143) = Find Middle + Reverse + Merge
LRU Cache (146) -> LFU Cache (460) -> All O(1) DS (432)
Copy Random Pointer (138) -> Clone Graph (133)
```
