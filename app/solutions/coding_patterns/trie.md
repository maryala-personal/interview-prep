# Trie (Prefix Tree) Pattern

## What is a Trie?

### Explain Like I'm 5
Imagine you're organizing your toy collection in a special cabinet. Instead of throwing all toys in one box, you create a path for each toy:
- All toy cars go in drawer "C" → then "A" → then "R" → then "S"
- All toy balls go in drawer "B" → then "A" → then "L" → then "L" → then "S"

Notice how "cars" and "cats" both start with "C" → "A", so they share the same first two drawers! This sharing of common prefixes is exactly what a Trie does with words.

### Technical Definition
A **Trie** (pronounced "try") is a tree-like data structure that stores a dynamic set of strings, where each node represents a single character and paths from root to nodes form strings. The key property is that all descendants of a node share a common prefix represented by that node's path from the root.

**Structure:**
- Each node contains:
  - An array/map of child nodes (typically 26 for lowercase English letters)
  - A boolean flag indicating if this node marks the end of a valid word
- The root is an empty node
- Each path from root to a node represents a prefix
- Paths ending at nodes marked as "end of word" represent complete words

## Real-World Analogy

### Autocomplete Systems
When you type "cat" in a search box:
1. System navigates: root → 'c' → 'a' → 't'
2. From 't' node, it explores all children to find: "category", "catch", "cats", "cattle"
3. All these words share the prefix "cat" and are stored in the same subtree

### Other Real-World Uses:
- **Spell Checkers**: Quickly validate if a word exists in dictionary
- **Phone Contact Search**: Type "Joh" and instantly see "John", "Johnny", "Johnson"
- **IP Routing Tables**: Longest prefix matching for network routing
- **DNA Sequence Analysis**: Finding common genetic patterns

## When to Use

### Clear Signals:
✅ **Prefix-based operations**: "Find all words starting with..."
✅ **Autocomplete/Type-ahead**: Suggesting words as user types
✅ **Word validation**: "Does this word exist in dictionary?"
✅ **Longest common prefix**: Finding shared prefixes across words
✅ **Word search in a grid**: Searching multiple words simultaneously
✅ **Spell checking**: Finding words with specific prefixes
✅ **Lexicographic ordering**: Words are naturally sorted in Trie

### Keywords in Problem:
- "prefix"
- "autocomplete"
- "dictionary"
- "word search"
- "all words starting with"
- "valid words"
- "spell checker"

## The Problem

### Classic Example: Implement Trie (Prefix Tree)

**Problem Statement:**
Implement a trie with `insert`, `search`, and `startsWith` methods.

```
Trie trie = new Trie();
trie.insert("apple");
trie.search("apple");   // returns true
trie.search("app");     // returns false
trie.startsWith("app"); // returns true
trie.insert("app");
trie.search("app");     // returns true
```

**Requirements:**
- `insert(word)`: Insert word into the trie
- `search(word)`: Return true if word is in the trie
- `startsWith(prefix)`: Return true if any word in trie starts with prefix

## Brute Force Approach

### Using a Set/List for Word Storage

```python
class NaiveTrie:
    """Brute force approach using a set to store complete words."""

    def __init__(self):
        # Simply store all words in a set
        self.words = set()

    def insert(self, word: str) -> None:
        """Add word to set - O(1) average case"""
        self.words.add(word)

    def search(self, word: str) -> bool:
        """Check if exact word exists - O(1) average case"""
        return word in self.words

    def startsWith(self, prefix: str) -> bool:
        """Check if any word starts with prefix - O(N*M) where N=number of words, M=word length"""
        # Must iterate through ALL words to check prefix
        for word in self.words:
            if word.startswith(prefix):
                return True
        return False

# Usage
naive = NaiveTrie()
naive.insert("apple")
naive.insert("app")
naive.insert("application")
print(naive.startsWith("app"))  # O(N*M) - checks all 3 words!
```

### Problems with Brute Force:
1. **Prefix search is slow**: O(N*M) where N = total words, M = average word length
2. **No prefix sharing**: "apple", "app", "application" store "app" characters 3 times
3. **Memory waste**: For dictionary with 100,000 words averaging 8 chars = 800KB minimum
4. **No early termination**: Can't stop search when prefix doesn't match

## Optimized Solution

### Trie Implementation with TrieNode

