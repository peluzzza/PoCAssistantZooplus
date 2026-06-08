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
  site_labels: {
    1: "Germany (de-DE)",
    3: "United Kingdom (en-GB)",
    15: "Spain (es-ES)",
  },
  default_site_id: 3,
  synthesis_mode: "template",
  chat_endpoint: "/chat/stream",
  models: { recommended: [], all: [], default: "" },
};

/** Abort in-flight stream when the shopper sends a new message. */
let activeChatAbort = null;
let configReady = false;
let chatSessionId = localStorage.getItem("zooplus_chat_session") || "";
if (!chatSessionId) {
  chatSessionId = crypto.randomUUID();
  localStorage.setItem("zooplus_chat_session", chatSessionId);
}
let typingEl = null;
let typingTimer = null;
let typingStep = 0;
const PACE_TYPING_MS = 1400;
const PACE_GAP_MS = 900;
const PACE_FINAL_MS = 1100;
let chunkInbox = [];
let chunkPaceChain = Promise.resolve();

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function enqueueChunk(text, chunkIndex) {
  chunkInbox.push({ text, chunkIndex: chunkIndex ?? 99 });
  chunkPaceChain = chunkPaceChain.then(drainChunkInbox);
}

async function drainChunkInbox() {
  while (chunkInbox.length > 0) {
    const item = chunkInbox.shift();
    const text = item.text;
    const typingMs = item.chunkIndex === 0 ? 350 : PACE_TYPING_MS;
    showTypingIndicator();
    await sleep(typingMs);
    hideTypingIndicator();
    appendMessage("bot", text);
    if (chunkInbox.length > 0) await sleep(PACE_GAP_MS);
  }
}

async function waitForChunkPacing() {
  await chunkPaceChain;
}

function resolvedSiteId() {
  const picked = Number(siteSelect.value);
  if (Number.isFinite(picked) && picked >= 1) return picked;
  const fallback = Number(uiConfig.default_site_id);
  return Number.isFinite(fallback) && fallback >= 1 ? fallback : 3;
}

function populateSiteSelect() {
  siteSelect.innerHTML = "";
  const labels = uiConfig.site_labels || {};
  for (const id of uiConfig.sites || [1, 3, 15]) {
    const opt = document.createElement("option");
    opt.value = String(id);
    opt.textContent =
      labels[id] ||
      labels[String(id)] ||
      uiConfig.site_labels?.[id] ||
      uiConfig.site_labels?.[String(id)] ||
      `Shop site_id ${id}`;
    siteSelect.appendChild(opt);
  }
  const desired = String(uiConfig.default_site_id || 3);
  if ([...siteSelect.options].some((o) => o.value === desired)) {
    siteSelect.value = desired;
  } else if (siteSelect.options.length > 0) {
    siteSelect.value = siteSelect.options[0].value;
  }
}

function scrollMessagesToEnd() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function showTypingIndicator() {
  if (!typingEl) {
    typingEl = document.createElement("div");
    typingEl.className = "msg bot typing-indicator";
    typingEl.setAttribute("aria-live", "polite");
    typingEl.setAttribute("aria-label", "Assistant is typing");
    const dots = document.createElement("span");
    dots.className = "typing-dots";
    dots.textContent = ".";
    typingEl.appendChild(dots);
    messagesEl.appendChild(typingEl);
  }
  scrollMessagesToEnd();
  if (!typingTimer) {
    typingStep = 0;
    typingTimer = setInterval(() => {
      typingStep = (typingStep + 1) % 3;
      const patterns = [".", "..", "..."];
      const span = typingEl?.querySelector(".typing-dots");
      if (span) span.textContent = patterns[typingStep];
    }, 450);
  }
}

function hideTypingIndicator() {
  if (typingTimer) {
    clearInterval(typingTimer);
    typingTimer = null;
  }
  typingStep = 0;
  if (typingEl) {
    typingEl.remove();
    typingEl = null;
  }
}

function buildProductCard(p) {
  const card = document.createElement("div");
  card.className = "card";
  card.innerHTML = `<strong>${escapeHtml(p.product_name)}</strong>
    <span class="meta">${escapeHtml(p.brands)} · ${p.pet_type} · EUR ${Number(p.price).toFixed(2)} · #${p.article_id}</span>`;
  return card;
}

function appendProductCards(listEl, products) {
  for (const p of products) {
    listEl.appendChild(buildProductCard(p));
  }
}

