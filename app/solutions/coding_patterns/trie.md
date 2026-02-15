# Trie (Prefix Tree) — Complete Interview Guide

## When to Use This Pattern

A Trie (pronounced "try," from re**trie**val) is a tree-like data structure that stores strings character by character. Each path from root to a node represents a prefix. Tries excel at prefix-based operations that hash maps cannot efficiently support.

**Signals that indicate a Trie:**
1. The problem involves **prefix matching** — "find all words with this prefix," "autocomplete," "search suggestions."
2. The problem requires searching for words with **wildcards** (`.` matches any character) — hash maps cannot handle this efficiently.
3. You need to search a **dictionary against a grid/stream** — Trie enables shared prefix traversal (Word Search II).
4. The problem involves checking if any **prefix of a string** exists in a set — Trie allows character-by-character checking without generating all substrings.
5. The problem asks about **palindrome pairs** or other relationships between strings that benefit from prefix/suffix indexing.
6. You are processing a **stream of characters** and need to check matches incrementally.

**When NOT to use a Trie:**
- Simple membership testing ("is this exact word in the set?") — a hash set is O(1) and simpler.
- The alphabet is very large (e.g., Unicode) — Trie nodes become memory-expensive.
- The strings are very long with little prefix sharing — Trie degenerates to a linked list per string.

---

## Core Mechanics

### Why Does a Trie Work?

A Trie exploits the hierarchical structure of strings. Instead of storing each string independently, strings that share a prefix share the same nodes for that prefix. This gives three advantages:

1. **Prefix queries in O(L)** where L is the prefix length, regardless of how many strings are stored.
2. **Character-by-character navigation** — you can walk the Trie one character at a time, which is essential for problems like wildcard search or stream matching.
3. **Space sharing** — words with common prefixes share nodes, reducing memory compared to storing all words separately.

### Trie Structure

```
Trie storing ["apple", "app", "apt", "bat"]:

        root
       /    \
      a      b
     /        \
    p          a
   / \          \
  p   t          t*
  |    *
  l
  |
  e*

* = end-of-word marker
```

Each node has:
- A map/array of children (one per possible character)
- A boolean indicating if this node marks the end of a complete word

### Complexity Analysis

| Operation | Time | Space |
|-----------|------|-------|
| Insert    | O(L) | O(L)  |
| Search    | O(L) | O(1)  |
| Prefix search | O(L) | O(1) |
| Delete    | O(L) | O(1)  |

Where L is the length of the string. Total space for N words of average length L is O(N * L) in the worst case, but usually much less due to prefix sharing.

---

## The Template

### Basic Trie with TrieNode class

```python
class TrieNode:
    def __init__(self):
        self.children = {}  # char -> TrieNode
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word):
        """Returns True if the exact word exists in the Trie."""
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end

    def starts_with(self, prefix):
        """Returns True if any word in the Trie starts with this prefix."""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True
```

```go
type TrieNode struct {
    Children map[byte]*TrieNode
    IsEnd    bool
}

type Trie struct {
    Root *TrieNode
}

func NewTrie() *Trie {
    return &Trie{Root: &TrieNode{Children: make(map[byte]*TrieNode)}}
}

func (t *Trie) Insert(word string) {
    node := t.Root
    for i := 0; i < len(word); i++ {
        ch := word[i]
        if _, ok := node.Children[ch]; !ok {
            node.Children[ch] = &TrieNode{Children: make(map[byte]*TrieNode)}
        }
        node = node.Children[ch]
    }
    node.IsEnd = true
}

func (t *Trie) Search(word string) bool {
    node := t.Root
    for i := 0; i < len(word); i++ {
        ch := word[i]
        if _, ok := node.Children[ch]; !ok {
            return false
        }
        node = node.Children[ch]
    }
    return node.IsEnd
}

func (t *Trie) StartsWith(prefix string) bool {
    node := t.Root
    for i := 0; i < len(prefix); i++ {
        ch := prefix[i]
        if _, ok := node.Children[ch]; !ok {
            return false
        }
        node = node.Children[ch]
    }
    return true
}
```

### Dictionary-based Trie (compact, for competitive programming)

When you do not need a class, a nested dictionary works well:

```python
def build_trie(words):
    trie = {}
    for word in words:
        node = trie
        for ch in word:
            node = node.setdefault(ch, {})
        node['$'] = True  # end-of-word marker
    return trie
```

