# Conversation Study — load any conversation by ID

This is the original multi-stage study, not a separate CSV table viewer. The
launcher, instructions, two-utterance transcript screens, debugging shortcuts,
and personality questionnaire are preserved.

## Start the server

In `conversation_study_debug/`, run:

```bash
python conversation_server.py
```

Open (substitute your real conversation ID):

```text
http://localhost:8000/launch.html?convo_id=002d68da-7738-4177-89d9-d72ae803e0e4
```

`http://localhost:8000/?convo_id=...` also works: the server redirects to
`launch.html` while retaining the conversation ID.

The launcher reads the selected CSV, populates **Target speaker** with the
actual speakers in that file, and starts the existing study when you click
**Launch study**. To change conversations, edit `convo_id` in the URL or type
another ID into the launcher. The ID is passed through all three stages.

CSV files are read *directly*; no preprocessing/export is necessary:

```text
../../conversation/data/processed_media_part_001/<convo_id>/transcription/transcript_cliffhanger.csv
```

This path is relative to `conversation_study_debug/`, independent of where you
run the server command. The CSV must have `speaker` and `utterance` columns;
`turn_id` is optional. The same speaker IDs appear in the target selector, but
transcript screens continue to show Person A / Person B.

If the data directory is in a different place, override it with an absolute
path to the directory **containing the conversation-ID folders**:

```bash
CONVERSATION_DATA_ROOT=/absolute/path/to/processed_media_part_001 python conversation_server.py
```

## Notes

- Use the Python server **instead of VS Code Live Server** for direct CSV
  loading. The browser cannot directly read CSVs located outside the web root.
- Keep `router.js`, `launch.html`, `stage1_instructions.html`,
  `stage2_transcript.html` and `stage3_questionnaire.html` together.
- `conversation-switcher.js` is no longer used. Remove its script tag if you
  copied it into another version of `launch.html`.
- The original exported example, `example_conversation`, can still load via
  its existing `data/conversations/example_conversation.json` file.
- For quick debugging, check that
  `http://localhost:8000/api/conversations/<convo_id>` returns a JSON object
  with `conversation_id`, `speakers`, and `utterances`.
- If port 8000 is in use, stop the previous server before restarting, or set
  `CONVERSATION_PORT=8001` and change the URL's port accordingly.

## Other debug options

In the launcher, the Debug mode checkbox still supports skipping stages.
Stage 2 still has **Jump to end of transcript**, and Stage 3 has
**Fill all with Neutral**. The questionnaire responses are still downloaded
as JSON when `submit_endpoint` is unset.

`prepare_study_data.py` remains available for the older, pre-exported JSON
workflow, but it is **not required** to load CSVs dynamically.


## If `loadConversationData is not defined` appears

This means the browser is running the old `router.js`, or `router.js` failed to load.
Replace **router.js** along with the four HTML pages. The script imports are
versioned (`router.js?v=20261022-fix1`) to bypass the browser's old cache.
Hard-refresh the study page (Ctrl+Shift+R or Cmd+Shift+R).

Verify that `http://localhost:8000/router.js?v=20261022-fix1` displays
`window.loadConversationData = async function ...` near the bottom. If it
does not, you are serving an older folder or the file was not replaced.
Run `python conversation_server.py` from the same folder that contains
`launch.html` and `router.js`.
