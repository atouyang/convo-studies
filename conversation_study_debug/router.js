
function getStudyParams() {
  const params = new URLSearchParams(window.location.search);
  return {
    params,
    conversationId: params.get("conversation_id") || params.get("convo_id"),
    targetId: params.get("target_id"),
    participantId: params.get("participant_id"),
    debug: params.get("debug") === "1",
    skipStages: new Set(
      (params.get("skip") || "")
        .split(",")
        .map(x => x.trim())
        .filter(Boolean)
    )
  };
}

function stageFilename(stage) {
  if (stage === 1) return "stage1_instructions.html";
  if (stage === 2) return "stage2_transcript.html";
  if (stage === 3) return "stage3_questionnaire.html";
  return "complete.html";
}

function nextStageAfter(currentStage) {
  const { debug, skipStages } = getStudyParams();
  for (let stage = currentStage + 1; stage <= 3; stage++) {
    if (!(debug && skipStages.has(String(stage)))) return stage;
  }
  return 4;
}

function goToNextStage(currentStage) {
  const next = nextStageAfter(currentStage);
  const query = window.location.search.substring(1);
  window.location.href = `${stageFilename(next)}?${query}`;
}

function routeIfCurrentStageSkipped(currentStage) {
  const { debug, skipStages } = getStudyParams();
  if (debug && skipStages.has(String(currentStage))) {
    goToNextStage(currentStage);
    return true;
  }
  return false;
}

// Return the same { conversation_id, speakers, utterances } object for either
// a live Cliffhanger CSV (served by conversation_server.py) or an existing
// pre-exported data/conversations/<id>.json file.
window.loadConversationData = async function loadConversationData(conversationId) {
  const id = String(conversationId || "").trim();
  if (!/^[A-Za-z0-9_-]+$/.test(id)) {
    throw new Error("Enter a valid conversation ID (letters, numbers, _ or -).");
  }

  let apiFailure = null;
  try {
    const response = await fetch(`/api/conversations/${encodeURIComponent(id)}`, {
      cache: "no-store"
    });
    if (response.ok) return await response.json();

    const body = (response.headers.get("content-type") || "").includes("application/json")
      ? await response.json()
      : {};
    apiFailure = body.expected_path
      ? `${body.error}: ${body.expected_path}`
      : (body.error || `Conversation API returned HTTP ${response.status}`);
  } catch (error) {
    apiFailure = error.message;
  }

  // Preserve the demo's example and any conversations previously exported as JSON.
  const fallback = await fetch(`data/conversations/${encodeURIComponent(id)}.json`);
  if (fallback.ok) return await fallback.json();

  throw new Error(
    `${apiFailure || "Conversation not found"}. ` +
    "For CSV transcripts, run 'python conversation_server.py' instead of Live Server."
  );
};