This is the approach used in Word Search II (LC #212) for its simplicity.

---

## Problem Walkthroughs

### Problem: Implement Trie / Prefix Tree (LC #208) — Medium
**Companies**: Google, Amazon, Meta, Microsoft
**Why it's asked**: The fundamental Trie problem. If you cannot implement this cleanly, you will struggle with all Trie problems. Interviewers expect fast, bug-free implementation.

**Key Insight**: A Trie node holds a dictionary of children and an end-of-word flag. Insert walks the Trie, creating nodes as needed. Search walks the Trie and checks the end flag. StartsWith walks and returns True if the path exists (regardless of end flag).

**Optimal Solution**:
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self._find_node(word)
        return node is not None and node.is_end

    def startsWith(self, prefix: str) -> bool:
        return self._find_node(prefix) is not None

    def _find_node(self, prefix: str):
        """Helper: traverse the Trie following the characters in prefix."""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node
```

**Dry Run**:
```
Insert "apple":
  root -> 'a' (new) -> 'p' (new) -> 'p' (new) -> 'l' (new) -> 'e' (new, is_end=True)

Search "apple": root -> a -> p -> p -> l -> e (is_end=True) -> True
Search "app":   root -> a -> p -> p (is_end=False) -> False
StartsWith "app": root -> a -> p -> p (node exists) -> True

Insert "app":
  root -> a -> p -> p (already exists, set is_end=True)

Search "app": root -> a -> p -> p (is_end=True now) -> True
```

**Edge Cases**: Empty string (root is_end), single character words, words that are prefixes of other words.

**Complexity**: All operations O(L) where L is the string length. Space O(total characters across all inserted words).

**Follow-up questions**: "How would you implement delete?" — walk to the node, unset is_end, optionally prune leaf nodes with no children. "How would you list all words with a given prefix?" — DFS from the prefix node. "What about using an array instead of a dictionary?" — `children = [None] * 26` uses more memory but O(1) child access.

---

### Problem: Design Add and Search Words Data Structure (LC #211) — Medium
**Companies**: Meta, Google, Amazon, Microsoft
**Why it's asked**: Extends the basic Trie with wildcard matching. Tests recursive DFS within a Trie, which is a pattern that appears in harder Trie problems.

**Brute Force**:
```python
class WordDictionaryBrute:
    def __init__(self):
        self.words = set()

    def addWord(self, word):
        self.words.add(word)

    def search(self, word):
        import re
        pattern = '^' + word.replace('.', '.') + '$'
        return any(re.match(pattern, w) for w in self.words)
```
Search is O(N * L) where N is the number of stored words.

**Key Insight**: The `.` wildcard can match any character. When we encounter a `.` during Trie search, we must try ALL children of the current node (DFS branching). For regular characters, we follow the single matching child. This is a DFS within the Trie structure.

**Optimal Solution**:
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class WordDictionary:
    def __init__(self):
        self.root = TrieNode()

    def addWord(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        def dfs(node, idx):
            if idx == len(word):
                return node.is_end

            ch = word[idx]
            if ch == '.':
                # Wildcard: try every child
                for child in node.children.values():
                    if dfs(child, idx + 1):
                        return True
                return False
            else:
                if ch not in node.children:
                    return False
                return dfs(node.children[ch], idx + 1)

        return dfs(self.root, 0)
```

**Dry Run**:
```
addWord("bad"), addWord("dad"), addWord("mad")

Trie:
  root -> b -> a -> d*
       -> d -> a -> d*
       -> m -> a -> d*

search("pad"): root has no 'p' -> False
search("bad"): root -> b -> a -> d (is_end=True) -> True
search(".ad"):
  idx=0, ch='.': try all children of root
    child 'b': dfs(b_node, 1)
      idx=1, ch='a': b_node has 'a' -> dfs(a_node, 2)
        idx=2, ch='d': a_node has 'd' -> dfs(d_node, 3)
          idx=3 == len("bad"): d_node.is_end=True -> True!
  Return True
search("b.."): root -> b -> '.' tries 'a' -> '.' tries 'd' -> is_end=True -> True
```

**Edge Cases**: All wildcards ("..."), wildcard at beginning, no matches, single character words with wildcard.

**Complexity**: addWord is O(L). search is O(L) for no wildcards, O(26^w * L) in the worst case where w is the number of wildcards (branching factor 26 at each `.`). In practice, the branching is usually much less than 26.

**Follow-up questions**: "What if wildcards can match multiple characters (like `*`)?" — much harder, essentially regex matching within a Trie. "How would you optimize for patterns with wildcards only at the end?" — prefix search suffices.

---

### Problem: Search Suggestions System (LC #1268) — Medium
**Companies**: Amazon, Google, Meta
**Why it's asked**: Practical autocomplete system. Tests Trie construction combined with prefix-based DFS to collect suggestions.

**Brute Force**:
```python
def suggested_products_brute(products, searchWord):
    products.sort()
    result = []
    for i in range(1, len(searchWord) + 1):
        prefix = searchWord[:i]
        matches = [p for p in products if p.startswith(prefix)]
        result.append(matches[:3])
    return result
```
O(n * L * k) where k is the length of searchWord.

**Key Insight**: Build a Trie from the sorted products. For each prefix of the search word, navigate to the Trie node for that prefix, then DFS to collect up to 3 words in lexicographic order. Since the products are sorted before insertion, a DFS in alphabetical order of children naturally produces results in lexicographic order.

**Optimal Solution**:
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.suggestions = []  # store up to 3 suggestions at each node

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
            # Keep up to 3 suggestions at each prefix node
            if len(node.suggestions) < 3:
                node.suggestions.append(word)

def suggested_products(products, searchWord):
    products.sort()  # sort for lexicographic order

    trie = Trie()
    for product in products:
        trie.insert(product)

    result = []
    node = trie.root
    for ch in searchWord:
        if node and ch in node.children:
            node = node.children[ch]
            result.append(node.suggestions)
        else:
            node = None  # no more matches possible
            result.append([])

    return result
```

**Alternative approach using binary search (simpler, same efficiency):**
```python
import bisect

def suggested_products_binary(products, searchWord):
    products.sort()
    result = []
    prefix = ""

    for ch in searchWord:
        prefix += ch
        idx = bisect.bisect_left(products, prefix)
        suggestions = []
        for i in range(idx, min(idx + 3, len(products))):
            if products[i].startswith(prefix):
                suggestions.append(products[i])
            else:
                break
        result.append(suggestions)

    return result
```

**Dry Run** with `products = ["mobile","mouse","moneypot","monitor","mousepad"]`, `searchWord = "mouse"`:
```
Sorted: ["mobile","moneypot","monitor","mouse","mousepad"]

Build Trie, storing up to 3 suggestions at each prefix node:
  'm': ["mobile","moneypot","monitor"]
  'mo': ["mobile","moneypot","monitor"]
  'mob': ["mobile"]
  'mon': ["moneypot","monitor"]
  'mou': ["mouse","mousepad"]
  'mous': ["mouse","mousepad"]
  'mouse': ["mouse","mousepad"]
  'mousep': ["mousepad"]

Query with searchWord "mouse":
  'm': ["mobile","moneypot","monitor"]
  'mo': ["mobile","moneypot","monitor"]
  'mou': ["mouse","mousepad"]
  'mous': ["mouse","mousepad"]
  'mouse': ["mouse","mousepad"]

Result: [["mobile","moneypot","monitor"],
         ["mobile","moneypot","monitor"],
         ["mouse","mousepad"],
         ["mouse","mousepad"],
         ["mouse","mousepad"]]
```

**Edge Cases**: No matching products, all products match, searchWord longer than all products, single-character products.

**Complexity**: O(N * L) to build the Trie (N products, L max length), O(K) to query each prefix (K = searchWord length). Total O(N * L + K). Space O(N * L) for the Trie.

**Follow-up questions**: "What if products are too many to fit in memory?" — external sorting + binary search on disk. "What if new products are added dynamically?" — insert into Trie incrementally. "What about fuzzy matching (typos)?" — use edit distance within the Trie (much harder).

---

### Problem: Word Search II (LC #212) — Hard
**Companies**: Google, Meta, Amazon, Microsoft, Uber
**Why it's asked**: The classic Trie + backtracking combination. Without the Trie, searching for each word independently is too slow.

**Brute Force**:
```python
def find_words_brute(board, words):
    """Run Word Search (LC #79) for each word independently."""
    def exist(word):
        rows, cols = len(board), len(board[0])
        def bt(r, c, idx):
            if idx == len(word):
                return True
            if r < 0 or r >= rows or c < 0 or c >= cols or board[r][c] != word[idx]:
                return False
            tmp, board[r][c] = board[r][c], '#'
            found = any(bt(r+dr, c+dc, idx+1) for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)])
            board[r][c] = tmp
            return found
        return any(bt(r, c, 0) for r in range(rows) for c in range(cols))

    return [w for w in words if exist(w)]
