# Tree Traversals Pattern

## What are Tree Traversals?

### Explain Like I'm 5
Imagine you have a family tree with grandparents, parents, and children. Tree traversal is like visiting everyone in your family, but you need to decide the ORDER in which you visit them:
- Do you visit grandparents first, then parents, then kids? (top to bottom)
- Do you visit all people on the same level together? (level by level)
- Do you visit the left side of the family before the right side?

Just like there are different ways to visit your family members, there are different ways to visit nodes in a tree!

### Technical Definition
Tree traversal is the process of visiting each node in a tree data structure exactly once in a systematic way. The main traversal strategies differ in the order in which they visit nodes:
- **Depth-First Search (DFS)**: Explores as far down a branch as possible before backtracking
  - Inorder (Left → Root → Right)
  - Preorder (Root → Left → Right)
  - Postorder (Left → Right → Root)
- **Breadth-First Search (BFS)**: Explores all nodes at the current level before moving to the next level
  - Level Order (level by level, left to right)

## Real-World Analogy

### File System Navigation
Think of your computer's file system:
```
/root
  /Documents
    /Work
      report.pdf
    /Personal
      photo.jpg
  /Downloads
    song.mp3
```

Different traversals represent different ways to explore files:
- **Preorder (Root → Left → Right)**: Like a "top-down" folder listing
  - Visit `/root` first, then explore `/Documents`, then `/Downloads`
  - Useful for copying a directory structure

- **Inorder (Left → Root → Right)**: For a Binary Search Tree
  - Gives you files in sorted alphabetical order
  - Like sorting all files alphabetically regardless of folder

- **Postorder (Left → Right → Root)**: Like calculating disk space
  - Calculate size of child folders first, then parent
  - Useful for deleting directories (delete contents before directory itself)

- **Level Order**: Like viewing files by depth
  - First see `/root`, then all top-level folders, then their contents
  - Useful for finding the shortest path or nearest file

### Organization Chart
An org chart is another tree:
```
        CEO
       /   \
    CTO     CFO
    / \     / \
  Dev Ops Acc HR
```
- **Preorder**: CEO announces something, then managers pass it down (top-down communication)
- **Postorder**: Employees report to managers, managers report to CEO (bottom-up reporting)
- **Level Order**: Annual all-hands meeting by seniority level

## When to Use

### Clear Signals for Tree Problems
Use tree traversal patterns when you see:

1. **Data Structure Clues**:
   - Problem mentions "binary tree", "BST", "tree node"
   - Hierarchical data (file system, org chart, XML/HTML DOM)
   - Parent-child relationships

2. **Operation Clues**:
   - "Visit all nodes"
   - "Search for a value"
   - "Print/collect nodes in specific order"
   - "Find path from root to node"
   - "Calculate tree properties" (height, diameter, sum)

3. **Traversal Type Signals**:
   - **Inorder**: BST problems, getting sorted order
   - **Preorder**: Creating a copy, serialization, prefix expressions
   - **Postorder**: Deletion, calculating properties from children, postfix expressions
   - **Level Order**: Shortest path, level-wise operations, BFS problems

4. **Problem Keywords**:
   - "Left to right", "level by level" → Level Order
   - "Sorted order" (in BST) → Inorder
   - "Top-down" → Preorder
   - "Bottom-up", "children first" → Postorder

## The Problems

### Core Traversal Problems

#### 1. Inorder Traversal (Left → Root → Right)
**Use Case**: Get nodes in sorted order for BST, check if tree is BST

```python
# Definition for a binary tree node
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# Recursive Approach
def inorderTraversal(root: TreeNode) -> list[int]:
    """
    Inorder traversal: Left → Root → Right
    Time: O(n) - visit each node once
    Space: O(h) - recursion stack height
    """
    result = []

    def inorder(node):
        if not node:
            return

        # First, traverse left subtree
        inorder(node.left)

        # Then, visit root (process current node)
        result.append(node.val)

        # Finally, traverse right subtree
        inorder(node.right)

    inorder(root)
    return result

# Iterative Approach using Stack
def inorderTraversalIterative(root: TreeNode) -> list[int]:
    """
    Iterative inorder using explicit stack
    Time: O(n)
    Space: O(h) - stack space

    Key insight: Keep going left until we can't, then process node,
    then go right once. This mimics the recursive call stack.
    """
    result = []
    stack = []
    current = root

    while current or stack:
        # Go as far left as possible
        while current:
            stack.append(current)
            current = current.left

        # Process the leftmost unprocessed node
        current = stack.pop()
        result.append(current.val)

        # Move to right subtree
        current = current.right

    return result
```

#### 2. Preorder Traversal (Root → Left → Right)
**Use Case**: Create copy of tree, serialize tree, evaluate prefix expressions

