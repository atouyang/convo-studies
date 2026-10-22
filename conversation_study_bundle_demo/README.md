# Conversation Study Prototype

Files
- `stage1_instructions.html` + `stage1_instructions.json`
- `stage2_transcript.html` + `stage2_transcript.json`
- `stage3_questionnaire.html` + `stage3_questionnaire.json`
- `config.json`

Behavior
1. Stage 1 shows instructions. ENTER starts the transcript.
2. Stage 2 shows two transcript rows at a time. ENTER advances.
3. Stage 3 shows all 15 BFI-2-XS items using a 5-point response scale.
4. In local testing, submission downloads a JSON result file.
5. For deployment, set `submit_endpoint` in `config.json` to your server endpoint.

Important configuration
- `rated_person`: which participant the questionnaire is about.
- `rows_per_transcript_screen`: currently 2.
- `submit_endpoint`: null for local testing, URL for production.
- `completion_url`: optional redirect after server submission.

Speaker IDs from the source transcript are not displayed to participants; they are mapped to Person A / Person B.

Run locally from this folder:
    python -m http.server 8000

Then open:
    http://localhost:8000/stage1_instructions.html