```
O(W * M * N * 4^L) where W is the number of words. For large word lists, this is far too slow.

**Key Insight**: Build a Trie from all the words. Then do a single backtracking search over the board, simultaneously searching for ALL words. At each cell, check if the current path forms a prefix in the Trie. If not, prune (no word starts with this prefix). If a complete word is found, record it. This amortizes the board search across all words that share prefixes.

**Optimal Solution**:
```python
def find_words(board, words):
    # Build Trie using nested dictionaries
    trie = {}
    for word in words:
        node = trie
        for ch in word:
            node = node.setdefault(ch, {})
        node['$'] = word  # store full word at terminal

    rows, cols = len(board), len(board[0])
    result = []

    def backtrack(r, c, parent):
        ch = board[r][c]
        node = parent.get(ch)
        if not node:
            return

        # Found a complete word
        if '$' in node:
            result.append(node.pop('$'))  # pop to avoid duplicates

        # Mark visited
        board[r][c] = '#'

        # Explore 4 directions
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != '#':
                backtrack(nr, nc, node)

        # Restore
        board[r][c] = ch

        # Prune: remove empty Trie branches to speed up future searches
        if not node:
            del parent[ch]

    for r in range(rows):
        for c in range(cols):
            backtrack(r, c, trie)

    return result
