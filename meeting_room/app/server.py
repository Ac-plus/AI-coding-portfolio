from __future__ import annotations

import argparse
import json
import os
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .service import BookingError, BookingService


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
SERVICE = BookingService()


class MeetingRoomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/rooms":
            self._handle_list_rooms()
            return
        if parsed.path == "/api/bookings":
            self._handle_list_bookings()
            return
        if parsed.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/bookings":
            self._handle_create_booking()
            return
        self._json_response(HTTPStatus.NOT_FOUND, {"error": "接口不存在。"})

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/api/bookings/"):
            self._json_response(HTTPStatus.NOT_FOUND, {"error": "接口不存在。"})
            return

        booking_id = parsed.path.removeprefix("/api/bookings/").strip()
        if not booking_id:
            self._json_response(HTTPStatus.BAD_REQUEST, {"error": "booking_id 不能为空。"})
            return

        try:
            booking = SERVICE.cancel_booking(booking_id)
        except BookingError as exc:
            self._json_response(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return

        self._json_response(HTTPStatus.OK, {"data": booking})

    def log_message(self, format: str, *args) -> None:
        return

    def _handle_list_rooms(self) -> None:
        self._json_response(HTTPStatus.OK, {"data": SERVICE.list_rooms()})

    def _handle_list_bookings(self) -> None:
        self._json_response(HTTPStatus.OK, {"data": SERVICE.list_bookings()})

    def _handle_create_booking(self) -> None:
        try:
            payload = self._read_json_body()
            booking = SERVICE.create_booking(payload)
        except json.JSONDecodeError:
            self._json_response(HTTPStatus.BAD_REQUEST, {"error": "请求体不是合法 JSON。"})
            return
        except BookingError as exc:
            self._json_response(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return

        self._json_response(HTTPStatus.CREATED, {"data": booking})

    def _read_json_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        return json.loads(raw_body.decode("utf-8"))

    def _json_response(self, status: HTTPStatus, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), MeetingRoomHandler)
    print(f"Server running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Meeting room MVP server")
    parser.add_argument("--host", default=os.getenv("MEETING_ROOM_HOST", "127.0.0.1"))
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("MEETING_ROOM_PORT", "8000")),
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run(host=args.host, port=args.port)
