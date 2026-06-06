# Git workflow — feature → release

**Branches**

| Branch | Purpose |
|--------|---------|
| `feature/*` | Your change (docs, fix, demo) |
| `releases` | **Interview / take-home line** — slim, verified |
| `main` | Full dev history, matrix tooling, generators |

For local setup and demo, use **`releases`** (`git checkout releases`).

---

## Day-to-day (contributor)

```text
releases ──► feature/my-change ──► (filters) ──► releases ──► tag v0.1.x
```

### 1. Start from `releases`

```powershell
git checkout releases
git pull origin releases
git checkout -b feature/my-change
```

### 2. Develop

```powershell
.\scripts\setup_wizard.ps1          # first time only
.\scripts\run_dev.ps1               # http://127.0.0.1:8090/ui/
```

### 3. Filters (in order — do not skip)

| Step | Script | When |
|------|--------|------|
| **F1** Fast smoke | `.\scripts\smoke_minimal.ps1` | After every meaningful change |
| **F2** Quality gates | `py -3.11 scripts/run_quality_gates.py` | Before merge |
| **F3** Release verify | `.\scripts\run_release_verify.ps1` | Before merging to `releases` |

```powershell
.\scripts\smoke_minimal.ps1
py -3.11 scripts/run_quality_gates.py
.\scripts\run_release_verify.ps1
```

### 4. Merge to `releases`

```powershell
git checkout releases
git merge --no-ff feature/my-change -m "merge feature/my-change into releases"
git push origin releases
```

Optional tag after interview milestones: `git tag -a v0.1.x -m "..."` · `git push origin v0.1.x`

### 5. Sync to `main` (optional)

Heavy dev artifacts live on `main` only. Merge `releases` → `main` when you want the slim app line on main, or cherry-pick specific fixes.

---

## Reviewer / interviewer (clone only)

```powershell
git clone git@github.com:peluzzza/PoCAssistantZooplus.git
cd PoCAssistantZooplus
git checkout releases
.\scripts\setup_wizard.ps1
```

No feature branch needed — run wizard, open UI, done.