```

**Dry Run** with `board = [["o","a","a","n"],["e","t","a","e"],["i","h","k","r"],["i","f","l","v"]]`, `words = ["oath","pea","eat","rain"]`:
```
Trie:
  o -> a -> t -> h -> {$: "oath"}
  p -> e -> a -> {$: "pea"}
  e -> a -> t -> {$: "eat"}
  r -> a -> i -> n -> {$: "rain"}

Start backtracking from each cell:

(0,0)='o': 'o' in trie -> descend into trie['o']
  mark (0,0)='#'
  try (0,1)='a': 'a' in trie['o'] -> descend
    mark (0,1)='#'
    try (1,1)='t': 't' in trie['o']['a'] -> descend
      mark (1,1)='#'
      try (2,1)='h': 'h' in trie['o']['a']['t'] -> descend
        '$' found -> record "oath", remove '$'
        mark (2,1)='#'
        no further matches from here
        restore (2,1)='h'
      restore (1,1)='t'
    restore (0,1)='a'
  restore (0,0)='o'

...continue from other cells...

(1,0)='e': 'e' in trie -> descend into trie['e']
  try (0,0)='o': not in trie['e']
  try (1,1)='t': not in trie['e']
  No 'a' neighbor at depth 0... actually:
  We need to find path e->a->t.
  From (1,0), neighbors: (0,0)='o', (2,0)='i', (1,1)='t'. None is 'a'.
  So no "eat" path from (1,0).

Eventually find "eat" from another 'e' cell, e.g., (0,3) or (1,3):
  ...paths explored...

Result: ["oath", "eat"]
```

**Edge Cases**: No words found, all words found, duplicate words in input (pop from Trie handles this), words that are prefixes of other words.

**Complexity**: O(M * N * 4^L) where L is the max word length, but Trie pruning makes it much faster in practice. Trie construction: O(sum of word lengths). Space O(sum of word lengths).

**Follow-up questions**: "How does the Trie pruning help?" — when all words under a prefix have been found, the branch is deleted, preventing future DFS into it. "What if the board is very large?" — the per-cell search depth is bounded by the max word length.

---

### Problem: Palindrome Pairs (LC #336) — Hard
**Companies**: Google, Amazon, Meta
**Why it's asked**: A hard Trie problem that combines string manipulation with Trie traversal. Tests deep understanding of palindrome properties.

**Brute Force**:
```python
def palindrome_pairs_brute(words):
    result = []
    for i in range(len(words)):
        for j in range(len(words)):
            if i != j:
                combined = words[i] + words[j]
                if combined == combined[::-1]:
                    result.append([i, j])
    return result
