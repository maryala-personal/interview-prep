# Meta/Facebook LeetCode Problems -- 2025 Comprehensive Guide

> Compiled from LeetCode company tags, Blind/TeamBlind reports, GitHub repositories (liquidslr, snehasishroy, krishnadey30), NeetCode, Sean Prashad's Patterns, Grind 75, interviewing.io, InterviewSolver, DesignGurus, LeetCode Discuss interview experiences, and multiple 2025 candidate reports.

---

## Key Meta Interview Insights (2025)

- **Meta explicitly states they do NOT ask dynamic programming questions.** Deprioritize DP and focus elsewhere.
- **Difficulty breakdown**: ~26% Easy, ~60% Medium, ~14% Hard
- **Most common patterns**: Arrays/Strings, Trees, Graphs, Hash Maps, Two Pointers, BFS/DFS, Stacks
- **QuickSelect** is used in ~40% of Meta's array-based questions
- **Phone screen**: 1 round, ~45 min total (behavioral + 2 coding questions from top 50 tagged)
- **Onsite**: 2 coding rounds (each ~35 min, 1-2 problems per round), plus system design + behavioral
- **New in late 2025**: AI-assisted coding round (1 of 2 coding rounds may be replaced; 60 min, harder problems, AI copilot available). Rolling out for all SWE roles in 2026.
- **Meta almost never asks problems verbatim** -- expect variants and follow-ups on core problems

---

## TIER 1: HIGHEST FREQUENCY (Must-Know -- Asked Repeatedly in 2025)

These problems are reported most frequently across all sources. Treat these as absolute top priority.

### Arrays and Strings

| # | Problem | Difficulty | Frequency | Notes |
|---|---------|------------|-----------|-------|
| 1249 | Minimum Remove to Make Valid Parentheses | Medium | **VERY HIGH** | #1 most asked at Meta in 2025. Variants: remove min chars to make valid brackets of multiple types; return all valid results |
| 680 | Valid Palindrome II | Easy | **VERY HIGH** | Can you make it a palindrome by removing at most one char? Variant: at most k removals |
| 1570 | Dot Product of Two Sparse Vectors | Medium | **VERY HIGH** | Variant: very large sparse arrays -- store only non-zero index+value pairs in LinkedList/Map/Sorted Set |
| 408 | Valid Word Abbreviation | Easy | **VERY HIGH** | Premium problem. Pattern matching with abbreviation rules |
| 314 | Binary Tree Vertical Order Traversal | Medium | **VERY HIGH** | Premium. BFS-based column ordering. Compare with LC 987 |
| 227 | Basic Calculator II | Medium | **VERY HIGH** | Stack-based expression evaluation. Variant: handle parentheses (Basic Calculator I/III) |
| 560 | Subarray Sum Equals K | Medium | **VERY HIGH** | Prefix sum + hash map. 2 common variants Meta asks on return types and constraints |
| 71 | Simplify Path | Medium | **VERY HIGH** | Stack-based Unix path simplification |
| 215 | Kth Largest Element in an Array | Medium | **VERY HIGH** | QuickSelect or min-heap. Meta loves this pattern |
| 88 | Merge Sorted Array | Easy | **VERY HIGH** | In-place merge. Variant: merge without extra space, one array has size N+M |
| 125 | Valid Palindrome | Easy | **VERY HIGH** | Two pointers. Often warm-up question |
| 543 | Diameter of Binary Tree | Easy | **VERY HIGH** | DFS on tree. Variant: diameter of N-ary tree (almost always asked as follow-up) |
| 236 | Lowest Common Ancestor of a Binary Tree | Medium | **VERY HIGH** | Recursive DFS. Foundational tree problem |
| 1650 | Lowest Common Ancestor of a Binary Tree III | Medium | **VERY HIGH** | Premium. With parent pointers -- like finding intersection of two linked lists |
| 146 | LRU Cache | Medium | **VERY HIGH** | HashMap + Doubly Linked List. Classic design problem |
| 528 | Random Pick with Weight | Medium | **VERY HIGH** | Prefix sum + binary search for weighted random selection |
| 670 | Maximum Swap | Medium | **VERY HIGH** | Greedy. Swap two digits to maximize number |
| 346 | Moving Average from Data Stream | Easy | **VERY HIGH** | Premium. Sliding window/queue. Variant: all integers given upfront instead of streaming |
| 938 | Range Sum of BST | Easy | **VERY HIGH** | DFS/BFS with BST pruning |
| 791 | Custom Sort String | Medium | **HIGH** | Custom comparator / counting sort |
| 339 | Nested List Weight Sum | Medium | **HIGH** | Premium. DFS/BFS on nested structure |