```python
# Recursive Approach
def preorderTraversal(root: TreeNode) -> list[int]:
    """
    Preorder traversal: Root → Left → Right
    Time: O(n)
    Space: O(h)
    """
    result = []

    def preorder(node):
        if not node:
            return

        # First, visit root (process current node)
        result.append(node.val)

        # Then, traverse left subtree
        preorder(node.left)

        # Finally, traverse right subtree
        preorder(node.right)

    preorder(root)
    return result

# Iterative Approach using Stack
def preorderTraversalIterative(root: TreeNode) -> list[int]:
    """
    Iterative preorder using stack
    Time: O(n)
    Space: O(h)

    Key insight: Process node immediately when we see it,
    then push right child first (so left is processed first)
    """
    if not root:
        return []

    result = []
    stack = [root]

    while stack:
        # Pop and process current node
        node = stack.pop()
        result.append(node.val)

        # Push right first so left is processed first (LIFO)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)

    return result
```

#### 3. Postorder Traversal (Left → Right → Root)
**Use Case**: Delete tree, calculate properties that depend on children

```python
# Recursive Approach
def postorderTraversal(root: TreeNode) -> list[int]:
    """
    Postorder traversal: Left → Right → Root
    Time: O(n)
    Space: O(h)
    """
    result = []

    def postorder(node):
        if not node:
            return

        # First, traverse left subtree
        postorder(node.left)

        # Then, traverse right subtree
        postorder(node.right)

        # Finally, visit root (process current node)
        result.append(node.val)

    postorder(root)
    return result

# Iterative Approach using Two Stacks
def postorderTraversalIterative(root: TreeNode) -> list[int]:
    """
    Iterative postorder using two stacks
    Time: O(n)
    Space: O(h)

    Key insight: Use two stacks. First stack does reverse postorder
    (Root → Right → Left), second stack reverses it back.
    """
    if not root:
        return []

    stack1 = [root]
    stack2 = []

    # Populate stack2 with reverse postorder
    while stack1:
        node = stack1.pop()
        stack2.append(node)

        # Push left first, then right (opposite of preorder)
        if node.left:
            stack1.append(node.left)
        if node.right:
            stack1.append(node.right)

    # Pop from stack2 to get correct postorder
    result = []
    while stack2:
        result.append(stack2.pop().val)

    return result

# Alternative: Iterative with One Stack (More Complex)
def postorderTraversalOneStack(root: TreeNode) -> list[int]:
    """
    Iterative postorder with one stack
    Time: O(n)
    Space: O(h)

    Track last visited node to know if we're coming back from right child
    """
    if not root:
        return []

    result = []
    stack = []
    current = root
    last_visited = None

    while current or stack:
        # Go to leftmost node
        while current:
            stack.append(current)
            current = current.left

        # Peek at top of stack
        peek_node = stack[-1]

        # If right child exists and not yet processed
        if peek_node.right and last_visited != peek_node.right:
            current = peek_node.right
        else:
            # Process this node
            result.append(peek_node.val)
            last_visited = stack.pop()

    return result
```

#### 4. Level Order Traversal (BFS)
**Use Case**: Find shortest path, level-wise operations, print tree by levels

```python
from collections import deque

def levelOrder(root: TreeNode) -> list[list[int]]:
    """
    Level order traversal using BFS with queue
    Time: O(n) - visit each node once
    Space: O(w) - where w is max width of tree

    Returns list of lists, where each inner list is one level
    """
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)  # Number of nodes at current level
        current_level = []

        # Process all nodes at current level
        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)

            # Add children for next level
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        result.append(current_level)

    return result

def levelOrderFlat(root: TreeNode) -> list[int]:
    """
    Level order traversal returning flat list
    Time: O(n)
    Space: O(w)
    """
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        node = queue.popleft()
        result.append(node.val)

        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)

    return result
```

### Key Tree Problems Using Traversals

#### 5. Lowest Common Ancestor (LCA)
**Pattern**: Postorder traversal (need info from children)

```python
def lowestCommonAncestor(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    """
    Find lowest common ancestor of two nodes
    Time: O(n) - might visit all nodes
    Space: O(h) - recursion stack

    Key insight: Use postorder logic - check children first.
    If we find both p and q in different subtrees, current node is LCA.
    """
    # Base case: empty tree or found one of the target nodes
    if not root or root == p or root == q:
        return root

    # Search in left and right subtrees (postorder: children first)
    left = lowestCommonAncestor(root.left, p, q)
    right = lowestCommonAncestor(root.right, p, q)

    # If both left and right found something, current node is LCA
    if left and right:
        return root

    # Otherwise, return whichever side found something (or None)
    return left if left else right

# For BST, we can optimize using BST property
def lowestCommonAncestorBST(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    """
    LCA in BST using BST properties
    Time: O(h) - only traverse one path
    Space: O(1) - iterative solution
    """
    while root:
        # Both p and q are smaller - LCA is in left subtree
        if p.val < root.val and q.val < root.val:
            root = root.left
        # Both p and q are larger - LCA is in right subtree
        elif p.val > root.val and q.val > root.val:
            root = root.right
        else:
            # Split point found - current node is LCA
            return root

    return None
```

