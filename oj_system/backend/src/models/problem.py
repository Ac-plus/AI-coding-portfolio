from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Problem:
    id: str
    title: str
    difficulty: str
    tags: list[str]
    description: str
    input_format: str
    output_format: str
    hint: str
    function_name: str
    return_type: str
    parameters: list[dict[str, str]]
    test_cases: list[dict[str, Any]]
    time_limit_ms: int = 1000
    memory_limit_mb: int = 256
    starter_code: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Problem":
        return cls(
            id=payload["id"],
            title=payload["title"],
            difficulty=payload.get("difficulty", "Medium"),
            tags=payload.get("tags", []),
            description=payload["description"],
            input_format=payload["input_format"],
            output_format=payload["output_format"],
            hint=payload.get("hint", ""),
            function_name=payload["function_name"],
            return_type=payload["return_type"],
            parameters=payload.get("parameters", []),
            test_cases=payload.get("test_cases", []),
            time_limit_ms=payload.get("time_limit_ms", 1000),
            memory_limit_mb=payload.get("memory_limit_mb", 256),
            starter_code=payload.get("starter_code", ""),
            metadata=payload.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "difficulty": self.difficulty,
            "tags": self.tags,
            "description": self.description,
            "input_format": self.input_format,
            "output_format": self.output_format,
            "hint": self.hint,
            "function_name": self.function_name,
            "return_type": self.return_type,
            "parameters": self.parameters,
            "test_cases": self.test_cases,
            "time_limit_ms": self.time_limit_ms,
            "memory_limit_mb": self.memory_limit_mb,
            "starter_code": self.starter_code,
            "metadata": self.metadata,
        }

    def summary(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "difficulty": self.difficulty,
            "tags": self.tags,
        }