```
O(n^2 * L) where L is the average word length.

**Key Insight**: For words[i] + words[j] to be a palindrome, there are several cases:
1. words[j] is the reverse of words[i] (full match).
2. words[i] is longer: words[i] = prefix + suffix, where suffix is a palindrome and reverse(prefix) = words[j].
3. words[j] is longer: words[j] = prefix + suffix, where prefix is a palindrome and reverse(suffix) = words[i].

Build a Trie of reversed words. For each word, walk the Trie and check for palindrome conditions at each step.

Alternatively, use a hash map approach which is simpler to implement:

**Optimal Solution (Hash Map approach, cleaner)**:
```python
def palindrome_pairs(words):
    word_map = {word: i for i, word in enumerate(words)}
    result = []

    for i, word in enumerate(words):
        for j in range(len(word) + 1):
            # Split word into prefix and suffix
            prefix = word[:j]
            suffix = word[j:]

            # Case 1: prefix is palindrome, check if reverse(suffix) exists
            # This gives reverse(suffix) + prefix + suffix = palindrome
            # i.e., word_map[rev_suffix] + words[i]
            if prefix == prefix[::-1]:
                rev_suffix = suffix[::-1]
                if rev_suffix in word_map and word_map[rev_suffix] != i:
                    result.append([word_map[rev_suffix], i])

            # Case 2: suffix is palindrome, check if reverse(prefix) exists
            # This gives prefix + suffix + reverse(prefix) = palindrome
            # i.e., words[i] + word_map[rev_prefix]
            if suffix and suffix == suffix[::-1]:
                rev_prefix = prefix[::-1]
                if rev_prefix in word_map and word_map[rev_prefix] != i:
                    result.append([i, word_map[rev_prefix]])

    return result
```

**Trie-based Solution** (more efficient for large word sets):
```python
def palindrome_pairs_trie(words):
    # Build a Trie of reversed words
    trie = {}
    for idx, word in enumerate(words):
        node = trie
        reversed_word = word[::-1]
        for j, ch in enumerate(reversed_word):
            # If remaining suffix of reversed word is a palindrome, record this index
            if reversed_word[j:] == reversed_word[j:][::-1]:
                node.setdefault('#', []).append(idx)
            node = node.setdefault(ch, {})
        node.setdefault('#', []).append(idx)  # full word endpoint

    result = []
    for i, word in enumerate(words):
        node = trie
        for j, ch in enumerate(word):
            # word is longer than the trie path: check if remaining word part is palindrome
            if '#' in node:
                for k in node['#']:
                    if k != i and word[j:] == word[j:][::-1]:
                        result.append([i, k])
            if ch not in node:
                break
            node = node[ch]
        else:
            # word exactly consumed: check all palindrome suffixes in trie
            if '#' in node:
                for k in node['#']:
                    if k != i:
                        result.append([i, k])

    return result
```

**Dry Run** with `words = ["abcd", "dcba", "lls", "s", "sssll"]`:
```
Hash map approach:
word_map = {"abcd":0, "dcba":1, "lls":2, "s":3, "sssll":4}

word="abcd" (i=0):
  j=0: prefix="", suffix="abcd". prefix is palindrome. rev_suffix="dcba". "dcba" in map at index 1. Result: [1, 0]
  j=1: prefix="a", suffix="bcd". suffix not palindrome.
  j=2: prefix="ab", suffix="cd". Neither palindrome.
  j=3: prefix="abc", suffix="d". Neither palindrome.
  j=4: prefix="abcd", suffix="". prefix not palindrome. (Skip suffix case since suffix empty)

word="dcba" (i=1):
  j=0: prefix="", rev_suffix="abcd". "abcd" at index 0. Result: [0, 1]
  j=4: prefix="dcba", suffix="". prefix not palindrome.

word="lls" (i=2):
  j=0: prefix="", rev_suffix="sll". Not in map.
  j=1: prefix="l", suffix="ls". prefix is palindrome("l"). rev_suffix="sl". Not in map.
  j=2: prefix="ll", suffix="s". prefix is palindrome. rev_suffix="s". "s" at index 3. Result: [3, 2]
  j=3: prefix="lls", suffix="". suffix empty, skip. prefix not palindrome.