#### 6. Validate Binary Search Tree
**Pattern**: Inorder traversal (should give sorted order)

```python
def isValidBST(root: TreeNode) -> bool:
    """
    Validate if tree is a valid BST
    Time: O(n)
    Space: O(h)

    Method 1: Inorder traversal should give sorted order
    """
    prev = [None]  # Use list to maintain reference across recursion

    def inorder(node):
        if not node:
            return True

        # Check left subtree
        if not inorder(node.left):
            return False

        # Check current node against previous
        if prev[0] is not None and node.val <= prev[0]:
            return False
        prev[0] = node.val

        # Check right subtree
        return inorder(node.right)

    return inorder(root)

def isValidBSTRange(root: TreeNode) -> bool:
    """
    Method 2: Use valid range for each node
    Time: O(n)
    Space: O(h)

    Each node must be within a valid range [min_val, max_val]
    """
    def validate(node, min_val, max_val):
        if not node:
            return True

        # Current node must be within range
        if node.val <= min_val or node.val >= max_val:
            return False

        # Left subtree: all values must be < node.val
        # Right subtree: all values must be > node.val
        return (validate(node.left, min_val, node.val) and
                validate(node.right, node.val, max_val))

    return validate(root, float('-inf'), float('inf'))
```

#### 7. Binary Tree Maximum Path Sum
**Pattern**: Postorder (need info from children to make decision)

```python
def maxPathSum(root: TreeNode) -> int:
    """
    Find maximum path sum in binary tree
    Path can start and end at any node
    Time: O(n)
    Space: O(h)

    Key insight: For each node, max path through it is:
    node.val + max_gain(left) + max_gain(right)
    But we can only return one branch to parent
    """
    max_sum = [float('-inf')]  # Use list to maintain reference

    def max_gain(node):
        """Returns max sum of path starting at this node going down"""
        if not node:
            return 0

        # Get max gain from left and right (ignore negative gains)
        left_gain = max(max_gain(node.left), 0)
        right_gain = max(max_gain(node.right), 0)

        # Calculate max path sum through current node
        path_sum = node.val + left_gain + right_gain

        # Update global maximum
        max_sum[0] = max(max_sum[0], path_sum)

        # Return max gain continuing to parent (can only pick one branch)
        return node.val + max(left_gain, right_gain)

    max_gain(root)
    return max_sum[0]
```

#### 8. Serialize and Deserialize Binary Tree
**Pattern**: Preorder for serialization, reconstruct using preorder logic

```python
def serialize(root: TreeNode) -> str:
    """
    Serialize tree to string using preorder traversal
    Time: O(n)
    Space: O(n)
    """
    def preorder(node):
        if not node:
            return ["null"]

        # Preorder: Root → Left → Right
        return ([str(node.val)] +
                preorder(node.left) +
                preorder(node.right))

    return ",".join(preorder(root))

def deserialize(data: str) -> TreeNode:
    """
    Deserialize string to tree
    Time: O(n)
    Space: O(n)
    """
    def build_tree(nodes):
        val = next(nodes)

        if val == "null":
            return None

        # Preorder: create root, then left, then right
        node = TreeNode(int(val))
        node.left = build_tree(nodes)
        node.right = build_tree(nodes)

        return node

    nodes = iter(data.split(","))
    return build_tree(nodes)
```

## Brute Force Approach

### When Brute Force Applies
Tree traversal problems don't typically have a "brute force" in the traditional sense, but there are inefficient approaches:

1. **Using Multiple Passes**:
   - Instead of calculating everything in one traversal, making multiple passes
   - Example: Finding height and diameter in separate traversals

2. **Not Using Appropriate Data Structures**:
   - Using array instead of queue for level order
   - Not using stack for iterative DFS

3. **Excessive Memory Usage**:
   - Storing entire traversal in memory when only need to check property
   - Creating new lists for each recursive call instead of passing accumulator

### Example: Finding Tree Height (Inefficient vs Efficient)

```python
# Inefficient: Multiple traversals
def getHeight(root: TreeNode) -> int:
    """This works but is less elegant"""
    if not root:
        return 0

    # Count all nodes in left and right
    left_count = countNodes(root.left)
    right_count = countNodes(root.right)

    # This doesn't actually give height, showing bad logic
    return 1 + max(left_count, right_count)

def countNodes(node):
    if not node:
        return 0
    return 1 + countNodes(node.left) + countNodes(node.right)

# Efficient: Single traversal
def maxDepth(root: TreeNode) -> int:
    """
    Calculate height in single postorder traversal
    Time: O(n)
    Space: O(h)
    """
    if not root:
        return 0

    # Get height from children, then calculate for current
    left_height = maxDepth(root.left)
    right_height = maxDepth(root.right)

    return 1 + max(left_height, right_height)
```

## Optimized Solutions

### Morris Traversal (O(1) Space)
**Ultimate Optimization**: Traverse tree without recursion or stack