### Graphs and BFS/DFS

| # | Problem | Difficulty | Frequency | Notes |
|---|---------|------------|-----------|-------|
| 200 | Number of Islands | Medium | **HIGH** | BFS/DFS grid traversal. Classic |
| 133 | Clone Graph | Medium | **HIGH** | DFS/BFS with hash map for visited nodes |
| 1091 | Shortest Path in Binary Matrix | Medium | **HIGH** | BFS shortest path in grid |
| 721 | Accounts Merge | Medium | **HIGH** | Union-Find or DFS. Meta variant exists |

---

## TIER 2: HIGH FREQUENCY (Very Likely to Appear)

### Arrays and Strings

| # | Problem | Difficulty | Frequency | Notes |
|---|---------|------------|-----------|-------|
| 1 | Two Sum | Easy | **HIGH** | Hash map. Often warm-up or part of larger problem |
| 15 | 3Sum | Medium | **HIGH** | Two pointers after sorting |
| 56 | Merge Intervals | Medium | **HIGH** | Sort + merge. Variant: merge two interval lists |
| 238 | Product of Array Except Self | Medium | **HIGH** | Prefix/suffix product without division |
| 415 | Add Strings | Medium | **HIGH** | Never asked directly -- Meta asks variant with decimal numbers |
| 498 | Diagonal Traverse | Medium | **HIGH** | Matrix diagonal iteration |
| 523 | Continuous Subarray Sum | Medium | **HIGH** | Prefix sum modulo + hash map |
| 31 | Next Permutation | Medium | **HIGH** | In-place array manipulation |
| 50 | Pow(x, n) | Medium | **HIGH** | Binary exponentiation / fast power |
| 162 | Find Peak Element | Medium | **HIGH** | Binary search. Variant: find local minimum in log(n) time |
| 973 | K Closest Points to Origin | Medium | **HIGH** | QuickSelect or max-heap |
| 249 | Group Shifted Strings | Medium | **HIGH** | Premium. Hashing with relative differences |
| 1762 | Buildings With an Ocean View | Medium | **HIGH** | Premium. Monotonic stack / right-to-left scan |
| 766 | Toeplitz Matrix | Easy | **HIGH** | Check diagonal equality in matrix |
| 1539 | Kth Missing Positive Number | Easy | **HIGH** | Binary search on missing count |

### Trees

| # | Problem | Difficulty | Frequency | Notes |
|---|---------|------------|-----------|-------|
| 199 | Binary Tree Right Side View | Medium | **HIGH** | BFS level-order or DFS keeping track of depth |
| 987 | Vertical Order Traversal of a Binary Tree | Hard | **HIGH** | BFS with column tracking + sorting |
| 124 | Binary Tree Maximum Path Sum | Hard | **HIGH** | DFS with global max tracking |
| 297 | Serialize and Deserialize Binary Tree | Hard | **HIGH** | BFS or preorder DFS serialization |

### Linked Lists

| # | Problem | Difficulty | Frequency | Notes |
|---|---------|------------|-----------|-------|
| 138 | Copy List with Random Pointer | Medium | **HIGH** | Hash map or interleaving technique |
| 23 | Merge K Sorted Lists | Hard | **HIGH** | Min-heap or divide-and-conquer. Variant: class with constructor taking k sorted lists + next() method |
| 206 | Reverse Linked List | Easy | **HIGH** | Iterative and recursive. Foundation for many follow-ups |
| 2 | Add Two Numbers | Medium | **HIGH** | Linked list digit-by-digit addition |

