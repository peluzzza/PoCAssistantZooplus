const messagesEl = document.getElementById("messages");
const form = document.getElementById("chatForm");
const queryInput = document.getElementById("queryInput");
const siteSelect = document.getElementById("siteId");
const modelSelect = document.getElementById("modelSelect");
const sendBtn = document.getElementById("sendBtn");
const modeBadge = document.getElementById("modeBadge");

let uiConfig = {
  sites: [1, 3, 15],
  default_site_id: 3,
  synthesis_mode: "template",
  wait_phases: {
    social: ["One moment…", "Reading message…", "Almost there…"],
    catalog: ["One moment…", "Searching catalog…", "Picking matches…"],
    decline: ["One moment…", "Checking scope…", "Almost there…"],
    default: ["One moment…", "Working on it…", "Almost there…"],
  },
  wait_phase_delays_ms: [0, 1000, 2200],
  wait_phase_max: 3,
  models: { recommended: [], all: [], default: "" },
};

function guessWaitLane(query) {
  const q = query.trim().toLowerCase();
  if (/^(hi|hello|hola|hey|buenas|good\s*(morning|afternoon|evening)|thanks|thank you|bye|goodbye|who are you|what can you|hola\s+que\s+tal|qué\s+tal|que\s+tal)/.test(q)) {
    return "social";
  }
  if (/\b(weather|traffic|news|politic|stock market|bitcoin|recipe for humans)\b/.test(q)) {
    return "decline";
  }
  if (/\b(dog|cat|puppy|kitten|food|treat|snack|litter|collar|leash|grain|hypoallergenic|eur|€|price|under)\b/.test(q)) {
    return "catalog";
  }
  return "default";
}

function waitPhasesForQuery(query) {
  const lane = guessWaitLane(query);
  const map = uiConfig.wait_phases || {};
  const phases = map[lane] || map.default || ["One moment…", "Almost there…"];
  const max = Math.min(uiConfig.wait_phase_max || 3, phases.length);
  return phases.slice(0, max);
}

/** Show 1–3 short status bubbles that appear over time (lane-aware). */
function startWaitMessages(query) {
  const phases = waitPhasesForQuery(query);
  const delays = uiConfig.wait_phase_delays_ms || [0, 1000, 2200];
  const nodes = [];
  const timers = [];

  phases.forEach((text, idx) => {
    const delay = delays[idx] ?? delays[delays.length - 1] ?? 0;
    const timer = setTimeout(() => {
      const el = document.createElement("div");
      el.className = "msg bot wait-phase";
      el.setAttribute("role", "status");
      el.setAttribute("aria-live", "polite");
      el.textContent = text;
      messagesEl.appendChild(el);
      messagesEl.scrollTop = messagesEl.scrollHeight;
      nodes.push(el);
    }, delay);
    timers.push(timer);
  });

  return () => {
    timers.forEach((t) => clearTimeout(t));
    nodes.forEach((n) => n.remove());
  };
}

function appendMessage(role, text, products = [], options = {}) {
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}${options.decline ? " decline" : ""}${options.error ? " error" : ""}`;
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

function populateModelSelect() {
  if (!modelSelect) return;
  const block = uiConfig.models || {};
  const ids = (block.recommended && block.recommended.length)
    ? block.recommended
    : (block.all || []).slice(0, 12);
  const fallback = uiConfig.opencode_model || "opencode/deepseek-v4-flash-free";
  const list = ids.length ? ids : [fallback];

  modelSelect.innerHTML = "";
  for (const id of list) {
    const opt = document.createElement("option");
    opt.value = id;
    opt.textContent = id.replace(/^[^/]+\//, "");
    modelSelect.appendChild(opt);
  }
  const preferred = block.default || fallback;
  if ([...modelSelect.options].some((o) => o.value === preferred)) {
    modelSelect.value = preferred;
  }
  modelSelect.addEventListener("change", () => setModeBadge());
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
  populateModelSelect();
  setModeBadge();
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const query = queryInput.value.trim();
  if (!query) return;

  const siteId = Number(siteSelect.value);
  const preferredModel = selectedModel();
  appendMessage("user", query);
  queryInput.value = "";
  sendBtn.disabled = true;

  const clearWait = startWaitMessages(query);

  const controller = new AbortController();
  const clientTimeout = setTimeout(() => controller.abort(), 50000);

  try {
    const body = { site_id: siteId, query };
    if (preferredModel) body.preferred_model = preferredModel;

    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    clearTimeout(clientTimeout);
    clearWait();

    if (!res.ok) {
      const err = await res.text();
      appendMessage("bot", `Error ${res.status}: ${err}`, [], { error: true });
      return;
    }

    const data = await res.json();
    const products = data.retrieved_products || [];
    if (data.meta) setModeBadge(data.meta);
    const decline = products.length === 0 && /can't help|couldn't find|zooplus Assistant/i.test(data.answer || "");
    appendMessage("bot", normalizeAnswer(data.answer) || "(empty)", products, { decline });
  } catch (err) {
    clearTimeout(clientTimeout);
    clearWait();
    const msg =
      err.name === "AbortError"
        ? "Request timed out (50s). Try a shorter question or pick a faster model."
        : `Network error: ${err.message}`;
    appendMessage("bot", msg, [], { error: true });
  } finally {
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
