const messagesEl = document.getElementById("messages");
const form = document.getElementById("chatForm");
const queryInput = document.getElementById("queryInput");
const siteSelect = document.getElementById("siteId");
const sendBtn = document.getElementById("sendBtn");
const modeBadge = document.getElementById("modeBadge");

let uiConfig = {
  sites: [1, 3, 15],
  default_site_id: 3,
  synthesis_mode: "template",
};

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

function setModeBadge() {
  const mode = uiConfig.synthesis_mode || "template";
  if (mode === "opencode") {
    const auth = uiConfig.opencode_auth_configured ? "auth OK" : "auth missing";
    modeBadge.textContent = `LLM: ${uiConfig.opencode_model || "opencode"} (${auth})`;
    modeBadge.classList.add("llm");
  } else {
    modeBadge.textContent = "Synthesis: template";
    modeBadge.classList.remove("llm");
  }
}

async function loadConfig() {
  try {
    const res = await fetch("/api/ui/config");
    if (res.ok) uiConfig = await res.json();
  } catch (_) {
    /* use defaults */
  }
  siteSelect.innerHTML = "";
  for (const id of uiConfig.sites || [1, 3, 15]) {
    const opt = document.createElement("option");
    opt.value = String(id);
    opt.textContent = `Site ${id}`;
    siteSelect.appendChild(opt);
  }
  siteSelect.value = String(uiConfig.default_site_id || 3);
  setModeBadge();
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const query = queryInput.value.trim();
  if (!query) return;

  const siteId = Number(siteSelect.value);
  appendMessage("user", query);
  queryInput.value = "";
  sendBtn.disabled = true;

  const typing = document.createElement("div");
  typing.className = "typing";
  typing.textContent = "One moment…";
  messagesEl.appendChild(typing);

  const controller = new AbortController();
  const clientTimeout = setTimeout(() => controller.abort(), 25000);

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ site_id: siteId, query }),
      signal: controller.signal,
    });
    clearTimeout(clientTimeout);
    typing.remove();

    if (!res.ok) {
      const err = await res.text();
      appendMessage("bot", `Error ${res.status}: ${err}`, [], { error: true });
      return;
    }

    const data = await res.json();
    const products = data.retrieved_products || [];
    const decline =
      products.length === 0 &&
      /can't help|couldn't find|not able to help|don't have live|zooplus Assistant|only help with|outside what I can/i.test(
        data.answer || "",
      );
    appendMessage("bot", data.answer || "(empty)", products, { decline });
  } catch (err) {
    clearTimeout(clientTimeout);
    typing.remove();
    const msg =
      err.name === "AbortError"
        ? "Request timed out (25s). Try a shorter question or set ZOOPLUS_SYNTHESIS_MODE=template in .env."
        : `Network error: ${err.message}`;
    appendMessage("bot", msg, [], { error: true });
  } finally {
    sendBtn.disabled = false;
    queryInput.focus();
  }
});

loadConfig().then(() => {
  appendMessage(
    "bot",
    "Hi! I'm the zooplus shop assistant — ask about dog or cat food, treats, toys, and more. " +
      "You can also say hello or ask who I am. Traffic, weather, and other off-topic questions I'll politely redirect.",
  );
});
