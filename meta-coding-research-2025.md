# Meta (Facebook) Coding Interview Research Report -- 2025/2026

> **Research Date**: February 15, 2026
> **Sources Consulted**: LeetCode Discuss, TeamBlind, Reddit (r/leetcode, r/cscareerquestions), Glassdoor, Medium, Exponent, IGotAnOffer, HelloInterview, Interviewing.io, DesignGurus, CodingKaro, Onsites.fyi, Coditioning, InterviewSolver, GeeksForGeeks, GitHub repos, various interview prep blogs and YouTube guides.
> **Total Searches Conducted**: 25+ across multiple platforms

---

## 1. Executive Summary

### Meta's Current Interview Focus Areas (2025-2026)

Meta's coding interview in 2025-2026 has undergone a significant transformation. The most notable change is the introduction of an **AI-enabled coding round** (piloted October 2025, rolling out to all SWE roles in 2026) that replaces one of the two traditional coding rounds at the onsite stage. Here are the key takeaways:

**Format Changes:**
- The traditional coding round remains (45 min, 2 LeetCode-style problems in 35 min)
- The new AI-enabled round is 60 min in a CoderPad environment with an AI assistant (GPT-4o mini, GPT-5, Claude Sonnet 4/4.5, Claude Haiku 3.5/4.5, Gemini 2.5 Pro, Llama 4 Maverick)
- AI-enabled round presents one extended real-world problem divided into stages/checkpoints (aim for 4+ checkpoints)
- Candidates get a file explorer, code editor, terminal, and AI chat panel

**Problem Focus:**
- Arrays/Strings and Trees/Graphs dominate (together ~60% of questions)
- Heavy emphasis on BFS/DFS, Two Pointers, and Hash Map patterns
- **Meta has moved AWAY from Dynamic Programming** -- multiple sources (ex-Meta interviewers, recent candidates) confirm DP is now rare
- Medium difficulty problems constitute ~60% of the question pool; Easy ~26%; Hard ~14%
- Problems frequently have "twists" or variations from standard LeetCode versions
- Follow-up questions probe understanding of trade-offs, alternative data structures, and optimization

**Top 5 Most Frequently Asked Problems (2025):**
1. Minimum Remove to Make Valid Parentheses (LC 1249) -- **the single most asked question**
2. Binary Tree Vertical Order Traversal (LC 314)
3. Lowest Common Ancestor of a Binary Tree (LC 236)
4. Buildings with an Ocean View (LC 1762)
5. Basic Calculator II (LC 227)

**Key Trend:** Meta does NOT ask DP questions anymore (or very rarely). Focus on Trees, Graphs, Arrays/Strings, Hash Maps, and Stacks.

---

## 2. Meta Coding Interview Format (2025-2026)

### 2.1 Interview Pipeline

| Stage | Duration | Format | Content |
|-------|----------|--------|---------|
| Recruiter Screen | 30 min | Phone | Background, motivation, role fit |
| Technical Phone Screen | 45-60 min | CoderPad | 2 coding problems (Easy-Medium), 35 min coding |
| Onsite: Coding Round 1 | 45 min | Whiteboard/CoderPad | 2 coding problems (Medium), 35 min coding |
| Onsite: Coding Round 2 (AI-enabled) | 60 min | CoderPad + AI | 1 extended project-style problem with checkpoints |
| Onsite: System Design | 45 min | Whiteboard | Architecture for billion-user scale |
| Onsite: Behavioral | 45 min | Discussion | Meta core values (Move Fast, Be Bold, etc.) |

### 2.2 Level-Specific Differences

| Level | Coding Expectations | Notes |
|-------|-------------------|-------|
| E3 (New Grad) | Solve 2 Medium problems optimally in 35 min | Focus on correctness and clean code |
| E4 (Mid-Level) | Solve 2 Medium problems with optimal solutions + edge cases | Must demonstrate strong problem solving |
| E5 (Senior) | Solve 2 Medium-Hard problems, discuss trade-offs | Expected to lead the conversation, narrate approach |
| E6 (Staff) | E5 expectations + deeper system awareness | Phone screen includes 15 min behavioral |

### 2.3 AI-Enabled Round Details

- **Duration**: 60 minutes
- **Environment**: CoderPad with file explorer, code editor, terminal, AI chat panel
- **Problem Type**: Multi-file project to iterate on (NOT two algorithmic problems)
- **Checkpoints**: Problem divided into stages; aim for 4+ checkpoints minimum
- **Evaluation**: Problem-solving approach, code quality, verification skills, NOT prompt engineering
- **Key Tip**: The practice puzzle Meta provides is reportedly harder than the real interview
- **Friction Points**: Output panel does not auto-clear between runs; manual scroll management needed

---

## 3. Complete Problem List -- Organized by Pattern

### 3.1 Arrays & Strings (HIGHEST FREQUENCY at Meta)

