from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.src.config.settings import SUBMISSIONS_DIR
from backend.src.judge.cpp_driver import CppJudge
from backend.src.models.problem import Problem
from backend.src.storage.json_store import ensure_dir, read_json, write_json


class SubmissionService:
    def __init__(self, submissions_dir: Path = SUBMISSIONS_DIR, judge: CppJudge | None = None) -> None:
        self.submissions_dir = submissions_dir
        self.judge = judge or CppJudge()
        ensure_dir(self.submissions_dir)

    def create_submission(self, problem: Problem, source_code: str) -> dict[str, Any]:
        result = self.judge.judge(problem, source_code)
        payload = {
            "id": result["submission_id"],
            "problem_id": problem.id,
            "status": result["status"],
            "score": result["score"],
            "passed": result["passed"],
            "total": result["total"],
            "compile_output": result["compile_output"],
            "results": result["results"],
            "source_code": source_code,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        write_json(self.submissions_dir / f"{payload['id']}.json", payload)
        return payload

    def get_submission(self, submission_id: str) -> dict[str, Any]:
        path = self.submissions_dir / f"{submission_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Submission {submission_id} not found")
        return read_json(path)
