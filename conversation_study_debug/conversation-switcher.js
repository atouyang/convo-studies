/*
 * Conversation selector for conversation_study_debug.
 * Add <script src="conversation-switcher.js"></script> after the demo's
 * existing scripts, just before </body>.
 *
 * The existing demo can consume loaded rows by defining:
 *   window.onConversationLoaded = ({ convo_id, columns, rows }) => {
 *     // Update the demo's data store, then redraw its components.
 *   };
 *
 * If no handler exists, a basic transcript table is displayed instead.
 */
(() => {
  "use strict";

  const form = document.createElement("form");
  form.id = "conversation-switcher";
  form.style.cssText = "display:flex;align-items:center;gap:8px;padding:12px;flex-wrap:wrap";

  const label = document.createElement("label");
  label.textContent = "Conversation ID";
  label.htmlFor = "conversation-id";
  const input = document.createElement("input");
  input.id = "conversation-id";
  input.name = "convo_id";
  input.required = true;
  input.placeholder = "Enter convo_id";
  input.value = new URLSearchParams(location.search).get("convo_id") || "";

  const button = document.createElement("button");
  button.type = "submit";
  button.textContent = "Load conversation";
  const status = document.createElement("span");
  status.id = "conversation-status";
  status.setAttribute("role", "status");
  form.append(label, input, button, status);
  document.body.prepend(form);

  let preview = null;

  // Only a fallback. Your existing demo should define onConversationLoaded.
  function showPreview({ columns, rows }) {
    if (!preview) {
      preview = document.createElement("section");
      preview.id = "conversation-preview";
      preview.style.cssText = "padding:12px;max-height:65vh;overflow:auto";
      form.after(preview);
    }
    preview.replaceChildren();
    const table = document.createElement("table");
    table.style.cssText = "border-collapse:collapse;width:100%;font-size:14px";
    const head = document.createElement("thead");
    const headerRow = document.createElement("tr");
    columns.forEach((column) => {
      const th = document.createElement("th");
      th.textContent = column;
      th.style.cssText = "text-align:left;border-bottom:1px solid #aaa;padding:6px";
      headerRow.appendChild(th);
    });
    head.appendChild(headerRow);
    const body = document.createElement("tbody");
    rows.forEach((row) => {
      const tr = document.createElement("tr");
      columns.forEach((column) => {
        const td = document.createElement("td");
        td.textContent = row[column] ?? "";
        td.style.cssText = "border-bottom:1px solid #ddd;padding:6px;vertical-align:top";
        tr.appendChild(td);
      });
      body.appendChild(tr);
    });
    table.append(head, body);
    preview.appendChild(table);
  }

  async function loadConversation(convoId) {
    const id = String(convoId).trim();
    if (!/^[A-Za-z0-9_-]+$/.test(id)) {
      throw new Error("convo_id may contain only letters, numbers, _ and -");
    }
    const response = await fetch(`/api/conversations/${encodeURIComponent(id)}`);
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);

    // Preserve CSV columns and all original cells for the existing demo.
    window.dispatchEvent(new CustomEvent("conversation:loaded", { detail: payload }));
    if (typeof window.onConversationLoaded === "function") {
      if (preview) preview.remove();
      preview = null;
      await window.onConversationLoaded(payload);
    } else {
      showPreview(payload);
    }
    return payload;
  }

  // Optional way for existing app code to trigger loading programmatically.
  window.loadConversationById = loadConversation;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const id = input.value.trim();
    button.disabled = true;
    status.textContent = "Loading...";
    try {
      const payload = await loadConversation(id);
      const url = new URL(location.href);
      url.searchParams.set("convo_id", id);
      history.replaceState({}, "", url);
      status.textContent = `Loaded ${payload.row_count} rows`;
    } catch (error) {
      status.textContent = `Error: ${error.message}`;
    } finally {
      button.disabled = false;
    }
  });

  if (input.value) form.requestSubmit();
})();