### Design

| # | Problem | Difficulty | Frequency | Notes |
|---|---------|------------|-----------|-------|
| 348 | Design Tic-Tac-Toe | Medium | **HIGH** | Premium. O(1) move validation. Meta variant: N x N board, check winner efficiently |
| 460 | LFU Cache | Hard | **HIGH** | Follow-up to LRU Cache. HashMap + frequency buckets |

---

## TIER 3: MODERATE FREQUENCY (Regularly Reported)

### Arrays and Strings

| # | Problem | Difficulty | Frequency | Notes |
|---|---------|------------|-----------|-------|
| 398 | Random Pick Index | Medium | MODERATE | Reservoir sampling |
| 636 | Exclusive Time of Functions | Medium | MODERATE | Stack-based interval processing |
| 986 | Interval List Intersections | Medium | MODERATE | Two pointers on sorted intervals |
| 921 | Minimum Add to Make Parentheses Valid | Medium | MODERATE | Counter-based parentheses balancing |
| 283 | Move Zeroes | Easy | MODERATE | Two pointers in-place |
| 347 | Top K Frequent Elements | Medium | MODERATE | Heap or bucket sort |
| 34 | Find First and Last Position of Element in Sorted Array | Medium | MODERATE | Two binary searches |
| 76 | Minimum Window Substring | Hard | MODERATE | Sliding window with hash map |
| 953 | Verifying an Alien Dictionary | Easy | MODERATE | Custom comparator |
| 65 | Valid Number | Hard | MODERATE | State machine or careful parsing |
| 282 | Expression Add Operators | Hard | MODERATE | Backtracking with evaluation |
| 67 | Add Binary | Easy | MODERATE | String addition with carry |
| 273 | Integer to English Words | Hard | MODERATE | Recursive string building |

### Trees and Graphs

| # | Problem | Difficulty | Frequency | Notes |
|---|---------|------------|-----------|-------|
| 235 | Lowest Common Ancestor of a BST | Medium | MODERATE | BST property exploitation |
| 426 | Convert BST to Sorted Doubly Linked List | Medium | MODERATE | Premium. In-order traversal |
| 103 | Binary Tree Zigzag Level Order Traversal | Medium | MODERATE | BFS with alternating direction |
| 958 | Check Completeness of a Binary Tree | Medium | MODERATE | BFS level-order check |
| 286 | Walls and Gates | Medium | MODERATE | Premium. Multi-source BFS |
| 269 | Alien Dictionary | Hard | MODERATE | Premium. Topological sort |
| 207 | Course Schedule | Medium | MODERATE | Topological sort / cycle detection |

### Binary Search

| # | Problem | Difficulty | Frequency | Notes |
|---|---------|------------|-----------|-------|
| 33 | Search in Rotated Sorted Array | Medium | MODERATE | Modified binary search |
| 74 | Search a 2D Matrix | Medium | MODERATE | Binary search on flattened matrix |

### Backtracking

| # | Problem | Difficulty | Frequency | Notes |
|---|---------|------------|-----------|-------|
| 17 | Letter Combinations of a Phone Number | Medium | MODERATE | Backtracking with mapping |
| 46 | Permutations | Medium | MODERATE | Classic backtracking |
| 78 | Subsets | Medium | MODERATE | Backtracking / bit manipulation |
| 39 | Combination Sum | Medium | MODERATE | Backtracking with reuse |

### Stacks and Queues

| # | Problem | Difficulty | Frequency | Notes |
|---|---------|------------|-----------|-------|
| 20 | Valid Parentheses | Easy | MODERATE | Stack matching |
| 155 | Min Stack | Medium | MODERATE | Stack with O(1) min |
| 232 | Implement Queue using Stacks | Easy | MODERATE | Two-stack queue |

---

## TIER 4: OCCASIONALLY REPORTED

