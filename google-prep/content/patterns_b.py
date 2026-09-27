"""Patterns 7-12: linked lists, trees, BSTs, heaps, intervals, greedy."""

LIST_HELPERS = '''
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def build(values):
    dummy = ListNode()
    tail = dummy
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next

def to_list(head):
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out
'''

TREE_HELPERS = '''
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def build(values):
    """Build a tree from LeetCode-style level order, e.g. [3, 9, 20, None, None, 15, 7]."""
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root

def find(root, val):
    if not root or root.val == val:
        return root
    return find(root.left, val) or find(root.right, val)
'''

LINKED = {
    "id": "linked-lists",
    "nav": "Linked lists",
    "title": "Linked lists",
    "tagline": "Careful pointer surgery. A dummy head and a fast/slow pair solve most of these.",
    "plain": """
<p>A linked list is a chain of nodes where each node knows only the next one. You can't jump to the middle; you have to walk. The problems test whether you can rewire <code>next</code> pointers without losing part of the chain.</p>
<p>Three tricks cover almost everything:</p>
<ul>
<li><b>Dummy head:</b> a fake node before the real head, so removing or inserting at the front needs no special case.</li>
<li><b>Fast and slow pointers:</b> one moves two steps, one moves one. When fast reaches the end, slow is in the middle. If there's a loop, they eventually meet.</li>
<li><b>Reverse in place:</b> walk the list, flipping each arrow backwards, remembering the next node before you break the link.</li>
</ul>
<div class="analogy"><b>Picture it:</b> a scavenger hunt where each clue only tells you where the next clue is. If you drop a clue before reading it, the rest of the hunt is lost. So always save <code>next</code> before you change it.</div>
""",
    "signals": [
        "The input is a <code>ListNode</code>",
        "Find the middle, the k-th from the end, or detect a cycle",
        "Reverse all or part of a list; reorder in place",
        "Merge sorted lists",
    ],
    "pitfalls": [
        "Losing the rest of the list by overwriting <code>node.next</code> before saving it",
        "Forgetting to set the new tail's <code>next</code> to <code>None</code> (creates a cycle)",
        "Special-casing the head instead of using a dummy node",
        "Not testing lists of length 0, 1 and 2",
    ],
    "template": LIST_HELPERS + '''
def reverse(head):
    prev = None
    while head:
        nxt = head.next          # 1. save the rest
        head.next = prev         # 2. flip the arrow
        prev = head              # 3. step forward
        head = nxt
    return prev

def middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow                  # second middle for even lengths

def has_cycle(head) -> bool:
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            return True
    return False

assert to_list(reverse(build([1, 2, 3]))) == [3, 2, 1]
assert middle(build([1, 2, 3, 4, 5])).val == 3
''',
    "complexity": "O(n) time, O(1) extra space for pointer rewiring.",
    "problems": [
        {
            "name": "Reverse Linked List",
            "lc": 206,
            "level": "E",
            "prompt": "<p>Reverse a singly linked list, both iteratively and recursively.</p><pre>1 → 2 → 3 → 4  becomes  4 → 3 → 2 → 1</pre>",
            "hint": "Three variables: prev, current, next.",
            "idea": "<p>Iterative: flip each arrow one node at a time. Recursive: reverse the rest of the list first, then hook the current node onto the end of the reversed part. Know both; interviewers like to ask for the other one.</p>",
            "code": LIST_HELPERS + '''
def reverse_iterative(head):
    prev = None
    while head:
        head.next, prev, head = prev, head, head.next
    return prev

def reverse_recursive(head):
    if not head or not head.next:
        return head
    new_head = reverse_recursive(head.next)
    head.next.next = head        # the node after me now points back to me
    head.next = None
    return new_head

assert to_list(reverse_iterative(build([1, 2, 3, 4]))) == [4, 3, 2, 1]
assert to_list(reverse_recursive(build([1, 2, 3, 4]))) == [4, 3, 2, 1]
assert reverse_iterative(None) is None
''',
            "complexity": "O(n) time. Iterative O(1) space, recursive O(n) stack.",
        },
        {
            "name": "Remove Nth Node From End",
            "lc": 19,
            "level": "M",
            "prompt": "<p>Remove the n-th node from the end in one pass.</p><pre>[1,2,3,4,5], n = 2  →  [1,2,3,5]</pre>",
            "hint": "Give one pointer an n-step head start.",
            "idea": "<p>Start two pointers at a dummy node. Move <code>fast</code> n + 1 steps ahead. Then move both until <code>fast</code> falls off the end. <code>slow</code> now sits just before the node to remove. The dummy handles removing the real head.</p>",
            "code": LIST_HELPERS + '''
def remove_nth_from_end(head, n):
    dummy = ListNode(0, head)
    slow = fast = dummy
    for _ in range(n + 1):
        fast = fast.next
    while fast:
        slow, fast = slow.next, fast.next
    slow.next = slow.next.next
    return dummy.next

assert to_list(remove_nth_from_end(build([1, 2, 3, 4, 5]), 2)) == [1, 2, 3, 5]
assert to_list(remove_nth_from_end(build([1]), 1)) == []
assert to_list(remove_nth_from_end(build([1, 2]), 2)) == [2]
''',
            "complexity": "O(n) time, O(1) space.",
        },
        {
            "name": "Reorder List",
            "lc": 143,
            "level": "M",
            "prompt": "<p>Reorder <code>L0 → L1 → … → Ln</code> into <code>L0 → Ln → L1 → Ln−1 → …</code> in place.</p><pre>[1,2,3,4,5]  →  [1,5,2,4,3]</pre>",
            "hint": "This is three easy problems in a row.",
            "idea": "<p>(1) Find the middle with fast/slow. (2) Cut the list there and reverse the second half. (3) Weave the two halves together, one node from each. Combining small known pieces like this is exactly what Google wants to see.</p>",
            "code": LIST_HELPERS + '''
def reorder_list(head) -> None:
    if not head:
        return
    slow = fast = head                        # 1. find the middle
    while fast.next and fast.next.next:
        slow, fast = slow.next, fast.next.next
    second, slow.next = slow.next, None       # 2. cut and reverse
    prev = None
    while second:
        second.next, prev, second = prev, second, second.next
    first, second = head, prev                # 3. weave
    while second:
        n1, n2 = first.next, second.next
        first.next, second.next = second, n1
        first, second = n1, n2

h = build([1, 2, 3, 4, 5]); reorder_list(h); assert to_list(h) == [1, 5, 2, 4, 3]
h = build([1, 2, 3, 4]);    reorder_list(h); assert to_list(h) == [1, 4, 2, 3]
h = build([1]);             reorder_list(h); assert to_list(h) == [1]
''',
            "complexity": "O(n) time, O(1) space.",
        },
        {
            "name": "Reverse Nodes in k-Group",
            "lc": 25,
            "level": "H",
            "prompt": "<p>Reverse the list k nodes at a time. A final group shorter than k stays as is.</p><pre>[1,2,3,4,5], k = 2  →  [2,1,4,3,5]</pre>",
            "hint": "Check that k nodes exist, reverse exactly those, then reconnect both ends of the group.",
            "idea": "<p>Keep <code>group_prev</code>, the node just before the current group (start at a dummy). Walk k steps to find the group's last node; if you run out, stop. Reverse the group, pointing its first node at the node after the group. Then link <code>group_prev</code> to the new front, and the old first node becomes the next <code>group_prev</code>.</p>",
            "code": LIST_HELPERS + '''
def reverse_k_group(head, k):
    dummy = ListNode(0, head)
    group_prev = dummy
    while True:
        kth = group_prev
        for _ in range(k):                    # is there a full group?
            kth = kth.next
            if not kth:
                return dummy.next
        group_next = kth.next
        prev, cur = group_next, group_prev.next
        while cur is not group_next:          # reverse this group
            cur.next, prev, cur = prev, cur, cur.next
        old_first = group_prev.next
        group_prev.next = kth                 # kth is the new front
        group_prev = old_first                # old front is now the tail

assert to_list(reverse_k_group(build([1, 2, 3, 4, 5]), 2)) == [2, 1, 4, 3, 5]
assert to_list(reverse_k_group(build([1, 2, 3, 4, 5]), 3)) == [3, 2, 1, 4, 5]
assert to_list(reverse_k_group(build([1, 2]), 1)) == [1, 2]
''',
            "complexity": "O(n) time, O(1) space.",
        },
    ],
}

