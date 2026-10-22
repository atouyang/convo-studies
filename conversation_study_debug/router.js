
function getStudyParams() {
  const params = new URLSearchParams(window.location.search);
  return {
    params,
    conversationId: params.get("conversation_id"),
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