word="s" (i=3):
  j=0: prefix="", rev_suffix="s". "s" at index 3 (same index, skip).
  j=1: prefix="s", suffix="". prefix is palindrome. rev_suffix="". Not in map? "" not a word.
    suffix is empty, skip case 2.

word="sssll" (i=4):
  j=3: prefix="sss", suffix="ll". suffix is palindrome. rev_prefix="sss". Not in map.
  j=0: prefix="", suffix="sssll". prefix palindrome. rev_suffix="llsss". Not in map.
  ... checking all splits ... eventually:
  j=2: prefix="ss", suffix="sll". prefix palindrome. rev_suffix="lls". "lls" at index 2. Result: [2, 4]
  Wait: this should be [4, 2]. Let me recheck.
  Actually j=2: suffix="sll", suffix palindrome? "sll" != "lls", no.
  j=3: prefix="sss", palindrome yes. rev_suffix = "ll"[::-1] = "ll". "ll" not in map.
  Hmm. Let me think again...
  For i=4 word="sssll":
    j=5: prefix="sssll", suffix="". prefix not palindrome.
    j=0: prefix="", suffix="sssll". rev_suffix="llsss". Not in map.
    j=2: prefix="ss", suffix="sll". prefix is palindrome. rev_suffix="lls"[::-1]="sll"... wait.

    Actually: suffix="sll", rev_suffix=suffix[::-1]="lls". And "lls" IS in map at index 2.
    But we're in case 1: prefix is palindrome, so result is [word_map[rev_suffix], i] = [2, 4].

Result: [[1,0],[0,1],[3,2],[2,4]]
```

**Edge Cases**: Empty string in the list (pairs with any palindrome), single character words, all same words, no valid pairs.

**Complexity**: Hash map approach: O(n * L^2) where L is the max word length (checking palindrome for each split is O(L)). Trie approach: similar but can be optimized. Space O(n * L).

**Follow-up questions**: "Can you do better than O(n * L^2)?" — with Manacher's algorithm for palindrome checks, some splits can be precomputed. "What about finding the count instead of all pairs?" — still need to enumerate, complexity does not improve much.

---

### Problem: Stream of Characters (LC #1032) — Hard
**Companies**: Google, Amazon
**Why it's asked**: Tests reverse Trie with streaming input. The key insight is to build the Trie on reversed words and match the stream from the end.

**Brute Force**:
```python
class StreamCheckerBrute:
    def __init__(self, words):
        self.words = words
        self.stream = []

    def query(self, letter):
        self.stream.append(letter)
        s = ''.join(self.stream)
        for word in self.words:
            if s.endswith(word):
                return True
        return False
```
O(N * L) per query where N is the number of words and L is the max word length.

**Key Insight**: We need to check if the stream ends with any word from the dictionary. Instead of checking all words, build a Trie of reversed words. After each new character, walk the Trie backwards through the recent stream characters (most recent first). If we reach an end-of-word node, the stream suffix matches a word.

The key optimization: keep a buffer of the last `max_word_length` characters. After each new character, traverse the Trie starting from the most recent character going backwards.

**Optimal Solution**:
```python
class StreamChecker:
    def __init__(self, words):
        self.trie = {}
        self.stream = []
        self.max_len = 0

        # Build Trie of reversed words
        for word in words:
            self.max_len = max(self.max_len, len(word))
            node = self.trie
            for ch in reversed(word):
                node = node.setdefault(ch, {})
            node['$'] = True

    def query(self, letter: str) -> bool:
        self.stream.append(letter)

        node = self.trie
        # Walk backwards through recent stream characters
        for i in range(len(self.stream) - 1,
                       max(-1, len(self.stream) - 1 - self.max_len), -1):
            ch = self.stream[i]
            if ch not in node:
                return False
            node = node[ch]
            if '$' in node:
                return True

        return False
```

**Dry Run** with `words = ["cd", "f", "kl"]`:
```
Reversed Trie:
  d -> c -> {$: True}     (reversed "cd")
  f -> {$: True}           (reversed "f")
  l -> k -> {$: True}     (reversed "kl")

max_len = 2