function appendMessage(role, text, products = [], options = {}) {
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}${options.decline ? " decline" : ""}${options.error ? " error" : ""}`;
  wrap.textContent = text;

  if (products.length > 0) {
    const list = document.createElement("div");
    list.className = "products";
    appendProductCards(list, products);
    wrap.appendChild(list);
  }

  messagesEl.appendChild(wrap);
  scrollMessagesToEnd();
  return wrap;
}

/** Live stream: product cards arrive in batches before the final answer. */
let streamingProductWrap = null;
let streamingProductList = null;

function resetStreamingProducts() {
  streamingProductWrap = null;
  streamingProductList = null;
}

function enqueueProductBatch(products, batchIndex) {
  if (!products || products.length === 0) return;
  const delay = batchIndex === 0 ? 200 : PACE_GAP_MS;
  chunkPaceChain = chunkPaceChain.then(async () => {
    await sleep(delay);
    if (!streamingProductWrap) {
      streamingProductWrap = document.createElement("div");
      streamingProductWrap.className = "msg bot";
      streamingProductList = document.createElement("div");
      streamingProductList.className = "products";
      streamingProductWrap.appendChild(streamingProductList);
      messagesEl.appendChild(streamingProductWrap);
    }
    appendProductCards(streamingProductList, products);
    scrollMessagesToEnd();
  });
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
  populateSiteSelect();
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
  let streamedProductCount = 0;
  resetStreamingProducts();

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

      if (evt.type === "typing") {
        if (evt.active !== false) showTypingIndicator();
      } else if (evt.type === "chunk" && evt.text) {
        enqueueChunk(evt.text, evt.chunk);
      } else if (evt.type === "status" && evt.text) {
        enqueueChunk(evt.text, evt.chunk);
      } else if (evt.type === "product_batch" && evt.retrieved_products) {
        streamedProductCount += evt.retrieved_products.length;
        enqueueProductBatch(evt.retrieved_products, evt.batch ?? 0);
      } else if (evt.type === "products" && evt.retrieved_products) {
        streamedProductCount += evt.retrieved_products.length;
        enqueueProductBatch(evt.retrieved_products, 0);
      } else if (evt.type === "done") {
        finalAnswer = normalizeAnswer(evt.answer) || "";
        finalProducts = evt.retrieved_products || [];
        finalMeta = evt.meta || null;
      }
    }
  }

  return {
    answer: finalAnswer,
    products: finalProducts,
    meta: finalMeta,
    streamedProductCount,
  };
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const query = queryInput.value.trim();
  if (!query) return;

  if (activeChatAbort) {
    activeChatAbort.abort();
    activeChatAbort = null;
  }
  const siteId = resolvedSiteId();
  if (!configReady && siteId < 1) {
    appendMessage("bot", "Shop list still loading — wait a moment and try again.", [], { error: true });
    return;
  }
  const preferredModel = selectedModel();
  appendMessage("user", query);
  queryInput.value = "";
  sendBtn.disabled = true;
  showTypingIndicator();

  const controller = new AbortController();
  activeChatAbort = controller;
  const clientTimeout = setTimeout(() => controller.abort(), 50000);

  try {
    const body = { site_id: siteId, query, session_id: chatSessionId };
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
      if (res.status === 422 && err.includes("site_id")) {
        appendMessage(
          "bot",
          "Please pick a shop from the dropdown above, then send your message again.",
          [],
          { error: true },
        );
      } else {
        appendMessage("bot", `Error ${res.status}: ${err}`, [], { error: true });
      }
      return;
    }

    const result = await consumeChatStream(res, controller.signal);
    await waitForChunkPacing();
    if (!result || controller.signal.aborted) return;

    const { answer, products, meta, streamedProductCount } = result;
    if (meta) setModeBadge(meta);
    const decline =
      products.length === 0 && /can't help|couldn't find|zooplus Assistant/i.test(answer || "");
    showTypingIndicator();
    await sleep(PACE_FINAL_MS);
    hideTypingIndicator();
    const productsAlreadyStreamed = streamedProductCount > 0;
    if (productsAlreadyStreamed && streamingProductWrap && answer) {
      const answerEl = document.createElement("div");
      answerEl.className = "stream-answer";
      answerEl.textContent = answer || "(empty)";
      streamingProductWrap.insertBefore(answerEl, streamingProductWrap.firstChild);
      if (decline) streamingProductWrap.classList.add("decline");
      scrollMessagesToEnd();
      resetStreamingProducts();
    } else {
      appendMessage("bot", answer || "(empty)", products, { decline });
      resetStreamingProducts();
    }
  } catch (err) {
    clearTimeout(clientTimeout);
    hideTypingIndicator();
    if (err.name === "AbortError") {
      if (activeChatAbort === controller) return;
    }
    const msg =
      err.name === "AbortError"
        ? "Request timed out (50s). Try a shorter question or pick a faster model."
        : `Network error: ${err.message}`;
    appendMessage("bot", msg, [], { error: true });
  } finally {
    hideTypingIndicator();
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

populateSiteSelect();
sendBtn.disabled = true;

loadConfig().then(() => {
  configReady = true;
  sendBtn.disabled = false;
  appendMessage(
    "bot",
    "Hi! Pick a shop and model, then ask about pet products. Off-topic questions are declined.",
  );
});