### Arrays and Strings

| # | Problem | Difficulty | Frequency | Notes |
|---|---------|------------|-----------|-------|
| 42 | Trapping Rain Water | Hard | OCCASIONAL | Two pointers or stack |
| 3 | Longest Substring Without Repeating Characters | Medium | OCCASIONAL | Sliding window |
| 5 | Longest Palindromic Substring | Medium | OCCASIONAL | Expand around center / Manacher |
| 11 | Container With Most Water | Medium | OCCASIONAL | Two pointers |
| 49 | Group Anagrams | Medium | OCCASIONAL | Hash map with sorted key |
| 54 | Spiral Matrix | Medium | OCCASIONAL | Matrix traversal with boundaries |
| 75 | Sort Colors | Medium | OCCASIONAL | Dutch National Flag / 3-way partition |
| 43 | Multiply Strings | Medium | OCCASIONAL | Digit-by-digit multiplication |
| 151 | Reverse Words in a String | Medium | OCCASIONAL | Split + reverse |
| 253 | Meeting Rooms II | Medium | OCCASIONAL | Premium. Min-heap for overlaps |

### Trees and Graphs

| # | Problem | Difficulty | Frequency | Notes |
|---|---------|------------|-----------|-------|
| 102 | Binary Tree Level Order Traversal | Medium | OCCASIONAL | BFS with level grouping |
| 98 | Validate Binary Search Tree | Medium | OCCASIONAL | In-order traversal or range checking |
| 104 | Maximum Depth of Binary Tree | Easy | OCCASIONAL | Simple DFS |
| 572 | Subtree of Another Tree | Easy | OCCASIONAL | Recursive comparison |
| 210 | Course Schedule II | Medium | OCCASIONAL | Topological sort with order |
| 261 | Graph Valid Tree | Medium | OCCASIONAL | Premium. Union-Find or DFS |

### Linked Lists

| # | Problem | Difficulty | Frequency | Notes |
|---|---------|------------|-----------|-------|
| 21 | Merge Two Sorted Lists | Easy | OCCASIONAL | Iterative or recursive merge |
| 25 | Reverse Nodes in k-Group | Hard | OCCASIONAL | Iterative reversal in chunks |
| 143 | Reorder List | Medium | OCCASIONAL | Find middle + reverse + merge |
| 19 | Remove Nth Node From End of List | Medium | OCCASIONAL | Two pointers with gap |

### Dynamic Programming (Rare at Meta but reported)

| # | Problem | Difficulty | Frequency | Notes |
|---|---------|------------|-----------|-------|
| 139 | Word Break | Medium | OCCASIONAL | Despite Meta saying no DP, this appears occasionally |
| 121 | Best Time to Buy and Sell Stock | Easy | OCCASIONAL | Single pass with min tracking |
| 322 | Coin Change | Medium | OCCASIONAL | Classic DP (rare at Meta) |

---

## ORGANIZED BY PATTERN / CATEGORY

### Pattern 1: Two Pointers / Sliding Window
| # | Problem | Difficulty | Tier |
|---|---------|------------|------|
| 125 | Valid Palindrome | Easy | 1 |
| 680 | Valid Palindrome II | Easy | 1 |
| 88 | Merge Sorted Array | Easy | 1 |
| 15 | 3Sum | Medium | 2 |
| 283 | Move Zeroes | Easy | 3 |
| 76 | Minimum Window Substring | Hard | 3 |
| 11 | Container With Most Water | Medium | 4 |
| 3 | Longest Substring Without Repeating Characters | Medium | 4 |
| 986 | Interval List Intersections | Medium | 3 |

### Pattern 2: Hash Map / Prefix Sum
| # | Problem | Difficulty | Tier |
|---|---------|------------|------|
| 1 | Two Sum | Easy | 2 |
| 560 | Subarray Sum Equals K | Medium | 1 |
| 523 | Continuous Subarray Sum | Medium | 2 |
| 249 | Group Shifted Strings | Medium | 2 |
| 347 | Top K Frequent Elements | Medium | 3 |
| 49 | Group Anagrams | Medium | 4 |
| 791 | Custom Sort String | Medium | 1 |
| 953 | Verifying an Alien Dictionary | Easy | 3 |