```python
class TrieNode:
    """
    Represents a single node in the Trie.
    Each node can have up to 26 children (for lowercase English letters).
    """
    def __init__(self):
        # Dictionary mapping character -> TrieNode
        # Could also use array of size 26: [None] * 26
        self.children = {}

        # Marks if this node represents end of a valid word
        self.is_end_of_word = False


class Trie:
    """
    Optimized Trie implementation for efficient prefix operations.
    """

    def __init__(self):
        """Initialize with empty root node."""
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        """
        Insert a word into the trie.
        Time: O(M) where M = length of word
        Space: O(M) in worst case (no shared prefixes)
        """
        node = self.root

        # Traverse/create path for each character
        for char in word:
            # If character path doesn't exist, create new node
            if char not in node.children:
                node.children[char] = TrieNode()

            # Move to child node
            node = node.children[char]

        # Mark the last node as end of word
        node.is_end_of_word = True

    def search(self, word: str) -> bool:
        """
        Search for exact word in trie.
        Time: O(M) where M = length of word
        Space: O(1)
        """
        node = self.root

        # Try to follow path of word
        for char in word:
            if char not in node.children:
                # Path doesn't exist -> word not in trie
                return False
            node = node.children[char]

        # Path exists, but is it marked as complete word?
        return node.is_end_of_word

    def startsWith(self, prefix: str) -> bool:
        """
        Check if any word in trie starts with given prefix.
        Time: O(M) where M = length of prefix
        Space: O(1)
        """
        node = self.root

        # Try to follow path of prefix
        for char in prefix:
            if char not in node.children:
                # Prefix path doesn't exist
                return False
            node = node.children[char]

        # If we successfully followed the path, prefix exists
        return True

    def delete(self, word: str) -> bool:
        """
        Delete a word from trie (bonus method).
        Returns True if word was deleted, False if word wasn't in trie.
        Time: O(M) where M = length of word
        """
        def _delete_helper(node: TrieNode, word: str, index: int) -> bool:
            """
            Recursive helper to delete word.
            Returns True if current node should be deleted.
            """
            # Base case: reached end of word
            if index == len(word):
                # Word doesn't exist
                if not node.is_end_of_word:
                    return False

                # Unmark as end of word
                node.is_end_of_word = False

                # Delete node only if it has no children
                return len(node.children) == 0

            char = word[index]

            # Character path doesn't exist
            if char not in node.children:
                return False

            # Recursively delete in child
            should_delete_child = _delete_helper(node.children[char], word, index + 1)

            # Delete child node if needed
            if should_delete_child:
                del node.children[char]

                # Delete current node if:
                # 1. It's not end of another word, AND
                # 2. It has no other children
                return not node.is_end_of_word and len(node.children) == 0

            return False

        return _delete_helper(self.root, word, 0)


# Usage Example
trie = Trie()

# Insert words
trie.insert("apple")
trie.insert("app")
trie.insert("application")
trie.insert("apply")
trie.insert("banana")

# Search operations
print(trie.search("apple"))        # True
print(trie.search("app"))          # True
print(trie.search("appl"))         # False (not marked as complete word)

# Prefix operations
print(trie.startsWith("app"))      # True (apple, app, application, apply)
print(trie.startsWith("ban"))      # True (banana)
print(trie.startsWith("cat"))      # False

# Visualization of the Trie structure:
#
#                    root
#                   /    \
#                  a      b
#                 /        \
#                p          a
#               /            \
#              p              n
#             /|\              \
#            * l y              a
#             / |                \
#            e  i                 n
#           /   |                  \
#          *    c                   a
#               |                    \
#               a                     *
#               |
#               t
#               |
#               i
#               |
#               o
#               |
#               n
#               |
#               *
#
# * = is_end_of_word = True
```

### Advanced Example: Word Search II

**Problem:** Given a 2D board and a list of words, find all words in the board.

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.word = None  # Store complete word at end node (optimization)


