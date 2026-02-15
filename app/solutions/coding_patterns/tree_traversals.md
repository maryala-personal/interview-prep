# Tree Traversals — Complete Interview Guide

## When to Use This Pattern

### Signals That Point to Tree Techniques
1. **Hierarchical data** — the input is a tree or can be modeled as one (DOM, file system, org chart).
2. **"For every node, compute something based on its children or subtree"** — post-order processing pattern.
3. **Serialization / deserialization** — converting a tree to a string and back.
4. **Path problems** — find paths with specific sums, longest paths, or paths between specific nodes.
5. **BST property** — the problem involves sorted order in a tree (validate BST, find kth smallest, range queries).
6. **Level-by-level processing** — BFS over tree levels (right side view, zigzag traversal).

### When NOT to Use
- If the structure is a general graph with cycles — use graph algorithms (BFS/DFS with visited set).
- If you need the shortest path in a weighted graph — use Dijkstra, not tree DFS.
- If the data is flat and unstructured — trees add unnecessary complexity.

---

## Core Mechanics

### Tree Fundamentals
A binary tree is a recursive structure: each node has at most two children. The key **invariant** is that there are no cycles, so every recursive call processes a strictly smaller subproblem.

```
        1
       / \
      2   3
     / \   \
    4   5   6
```

**Types of binary trees**:
- **Full**: Every node has 0 or 2 children.
- **Complete**: All levels filled except possibly the last, which is filled left to right.
- **Perfect**: All internal nodes have 2 children, all leaves at same level.
- **BST**: For every node, all values in the left subtree < node < all values in right subtree.
- **Balanced**: Height is O(log n). Examples: AVL, Red-Black trees.

### Traversal Orders
The four fundamental traversals differ in when you "visit" the current node relative to its children:

```
        1
       / \
      2   3
     / \
    4   5
```

| Traversal | Order | Result | Use Case |
|-----------|-------|--------|----------|
| Pre-order | root, left, right | 1,2,4,5,3 | Serialize/copy tree, prefix expression |
| In-order | left, root, right | 4,2,5,1,3 | BST gives sorted order |
| Post-order | left, right, root | 4,5,2,3,1 | Delete tree, compute subtree properties |
| Level-order | level by level | 1,2,3,4,5 | BFS, right side view, level averages |

### Why Post-Order Matters for "Gather Info from Children"
Many tree problems follow this pattern: to compute something for the current node, you first need results from both children. This is naturally post-order:
1. Recurse left — get left result.
2. Recurse right — get right result.
3. Combine left and right results to compute current node's answer.

Examples: tree height, diameter, max path sum, balanced check, subtree sum.

### Complexity
- **Time**: O(n) for any complete traversal — we visit every node exactly once.
- **Space**: O(h) for recursive traversal (call stack) where h is height. O(h) = O(log n) balanced, O(n) skewed.
- **Morris traversal**: O(n) time, O(1) space — uses threaded binary trees.

---

## The Templates

### Python — Recursive Traversals
```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def preorder(root: TreeNode) -> list:
    if not root:
        return []
    return [root.val] + preorder(root.left) + preorder(root.right)

def inorder(root: TreeNode) -> list:
    if not root:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)

def postorder(root: TreeNode) -> list:
    if not root:
        return []
    return postorder(root.left) + postorder(root.right) + [root.val]
```

### Python — Iterative Traversals
```python
def preorder_iterative(root: TreeNode) -> list:
    if not root:
        return []
    result, stack = [], [root]
    while stack:
        node = stack.pop()
        result.append(node.val)
        if node.right:  # push right first so left is processed first
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
    return result

def inorder_iterative(root: TreeNode) -> list:
    result, stack = [], []
    curr = root
    while curr or stack:
        while curr:            # go as far left as possible
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()     # backtrack
        result.append(curr.val)
        curr = curr.right      # move to right subtree
    return result

def postorder_iterative(root: TreeNode) -> list:
    if not root:
        return []
    result, stack = [], [root]
    while stack:
        node = stack.pop()
        result.append(node.val)
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)
    return result[::-1]  # reverse of modified pre-order (root, right, left)
```

### Python — Level-Order (BFS)
```python
from collections import deque

def level_order(root: TreeNode) -> list:
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result
```

