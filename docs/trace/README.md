# Implementation trace (PoC journal)

Mirrors the **completion style** of `project_temp/plans/*-phase-N-complete.md`, adapted for a take-home PoC: small steps, brief alignment, evidence per step.

---

## Status dashboard

See **[`PROGRESS.md`](PROGRESS.md)** (updated every session).

---

## Trace steps (T0–T6)

| Step | File | Phase | Status |
|------|------|-------|--------|
| T0 | [`T0-repo-bootstrap.md`](T0-repo-bootstrap.md) | P0 | **DONE** |
| T1 | [`T1-eda-run.md`](T1-eda-run.md) | P1 | PENDING |
| T2 | [`T2-rag-index.md`](T2-rag-index.md) | P2 | PENDING |
| T3 | [`T3-opencode-mcp-agents.md`](T3-opencode-mcp-agents.md) | P3 | PENDING |
| T4 | [`T4-dual-lane-acp.md`](T4-dual-lane-acp.md) | P4 | PENDING |
| T5 | [`T5-api-contract.md`](T5-api-contract.md) | P5 | PENDING |
| T6 | [`T6-readme-submission.md`](T6-readme-submission.md) | P6 | PENDING |

---

## Templates

- New step: copy [`_TEMPLATE.md`](_TEMPLATE.md)
- Phase complete: copy [`phases/_PHASE_TEMPLATE.md`](phases/_PHASE_TEMPLATE.md) → `phases/Pn-<name>-complete.md`
- Session log: copy [`sessions/_SESSION_TEMPLATE.md`](sessions/_SESSION_TEMPLATE.md)

---

## Folder layout

```
trace/
├── README.md           ← you are here
├── PROGRESS.md         ← living dashboard
├── _TEMPLATE.md
├── T0-repo-bootstrap.md … T6-readme-submission.md
├── phases/             ← *-complete.md artifacts
└── sessions/           ← Zeus / CLI session logs
```
