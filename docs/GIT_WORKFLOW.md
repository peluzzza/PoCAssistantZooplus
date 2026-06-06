# Git workflow — feature → dev → main → releases

**Branches**

| Branch | Purpose |
|--------|---------|
| `feature/*` | Your change (docs, fix, demo) |
| `dev` | Integration branch — features merge here first |
| `main` | Stabilised line after quality gates |
| `releases` | **Interview / take-home line** — slim, verified |

For local setup and demo, use **`releases`** (`git checkout releases`).

---

## Mandatory promotion chain

**Never merge `feature/*` directly into `main` or `releases`.**

```text
releases ◄── main ◄── dev ◄── feature/my-change
```

| Step | Action | Required filters |
|------|--------|------------------|
| 1 | Branch from `dev` (or `releases` if hotfix on interview line) | — |
| 2 | Develop + commit on `feature/*` | — |
| 3 | Merge `feature/*` → `dev` | **F1** `smoke_minimal.ps1` |
| 4 | Merge `dev` → `main` | **F2** `run_quality_gates.py` |
| 5 | Merge `main` → `releases` | **F3** `run_release_verify.ps1` |
| 6 | Push `dev`, `main`, `releases` | All filters green |

---

## Day-to-day (contributor)

### 1. Start from `dev`

```powershell
git checkout dev
git pull origin dev
git checkout -b feature/my-change
```

### 2. Develop

```powershell
.\scripts\setup_wizard.ps1          # first time only
.\scripts\run_dev.ps1               # http://127.0.0.1:8090/ui/
```

### 3. Filters (in order — do not skip)

| Step | Script | Before merge to |
|------|--------|-----------------|
| **F1** Fast smoke | `.\scripts\smoke_minimal.ps1` (~4 min) | `dev` |
| **F2** Quality gates | `py -3 scripts/run_quality_gates.py` (~8–12 min; oracle/template, no social matrix) | `main` |
| **F3** Release verify | `.\scripts\run_release_verify.ps1` (F2 + OpenCode agentic/social, ~15–25 min) | `releases` |

```powershell
.\scripts\smoke_minimal.ps1
py -3 scripts/run_quality_gates.py
.\scripts\run_release_verify.ps1
```

### 4. Promote (example)

```powershell
# feature → dev (after F1)
git checkout dev
git merge --no-ff feature/my-change -m "merge feature/my-change into dev"
git push origin dev

# dev → main (after F2)
git checkout main
git pull origin main
git merge --no-ff dev -m "merge dev into main"
git push origin main

# main → releases (after F3)
git checkout releases
git pull origin releases
git merge --no-ff main -m "merge main into releases"
git push origin releases
```

Optional tag after interview milestones: `git tag -a v0.1.x -m "..."` · `git push origin v0.1.x`

---

## Reviewer / interviewer (clone only)

```powershell
git clone git@github.com:peluzzza/PoCAssistantZooplus.git
cd PoCAssistantZooplus
git checkout releases
.\scripts\setup_wizard.ps1
```

No feature branch needed — run wizard, open UI, done.
