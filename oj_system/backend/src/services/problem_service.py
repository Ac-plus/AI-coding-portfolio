from __future__ import annotations

from pathlib import Path

from backend.src.config.settings import PROBLEMS_DIR
from backend.src.models.problem import Problem
from backend.src.storage.json_store import ensure_dir, read_json, write_json


class ProblemService:
    def __init__(self, problems_dir: Path = PROBLEMS_DIR) -> None:
        self.problems_dir = problems_dir
        ensure_dir(self.problems_dir)

    def list_problems(self, tag: str | None = None) -> list[dict]:
        problems = [self._load_problem(path).summary() for path in sorted(self.problems_dir.glob("*.json"))]
        if tag:
            return [problem for problem in problems if tag in problem["tags"]]
        return problems

    def list_tags(self) -> list[str]:
        tag_set: set[str] = set()
        for item in self.list_problems():
            tag_set.update(item["tags"])
        return sorted(tag_set)

    def get_problem(self, problem_id: str) -> Problem:
        path = self._problem_path(problem_id)
        if not path.exists():
            raise FileNotFoundError(f"Problem {problem_id} not found")
        return self._load_problem(path)

    def create_problem(self, payload: dict) -> dict:
        problem = Problem.from_dict(payload)
        path = self._problem_path(problem.id)
        if path.exists():
            raise FileExistsError(f"Problem {problem.id} already exists")
        write_json(path, problem.to_dict())
        return problem.to_dict()

    def update_problem(self, problem_id: str, payload: dict) -> dict:
        path = self._problem_path(problem_id)
        if not path.exists():
            raise FileNotFoundError(f"Problem {problem_id} not found")

        normalized_payload = dict(payload)
        payload_id = normalized_payload.get("id", problem_id)
        if payload_id != problem_id:
            raise ValueError("Problem id cannot be changed during update")

        normalized_payload["id"] = problem_id
        problem = Problem.from_dict(normalized_payload)
        write_json(path, problem.to_dict())
        return problem.to_dict()

    def _problem_path(self, problem_id: str) -> Path:
        return self.problems_dir / f"{problem_id}.json"

    @staticmethod
    def _load_problem(path: Path) -> Problem:
        return Problem.from_dict(read_json(path))