### Python — Morris In-Order Traversal (O(1) Space)
```python
def morris_inorder(root: TreeNode) -> list:
    """O(n) time, O(1) space in-order traversal using threaded binary tree."""
    result = []
    curr = root
    while curr:
        if not curr.left:
            # No left subtree — visit current, move right
            result.append(curr.val)
            curr = curr.right
        else:
            # Find in-order predecessor (rightmost in left subtree)
            pred = curr.left
            while pred.right and pred.right != curr:
                pred = pred.right
            if not pred.right:
                # First visit: create thread back to curr
                pred.right = curr
                curr = curr.left
            else:
                # Second visit: remove thread, visit curr
                pred.right = None
                result.append(curr.val)
                curr = curr.right
    return result
```

**How Morris Traversal Works**: Instead of using a stack, we temporarily modify the tree by creating "threads" — right pointers from the in-order predecessor back to the current node. This lets us return to the current node after processing its left subtree. We visit each edge at most twice (once to create the thread, once to remove it), so it is O(n) time. After traversal, the tree is restored to its original shape.

### Python — Post-Order DFS Template (Gather from Children)
```python
def solve(root: TreeNode) -> int:
    """Template for problems that gather info from children."""
    def dfs(node):
        if not node:
            return BASE_CASE  # e.g., 0 for height, True for valid

        left_result = dfs(node.left)
        right_result = dfs(node.right)

        # Process current node using children's results
        current_result = COMBINE(left_result, right_result, node.val)

        # Optionally update a global answer
        # nonlocal ans
        # ans = max(ans, SOME_FUNCTION(left_result, right_result))

        return current_result

    # ans = INITIAL_VALUE
    dfs(root)
    # return ans
```

### Go — Core Templates
```go
type TreeNode struct {
    Val   int
    Left  *TreeNode
    Right *TreeNode
}

func inorderIterative(root *TreeNode) []int {
    var result []int
    var stack []*TreeNode
    curr := root
    for curr != nil || len(stack) > 0 {
        for curr != nil {
            stack = append(stack, curr)
            curr = curr.Left
        }
        curr = stack[len(stack)-1]
        stack = stack[:len(stack)-1]
        result = append(result, curr.Val)
        curr = curr.Right
    }
    return result
}

func levelOrder(root *TreeNode) [][]int {
    if root == nil {
        return nil
    }
    var result [][]int
    queue := []*TreeNode{root}
    for len(queue) > 0 {
        size := len(queue)
        var level []int
        for i := 0; i < size; i++ {
            node := queue[0]
            queue = queue[1:]
            level = append(level, node.Val)
            if node.Left != nil {
                queue = append(queue, node.Left)
            }
            if node.Right != nil {
                queue = append(queue, node.Right)
            }
        }
        result = append(result, level)
    }
    return result
}
```

---

## Variant Subpatterns

### 1. Top-Down DFS (Pre-Order Style)
Pass information DOWN from parent to children. The parent tells each child what it needs to know.
- Example: "Is this BST valid?" — pass the valid range [min, max] down.
- Example: root-to-leaf path sum — pass the running sum down.

### 2. Bottom-Up DFS (Post-Order Style)
Gather information UP from children to parent. Each node computes its answer from its children's answers.
- Example: Tree height — `1 + max(left_height, right_height)`.
- Example: Diameter — max path through any node, where path through node = left_height + right_height.
- Example: Max path sum — can include or exclude the node as a turning point.

### 3. BST Exploitation
In a BST, in-order traversal gives sorted values. This unlocks:
- **Validation**: ensure in-order is strictly increasing.
- **Kth smallest**: in-order traversal, return the kth element.
- **Range queries**: prune branches that fall outside the range.
- **Successor/predecessor**: follow right then go all the way left, or vice versa.

### 4. Level-Order Variants
- **Right side view**: take the last element of each level.
- **Zigzag**: alternate left-to-right and right-to-left per level.
- **Level averages/max**: aggregate each level.
- **Connect next pointers**: link nodes at the same level.

### 5. Tree Construction
Build a tree from traversal arrays:
- **Preorder + Inorder**: preorder's first element is root; find it in inorder to split left/right subtrees.
- **Postorder + Inorder**: postorder's last element is root.
- **Preorder alone (BST)**: use the BST property to determine subtree boundaries.

