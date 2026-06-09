# Release line — `releases` branch

**Baseline tag:** `v0.1.0` · **Current interview line:** v2.1.6 (see [`deliverables/v0.1/CHANGELOG_v2.1.4_to_v2.1.6.md`](deliverables/v0.1/CHANGELOG_v2.1.4_to_v2.1.6.md)).

## Verify

```powershell
.\scripts\run_release_verify.ps1
```

## Run locally

```powershell
git checkout releases
.\scripts\setup_wizard.ps1    # first time — installs deps + optional OpenCode login
.\scripts\run_dev.ps1
# http://127.0.0.1:8090/ui/
```

Full guide: [`QUICKSTART.md`](QUICKSTART.md)

## Deliverable (Coding Task)

| Item | Path |
|------|------|
| Brief + catalog | [`docs/instructions/`](instructions/) |
| Acceptance criteria | [`docs/instructions/ACCEPTANCE.md`](instructions/ACCEPTANCE.md) |
| Checklist | [`docs/deliverables/v0.1/CODING_TASK_CHECKLIST.md`](deliverables/v0.1/CODING_TASK_CHECKLIST.md) |
| **Presentation (pro)** | [`docs/deliverables/v0.1/zooplus-assistant-interview-15min-pro.pptx`](deliverables/v0.1/zooplus-assistant-interview-15min-pro.pptx) |