| # | Problem | LC# | Difficulty | Frequency | Round | Follow-ups |
|---|---------|-----|------------|-----------|-------|------------|
| 1 | **Minimum Remove to Make Valid Parentheses** | 1249 | Medium | **Very High** | Phone, Onsite | Remove minimum brackets with other chars; return count removed; handle nested brackets with priorities |
| 2 | **Valid Palindrome** | 125 | Easy | Very High | Phone | - |
| 3 | **Valid Palindrome II** | 680 | Easy | Very High | Phone | What if you can remove at most k characters? |
| 4 | **Move Zeroes** | 283 | Easy | High | Phone | Move all instances of a value; maintain relative order variant |
| 5 | **Add Strings** | 415 | Easy | High | Phone | Follow-up: multiply strings (LC 43) |
| 6 | **Product of Array Except Self** | 238 | Medium | Very High | Phone, Onsite | Do it without division; O(1) space |
| 7 | **Group Anagrams** | 49 | Medium | High | Onsite | Group by sorted key vs. character count |
| 8 | **Longest Substring Without Repeating Characters** | 3 | Medium | Very High | Phone, Onsite | What if we need longest with at most k distinct? |
| 9 | **Basic Calculator II** | 227 | Medium | **Very High** | Phone, Onsite | Add parentheses (LC 224); handle unary minus |
| 10 | **Longest Palindromic Substring** | 5 | Medium | High | Onsite | Expand around center vs. DP approach |
| 11 | **Encode and Decode Strings** | 271 | Medium | High | Onsite | - |
| 12 | **Subarray Sum Equals K** | 560 | Medium | Very High | Phone, Onsite | Continuous subarray sum (LC 523) |
| 13 | **Custom Sort String** | 791 | Medium | High | Onsite | - |
| 14 | **Simplify Path** | 71 | Medium | High | Onsite | - |
| 15 | **Minimum Window Substring** | 76 | Hard | High | Onsite | - |
| 16 | **Text Justification** | 68 | Hard | Medium | Onsite | - |
| 17 | **Next Permutation** | 31 | Medium | High | Onsite | Find next smallest number with same digits |
| 18 | **Multiply Strings** | 43 | Medium | High | Phone | Follow-up to Add Strings |
| 19 | **Continuous Subarray Sum** | 523 | Medium | High | Onsite | Variant of Subarray Sum Equals K |

### 3.2 Trees (VERY HIGH FREQUENCY at Meta)

| # | Problem | LC# | Difficulty | Frequency | Round | Follow-ups |
|---|---------|-----|------------|-----------|-------|------------|
| 1 | **Binary Tree Vertical Order Traversal** | 314 | Medium | **Very High** | Phone, Onsite | Vertical Order Traversal (LC 987 -- harder sorting rules) |
| 2 | **Lowest Common Ancestor of a Binary Tree** | 236 | Medium | **Very High** | Phone, Onsite | LCA of BST (LC 235); iterative solution; what if nodes have parent pointers? |
| 3 | **Binary Tree Right Side View** | 199 | Medium | Very High | Phone, Onsite | Left side view variant |
| 4 | **Diameter of Binary Tree** | 543 | Easy | Very High | Phone, Onsite | - |
| 5 | **Validate Binary Search Tree** | 98 | Medium | High | Onsite | - |
| 6 | **Serialize and Deserialize Binary Tree** | 297 | Hard | High | Onsite | BFS vs DFS approaches; handle N-ary tree |
| 7 | **Binary Tree Maximum Path Sum** | 124 | Hard | High | Onsite | - |
| 8 | **Lowest Common Ancestor of a Binary Search Tree** | 235 | Medium | High | Phone | Follow-up to LC 236 |
| 9 | **Binary Tree Level Order Traversal** | 102 | Medium | High | Phone, Onsite | Find min element in each level (reported variant) |
| 10 | **Invert Binary Tree** | 226 | Easy | Medium | Phone | - |
| 11 | **Range Sum of BST** | 938 | Easy | High | Phone | - |
| 12 | **Construct Binary Tree from Preorder and Inorder** | 105 | Medium | Medium | Onsite | - |
| 13 | **Flatten Binary Tree to Linked List** | 114 | Medium | Medium | Onsite | - |

### 3.3 Graphs & BFS/DFS (HIGH FREQUENCY at Meta)

| # | Problem | LC# | Difficulty | Frequency | Round | Follow-ups |
|---|---------|-----|------------|-----------|-------|------------|
| 1 | **Number of Islands** | 200 | Medium | Very High | Phone, Onsite | Number of Islands II (LC 305) |
| 2 | **Clone Graph** | 133 | Medium | High | Onsite | - |
| 3 | **Course Schedule** | 207 | Medium | High | Onsite | Course Schedule II (LC 210) -- return order |
| 4 | **Word Ladder** | 127 | Hard | Medium | Onsite | - |
| 5 | **Shortest Path in Binary Matrix** | 1091 | Medium | High | Onsite | Track and output the actual path |
| 6 | **Rotting Oranges** | 994 | Medium | High | Phone | - |
| 7 | **Accounts Merge** | 721 | Medium | High | Onsite | - |
| 8 | **Alien Dictionary** | 269 | Hard | Medium | Onsite | - |
| 9 | **Number of Connected Components** | 323 | Medium | High | Onsite | - |
| 10 | **Making A Large Island** | 827 | Hard | Medium | Onsite | - |
| 11 | **Course Schedule II** | 210 | Medium | High | Onsite | - |
| 12 | **Graph Valid Tree** | 261 | Medium | Medium | Onsite | - |
| 13 | **Remove Invalid Parentheses** | 301 | Hard | Medium | Onsite | BFS approach to find all valid results |
| 14 | **Walls and Gates** | 286 | Medium | Medium | Onsite | - |

