# Git workflow

**Remote:** [https://github.com/peluzzza/PoCAssistantZooplus.git](https://github.com/peluzzza/PoCAssistantZooplus.git)

## Current local state (2026-06-03)

| Branch | Commit | Notes |
|--------|--------|-------|
| `main` | `a6f9d26` | P0 bootstrap only |
| `dev` | `d514225` | P0 + T1 EDA merged |
| `feature/T1-eda` | `d514225` | Merged; can delete after push |

**Push:** synced 2026-06-03 — `origin/main`, `origin/dev`, `origin/feature/T1-eda`.

## Branches

| Branch | Purpose |
|--------|---------|
| `main` | Stable, demo-ready snapshots only |
| `dev` | Integration branch — merge all `feature/*` here first |
| `feature/<name>` | Short-lived work (T1, T2, …) |

## Flow

```mermaid
gitGraph
  commit id: "bootstrap"
  branch dev
  checkout dev
  branch feature/T1-eda
  commit id: "T1 EDA"
  checkout dev
  merge feature/T1-eda
  checkout main
  merge dev tag: "release when ready"
```

1. Branch `feature/<step>` from `dev`.
2. Implement + update `docs/trace/`.
3. Merge `feature/*` → `dev` (PR or local merge).
4. When a milestone is ready to show: merge `dev` → `main` (or cherry-pick).

## Commands (from repo root)

```bash
git fetch origin
git checkout dev
git pull origin dev
git checkout -b feature/T1-eda
# ... work ...
git push -u origin feature/T1-eda
git checkout dev && git merge feature/T1-eda
git push origin dev
```