```python
def morrisInorder(root: TreeNode) -> list[int]:
    """
    Morris Inorder Traversal - O(1) space
    Time: O(n) - each edge visited at most twice
    Space: O(1) - only using pointers, no stack/recursion

    Key idea: Use the tree itself as the stack by creating
    temporary links (threaded tree)
    """
    result = []
    current = root

    while current:
        if not current.left:
            # No left subtree, process current and go right
            result.append(current.val)
            current = current.right
        else:
            # Find inorder predecessor (rightmost node in left subtree)
            predecessor = current.left
            while predecessor.right and predecessor.right != current:
                predecessor = predecessor.right

            if not predecessor.right:
                # Create temporary link (thread)
                predecessor.right = current
                current = current.left
            else:
                # We've already visited left subtree, remove thread
                predecessor.right = None
                result.append(current.val)
                current = current.right

    return result

def morrisPreorder(root: TreeNode) -> list[int]:
    """
    Morris Preorder Traversal - O(1) space
    Time: O(n)
    Space: O(1)
    """
    result = []
    current = root

    while current:
        if not current.left:
            result.append(current.val)
            current = current.right
        else:
            predecessor = current.left
            while predecessor.right and predecessor.right != current:
                predecessor = predecessor.right

            if not predecessor.right:
                # Process node BEFORE going left (preorder)
                result.append(current.val)
                predecessor.right = current
                current = current.left
            else:
                predecessor.right = None
                current = current.right

    return result
```

### Vertical Order Traversal
**Advanced Pattern**: Combine BFS with coordinate tracking

```python
from collections import defaultdict, deque

def verticalOrder(root: TreeNode) -> list[list[int]]:
    """
    Vertical order traversal using BFS
    Time: O(n log n) - due to sorting columns
    Space: O(n)

    Each node has (row, col) coordinate
    Nodes in same column go together, sorted by row
    """
    if not root:
        return []

    # Map column index to list of (row, value) pairs
    column_table = defaultdict(list)
    queue = deque([(root, 0, 0)])  # (node, row, col)

    while queue:
        node, row, col = queue.popleft()
        column_table[col].append((row, node.val))

        if node.left:
            queue.append((node.left, row + 1, col - 1))
        if node.right:
            queue.append((node.right, row + 1, col + 1))

    # Sort columns and build result
    result = []
    for col in sorted(column_table.keys()):
        # Sort by row within each column
        column_table[col].sort()
        result.append([val for row, val in column_table[col]])

    return result
```

### Tree Construction from Traversals

```python
def buildTreeFromInorderPreorder(preorder: list[int], inorder: list[int]) -> TreeNode:
    """
    Construct tree from inorder and preorder traversal
    Time: O(n)
    Space: O(n)

    Key insight:
    - First element of preorder is root
    - Find root in inorder to split left/right subtrees
    - Recursively build left and right
    """
    if not preorder or not inorder:
        return None

    # Build map for O(1) lookup of root index in inorder
    inorder_map = {val: idx for idx, val in enumerate(inorder)}

    def build(pre_start, pre_end, in_start, in_end):
        if pre_start > pre_end:
            return None

        # First element in preorder is root
        root_val = preorder[pre_start]
        root = TreeNode(root_val)

        # Find root position in inorder
        root_index = inorder_map[root_val]
        left_size = root_index - in_start

        # Build left and right subtrees
        root.left = build(
            pre_start + 1,
            pre_start + left_size,
            in_start,
            root_index - 1
        )
        root.right = build(
            pre_start + left_size + 1,
            pre_end,
            root_index + 1,
            in_end
        )

        return root

    return build(0, len(preorder) - 1, 0, len(inorder) - 1)

def buildTreeFromInorderPostorder(inorder: list[int], postorder: list[int]) -> TreeNode:
    """
    Construct tree from inorder and postorder traversal
    Time: O(n)
    Space: O(n)

    Key insight:
    - Last element of postorder is root
    - Find root in inorder to split left/right subtrees
    """
    if not inorder or not postorder:
        return None

    inorder_map = {val: idx for idx, val in enumerate(inorder)}

    def build(in_start, in_end, post_start, post_end):
        if in_start > in_end:
            return None

        # Last element in postorder is root
        root_val = postorder[post_end]
        root = TreeNode(root_val)

        root_index = inorder_map[root_val]
        left_size = root_index - in_start

        root.left = build(
            in_start,
            root_index - 1,
            post_start,
            post_start + left_size - 1
        )
        root.right = build(
            root_index + 1,
            in_end,
            post_start + left_size,
            post_end - 1
        )

        return root

    return build(0, len(inorder) - 1, 0, len(postorder) - 1)
```

## Time & Space Complexity Analysis

### Recursive Traversals

| Traversal Type | Time Complexity | Space Complexity | Notes |
|----------------|-----------------|------------------|-------|
| Inorder (Recursive) | O(n) | O(h) | h = height, worst case O(n) for skewed tree |
| Preorder (Recursive) | O(n) | O(h) | Same as inorder |
| Postorder (Recursive) | O(n) | O(h) | Same as inorder |