### 3.4 Linked Lists

| # | Problem | LC# | Difficulty | Frequency | Round | Follow-ups |
|---|---------|-----|------------|-----------|-------|------------|
| 1 | **Reverse Linked List** | 206 | Easy | High | Phone | Reverse in groups of k |
| 2 | **Copy List with Random Pointer** | 138 | Medium | Very High | Onsite | Clone linked list with additional pointer |
| 3 | **Merge Two Sorted Lists** | 21 | Easy | High | Phone | Merge K Sorted Lists (LC 23) |
| 4 | **Reverse Nodes in k-Group** | 25 | Hard | High | Onsite | - |
| 5 | **LRU Cache** | 146 | Medium | Very High | Onsite | LFU Cache (LC 460) |
| 6 | **Reorder List** | 143 | Medium | Medium | Onsite | - |
| 7 | **Add Two Numbers** | 2 | Medium | High | Phone, Onsite | Add Two Numbers II (LC 445) |
| 8 | **Merge K Sorted Lists** | 23 | Hard | High | Onsite | Merge 3 sorted arrays (reported variant) |

### 3.5 Stack & Queue

| # | Problem | LC# | Difficulty | Frequency | Round | Follow-ups |
|---|---------|-----|------------|-----------|-------|------------|
| 1 | **Minimum Remove to Make Valid Parentheses** | 1249 | Medium | **Very High** | Phone, Onsite | (see Arrays section) |
| 2 | **Basic Calculator II** | 227 | Medium | Very High | Phone, Onsite | Basic Calculator (LC 224) |
| 3 | **Exclusive Time of Functions** | 636 | Medium | High | Onsite | - |
| 4 | **Valid Parentheses** | 20 | Easy | High | Phone | - |
| 5 | **Daily Temperatures** | 739 | Medium | Medium | Onsite | - |
| 6 | **Largest Rectangle in Histogram** | 84 | Hard | Medium | Onsite | Maximal Rectangle (LC 85) |
| 7 | **Generate Parentheses** | 22 | Medium | High | Phone, Onsite | - |

### 3.6 Two Pointers

| # | Problem | LC# | Difficulty | Frequency | Round | Follow-ups |
|---|---------|-----|------------|-----------|-------|------------|
| 1 | **3Sum** | 15 | Medium | High | Phone, Onsite | 4Sum, 3Sum Closest |
| 2 | **Container With Most Water** | 11 | Medium | High | Onsite | - |
| 3 | **Trapping Rain Water** | 42 | Hard | High | Onsite | Two-pointer vs. stack approach |
| 4 | **Valid Palindrome** | 125 | Easy | Very High | Phone | - |
| 5 | **Valid Palindrome II** | 680 | Easy | Very High | Phone | Remove at most k characters variant |
| 6 | **Two Sum** | 1 | Easy | High | Phone | Two Sum II (sorted input) |

### 3.7 Sliding Window

| # | Problem | LC# | Difficulty | Frequency | Round | Follow-ups |
|---|---------|-----|------------|-----------|-------|------------|
| 1 | **Longest Substring Without Repeating Characters** | 3 | Medium | Very High | Phone, Onsite | At most k distinct characters |
| 2 | **Minimum Window Substring** | 76 | Hard | High | Onsite | - |
| 3 | **Longest Repeating Character Replacement** | 424 | Medium | Medium | Onsite | - |
| 4 | **Sliding Window Maximum** | 239 | Hard | Medium | Onsite | Monotonic deque approach |

### 3.8 Heap / Priority Queue

| # | Problem | LC# | Difficulty | Frequency | Round | Follow-ups |
|---|---------|-----|------------|-----------|-------|------------|
| 1 | **Kth Largest Element in an Array** | 215 | Medium | Very High | Phone, Onsite | Quickselect vs. heap approach; follow-up on streaming data |
| 2 | **K Closest Points to Origin** | 973 | Medium | Very High | Phone, Onsite | - |
| 3 | **Top K Frequent Elements** | 347 | Medium | High | Phone, Onsite | - |
| 4 | **Merge K Sorted Lists** | 23 | Hard | High | Onsite | - |
| 5 | **Find Median from Data Stream** | 295 | Hard | High | Onsite | - |
| 6 | **Task Scheduler** | 621 | Medium | High | Onsite | - |
| 7 | **Reorganize String** | 767 | Medium | Medium | Onsite | - |

### 3.9 Hash Maps & Prefix Sum

| # | Problem | LC# | Difficulty | Frequency | Round | Follow-ups |
|---|---------|-----|------------|-----------|-------|------------|
| 1 | **Two Sum** | 1 | Easy | High | Phone | - |
| 2 | **Subarray Sum Equals K** | 560 | Medium | Very High | Phone, Onsite | Continuous Subarray Sum (LC 523) |
| 3 | **Continuous Subarray Sum** | 523 | Medium | High | Onsite | - |
| 4 | **Group Anagrams** | 49 | Medium | High | Onsite | - |
| 5 | **Maximum Size Subarray Sum Equals k** | 325 | Medium | Medium | Onsite | - |
| 6 | **Contiguous Array** | 525 | Medium | Medium | Onsite | - |
| 7 | **Range Sum Query 2D - Immutable** | 304 | Medium | Medium | Onsite | - |