---

## Problem Walkthroughs

---

### Problem: Invert Binary Tree (LC #226) — Easy
**Companies**: Google, Meta, Amazon — the famous "Homebrew guy" problem.

**Problem**: Invert a binary tree (mirror it: swap left and right children at every node).

```
Input:       Output:
    4            4
   / \          / \
  2   7        7   2
 / \ / \      / \ / \
1  3 6  9    9  6 3  1
```

**Brute Force**: There is no real brute force — this IS the simplest approach. Every solution visits all nodes.

**Key Insight**: At every node, swap its left and right children, then recursively invert both subtrees. This is a pre-order traversal where the "visit" action is swapping children.

**Optimal Solution — Recursive**:
```python
def invert_tree(root: TreeNode) -> TreeNode:
    if not root:
        return None
    # Swap children
    root.left, root.right = root.right, root.left
    # Recursively invert subtrees
    invert_tree(root.left)
    invert_tree(root.right)
    return root
```
Time: O(n), Space: O(h) for recursion stack.

**Optimal Solution — Iterative (BFS)**:
```python
from collections import deque

def invert_tree_iterative(root: TreeNode) -> TreeNode:
    if not root:
        return None
    queue = deque([root])
    while queue:
        node = queue.popleft()
        node.left, node.right = node.right, node.left
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return root
```

**Dry Run** with the example tree:
```
Start: root = 4
Swap children of 4: left=7, right=2
Recurse on 7: swap children -> left=9, right=6
Recurse on 9: leaf, no children to swap
Recurse on 6: leaf, no children to swap
Recurse on 2: swap children -> left=3, right=1
Recurse on 3: leaf
Recurse on 1: leaf
Result: fully mirrored tree
```

**Edge Cases**: Empty tree, single node, tree with only left children, tree with only right children.

**Follow-up Questions**:
- Can you do it iteratively? (BFS or DFS with stack.)
- What if the tree is very deep — which approach avoids stack overflow? (Iterative BFS.)
- Is the tree modified in-place? (Yes, we swap pointers.)

---

### Problem: Diameter of Binary Tree (LC #543) — Easy
**Companies**: Meta, Google, Amazon, Microsoft.

**Problem**: The diameter of a binary tree is the length of the longest path between any two nodes (measured in edges, not nodes). The path may or may not pass through the root.

```
        1
       / \
      2   3
     / \
    4   5
Diameter = 3 (path: 4 -> 2 -> 1 -> 3, or 5 -> 2 -> 1 -> 3)
```

**Brute Force**: For every node, compute the height of its left and right subtrees, sum them to get the path through that node. Take the maximum.
```python
def diameter_brute(root: TreeNode) -> int:
    def height(node):
        if not node:
            return 0
        return 1 + max(height(node.left), height(node.right))

    def diameter_at(node):
        if not node:
            return 0
        return height(node.left) + height(node.right)

    if not root:
        return 0
    return max(diameter_at(root),
               diameter_brute(root.left),
               diameter_brute(root.right))
```
Time: O(n^2) — for each node, we recompute heights.

**Key Insight**: The diameter through any node equals `left_height + right_height`. If we compute height bottom-up (post-order), we can simultaneously track the maximum diameter seen so far. This avoids recomputing heights.

**Optimal Solution**:
```python
def diameter_of_binary_tree(root: TreeNode) -> int:
    diameter = 0

    def height(node):
        nonlocal diameter
        if not node:
            return 0
        left_h = height(node.left)
        right_h = height(node.right)
        # The path through this node has length left_h + right_h
        diameter = max(diameter, left_h + right_h)
        # Return height of this subtree
        return 1 + max(left_h, right_h)

    height(root)
    return diameter
```
Time: O(n), Space: O(h).

**Dry Run** with the example:
```
height(4): left=0, right=0, diameter=max(0,0)=0, return 1
height(5): left=0, right=0, diameter=max(0,0)=0, return 1
height(2): left=1, right=1, diameter=max(0,1+1)=2, return 2
height(3): left=0, right=0, diameter=max(2,0)=2, return 1
height(1): left=2, right=1, diameter=max(2,2+1)=3, return 3
Answer: diameter = 3
```