- **Time**: O(n) because we visit each node exactly once
- **Space**: O(h) for recursion stack
  - Best case: O(log n) for balanced tree
  - Worst case: O(n) for completely skewed tree

### Iterative Traversals

| Traversal Type | Time Complexity | Space Complexity | Notes |
|----------------|-----------------|------------------|-------|
| Inorder (Iterative) | O(n) | O(h) | Explicit stack instead of call stack |
| Preorder (Iterative) | O(n) | O(h) | Same space as recursive |
| Postorder (Iterative) | O(n) | O(h) | May use two stacks |
| Level Order (BFS) | O(n) | O(w) | w = max width of tree |

- **Level Order Space**: O(w) where w is maximum width
  - For balanced tree: O(n/2) ≈ O(n) at last level
  - For skewed tree: O(1) only one node per level

### Morris Traversal

| Traversal Type | Time Complexity | Space Complexity | Notes |
|----------------|-----------------|------------------|-------|
| Morris Inorder | O(n) | O(1) | No extra space! |
| Morris Preorder | O(n) | O(1) | No extra space! |

- **Time**: Still O(n) even though we visit some edges twice
- **Space**: O(1) constant space, only pointers
- **Trade-off**: More complex code, temporarily modifies tree structure

### Complex Operations

| Operation | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| LCA (Binary Tree) | O(n) | O(h) |
| LCA (BST) | O(h) | O(1) iterative |
| Validate BST | O(n) | O(h) |
| Max Path Sum | O(n) | O(h) |
| Serialize/Deserialize | O(n) | O(n) |
| Build from Traversals | O(n) | O(n) |
| Vertical Order | O(n log n) | O(n) |

## Variations

### 1. Recursive vs Iterative

```python
# When to use each:

# Recursive:
# ✅ Cleaner, more intuitive code
# ✅ Natural for tree problems
# ✅ Easy to understand and maintain
# ❌ Can cause stack overflow for very deep trees
# ❌ Harder to pause/resume traversal

def recursiveExample(root):
    def traverse(node):
        if not node:
            return
        # Process node
        traverse(node.left)
        traverse(node.right)

    traverse(root)

# Iterative:
# ✅ No stack overflow risk
# ✅ Can pause/resume traversal
# ✅ More control over execution
# ❌ More complex code
# ❌ Need to manage explicit stack/queue

def iterativeExample(root):
    if not root:
        return

    stack = [root]
    while stack:
        node = stack.pop()
        # Process node
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
```

### 2. Reverse Order Traversals

```python
def reverseLevelOrder(root: TreeNode) -> list[list[int]]:
    """
    Level order from bottom to top
    Time: O(n), Space: O(n)
    """
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        level = []

        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        result.append(level)

    # Reverse the result
    return result[::-1]

def zigzagLevelOrder(root: TreeNode) -> list[list[int]]:
    """
    Zigzag (alternating left-to-right, right-to-left)
    Time: O(n), Space: O(n)
    """
    if not root:
        return []

    result = []
    queue = deque([root])
    left_to_right = True

    while queue:
        level_size = len(queue)
        level = []

        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        # Reverse every other level
        if not left_to_right:
            level.reverse()

        result.append(level)
        left_to_right = not left_to_right

    return result
```

### 3. Boundary Traversal

```python
def boundaryTraversal(root: TreeNode) -> list[int]:
    """
    Print boundary of tree: left boundary, leaves, right boundary
    Time: O(n), Space: O(h)
    """
    if not root:
        return []

    result = [root.val]

    def is_leaf(node):
        return node and not node.left and not node.right

    def add_left_boundary(node):
        """Add left boundary (excluding leaves)"""
        while node:
            if not is_leaf(node):
                result.append(node.val)

            if node.left:
                node = node.left
            else:
                node = node.right

    def add_leaves(node):
        """Add all leaves (inorder)"""
        if not node:
            return

        add_leaves(node.left)

        if is_leaf(node):
            result.append(node.val)

        add_leaves(node.right)

    def add_right_boundary(node):
        """Add right boundary in reverse (excluding leaves)"""
        temp = []
        while node:
            if not is_leaf(node):
                temp.append(node.val)

            if node.right:
                node = node.right
            else:
                node = node.left

        # Add in reverse order
        result.extend(reversed(temp))

    if not is_leaf(root):
        add_left_boundary(root.left)
        add_leaves(root)
        add_right_boundary(root.right)

    return result
```

### 4. Right/Left Side View

```python
def rightSideView(root: TreeNode) -> list[int]:
    """
    View tree from right side (rightmost node at each level)
    Time: O(n), Space: O(h)
    """
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)

        for i in range(level_size):
            node = queue.popleft()

            # Last node in level is rightmost
            if i == level_size - 1:
                result.append(node.val)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

    return result

def leftSideView(root: TreeNode) -> list[int]:
    """
    View tree from left side (leftmost node at each level)
    Time: O(n), Space: O(h)
    """
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)

        for i in range(level_size):
            node = queue.popleft()

            # First node in level is leftmost
            if i == 0:
                result.append(node.val)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

    return result
```