class Solution:
    def findWords(self, board: list[list[str]], words: list[str]) -> list[str]:
        """
        Use Trie + DFS to efficiently search multiple words.

        Why Trie is better than searching each word individually:
        - With N words, naive DFS would be O(N * M * 4^L) where M=cells, L=word length
        - With Trie, we share prefix exploration: O(M * 4^L)
        - If 100 words start with "app", we only explore "app" path once!
        """
        # Build Trie from word list
        root = TrieNode()
        for word in words:
            node = root
            for char in word:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
            node.word = word  # Store word at terminal node

        rows, cols = len(board), len(board[0])
        result = []

        def dfs(row: int, col: int, node: TrieNode):
            """DFS from current cell, following Trie paths."""
            # Get current character
            char = board[row][col]

            # Check if this character exists in Trie
            if char not in node.children:
                return

            # Move to next Trie node
            next_node = node.children[char]

            # Found a complete word!
            if next_node.word:
                result.append(next_node.word)
                next_node.word = None  # Avoid duplicates

            # Mark cell as visited
            board[row][col] = '#'

            # Explore all 4 directions
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < rows and 0 <= new_col < cols and board[new_row][new_col] != '#':
                    dfs(new_row, new_col, next_node)

            # Restore cell
            board[row][col] = char

            # Optimization: Remove leaf nodes to prune Trie
            if not next_node.children:
                del node.children[char]

        # Start DFS from each cell
        for i in range(rows):
            for j in range(cols):
                dfs(i, j, root)

        return result


# Example usage
board = [
    ['o','a','a','n'],
    ['e','t','a','e'],
    ['i','h','k','r'],
    ['i','f','l','v']
]
words = ["oath","pea","eat","rain","hklf","hf"]

sol = Solution()
print(sol.findWords(board, words))  # Output: ["oath","eat","hklf"]
```

## Time & Space Complexity Analysis

### Comparison Table

| Operation | Brute Force (Set) | Trie |
|-----------|------------------|------|
| **Insert word** | O(M) - hash/add | O(M) - traverse path |
| **Search word** | O(M) - hash lookup | O(M) - traverse path |
| **Prefix search** | O(N*M) - check all words | O(P) - traverse prefix only |
| **Space** | O(N*M) - store all words | O(ALPHABET_SIZE * N * M) worst case, but shares prefixes |

Where:
- M = average word length
- N = number of words
- P = prefix length

### Detailed Trie Complexity

**Time Complexity:**
- `insert(word)`: **O(M)** - visit each character once
- `search(word)`: **O(M)** - visit each character once
- `startsWith(prefix)`: **O(P)** - visit each prefix character once
- `delete(word)`: **O(M)** - visit each character once

**Space Complexity:**
- **Worst Case**: O(ALPHABET_SIZE × N × M)
  - When: No words share prefixes (all completely different)
  - Example: 1000 random 10-char words ≈ 26 × 1000 × 10 = 260,000 node pointers

- **Best Case**: O(N × M)
  - When: All words share maximum prefixes
  - Example: "a", "ab", "abc", "abcd" → only 10 nodes total

- **Average Case**: O(N × M)
  - Natural language has significant prefix overlap
  - English dictionary: ~170,000 words, but only ~1M nodes (not 44M)

### Why Trie Wins for Prefix Operations

**Example:** Dictionary with 100,000 words, searching prefix "pre"

| Approach | Operations |
|----------|-----------|
| Set | Must check all 100,000 words: `100,000 × 3 = 300,000` comparisons |
| Trie | Navigate 3 nodes: `3` comparisons |

**Speedup: 100,000×**

## Variations

### 1. Trie with Frequency Count

Track how many times each word was inserted (useful for autocomplete ranking).

```python
class TrieNodeWithFrequency:
    def __init__(self):
        self.children = {}
        self.frequency = 0  # How many times word was inserted
        self.word = None

class TrieWithFrequency:
    def __init__(self):
        self.root = TrieNodeWithFrequency()

    def insert(self, word: str) -> None:
        """Insert word and increment its frequency."""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNodeWithFrequency()
            node = node.children[char]

        node.word = word
        node.frequency += 1  # Track frequency

    def get_top_k_words(self, prefix: str, k: int) -> list[tuple[str, int]]:
        """Get top K most frequent words with given prefix."""
        # Navigate to prefix
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        # Collect all words under this prefix with frequencies
        words_with_freq = []

        def dfs(node: TrieNodeWithFrequency):
            if node.word:
                words_with_freq.append((node.word, node.frequency))
            for child in node.children.values():
                dfs(child)

        dfs(node)

        # Return top K by frequency
        words_with_freq.sort(key=lambda x: x[1], reverse=True)
        return words_with_freq[:k]