**Edge Cases**: Single node (diameter = 0), linear tree (all left or all right), empty tree.

**Follow-up Questions**:
- What if we want the actual path nodes, not just the length?
- What if diameter is measured in nodes instead of edges?
- How is this different from the maximum path sum problem? (Same structure, different "cost" function.)

---

### Problem: Lowest Common Ancestor of a Binary Tree (LC #236) — Medium
**Companies**: Meta, Google, Amazon, Microsoft, Apple.

**Problem**: Given a binary tree and two nodes p and q, find their lowest common ancestor (LCA). The LCA is the deepest node that has both p and q as descendants (a node can be a descendant of itself).

**Brute Force**: Find the path from root to p and root to q. Compare the paths to find the last common node.
```python
def lca_brute(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    def find_path(root, target, path):
        if not root:
            return False
        path.append(root)
        if root == target:
            return True
        if find_path(root.left, target, path) or find_path(root.right, target, path):
            return True
        path.pop()
        return False

    path_p, path_q = [], []
    find_path(root, p, path_p)
    find_path(root, q, path_q)

    lca = None
    for a, b in zip(path_p, path_q):
        if a == b:
            lca = a
        else:
            break
    return lca
```
Time: O(n), Space: O(n) for the paths.

**Key Insight**: Use post-order DFS. At each node, check: does my left subtree contain p or q? Does my right subtree? If both sides return non-null, the current node is the LCA. If only one side returns non-null, propagate that result up.

**Optimal Solution**:
```python
def lowest_common_ancestor(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    if not root or root == p or root == q:
        return root

    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)

    if left and right:
        return root     # p and q are in different subtrees -> root is LCA
    return left or right  # both are in the same subtree
```
Time: O(n), Space: O(h).

**Why this works**: The recursion explores the entire tree. The base case returns the node if it matches p or q. For any internal node:
- If both left and right recursive calls return non-null, p is in one subtree and q is in the other, so the current node is the LCA.
- If only one side returns non-null, both p and q are in that subtree, and the returned node is the LCA.
- If both return null, neither p nor q is in this subtree.

**Dry Run** with tree `[3,5,1,6,2,0,8,null,null,7,4]`, p=5, q=1:
```
        3
       / \
      5   1
     / \ / \
    6  2 0  8
      / \
     7   4

lca(3, 5, 1):
  left = lca(5, 5, 1) -> 5 == p, return 5
  right = lca(1, 5, 1) -> 1 == q, return 1
  Both non-null -> return 3
Answer: 3
```

**Dry Run** with p=5, q=4:
```
lca(3, 5, 4):
  left = lca(5, 5, 4) -> 5 == p, return 5
  right = lca(1, 5, 4) -> explores subtrees, finds neither, returns None
  Only left is non-null -> return 5
Answer: 5  (5 is ancestor of 4 and ancestor of itself)
```

**Edge Cases**: p is ancestor of q, p and q are the same node, p or q is the root.

**Follow-up Questions**:
- What if it is a BST? (Exploit sorted property: go left if both < root, right if both > root, otherwise root is LCA.)
- What if nodes have parent pointers? (Treat as "intersection of two linked lists" — find where paths from p and q to root converge.)
- What if p or q might not be in the tree? (Need a modified version that checks both are found.)
- Repeated LCA queries on the same tree? (Preprocess with Euler tour + sparse table for O(1) queries.)

---

### Problem: Validate Binary Search Tree (LC #98) — Medium
**Companies**: Meta, Amazon, Google, Microsoft, Bloomberg.

**Problem**: Determine if a binary tree is a valid BST. A valid BST has: left subtree values < node, right subtree values > node.

**Brute Force**: Do in-order traversal, check if the result is strictly increasing.
```python
def is_valid_bst_inorder(root: TreeNode) -> bool:
    vals = []
    def inorder(node):
        if not node:
            return
        inorder(node.left)
        vals.append(node.val)
        inorder(node.right)
    inorder(root)
    for i in range(1, len(vals)):
        if vals[i] <= vals[i - 1]:
            return False
    return True
```
Time: O(n), Space: O(n) for the array.

