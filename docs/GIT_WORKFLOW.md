# Git workflow

**Remote:** [https://github.com/peluzzza/PoCAssistantZooplus.git](https://github.com/peluzzza/PoCAssistantZooplus.git)

## Branch hierarchy (top → bottom)

```text
releases   ← production / tagged releases (v0.1.0, …) — ABOVE main
main       ← stable integration promoted from dev
dev        ← daily integration (feature/*, bugfix/*)
```

Promotion flow: **`dev` → `main` → `releases`** (never skip `main` unless hotfix policy says so).

| Branch | Role |
|--------|------|
| **`releases`** | Top line: tags `v0.x.y`, demo/POC entregables, Coding Task sign-off |
| **`main`** | Stable; merge from `dev` when milestone passes quality gates |
| **`dev`** | Integration branch for all short-lived work |
| `feature/*`, `bugfix/*` | Short-lived; merge into `dev` |

## Version tags (on `releases`)

| Tag | Base | Notes |
|-----|------|--------|
| **`v0.1.0`** | `main` @ merge | Agentic PoC baseline (OpenCode internal, UI, no template runtime) |
| `v1.x` (legacy) | old `main` | Historical v2.x tags remain on old commits |

## Pre-promotion quality (required)

```powershell
.\scripts\run_release_verify.ps1
```

Or: `python scripts/run_quality_gates.py` + agentic + social (see `docs/RELEASE_v0.1.md`).

## Commands

### Day-to-day (dev)

```bash
git checkout dev && git pull origin dev
git checkout -b feature/my-step
# ... work ...
git push -u origin feature/my-step
git checkout dev && git merge feature/my-step && git push origin dev
```

### Promote to main

```bash
.\scripts\run_release_verify.ps1
git checkout main && git pull origin main
git merge dev -m "release: integrate dev into main"
git push origin main
```

### Promote to releases (tag)

```bash
git checkout releases && git pull origin releases
git merge main -m "release: promote main to releases for v0.x.y"
# bump version in pyproject.toml if needed
git tag -a v0.1.0 -m "v0.1.0 — title"
git push origin releases && git push origin v0.1.0
```

`releases` is created from `main`:

```bash
git checkout main
git checkout -B releases
git merge <feature-or-dev-commit> -m "release(v0.1.0): ..."
git tag -a v0.1.0 -m "v0.1.0"
git push -u origin releases --force-with-lease
git push origin v0.1.0
```