# Usage
trie = TrieWithFrequency()
trie.insert("apple")
trie.insert("apple")
trie.insert("application")
trie.insert("app")
trie.insert("app")
trie.insert("app")

print(trie.get_top_k_words("app", 2))
# Output: [('app', 3), ('apple', 2)]
```

### 2. Compressed Trie (Radix Tree/Patricia Trie)

Merge chains of single-child nodes to save space.

```python
class CompressedTrieNode:
    """Node that can store edge labels (multi-character strings)."""
    def __init__(self):
        self.children = {}  # maps edge_label -> child_node
        self.is_end = False

class CompressedTrie:
    """
    Instead of one node per character, store strings on edges.

    Regular Trie for ["test", "testing"]:
        root -> t -> e -> s -> t -> i -> n -> g

    Compressed Trie:
        root -> "test" -> "ing"
    """
    def __init__(self):
        self.root = CompressedTrieNode()

    # Implementation would merge single-child chains
    # More complex but saves space for sparse tries
```

### 3. Trie + DFS for Complex Queries

Combine Trie with DFS for pattern matching, wildcards, etc.

```python
class WordDictionary:
    """Support adding words and searching with '.' wildcard."""

    def __init__(self):
        self.root = TrieNode()

    def addWord(self, word: str) -> None:
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, word: str) -> bool:
        """Search with '.' matching any character."""
        def dfs(node: TrieNode, index: int) -> bool:
            # Reached end of word
            if index == len(word):
                return node.is_end_of_word

            char = word[index]

            # Wildcard: try all possible children
            if char == '.':
                for child in node.children.values():
                    if dfs(child, index + 1):
                        return True
                return False

            # Regular character
            if char not in node.children:
                return False
            return dfs(node.children[char], index + 1)

        return dfs(self.root, 0)

# Usage
wd = WordDictionary()
wd.addWord("bad")
wd.addWord("dad")
wd.addWord("mad")

print(wd.search("pad"))    # False
print(wd.search("bad"))    # True
print(wd.search(".ad"))    # True (matches bad, dad, mad)
print(wd.search("b.."))    # True (matches bad)
```

### 4. Ternary Search Trie (TST)

Space-efficient alternative using three-way branching.

```python
class TSTNode:
    """Each node has left, middle, right children."""
    def __init__(self, char):
        self.char = char           # Character at this node
        self.left = None          # Lesser characters
        self.middle = None        # Next character in word
        self.right = None         # Greater characters
        self.is_end = False

class TernarySearchTrie:
    """
    More space-efficient than standard Trie.
    Instead of 26-way branching, use 3-way branching with BST-like structure.

    Good for: Large alphabets (Unicode), memory-constrained systems
    """
    def __init__(self):
        self.root = None

    # Each node stores one char and has 3 children
    # Space: O(N) nodes instead of O(ALPHABET_SIZE * N)
```

## Pro Tips for Senior Engineers

### 1. Array vs HashMap for Children

```python
# HashMap approach (flexible, any character set)
class TrieNode:
    def __init__(self):
        self.children = {}  # Can store any character

# Array approach (faster, only lowercase letters)
class TrieNodeArray:
    def __init__(self):
        self.children = [None] * 26  # Fixed size
        self.is_end = False

    def get_index(self, char: str) -> int:
        return ord(char) - ord('a')

    def insert_char(self, char: str):
        idx = self.get_index(char)
        if self.children[idx] is None:
            self.children[idx] = TrieNodeArray()
        return self.children[idx]

# Array is ~2x faster for lookup but wastes space if sparse
```

### 2. Space Optimization: Store Word at End Node

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.word = None  # Instead of just is_end_of_word = True

# Benefit: No need to reconstruct word when searching
# Trade-off: More memory (storing full words)
```

### 3. Early Termination with Trie Pruning

In Word Search II, delete found words to avoid duplicates and improve performance:

```python
if next_node.word:
    result.append(next_node.word)
    next_node.word = None  # Mark as found

# Prune empty branches
if not next_node.children:
    del node.children[char]  # Remove leaf, reduce search space
```

### 4. When NOT to Use Trie

❌ **Don't use Trie when:**
- Only searching for exact words (use HashSet - O(1) vs O(M))
- Suffix search required (use Suffix Tree/Array instead)
- Memory is severely constrained and no prefix overlap (use compressed trie or TST)
- Need range queries (use Binary Search Tree)
- Single word, one-time search (overhead not worth it)