TREES = {
    "id": "trees",
    "nav": "Binary trees",
    "title": "Binary trees: DFS and BFS",
    "tagline": "Ask each child for an answer, combine them at the parent. Or sweep level by level with a queue.",
    "plain": """
<p>Almost every tree problem is solved by one of two walks:</p>
<ul>
<li><b>Depth-first (DFS), usually recursive:</b> write a function that solves the problem for a node <i>assuming</i> it already has the answers for its left and right subtrees. Handle the empty tree as the base case. Trust the recursion.</li>
<li><b>Breadth-first (BFS), with a queue:</b> visit the tree level by level. Use it when the question mentions levels, depth-by-depth views, or the nearest something.</li>
</ul>
<p>A useful question to ask for DFS: <b>what does each node need to tell its parent?</b> Height? Sum? Whether it's balanced? Sometimes the value you return upward (e.g. the best single path) differs from the global answer you track (e.g. the best path through this node).</p>
<div class="analogy"><b>Picture it:</b> a company org chart. To count all employees, each manager asks each direct report "how many people are under you?", adds them up, adds one for themselves, and reports to their own boss.</div>
""",
    "signals": [
        "The input is a <code>TreeNode</code> root",
        "Height, depth, diameter, balanced, paths from root to leaf",
        "\"Level order\", \"right side view\", \"zigzag\", \"minimum depth\" (BFS)",
        "Lowest common ancestor",
        "Turning a tree into a string and back",
    ],
    "pitfalls": [
        "Missing the <code>None</code> base case",
        "Mixing up \"return value to the parent\" with \"global best answer\"",
        "Recursion depth over 1000 on a skewed tree (mention the iterative version)",
        "Forgetting a node can have one child: <i>minimum</i> depth must ignore missing children",
    ],
    "template": TREE_HELPERS + '''
def height(node) -> int:
    """DFS: answer = combine(answer(left), answer(right))."""
    if not node:
        return 0
    return 1 + max(height(node.left), height(node.right))

def level_order(root) -> list[list[int]]:
    """BFS: process one whole level per outer loop iteration."""
    if not root:
        return []
    levels, queue = [], deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):           # exactly this level's nodes
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        levels.append(level)
    return levels

def inorder_iterative(root) -> list[int]:
    out, stack, node = [], [], root
    while stack or node:
        while node:                           # go left as far as possible
            stack.append(node)
            node = node.left
        node = stack.pop()
        out.append(node.val)
        node = node.right
    return out

t = build([3, 9, 20, None, None, 15, 7])
assert height(t) == 3
assert level_order(t) == [[3], [9, 20], [15, 7]]
assert inorder_iterative(t) == [9, 3, 15, 20, 7]
''',
    "complexity": "O(n) time. Space O(h) for DFS (h = height) and O(width) for BFS.",
    "problems": [
        {
            "name": "Diameter of Binary Tree",
            "lc": 543,
            "level": "E",
            "prompt": "<p>Return the number of edges on the longest path between any two nodes. The path may skip the root.</p><pre>[1,2,3,4,5]  →  3   (4 → 2 → 1 → 3)</pre>",
            "hint": "The longest path through a node = height(left) + height(right).",
            "idea": "<p>Compute heights with DFS. At every node, the longest path that bends there is <code>left_height + right_height</code>; keep the maximum in an outer variable. Return the height upward. This \"return one thing, track another\" trick is the key to many tree problems.</p>",
            "code": TREE_HELPERS + '''
def diameter_of_binary_tree(root) -> int:
    best = 0
    def height(node):
        nonlocal best
        if not node:
            return 0
        left, right = height(node.left), height(node.right)
        best = max(best, left + right)        # path bending at this node
        return 1 + max(left, right)           # what the parent needs
    height(root)
    return best

assert diameter_of_binary_tree(build([1, 2, 3, 4, 5])) == 3
assert diameter_of_binary_tree(build([1, 2])) == 1
assert diameter_of_binary_tree(None) == 0
''',
            "complexity": "O(n) time, O(h) space.",
        },
        {
            "name": "Binary Tree Right Side View",
            "lc": 199,
            "level": "M",
            "hot": True,
            "prompt": "<p>Standing on the right of the tree, which values do you see from top to bottom?</p><pre>[1,2,3,None,5,None,4]  →  [1,3,4]</pre>",
            "hint": "The last node of each BFS level.",
            "idea": "<p>Run BFS level by level and record the last node of each level. A DFS alternative: visit right before left, and record a node's value the first time you reach a new depth.</p>",
            "code": TREE_HELPERS + '''
def right_side_view(root) -> list[int]:
    if not root:
        return []
    view, queue = [], deque([root])
    while queue:
        for i in range(len(queue)):
            node = queue.popleft()
            if i == 0:
                view.append(node.val)          # first seen = rightmost
            if node.right:
                queue.append(node.right)       # right child first
            if node.left:
                queue.append(node.left)
    return view

assert right_side_view(build([1, 2, 3, None, 5, None, 4])) == [1, 3, 4]
assert right_side_view(build([1, 2, 3, 4])) == [1, 3, 4]
assert right_side_view(None) == []
''',
            "complexity": "O(n) time, O(width) space.",
        },
        {
            "name": "Lowest Common Ancestor of a Binary Tree",
            "lc": 236,
            "level": "M",
            "hot": True,
            "prompt": "<p>Given two nodes <code>p</code> and <code>q</code> in a binary tree, return their lowest common ancestor: the deepest node that has both below it (a node counts as below itself).</p>",
            "hint": "Ask each subtree: did you find p or q? If both sides say yes, you are the answer.",
            "idea": "<p>DFS returns the node it found (p, q, or their LCA) or None. If the current node is p or q, return it. Otherwise recurse both sides. If both return something, p and q are on different sides, so the current node is the LCA. If only one side returns something, pass it up.</p>",
            "code": TREE_HELPERS + '''
def lowest_common_ancestor(root, p, q):
    if not root or root is p or root is q:
        return root
    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)
    if left and right:
        return root
    return left or right

t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
assert lowest_common_ancestor(t, find(t, 5), find(t, 1)).val == 3
assert lowest_common_ancestor(t, find(t, 5), find(t, 4)).val == 5
assert lowest_common_ancestor(t, find(t, 7), find(t, 8)).val == 3
''',
            "complexity": "O(n) time, O(h) space.",
            "followups": ["Nodes have parent pointers: it becomes \"intersection of two linked lists\".", "Many queries on the same tree: binary lifting gives O(log n) per query."],
        },
        {
            "name": "Binary Tree Maximum Path Sum",
            "lc": 124,
            "level": "H",
            "hot": True,
            "prompt": "<p>A path is any sequence of connected nodes (it doesn't need to pass through the root). Values may be negative. Return the largest path sum.</p><pre>[-10,9,20,None,None,15,7]  →  42   (15 → 20 → 7)</pre>",
            "hint": "Same shape as Diameter. What does a node return to its parent, and what does it record globally?",
            "idea": "<p>Each node returns the best <b>one-sided</b> path going down from it: <code>val + max(0, left, right)</code>. The parent can only extend one side. But the best path <b>bending</b> at the node is <code>val + max(0, left) + max(0, right)</code>; record that globally. Dropping negative branches with <code>max(0, …)</code> handles negative values.</p>",
            "code": TREE_HELPERS + '''
def max_path_sum(root) -> int:
    best = float("-inf")
    def gain(node) -> int:
        nonlocal best
        if not node:
            return 0
        left = max(gain(node.left), 0)        # ignore branches that hurt
        right = max(gain(node.right), 0)
        best = max(best, node.val + left + right)
        return node.val + max(left, right)
    gain(root)
    return best

assert max_path_sum(build([1, 2, 3])) == 6
assert max_path_sum(build([-10, 9, 20, None, None, 15, 7])) == 42
assert max_path_sum(build([-3])) == -3
''',
            "complexity": "O(n) time, O(h) space.",
        },
        {
            "name": "Serialize and Deserialize Binary Tree",
            "lc": 297,
            "level": "H",
            "hot": True,
            "prompt": "<p>Design <code>serialize(root) → str</code> and <code>deserialize(str) → root</code> so any tree survives the round trip.</p>",
            "hint": "Preorder traversal that also writes a marker for every empty child is enough to rebuild the tree uniquely.",
            "idea": "<p>Write values in preorder (node, left, right), using <code>#</code> for None. To rebuild, read tokens in the same order: a <code>#</code> means None; otherwise make a node, then build its left subtree, then its right. An iterator over tokens keeps the position for you.</p>",
            "code": TREE_HELPERS + '''
class Codec:
    def serialize(self, root) -> str:
        out = []
        def dfs(node):
            if not node:
                out.append("#")
                return
            out.append(str(node.val))
            dfs(node.left)
            dfs(node.right)
        dfs(root)
        return ",".join(out)

    def deserialize(self, data: str):
        tokens = iter(data.split(","))
        def build_node():
            tok = next(tokens)
            if tok == "#":
                return None
            node = TreeNode(int(tok))
            node.left = build_node()
            node.right = build_node()
            return node
        return build_node()

codec = Codec()
t = build([1, 2, 3, None, None, 4, 5])
s = codec.serialize(t)
assert s == "1,2,#,#,3,4,#,#,5,#,#"
assert codec.serialize(codec.deserialize(s)) == s
assert codec.deserialize(codec.serialize(None)) is None
''',
            "complexity": "O(n) time and space for both.",
            "followups": ["BST only (LC 449): preorder without # markers is enough, because the value bounds tell you where each subtree ends."],
        },
    ],
}