**Key Insight**: Pass a valid range [lo, hi] down the tree. Each node must satisfy `lo < node.val < hi`. Left children narrow the upper bound, right children narrow the lower bound.

**Optimal Solution — Range Checking (Top-Down)**:
```python
def is_valid_bst(root: TreeNode) -> bool:
    def validate(node, lo, hi):
        if not node:
            return True
        if node.val <= lo or node.val >= hi:
            return False
        return (validate(node.left, lo, node.val) and
                validate(node.right, node.val, hi))

    return validate(root, float('-inf'), float('inf'))
```
Time: O(n), Space: O(h).

**Optimal Solution — In-Order with Early Termination**:
```python
def is_valid_bst_iterative(root: TreeNode) -> bool:
    stack = []
    prev_val = float('-inf')
    curr = root
    while curr or stack:
        while curr:
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()
        if curr.val <= prev_val:
            return False
        prev_val = curr.val
        curr = curr.right
    return True
```

**Dry Run** with tree `[5, 1, 4, null, null, 3, 6]`:
```
        5
       / \
      1   4    <-- INVALID: 4 < 5 but 3 < 5 is in right subtree
         / \
        3   6

validate(5, -inf, inf): 5 is in range
  validate(1, -inf, 5): 1 is in range
    validate(None, -inf, 1): True
    validate(None, 1, 5): True
  validate(4, 5, inf): 4 < 5? NO -> return False
Answer: False
```

Common mistake: Only checking `node.left.val < node.val < node.right.val` is WRONG. You need to validate the entire subtree constraint, not just the immediate children. Example: `[5, 1, 6, null, null, 3, 7]` — node 3 is in the right subtree of 5 but has value 3 < 5.

**Edge Cases**: Single node (valid), all same values (invalid — BST requires strict inequality), tree with INT_MIN or INT_MAX values.

**Follow-up Questions**:
- What if duplicates are allowed on the left (or right)?
- Can you do it iteratively? (In-order traversal with prev tracking.)
- What is the in-order predecessor and successor of a given node?

---

### Problem: Binary Tree Right Side View (LC #199) — Medium
**Companies**: Meta, Amazon, Microsoft, Bloomberg.

**Problem**: Given a binary tree, return the values of the nodes you can see from the right side (one per level, the rightmost node).

```
        1
       / \
      2   3
       \   \
        5   4
Right side view: [1, 3, 4]
```

**Brute Force / BFS Approach**: Level-order traversal, take the last element of each level.
```python
from collections import deque

def right_side_view_bfs(root: TreeNode) -> list:
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level_size = len(queue)
        for i in range(level_size):
            node = queue.popleft()
            if i == level_size - 1:  # last node in this level
                result.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    return result
```
Time: O(n), Space: O(w) where w = max width of tree.

**Key Insight for DFS**: Do a modified pre-order: visit root, then RIGHT, then LEFT. The first node we see at each depth is the rightmost node at that level.

**Optimal Solution — DFS**:
```python
def right_side_view(root: TreeNode) -> list:
    result = []

    def dfs(node, depth):
        if not node:
            return
        if depth == len(result):
            # First node we see at this depth (from right side)
            result.append(node.val)
        dfs(node.right, depth + 1)  # Visit right first
        dfs(node.left, depth + 1)

    dfs(root, 0)
    return result
```
Time: O(n), Space: O(h).

**Dry Run** with the example:
```
dfs(1, 0): depth=0, len(result)=0, add 1. result=[1]
  dfs(3, 1): depth=1, len(result)=1, add 3. result=[1,3]
    dfs(None, 2): return
    dfs(4, 2): depth=2, len(result)=2, add 4. result=[1,3,4]
  dfs(2, 1): depth=1, len(result)=2, 1 != 2, skip
    dfs(5, 2): depth=2, len(result)=3, 2 != 3, skip
    dfs(None, 2): return
Answer: [1, 3, 4]
```

**Edge Cases**: Empty tree, single node, left-skewed tree (left nodes are visible), complete tree.

**Follow-up Questions**:
- What about the left side view? (Visit left before right.)
- What about top view or bottom view? (Use column indices and BFS.)
- Can you return the boundary of the tree?

---