### 3.10 Design / Data Structures

| # | Problem | LC# | Difficulty | Frequency | Round | Follow-ups |
|---|---------|-----|------------|-----------|-------|------------|
| 1 | **LRU Cache** | 146 | Medium | Very High | Onsite | LFU Cache (LC 460) |
| 2 | **Random Pick with Weight** | 528 | Medium | Very High | Onsite | Prefix sum + binary search approach |
| 3 | **Insert Delete GetRandom O(1)** | 380 | Medium | High | Onsite | - |
| 4 | **Dot Product of Two Sparse Vectors** | 1570 | Medium | Very High | Phone, Onsite | What if vectors are streaming? Use LinkedList/Map |
| 5 | **Design Hit Counter** | 362 | Medium | High | Onsite | - |
| 6 | **Design Twitter** | 355 | Medium | Medium | Onsite | - |
| 7 | **All O(1) Data Structure** | 432 | Hard | Medium | Onsite | - |
| 8 | **Design In-Memory File System** | 588 | Hard | Medium | Onsite | - |
| 9 | **Maximum Frequency Stack** | 895 | Hard | Medium | Onsite | - |
| 10 | **LFU Cache** | 460 | Hard | Medium | Onsite | - |

### 3.11 Binary Search

| # | Problem | LC# | Difficulty | Frequency | Round | Follow-ups |
|---|---------|-----|------------|-----------|-------|------------|
| 1 | **Search in Rotated Sorted Array** | 33 | Medium | High | Phone, Onsite | - |
| 2 | **Random Pick with Weight** | 528 | Medium | Very High | Onsite | Prefix sum + binary search |
| 3 | **Find First and Last Position of Element** | 34 | Medium | High | Phone | Given sorted array, find frequency of target |
| 4 | **Pow(x, n)** | 50 | Medium | High | Phone, Onsite | - |
| 5 | **Median of Two Sorted Arrays** | 4 | Hard | Medium | Onsite | - |

### 3.12 Intervals

| # | Problem | LC# | Difficulty | Frequency | Round | Follow-ups |
|---|---------|-----|------------|-----------|-------|------------|
| 1 | **Merge Intervals** | 56 | Medium | Very High | Phone, Onsite | - |
| 2 | **Insert Interval** | 57 | Medium | High | Onsite | - |
| 3 | **Meeting Rooms II** | 253 | Medium | High | Onsite | - |
| 4 | **Interval List Intersections** | 986 | Medium | High | Onsite | - |

### 3.13 Backtracking

| # | Problem | LC# | Difficulty | Frequency | Round | Follow-ups |
|---|---------|-----|------------|-----------|-------|------------|
| 1 | **Subsets** | 78 | Medium | High | Onsite | Subsets II (LC 90) |
| 2 | **Permutations** | 46 | Medium | High | Onsite | Permutations II (LC 47) |
| 3 | **Combination Sum** | 39 | Medium | Medium | Onsite | - |
| 4 | **Letter Combinations of a Phone Number** | 17 | Medium | High | Phone, Onsite | - |
| 5 | **Generate Parentheses** | 22 | Medium | High | Phone, Onsite | - |
| 6 | **Word Search** | 79 | Medium | Medium | Onsite | Word Search II (LC 212) |

### 3.14 Matrix / Grid

| # | Problem | LC# | Difficulty | Frequency | Round | Follow-ups |
|---|---------|-----|------------|-----------|-------|------------|
| 1 | **Toeplitz Matrix** | 766 | Easy | High | Phone | Efficient streaming approach |
| 2 | **Spiral Matrix** | 54 | Medium | Medium | Onsite | - |
| 3 | **Set Matrix Zeroes** | 73 | Medium | Medium | Onsite | - |
| 4 | **Rotate Image** | 48 | Medium | Medium | Onsite | - |
| 5 | **Diagonal Traverse** | 498 | Medium | Medium | Onsite | - |

### 3.15 Greedy

| # | Problem | LC# | Difficulty | Frequency | Round | Follow-ups |
|---|---------|-----|------------|-----------|-------|------------|
| 1 | **Merge Intervals** | 56 | Medium | Very High | Phone, Onsite | - |
| 2 | **Task Scheduler** | 621 | Medium | High | Onsite | - |
| 3 | **Jump Game** | 55 | Medium | Medium | Onsite | - |
| 4 | **Maximum Subarray** | 53 | Medium | High | Phone | - |

### 3.16 Dynamic Programming (RARE at Meta in 2025)

**Important Note:** Multiple sources confirm Meta has moved away from DP questions. However, these may still appear occasionally:

| # | Problem | LC# | Difficulty | Frequency | Round | Notes |
|---|---------|-----|------------|-----------|-------|-------|
| 1 | **Word Break** | 139 | Medium | Low-Medium | Onsite | Still occasionally asked |
| 2 | **Longest Increasing Subsequence** | 300 | Medium | Low | Onsite | - |
| 3 | **Coin Change** | 322 | Medium | Low | Onsite | - |
| 4 | **Edit Distance** | 72 | Medium | Low | Onsite | - |
| 5 | **Decode Ways** | 91 | Medium | Low | Onsite | - |

### 3.17 Recursion / Other

| # | Problem | LC# | Difficulty | Frequency | Round | Follow-ups |
|---|---------|-----|------------|-----------|-------|------------|
| 1 | **Nested List Weight Sum** | 339 | Medium | High | Phone, Onsite | Nested List Weight Sum II (LC 364) |
| 2 | **Pow(x, n)** | 50 | Medium | High | Phone | - |
| 3 | **Buildings with an Ocean View** | 1762 | Medium | Very High | Phone | O(n) required; monotonic stack approach |
| 4 | **Palindrome Pairs** | 336 | Hard | Medium | Onsite | - |

---

## 4. Frequency Analysis -- Most Commonly Asked Problems

### Tier 1: Must-Know (Asked Extremely Frequently -- Reported 10+ times)

| Rank | Problem | LC# | Difficulty | Pattern |
|------|---------|-----|------------|---------|
| 1 | Minimum Remove to Make Valid Parentheses | 1249 | Medium | Stack/String |
| 2 | Binary Tree Vertical Order Traversal | 314 | Medium | BFS/Tree |
| 3 | Lowest Common Ancestor of a Binary Tree | 236 | Medium | Tree/DFS |
| 4 | Buildings with an Ocean View | 1762 | Medium | Monotonic Stack |
| 5 | Valid Palindrome II | 680 | Easy | Two Pointers |
| 6 | Dot Product of Two Sparse Vectors | 1570 | Medium | Design/Array |
| 7 | Basic Calculator II | 227 | Medium | Stack |
| 8 | Random Pick with Weight | 528 | Medium | Binary Search/Prefix Sum |
| 9 | Subarray Sum Equals K | 560 | Medium | Prefix Sum/HashMap |
| 10 | Product of Array Except Self | 238 | Medium | Array |

### Tier 2: Very Important (Asked Frequently -- Reported 5-10 times)

| Rank | Problem | LC# | Difficulty | Pattern |
|------|---------|-----|------------|---------|
| 11 | LRU Cache | 146 | Medium | Design |
| 12 | Kth Largest Element in an Array | 215 | Medium | Heap |
| 13 | Binary Tree Right Side View | 199 | Medium | BFS/Tree |
| 14 | K Closest Points to Origin | 973 | Medium | Heap |
| 15 | Merge Intervals | 56 | Medium | Intervals/Greedy |
| 16 | Number of Islands | 200 | Medium | BFS/DFS |
| 17 | Copy List with Random Pointer | 138 | Medium | Linked List |
| 18 | Longest Substring Without Repeating Characters | 3 | Medium | Sliding Window |
| 19 | Group Anagrams | 49 | Medium | Hash Map |
| 20 | Valid Palindrome | 125 | Easy | Two Pointers |

### Tier 3: Important (Asked Regularly -- Reported 3-5 times)

| Rank | Problem | LC# | Difficulty | Pattern |
|------|---------|-----|------------|---------|
| 21 | Continuous Subarray Sum | 523 | Medium | Prefix Sum |
| 22 | Add Strings | 415 | Easy | String |
| 23 | Nested List Weight Sum | 339 | Medium | Recursion/DFS |
| 24 | Clone Graph | 133 | Medium | BFS/DFS |
| 25 | Toeplitz Matrix | 766 | Easy | Matrix |
| 26 | Range Sum of BST | 938 | Easy | Tree |
| 27 | Diameter of Binary Tree | 543 | Easy | Tree |
| 28 | Move Zeroes | 283 | Easy | Two Pointers |
| 29 | Insert Delete GetRandom O(1) | 380 | Medium | Design |
| 30 | 3Sum | 15 | Medium | Two Pointers |
| 31 | Reverse Nodes in k-Group | 25 | Hard | Linked List |
| 32 | Serialize and Deserialize Binary Tree | 297 | Hard | Tree |
| 33 | Merge K Sorted Lists | 23 | Hard | Heap/Linked List |
| 34 | Top K Frequent Elements | 347 | Medium | Heap/Hash Map |
| 35 | Accounts Merge | 721 | Medium | Union-Find/Graph |
| 36 | Next Permutation | 31 | Medium | Array |
| 37 | Letter Combinations of a Phone Number | 17 | Medium | Backtracking |
| 38 | Meeting Rooms II | 253 | Medium | Intervals |
| 39 | Exclusive Time of Functions | 636 | Medium | Stack |
| 40 | Custom Sort String | 791 | Medium | Hash Map/String |

---

## 5. Problems NOT Currently in Your Database That Should Be Added

After comparing the research findings against your current `seed_data.py` and `add_hard_problems.py`, the following high-frequency Meta problems are **MISSING** from your database:

### Critical Additions (Tier 1 -- Must Add)