## Pro Tips for Senior Engineers

### 1. Choosing the Right Traversal

**Decision Framework:**

- **Inorder (Left → Root → Right)**
  - Use when: Working with BST and need sorted order
  - Examples: Validate BST, find kth smallest, BST iterator
  - Binary operator evaluation: (left operand) operator (right operand)

- **Preorder (Root → Left → Right)**
  - Use when: Need to create copy or serialize tree
  - Examples: Clone tree, serialize, prefix expression evaluation
  - Top-down operations: parent info needed before children

- **Postorder (Left → Right → Root)**
  - Use when: Need info from children before processing parent
  - Examples: Delete tree, calculate height/diameter, postfix expressions
  - Bottom-up operations: child results needed to calculate parent

- **Level Order (BFS)**
  - Use when: Need to process by levels or find shortest path
  - Examples: Right side view, zigzag traversal, minimum depth
  - Level-wise operations: same-depth nodes together

### 2. Space Optimization Techniques

```python
# Technique 1: Use iterators/generators for large trees
def inorder_generator(root):
    """
    Yields nodes one at a time instead of storing all in memory
    Useful for huge trees where you only need to process nodes one by one
    """
    stack = []
    current = root

    while current or stack:
        while current:
            stack.append(current)
            current = current.left

        current = stack.pop()
        yield current.val  # Yield instead of append
        current = current.right

# Usage: for val in inorder_generator(root): process(val)

# Technique 2: Morris traversal for O(1) space
# Use when: Memory is extremely limited
# Trade-off: More complex code, modifies tree temporarily

# Technique 3: Tail recursion optimization (language-dependent)
# Python doesn't optimize tail recursion, but concept is important
```

### 3. Edge Cases to Always Check

```python
def robustTraversal(root):
    """Template showing all edge cases"""

    # Edge case 1: Null tree
    if not root:
        return []

    # Edge case 2: Single node
    if not root.left and not root.right:
        return [root.val]

    # Edge case 3: Only left child (skewed tree)
    # Edge case 4: Only right child (skewed tree)
    # Your traversal logic should handle these naturally

    # Edge case 5: Negative values
    # Don't assume all values are positive!

    # Edge case 6: Duplicate values
    # Tree may have duplicate values

    result = []
    # ... traversal logic
    return result
```

### 4. DFS vs BFS: Making the Choice

```python
# Use DFS (recursive or with stack) when:
# 1. Solution is deep in the tree
# 2. Tree is very wide (level order would use too much space)
# 3. Backtracking is needed
# 4. Need to explore all paths

# Use BFS (with queue) when:
# 1. Solution is close to root
# 2. Need shortest path
# 3. Level-wise processing required
# 4. Tree is very deep (avoid stack overflow)

# Example: Find minimum depth
def minDepthBFS(root):
    """
    BFS is better here because we can return as soon as we find first leaf
    No need to explore entire tree
    """
    if not root:
        return 0

    queue = deque([(root, 1)])

    while queue:
        node, depth = queue.popleft()

        # First leaf we encounter is at minimum depth
        if not node.left and not node.right:
            return depth

        if node.left:
            queue.append((node.left, depth + 1))
        if node.right:
            queue.append((node.right, depth + 1))

    return 0

def minDepthDFS(root):
    """
    DFS is less efficient here - must explore all paths
    """
    if not root:
        return 0

    if not root.left:
        return 1 + minDepthDFS(root.right)
    if not root.right:
        return 1 + minDepthDFS(root.left)

    return 1 + min(minDepthDFS(root.left), minDepthDFS(root.right))
```

### 5. Handling Tree Modifications

```python
# When modifying tree during traversal:
# 1. Be careful with iterative approaches (can lose references)
# 2. Consider making copy if original tree needs to be preserved
# 3. Watch out for cycles if creating links (like Morris traversal)

def deleteNode(root, key):
    """
    Example: Safely delete node from BST
    Always return new root (might change)
    """
    if not root:
        return None

    if key < root.val:
        root.left = deleteNode(root.left, key)
    elif key > root.val:
        root.right = deleteNode(root.right, key)
    else:
        # Node found - handle three cases
        if not root.left:
            return root.right
        if not root.right:
            return root.left

        # Node has two children: find inorder successor
        min_node = root.right
        while min_node.left:
            min_node = min_node.left

        root.val = min_node.val
        root.right = deleteNode(root.right, min_node.val)

    return root
```

### 6. Testing Strategies

