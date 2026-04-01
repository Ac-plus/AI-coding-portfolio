from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from backend.src.config.settings import FRONTEND_PUBLIC_DIR, FRONTEND_SRC_DIR, HOST, PORT
from backend.src.services.problem_service import ProblemService
from backend.src.services.submission_service import SubmissionService
from backend.src.utils.http import read_json_body, send_error_json, send_file, send_json


problem_service = ProblemService()
submission_service = SubmissionService()


class OJRequestHandler(BaseHTTPRequestHandler):
    server_version = "LightOJ/0.1"

    def do_OPTIONS(self) -> None:
        send_json(self, 200, {"ok": True})

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)

        try:
            if path == "/":
                send_file(self, FRONTEND_PUBLIC_DIR / "index.html")
                return

            static_path = self._resolve_static_path(path)
            if static_path is not None:
                send_file(self, static_path)
                return

            if path == "/api/health":
                send_json(self, 200, {"status": "ok"})
                return

            if path == "/api/problems":
                tag = query.get("tag", [None])[0]
                send_json(self, 200, {"items": problem_service.list_problems(tag=tag)})
                return

            if path == "/api/tags":
                send_json(self, 200, {"items": problem_service.list_tags()})
                return

            if path.startswith("/api/problems/"):
                problem_id = path.split("/")[-1]
                send_json(self, 200, problem_service.get_problem(problem_id).to_dict())
                return

            if path.startswith("/api/submissions/"):
                submission_id = path.split("/")[-1]
                send_json(self, 200, submission_service.get_submission(submission_id))
                return

            send_error_json(self, 404, "Route not found")
        except FileNotFoundError as exc:
            send_error_json(self, 404, str(exc))
        except json.JSONDecodeError:
            send_error_json(self, 400, "Invalid JSON body")
        except Exception as exc:  # noqa: BLE001
            send_error_json(self, 500, str(exc))

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        try:
            body = read_json_body(self)

            if path == "/api/problems":
                created = problem_service.create_problem(body)
                send_json(self, 201, created)
                return

            if path == "/api/submissions":
                problem_id = body.get("problem_id")
                source_code = body.get("source_code", "")
                if not problem_id or not source_code:
                    send_error_json(self, 400, "problem_id and source_code are required")
                    return
                problem = problem_service.get_problem(problem_id)
                submission = submission_service.create_submission(problem, source_code)
                send_json(self, 201, submission)
                return

            send_error_json(self, 404, "Route not found")
        except FileExistsError as exc:
            send_error_json(self, 409, str(exc))
        except FileNotFoundError as exc:
            send_error_json(self, 404, str(exc))
        except json.JSONDecodeError:
            send_error_json(self, 400, "Invalid JSON body")
        except Exception as exc:  # noqa: BLE001
            send_error_json(self, 500, str(exc))

    def do_PUT(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        try:
            body = read_json_body(self)

            if path.startswith("/api/problems/"):
                problem_id = path.split("/")[-1]
                updated = problem_service.update_problem(problem_id, body)
                send_json(self, 200, updated)
                return

            send_error_json(self, 404, "Route not found")
        except FileNotFoundError as exc:
            send_error_json(self, 404, str(exc))
        except ValueError as exc:
            send_error_json(self, 400, str(exc))
        except json.JSONDecodeError:
            send_error_json(self, 400, "Invalid JSON body")
        except Exception as exc:  # noqa: BLE001
            send_error_json(self, 500, str(exc))

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def _resolve_static_path(self, request_path: str) -> Path | None:
        if request_path.startswith("/static/"):
            relative = request_path.removeprefix("/static/")
            candidate = (FRONTEND_SRC_DIR / relative).resolve()
            if candidate.is_file() and FRONTEND_SRC_DIR.resolve() in candidate.parents:
                return candidate
            raise FileNotFoundError("Static asset not found")
        return None


def run(host: str = HOST, port: int = PORT) -> None:
    httpd = ThreadingHTTPServer((host, port), OJRequestHandler)
    print(f"OJ backend listening on http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