| Problem | LC# | Difficulty | Pattern | Why Critical |
|---------|-----|------------|---------|--------------|
| **Minimum Remove to Make Valid Parentheses** | 1249 | Medium | Stack/String | #1 most asked Meta question in 2025 |
| **Binary Tree Vertical Order Traversal** | 314 | Medium | BFS/Tree | #2 most asked Meta question |
| **Buildings with an Ocean View** | 1762 | Medium | Monotonic Stack | #4 most asked, classic Meta phone screen |
| **Valid Palindrome II** | 680 | Easy | Two Pointers | #5 most asked, frequent phone screen |
| **Dot Product of Two Sparse Vectors** | 1570 | Medium | Design/Array | #6 most asked, Meta signature problem |
| **K Closest Points to Origin** | 973 | Medium | Heap | Top 15, very frequently asked |
| **Add Strings** | 415 | Easy | String/Math | Frequently paired with other problems |
| **Toeplitz Matrix** | 766 | Easy | Matrix | Common Meta phone screen starter |
| **Nested List Weight Sum** | 339 | Medium | DFS/Recursion | Frequently asked at Meta |
| **Add Two Numbers** | 2 | Medium | Linked List | Classic Meta problem |

### Important Additions (Tier 2 -- Should Add)

| Problem | LC# | Difficulty | Pattern | Why Important |
|---------|-----|------------|---------|---------------|
| **Move Zeroes** | 283 | Easy | Two Pointers/Array | Common phone screen warm-up |
| **Two Sum** | 1 | Easy | Hash Map | Foundation problem, often warm-up |
| **Range Sum of BST** | 938 | Easy | Tree | Common easy tree question |
| **Lowest Common Ancestor of a BST** | 235 | Medium | Tree | Follow-up to LC 236 |
| **Contiguous Array** | 525 | Medium | Prefix Sum/Hash Map | Frequently asked |
| **Find First and Last Position of Element** | 34 | Medium | Binary Search | "Find frequency of target" variant |
| **Letter Combinations of a Phone Number** | 17 | Medium | Backtracking | Frequently asked |
| **Multiply Strings** | 43 | Medium | String/Math | Follow-up to Add Strings |
| **Exclusive Time of Functions** | 636 | Medium | Stack | Meta-specific problem |
| **Custom Sort String** | 791 | Medium | Hash Map/String | Meta-specific problem |
| **Walls and Gates** | 286 | Medium | BFS | Meta-specific BFS problem |
| **Interval List Intersections** | 986 | Medium | Two Pointers/Intervals | Commonly asked |
| **Pow(x, n)** | 50 | Medium | Math/Recursion | Common Meta problem |
| **Flatten Binary Tree to Linked List** | 114 | Medium | Tree | Common tree manipulation |
| **Diagonal Traverse** | 498 | Medium | Matrix | Meta-specific matrix problem |
| **Simplify Path** | 71 | Medium | Stack/String | Meta-specific stack problem |
| **Valid Parentheses** | 20 | Easy | Stack | Foundation problem |
| **Longest Repeating Character Replacement** | 424 | Medium | Sliding Window | Important sliding window |
| **Palindrome Pairs** | 336 | Hard | Trie/Hash Map | Advanced Meta problem |
| **Maximum Size Subarray Sum Equals k** | 325 | Medium | Prefix Sum | Meta prefix sum problem |
| **Decode Ways** | 91 | Medium | DP | Occasionally asked |
| **Binary Tree Level Order Traversal** | 102 | Medium | BFS | "Min element per level" variant |
| **Nested List Weight Sum II** | 364 | Medium | DFS | Follow-up to LC 339 |

---

## 6. Pattern Gap Analysis

### Patterns in Your Database vs. What Meta Actually Asks

| Pattern | In Your DB? | Meta Frequency | Gap Assessment |
|---------|-------------|----------------|----------------|
| Stack/Parentheses | Partial | **Very High** | **CRITICAL GAP** -- Missing LC 1249 (most asked!), LC 636, LC 71 |
| Trees (LCA, Vertical Order) | Partial | **Very High** | **CRITICAL GAP** -- Missing LC 314, LC 1762, LC 938, LC 235 |
| Design (Sparse Vectors, Random Pick) | Partial | Very High | **GAP** -- Missing LC 1570 (Sparse Vectors) |
| Two Pointers (Palindrome variants) | Partial | Very High | **GAP** -- Missing LC 680 (Valid Palindrome II) |
| String/Math (Add/Multiply) | Minimal | High | **GAP** -- Missing LC 415, LC 43, LC 283 |
| Matrix/Grid (Toeplitz) | Good | Medium-High | Minor gap -- LC 766 missing |
| Prefix Sum | Good (added) | High | Adequate coverage |
| Sliding Window | Good | High | Adequate -- consider adding LC 424 |
| BFS/DFS | Good | High | Minor gap -- LC 286 (Walls and Gates) |
| Heap | Good | High | Minor gap -- LC 973 (K Closest Points) |
| Intervals | Good | Medium-High | Minor gap -- LC 986 |
| Backtracking | Good | Medium | Minor gap -- LC 17 |
| Dynamic Programming | Heavy | **LOW at Meta** | **OVER-REPRESENTED** -- You have 12 DP problems but Meta rarely asks DP |
| Union-Find | Good | Medium | Adequate |
| Bit Manipulation | Good | Low at Meta | Over-represented for Meta prep |
| Trie | Good | Low-Medium | Adequate |

