# Deliverable pack — v0.1 (Coding Task)

**Brief:** [`../../instructions/Coding Task.docx`](../../instructions/Coding%20Task.docx)

## Interview materials

| Item | Path |
|------|------|
| **Presentation (pro)** | [`zooplus-assistant-interview-15min-pro.pptx`](zooplus-assistant-interview-15min-pro.pptx) |
| Speaker script | [`PRESENTATION_15MIN.md`](PRESENTATION_15MIN.md) |
| **Changelog v0.1.2 → v0.1.3** | [`CHANGELOG_v0.1.2_to_v0.1.3.md`](CHANGELOG_v0.1.2_to_v0.1.3.md) |
| Checklist | [`CODING_TASK_CHECKLIST.md`](CODING_TASK_CHECKLIST.md) |
| Future roadmap (summary) | [`FUTURE_IMPROVEMENTS.md`](FUTURE_IMPROVEMENTS.md) |

Refresh PPT slides after code changes:

```powershell
py -3 scripts/patch_interview_pptx_agentic_ux.py
```

## Run locally (reviewer)

```powershell
git checkout releases
.\scripts\setup_wizard.ps1    # installs everything + optional OpenCode login
.\scripts\run_dev.ps1
# http://127.0.0.1:8090/ui/
```

Guide: [`../../QUICKSTART.md`](../../QUICKSTART.md)

## Verify before presenting

```powershell
.\scripts\run_release_verify.ps1
```

Extended methodology, PPT build scripts, diagram packs, and agent snapshots live on **`main`**, not on this branch.
