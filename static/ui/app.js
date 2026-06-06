const messagesEl = document.getElementById("messages");
const form = document.getElementById("chatForm");
const queryInput = document.getElementById("queryInput");
const siteSelect = document.getElementById("siteId");
const modelSelect = document.getElementById("modelSelect");
const sendBtn = document.getElementById("sendBtn");
const modeBadge = document.getElementById("modeBadge");
const agentModelsList = document.getElementById("agentModelsList");

let uiConfig = {
  sites: [1, 3, 15],
  default_site_id: 3,
  synthesis_mode: "template",
  chat_endpoint: "/chat/stream",
  models: { recommended: [], all: [], default: "" },
};

/** Abort in-flight stream when the shopper sends a new message. */
let activeChatAbort = null;

function appendMessage(role, text, products = [], options = {}) {
  const wrap = document.createElement("div");
  const extra = options.status ? " status-reply" : "";
  wrap.className = `msg ${role}${extra}${options.decline ? " decline" : ""}${options.error ? " error" : ""}`;
  if (options.status) {
    wrap.setAttribute("role", "status");
    wrap.setAttribute("aria-live", "polite");
  }
  wrap.textContent = text;

  if (products.length > 0) {
    const list = document.createElement("div");
    list.className = "products";
    for (const p of products) {
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `<strong>${escapeHtml(p.product_name)}</strong>
        <span class="meta">${escapeHtml(p.brands)} · ${p.pet_type} · EUR ${Number(p.price).toFixed(2)} · #${p.article_id}</span>`;
      list.appendChild(card);
    }
    wrap.appendChild(list);
  }

  messagesEl.appendChild(wrap);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function escapeHtml(s) {
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

function normalizeAnswer(text) {
  if (!text) return "";
  let raw = String(text).trim();
  const fenced = raw.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/i);
  if (fenced) raw = fenced[1].trim();
  if (raw.startsWith("{")) {
    try {
      const data = JSON.parse(raw);
      if (typeof data.answer === "string") return data.answer.trim();
      if (typeof data.text === "string") return data.text.trim();
    } catch (_) {
      /* keep raw */
    }
  }
  return raw;
}

function formatModelLabel(model, agent) {
  const m = model || selectedModel() || uiConfig.opencode_model || "opencode";
  const short = m.includes("/") ? m.split("/").slice(-2).join("/") : m;
  return agent ? `${short} · ${agent}` : short;
}

function selectedModel() {
  return modelSelect && modelSelect.value ? modelSelect.value : null;
}

function setModeBadge(meta) {
  const mode = uiConfig.synthesis_mode || "template";
  if (meta && meta.llm_model) {
    const auth = uiConfig.opencode_auth_configured ? "" : " · auth missing";
    modeBadge.textContent = `LLM: ${formatModelLabel(meta.llm_model, meta.llm_agent)}${auth}`;
    modeBadge.classList.add("llm");
    return;
  }
  if (mode === "opencode") {
    const auth = uiConfig.opencode_auth_configured ? "auth OK" : "auth missing";
    modeBadge.textContent = `LLM: ${formatModelLabel(selectedModel())} (${auth})`;
    modeBadge.classList.add("llm");
  } else {
    modeBadge.textContent = "Synthesis: template";
    modeBadge.classList.remove("llm");
  }
}

function shortModelId(id) {
  if (!id) return "";
  return id.includes("/") ? id.split("/").slice(-2).join("/") : id;
}

function populateAgentModels() {
  if (!agentModelsList) return;
  const map = uiConfig.agent_models || {};
  agentModelsList.innerHTML = "";
  const order = [
    "zooplus-conductor",
    "zooplus-intent-agent",
    "zooplus-social-agent",
    "zooplus-topic-guard",
    "zooplus-rag-worker",
    "zooplus-logic-worker",
    "zooplus-synthesis",
  ];
  for (const agentId of order) {
    const model = map[agentId];
    if (!model) continue;
    const li = document.createElement("li");
    li.textContent = `${agentId.replace("zooplus-", "")}: ${shortModelId(model)}`;
    agentModelsList.appendChild(li);
  }
}

function populateModelSelect() {
  if (!modelSelect) return;
  const block = uiConfig.models || {};
  const ids = (block.recommended && block.recommended.length)
    ? block.recommended
    : (block.all || []).slice(0, 12);

  const keep = modelSelect.querySelector('option[value=""]');
  modelSelect.innerHTML = "";
  if (keep) modelSelect.appendChild(keep);
  else {
    const def = document.createElement("option");
    def.value = "";
    def.textContent = "Per-agent (default)";
    modelSelect.appendChild(def);
  }
  for (const id of ids) {
    const opt = document.createElement("option");
    opt.value = id;
    opt.textContent = shortModelId(id);
    modelSelect.appendChild(opt);
  }
  modelSelect.value = "";
  modelSelect.onchange = () => setModeBadge();
}

async function loadConfig() {
  try {
    const res = await fetch("/api/ui/config");
    if (res.ok) uiConfig = await res.json();
  } catch (_) {
    /* use defaults */
  }
  siteSelect.innerHTML = "";
  const labels = uiConfig.site_labels || {};
  for (const id of uiConfig.sites || [1, 3, 15]) {
    const opt = document.createElement("option");
    opt.value = String(id);
    opt.textContent = labels[id] || labels[String(id)] || `Shop site_id ${id}`;
    siteSelect.appendChild(opt);
  }
  siteSelect.value = String(uiConfig.default_site_id || 3);
  populateAgentModels();
  populateModelSelect();
  setModeBadge();
}

async function consumeChatStream(response, signal) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let finalAnswer = "";
  let finalProducts = [];
  let finalMeta = null;

  while (true) {
    if (signal.aborted) return null;

    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const raw of lines) {
      const line = raw.trim();
      if (!line) continue;
      if (signal.aborted) return null;

      let evt;
      try {
        evt = JSON.parse(line);
      } catch (_) {
        continue;
      }

      if (evt.type === "status" && evt.text) {
        appendMessage("bot", evt.text, [], { status: true });
      } else if (evt.type === "done") {
        finalAnswer = normalizeAnswer(evt.answer) || "";
        finalProducts = evt.retrieved_products || [];
        finalMeta = evt.meta || null;
      }
    }
  }

  return { answer: finalAnswer, products: finalProducts, meta: finalMeta };
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const query = queryInput.value.trim();
  if (!query) return;

  if (activeChatAbort) {
    activeChatAbort.abort();
    activeChatAbort = null;
  }

  const siteId = Number(siteSelect.value);
  const preferredModel = selectedModel();
  appendMessage("user", query);
  queryInput.value = "";
  sendBtn.disabled = true;

  const controller = new AbortController();
  activeChatAbort = controller;
  const clientTimeout = setTimeout(() => controller.abort(), 50000);

  try {
    const body = { site_id: siteId, query };
    if (preferredModel && preferredModel.trim()) body.preferred_model = preferredModel.trim();

    const endpoint = uiConfig.chat_endpoint || uiConfig.stream_endpoint || "/chat/stream";
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    clearTimeout(clientTimeout);

    if (!res.ok) {
      const err = await res.text();
      appendMessage("bot", `Error ${res.status}: ${err}`, [], { error: true });
      return;
    }

    const result = await consumeChatStream(res, controller.signal);
    if (!result || controller.signal.aborted) return;

    const { answer, products, meta } = result;
    if (meta) setModeBadge(meta);
    const decline =
      products.length === 0 && /can't help|couldn't find|zooplus Assistant/i.test(answer || "");
    appendMessage("bot", answer || "(empty)", products, { decline });
  } catch (err) {
    clearTimeout(clientTimeout);
    if (err.name === "AbortError") {
      if (activeChatAbort === controller) return;
    }
    const msg =
      err.name === "AbortError"
        ? "Request timed out (50s). Try a shorter question or pick a faster model."
        : `Network error: ${err.message}`;
    appendMessage("bot", msg, [], { error: true });
  } finally {
    if (activeChatAbort === controller) activeChatAbort = null;
    sendBtn.disabled = false;
    queryInput.focus();
  }
});

queryInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    if (!sendBtn.disabled && queryInput.value.trim()) {
      form.requestSubmit();
    }
  }
});

loadConfig().then(() => {
  appendMessage(
    "bot",
    "Hi! Pick a shop and model, then ask about pet products. Off-topic questions are declined.",
  );
});
