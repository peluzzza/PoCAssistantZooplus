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

## Catalog (Coding Task)

- `docs/instructions/product_catalog_dataset.json` — 300 rows, `site_id` 1|3|15, **DOGS/CATS only**
- `docs/instructions/AGENT_BUNDLE.md` — agent policy
- `Coding Task.docx` — place under `docs/instructions/` when available