query('a'): stream=['a']. Walk back: 'a' not in trie root -> False
query('b'): stream=['a','b']. Walk back: 'b' not in root -> False
query('c'): stream=['a','b','c']. Walk back: 'c' not in root -> False
query('d'): stream=['a','b','c','d']. Walk back:
  i=3: 'd' in root -> node=trie['d']
    '$' not in node
  i=2: 'c' in trie['d'] -> node=trie['d']['c']
    '$' in node -> True!  (stream ends with "cd")
query('e'): stream=['a','b','c','d','e']. Walk back: 'e' not in root -> False
query('f'): stream=['a','b','c','d','e','f']. Walk back:
  i=5: 'f' in root -> node=trie['f']
    '$' in node -> True!  (stream ends with "f")
```

**Edge Cases**: Very long stream (only look back max_len characters), words of length 1, overlapping words in stream.

**Complexity**: O(L) per query where L is the max word length. Space O(sum of word lengths) for the Trie plus O(Q) for the stream buffer (where Q is the number of queries).

**Follow-up questions**: "What if the stream is very long and memory is a concern?" — only keep the last `max_len` characters using a deque. "What if words can be added dynamically?" — insert reversed word into the Trie incrementally.

---

## Common Mistakes & Interview Tips

### Common Mistakes

1. **Using a hash set when a Trie is needed.** Hash sets support exact lookup and prefix checking (by storing all prefixes), but they cannot efficiently handle wildcard search, character-by-character navigation, or prefix enumeration. If the problem needs these, use a Trie.

2. **Not marking end-of-word correctly.** Forgetting the `is_end` flag means `search("app")` returns True even if only "apple" was inserted (because the prefix "app" exists in the Trie). Always check `is_end` for exact match and ignore it for prefix match.

3. **Memory-heavy Trie nodes.** Using an array of size 26 for children when most are null wastes memory. Use a dictionary for sparse alphabets, an array for dense alphabets (when most letters appear at each level).

4. **Forgetting Trie pruning in Word Search II.** Without pruning empty branches, the algorithm revisits dead-end Trie paths repeatedly. The `if not node: del parent[ch]` optimization is critical for passing time limits.

5. **Not considering the reverse Trie pattern.** For suffix-based problems (Stream of Characters, some palindrome problems), building a Trie on reversed strings is the key insight that many candidates miss.

### Interview Tips

1. **Implement Trie in under 5 minutes.** The basic Trie (insert, search, startsWith) should be second nature. Practice until you can write it from memory without bugs.

2. **Know when to use dict-based Trie vs class-based.** For clean production code (LC #208, #211), use a TrieNode class. For competitive problems embedded in larger solutions (LC #212), the nested dictionary approach is faster to write and often cleaner.

3. **Explain the Trie advantage over hash sets.** In an interview, articulate: "A hash set would require O(L) for each prefix check and cannot handle wildcards. A Trie gives O(L) prefix traversal with natural branching for wildcards."

4. **Combine Trie with other patterns.** Trie + Backtracking (Word Search II), Trie + DFS (Wildcard search), Trie + Stream processing (Stream of Characters). The Trie rarely stands alone in hard problems.

5. **Mention optimization opportunities.** Compressed tries (Patricia tries) for long shared prefixes, Trie with frequency counts for autocomplete ranking, Trie with arrays vs dictionaries for different performance profiles.

---

## Pattern Connections

- **Trie + Backtracking**: Word Search II (LC #212) is the most important combination. The Trie enables searching for multiple words simultaneously during grid backtracking.

- **Trie + DFS**: Wildcard search (LC #211) uses DFS within the Trie to branch at wildcard characters. This pattern also appears in regex-like matching.

- **Trie vs Hash Map**: For exact lookups, hash maps win (O(1) amortized vs O(L)). For prefix operations, Tries win. For wildcard operations, Tries are the only practical option. Choose based on the problem requirements.

- **Reverse Trie**: Building a Trie on reversed strings enables suffix matching. This transforms "does the stream end with any word?" into "does the reversed recent stream start with any reversed word?" — a prefix problem.

- **Trie + Bit Manipulation**: For maximum XOR problems (LC #421), build a Trie on the binary representations of numbers and greedily choose the bit that maximizes XOR. Each node has at most 2 children (0 and 1).

- **Trie for IP Routing / Longest Prefix Match**: In networking, Tries are used for IP routing tables where the longest matching prefix determines the route. This is a real-world application of the `startsWith` operation.
