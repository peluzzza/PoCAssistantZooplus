# Coding Task — checklist (1:1 con el .docx)

**Brief:** [`../../instructions/Coding Task.docx`](../../instructions/Coding%20Task.docx)  
**Guion:** [`PRESENTATION_15MIN.md`](PRESENTATION_15MIN.md)  
**PPT (pro):** [`zooplus-assistant-interview-15min-pro.pptx`](zooplus-assistant-interview-15min-pro.pptx)

Marca `[x]` al ensayar cada fila.

---

## Functional requirements (documento §1–5)

| ID | Requisito (texto del brief) | Demo / prueba | Listo |
|----|----------------------------|---------------|-------|
| **FR1** | Async FastAPI + `POST /chat` `{ site_id, query }` | `/docs`, curl, UI | [ ] |
| **FR2** | Respuesta `{ answer, retrieved_products }` | Network tab; schema tests | [ ] |
| **FR3** | RAG solo del dataset JSON | ingest + grounding test; explicar Chroma | [ ] |
| **FR4** | Guardrails mascotas; off-topic decline | weather / humans | [ ] |
| **FR5** | Diseño orientado a producción | tree `cli/`, `src/`, Docker, tests | [ ] |

### Query obligatoria del brief (FR1+FR2+FR3)

```json
{
  "site_id": 3,
  "query": "What's the best dry food for a puppy with a sensitive stomach?"
}
```

Demo en vivo en UI o curl — [ ] ensayada

---

## Submission — README (documento)

| ID | Sección README pedida | Dónde | Listo |
|----|----------------------|-------|-------|
| **R1** | High-Level Design + diagrama | README (mermaid) | [ ] |
| **R2** | Setup and Execution | README + RUNBOOK + `run_dev.ps1` | [ ] |
| **R3** | Decisions and Trade-offs | README + `02-rag-architecture.md` | [ ] |
| **R4** | Future Roadmap (3–5 pasos) | README § Roadmap + PPT slides 9–11 | [ ] |

---

## Evaluation criteria (documento)

| ID | Criterio | Cómo lo muestras | Listo |
|----|----------|------------------|-------|
| **E1** | Engineering rigor | `run_release_verify.ps1`, acceptance tests | [ ] |
| **E2** | Agentic flows + RAG | PPT slides 5–6, orchestrator | [ ] |
| **E3** | Data awareness | 300 rows, 3 sites, DOGS/CATS, site isolation demo | [ ] |
| **E4** | Trade-off transparency | README trade-offs + PPT | [ ] |

---

## Demo script (5–7 min) — orden FR4 → FR3 → FR1

| Paso | Acción | Cubre |
|------|--------|-------|
| 1 | `hello` site 3 | FR2 social |
| 2 | `options for cats` site 3 | FR3 + FR2 |
| 3 | Misma query site **15** | FR1 site_id |
| 4 | `products for humans` | FR4 |
| 5 | Query **puppy sensitive stomach** site 3 | Texto exacto del .docx |

---

## Políticas PoC (acceptance / constraints)

| ID | Regla | Listo |
|----|-------|-------|
| **P1** | Máx. 4 productos | [ ] |
| **P2** | Decline → answer, lista vacía | [ ] |
| **P3** | 300 variantes ingestadas | [ ] |

---

## Automatizado (antes de la entrevista)

```powershell
.\scripts\run_release_verify.ps1
py -3 -m pytest tests/acceptance -m acceptance -q
```

- [ ] Verde en las últimas 24 h

---

## Material de entrevista

- [ ] PPTX pro abierto y ensayado ([`PRESENTATION_15MIN.md`](PRESENTATION_15MIN.md))
- [ ] Servidor local `:8090` probado