### Key Recommendations

1. **URGENT**: Add the "Stack/Parentheses" cluster (LC 1249, 636, 71) -- this is Meta's #1 question category
2. **URGENT**: Add the "Meta Trees" cluster (LC 314, 1762, 938, 235) -- these are signature Meta tree problems
3. **URGENT**: Add LC 1570 (Dot Product of Sparse Vectors) -- signature Meta design problem
4. **HIGH**: Add LC 680 (Valid Palindrome II) -- extremely common phone screen question
5. **HIGH**: Add string math problems (LC 415, 43) -- common phone screen pairing
6. **ADJUST**: De-emphasize DP problems for Meta prep -- Meta has moved away from DP
7. **ADJUST**: De-emphasize Bit Manipulation for Meta prep -- rarely asked at Meta

---

## 7. Common Follow-Up Questions and Variations

### Reported Meta Interview Variations (2025)

| Original Problem | Variation/Follow-up |
|-----------------|---------------------|
| Minimum Remove to Make Valid Parentheses (1249) | "What if you have multiple types of brackets?"; "Return the count of removed brackets"; "Handle nested brackets with priorities" |
| Binary Tree Vertical Order (314) | Vertical Order Traversal with stricter sorting (LC 987) |
| Lowest Common Ancestor (236) | "What if nodes have parent pointers?"; "Iterative solution?"; "What if it is a BST?" |
| Buildings with Ocean View (1762) | "What if the ocean is on both sides?" |
| Dot Product Sparse Vectors (1570) | "What if vectors are very large and streaming?"; "Use LinkedList/Map for non-zero elements" |
| Binary Tree Right Side View (199) | "Return the left side view instead" |
| Kth Largest Element (215) | "Use quickselect"; "What about streaming data?" |
| Subarray Sum Equals K (560) | "What about continuous subarray with sum divisible by k?" (LC 523) |
| Add Strings (415) | "Now multiply two strings" (LC 43) |
| Binary Tree Level Order (102) | "Find minimum element in each level" (reported variant) |
| Shortest Path in Binary Matrix (1091) | "Track and output the actual path" |
| Merge Sorted Arrays | "Merge three sorted arrays without duplicates" (reported variant) |
| Product of Array Except Self (238) | "Do it without division"; "O(1) space" |
| Basic Calculator II (227) | "Add parentheses support" (LC 224); "Handle unary minus" |
| LRU Cache (146) | "Implement LFU Cache" (LC 460) |
| Toeplitz Matrix (766) | "Efficient streaming approach for large matrix" |
| Valid Palindrome II (680) | "What if you can remove at most k characters?" |
| Subsets (78) | "What if there are duplicates?" (LC 90) |

---

## 8. Meta's Preferred Interview Patterns (2025) -- Ranked

Based on analysis of 180+ interview experiences and multiple frequency lists:

| Rank | Pattern | Approximate % of Questions | Trend |
|------|---------|---------------------------|-------|
| 1 | **Arrays & Strings** | 25-30% | Stable |
| 2 | **Trees & Binary Trees** | 20-25% | Increasing |
| 3 | **BFS/DFS (Graphs & Trees)** | 15-20% | Stable |
| 4 | **Hash Maps & Prefix Sums** | 10-15% | Increasing |
| 5 | **Stack / Queue** | 8-10% | Increasing |
| 6 | **Heap / Priority Queue** | 5-8% | Stable |
| 7 | **Linked Lists** | 5-8% | Stable |
| 8 | **Two Pointers** | 5-8% | Stable |
| 9 | **Sliding Window** | 3-5% | Stable |
| 10 | **Binary Search** | 3-5% | Stable |
| 11 | **Design / Data Structures** | 3-5% | Increasing |
| 12 | **Intervals** | 2-3% | Stable |
| 13 | **Backtracking** | 2-3% | Stable |
| 14 | **Greedy** | 1-2% | Stable |
| 15 | **Dynamic Programming** | <1% | **Declining** |
| 16 | **Union-Find** | <1% | Stable |

---

## 9. Complete Research Sources

### Primary Sources Consulted