BST = {
    "id": "bst",
    "nav": "Binary search trees",
    "title": "Binary search trees",
    "tagline": "Left is smaller, right is bigger. An in-order walk visits values in sorted order.",
    "plain": """
<p>A binary search tree (BST) keeps a rule at every node: everything in the left subtree is smaller, everything in the right subtree is bigger. That gives you two superpowers:</p>
<ul>
<li><b>Search like binary search:</b> at each node you know which side to go. O(height) per lookup, which is O(log n) if the tree is balanced.</li>
<li><b>In-order traversal (left, node, right) gives sorted order.</b> Many BST problems become "walk in order and do something".</li>
</ul>
<div class="analogy"><b>Picture it:</b> a "choose your path" book where each page says "if your number is smaller, turn left; bigger, turn right".</div>
<p>Python has no built-in balanced BST. In interviews, a sorted list with <code>bisect</code> or a heap often replaces one. If you truly need one, say you would use a balanced tree (like <code>sortedcontainers.SortedList</code>) and explain its costs.</p>
""",
    "signals": [
        "The input is explicitly a BST",
        "\"k-th smallest\", \"validate\", \"closest value\", \"successor\"",
        "Sorted-order questions on a tree",
    ],
    "pitfalls": [
        "Validating a BST by comparing only a node to its direct children. The rule applies to whole subtrees; pass down lower and upper bounds",
        "Assuming a BST is balanced (a sorted insert order makes it a linked list)",
    ],
    "template": TREE_HELPERS + '''
def search_bst(node, target):
    while node and node.val != target:
        node = node.left if target < node.val else node.right
    return node

def inorder(node):
    """Yields BST values in sorted order, lazily."""
    if node:
        yield from inorder(node.left)
        yield node.val
        yield from inorder(node.right)

t = build([4, 2, 7, 1, 3])
assert search_bst(t, 2).val == 2 and search_bst(t, 5) is None
assert list(inorder(t)) == [1, 2, 3, 4, 7]
''',
    "complexity": "O(h) per search or insert, O(n) for a full walk.",
    "problems": [
        {
            "name": "Search in a Binary Search Tree",
            "lc": 700,
            "level": "E",
            "prompt": "<p>Return the subtree rooted at the node with value <code>val</code>, or None.</p>",
            "hint": "Pick one side at each node.",
            "idea": "<p>Compare the target with the current value and move left or right. No recursion needed.</p>",
            "code": TREE_HELPERS + '''
def search_bst(root, val):
    node = root
    while node:
        if val == node.val:
            return node
        node = node.left if val < node.val else node.right
    return None

t = build([4, 2, 7, 1, 3])
assert search_bst(t, 2).left.val == 1
assert search_bst(t, 5) is None
''',
            "complexity": "O(h) time, O(1) space.",
        },
        {
            "name": "Validate Binary Search Tree",
            "lc": 98,
            "level": "M",
            "hot": True,
            "prompt": "<p>Is the tree a valid BST (strictly smaller on the left, strictly bigger on the right)?</p><pre>[5,4,6,None,None,3,7]  →  False   (3 is in 5's right subtree)</pre>",
            "hint": "Every node must fit inside a (low, high) range inherited from its ancestors.",
            "idea": "<p>Pass an allowed range down the tree. The root can be anything. Going left narrows the upper bound to the parent's value; going right narrows the lower bound. Any node outside its range breaks the rule. Alternative: in-order values must be strictly increasing.</p>",
            "code": TREE_HELPERS + '''
def is_valid_bst(root) -> bool:
    def ok(node, low, high) -> bool:
        if not node:
            return True
        if not (low < node.val < high):
            return False
        return ok(node.left, low, node.val) and ok(node.right, node.val, high)
    return ok(root, float("-inf"), float("inf"))

assert is_valid_bst(build([2, 1, 3]))
assert not is_valid_bst(build([5, 1, 4, None, None, 3, 6]))
assert not is_valid_bst(build([5, 4, 6, None, None, 3, 7]))
assert not is_valid_bst(build([2, 2, 2]))
''',
            "complexity": "O(n) time, O(h) space.",
        },
        {
            "name": "Kth Smallest Element in a BST",
            "lc": 230,
            "level": "M",
            "prompt": "<p>Return the k-th smallest value (1-indexed) in a BST.</p>",
            "hint": "In-order is sorted order. Stop after k steps.",
            "idea": "<p>Do an iterative in-order walk and count. Stop as soon as you pop the k-th node, so you only do O(h + k) work.</p>",
            "code": TREE_HELPERS + '''
def kth_smallest(root, k: int) -> int:
    stack, node = [], root
    while stack or node:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        k -= 1
        if k == 0:
            return node.val
        node = node.right
    raise ValueError("k is larger than the tree")

assert kth_smallest(build([3, 1, 4, None, 2]), 1) == 1
assert kth_smallest(build([5, 3, 6, 2, 4, None, None, 1]), 3) == 3
''',
            "complexity": "O(h + k) time, O(h) space.",
            "followups": ["The tree changes often and you query often: store subtree sizes in each node for O(h) queries."],
        },
        {
            "name": "Lowest Common Ancestor of a BST",
            "lc": 235,
            "level": "M",
            "prompt": "<p>Same as the binary tree LCA, but the tree is a BST. Can you do it without visiting both subtrees?</p>",
            "hint": "If both values are smaller than the node, the answer is on the left.",
            "idea": "<p>From the root: if both p and q are smaller, go left; if both are bigger, go right. Otherwise they split here (or one of them is here), so this node is the LCA.</p>",
            "code": TREE_HELPERS + '''
def lca_bst(root, p, q):
    node = root
    while node:
        if p.val < node.val and q.val < node.val:
            node = node.left
        elif p.val > node.val and q.val > node.val:
            node = node.right
        else:
            return node
    return None

t = build([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5])
assert lca_bst(t, find(t, 2), find(t, 8)).val == 6
assert lca_bst(t, find(t, 2), find(t, 4)).val == 2
assert lca_bst(t, find(t, 3), find(t, 5)).val == 4
''',
            "complexity": "O(h) time, O(1) space.",
        },
    ],
}

