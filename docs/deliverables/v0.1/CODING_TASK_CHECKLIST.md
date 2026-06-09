# Coding Task — checklist (1:1 with the .docx)

**Brief:** [`../../instructions/Coding Task.docx`](../../instructions/Coding%20Task.docx)  
**Speaker script:** [`PRESENTATION_15MIN.md`](PRESENTATION_15MIN.md)  
**PPT (pro):** [`zooplus-assistant-interview-15min-pro.pptx`](zooplus-assistant-interview-15min-pro.pptx)

Check `[x]` when you have rehearsed each row.

---

## Functional requirements (document §1–5)

| ID | Requirement (brief text) | Demo / test | Done |
|----|--------------------------|-------------|------|
| **FR1** | Async FastAPI + `POST /chat` `{ site_id, query }` | `/docs`, curl, UI | [ ] |
| **FR2** | Response `{ answer, retrieved_products }` | Network tab; schema tests | [ ] |
| **FR3** | RAG from dataset JSON only | ingest + grounding test; explain Chroma | [ ] |
| **FR4** | Pet guardrails; off-topic decline | weather / humans | [ ] |
| **FR5** | Production-oriented design | tree `cli/`, `src/`, Docker, tests | [ ] |

### Mandatory brief query (FR1+FR2+FR3)

```json
{
  "site_id": 3,
  "query": "What's the best dry food for a puppy with a sensitive stomach?"
}
```

Live demo in UI or curl — [ ] rehearsed

---

## Submission — README (document)

| ID | README section required | Where | Done |
|----|-------------------------|-------|------|
| **R1** | High-Level Design + diagram | README (mermaid) | [ ] |
| **R2** | Setup and Execution | README + RUNBOOK + `run_dev.ps1` | [ ] |
| **R3** | Decisions and Trade-offs | README + `02-rag-architecture.md` | [ ] |
| **R4** | Future Roadmap (3–5 steps) | README § Roadmap + PPT slides 11–13 | [ ] |

---

## Evaluation criteria (document)

| ID | Criterion | How you show it | Done |
|----|-----------|-----------------|------|
| **E1** | Engineering rigor | `run_release_verify.ps1`, acceptance tests | [ ] |
| **E2** | Agentic flows + RAG | PPT slides 5–6, orchestrator | [ ] |
| **E3** | Data awareness | 300 rows, 3 sites, DOGS/CATS, site isolation demo | [ ] |
| **E4** | Trade-off transparency | README trade-offs + PPT | [ ] |

---

## Demo script (5–7 min) — order FR4 → FR3 → FR1

| Step | Action | Covers |
|------|--------|--------|
| 1 | `hello` site 3 | FR2 social |
| 2 | `options for cats` site 3 | FR3 + FR2 |
| 3 | Same query site **15** | FR1 site_id |
| 4 | `products for humans` | FR4 |
| 5 | **Puppy sensitive stomach** query site 3 | Exact .docx text |

---

## PoC policies (acceptance / constraints)

| ID | Rule | Done |
|----|------|------|
| **P1** | Max 4 products | [ ] |
| **P2** | Decline → answer, empty list | [ ] |
| **P3** | 300 variants ingested | [ ] |

---

## Automated (before the interview)

```powershell
.\scripts\run_release_verify.ps1
py -3 -m pytest tests/acceptance -m acceptance -q
```

- [ ] Green within the last 24 h

---

## Interview materials

- [ ] Pro PPTX opened and rehearsed ([`PRESENTATION_15MIN.md`](PRESENTATION_15MIN.md))
- [ ] Local server `:8090` tested