✅ **DO use Trie when:**
- Multiple prefix queries on same dataset
- Autocomplete/typeahead features
- Word validation from large dictionary
- Pattern matching with shared prefixes

### 5. Unicode and International Characters

```python
class UnicodeTrieNode:
    def __init__(self):
        # HashMap handles any Unicode character
        self.children = {}
        self.is_end = False

# For Unicode, always use HashMap (not array)
# Alphabet size could be 100,000+ characters!
```

### 6. Memory Pool for Node Allocation

For high-performance systems, pre-allocate nodes:

```python
class TrieWithPool:
    def __init__(self, max_nodes=10000):
        # Pre-allocate node pool
        self.pool = [TrieNode() for _ in range(max_nodes)]
        self.pool_index = 0
        self.root = self._get_node()

    def _get_node(self):
        """Get node from pool instead of creating new."""
        if self.pool_index >= len(self.pool):
            return TrieNode()  # Fallback
        node = self.pool[self.pool_index]
        self.pool_index += 1
        return node

# Benefit: Reduces allocation overhead in tight loops
```

## Problem Recognition

### Keywords that Scream "TRIE!"

🔑 **Instant Trie Indicators:**
- "prefix"
- "autocomplete" / "typeahead" / "search suggestions"
- "words starting with"
- "dictionary of words"
- "multiple words" + "2D grid/board"
- "longest common prefix"
- "word validation"
- "spell checker"

### Problem Patterns

| Pattern | Example Problem | Why Trie? |
|---------|----------------|-----------|
| **Prefix search** | "Find all words starting with 'pre'" | Direct prefix traversal |
| **Multiple word search** | Word Search II | Share prefix exploration |
| **Autocomplete** | Design Search Autocomplete System | Efficient prefix matching |
| **Word validation** | Implement Trie, Word Break | Fast word lookup |
| **Longest prefix** | Longest Common Prefix | Natural tree traversal |

### Not Trie - Common Confusions

❌ **Suffix operations** → Use Suffix Array/Tree
❌ **Range queries** → Use Segment Tree or BST
❌ **Single exact match** → Use HashMap
❌ **Substring search** → Use KMP or Rolling Hash

## Practice Problems

### Beginner (Fundamentals)
1. **Implement Trie (Prefix Tree)** [LeetCode 208]
   - Core implementation
   - Master insert, search, startsWith

2. **Longest Word in Dictionary** [LeetCode 720]
   - Build trie, then DFS to find longest buildable word
   - Practice trie traversal

### Intermediate (Applications)
3. **Word Search II** [LeetCode 212]
   - Trie + DFS on 2D grid
   - Classic combination pattern
   - Learn trie pruning optimization

4. **Design Add and Search Words Data Structure** [LeetCode 211]
   - Trie + DFS for wildcard matching
   - Handle '.' wildcard with recursive search

5. **Replace Words** [LeetCode 648]
   - Find shortest prefix in dictionary
   - Early termination optimization

### Advanced (Complex Scenarios)
6. **Design Search Autocomplete System** [LeetCode 642]
   - Trie + frequency tracking
   - Top K results by frequency
   - Streaming input handling

7. **Word Squares** [LeetCode 425]
   - Trie + backtracking
   - Prefix matching in both dimensions
   - Complex constraint satisfaction

8. **Palindrome Pairs** [LeetCode 336]
   - Reverse trie trick
   - String manipulation + trie
   - O(N*M^2) optimization using trie

### Expert (Variations)
9. **Stream of Characters** [LeetCode 1032]
   - Reverse trie for suffix matching
   - Streaming data handling

10. **Maximum XOR of Two Numbers** [LeetCode 421]
    - Binary trie (0/1 children)
    - Bit manipulation + trie

## Common Mistakes

### 1. Forgetting to Mark End of Word

```python
# WRONG - Missing is_end_of_word check
def search(self, word: str) -> bool:
    node = self.root
    for char in word:
        if char not in node.children:
            return False
        node = node.children[char]
    return True  # BUG: Path exists but might not be a complete word!

# CORRECT
def search(self, word: str) -> bool:
    node = self.root
    for char in word:
        if char not in node.children:
            return False
        node = node.children[char]
    return node.is_end_of_word  # Must check end marker!
```