HEAPS = {
    "id": "heaps",
    "nav": "Heaps and top-k",
    "title": "Heaps and priority queues",
    "tagline": "Always know the smallest (or largest) item, even while items keep arriving.",
    "plain": """
<p>A heap is a structure that hands you the smallest item in O(1) and lets you add or remove items in O(log n). You don't get full sorted order, just \"what's the most urgent thing right now\". Python's <code>heapq</code> works on a normal list and is a <b>min-heap</b>.</p>
<p>The classic trick for \"top k\": keep a heap of size k. For the k <i>largest</i>, use a <i>min</i>-heap of size k; the smallest of your top k sits on top, ready to be kicked out when something bigger shows up. That's O(n log k) instead of sorting everything.</p>
<div class="analogy"><b>Picture it:</b> a hospital emergency room. Patients arrive in any order, but the most urgent one is always seen next.</div>
""",
    "signals": [
        "\"k largest / smallest / most frequent / closest\"",
        "Merge k sorted lists or streams",
        "Running median, or anything \"from a stream\"",
        "Scheduling: always pick the task that ends first or has highest priority",
        "Shortest path with weights (Dijkstra uses a heap)",
    ],
    "pitfalls": [
        "Forgetting Python's heap is a min-heap (negate values for max)",
        "Pushing objects that can't be compared. Add a tie-breaker: <code>(priority, counter, obj)</code>",
        "Sorting everything (O(n log n)) when a size-k heap (O(n log k)) was expected",
    ],
    "template": '''
import heapq

def k_largest(nums: list[int], k: int) -> list[int]:
    heap = []                              # min-heap holding the best k so far
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)            # drop the smallest of the k+1
    return sorted(heap, reverse=True)

assert k_largest([3, 1, 5, 12, 2, 11], 3) == [12, 11, 5]
''',
    "complexity": "O(n log k) time, O(k) space.",
    "problems": [
        {
            "name": "Kth Largest Element in a Stream",
            "lc": 703,
            "level": "E",
            "prompt": "<p>Build a class whose <code>add(val)</code> returns the k-th largest value seen so far.</p>",
            "hint": "Keep only the k largest values. The smallest of them is the answer.",
            "idea": "<p>Keep a min-heap of at most k values. After each add, trim it to size k. The top of the heap is the k-th largest.</p>",
            "code": '''
import heapq

class KthLargest:
    def __init__(self, k: int, nums: list[int]):
        self.k = k
        self.heap = nums[:]
        heapq.heapify(self.heap)
        while len(self.heap) > k:
            heapq.heappop(self.heap)

    def add(self, val: int) -> int:
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)
        return self.heap[0]

kl = KthLargest(3, [4, 5, 8, 2])
assert [kl.add(x) for x in [3, 5, 10, 9, 4]] == [4, 5, 5, 8, 8]
''',
            "complexity": "O(log k) per add, O(k) space.",
        },
        {
            "name": "Top K Frequent Elements",
            "lc": 347,
            "level": "M",
            "hot": True,
            "prompt": "<p>Return the k most frequent values, in any order. Beat O(n log n).</p><pre>[1,1,1,2,2,3], k = 2  →  [1, 2]</pre>",
            "hint": "Count first. Then either a size-k heap or buckets indexed by frequency.",
            "idea": "<p>Count with <code>Counter</code>. Heap approach: <code>heapq.nlargest(k, counts, key=counts.get)</code> is O(n log k). Bucket approach: a frequency can be at most n, so put each value into bucket[frequency] and read buckets from high to low. That's O(n).</p>",
            "code": '''
from collections import Counter
import heapq

def top_k_frequent(nums: list[int], k: int) -> list[int]:
    counts = Counter(nums)
    return heapq.nlargest(k, counts, key=counts.get)

def top_k_frequent_buckets(nums: list[int], k: int) -> list[int]:
    counts = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for value, freq in counts.items():
        buckets[freq].append(value)
    out = []
    for freq in range(len(buckets) - 1, 0, -1):
        for value in buckets[freq]:
            out.append(value)
            if len(out) == k:
                return out
    return out

assert sorted(top_k_frequent([1, 1, 1, 2, 2, 3], 2)) == [1, 2]
assert sorted(top_k_frequent_buckets([1, 1, 1, 2, 2, 3], 2)) == [1, 2]
assert top_k_frequent_buckets([7], 1) == [7]
''',
            "complexity": "Heap: O(n log k). Buckets: O(n). Both O(n) space.",
        },
        {
            "name": "K Closest Points to Origin",
            "lc": 973,
            "level": "M",
            "prompt": "<p>Return the k points closest to (0, 0).</p><pre>[[3,3],[5,-1],[-2,4]], k = 2  →  [[3,3],[-2,4]]</pre>",
            "hint": "Compare squared distances; no square root needed.",
            "idea": "<p>Keep a max-heap of size k (push negative distances). When the heap grows past k, pop the farthest. What remains are the k closest. Squared distance keeps everything in integers.</p>",
            "code": '''
import heapq

def k_closest(points: list[list[int]], k: int) -> list[list[int]]:
    heap = []                                   # (-dist, x, y): a max-heap
    for x, y in points:
        heapq.heappush(heap, (-(x * x + y * y), x, y))
        if len(heap) > k:
            heapq.heappop(heap)                 # remove the farthest
    return [[x, y] for _, x, y in heap]

assert k_closest([[1, 3], [-2, 2]], 1) == [[-2, 2]]
assert sorted(k_closest([[3, 3], [5, -1], [-2, 4]], 2)) == [[-2, 4], [3, 3]]
''',
            "complexity": "O(n log k) time, O(k) space. Quickselect gives O(n) average.",
        },
        {
            "name": "Merge k Sorted Lists",
            "lc": 23,
            "level": "H",
            "hot": True,
            "prompt": "<p>Merge k sorted linked lists into one sorted list.</p>",
            "hint": "The next output node is the smallest among the k current heads.",
            "idea": "<p>Put the head of each list in a min-heap. Pop the smallest, append it to the output, and push its successor. Store <code>(value, list_index, node)</code> so ties compare the index instead of the nodes (nodes can't be compared).</p>",
            "code": LIST_HELPERS + '''
import heapq

def merge_k_lists(lists):
    heap = [(node.val, i, node) for i, node in enumerate(lists) if node]
    heapq.heapify(heap)
    dummy = tail = ListNode()
    while heap:
        _, i, node = heapq.heappop(heap)
        tail.next = node
        tail = node
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next

lists = [build([1, 4, 5]), build([1, 3, 4]), build([2, 6])]
assert to_list(merge_k_lists(lists)) == [1, 1, 2, 3, 4, 4, 5, 6]
assert merge_k_lists([]) is None
''',
            "complexity": "O(N log k) time for N total nodes, O(k) space.",
        },
        {
            "name": "Find Median from Data Stream",
            "lc": 295,
            "level": "H",
            "hot": True,
            "prompt": "<p>Support <code>add_num(x)</code> and <code>find_median()</code> on a growing stream.</p>",
            "hint": "Keep the smaller half and the larger half in two heaps.",
            "idea": "<p>A max-heap <code>low</code> holds the smaller half; a min-heap <code>high</code> holds the larger half. Keep their sizes equal, or <code>low</code> one bigger. The median is the top of <code>low</code>, or the average of both tops. To add: push into <code>low</code>, move <code>low</code>'s max to <code>high</code>, and if <code>high</code> became bigger, move its min back.</p>",
            "code": '''
import heapq

class MedianFinder:
    def __init__(self):
        self.low = []    # max-heap (negated values): smaller half
        self.high = []   # min-heap: larger half

    def add_num(self, x: int) -> None:
        heapq.heappush(self.low, -x)
        heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def find_median(self) -> float:
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2

mf = MedianFinder()
mf.add_num(1); mf.add_num(2)
assert mf.find_median() == 1.5
mf.add_num(3)
assert mf.find_median() == 2.0
''',
            "complexity": "O(log n) per add, O(1) per median.",
            "followups": ["All numbers are in 0..100: keep 101 counters instead.", "Sliding-window median (LC 480): lazy deletion from both heaps."],
        },
    ],
}