```python
# Always test with these tree shapes:

# 1. Empty tree
test_tree_1 = None

# 2. Single node
test_tree_2 = TreeNode(1)

# 3. Left-skewed tree
#     1
#    /
#   2
#  /
# 3

# 4. Right-skewed tree
# 1
#  \
#   2
#    \
#     3

# 5. Complete binary tree
#       1
#     /   \
#    2     3
#   / \   / \
#  4   5 6   7

# 6. Tree with only left children at some nodes
#       1
#      / \
#     2   3
#    /
#   4

# 7. Tree with negative values
#      -1
#     /  \
#   -2   -3

# 8. Tree with duplicates
#      1
#     / \
#    1   1
```

## Problem Recognition

### Identifying Tree Traversal Problems

**Ask yourself these questions:**

1. **Is data hierarchical?** → Likely a tree problem
   - Organization charts, file systems, expression trees, DOM structure

2. **Do I need to visit all nodes?** → Need a traversal strategy
   - Decide which traversal based on required order

3. **Do I need information from children?** → Postorder or bottom-up
   - Height, diameter, tree validity, subtree sums

4. **Do I need to process top-down?** → Preorder
   - Copying, serialization, path sums

5. **Is it a BST?** → Consider inorder for sorted order
   - Validation, kth smallest/largest, range queries

6. **Do I need level-wise processing?** → Level order (BFS)
   - Minimum depth, level sums, zigzag, width

7. **Do I need to find a path?** → DFS with backtracking
   - Root to leaf paths, path sum, LCA

### Problem Pattern Categories

| Pattern | Traversal Type | Examples |
|---------|----------------|----------|
| Tree Properties | Postorder | Height, diameter, balanced check |
| Tree Validation | Inorder | Validate BST, find duplicates |
| Tree Construction | Preorder | Clone tree, serialize |
| Path Finding | DFS Backtracking | Path sum, root to leaf paths |
| Level Operations | Level Order (BFS) | Right side view, zigzag |
| Node Relationships | DFS/BFS | LCA, distance between nodes |
| Tree Modification | Choose based on operation | Delete, insert, flatten |

### Keywords That Signal Tree Traversals

- **"All nodes"** → Need complete traversal
- **"Sorted order"** (BST) → Inorder
- **"Level by level"** → Level order (BFS)
- **"Top to bottom"** → Preorder
- **"Bottom to top"** → Postorder
- **"Shortest"** → BFS
- **"All paths"** → DFS with backtracking
- **"Serialize"** → Usually preorder
- **"From leaves"** → Postorder

## Practice Problems

### Beginner Level
1. **Binary Tree Inorder Traversal** (LeetCode 94)
   - Practice: Basic recursive and iterative inorder
   - Concepts: Stack usage, recursion basics

2. **Maximum Depth of Binary Tree** (LeetCode 104)
   - Practice: Simple postorder traversal
   - Concepts: Bottom-up calculation

3. **Same Tree** (LeetCode 100)
   - Practice: Preorder traversal comparison
   - Concepts: Simultaneous traversal of two trees

### Intermediate Level
4. **Binary Tree Level Order Traversal** (LeetCode 102)
   - Practice: BFS with queue
   - Concepts: Level-wise processing

5. **Lowest Common Ancestor of BST** (LeetCode 235)
   - Practice: BST properties
   - Concepts: Optimization using BST characteristics

6. **Validate Binary Search Tree** (LeetCode 98)
   - Practice: Inorder traversal or range checking
   - Concepts: BST validation, multiple approaches

7. **Serialize and Deserialize Binary Tree** (LeetCode 297)
   - Practice: Preorder traversal, string manipulation
   - Concepts: Tree encoding/decoding, delimiter handling

### Advanced Level
8. **Binary Tree Maximum Path Sum** (LeetCode 124)
   - Practice: Postorder with global state
   - Concepts: Complex bottom-up calculation

9. **Vertical Order Traversal** (LeetCode 987)
   - Practice: BFS with coordinate tracking
   - Concepts: Multi-dimensional sorting, hashmap usage

10. **Morris Inorder Traversal** (No specific LeetCode number)
    - Practice: O(1) space traversal
    - Concepts: Threaded binary tree, space optimization

### Bonus: Comprehensive Problem
11. **All Nodes Distance K in Binary Tree** (LeetCode 863)
    - Practice: Tree as graph, BFS from arbitrary node
    - Concepts: Parent pointers, bidirectional traversal

## Common Mistakes

### 1. Confusing Traversal Orders
```python
# ❌ Wrong: Mixing up traversal orders
def confusedTraversal(root):
    if not root:
        return

    # Trying to do inorder but processing root first (this is preorder!)
    result.append(root.val)  # Processing too early
    confusedTraversal(root.left)
    confusedTraversal(root.right)

# ✅ Correct: Clear about what order you're using
def correctInorder(root, result):
    if not root:
        return

    correctInorder(root.left, result)   # Left first
    result.append(root.val)             # Then root
    correctInorder(root.right, result)  # Then right
```

### 2. Not Handling Empty Tree
```python
# ❌ Wrong: Assuming tree exists
def buggyCode(root):
    result = [root.val]  # Crash if root is None!
    # ...

# ✅ Correct: Always check for None
def safeCode(root):
    if not root:
        return []

    result = [root.val]
    # ...
```

