from __future__ import annotations

import json
import subprocess
import textwrap
import uuid
from pathlib import Path
from typing import Any

from backend.src.config.settings import TEMP_DIR
from backend.src.models.problem import Problem
from backend.src.storage.json_store import ensure_dir


class CppJudge:
    SUPPORTED_BASE_TYPES = {"int", "long long", "double", "bool", "string"}

    def __init__(self, temp_dir: Path = TEMP_DIR) -> None:
        self.temp_dir = temp_dir
        ensure_dir(self.temp_dir)

    def judge(self, problem: Problem, source_code: str) -> dict[str, Any]:
        submission_id = uuid.uuid4().hex
        workdir = self.temp_dir / submission_id
        ensure_dir(workdir)

        source_path = workdir / "main.cpp"
        binary_path = workdir / "main"
        source_path.write_text(self._build_source(problem, source_code), encoding="utf-8")

        compile_process = subprocess.run(
            [
                "g++",
                "-std=c++17",
                "-O2",
                "-pipe",
                str(source_path),
                "-o",
                str(binary_path),
            ],
            capture_output=True,
            text=True,
            cwd=workdir,
        )

        if compile_process.returncode != 0:
            return {
                "submission_id": submission_id,
                "status": "Compile Error",
                "score": 0,
                "passed": 0,
                "total": len(problem.test_cases),
                "compile_output": compile_process.stderr.strip(),
                "results": [],
            }

        results: list[dict[str, Any]] = []
        passed = 0
        final_status = "Accepted"

        for index, case in enumerate(problem.test_cases):
            try:
                run_process = subprocess.run(
                    [str(binary_path), str(index)],
                    capture_output=True,
                    text=True,
                    cwd=workdir,
                    timeout=problem.time_limit_ms / 1000,
                )
            except subprocess.TimeoutExpired:
                results.append(
                    {
                        "case_index": index,
                        "status": "Time Limit Exceeded",
                        "expected": self._serialize_python_value(case["expected"]),
                        "actual": None,
                    }
                )
                final_status = "Time Limit Exceeded"
                break

            if run_process.returncode != 0:
                results.append(
                    {
                        "case_index": index,
                        "status": "Runtime Error",
                        "expected": self._serialize_python_value(case["expected"]),
                        "actual": run_process.stderr.strip() or run_process.stdout.strip(),
                    }
                )
                final_status = "Runtime Error"
                break

            actual = run_process.stdout.strip()
            expected = self._serialize_python_value(case["expected"])
            case_status = "Accepted" if actual == expected else "Wrong Answer"
            if case_status == "Accepted":
                passed += 1
            else:
                final_status = "Wrong Answer"

            results.append(
                {
                    "case_index": index,
                    "status": case_status,
                    "expected": expected,
                    "actual": actual,
                }
            )

            if case_status != "Accepted":
                break

        total = len(problem.test_cases)
        score = int((passed / total) * 100) if total else 0

        return {
            "submission_id": submission_id,
            "status": final_status,
            "score": score,
            "passed": passed,
            "total": total,
            "compile_output": compile_process.stderr.strip(),
            "results": results,
        }

    def _build_source(self, problem: Problem, source_code: str) -> str:
        switches = []
        for index, case in enumerate(problem.test_cases):
            declarations = []
            argument_names = []
            for arg_index, (parameter, value) in enumerate(zip(problem.parameters, case["input"], strict=True)):
                variable_name = f"arg_{arg_index}"
                storage_type = self._storage_type(parameter["type"])
                declarations.append(
                    f"{storage_type} {variable_name} = {self._to_cpp_literal(storage_type, value)};"
                )
                argument_names.append(variable_name)
            switches.append(
                textwrap.dedent(
                    f"""
                    case {index}: {{
                        {' '.join(declarations)}
                        auto actual = solution.{problem.function_name}({", ".join(argument_names)});
                        cout << serialize(actual);
                        return 0;
                    }}
                    """
                ).strip()
            )

        return textwrap.dedent(
            f"""
            #include <bits/stdc++.h>
            using namespace std;

            {self._support_code()}

            {source_code}

            int main(int argc, char** argv) {{
                if (argc < 2) {{
                    cerr << "Missing case index";
                    return 1;
                }}

                int case_index = stoi(argv[1]);
                Solution solution;

                switch (case_index) {{
                    {" ".join(switches)}
                    default:
                        cerr << "Invalid case index";
                        return 1;
                }}
            }}
            """
        ).strip() + "\n"

    def _support_code(self) -> str:
        return textwrap.dedent(
            """
            string serialize(const string& value) { return value; }
            string serialize(const char* value) { return string(value); }
            string serialize(bool value) { return value ? "true" : "false"; }

            template <typename T>
            typename enable_if<is_arithmetic<T>::value && !is_same<T, bool>::value, string>::type
            serialize(T value) {
                ostringstream out;
                out << value;
                return out.str();
            }

            template <typename T>
            string serialize(const vector<T>& items) {
                string result = "[";
                for (size_t i = 0; i < items.size(); ++i) {
                    if (i > 0) result += ",";
                    result += serialize(items[i]);
                }
                result += "]";
                return result;
            }
            """
        ).strip()

    def _to_cpp_literal(self, cpp_type: str, value: Any) -> str:
        normalized = " ".join(cpp_type.split())
        if normalized in {"int", "long long"}:
            return str(value)
        if normalized == "double":
            return repr(value)
        if normalized == "bool":
            return "true" if value else "false"
        if normalized == "string":
            return json.dumps(value, ensure_ascii=False)
        if normalized.startswith("vector<") and normalized.endswith(">"):
            inner_type = normalized[7:-1].strip()
            rendered = ",".join(self._to_cpp_literal(inner_type, item) for item in value)
            return f"vector<{inner_type}>{{{rendered}}}"
        raise ValueError(f"Unsupported C++ type: {cpp_type}")

    def _storage_type(self, cpp_type: str) -> str:
        normalized = " ".join(cpp_type.replace("&", " ").split())
        if normalized.startswith("const "):
            normalized = normalized[6:].strip()
        return normalized

    def _serialize_python_value(self, value: Any) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, str):
            return value
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, list):
            return "[" + ",".join(self._serialize_python_value(item) for item in value) + "]"
        raise ValueError(f"Unsupported expected value: {value!r}")
