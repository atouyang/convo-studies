"""Serve the existing conversation_study_debug frontend and CSV transcripts.

Put this file inside conversation_study_debug and run:
    python conversation_server.py

Then open http://localhost:8000/?convo_id=YOUR_CONVO_ID

The transcript directory is resolved relative to this file, not the shell's
current working directory.
"""

import csv
import json
import os
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


HERE = Path(__file__).resolve().parent
# Expected repo layout:  sibling folders ``convo-studies`` and ``conversation``.
DATA_ROOT = Path(
    os.environ.get(
        "CONVERSATION_DATA_ROOT",
        str(HERE / "../../conversation/data/processed_media_part_001"),
    )
).resolve()
TRANSCRIPT_FILENAME = "transcript_cliffhanger.csv"
CONVO_ID_PATTERN = re.compile(r"[A-Za-z0-9_-]+\Z")


class ConversationHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(HERE), **kwargs)

    def send_json(self, status, payload):
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        parsed = urlsplit(self.path)
        path = parsed.path

        # The demo entry point is launch.html, not index.html.
        # Preserve query parameters (notably convo_id) across redirect.
        if path == "/":
            location = "/launch.html"
            if parsed.query:
                location += "?" + parsed.query
            self.send_response(302)
            self.send_header("Location", location)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        prefix = "/api/conversations/"
        if not path.startswith(prefix):
            return super().do_GET()

        convo_id = unquote(path[len(prefix):])
        if not CONVO_ID_PATTERN.fullmatch(convo_id):
            return self.send_json(400, {"error": "Invalid convo_id"})

        csv_path = DATA_ROOT / convo_id / "transcription" / TRANSCRIPT_FILENAME
        if not csv_path.is_file():
            return self.send_json(
                404,
                {"error": "Transcript not found", "convo_id": convo_id,
                 "expected_path": str(csv_path)},
            )

        try:
            with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
                reader = csv.DictReader(fh)
                if not reader.fieldnames:
                    return self.send_json(422, {"error": "Transcript has no header"})
                columns = reader.fieldnames
                rows = list(reader)
        except (OSError, UnicodeError, csv.Error) as exc:
            return self.send_json(500, {"error": f"Could not read transcript: {exc}"})

        return self.send_json(
            200, {"convo_id": convo_id, "columns": columns, "rows": rows,
                  "row_count": len(rows)},
        )


if __name__ == "__main__":
    host = os.environ.get("CONVERSATION_HOST", "127.0.0.1")
    port = int(os.environ.get("CONVERSATION_PORT", "8000"))
    print(f"Serving demo at http://{host}:{port}")
    print(f"Transcript root: {DATA_ROOT}")
    ThreadingHTTPServer((host, port), ConversationHandler).serve_forever()
