"""Seed the database with problems, topics, and study plan from research files."""

from data.db import get_conn, init_db, is_seeded


def seed_all():
    """Populate database with initial data from research."""
    init_db()
    if is_seeded():
        return
    _seed_coding_problems()
    _seed_system_design()
    _seed_behavioral_questions()
    _seed_study_plan()


def _seed_coding_problems():
    problems = [
        # ── Two Pointers ──
        ("Two Pointers", "Two Sum II - Input Array Is Sorted", 167, "Easy", "Microsoft"),
        ("Two Pointers", "3Sum", 15, "Medium", "Meta, Uber"),
        ("Two Pointers", "Container With Most Water", 11, "Medium", "Meta, Microsoft"),
        ("Two Pointers", "Trapping Rain Water", 42, "Hard", "Meta, Uber, Microsoft"),
        # ── Sliding Window ──
        ("Sliding Window", "Best Time to Buy and Sell Stock", 121, "Easy", "All"),
        ("Sliding Window", "Longest Substring Without Repeating Characters", 3, "Medium", "Meta, Uber, Microsoft"),
        ("Sliding Window", "Minimum Window Substring", 76, "Hard", "Meta, Microsoft"),
        ("Sliding Window", "Sliding Window Maximum", 239, "Hard", "Uber, Microsoft"),
        # ── Binary Search ──
        ("Binary Search", "Binary Search", 704, "Easy", "All"),
        ("Binary Search", "Find Minimum in Rotated Sorted Array", 153, "Medium", "Microsoft, Uber"),
        ("Binary Search", "Search in Rotated Sorted Array", 33, "Medium", "Meta, Microsoft"),
        ("Binary Search", "Median of Two Sorted Arrays", 4, "Hard", "Meta, Microsoft"),
        ("Binary Search", "Koko Eating Bananas", 875, "Medium", "Uber, Meta"),
        ("Binary Search", "Split Array Largest Sum", 410, "Hard", "Microsoft"),
        # ── BFS ──
        ("BFS", "Binary Tree Level Order Traversal", 102, "Medium", "All"),
        ("BFS", "Rotting Oranges", 994, "Medium", "Meta, Uber"),
        ("BFS", "Word Ladder", 127, "Hard", "Meta, Microsoft"),
        ("BFS", "Shortest Path in Binary Matrix", 1091, "Medium", "Meta"),
        ("BFS", "Open the Lock", 752, "Medium", "Microsoft"),
        # ── DFS ──
        ("DFS", "Number of Islands", 200, "Medium", "Meta, Uber"),
        ("DFS", "Clone Graph", 133, "Medium", "Meta, Microsoft"),
        ("DFS", "Course Schedule", 207, "Medium", "Meta, Uber"),
        ("DFS", "Alien Dictionary", 269, "Hard", "Meta, Uber, Microsoft"),
        ("DFS", "Number of Connected Components", 323, "Medium", "Meta, Microsoft"),
        # ── Dynamic Programming ──
        ("Dynamic Programming", "Climbing Stairs", 70, "Easy", "All"),
        ("Dynamic Programming", "House Robber", 198, "Medium", "Meta, Uber"),
        ("Dynamic Programming", "Longest Increasing Subsequence", 300, "Medium", "Microsoft, Meta"),
        ("Dynamic Programming", "Word Break", 139, "Medium", "Meta, Microsoft"),
        ("Dynamic Programming", "Unique Paths", 62, "Medium", "Microsoft"),
        ("Dynamic Programming", "Longest Common Subsequence", 1143, "Medium", "Microsoft, Uber"),
        ("Dynamic Programming", "Edit Distance", 72, "Medium", "Meta, Microsoft"),
        ("Dynamic Programming", "Regular Expression Matching", 10, "Hard", "Meta"),
        ("Dynamic Programming", "Partition Equal Subset Sum", 416, "Medium", "Meta"),
        ("Dynamic Programming", "Coin Change", 322, "Medium", "Meta, Uber, Microsoft"),
        ("Dynamic Programming", "Target Sum", 494, "Medium", "Meta"),
        ("Dynamic Programming", "Best Time to Buy and Sell Stock with Cooldown", 309, "Medium", "Meta"),
        ("Dynamic Programming", "Burst Balloons", 312, "Hard", "Microsoft"),
        # ── Backtracking ──
        ("Backtracking", "Subsets", 78, "Medium", "Meta, Microsoft"),
        ("Backtracking", "Permutations", 46, "Medium", "Meta, Microsoft"),
        ("Backtracking", "Combination Sum", 39, "Medium", "Meta"),
        ("Backtracking", "N-Queens", 51, "Hard", "Microsoft"),
        ("Backtracking", "Word Search", 79, "Medium", "Meta"),
        ("Backtracking", "Generate Parentheses", 22, "Medium", "Meta, Microsoft"),
        # ── Greedy ──
        ("Greedy", "Maximum Subarray", 53, "Medium", "All"),
        ("Greedy", "Jump Game", 55, "Medium", "Meta"),
        ("Greedy", "Task Scheduler", 621, "Medium", "Meta"),
        ("Greedy", "Merge Intervals", 56, "Medium", "Meta, Uber, Microsoft"),
        ("Greedy", "Non-overlapping Intervals", 435, "Medium", "Uber"),
        ("Greedy", "Gas Station", 134, "Medium", "Microsoft"),
        # ── Graph Algorithms ──
        ("Graph Algorithms", "Course Schedule II", 210, "Medium", "Meta, Uber"),
        ("Graph Algorithms", "Network Delay Time", 743, "Medium", "Uber, Microsoft"),
        ("Graph Algorithms", "Cheapest Flights Within K Stops", 787, "Medium", "Uber"),
        ("Graph Algorithms", "Graph Valid Tree", 261, "Medium", "Meta"),
        ("Graph Algorithms", "Is Graph Bipartite?", 785, "Medium", "Microsoft"),
        ("Graph Algorithms", "Reconstruct Itinerary", 332, "Hard", "Uber"),
        # ── Trie ──
        ("Trie", "Implement Trie", 208, "Medium", "All"),
        ("Trie", "Design Add and Search Words", 211, "Medium", "Meta"),
        ("Trie", "Word Search II", 212, "Hard", "Meta, Microsoft"),
        ("Trie", "Search Suggestions System", 1268, "Medium", "Microsoft"),
        # ── Union-Find ──
        ("Union-Find", "Number of Connected Components in Undirected Graph", 323, "Medium", "Meta"),
        ("Union-Find", "Redundant Connection", 684, "Medium", "Microsoft"),
        ("Union-Find", "Accounts Merge", 721, "Medium", "Meta"),
        ("Union-Find", "Smallest String With Swaps", 1202, "Medium", "Microsoft"),
        # ── Monotonic Stack ──
        ("Monotonic Stack", "Daily Temperatures", 739, "Medium", "Meta"),
        ("Monotonic Stack", "Next Greater Element I", 496, "Easy", "Microsoft"),
        ("Monotonic Stack", "Largest Rectangle in Histogram", 84, "Hard", "Meta, Microsoft"),
        ("Monotonic Stack", "Sliding Window Maximum", 239, "Hard", "Uber, Microsoft"),
        ("Monotonic Stack", "Maximal Rectangle", 85, "Hard", "Meta"),
        # ── Topological Sort ──
        ("Topological Sort", "Course Schedule", 207, "Medium", "Meta, Uber"),
        ("Topological Sort", "Course Schedule II", 210, "Medium", "Meta, Uber"),
        ("Topological Sort", "Alien Dictionary", 269, "Hard", "Meta, Uber"),
        ("Topological Sort", "Parallel Courses", 1136, "Medium", "Microsoft"),
        # ── Heap / Priority Queue ──
        ("Heap / Priority Queue", "Kth Largest Element in an Array", 215, "Medium", "Meta"),
        ("Heap / Priority Queue", "Top K Frequent Elements", 347, "Medium", "Meta, Uber"),
        ("Heap / Priority Queue", "Merge K Sorted Lists", 23, "Hard", "Meta, Microsoft"),
        ("Heap / Priority Queue", "Find Median from Data Stream", 295, "Hard", "Meta, Microsoft"),
        ("Heap / Priority Queue", "Task Scheduler", 621, "Medium", "Meta"),
        ("Heap / Priority Queue", "Reorganize String", 767, "Medium", "Meta"),
        # ── Intervals ──
        ("Intervals", "Merge Intervals", 56, "Medium", "Meta, Uber"),
        ("Intervals", "Insert Interval", 57, "Medium", "Meta, Microsoft"),
        ("Intervals", "Meeting Rooms II", 253, "Medium", "Meta, Uber, Microsoft"),
        ("Intervals", "Non-overlapping Intervals", 435, "Medium", "Uber"),
        ("Intervals", "Employee Free Time", 759, "Hard", "Uber"),
        # ── Linked List ──
        ("Linked List", "Reverse Linked List", 206, "Easy", "All"),
        ("Linked List", "Linked List Cycle", 141, "Easy", "Microsoft"),
        ("Linked List", "Merge Two Sorted Lists", 21, "Easy", "Meta, Microsoft"),
        ("Linked List", "Reorder List", 143, "Medium", "Meta"),
        ("Linked List", "LRU Cache", 146, "Medium", "Meta, Uber, Microsoft"),
        ("Linked List", "Copy List with Random Pointer", 138, "Medium", "Meta"),
        ("Linked List", "Reverse Nodes in k-Group", 25, "Hard", "Meta, Microsoft"),
        # ── Trees ──
        ("Trees", "Invert Binary Tree", 226, "Easy", "All"),
        ("Trees", "Lowest Common Ancestor of a Binary Tree", 236, "Medium", "Meta"),
        ("Trees", "Validate Binary Search Tree", 98, "Medium", "Meta, Microsoft"),
        ("Trees", "Binary Tree Right Side View", 199, "Medium", "Meta"),
        ("Trees", "Serialize and Deserialize Binary Tree", 297, "Hard", "Meta, Microsoft"),
        ("Trees", "Binary Tree Maximum Path Sum", 124, "Hard", "Meta"),
        ("Trees", "Diameter of Binary Tree", 543, "Easy", "Meta"),
        ("Trees", "Construct Binary Tree from Preorder and Inorder", 105, "Medium", "Microsoft"),
        # ── Bit Manipulation ──
        ("Bit Manipulation", "Single Number", 136, "Easy", "Microsoft"),
        ("Bit Manipulation", "Number of 1 Bits", 191, "Easy", "Microsoft"),
        ("Bit Manipulation", "Counting Bits", 338, "Easy", "Microsoft"),
        ("Bit Manipulation", "Reverse Bits", 190, "Easy", "Microsoft"),
        ("Bit Manipulation", "Sum of Two Integers", 371, "Medium", "Meta"),
        # ── String / Array ──
        ("String / Array", "Valid Palindrome", 125, "Easy", "Meta"),
        ("String / Array", "Group Anagrams", 49, "Medium", "Meta"),
        ("String / Array", "Longest Palindromic Substring", 5, "Medium", "Meta"),
        ("String / Array", "Encode and Decode Strings", 271, "Medium", "Meta"),
        ("String / Array", "Product of Array Except Self", 238, "Medium", "Meta, Microsoft"),
        ("String / Array", "Basic Calculator II", 227, "Medium", "Meta"),
        # ── Design / Data Structure ──
        ("Design / Data Structure", "LRU Cache", 146, "Medium", "Meta, Uber, Microsoft"),
        ("Design / Data Structure", "Min Stack", 155, "Medium", "Microsoft"),
        ("Design / Data Structure", "Design Twitter", 355, "Medium", "Meta"),
        ("Design / Data Structure", "Design Hit Counter", 362, "Medium", "Meta, Uber"),
        ("Design / Data Structure", "LFU Cache", 460, "Hard", "Meta"),
        ("Design / Data Structure", "Time Based Key-Value Store", 981, "Medium", "Uber"),
        ("Design / Data Structure", "Random Pick with Weight", 528, "Medium", "Meta"),
        ("Design / Data Structure", "Insert Delete GetRandom O(1)", 380, "Medium", "Meta, Uber"),
    ]

    with get_conn() as conn:
        conn.executemany(
            """INSERT OR IGNORE INTO coding_problems
               (pattern, title, leetcode_num, difficulty, company_tags, url)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [
                (p, t, lc, d, co, f"https://leetcode.com/problems/{t.lower().replace(' ', '-').replace('(', '').replace(')', '')}/")
                for p, t, lc, d, co in problems
            ],
        )


def _seed_system_design():
    topics = [
        # Core 25
        ("Design a URL Shortener (TinyURL)", "core", "Meta, Microsoft, All"),
        ("Design a News Feed / Timeline", "core", "Meta"),
        ("Design a Chat/Messaging System", "core", "Meta, Uber"),
        ("Design a Rate Limiter", "core", "Meta, Uber, Microsoft"),
        ("Design a Web Crawler", "core", "Microsoft, Meta"),
        ("Design a Notification System", "core", "Meta, Uber"),
        ("Design a Ride-Sharing Service", "core", "Uber"),
        ("Design a Real-Time Location Tracking System", "core", "Uber"),
        ("Design a Distributed Cache", "core", "Meta, Microsoft"),
        ("Design Search Autocomplete / Typeahead", "core", "Meta, Microsoft"),
        ("Design a Distributed Key-Value Store", "core", "Meta, Microsoft, AI companies"),
        ("Design a Content Delivery Network (CDN)", "core", "Meta, Microsoft"),
        ("Design YouTube / Netflix (Video Streaming)", "core", "Meta, Microsoft"),
        ("Design Google Maps / Proximity Service", "core", "Uber, Microsoft"),
        ("Design a Distributed Task Scheduler", "core", "Uber, Meta, AI companies"),
        ("Design a Metrics/Monitoring System", "core", "Uber, Meta, AI companies"),
        ("Design a Distributed Log System (Kafka)", "core", "Uber, Meta"),
        ("Design an Object Storage System (S3)", "core", "Microsoft, AI companies"),
        ("Design a Container Orchestration System", "core", "Microsoft, AI companies"),
        ("Design a Load Balancer", "core", "Microsoft, Uber"),
        ("Design an Ad Click Aggregation System", "core", "Meta"),
        ("Design a Hotel/Restaurant Reservation System", "core", "Uber, Microsoft"),
        ("Design a Distributed File System (GFS/HDFS)", "core", "Meta, Microsoft"),
        ("Design an ML Feature Store / Training Pipeline", "ml_infra", "AI companies"),
        ("Design a Multi-Region Deployment System", "core", "Meta, Microsoft, Uber"),
        # EKS-Specific (9)
        ("Design a Container Orchestration System (K8s Deep Dive)", "eks_specific", "Microsoft, AI companies"),
        ("Design a Control Plane", "eks_specific", "Microsoft, AI companies"),
        ("Design a Data Plane", "eks_specific", "Microsoft, AI companies"),
        ("Design a Service Mesh", "eks_specific", "Microsoft, Uber"),
        ("Design a Cloud Load Balancer", "eks_specific", "Microsoft, Uber"),
        ("Design an Auto-Scaling System", "eks_specific", "Microsoft, AI companies"),
        ("Design a Cluster Scheduler", "eks_specific", "Microsoft, AI companies"),
        ("Design a Container Registry", "eks_specific", "Microsoft"),
        ("Design a Multi-Tenant Kubernetes Platform", "eks_specific", "Microsoft, AI companies"),
    ]

    with get_conn() as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO system_design (title, category, company_tags) VALUES (?, ?, ?)",
            topics,
        )


def _seed_behavioral_questions():
    questions = [
        # Leadership
        ("leadership", "Drive a cross-team technical initiative",
         "Tell me about a time you drove a technical initiative across multiple teams."),
        ("leadership", "Convince senior leadership to change direction",
         "Describe a situation where you had to convince senior leadership to change direction on a technical decision."),
        ("leadership", "Mentor someone with significant team impact",
         "Tell me about a time you mentored someone and it significantly impacted the team."),
        ("leadership", "Influence engineering culture beyond your team",
         "How have you influenced engineering culture or practices beyond your immediate team?"),
        ("leadership", "Lead without formal authority",
         "Describe a time you had to lead a project where you had no formal authority over the contributors."),
        ("leadership", "Identify unseen problem and drive solution",
         "Tell me about a time you identified a problem nobody else saw and drove the solution."),
        # Conflict
        ("conflict", "Significant technical disagreement with colleague",
         "Tell me about a time you had a significant disagreement with a colleague about a technical approach."),
        ("conflict", "Handling critical feedback",
         "Describe a situation where you received critical feedback. How did you handle it?"),
        ("conflict", "Delivering difficult feedback",
         "Tell me about a time you had to deliver difficult feedback to a peer or report."),
        ("conflict", "Resolving conflict between team members",
         "Describe a conflict between two team members that you helped resolve."),
        ("conflict", "Disagreeing with manager's decision",
         "Tell me about a time when you disagreed with your manager's decision. What did you do?"),
        # Technical Decision
        ("technical_decision", "Critical decision with incomplete information",
         "Tell me about a time you had to make a critical technical decision with incomplete information."),
        ("technical_decision", "Choosing between multiple viable approaches",
         "Describe a situation where you had multiple viable technical approaches. How did you decide?"),
        ("technical_decision", "Technical bet that didn't work out",
         "Tell me about a time when a technical bet you made didn't work out. What happened?"),
        ("technical_decision", "Most complex system designed",
         "Describe the most architecturally complex system you've designed. What trade-offs did you make?"),
        ("technical_decision", "Build vs. buy vs. open-source",
         "How do you decide when to build vs. buy vs. adopt open-source?"),
        ("technical_decision", "Simplifying a complex system",
         "Tell me about a time you had to simplify a complex system."),
        # Collaboration
        ("collaboration", "Coordinating across 3+ teams",
         "Tell me about a project that required coordinating across 3+ teams."),
        ("collaboration", "Handling dependencies with different priorities",
         "How do you handle dependencies on teams that have different priorities?"),
        ("collaboration", "Aligning stakeholders with competing interests",
         "Describe a time you had to align multiple stakeholders with competing interests."),
        ("collaboration", "Improving a cross-team process",
         "Tell me about a time you improved a cross-team process."),
        # Mentoring
        ("mentoring", "Growing technical skills of your team",
         "Tell me about how you've grown the technical skills of your team."),
        ("mentoring", "Code review approach balancing speed and teaching",
         "Describe your approach to code review. How do you balance speed with teaching?"),
        ("mentoring", "Helping someone get promoted",
         "Tell me about a time you helped someone get promoted."),
        ("mentoring", "Onboarding new engineers to complex systems",
         "How do you onboard new engineers to a complex system?"),
        # Ambiguity
        ("ambiguity", "Defining solution space from vague problem",
         "Tell me about a time you were given a vague problem and had to define the solution space."),
        ("ambiguity", "Prioritizing when everything is urgent",
         "How do you prioritize when everything seems urgent?"),
        ("ambiguity", "Requirements changed mid-project",
         "Describe a time when requirements changed significantly mid-project."),
        ("ambiguity", "Saying no to a stakeholder",
         "Tell me about a time you had to say no to a stakeholder."),
    ]

    with get_conn() as conn:
        conn.executemany(
            """INSERT OR IGNORE INTO behavioral_stories
               (category, title, applicable_questions)
               VALUES (?, ?, ?)""",
            questions,
        )


def _seed_study_plan():
    plan = {
        1: [
            "Review Two Pointers pattern + solve 3 problems",
            "Review Sliding Window pattern + solve 3 problems",
            "Review Binary Search pattern + solve 3 problems",
            "Review BFS/DFS patterns + solve 4 problems",
            "System Design: URL Shortener + Rate Limiter",
            "Write 2 behavioral stories (Leadership, Conflict)",
            "Review week 1, re-solve missed problems",
        ],
        2: [
            "Review Dynamic Programming (1D) + solve 4 problems",
            "Review Dynamic Programming (2D, Knapsack) + solve 4 problems",
            "Review Backtracking pattern + solve 3 problems",
            "Review Greedy pattern + solve 3 problems",
            "System Design: News Feed + Chat System",
            "Write 2 behavioral stories (Technical Decision, Collaboration)",
            "Review week 2, re-solve missed problems",
        ],
        3: [
            "Review Graph Algorithms + solve 4 problems",
            "Review Trie + Union-Find + solve 3 problems",
            "Review Monotonic Stack + Topological Sort + solve 3 problems",
            "Review Heap/Priority Queue + solve 3 problems",
            "System Design: Ride-Sharing + Location Tracking",
            "Write 2 behavioral stories (Mentoring, Ambiguity)",
            "Review week 3, re-solve missed problems",
        ],
        4: [
            "Review Intervals + Linked List + solve 4 problems",
            "Review Trees + solve 4 problems",
            "Review Bit Manipulation + String/Array + solve 4 problems",
            "Review Design/Data Structure problems + solve 3 problems",
            "System Design: Distributed Cache + Key-Value Store",
            "Review all behavioral stories, practice out loud",
            "Mock coding interview (2 problems in 45 min)",
        ],
        5: [
            "Spaced repetition: re-solve week 1 problems (lowest confidence)",
            "Spaced repetition: re-solve week 2 problems (lowest confidence)",
            "System Design: Task Scheduler + Monitoring System",
            "System Design: Container Orchestration (EKS deep dive)",
            "System Design: Control Plane + Data Plane design",
            "Mock system design interview (45 min)",
            "Review week 5, identify weak areas",
        ],
        6: [
            "Spaced repetition: re-solve week 3 problems",
            "Spaced repetition: re-solve week 4 problems",
            "System Design: Service Mesh + Cloud Load Balancer",
            "System Design: Auto-Scaling + Cluster Scheduler",
            "Meta-specific coding practice (top 10 Meta problems)",
            "Mock behavioral interview (30 min)",
            "Review and refine behavioral stories",
        ],
        7: [
            "Company-specific prep: Meta top problems + system design",
            "Company-specific prep: Uber top problems + system design",
            "Company-specific prep: Microsoft top problems + system design",
            "Company-specific prep: AI companies problems + ML infra design",
            "Full mock interview: coding + system design + behavioral",
            "System Design: ML Feature Store + Multi-Region Deployment",
            "Review weak patterns, targeted practice",
        ],
        8: [
            "Final review: all coding patterns (solve 1 per pattern)",
            "Final review: all system design topics (5 min summary each)",
            "Final review: all behavioral stories (practice delivery)",
            "Mock interview day 1: Full Meta loop simulation",
            "Mock interview day 2: Full Microsoft/Uber loop simulation",
            "Light review, rest, and confidence building",
            "Final prep: review notes, get good sleep",
        ],
    }

    with get_conn() as conn:
        for week, tasks in plan.items():
            for day_idx, task_text in enumerate(tasks, 1):
                conn.execute(
                    "INSERT OR IGNORE INTO study_plan_progress (week, day, task_text) VALUES (?, ?, ?)",
                    (week, day_idx, task_text),
                )


if __name__ == "__main__":
    seed_all()
    print("Database seeded successfully!")
