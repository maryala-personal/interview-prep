"""SQLite database helper for Interview Prep Tracker."""

import sqlite3
import os
from datetime import date, datetime, timedelta
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "interview_prep.db")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create all tables if they don't exist."""
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS coding_problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT NOT NULL,
                title TEXT NOT NULL,
                leetcode_num INTEGER,
                difficulty TEXT CHECK(difficulty IN ('Easy', 'Medium', 'Hard')),
                company_tags TEXT DEFAULT '',
                url TEXT DEFAULT '',
                status TEXT DEFAULT 'not_started'
                    CHECK(status IN ('not_started', 'attempted', 'solved', 'mastered')),
                last_practiced TEXT,
                next_review TEXT,
                times_practiced INTEGER DEFAULT 0,
                notes TEXT DEFAULT '',
                confidence INTEGER DEFAULT 0 CHECK(confidence BETWEEN 0 AND 5),
                UNIQUE(pattern, title)
            );

            CREATE TABLE IF NOT EXISTS system_design (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                category TEXT DEFAULT 'core'
                    CHECK(category IN ('core', 'eks_specific', 'ml_infra')),
                company_tags TEXT DEFAULT '',
                status TEXT DEFAULT 'not_started'
                    CHECK(status IN ('not_started', 'studying', 'reviewed', 'confident')),
                notes TEXT DEFAULT '',
                last_reviewed TEXT,
                confidence INTEGER DEFAULT 0 CHECK(confidence BETWEEN 0 AND 5)
            );

            CREATE TABLE IF NOT EXISTS behavioral_stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL
                    CHECK(category IN ('leadership', 'conflict', 'technical_decision',
                                       'collaboration', 'mentoring', 'ambiguity')),
                title TEXT DEFAULT '',
                situation TEXT DEFAULT '',
                task TEXT DEFAULT '',
                action TEXT DEFAULT '',
                result TEXT DEFAULT '',
                applicable_questions TEXT DEFAULT '',
                company_tags TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS daily_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                coding_count INTEGER DEFAULT 0,
                system_design_minutes INTEGER DEFAULT 0,
                behavioral_count INTEGER DEFAULT 0,
                notes TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS study_plan_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week INTEGER NOT NULL,
                day INTEGER NOT NULL,
                task_text TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                start_date TEXT,
                UNIQUE(week, day, task_text)
            );
        """)


# ── Coding Problems CRUD ──

def get_all_coding_problems(filters=None):
    with get_conn() as conn:
        query = "SELECT * FROM coding_problems"
        params = []
        conditions = []
        if filters:
            if filters.get("pattern"):
                conditions.append("pattern = ?")
                params.append(filters["pattern"])
            if filters.get("difficulty"):
                conditions.append("difficulty = ?")
                params.append(filters["difficulty"])
            if filters.get("status"):
                conditions.append("status = ?")
                params.append(filters["status"])
            if filters.get("company"):
                conditions.append("company_tags LIKE ?")
                params.append(f"%{filters['company']}%")
            if filters.get("min_confidence") is not None:
                conditions.append("confidence >= ?")
                params.append(filters["min_confidence"])
            if filters.get("max_confidence") is not None:
                conditions.append("confidence <= ?")
                params.append(filters["max_confidence"])
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY pattern, difficulty, title"
        return [dict(r) for r in conn.execute(query, params).fetchall()]


def get_coding_patterns():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT pattern FROM coding_problems ORDER BY pattern"
        ).fetchall()
        return [r["pattern"] for r in rows]


def update_coding_problem(problem_id, **kwargs):
    with get_conn() as conn:
        sets = []
        params = []
        for k, v in kwargs.items():
            sets.append(f"{k} = ?")
            params.append(v)
        params.append(problem_id)
        conn.execute(
            f"UPDATE coding_problems SET {', '.join(sets)} WHERE id = ?", params
        )


def add_coding_problem(**kwargs):
    with get_conn() as conn:
        cols = list(kwargs.keys())
        placeholders = ", ".join(["?"] * len(cols))
        conn.execute(
            f"INSERT OR IGNORE INTO coding_problems ({', '.join(cols)}) VALUES ({placeholders})",
            list(kwargs.values()),
        )


def practice_coding_problem(problem_id, confidence):
    """Mark a problem as practiced with spaced repetition scheduling."""
    today = date.today().isoformat()
    with get_conn() as conn:
        row = conn.execute(
            "SELECT times_practiced FROM coding_problems WHERE id = ?", (problem_id,)
        ).fetchone()
        times = (row["times_practiced"] if row else 0) + 1
        # Spaced repetition: 1, 3, 7, 14, 30 days
        intervals = [1, 3, 7, 14, 30]
        idx = min(times - 1, len(intervals) - 1)
        next_review = (date.today() + timedelta(days=intervals[idx])).isoformat()
        status = "mastered" if confidence >= 4 and times >= 3 else "solved" if confidence >= 3 else "attempted"
        conn.execute(
            """UPDATE coding_problems
               SET last_practiced = ?, next_review = ?, times_practiced = ?,
                   confidence = ?, status = ?
               WHERE id = ?""",
            (today, next_review, times, confidence, status, problem_id),
        )


def get_due_for_review():
    today = date.today().isoformat()
    with get_conn() as conn:
        return [
            dict(r) for r in conn.execute(
                """SELECT * FROM coding_problems
                   WHERE (next_review IS NULL OR next_review <= ?)
                     AND status != 'mastered'
                   ORDER BY confidence ASC, next_review ASC""",
                (today,),
            ).fetchall()
        ]


def get_coding_stats():
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) as c FROM coding_problems").fetchone()["c"]
        solved = conn.execute(
            "SELECT COUNT(*) as c FROM coding_problems WHERE status IN ('solved', 'mastered')"
        ).fetchone()["c"]
        mastered = conn.execute(
            "SELECT COUNT(*) as c FROM coding_problems WHERE status = 'mastered'"
        ).fetchone()["c"]
        by_pattern = [
            dict(r) for r in conn.execute(
                """SELECT pattern,
                          COUNT(*) as total,
                          SUM(CASE WHEN status IN ('solved','mastered') THEN 1 ELSE 0 END) as done,
                          ROUND(AVG(confidence), 1) as avg_confidence
                   FROM coding_problems GROUP BY pattern ORDER BY pattern"""
            ).fetchall()
        ]
        return {"total": total, "solved": solved, "mastered": mastered, "by_pattern": by_pattern}


# ── System Design CRUD ──

def get_all_system_design(filters=None):
    with get_conn() as conn:
        query = "SELECT * FROM system_design"
        params = []
        conditions = []
        if filters:
            if filters.get("category"):
                conditions.append("category = ?")
                params.append(filters["category"])
            if filters.get("status"):
                conditions.append("status = ?")
                params.append(filters["status"])
            if filters.get("company"):
                conditions.append("company_tags LIKE ?")
                params.append(f"%{filters['company']}%")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY category, title"
        return [dict(r) for r in conn.execute(query, params).fetchall()]


def update_system_design(topic_id, **kwargs):
    with get_conn() as conn:
        sets = []
        params = []
        for k, v in kwargs.items():
            sets.append(f"{k} = ?")
            params.append(v)
        params.append(topic_id)
        conn.execute(
            f"UPDATE system_design SET {', '.join(sets)} WHERE id = ?", params
        )


def get_system_design_stats():
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) as c FROM system_design").fetchone()["c"]
        reviewed = conn.execute(
            "SELECT COUNT(*) as c FROM system_design WHERE status IN ('reviewed', 'confident')"
        ).fetchone()["c"]
        return {"total": total, "reviewed": reviewed}


# ── Behavioral Stories CRUD ──

def get_all_behavioral_stories(category=None):
    with get_conn() as conn:
        if category:
            rows = conn.execute(
                "SELECT * FROM behavioral_stories WHERE category = ? ORDER BY id", (category,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM behavioral_stories ORDER BY category, id").fetchall()
        return [dict(r) for r in rows]


def add_behavioral_story(**kwargs):
    with get_conn() as conn:
        cols = list(kwargs.keys())
        placeholders = ", ".join(["?"] * len(cols))
        conn.execute(
            f"INSERT INTO behavioral_stories ({', '.join(cols)}) VALUES ({placeholders})",
            list(kwargs.values()),
        )


def update_behavioral_story(story_id, **kwargs):
    with get_conn() as conn:
        sets = []
        params = []
        for k, v in kwargs.items():
            sets.append(f"{k} = ?")
            params.append(v)
        params.append(story_id)
        conn.execute(
            f"UPDATE behavioral_stories SET {', '.join(sets)} WHERE id = ?", params
        )


def delete_behavioral_story(story_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM behavioral_stories WHERE id = ?", (story_id,))


def get_behavioral_stats():
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) as c FROM behavioral_stories").fetchone()["c"]
        by_cat = [
            dict(r) for r in conn.execute(
                "SELECT category, COUNT(*) as count FROM behavioral_stories GROUP BY category"
            ).fetchall()
        ]
        return {"total": total, "by_category": by_cat}


# ── Daily Log CRUD ──

def log_daily(coding_count=0, system_design_minutes=0, behavioral_count=0, notes=""):
    today = date.today().isoformat()
    with get_conn() as conn:
        existing = conn.execute("SELECT * FROM daily_log WHERE date = ?", (today,)).fetchone()
        if existing:
            conn.execute(
                """UPDATE daily_log
                   SET coding_count = coding_count + ?,
                       system_design_minutes = system_design_minutes + ?,
                       behavioral_count = behavioral_count + ?,
                       notes = CASE WHEN notes = '' THEN ? ELSE notes || '\n' || ? END
                   WHERE date = ?""",
                (coding_count, system_design_minutes, behavioral_count, notes, notes, today),
            )
        else:
            conn.execute(
                "INSERT INTO daily_log (date, coding_count, system_design_minutes, behavioral_count, notes) VALUES (?, ?, ?, ?, ?)",
                (today, coding_count, system_design_minutes, behavioral_count, notes),
            )


def get_daily_logs(days=30):
    with get_conn() as conn:
        since = (date.today() - timedelta(days=days)).isoformat()
        return [
            dict(r) for r in conn.execute(
                "SELECT * FROM daily_log WHERE date >= ? ORDER BY date DESC", (since,)
            ).fetchall()
        ]


def get_streak():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT date FROM daily_log WHERE coding_count > 0 OR system_design_minutes > 0 ORDER BY date DESC"
        ).fetchall()
        if not rows:
            return 0
        streak = 0
        check_date = date.today()
        for row in rows:
            row_date = date.fromisoformat(row["date"])
            if row_date == check_date:
                streak += 1
                check_date -= timedelta(days=1)
            elif row_date == check_date - timedelta(days=1):
                streak += 1
                check_date = row_date - timedelta(days=1)
            else:
                break
        return streak


# ── Study Plan CRUD ──

def get_study_plan():
    with get_conn() as conn:
        return [
            dict(r) for r in conn.execute(
                "SELECT * FROM study_plan_progress ORDER BY week, day"
            ).fetchall()
        ]


def toggle_study_task(task_id):
    with get_conn() as conn:
        conn.execute(
            "UPDATE study_plan_progress SET completed = 1 - completed WHERE id = ?",
            (task_id,),
        )


def set_study_start_date(start_date):
    with get_conn() as conn:
        conn.execute(
            "UPDATE study_plan_progress SET start_date = ?", (start_date,)
        )


def is_seeded():
    with get_conn() as conn:
        count = conn.execute("SELECT COUNT(*) as c FROM coding_problems").fetchone()["c"]
        return count > 0
