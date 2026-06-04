# Release v0.1.0 — `releases` branch (above `main`)

**Line:** `releases` is the top branch; **`v0.1.0` is cut from `main`** + PoC agentic merge.  
**Tag:** `v0.1.0` on branch `releases` (not on `main`).

## Verify

```powershell
.\scripts\run_release_verify.ps1
```

## Run locally

```powershell
git checkout releases
.\scripts\run_dev.ps1
# http://127.0.0.1:8090/ui/
```

## Deliverable (Coding Task)

- [`docs/deliverables/v0.1/`](deliverables/v0.1/) — checklist + **PPT base**
- `docs/instructions/` — catalog, `ACCEPTANCE.md`, `AGENT_BUNDLE.md`
- Add `Coding Task.docx` under `docs/instructions/` for full acceptance B7