**Example:** Insert "apple", search "app" should return False!

### 2. Confusing Search vs StartsWith

```python
# search("app") after inserting "apple" → False (not marked as word)
# startsWith("app") after inserting "apple" → True (prefix exists)

# They're different! search() needs is_end_of_word check
```

### 3. Not Handling Empty String

```python
def insert(self, word: str) -> None:
    if not word:  # Handle empty string!
        self.root.is_end_of_word = True
        return
    # ... rest of implementation
```

### 4. Memory Leak in Delete Operation

```python
# WRONG - Just unmarking doesn't free memory
def delete(self, word: str) -> None:
    node = self.find(word)
    if node:
        node.is_end_of_word = False  # Memory leak! Nodes remain

# CORRECT - Recursively remove unused nodes
def delete(self, word: str) -> bool:
    def helper(node, word, index):
        if index == len(word):
            if not node.is_end_of_word:
                return False
            node.is_end_of_word = False
            return len(node.children) == 0  # Delete if no children

        char = word[index]
        if char not in node.children:
            return False

        should_delete = helper(node.children[char], word, index + 1)

        if should_delete:
            del node.children[char]
            return not node.is_end_of_word and len(node.children) == 0

        return False

    return helper(self.root, word, 0)
```

### 5. Inefficient Array Initialization

```python
# WRONG - Creates 26 nodes for every TrieNode!
class TrieNode:
    def __init__(self):
        self.children = [TrieNode() for _ in range(26)]  # WASTEFUL!

# CORRECT - Create nodes lazily
class TrieNode:
    def __init__(self):
        self.children = [None] * 26  # Just pointers, create when needed
```

### 6. Not Handling Case Sensitivity

```python
# Be explicit about case handling
def insert(self, word: str) -> None:
    word = word.lower()  # Normalize to lowercase
    # or handle uppercase separately if needed
```

### 7. Forgetting to Restore State in DFS (Word Search II)

```python
# WRONG
def dfs(row, col, node):
    board[row][col] = '#'  # Mark visited
    # ... recursive calls ...
    # FORGOT TO RESTORE!

# CORRECT
def dfs(row, col, node):
    char = board[row][col]
    board[row][col] = '#'  # Mark visited
    # ... recursive calls ...
    board[row][col] = char  # RESTORE for other paths!
```

### 8. Premature Optimization with Compression

Don't implement compressed trie unless space is proven bottleneck:
- Standard trie is simpler and usually sufficient
- Compression adds complexity
- Profile first, optimize later

### 9. Index Out of Bounds with Array Implementation

```python
# WRONG - No bounds checking
def insert(self, word: str) -> None:
    for char in word:
        idx = ord(char) - ord('a')
        self.children[idx] = ...  # What if char is '!', 'Z', or '5'?

# CORRECT - Validate input
def insert(self, word: str) -> None:
    for char in word:
        if not char.islower():
            raise ValueError(f"Invalid character: {char}")
        idx = ord(char) - ord('a')
        # ...
```

### 10. Not Considering Thread Safety

For production systems:
```python
from threading import Lock

class ThreadSafeTrie:
    def __init__(self):
        self.root = TrieNode()
        self.lock = Lock()

    def insert(self, word: str) -> None:
        with self.lock:  # Protect shared state
            # ... implementation
```

---

## Summary Cheatsheet

**When to reach for Trie:**
- 🔍 Need fast prefix search (O(P) vs O(N*M))
- 📝 Building autocomplete/typeahead
- ✅ Validating words from dictionary
- 🔤 Multiple words sharing prefixes
- 🎯 Word games, spell checkers, search suggestions

**Core Operations:**
- Insert: O(M) - walk path, create nodes as needed
- Search: O(M) - walk path, check end marker
- Prefix: O(P) - walk path, any path exists = true

**Key Implementation Details:**
- Mark end of word (don't just check path exists!)
- Choose HashMap (flexible) vs Array (faster, fixed alphabet)
- Consider memory: natural language has ~30-40% prefix overlap
- Optimize: store word at end node, prune in searches, lazy node creation

**Red Flags (NOT Trie):**
- Exact match only → HashSet
- Suffix search → Suffix Tree
- Single query → not worth overhead

Now go crush those Trie problems!