### Problem: Construct Binary Tree from Preorder and Inorder Traversal (LC #105) — Medium
**Companies**: Meta, Amazon, Google, Microsoft.

**Problem**: Given preorder and inorder traversal arrays, construct the binary tree.

**Key Insight**: In preorder, the first element is always the root. Find that root's position in inorder — everything to its left is the left subtree, everything to its right is the right subtree. Recursively build each subtree.

Use a hashmap for O(1) lookup of root positions in inorder.

**Brute Force** (without hashmap — linear search each time):
```python
def build_tree_brute(preorder, inorder):
    if not preorder or not inorder:
        return None
    root_val = preorder[0]
    root = TreeNode(root_val)
    mid = inorder.index(root_val)  # O(n) search
    root.left = build_tree_brute(preorder[1:mid+1], inorder[:mid])
    root.right = build_tree_brute(preorder[mid+1:], inorder[mid+1:])
    return root
```
Time: O(n^2) worst case due to linear search and array slicing.

**Optimal Solution**:
```python
def build_tree(preorder: list, inorder: list) -> TreeNode:
    inorder_map = {val: idx for idx, val in enumerate(inorder)}
    pre_idx = [0]  # use list to allow mutation in nested function

    def build(in_left, in_right):
        if in_left > in_right:
            return None

        root_val = preorder[pre_idx[0]]
        pre_idx[0] += 1
        root = TreeNode(root_val)

        mid = inorder_map[root_val]
        root.left = build(in_left, mid - 1)    # build left subtree first
        root.right = build(mid + 1, in_right)   # then right subtree

        return root

    return build(0, len(inorder) - 1)
```
Time: O(n), Space: O(n) for the hashmap.

**Dry Run** with `preorder=[3,9,20,15,7], inorder=[9,3,15,20,7]`:
```
inorder_map = {9:0, 3:1, 15:2, 20:3, 7:4}

build(0, 4): root = preorder[0] = 3, mid = 1
  build(0, 0): root = preorder[1] = 9, mid = 0
    build(0, -1): None (left of 9)
    build(1, 0): None (right of 9 — in_left > in_right)
    return TreeNode(9)
  build(2, 4): root = preorder[2] = 20, mid = 3
    build(2, 2): root = preorder[3] = 15, mid = 2
      build(2, 1): None
      build(3, 2): None
      return TreeNode(15)
    build(4, 4): root = preorder[4] = 7, mid = 4
      build(4, 3): None
      build(5, 4): None
      return TreeNode(7)
    return TreeNode(20, left=15, right=7)
  return TreeNode(3, left=9, right=20)

Result:
    3
   / \
  9  20
    /  \
   15   7
```

**Why we build left before right**: Preorder visits root, then LEFT subtree, then right subtree. So after consuming the root, the next entries in preorder belong to the left subtree. If we built right first, we would consume the wrong entries.

**Edge Cases**: Single node, all in left subtree (sorted input for preorder), all in right subtree.

**Follow-up Questions**:
- Can you do it from postorder + inorder? (Last element of postorder is root, build right before left.)
- Can you do it from preorder alone if it is a BST? (Use BST bounds to determine subtree boundaries.)
- What if there are duplicate values? (Cannot construct a unique tree.)

---

### Problem: Serialize and Deserialize Binary Tree (LC #297) — Hard
**Companies**: Meta, Google, Amazon, Microsoft, Uber.

**Problem**: Design an algorithm to serialize a binary tree to a string and deserialize the string back to the tree.

**Key Insight**: Use pre-order traversal with null markers. Serialize: visit each node and record its value (or "null" for empty nodes). Deserialize: read values in the same order and reconstruct.

**Brute Force**: Level-order serialization with null placeholders. Works but produces longer strings due to trailing nulls.
```python
from collections import deque

def serialize_level(root):
    if not root:
        return "[]"
    result = []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        if node:
            result.append(str(node.val))
            queue.append(node.left)
            queue.append(node.right)
        else:
            result.append("null")
    # Remove trailing nulls
    while result and result[-1] == "null":
        result.pop()
    return "[" + ",".join(result) + "]"
```

