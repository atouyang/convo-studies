from pathlib import Path
import pandas as pd
import json

DEFAULT_DATA_DIR = Path("../../conversation/data")
OUTPUT_DIR = Path(__file__).resolve().parent / "data"
CONVERSATION_OUTPUT_DIR = OUTPUT_DIR / "conversations"


def find_questionnaire(data_dir):
    matches = list(data_dir.rglob("bfi_15_2_xs.csv"))
    return matches[0] if matches else None


def find_transcripts(data_dir):
    return sorted(
        p for p in data_dir.rglob("transcript_cliffhanger.csv")
        if p.is_file()
    )


def export_questionnaire(path):
    df = pd.read_csv(path)
    payload = {
        "title": "Personality Questionnaire",
        "instructions": (
            "Based only on the conversation you just read, indicate how well "
            "each statement describes {target_label}."
        ),
        "scale": [
            {"value": 1, "label": "Strongly disagree"},
            {"value": 2, "label": "Disagree"},
            {"value": 3, "label": "Neutral"},
            {"value": 4, "label": "Agree"},
            {"value": 5, "label": "Strongly agree"},
        ],
        "items": [
            {
                "item_id": int(r.item_id),
                "item_text": str(r.item_text),
                "trait": str(r.trait),
                "reverse_scored": bool(r.reverse_scored),
            }
            for r in df.itertuples(index=False)
        ],
    }
    (OUTPUT_DIR / "questionnaire.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def export_conversation(path):
    conversation_id = path.parent.parent.name if path.parent.name == "transcription" else path.parent.name
    df = pd.read_csv(path)
    speakers = df["speaker"].drop_duplicates().astype(str).tolist()

    payload = {
        "conversation_id": conversation_id,
        "speakers": speakers,
        "utterances": [
            {
                "turn_id": int(r.turn_id),
                "speaker_id": str(r.speaker),
                "utterance": "" if pd.isna(r.utterance) else str(r.utterance),
            }
            for r in df.itertuples(index=False)
        ],
    }

    CONVERSATION_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (CONVERSATION_OUTPUT_DIR / f"{conversation_id}.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {
        "conversation_id": conversation_id,
        "speakers": speakers,
        "n_utterances": len(df),
    }


def main():
    raw = input(f"Path to conversation/data [{DEFAULT_DATA_DIR}]: ").strip()
    data_dir = (Path(raw).expanduser() if raw else DEFAULT_DATA_DIR).resolve()

    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    questionnaire = find_questionnaire(data_dir)
    if questionnaire is None:
        raise FileNotFoundError("Could not find bfi_15_2_xs.csv.")
    export_questionnaire(questionnaire)

    transcripts = find_transcripts(data_dir)
    if not transcripts:
        raise FileNotFoundError("Could not find transcript_cliffhanger.csv files.")

    print(f"Found {len(transcripts)} conversations.")
    requested = input("Conversation ID to export [ENTER = all]: ").strip()

    if requested:
        transcripts = [p for p in transcripts if (
            p.parent.parent.name if p.parent.name == "transcription" else p.parent.name
        ) == requested]
        if not transcripts:
            raise ValueError(f"No conversation found with ID: {requested}")

    rows = [export_conversation(p) for p in transcripts]

    manifest_path = OUTPUT_DIR / "conversations.json"
    if requested and manifest_path.exists():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        by_id = {r["conversation_id"]: r for r in existing}
        for r in rows:
            by_id[r["conversation_id"]] = r
        rows = sorted(by_id.values(), key=lambda r: r["conversation_id"])
    else:
        rows = sorted(rows, key=lambda r: r["conversation_id"])

    manifest_path.write_text(
        json.dumps(rows, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("Done. Open launch.html with Live Server / Ctrl+Shift+L.")


if __name__ == "__main__":
    main()
