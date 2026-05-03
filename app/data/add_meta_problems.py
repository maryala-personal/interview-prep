"""Add Meta-specific coding problems identified from 2025 interview research.

Cross-referenced against existing DB — only adds problems NOT already present.
Problems are tagged with Meta frequency tiers (T1=Must-Know, T2=Very Likely, T3=Moderate, T4=Occasional).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from data.db import get_conn, init_db

# (pattern, title, lc_num, difficulty, company_tags, meta_tier)
META_PROBLEMS = [
    # ═══════════════════════════════════════════════════
    # TIER 1: VERY HIGH FREQUENCY — Must-Know (Asked Repeatedly in 2025)
    # ═══════════════════════════════════════════════════

    # #1 most asked at Meta in 2025
    ("String / Array", "Minimum Remove to Make Valid Parentheses", 1249, "Medium", "Meta", "T1"),
    ("Two Pointers", "Valid Palindrome II", 680, "Easy", "Meta", "T1"),
    ("Design / Data Structure", "Dot Product of Two Sparse Vectors", 1570, "Medium", "Meta", "T1"),
    ("String / Array", "Valid Word Abbreviation", 408, "Easy", "Meta", "T1"),
    ("Trees", "Binary Tree Vertical Order Traversal", 314, "Medium", "Meta", "T1"),
    ("String / Array", "Simplify Path", 71, "Medium", "Meta", "T1"),
    ("Two Pointers", "Merge Sorted Array", 88, "Easy", "Meta", "T1"),
    ("Trees", "Lowest Common Ancestor of a Binary Tree III", 1650, "Medium", "Meta", "T1"),
    ("Greedy", "Maximum Swap", 670, "Medium", "Meta", "T1"),
    ("Design / Data Structure", "Moving Average from Data Stream", 346, "Easy", "Meta", "T1"),
    ("Trees", "Range Sum of BST", 938, "Easy", "Meta", "T1"),
    ("String / Array", "Custom Sort String", 791, "Medium", "Meta", "T1"),
    ("DFS", "Nested List Weight Sum", 339, "Medium", "Meta", "T1"),

    # ═══════════════════════════════════════════════════
    # TIER 2: HIGH FREQUENCY — Very Likely to Appear
    # ═══════════════════════════════════════════════════

    ("String / Array", "Two Sum", 1, "Easy", "Meta", "T2"),
    ("String / Array", "Add Strings", 415, "Medium", "Meta", "T2"),
    ("Matrix / Grid", "Diagonal Traverse", 498, "Medium", "Meta", "T2"),
    ("String / Array", "Next Permutation", 31, "Medium", "Meta", "T2"),
    ("Binary Search", "Pow(x, n)", 50, "Medium", "Meta", "T2"),
    ("Binary Search", "Find Peak Element", 162, "Medium", "Meta", "T2"),
    ("Heap / Priority Queue", "K Closest Points to Origin", 973, "Medium", "Meta", "T2"),
    ("String / Array", "Group Shifted Strings", 249, "Medium", "Meta", "T2"),
    ("Monotonic Stack", "Buildings With an Ocean View", 1762, "Medium", "Meta", "T2"),
    ("Matrix / Grid", "Toeplitz Matrix", 766, "Easy", "Meta", "T2"),
    ("Binary Search", "Kth Missing Positive Number", 1539, "Easy", "Meta", "T2"),
    ("Trees", "Vertical Order Traversal of a Binary Tree", 987, "Hard", "Meta", "T2"),
    ("Linked List", "Add Two Numbers", 2, "Medium", "Meta", "T2"),
    ("Design / Data Structure", "Design Tic-Tac-Toe", 348, "Medium", "Meta", "T2"),

    # ═══════════════════════════════════════════════════
    # TIER 3: MODERATE FREQUENCY — Regularly Reported
    # ═══════════════════════════════════════════════════

    ("Design / Data Structure", "Random Pick Index", 398, "Medium", "Meta", "T3"),
    ("String / Array", "Exclusive Time of Functions", 636, "Medium", "Meta", "T3"),
    ("Intervals", "Interval List Intersections", 986, "Medium", "Meta", "T3"),
    ("String / Array", "Minimum Add to Make Parentheses Valid", 921, "Medium", "Meta", "T3"),
    ("Two Pointers", "Move Zeroes", 283, "Easy", "Meta", "T3"),
    ("Binary Search", "Find First and Last Position of Element in Sorted Array", 34, "Medium", "Meta", "T3"),
    ("String / Array", "Verifying an Alien Dictionary", 953, "Easy", "Meta", "T3"),
    ("String / Array", "Valid Number", 65, "Hard", "Meta", "T3"),
    ("Backtracking", "Expression Add Operators", 282, "Hard", "Meta", "T3"),
    ("String / Array", "Add Binary", 67, "Easy", "Meta", "T3"),
    ("String / Array", "Integer to English Words", 273, "Hard", "Meta", "T3"),
    ("Trees", "Lowest Common Ancestor of a BST", 235, "Medium", "Meta", "T3"),
    ("Trees", "Convert BST to Sorted Doubly Linked List", 426, "Medium", "Meta", "T3"),
    ("BFS", "Binary Tree Zigzag Level Order Traversal", 103, "Medium", "Meta", "T3"),
    ("BFS", "Check Completeness of a Binary Tree", 958, "Medium", "Meta", "T3"),
    ("BFS", "Walls and Gates", 286, "Medium", "Meta", "T3"),
    ("Binary Search", "Search a 2D Matrix", 74, "Medium", "Meta", "T3"),
    ("Backtracking", "Letter Combinations of a Phone Number", 17, "Medium", "Meta", "T3"),
    ("String / Array", "Valid Parentheses", 20, "Easy", "Meta", "T3"),
    ("Design / Data Structure", "Implement Queue using Stacks", 232, "Easy", "Meta", "T3"),

    # ═══════════════════════════════════════════════════
    # TIER 4: OCCASIONALLY REPORTED
    # ═══════════════════════════════════════════════════

    ("Two Pointers", "Sort Colors", 75, "Medium", "Meta", "T4"),
    ("String / Array", "Multiply Strings", 43, "Medium", "Meta", "T4"),
    ("String / Array", "Reverse Words in a String", 151, "Medium", "Meta", "T4"),
    ("Trees", "Maximum Depth of Binary Tree", 104, "Easy", "Meta", "T4"),
    ("Trees", "Subtree of Another Tree", 572, "Easy", "Meta", "T4"),
    ("Linked List", "Remove Nth Node From End of List", 19, "Medium", "Meta", "T4"),
]


def add_meta_problems():
    init_db()
    with get_conn() as conn:
        # Get existing LC numbers
        existing = set()
        for row in conn.execute("SELECT leetcode_num FROM coding_problems WHERE leetcode_num > 0"):
            existing.add(row[0])

        added = 0
        skipped = 0
        updated_tags = 0

        for pattern, title, lc, diff, companies, tier in META_PROBLEMS:
            url = f"https://leetcode.com/problems/{title.lower().replace(' ', '-').replace('(', '').replace(')', '').replace(',', '').replace('/', '')}/description/"

            if lc in existing:
                # Problem exists — update company_tags to include Meta if not already
                rows = conn.execute(
                    "SELECT id, company_tags FROM coding_problems WHERE leetcode_num = ?", (lc,)
                ).fetchall()
                for row in rows:
                    tags = row[1] or ""
                    if "Meta" not in tags:
                        new_tags = f"{tags}, Meta" if tags else "Meta"
                        conn.execute(
                            "UPDATE coding_problems SET company_tags = ? WHERE id = ?",
                            (new_tags, row[0])
                        )
                        updated_tags += 1
                skipped += 1
                continue

            try:
                conn.execute(
                    """INSERT INTO coding_problems
                       (pattern, title, leetcode_num, difficulty, company_tags, url)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (pattern, title, lc, diff, companies, url),
                )
                added += 1
                existing.add(lc)
                print(f"  + [{tier}] {title} (LC#{lc}) -> {pattern}")
            except Exception as e:
                print(f"  SKIP {title}: {e}")

        # Also update existing problems that are Meta-tagged in research but missing the tag
        meta_lc_numbers = [
            # Tier 1 already in DB
            227, 560, 215, 125, 543, 236, 146, 528,
            # Tier 2 already in DB
            15, 56, 238, 523, 199, 124, 297, 138, 23, 206, 460,
            # Tier 3 already in DB
            347, 76, 269, 207, 33, 46, 78, 39, 155,
            # Tier 4 already in DB
            42, 3, 5, 11, 49, 54, 253, 102, 98, 210, 261,
            21, 25, 143, 139, 121, 322, 200, 133, 1091, 721,
        ]
        for lc in meta_lc_numbers:
            rows = conn.execute(
                "SELECT id, company_tags FROM coding_problems WHERE leetcode_num = ?", (lc,)
            ).fetchall()
            for row in rows:
                tags = row[1] or ""
                if "Meta" not in tags:
                    new_tags = f"{tags}, Meta" if tags else "Meta"
                    conn.execute(
                        "UPDATE coding_problems SET company_tags = ? WHERE id = ?",
                        (new_tags, row[0])
                    )
                    updated_tags += 1

        print(f"\n{'='*50}")
        print(f"Added {added} new Meta problems")
        print(f"Skipped {skipped} (already in DB)")
        print(f"Updated {updated_tags} existing problems with Meta tag")

        # Summary by tier
        total = conn.execute("SELECT COUNT(*) FROM coding_problems").fetchone()[0]
        meta_count = conn.execute(
            "SELECT COUNT(*) FROM coding_problems WHERE company_tags LIKE '%Meta%'"
        ).fetchone()[0]
        print(f"\nTotal problems in DB: {total}")
        print(f"Meta-tagged problems: {meta_count}")


if __name__ == "__main__":
    add_meta_problems()
