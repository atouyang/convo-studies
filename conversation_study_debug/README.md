# Conversation Study

## Live Server

Open `launch.html` in VS Code and use your normal Live Server shortcut
(e.g. Ctrl+Shift+L in your setup).

The browser URL should start with something like:

`http://127.0.0.1:5500/...`

Do not open the HTML as `file://...`, because the pages load JSON with `fetch()`.

## Debug mode

`launch.html` has a Debug mode checkbox.

You can skip:
- Stage 1 — instructions
- Stage 2 — transcript
- Stage 3 — questionnaire

Extra debug controls:
- Stage 2: **Jump to end of transcript**
- Stage 3: **Fill all with Neutral**

When Debug mode is off, participants do not see any debug controls.

Example:

`stage3_questionnaire.html?conversation_id=abc&target_id=user123&debug=1&skip=1,2`

## Real data

Run:

`python prepare_study_data.py`

Then enter your `conversation/data` path.

The script finds:

`processed_media_part_*/<conversation_id>/transcript_cliffhanger.csv`

and writes one JSON file per conversation.

After that, refresh `launch.html` and choose any exported conversation.