INTERVALS = {
    "id": "intervals",
    "nav": "Intervals",
    "title": "Intervals and sweep line",
    "tagline": "Sort by start time, then walk once. Overlaps become obvious.",
    "plain": """
<p>Interval problems talk about ranges like meetings <code>[start, end]</code>. Almost all of them begin the same way: <b>sort by start</b>. After sorting, an interval can only overlap with the ones right before it, so one pass is enough.</p>
<p>Two intervals <code>[a, b]</code> and <code>[c, d]</code> overlap when <code>a &lt; d and c &lt; b</code>. (Whether touching endpoints count is a question to ask your interviewer.)</p>
<p>For \"how many at the same time\" questions, use a <b>sweep line</b>: turn each interval into a +1 event at its start and a −1 event at its end, sort the events, and keep a running count. Or keep a min-heap of end times.</p>
<div class="analogy"><b>Picture it:</b> a hotel front desk. Guests check in and out through the day. The most rooms you ever need is the highest number of guests in the building at once.</div>
""",
    "signals": [
        "Meetings, bookings, time ranges, calendar slots",
        "Merge overlapping ranges, insert a range, find gaps",
        "\"Minimum rooms / platforms / resources\"",
        "\"Remove the fewest intervals so none overlap\"",
    ],
    "pitfalls": [
        "Forgetting to sort first",
        "Not asking whether <code>[1,2]</code> and <code>[2,3]</code> overlap",
        "Mutating the input's intervals when building the result",
        "For \"max non-overlapping\", sorting by start instead of by end",
    ],
    "template": '''
def merge(intervals: list[list[int]]) -> list[list[int]]:
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:     # overlaps the last one
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged

def max_overlap(intervals: list[list[int]]) -> int:
    """Sweep line: +1 at start, -1 at end. Ends sort before starts at the same time."""
    events = []
    for s, e in intervals:
        events.append((s, 1))
        events.append((e, -1))
    events.sort()                                  # (t, -1) comes before (t, 1)
    best = current = 0
    for _, delta in events:
        current += delta
        best = max(best, current)
    return best

assert merge([[1, 3], [2, 6], [8, 10]]) == [[1, 6], [8, 10]]
assert max_overlap([[0, 30], [5, 10], [15, 20]]) == 2
''',
    "complexity": "O(n log n) for the sort, then O(n).",
    "problems": [
        {
            "name": "Meeting Rooms",
            "lc": 252,
            "level": "E",
            "prompt": "<p>Can one person attend every meeting (no overlaps)?</p><pre>[[0,30],[5,10],[15,20]]  →  False</pre>",
            "hint": "After sorting, only neighbors can clash.",
            "idea": "<p>Sort by start. If any meeting starts before the previous one ends, there's a clash.</p>",
            "code": '''
def can_attend_meetings(intervals: list[list[int]]) -> bool:
    intervals = sorted(intervals)
    for i in range(1, len(intervals)):
        if intervals[i][0] < intervals[i - 1][1]:
            return False
    return True

assert not can_attend_meetings([[0, 30], [5, 10], [15, 20]])
assert can_attend_meetings([[7, 10], [2, 4]])
assert can_attend_meetings([])
''',
            "complexity": "O(n log n) time, O(n) space for the sorted copy.",
        },
        {
            "name": "Merge Intervals",
            "lc": 56,
            "level": "M",
            "hot": True,
            "prompt": "<p>Merge all overlapping intervals.</p><pre>[[1,3],[2,6],[8,10],[15,18]]  →  [[1,6],[8,10],[15,18]]</pre>",
            "hint": "Sort, then compare each interval with the last merged one.",
            "idea": "<p>Sort by start. Keep a result list. If the next interval starts before the last result ends, stretch the last result's end. Otherwise start a new one.</p>",
            "code": '''
def merge(intervals: list[list[int]]) -> list[list[int]]:
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged

assert merge([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
assert merge([[1, 4], [4, 5]]) == [[1, 5]]
assert merge([[1, 4], [2, 3]]) == [[1, 4]]
''',
            "complexity": "O(n log n) time, O(n) space.",
        },
        {
            "name": "Insert Interval",
            "lc": 57,
            "level": "M",
            "prompt": "<p>The list is sorted and non-overlapping. Insert a new interval and merge if needed.</p><pre>[[1,2],[3,5],[6,7],[8,10],[12,16]] + [4,8]  →  [[1,2],[3,10],[12,16]]</pre>",
            "hint": "Three phases: before the new interval, overlapping it, after it.",
            "idea": "<p>Copy intervals that end before the new one starts. Then absorb every interval that overlaps, growing the new interval's start and end. Append it. Copy the rest. No sort needed: O(n).</p>",
            "code": '''
def insert(intervals: list[list[int]], new: list[int]) -> list[list[int]]:
    out, i, n = [], 0, len(intervals)
    start, end = new
    while i < n and intervals[i][1] < start:          # entirely before
        out.append(intervals[i])
        i += 1
    while i < n and intervals[i][0] <= end:           # overlapping
        start = min(start, intervals[i][0])
        end = max(end, intervals[i][1])
        i += 1
    out.append([start, end])
    out.extend(intervals[i:])                         # entirely after
    return out

assert insert([[1, 3], [6, 9]], [2, 5]) == [[1, 5], [6, 9]]
assert insert([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]) == [[1, 2], [3, 10], [12, 16]]
assert insert([], [5, 7]) == [[5, 7]]
''',
            "complexity": "O(n) time, O(n) space.",
        },
        {
            "name": "Meeting Rooms II",
            "lc": 253,
            "level": "M",
            "hot": True,
            "prompt": "<p>What's the minimum number of rooms needed for all meetings?</p><pre>[[0,30],[5,10],[15,20]]  →  2</pre>",
            "hint": "Process meetings by start time. A room is free again when its meeting ends. Which room frees up first?",
            "idea": "<p>Sort by start. Keep a min-heap of end times for rooms in use. For each meeting, if the earliest-ending room is free by now, reuse it (pop). Push this meeting's end. The heap's largest size is the answer.</p>",
            "code": '''
import heapq

def min_meeting_rooms(intervals: list[list[int]]) -> int:
    ends = []                                  # end times of busy rooms
    for start, end in sorted(intervals):
        if ends and ends[0] <= start:
            heapq.heappop(ends)                # reuse the room that freed up
        heapq.heappush(ends, end)
    return len(ends)

assert min_meeting_rooms([[0, 30], [5, 10], [15, 20]]) == 2
assert min_meeting_rooms([[7, 10], [2, 4]]) == 1
assert min_meeting_rooms([[1, 5], [2, 6], [3, 7]]) == 3
''',
            "complexity": "O(n log n) time, O(n) space.",
            "followups": ["Return which room each meeting gets (LC 2402 Meeting Rooms III): two heaps, free rooms and busy rooms."],
        },
        {
            "name": "Employee Free Time",
            "lc": 759,
            "level": "H",
            "prompt": "<p>Each employee has a sorted list of busy intervals. Return the finite intervals when everyone is free.</p><pre>[[[1,3],[6,7]], [[2,4]], [[2,5],[9,12]]]  →  [[5,6],[7,9]]</pre>",
            "hint": "Who owns an interval doesn't matter. Merge everything and look at the gaps.",
            "idea": "<p>Put every busy interval into one list and sort by start. Walk through, tracking the latest end seen so far. When the next interval starts after that end, the gap between them is free time for everyone. (A heap merging the k sorted lists does the same in O(n log k).)</p>",
            "code": '''
def employee_free_time(schedule: list[list[list[int]]]) -> list[list[int]]:
    busy = sorted(iv for person in schedule for iv in person)
    free = []
    latest_end = busy[0][1]
    for start, end in busy[1:]:
        if start > latest_end:
            free.append([latest_end, start])
        latest_end = max(latest_end, end)
    return free

assert employee_free_time([[[1, 2], [5, 6]], [[1, 3]], [[4, 10]]]) == [[3, 4]]
assert employee_free_time([[[1, 3], [6, 7]], [[2, 4]], [[2, 5], [9, 12]]]) == [[5, 6], [7, 9]]
''',
            "complexity": "O(n log n) time, O(n) space.",
        },
    ],
}

