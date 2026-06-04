# Release v0.1.0 — agentic PoC baseline

**Branch:** `releases` (promoted from `dev`)  
**Tag:** `v0.1.0`  
**Compliance:** `docs/instructions/AGENT_BUNDLE.md`, `product_catalog_dataset.json`, Coding Task (docx when present in `docs/instructions/`)

## Scope

- 3 shops: `site_id` 1, 3, 15 — 100 variants each (50 DOGS + 50 CATS)
- Shopper-facing: **zooplus Assistant** only; OpenCode agents internal
- `POST /chat` → `{ answer, retrieved_products }` (max 4 products)

## Verify before tag

```powershell
.\scripts\run_release_verify.ps1
```

## Git promote (from clean `dev`)

```powershell
git checkout dev
git merge bugfix/agentic-from-v2.2
git checkout -b releases
git tag -a v0.1.0 -m "v0.1.0 — agentic baseline, OpenCode, UI, no template runtime"
git push -u origin releases
git push origin v0.1.0
```

## Next (v0.2+)

- Deliverables folder under `docs/deliverables/v0.1/`
- Presentation (PPT): architecture, demo screenshots, Coding Task checklist, catalog stats
