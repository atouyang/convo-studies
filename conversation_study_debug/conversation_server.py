"""Serve the original conversation study using transcripts selected by conversation ID.

From this directory run:
    python conversation_server.py

Then open:
    http://localhost:8000/launch.html?convo_id=YOUR_CONVO_ID

The CSV location is relative to this script, not the current terminal directory:
    ../../conversation/data/processed_media_part_001/<convo_id>/transcription/transcript_cliffhanger.csv

Override the directory containing conversation ID folders with the
CONVERSATION_DATA_ROOT environment variable if your data is elsewhere.
"""

import csv
import json
import os
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
DATA_ROOT = Path(
    os.environ.get(
        "CONVERSATION_DATA_ROOT",
        str(HERE / "../../conversation/data/processed_media_part_001"),
    )
).expanduser().resolve()
TRANSCRIPT_FILENAME = "transcript_cliffhanger.csv"
CONVO_ID_PATTERN = re.compile(r"[A-Za-z0-9_-]+\Z")


def read_conversation(convo_id):
    """Convert a Cliffhanger CSV into the schema used by the existing study."""
    path = DATA_ROOT / convo_id / "transcription" / TRANSCRIPT_FILENAME
    if not path.is_file():
        raise FileNotFoundError(str(path))

    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames:
            raise ValueError("CSV has no header")
        fields = {name.strip(): name for name in reader.fieldnames}
        speaker_key = fields.get("speaker", fields.get("speaker_id"))
        utterance_key = fields.get("utterance")
        turn_key = fields.get("turn_id")
        if not speaker_key or not utterance_key:
            raise ValueError("CSV must contain 'speaker' and 'utterance' columns")

        speakers = []
        utterances = []
        for index, row in enumerate(reader):
            speaker = (row.get(speaker_key) or "").strip()
            if not speaker:
                raise ValueError(f"Missing speaker in CSV row {index + 2}")
            if speaker not in speakers:
                speakers.append(speaker)

            # Retain the source turn_id where available, for timing output.
            raw_turn_id = row.get(turn_key) if turn_key else None
            try:
                turn_id = int(raw_turn_id) if raw_turn_id else index
            except (TypeError, ValueError):
                turn_id = index
            utterances.append({
                "turn_id": turn_id,
                "speaker_id": speaker,
                "utterance": row.get(utterance_key) or "",
            })

    if not utterances:
        raise ValueError("CSV contains no utterances")

    return {
        "conversation_id": convo_id,
        "speakers": speakers,
        "n_utterances": len(utterances),
        "utterances": utterances,
    }


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

        if path == "/":
            # launch.html is the entry point (this demo has no index.html).
            location = "/launch.html"
            if parsed.query:
                location += "?" + parsed.query
            self.send_response(302)
            self.send_header("Location", location)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        prefix = "/api/conversations/"
        if path.startswith(prefix):
            convo_id = unquote(path[len(prefix):])
            if not CONVO_ID_PATTERN.fullmatch(convo_id):
                return self.send_json(400, {"error": "Invalid convo_id"})
            try:
                conversation = read_conversation(convo_id)
            except FileNotFoundError as exc:
                return self.send_json(404, {
                    "error": "Transcript not found",
                    "conversation_id": convo_id,
                    "expected_path": str(exc),
                })
            except (OSError, UnicodeError, csv.Error, ValueError) as exc:
                return self.send_json(422, {"error": f"Could not read transcript: {exc}"})
            return self.send_json(200, conversation)

        return super().do_GET()


if __name__ == "__main__":
    host = os.environ.get("CONVERSATION_HOST", "127.0.0.1")
    port = int(os.environ.get("CONVERSATION_PORT", "8000"))
    print(f"Serving study at http://{host}:{port}/launch.html")
    print(f"Transcript root: {DATA_ROOT}")
    ThreadingHTTPServer((host, port), ConversationHandler).serve_forever()
