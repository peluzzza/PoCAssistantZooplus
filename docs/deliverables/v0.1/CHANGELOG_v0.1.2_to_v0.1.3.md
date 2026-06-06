# Changelog — desde deck PPT v0.1.2 hasta `releases` actual

**Baseline PPT:** commit `2086daf` (13 slides: hybrid RAG + FR1 async evidence)  
**Línea actual:** `releases` @ `678084f` y posteriores  
**Resumen:** conductor-led UX, streaming de estado, routing agentico multilingüe, lexicón desde catálogo, LLMs por agente, latencia y fixes de UI.

---

## 1. Arquitectura y routing (agentic)

| Área | Antes (v0.1.2 PPT) | Ahora |
|------|-------------------|--------|
| Intent | Intent agent → lane en cada turno | **Conductor-first** (`ZOOPLUS_CONDUCTOR_INTENT=1`): clasifica tema **antes** de RAG |
| Saludos / social | Podían disparar búsqueda en catálogo (lentitud) | Fast-path social + conductor: **sin RAG** en *hola*, *thanks*, help |
| Timeout intent | Cascada completa lenta | Fallback por tema + single-agent intent; prefetch catálogo en paralelo |
| Multilingüe | Principalmente inglés en hints | **OpenCode interpreta cualquier idioma**; lexicón del catálogo en prompt |
| Keywords fijos | Hints con dog/cat/perro/gato | **Eliminados**; vocabulario desde `routing_lexicon.json` (ingest) |
| Reparación LLM | — | Opt-in `ZOOPLUS_INTENT_REPAIR=0` (conductor decide; repair solo con señal de catálogo) |

**Archivos clave:** `src/agents/intent_agent.py`, `src/lanes/orchestrator.py`, `src/rag/catalog_lexicon.py`, `src/agents/prompts.py`

---

## 2. UX conversacional (Chat UI)

| Área | Antes | Ahora |
|------|-------|--------|
| Espera en UI | Timers fijos (*One moment…*, *Searching catalog…*) | **`POST /chat/stream`**: estados reales del backend |
| Burbujas de estado | Varias permanentes o estáticas | **Una burbuja transitoria** que se actualiza y **desaparece** al llegar la respuesta |
| Interrupción | — | Nuevo mensaje del usuario **aborta** el stream anterior |
| Idioma UI | — | Copy estático en **inglés**; respuestas del agente **multilingües** |
| `site_id` | Podía enviarse `0` si el usuario enviaba antes de cargar shops | Select poblado al instante; **Send** bloqueado hasta config; fallback shop 3 |

**Archivos clave:** `static/ui/app.js`, `src/lanes/stream.py`, `src/lanes/customer_status.py`, `src/api/routes/ui.py`

---

## 3. Estado al cliente (no técnico)

- Fases: `reading` → `understood` → `searching` → `narrowing` → `composing` (catálogo).
- Texto **`shopper_status`** generado por el agente (campo JSON del conductor), no plantillas con especies.
- Fases genéricas en inglés si el agente no devuelve resumen.

---

## 4. OpenCode — un LLM por agente

| Agente | Rol | Modelo (PoC) |
|--------|-----|----------------|
| zooplus-conductor | Routing rápido | `opencode/mimo-v2.5-free` |
| zooplus-social-agent | Social multilingüe | `opencode/mimo-v2.5-free` |
| zooplus-intent-agent | Intent fallback | `opencode-go/deepseek-v4-flash` |
| zooplus-topic-guard | Calidad / scope | `opencode-go/minimax-m2.5` |
| zooplus-logic-worker | Ranking | `opencode-go/qwen3.6-plus` |
| zooplus-synthesis | Respuesta catálogo | `opencode/deepseek-v4-flash-free` |

- Config oficial en `.opencode/config-cli/opencode.json` + frontmatter en `*.md`.
- UI: badge **LLM real** desde `ChatResponse.meta`; panel Agent LLMs; override debug opcional.

---

## 5. Rendimiento y caché

- **TTL cache** in-process: intent, chat, retrieval (`ZOOPLUS_CACHE=1`).
- **Redis opcional** (`ZOOPLUS_CACHE_BACKEND=redis`, `ZOOPLUS_REDIS_URL`): espejo de caches + lexicón pre-indexado.
- **Lexicón en ingest:** `artifacts/index/routing_lexicon.json` (marcas, tokens, pet_types desde JSON).
- Precio EUR: parser ampliado (`entre X y Y`, español).
- Gates F2 más rápidos; pruebas agentic/social en F3.

---

## 6. Correcciones destacadas

1. Consultas ES de catálogo (*comida gatos 40–60€*) ya no caen en decline por keywords ingleses.
2. Error 422 `site_id: 0` al enviar antes de cargar la lista de tiendas.
3. Stream alineado con orchestrator (intent acotado, prefetch hits, `preferred_model`).

---

## 7. Comandos útiles

```powershell
.\scripts\run_dev.ps1                    # http://127.0.0.1:8090/ui/
.\scripts\smoke_minimal.ps1
py -3 -m cli ingest                      # Chroma + routing_lexicon.json
py -3 scripts/patch_interview_pptx_agentic_ux.py   # actualizar deck pro
```

---

## 8. PPT pro — diapositivas actualizadas (mismo deck 13 slides)

| Slide | Título | Cambio |
|-------|--------|--------|
| 6 | RAG end-to-end | Stream con **status** + lexicón en ingest |
| 7 | Agentic architecture | Conductor-first, lexicón, caché, latencia |
| 8 | Agents | Per-agent LLMs + `shopper_status` |
| 9 | Guardrails + demo | Stream UX, multilingüe, demos rápidas |

Speaker notes: [`PRESENTATION_15MIN.md`](PRESENTATION_15MIN.md)

---

## 9. Commits principales (2086daf → HEAD)

- Conductor-first routing, fallback, latencia intent
- Per-agent OpenCode models, model selector UI
- Backend-driven status stream → burbuja transitoria única
- Spanish catalog fix → agentic lexicon + `shopper_status`
- Redis optional + catalog lexicon pre-index
- Fix `site_id` 0 race en UI