**Optimal Solution — Preorder DFS**:
```python
class Codec:
    def serialize(self, root: TreeNode) -> str:
        """Pre-order traversal with null markers."""
        result = []

        def dfs(node):
            if not node:
                result.append("N")
                return
            result.append(str(node.val))
            dfs(node.left)
            dfs(node.right)

        dfs(root)
        return ",".join(result)

    def deserialize(self, data: str) -> TreeNode:
        """Reconstruct from pre-order sequence."""
        vals = iter(data.split(","))

        def dfs():
            val = next(vals)
            if val == "N":
                return None
            node = TreeNode(int(val))
            node.left = dfs()
            node.right = dfs()
            return node

        return dfs()
```
Time: O(n) for both operations. Space: O(n).

**Dry Run**:
```
Tree:     1
         / \
        2   3
           / \
          4   5

Serialize:
  dfs(1): append "1"
    dfs(2): append "2"
      dfs(None): append "N"
      dfs(None): append "N"
    dfs(3): append "3"
      dfs(4): append "4"
        dfs(None): append "N"
        dfs(None): append "N"
      dfs(5): append "5"
        dfs(None): append "N"
        dfs(None): append "N"
Result: "1,2,N,N,3,4,N,N,5,N,N"

Deserialize "1,2,N,N,3,4,N,N,5,N,N":
  val="1": create node(1)
    val="2": create node(2)
      val="N": return None (left of 2)
      val="N": return None (right of 2)
    val="3": create node(3)
      val="4": create node(4)
        val="N": return None
        val="N": return None
      val="5": create node(5)
        val="N": return None
        val="N": return None
  Reconstructed tree matches original.
```

**Why preorder works for serialization**: Preorder uniquely encodes the tree structure when null markers are included. Each node and each null is recorded exactly once, and the order of traversal lets us reconstruct without ambiguity.

**Edge Cases**: Empty tree (serializes to "N"), single node, tree with negative values, very large values.

**Follow-up Questions**:
- Can you compress the serialized format? (Use binary encoding, varint for values.)
- How would you handle a BST more efficiently? (Preorder without null markers suffices — BST bounds determine subtree boundaries.)
- What if the tree is very wide? (Level-order uses more space with null placeholders.)
- Stream serialization? (Use a delimiter-based format that can be parsed incrementally.)

---

### Problem: Binary Tree Maximum Path Sum (LC #124) — Hard
**Companies**: Meta, Google, Amazon, Microsoft — frequently asked at senior levels.

**Problem**: Find the maximum path sum in a binary tree. A path is any sequence of nodes connected by edges. The path does not need to pass through the root and does not need to go from a leaf.

```
       -10
       /  \
      9   20
         /  \
        15   7
Max path sum: 15 + 20 + 7 = 42
```

**Brute Force**: For every pair of nodes, find the path between them and compute its sum. This is O(n^3) and impractical.

**Key Insight**: At each node, we make a choice: the path either "turns" at this node (using both left and right children) or continues through this node (can only use one child). We track the global max considering turns, but return only the one-sided max (for the parent to use).

The distinction:
- **Path through node** (for global max): `node.val + max(0, left_gain) + max(0, right_gain)`
- **Path extending to parent** (return value): `node.val + max(0, max(left_gain, right_gain))`

We use `max(0, ...)` because a negative-sum subtree should be ignored (do not extend into it).

**Optimal Solution**:
```python
def max_path_sum(root: TreeNode) -> int:
    max_sum = float('-inf')

    def gain(node):
        """Return max gain obtainable from a path starting at node going downward."""
        nonlocal max_sum
        if not node:
            return 0

        # Max gain from left and right children (ignore negative paths)
        left_gain = max(0, gain(node.left))
        right_gain = max(0, gain(node.right))

        # Path through this node as the highest point (turning point)
        path_through = node.val + left_gain + right_gain
        max_sum = max(max_sum, path_through)

        # Return max gain extending downward (can only go one way to parent)
        return node.val + max(left_gain, right_gain)

    gain(root)
    return max_sum
```
Time: O(n), Space: O(h).