### 3. Forgetting to Return Updated Root
```python
# ❌ Wrong: Modifying tree but not returning
def buggyDelete(root, val):
    if not root:
        return None

    if root.val == val:
        return root.right  # Return new root

    buggyDelete(root.left, val)  # Bug: not updating root.left!
    return root

# ✅ Correct: Always update and return
def correctDelete(root, val):
    if not root:
        return None

    if root.val == val:
        return root.right

    root.left = correctDelete(root.left, val)  # Update left
    root.right = correctDelete(root.right, val)  # Update right
    return root
```

### 4. Using Wrong Data Structure for BFS
```python
# ❌ Wrong: Using list as queue (inefficient)
def slowBFS(root):
    queue = [root]
    while queue:
        node = queue.pop(0)  # O(n) operation! Bad!
        # ...

# ✅ Correct: Use deque for O(1) popleft
from collections import deque

def fastBFS(root):
    queue = deque([root])
    while queue:
        node = queue.popleft()  # O(1) operation!
        # ...
```

### 5. Not Tracking Level in Level Order
```python
# ❌ Wrong: Can't separate levels
def wrongLevelOrder(root):
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        node = queue.popleft()
        result.append(node.val)  # All values in one list!

        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)

    return result  # Returns flat list, not list of levels

# ✅ Correct: Track level size
def correctLevelOrder(root):
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)  # Key: track current level size
        current_level = []

        for _ in range(level_size):  # Process entire level
            node = queue.popleft()
            current_level.append(node.val)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        result.append(current_level)  # Add level as separate list

    return result
```

### 6. Incorrect BST Validation
```python
# ❌ Wrong: Only checking immediate children
def wrongValidation(root):
    if not root:
        return True

    # Bug: Only checks immediate children, not entire subtree
    if root.left and root.left.val >= root.val:
        return False
    if root.right and root.right.val <= root.val:
        return False

    return wrongValidation(root.left) and wrongValidation(root.right)

# Problem: Tree like this passes but is invalid BST:
#       5
#      / \
#     3   7
#    / \
#   1   6  <- 6 > 5, violates BST property!

# ✅ Correct: Use range validation
def correctValidation(root, min_val=float('-inf'), max_val=float('inf')):
    if not root:
        return True

    # Check if current value is within valid range
    if root.val <= min_val or root.val >= max_val:
        return False

    # Left subtree: all values must be < root.val
    # Right subtree: all values must be > root.val
    return (correctValidation(root.left, min_val, root.val) and
            correctValidation(root.right, root.val, max_val))
```

### 7. Modifying Tree During Iteration
```python
# ❌ Wrong: Modifying tree while iterating
def dangerousIteration(root):
    if not root:
        return

    stack = [root]
    while stack:
        node = stack.pop()

        # Danger: Modifying tree structure while iterating
        if node.left:
            node.left = None  # Could lose references!
            stack.append(node.left)  # Appending None!
        # ...

# ✅ Correct: Be careful with modifications
def safeIteration(root):
    if not root:
        return

    stack = [root]
    while stack:
        node = stack.pop()

        # Save references before modifying
        left_child = node.left
        right_child = node.right

        # Now safe to modify
        if left_child:
            stack.append(left_child)
        if right_child:
            stack.append(right_child)
```

### 8. Not Considering Unbalanced Trees
```python
# ❌ Wrong: Assuming tree is balanced
def assumingBalanced(root):
    # Using recursion without considering depth
    # For skewed tree with 10,000 nodes, this will
    # cause stack overflow!
    if not root:
        return 0
    return 1 + max(assumingBalanced(root.left),
                   assumingBalanced(root.right))

# ✅ Correct: Use iterative for deep trees
def handleUnbalanced(root):
    if not root:
        return 0

    max_depth = 0
    stack = [(root, 1)]

    while stack:
        node, depth = stack.pop()
        max_depth = max(max_depth, depth)

        if node.left:
            stack.append((node.left, depth + 1))
        if node.right:
            stack.append((node.right, depth + 1))

    return max_depth
```

---

## Summary

**Tree Traversals** are fundamental to working with hierarchical data. Master these key points:

1. **Choose the right traversal** for your problem:
   - Inorder → sorted order for BST
   - Preorder → top-down, copying, serialization
   - Postorder → bottom-up, deletion, calculating from children
   - Level Order → level-wise, shortest path

2. **Understand time/space trade-offs**:
   - Recursive: cleaner but O(h) space
   - Iterative: more control, same space but explicit stack
   - Morris: O(1) space but complex and modifies tree

3. **Always handle edge cases**: empty tree, single node, skewed trees, negative values

4. **Choose DFS vs BFS** based on tree shape and where solution likely exists

5. **Practice both recursive and iterative** approaches for flexibility

Master tree traversals and you'll handle any tree problem with confidence!
