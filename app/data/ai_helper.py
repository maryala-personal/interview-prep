"""AI-powered problem classification using Claude API."""

import json
import os

KNOWN_PATTERNS = [
    "Two Pointers", "Sliding Window", "Binary Search", "BFS", "DFS",
    "Dynamic Programming", "Backtracking", "Greedy", "Graph Algorithms",
    "Trie", "Union-Find", "Monotonic Stack", "Topological Sort",
    "Heap / Priority Queue", "Intervals", "Linked List", "Trees",
    "Bit Manipulation", "String / Array", "Design / Data Structure",
]


def classify_problem(query: str) -> dict | None:
    """Call Claude to classify a coding problem from a name, description, or URL.

    Returns dict with: pattern, title, leetcode_num, difficulty, company_tags, url
    Or None if classification fails.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None

    try:
        import anthropic
    except ImportError:
        return None

    patterns_list = ", ".join(KNOWN_PATTERNS)

    prompt = f"""Classify this coding interview problem. The user provided: "{query}"

Return a JSON object with exactly these fields:
- "title": the standard problem name (e.g. "Two Sum", "Merge Intervals")
- "leetcode_num": the LeetCode problem number as an integer, or 0 if unknown
- "difficulty": exactly one of "Easy", "Medium", or "Hard"
- "pattern": the primary algorithm pattern, pick the best match from: {patterns_list}. If none fit, use the closest one.
- "company_tags": comma-separated companies commonly known to ask this (e.g. "Meta, Google, Amazon"). Use your knowledge of interview frequencies. If unsure, leave empty string.
- "url": the LeetCode URL if you know the problem number (format: https://leetcode.com/problems/slug/), or empty string

Return ONLY the JSON object, no other text."""

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )

    text = message.content[0].text.strip()
    # Handle potential markdown code fences
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    result = json.loads(text)

    # Validate required fields
    for field in ("title", "leetcode_num", "difficulty", "pattern"):
        if field not in result:
            return None

    if result["difficulty"] not in ("Easy", "Medium", "Hard"):
        result["difficulty"] = "Medium"

    result["leetcode_num"] = int(result.get("leetcode_num", 0) or 0)
    result.setdefault("company_tags", "")
    result.setdefault("url", "")

    return result
