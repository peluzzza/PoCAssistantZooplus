# Demo completa — qué está listo y qué falta

**Objetivo:** probar **todo** el PoC (RAG, `/chat`, stream, MCP, golden, métricas, Docker).

---

## Estado del plan (fases)

| Ámbito | Estado |
|--------|--------|
| P0–P6 (brief take-home) | **DONE** en `main` |
| Releases v1.0.0 → v2.1.0 | **DONE** |
| Fase opcional documentación agentes | `docs/03-agent-flows-and-prompts.md` — actualizar evidencias |

**No quedan fases obligatorias del plan de releases.** Lo que sigue es **demo en tu máquina** u **opcional cloud**.

---

## Opción A — Local (recomendada, ~10 min)

### 1. Requisitos

- Python **3.11** (o Docker)
- `pip install -e ".[rag,dev]"`

### 2. API en marcha (elige una)

**Docker (más parecido a prod):**

```bash
cd "d:\temp\review_clones\PoC chatbot zooplus"
docker compose up --build -d
```

**Venv:**

```bash
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -e ".[rag,dev]"
python -m cli ingest
uvicorn src.api.app:app --host 0.0.0.0 --port 8080
```

### 3. Demo automática (todo en un script)

Con el API **ya levantado** en el puerto 8080:

```bash
python scripts/demo_all.py --with-gates
```

Incluye: gates (opcional), ingest, eda, evaluate, G1 load test, deploy_smoke, muestras HTTP (in-scope + off-topic).

### 4. Pruebas manuales rápidas

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready
curl -X POST http://127.0.0.1:8080/chat -H "Content-Type: application/json" \
  -d "{\"site_id\":3,\"query\":\"best dry food for puppy\"}"
curl -X POST http://127.0.0.1:8080/mcp/tools/topic_check \
  -H "Content-Type: application/json" -d "{\"query\":\"dog food\"}"
```

Stream: `POST /chat/stream` (NDJSON) — ver [`RUNBOOK.md`](RUNBOOK.md).

---

## Opción B — Google Cloud (rápido: Cloud Run, no Vertex AI completo)

| Enfoque | Esfuerzo | Qué obtienes |
|---------|----------|--------------|
| **Cloud Run + imagen Docker actual** | Bajo (~30 min) | Mismo PoC en URL pública, Chroma en disco del contenedor |
| **Vertex AI Search / Matching Engine** | Alto | Reemplazar Chroma + embeddings; no está cableado en el repo |
| **Vertex Gemini para síntesis** | Medio | Sustituir plantillas en `process.py`; requiere API key + código nuevo |

Guía mínima Cloud Run: [`deploy/CLOUD_RUN.md`](deploy/CLOUD_RUN.md).

**Qué falta para “Vertex RAG nativo”:**

1. Proveedor de embeddings en Vertex (p. ej. `text-embedding-004`)
2. Índice vectorial gestionado (Matching Engine o AlloyDB pgvector)
3. Sustituir `src/rag/store/chroma_store.py` por cliente GCP
4. Secretos: `GOOGLE_APPLICATION_CREDENTIALS`, proyecto, región

El PoC **no incluye** ese cableado; está diseñado para **demo local/Docker sin claves**.

---

## Qué NO necesitas para probar el brief

| Item | Necesario para demo actual |
|------|----------------------------|
| Anthropic / OpenAI API | No (síntesis por plantilla) |
| Vertex AI | No |
| SonarCloud token | No (opcional CI) |

---

## Checklist “he probado todo”

- [ ] `python scripts/run_quality_gates.py` → 41 tests OK
- [ ] `docker compose up` + `python scripts/deploy_smoke.py`
- [ ] `python scripts/demo_all.py` → ALL PASSED
- [ ] `python -m cli evaluate` → 4/4 golden
- [ ] Off-topic devuelve decline sin productos
- [ ] `site_id` distinto no mezcla tiendas (tests integration)

---

## Siguiente paso opcional (fuera del plan)

- v3.0: Vertex/Gemini opcional detrás de feature flag
- SonarCloud con `SONAR_TOKEN`