- [Meta's Most Asked 73 LeetCode Problems (Medium)](https://medium.com/@johnadjanohoun/metas-most-asked-coding-interview-questions-the-complete-list-of-73-leetcode-problems-47e96767adc7)
- [Meta Coding Interview Guide 2025 - E4, E5, E6 (TeamBlind)](https://www.teamblind.com/post/meta-coding-interview-guide-in-2025-e4-e5-e6-nfdaffpb)
- [Meta AI-Enabled Coding Interview Guide (HelloInterview)](https://www.hellointerview.com/blog/meta-ai-enabled-coding)
- [Meta AI-Enabled Coding Interview (Coditioning)](https://www.coditioning.com/blog/13/meta-ai-enabled-coding-interview-guide)
- [Meta Coding Interview Questions (IGotAnOffer)](https://igotanoffer.com/en/advice/meta-coding-interviews)
- [Senior Engineer's Guide to Meta Interviews (Interviewing.io)](https://interviewing.io/guides/hiring-process/meta-facebook)
- [How to Use AI in Meta's AI-Assisted Coding Interview (Interviewing.io)](https://interviewing.io/blog/how-to-use-ai-in-meta-s-ai-assisted-coding-interview-with-real-prompts-and-examples)
- [Meta Coding Interview Questions Updated 2026 (Exponent)](https://www.tryexponent.com/questions?company=facebook&type=coding)
- [Top 30 Meta LeetCode Questions (VerveCopilot)](https://www.vervecopilot.com/hot-blogs/meta-leetcode-interview-questions)
- [Meta DS & Algo Roadmap 2025 (Medium)](https://medium.com/@prashant558908/meta-facebook-ds-algo-interview-preparation-roadmap-2025-e4b65b30a20e)
- [Top 20 Coding Questions for Meta (DesignGurus)](https://www.designgurus.io/blog/top-20-coding-questions-to-pass-meta-interview)
- [Meta Interview Questions & Experiences 2026 - 180+ Stories (CodingKaro)](https://www.codingkaro.in/jobs-internships/leetcode-interview-experience/Meta)
- [Meta SWE Interview Questions (Onsites.fyi)](https://www.onsites.fyi/blog/article/meta-software-engineer-interview-questions-technical)
- [Meta Interview Questions (InterviewSolver)](https://interviewsolver.com/interview-questions/meta)
- [Facebook(Meta) SDE Sheet (GeeksForGeeks)](https://www.geeksforgeeks.org/dsa/facebookmeta-sde-sheet-interview-questions-and-answers/)
- [LeetCode Meta Phone Screen Discussions](https://leetcode.com/discuss/post/4777086/Meta-Phone-Screen-Round/)
- [Meta E5 Offer Experience (Medium)](https://medium.com/@amukul82/my-meta-interview-experience-e5-offer-44f9816cf9e6)
- [Meta Variant Compilation - LeetCode Discuss](https://leetcode.com/discuss/post/6615244/meta-variant-compilation-by-codingwithmi-0pm7/)
- [Meta 1249 Variants - LeetCode Discuss](https://leetcode.com/discuss/interview-question/6147201/Meta's-Asked-Variants-for-Leetcode-1249-(Min-Remove-to-Make-Valid-Parentheses)/)
- [Meta Full Interview Experience Sept-Oct 2025 - LeetCode Discuss](https://leetcode.com/discuss/interview-experience/7357112/)
- [LeetCode Company Wise Questions (GitHub)](https://github.com/krishnadey30/LeetCode-Questions-CompanyWise)
- [Facebook Interview LeetCode Prep (GitHub Gist)](https://gist.github.com/fielding/8e22a9e8c2eb4c707f10d3a2b5db59c7)
- [Meta Software Engineer Interview (Glassdoor)](https://www.glassdoor.com/Interview/Meta-Software-Engineer-Interview-Questions-EI_IE40772.0,4_KO5,22.htm)
- [Meta Technical Interview Questions 2026 Guide (Jobright)](https://jobright.ai/blog/meta-technical-interview-questions-complete-2026-guide/)
- [Meta Interview Guide 2026 OA & Coding Assessment (Shadecoder)](https://www.shadecoder.com/blogs/meta-interview-guide-2026-oa-coding-assessment-prep)
- [Meta Software Engineer Interview (Prepfully)](https://prepfully.com/interview-guides/meta-software-engineer)

---

## 10. Summary Action Items

### Immediate Priorities for Meta Preparation

1. **Master LC 1249** (Minimum Remove to Make Valid Parentheses) -- learn all variants
2. **Master LC 314** (Binary Tree Vertical Order Traversal) -- know BFS approach cold
3. **Master LC 236** (Lowest Common Ancestor) -- know BST variant (LC 235) too
4. **Master LC 1762** (Buildings with Ocean View) -- O(n) monotonic stack approach
5. **Master LC 1570** (Dot Product Sparse Vectors) -- know streaming variant
6. **Master LC 680** (Valid Palindrome II) -- common phone screen warm-up
7. **Master LC 227** (Basic Calculator II) -- know LC 224 follow-up
8. **Master LC 528** (Random Pick with Weight) -- prefix sum + binary search
9. **Practice the AI-enabled round format** -- request practice CoderPad from recruiter
10. **De-prioritize DP** for Meta specifically (still important for other companies)

### Study Time Allocation for Meta-Specific Prep

| Category | Recommended Time | Your Current Coverage |
|----------|-----------------|----------------------|
| Trees (LCA, Vertical Order, BST) | 25% | Partial -- needs LC 314, 1762, 938 |
| Arrays/Strings/Stack | 25% | Partial -- needs LC 1249, 415, 680 |
| BFS/DFS/Graphs | 15% | Good |
| Hash Maps/Prefix Sums | 10% | Good after additions |
| Design/Data Structures | 10% | Partial -- needs LC 1570 |
| Heap/Priority Queue | 5% | Good after LC 973 |
| Linked Lists | 5% | Good |
| Other (Intervals, Backtracking, etc.) | 5% | Good |