**Dry Run** with the example:
```
gain(9):   left=0, right=0, path_through=9, max_sum=9, return 9
gain(15):  left=0, right=0, path_through=15, max_sum=15, return 15
gain(7):   left=0, right=0, path_through=7, max_sum=15, return 7
gain(20):  left=max(0,15)=15, right=max(0,7)=7
           path_through = 20+15+7 = 42, max_sum=42
           return 20 + max(15,7) = 35
gain(-10): left=max(0,9)=9, right=max(0,35)=35
           path_through = -10+9+35 = 34, max_sum=42 (no update)
           return -10 + max(9,35) = 25

Answer: max_sum = 42
```

**Why `max(0, ...)` is critical**: A subtree with negative gain should not be included — the path is better off not going there at all. Without this, negative subtrees would drag down the sum.

**Edge Cases**: All negative values (answer is the least negative single node), single node, tree with all zeros.

**Follow-up Questions**:
- What if the path must go from leaf to leaf? (Cannot use `max(0, ...)` — must include at least one path from each non-null child.)
- What if we need to return the actual path, not just the sum?
- How is this related to Kadane's algorithm? (Same idea: at each position, decide whether to extend the current path or start fresh.)

---

## Common Mistakes & Interview Tips

### Mistakes to Avoid
1. **Confusing height with depth** — Height is bottom-up (leaf = 0 or 1 depending on convention). Depth is top-down (root = 0). Be consistent and clarify with the interviewer.
2. **Not handling null nodes** — Always have a base case `if not node: return ...` as the very first line.
3. **Mutating the tree unintentionally** — Morris traversal modifies and restores the tree. Make sure you restore it if the tree is needed later.
4. **Wrong return value in post-order** — When a function returns info to the parent, make sure the return value represents what the parent needs (one-sided path, not both-sided).
5. **BST validation: checking only immediate children** — `node.left.val < node.val` is necessary but not sufficient. You must check the entire subtree constraint.
6. **In-order traversal of BST: assuming sorted without handling duplicates** — Clarify with the interviewer whether the BST has strict inequality.
7. **Confusing preorder and inorder indices** — In the construct-from-preorder-inorder problem, be precise about which slice of the preorder array corresponds to which subtree.

### Interview Tips
1. **Start with recursive solution** — Trees are recursive structures. The recursive solution is usually the most natural. Convert to iterative if asked.
2. **Clarify the return value of your DFS** — Before coding, explicitly state what your recursive function returns. "This function returns the height of the subtree rooted at node."
3. **Draw the tree and trace through** — Interviewers want to see you think. Draw a small tree (5-7 nodes) and trace your algorithm.
4. **Know when to use BFS vs DFS** — BFS for level-by-level problems. DFS for depth/height/path problems.
5. **For hard problems, identify the two-value pattern** — Many hard tree problems require tracking two things: a return value for the parent AND a global optimum. Diameter, max path sum, and others all follow this pattern.
6. **Mention space complexity** — Recursive solutions use O(h) stack space. For balanced trees this is O(log n), but for skewed trees it is O(n). If this matters, offer an iterative or Morris traversal solution.

---

## Pattern Connections

| Pattern | Connection to Trees |
|---------|--------------------|
| **DFS** | Tree DFS is the simplest form of graph DFS — no visited set needed because trees are acyclic. |
| **BFS** | Level-order traversal is BFS on a tree. Same queue-based approach as graph BFS. |
| **Divide and Conquer** | Every recursive tree problem is D&C: split at the root into left and right subproblems. |
| **Binary Search** | BST operations (search, insert, validate) are binary search in tree form. |
| **Stack** | Iterative tree traversals use an explicit stack to simulate recursion. |
| **Recursion** | Trees ARE recursion. Mastering tree problems means mastering recursive thinking. |
| **Dynamic Programming** | Some tree DP problems exist (house robber on tree, tree diameter). They follow the post-order pattern. |
| **Serialization** | Serialize/deserialize is about encoding tree structure — similar to encoding graphs or complex data structures. |

### Progression Path
```
Invert Tree (226) -> Same Tree (100) -> Symmetric Tree (101)
Max Depth (104) -> Diameter (543) -> Max Path Sum (124)
Validate BST (98) -> Kth Smallest (230) -> BST Iterator (173)
LCA (236) -> LCA in BST (235) -> LCA with Parent Pointers
Level Order (102) -> Right Side View (199) -> Zigzag (103)
Construct from Preorder+Inorder (105) -> Serialize/Deserialize (297)
```