GREEDY = {
    "id": "greedy",
    "nav": "Greedy",
    "title": "Greedy algorithms",
    "tagline": "Make the best-looking choice at each step and never look back. Works only when you can argue it's safe.",
    "plain": """
<p>A greedy algorithm builds the answer one step at a time and always takes the choice that looks best right now. It's fast and short, but it's only correct for certain problems. The hard part is convincing yourself (and the interviewer) that the local choice never hurts later.</p>
<p>The usual argument is an <b>exchange argument</b>: \"Suppose the best solution made a different choice here. I can swap it for my choice without making it worse. So my choice is safe.\" If you can't make that argument, and a small counterexample breaks the greedy, switch to dynamic programming.</p>
<div class="analogy"><b>Picture it:</b> giving change with US coins. Always handing over the biggest coin that fits works. But with coins of 1, 3 and 4, making 6 greedily gives 4+1+1 (three coins) when 3+3 (two coins) is better. That's when greedy fails and you need DP.</div>
""",
    "signals": [
        "Scheduling: most tasks done, fewest arrows, fewest resources",
        "\"Can you reach the end?\", \"minimum jumps\"",
        "Problems where sorting by one key makes the choice obvious",
        "An O(n) or O(n log n) answer is expected and DP would be O(n²)",
    ],
    "pitfalls": [
        "Using greedy without checking a small counterexample",
        "Sorting by the wrong key (for interval scheduling, sort by <b>end</b>)",
        "Not being able to explain why it's correct. Always say the exchange argument out loud",
    ],
    "template": '''
def max_non_overlapping(intervals: list[list[int]]) -> int:
    """Classic greedy: always keep the interval that ends first.
    Ending early leaves the most room for everything after."""
    count = 0
    last_end = float("-inf")
    for start, end in sorted(intervals, key=lambda iv: iv[1]):
        if start >= last_end:
            count += 1
            last_end = end
    return count

assert max_non_overlapping([[1, 2], [2, 3], [3, 4], [1, 3]]) == 3
''',
    "complexity": "Usually O(n log n) for a sort plus O(n).",
    "problems": [
        {
            "name": "Assign Cookies",
            "lc": 455,
            "level": "E",
            "prompt": "<p>Child i is happy with a cookie of size at least <code>g[i]</code>. Each child gets at most one cookie. Maximize happy children.</p><pre>g = [1,2], s = [1,2,3]  →  2</pre>",
            "hint": "Give the smallest cookie that works to the least greedy child.",
            "idea": "<p>Sort both. Walk the cookies from small to large; if the current cookie satisfies the current (least demanding) child, pair them. Using a small cookie on an easy child never hurts: a bigger cookie would be wasted there.</p>",
            "code": '''
def find_content_children(g: list[int], s: list[int]) -> int:
    g, s = sorted(g), sorted(s)
    child = 0
    for cookie in s:
        if child < len(g) and cookie >= g[child]:
            child += 1
    return child

assert find_content_children([1, 2, 3], [1, 1]) == 1
assert find_content_children([1, 2], [1, 2, 3]) == 2
''',
            "complexity": "O(n log n + m log m) time.",
        },
        {
            "name": "Jump Game",
            "lc": 55,
            "level": "M",
            "prompt": "<p><code>nums[i]</code> is your maximum jump length from index i. Can you reach the last index from index 0?</p><pre>[2,3,1,1,4]  →  True\n[3,2,1,0,4]  →  False</pre>",
            "hint": "Track the farthest index you can reach so far.",
            "idea": "<p>Walk left to right keeping <code>reach</code>, the farthest index reachable. If you ever stand on an index beyond <code>reach</code>, you're stuck. Otherwise update <code>reach = max(reach, i + nums[i])</code>.</p>",
            "code": '''
def can_jump(nums: list[int]) -> bool:
    reach = 0
    for i, step in enumerate(nums):
        if i > reach:
            return False
        reach = max(reach, i + step)
    return True

assert can_jump([2, 3, 1, 1, 4])
assert not can_jump([3, 2, 1, 0, 4])
assert can_jump([0])
''',
            "complexity": "O(n) time, O(1) space.",
        },
        {
            "name": "Jump Game II",
            "lc": 45,
            "level": "M",
            "hot": True,
            "prompt": "<p>Same setup; the end is reachable. Return the minimum number of jumps.</p><pre>[2,3,1,1,4]  →  2</pre>",
            "hint": "Think BFS by levels: all indices reachable with j jumps form one range.",
            "idea": "<p>Indices reachable with the same number of jumps form a window <code>[start, end]</code>. While scanning that window, compute the farthest reach for the next jump. When you reach the window's end, you must jump: count it and the window becomes everything up to the farthest reach.</p>",
            "code": '''
def jump(nums: list[int]) -> int:
    jumps = 0
    current_end = farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == current_end:            # used up this jump's range
            jumps += 1
            current_end = farthest
    return jumps

assert jump([2, 3, 1, 1, 4]) == 2
assert jump([2, 3, 0, 1, 4]) == 2
assert jump([0]) == 0
''',
            "complexity": "O(n) time, O(1) space.",
        },
        {
            "name": "Gas Station",
            "lc": 134,
            "level": "M",
            "prompt": "<p>Stations in a circle: <code>gas[i]</code> fuel available, <code>cost[i]</code> to drive to the next. Return the start index to complete the loop, or −1.</p><pre>gas = [1,2,3,4,5], cost = [3,4,5,1,2]  →  3</pre>",
            "hint": "If total gas ≥ total cost, a start exists. If you run dry at station j starting from i, no station between i and j works either.",
            "idea": "<p>If total gas is less than total cost, it's impossible. Otherwise, drive from station 0 with a running tank. Whenever the tank goes negative at station i, none of the stations you passed can be the start (each would arrive at i with even less fuel), so restart from i + 1 with an empty tank.</p>",
            "code": '''
def can_complete_circuit(gas: list[int], cost: list[int]) -> int:
    if sum(gas) < sum(cost):
        return -1
    start = tank = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:
            start, tank = i + 1, 0
    return start

assert can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]) == 3
assert can_complete_circuit([2, 3, 4], [3, 4, 3]) == -1
''',
            "complexity": "O(n) time, O(1) space.",
        },
        {
            "name": "Task Scheduler",
            "lc": 621,
            "level": "M",
            "hot": True,
            "prompt": "<p>CPU tasks labeled by letter; the same task needs <code>n</code> idle slots between runs. Return the minimum time to run them all.</p><pre>[\"A\",\"A\",\"A\",\"B\",\"B\",\"B\"], n = 2  →  8   (A B _ A B _ A B)</pre>",
            "hint": "The most frequent task sets the skeleton. How many slots does that skeleton need?",
            "idea": "<p>Let the most frequent task appear <code>f</code> times. It forces <code>f − 1</code> blocks of length <code>n + 1</code>, plus a final block containing every task that also appears <code>f</code> times. Other tasks fill the gaps. If there are more tasks than slots, no idles are needed and the answer is simply the number of tasks.</p>",
            "code": '''
from collections import Counter

def least_interval(tasks: list[str], n: int) -> int:
    counts = Counter(tasks)
    f = max(counts.values())
    tied = sum(1 for c in counts.values() if c == f)
    return max(len(tasks), (f - 1) * (n + 1) + tied)

assert least_interval(["A", "A", "A", "B", "B", "B"], 2) == 8
assert least_interval(["A", "A", "A", "B", "B", "B"], 0) == 6
assert least_interval(["A"] * 6 + list("BCDEFG"), 2) == 16
''',
            "complexity": "O(n) time, O(26) space.",
            "followups": ["Output the actual schedule: a max-heap by remaining count plus a cooldown queue."],
        },
        {
            "name": "Candy",
            "lc": 135,
            "level": "H",
            "prompt": "<p>Children stand in a line with ratings. Each gets at least one candy; a child with a higher rating than a neighbor must get more than that neighbor. Minimum total candies?</p><pre>[1,0,2]  →  5\n[1,2,2]  →  4</pre>",
            "hint": "Handle the left-neighbor rule and the right-neighbor rule in two separate passes.",
            "idea": "<p>Pass 1, left to right: if a child beats the left neighbor, give one more than that neighbor. Pass 2, right to left: if a child beats the right neighbor, make sure they have at least one more than that neighbor (take the max so pass 1's rule still holds). Each pass satisfies one side; the max keeps both.</p>",
            "code": '''
def candy(ratings: list[int]) -> int:
    n = len(ratings)
    c = [1] * n
    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            c[i] = c[i - 1] + 1
    for i in range(n - 2, -1, -1):
        if ratings[i] > ratings[i + 1]:
            c[i] = max(c[i], c[i + 1] + 1)
    return sum(c)

assert candy([1, 0, 2]) == 5
assert candy([1, 2, 2]) == 4
assert candy([1, 3, 4, 5, 2]) == 11
''',
            "complexity": "O(n) time, O(n) space.",
        },
    ],
}

PATTERNS = [LINKED, TREES, BST, HEAPS, INTERVALS, GREEDY]
