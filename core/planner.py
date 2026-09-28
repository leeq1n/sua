"""Task planner — decomposes goals into executable steps.

[FROZEN v1.1.0] — stable interface, tested.

This module is the PRIMARY target for self-improvement.
Papers about new planning algorithms generate patches for this file.
"""
__version__ = "1.3.0"
from typing import List, Callable


from dataclasses import dataclass, asdict
import json
import sqlite3
from typing import List, Callable, Optional
from datetime import datetime, timezone
import os
import re


@dataclass
class RoundResult:
    """Result of a planning round for persistence."""
    task: str
    steps: List[str]
    timestamp: str
    round_id: Optional[int] = None

    def to_dict(self):
        return asdict(self)


def _get_db_path() -> str:
    """Get path to the RoundResults database."""
    db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, 'round_results.db')


def _init_db():
    """Initialize the RoundResults table if it doesn't exist."""
    conn = sqlite3.connect(_get_db_path())
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS round_results (
            round_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            steps TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def save_round_result(result: RoundResult) -> int:
    """Persist a RoundResult to the database and return its ID."""
    _init_db()
    conn = sqlite3.connect(_get_db_path())
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO round_results (task, steps, timestamp) VALUES (?, ?, ?)',
        (result.task, json.dumps(result.steps), result.timestamp)
    )
    round_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return round_id


def get_round_result(round_id: int) -> Optional[RoundResult]:
    """Retrieve a RoundResult from the database by ID."""
    _init_db()
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM round_results WHERE round_id = ?', (round_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return RoundResult(
            round_id=row['round_id'],
            task=row['task'],
            steps=json.loads(row['steps']),
            timestamp=row['timestamp']
        )
    return None


def create_regression_test_plan(failed_task: str, failure_reason: str, llm_call: Callable) -> List[str]:
    """Create a regression test plan from a failed task.
    
    Args:
        failed_task: The original task that failed.
        failure_reason: Description of why the task failed.
        llm_call: LLM callable for generating test plan.
        
    Returns:
        List of steps defining the regression test.
    """
    prompt = (
        f"Create a regression test plan for this failed task.\n"
        f"Task: {failed_task}\n"
        f"Failure reason: {failure_reason}\n"
        f"Generate 3-5 numbered steps to prevent this failure in the future:\n"
    )
    result = llm_call(prompt)
    steps = []
    for line in result.split("\n"):
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith("- ")):
            steps.append(line)
    if not steps:
        steps = [f"Verify: {failed_task}"]
    return steps


def _parse_steps(response: str, task: str) -> List[str]:
    """Preserve JSON plans and split plain numbered plans into executable steps."""
    raw = response.strip() if isinstance(response, str) else ""
    if not raw:
        return [f"Do: {task}"]
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        parsed = raw
    if isinstance(parsed, list):
        steps = [str(item).strip() for item in parsed if item is not None and str(item).strip()]
        return steps or [f"Do: {task}"]
    if isinstance(parsed, str):
        lines = [line.strip() for line in parsed.splitlines() if line.strip()]
        numbered = [re.fullmatch(r"\d+[.)]\s*(.+)", line) for line in lines]
        if lines and all(numbered):
            return [match.group(1).strip() for match in numbered]
        return [parsed.strip()] if parsed.strip() else [f"Do: {task}"]
    return [str(parsed)]


def plan_task(task: str, llm_call: Callable, context: Optional[dict] = None) -> RoundResult:
    """Decompose a goal into executable steps using LLM.
    
    Args:
        task: The high-level task to decompose.
        llm_call: LLM callable that takes a prompt and returns text.
        context: Optional context dict with additional information.
        
    Returns:
        RoundResult containing the decomposed steps.
    """
    context_str = json.dumps(context) if context else ""
    prompt = (
        f"Decompose this task into executable steps.\n"
        f"Task: {task}\n"
        f"Context: {context_str}\n"
        f"Return a JSON list of step strings."
    )
    
    response = llm_call(prompt)
    steps = _parse_steps(response, task)
    
    result = RoundResult(
        task=task,
        steps=steps,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
    
    round_id = save_round_result(result)
    result.round_id = round_id
    
    return result



# --------------------------------------------------------------------- #
# TODO (v5.0.0 — RECURSIVE QUALITY, per 你 idea 2026-07-12):
# Per 你 '类比和自指' insight + LITERATURE (Reflexion, Self-Refine, DyLAN)
# See docs/RECURSIVE_QUALITY.md for design.
#
# Sub-task 1: reflection step after NO_PATCH
# Sub-task 2: analogy step using past reflections
# Sub-task 3: decomposition step (big → small)
# Sub-task 4: self-reference step (pass meta-context)
# --------------------------------------------------------------------- #