### Pattern 3: Stack / Parentheses
| # | Problem | Difficulty | Tier |
|---|---------|------------|------|
| 1249 | Minimum Remove to Make Valid Parentheses | Medium | 1 |
| 227 | Basic Calculator II | Medium | 1 |
| 71 | Simplify Path | Medium | 1 |
| 20 | Valid Parentheses | Easy | 3 |
| 921 | Minimum Add to Make Parentheses Valid | Medium | 3 |
| 636 | Exclusive Time of Functions | Medium | 3 |
| 155 | Min Stack | Medium | 3 |
| 1762 | Buildings With an Ocean View | Medium | 2 |

### Pattern 4: Binary Search / QuickSelect
| # | Problem | Difficulty | Tier |
|---|---------|------------|------|
| 215 | Kth Largest Element in an Array | Medium | 1 |
| 528 | Random Pick with Weight | Medium | 1 |
| 162 | Find Peak Element | Medium | 2 |
| 973 | K Closest Points to Origin | Medium | 2 |
| 1539 | Kth Missing Positive Number | Easy | 2 |
| 33 | Search in Rotated Sorted Array | Medium | 3 |
| 34 | Find First and Last Position of Element in Sorted Array | Medium | 3 |
| 74 | Search a 2D Matrix | Medium | 3 |
| 50 | Pow(x, n) | Medium | 2 |

### Pattern 5: Tree DFS / BFS
| # | Problem | Difficulty | Tier |
|---|---------|------------|------|
| 543 | Diameter of Binary Tree | Easy | 1 |
| 236 | Lowest Common Ancestor of a Binary Tree | Medium | 1 |
| 1650 | Lowest Common Ancestor of a Binary Tree III | Medium | 1 |
| 938 | Range Sum of BST | Easy | 1 |
| 314 | Binary Tree Vertical Order Traversal | Medium | 1 |
| 199 | Binary Tree Right Side View | Medium | 2 |
| 987 | Vertical Order Traversal of a Binary Tree | Hard | 2 |
| 124 | Binary Tree Maximum Path Sum | Hard | 2 |
| 297 | Serialize and Deserialize Binary Tree | Hard | 2 |
| 339 | Nested List Weight Sum | Medium | 1 |
| 346 | Moving Average from Data Stream | Easy | 1 |
| 235 | Lowest Common Ancestor of a BST | Medium | 3 |
| 426 | Convert BST to Sorted Doubly Linked List | Medium | 3 |
| 103 | Binary Tree Zigzag Level Order Traversal | Medium | 3 |
| 958 | Check Completeness of a Binary Tree | Medium | 3 |

### Pattern 6: Graph BFS / DFS / Union-Find
| # | Problem | Difficulty | Tier |
|---|---------|------------|------|
| 200 | Number of Islands | Medium | 2 |
| 133 | Clone Graph | Medium | 2 |
| 1091 | Shortest Path in Binary Matrix | Medium | 2 |
| 721 | Accounts Merge | Medium | 2 |
| 286 | Walls and Gates | Medium | 3 |
| 269 | Alien Dictionary | Hard | 3 |
| 207 | Course Schedule | Medium | 3 |

### Pattern 7: Linked List
| # | Problem | Difficulty | Tier |
|---|---------|------------|------|
| 138 | Copy List with Random Pointer | Medium | 2 |
| 23 | Merge K Sorted Lists | Hard | 2 |
| 206 | Reverse Linked List | Easy | 2 |
| 2 | Add Two Numbers | Medium | 2 |
| 21 | Merge Two Sorted Lists | Easy | 4 |
| 25 | Reverse Nodes in k-Group | Hard | 4 |
| 143 | Reorder List | Medium | 4 |

