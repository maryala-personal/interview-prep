"""Add missing Hard problems and new patterns to ensure every pattern has 2+ Hard problems."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from data.db import get_conn, init_db

NEW_PROBLEMS = [
    # ── Two Pointers (needs 1 more Hard) ──
    ("Two Pointers", "4Sum", 18, "Hard", "Meta, Google"),
    ("Two Pointers", "Minimum Window Subsequence", 727, "Hard", "Google, Meta"),

    # ── BFS (needs 1 more Hard) ──
    ("BFS", "Minimum Moves to Reach Target with Rotations", 1210, "Hard", "Google"),
    ("BFS", "Shortest Path to Get All Keys", 864, "Hard", "Google, Amazon"),
    ("BFS", "Cut Off Trees for Golf Event", 675, "Hard", "Amazon, Meta"),

    # ── DFS (needs 1 more Hard) ──
    ("DFS", "Making A Large Island", 827, "Hard", "Meta, Google"),
    ("DFS", "Remove Invalid Parentheses", 301, "Hard", "Meta"),
    ("DFS", "Critical Connections in a Network", 1192, "Hard", "Amazon, Google"),

    # ── Backtracking (needs 1 more Hard) ──
    ("Backtracking", "Sudoku Solver", 37, "Hard", "Microsoft, Google"),
    ("Backtracking", "Word Search II", 212, "Hard", "Meta, Microsoft"),
    ("Backtracking", "Palindrome Partitioning", 131, "Medium", "Meta, Google"),

    # ── Greedy (needs 2+ Hard) ──
    ("Greedy", "Candy", 135, "Hard", "Meta, Google"),
    ("Greedy", "IPO", 502, "Hard", "Google, Amazon"),
    ("Greedy", "Minimum Number of Refueling Stops", 871, "Hard", "Google"),
    ("Greedy", "Course Schedule III", 630, "Hard", "Google, Amazon"),

    # ── Graph Algorithms (needs 1 more Hard) ──
    ("Graph Algorithms", "Swim in Rising Water", 778, "Hard", "Google"),
    ("Graph Algorithms", "Minimum Cost to Make at Least One Valid Path", 1368, "Hard", "Google, Uber"),
    ("Graph Algorithms", "Critical Connections in a Network", 1192, "Hard", "Amazon, Google"),

    # ── Trie (needs 1 more Hard) ──
    ("Trie", "Palindrome Pairs", 336, "Hard", "Meta, Google"),
    ("Trie", "Stream of Characters", 1032, "Hard", "Google"),

    # ── Union-Find (needs 2+ Hard) ──
    ("Union-Find", "Number of Islands II", 305, "Hard", "Google, Meta"),
    ("Union-Find", "Minimize Malware Spread", 924, "Hard", "Google"),
    ("Union-Find", "Remove Max Number of Edges", 1579, "Hard", "Google"),

    # ── Topological Sort (needs 1 more Hard) ──
    ("Topological Sort", "Sort Items by Groups Respecting Dependencies", 1203, "Hard", "Google"),
    ("Topological Sort", "Sequence Reconstruction", 444, "Hard", "Google, Uber"),

    # ── Intervals (needs 1 more Hard) ──
    ("Intervals", "Data Stream as Disjoint Intervals", 352, "Hard", "Google"),
    ("Intervals", "Minimum Interval to Include Each Query", 1851, "Hard", "Google, Meta"),

    # ── Linked List (needs 1 more Hard) ──
    ("Linked List", "Merge K Sorted Lists", 23, "Hard", "Meta, Microsoft"),
    ("Linked List", "Reverse Nodes in k-Group", 25, "Hard", "Meta, Microsoft, Google"),

    # ── Bit Manipulation (needs 2+ Hard) ──
    ("Bit Manipulation", "Maximum XOR of Two Numbers in an Array", 421, "Hard", "Google"),
    ("Bit Manipulation", "Find the Shortest Superstring", 943, "Hard", "Google"),

    # ── String / Array (needs 2+ Hard) ──
    ("String / Array", "Text Justification", 68, "Hard", "Meta, Google, Microsoft"),
    ("String / Array", "Minimum Window Substring", 76, "Hard", "Meta, Microsoft"),
    ("String / Array", "Basic Calculator", 224, "Hard", "Meta, Google"),
    ("String / Array", "Substring with Concatenation of All Words", 30, "Hard", "Google"),

    # ── Design / Data Structure (needs 1 more Hard) ──
    ("Design / Data Structure", "All O(1) Data Structure", 432, "Hard", "Meta"),
    ("Design / Data Structure", "Design In-Memory File System", 588, "Hard", "Meta, Google"),
    ("Design / Data Structure", "Maximum Frequency Stack", 895, "Hard", "Meta, Google"),

    # ── Monotonic Stack (already has 3 Hard but add key ones) ──
    ("Monotonic Stack", "Trapping Rain Water", 42, "Hard", "Meta, Microsoft, Google"),

    # ── NEW PATTERN: Prefix Sum ──
    ("Prefix Sum", "Subarray Sum Equals K", 560, "Medium", "Meta, Google"),
    ("Prefix Sum", "Continuous Subarray Sum", 523, "Medium", "Meta"),
    ("Prefix Sum", "Range Sum Query 2D - Immutable", 304, "Medium", "Meta, Google"),
    ("Prefix Sum", "Maximum Size Subarray Sum Equals k", 325, "Medium", "Meta"),
    ("Prefix Sum", "Count of Range Sum", 327, "Hard", "Google"),
    ("Prefix Sum", "Number of Submatrices That Sum to Target", 1074, "Hard", "Google, Meta"),
    ("Prefix Sum", "Max Sum of Rectangle No Larger Than K", 363, "Hard", "Google"),

    # ── NEW PATTERN: Matrix / Grid ──
    ("Matrix / Grid", "Set Matrix Zeroes", 73, "Medium", "Meta, Microsoft"),
    ("Matrix / Grid", "Spiral Matrix", 54, "Medium", "Meta, Microsoft"),
    ("Matrix / Grid", "Rotate Image", 48, "Medium", "Meta, Microsoft"),
    ("Matrix / Grid", "Search a 2D Matrix II", 240, "Medium", "Microsoft, Google"),
    ("Matrix / Grid", "Maximal Square", 221, "Medium", "Meta, Google"),
    ("Matrix / Grid", "Shortest Path in a Grid with Obstacles Elimination", 1293, "Hard", "Google, Meta"),
    ("Matrix / Grid", "Maximal Rectangle", 85, "Hard", "Meta, Google"),
    ("Matrix / Grid", "Dungeon Game", 174, "Hard", "Google"),
]


def add_new_problems():
    init_db()
    with get_conn() as conn:
        added = 0
        for pattern, title, lc, diff, companies in NEW_PROBLEMS:
            url = f"https://leetcode.com/problems/{title.lower().replace(' ', '-').replace('(', '').replace(')', '').replace(',', '')}/"
            try:
                conn.execute(
                    """INSERT OR IGNORE INTO coding_problems
                       (pattern, title, leetcode_num, difficulty, company_tags, url)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (pattern, title, lc, diff, companies, url),
                )
                added += 1
            except Exception as e:
                print(f"  Skip {title}: {e}")
        print(f"Added {added} new problems")


if __name__ == "__main__":
    add_new_problems()