### Pattern 8: Design / Data Structures
| # | Problem | Difficulty | Tier |
|---|---------|------------|------|
| 146 | LRU Cache | Medium | 1 |
| 460 | LFU Cache | Hard | 2 |
| 348 | Design Tic-Tac-Toe | Medium | 2 |
| 232 | Implement Queue using Stacks | Easy | 3 |

### Pattern 9: Greedy / Math / String Manipulation
| # | Problem | Difficulty | Tier |
|---|---------|------------|------|
| 670 | Maximum Swap | Medium | 1 |
| 415 | Add Strings | Medium | 2 |
| 766 | Toeplitz Matrix | Easy | 2 |
| 498 | Diagonal Traverse | Medium | 2 |
| 31 | Next Permutation | Medium | 2 |
| 67 | Add Binary | Easy | 3 |
| 273 | Integer to English Words | Hard | 3 |
| 43 | Multiply Strings | Medium | 4 |
| 65 | Valid Number | Hard | 3 |

### Pattern 10: Backtracking
| # | Problem | Difficulty | Tier |
|---|---------|------------|------|
| 17 | Letter Combinations of a Phone Number | Medium | 3 |
| 46 | Permutations | Medium | 3 |
| 78 | Subsets | Medium | 3 |
| 39 | Combination Sum | Medium | 3 |
| 282 | Expression Add Operators | Hard | 3 |

### Pattern 11: Intervals
| # | Problem | Difficulty | Tier |
|---|---------|------------|------|
| 56 | Merge Intervals | Medium | 2 |
| 986 | Interval List Intersections | Medium | 3 |
| 253 | Meeting Rooms II | Medium | 4 |

---

## META-SPECIFIC VARIANTS (Documented on LeetCode Discuss)

Meta almost never asks LeetCode problems verbatim. Here are documented variants:

### LC 1249 -- Minimum Remove to Make Valid Parentheses
- **Variant 1**: Handle multiple bracket types `()`, `[]`, `{}`
- **Variant 2**: Return ALL possible valid results (not just one)
- **Variant 3**: Minimize removals across nested bracket types

### LC 543 -- Diameter of Binary Tree
- **Variant (almost always asked as follow-up)**: Find the diameter of an N-ary tree

### LC 346 -- Moving Average from Data Stream
- **Variant**: What if you are given ALL integers upfront (not streaming)?

### LC 415 -- Add Strings
- **Meta never asks the original directly**. Variant: strings can contain decimal points

### LC 560 -- Subarray Sum Equals K
- **Variant 1**: Different return type (return the subarrays themselves, not just count)
- **Variant 2**: Additional constraints on the input array

### LC 348 -- Design Tic-Tac-Toe
- **Variant**: N x N board with efficient winner checking using row/column/diagonal sums

### LC 721 -- Accounts Merge
- **Variant**: Different input format or additional merge criteria

### LC 249 -- Group Shifted Strings
- **Variant**: Modified shift rules or grouping criteria

### LC 1570 -- Dot Product of Two Sparse Vectors
- **Variant**: Very large sparse arrays -- store only non-zero index+value pairs, merge on the fly

### LC 528 -- Random Pick with Weight
- **Variant**: Dynamic weights that change over time

### LC 88 -- Merge Sorted Array
- **Variant**: Merge 3+ sorted arrays with no duplicates allowed

---

## AI-ASSISTED CODING ROUND (New in Late 2025)

Starting October 2025, Meta began piloting an AI-enabled coding interview:
- **Format**: Replaces 1 of 2 traditional coding rounds randomly
- **Duration**: 60 minutes in a CoderPad environment
- **AI Tools Available**: GPT-4o mini, Claude 3.5 Haiku, Llama 4 Maverick
- **Problem Style**: Harder than typical medium LeetCode; multi-stage continuous engineering task (~120 lines of code); iterating on a miniature software system rather than two independent algorithm problems
- **Evaluation**: Classic coding skills + ability to verify and review AI output. You must understand any AI-generated code you use.
- **Rollout**: Full rollout for all SWE roles planned for 2026

---

## PREPARATION STRATEGY (Synthesized from Multiple Sources)

### Priority Order
1. **Tier 1 (21 problems)**: Solve ALL of these. Know them cold with variants.
2. **Tier 2 (23 problems)**: Solve all of these. Practice variants.
3. **Tier 3 (28 problems)**: Work through these for pattern coverage.
4. **Tier 4 (20+ problems)**: Time permitting, for breadth.

### Time Allocation
- **60% on Arrays/Strings/Stack problems** (Meta's strongest focus area)
- **25% on Trees/Graphs** (second most common)
- **10% on Linked Lists/Design**
- **5% on Binary Search / Backtracking**
- **0-5% on DP** (Meta says they do not ask DP, though rare exceptions exist)

### Key Skills Meta Evaluates
1. **Communication**: Talk through your approach before coding
2. **Problem Solving**: Handle ambiguity, ask clarifying questions, consider edge cases
3. **Coding**: Clean, bug-free code in 35 minutes
4. **Verification**: Test your solution, walk through examples, find edge cases

### Practice Tips
- Solve top 100 Facebook-tagged problems sorted by frequency on LeetCode Premium
- For each problem, write down the pattern used (e.g., "Sliding Window", "Prefix Sum")
- Practice explaining your approach aloud before coding
- Time yourself: 35 minutes max per medium problem
- After solving, look up Meta variants on LeetCode Discuss
- For the new AI round: practice using AI copilot tools but always verify and understand output

---

## PREMIUM (LOCKED) PROBLEMS FREQUENTLY ASKED AT META

These require LeetCode Premium but are critical for Meta prep:

| # | Problem | Difficulty | Category |
|---|---------|------------|----------|
| 408 | Valid Word Abbreviation | Easy | String |
| 314 | Binary Tree Vertical Order Traversal | Medium | Tree/BFS |
| 1650 | Lowest Common Ancestor of a Binary Tree III | Medium | Tree |
| 339 | Nested List Weight Sum | Medium | DFS |
| 346 | Moving Average from Data Stream | Easy | Queue/Design |
| 1570 | Dot Product of Two Sparse Vectors | Medium | Array/Design |
| 1762 | Buildings With an Ocean View | Medium | Stack/Array |
| 249 | Group Shifted Strings | Medium | Hash Map |
| 348 | Design Tic-Tac-Toe | Medium | Design |
| 426 | Convert BST to Sorted Doubly Linked List | Medium | Tree |
| 286 | Walls and Gates | Medium | BFS |
| 269 | Alien Dictionary | Hard | Topological Sort |
| 253 | Meeting Rooms II | Medium | Intervals/Heap |
| 261 | Graph Valid Tree | Medium | Graph/Union-Find |

---

## QUICK REFERENCE: TOP 30 PROBLEMS BY FREQUENCY

For maximum ROI with limited time, focus on these 30 in order:

1. **1249** - Minimum Remove to Make Valid Parentheses (Medium)
2. **680** - Valid Palindrome II (Easy)
3. **1570** - Dot Product of Two Sparse Vectors (Medium, Premium)
4. **408** - Valid Word Abbreviation (Easy, Premium)
5. **314** - Binary Tree Vertical Order Traversal (Medium, Premium)
6. **227** - Basic Calculator II (Medium)
7. **560** - Subarray Sum Equals K (Medium)
8. **543** - Diameter of Binary Tree (Easy)
9. **236** - Lowest Common Ancestor of a Binary Tree (Medium)
10. **1650** - Lowest Common Ancestor of a Binary Tree III (Medium, Premium)
11. **528** - Random Pick with Weight (Medium)
12. **71** - Simplify Path (Medium)
13. **146** - LRU Cache (Medium)
14. **215** - Kth Largest Element in an Array (Medium)
15. **670** - Maximum Swap (Medium)
16. **938** - Range Sum of BST (Easy)
17. **88** - Merge Sorted Array (Easy)
18. **125** - Valid Palindrome (Easy)
19. **339** - Nested List Weight Sum (Medium, Premium)
20. **346** - Moving Average from Data Stream (Easy, Premium)
21. **791** - Custom Sort String (Medium)
22. **56** - Merge Intervals (Medium)
23. **199** - Binary Tree Right Side View (Medium)
24. **973** - K Closest Points to Origin (Medium)
25. **238** - Product of Array Except Self (Medium)
26. **1** - Two Sum (Easy)
27. **200** - Number of Islands (Medium)
28. **138** - Copy List with Random Pointer (Medium)
29. **23** - Merge K Sorted Lists (Hard)
30. **133** - Clone Graph (Medium)

---

## SOURCES

- [LeetCode Meta/Facebook Company Tag](https://leetcode.com/company/facebook/)
- [LeetCode Top Facebook Questions](https://leetcode.com/problem-list/top-facebook-questions/)
- [Meta 73 Most Asked Problems (Medium)](https://medium.com/@johnadjanohoun/metas-most-asked-coding-interview-questions-the-complete-list-of-73-leetcode-problems-47e96767adc7)
- [Meta DS & Algo Interview Roadmap 2025 (Medium)](https://medium.com/@prashant558908/meta-facebook-ds-algo-interview-preparation-roadmap-2025-e4b65b30a20e)
- [InterviewSolver Meta Questions](https://interviewsolver.com/interview-questions/meta)
- [liquidslr/leetcode-company-wise-problems (GitHub)](https://github.com/liquidslr/leetcode-company-wise-problems)
- [snehasishroy/leetcode-companywise-interview-questions (GitHub, Nov 2025)](https://github.com/snehasishroy/leetcode-companywise-interview-questions)
- [Meta Variant Compilation (LeetCode Discuss)](https://leetcode.com/discuss/post/6615244/meta-variant-compilation-by-codingwithmi-0pm7/)
- [Meta Tagged Problems and Solutions (gauravaryal.com)](https://www.gauravaryal.com/leetcode/meta-tagged-problems/)
- [Sean Prashad LeetCode Patterns](https://seanprashad.com/leetcode-patterns/)
- [NeetCode Meta Practice](https://neetcode.io/practice/company)
- [Grind 75 / Blind 75](https://www.techinterviewhandbook.org/grind75/)
- [Meta Interview Guide (interviewing.io)](https://interviewing.io/guides/hiring-process/meta-facebook)
- [DesignGurus Top 20 Meta Coding Questions](https://www.designgurus.io/blog/top-20-coding-questions-to-pass-meta-interview)
- [VerveCopilot Top 30 Meta LeetCode Questions](https://www.vervecopilot.com/hot-blogs/meta-leetcode-interview-questions)
- [TeamBlind Meta Top 30 LeetCode](https://www.teamblind.com/post/meta-top-30-leetcode-question-ksxp4e8m)
- [Meta Preparation Strategy (LeetCode Discuss)](https://leetcode.com/discuss/interview-question/4979750/meta-preparation-strategy-step-by-step-guide-e4-and-plus/)
- [bala92/InterviewProblemsSolved Meta Problems (GitHub)](https://github.com/bala92/InterviewProblemsSolved/blob/main/Meta_Facebook_Coding_Problems.md)
- [GeeksforGeeks Meta SDE Sheet](https://www.geeksforgeeks.org/dsa/facebookmeta-sde-sheet-interview-questions-and-answers/)
- [Meta AI-Enabled Coding Interview Guide (HelloInterview)](https://www.hellointerview.com/blog/meta-ai-enabled-coding)
- [Meta AI Coding Interview (interviewing.io)](https://interviewing.io/blog/how-to-use-ai-in-meta-s-ai-assisted-coding-interview-with-real-prompts-and-examples)
- [Educative: Cracking Top 40 Facebook Questions](https://www.educative.io/blog/cracking-top-facebook-coding-interview-questions)
- [Grind 75 vs LeetCode Patterns for Meta (Educative)](https://www.educative.io/blog/grind-75-vs-leetcode-patterns-for-meta-coding-interviews)
