# Quickstart — run locally in 10 minutes

**Pick one path.** Both end at **http://127.0.0.1:8090/ui/** (default dev port).

| Path | OpenCode | Best for |
|------|----------|----------|
| **A — Wizard (recommended)** | Your choice | First install on Windows |
| **B — Template only** | Not needed | Reviewers / CI / fastest smoke |
| **C — OpenCode agentic** | Required | Interview demo with free LLMs |

---

## Path A — Setup wizard (Windows)

```powershell
git clone git@github.com:peluzzza/PoCAssistantZooplus.git
cd PoCAssistantZooplus
git checkout releases
.\scripts\setup_wizard.ps1
```

The wizard will:

1. Check **Python 3.11**
2. Create `.venv` and `pip install -e ".[rag,dev]"`
3. Let you choose **template** (no login) or **OpenCode** (free models)
4. Run `cli ingest` (Chroma index)
5. Optionally log in to OpenCode (`opencode auth login` → gitignored `.opencode/data/`)
6. Run a quick smoke test
7. Print the URL to open

Then start anytime:

```powershell
.\scripts\run_dev.ps1
# http://127.0.0.1:8090/ui/   Swagger: http://127.0.0.1:8090/docs
```

---

## Path B — Template only (no OpenCode)

```powershell
git checkout releases
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[rag,dev]"
copy .env.example .env
```

Edit `.env` — **minimum for template mode:**

```env
ZOOPLUS_INTENT_MODE=oracle
ZOOPLUS_SYNTHESIS_MODE=template
ZOOPLUS_AGENT_CASCADE=0
ZOOPLUS_DEV_PORT=8090
```

```powershell
py -3.11 -m cli ingest
.\scripts\smoke_minimal.ps1
.\scripts\run_dev.ps1
```

Answers use **template synthesis** (deterministic, no API keys). Good for FR1–FR5 demo and acceptance tests.

---

## Path C — OpenCode free LLMs (agentic demo)

**Prerequisites:** [OpenCode CLI](https://opencode.ai/docs/cli/) installed (`opencode --version`).

```powershell
git checkout releases
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[rag,dev]"
copy .env.example .env
```

**Login (once per machine)** — credentials stay **gitignored**:

```powershell
$env:OPENCODE_DATA_DIR = "$PWD\.opencode\data"
$env:OPENCODE_CONFIG_DIR = "$PWD\.opencode\config-cli"
New-Item -ItemType Directory -Force -Path .opencode\data | Out-Null
opencode auth login
```

Or copy an existing global login:

```powershell
.\scripts\setup_opencode_local.ps1
```

**Free model** (already in `.env.example`):

```env
ZOOPLUS_OPENCODE_MODEL=opencode/deepseek-v4-flash-free
```

List models: `opencode models`

```powershell
py -3.11 -m cli ingest
.\scripts\run_dev.ps1
```

If OpenCode is missing or times out, the API **falls back to template** automatically.

---

## Verify installation

| Check | Command | Expected |
|-------|---------|----------|
| Fast smoke (~2 min) | `.\scripts\smoke_minimal.ps1` | `OK - minimal functional` |
| Full quality gates | `py -3.11 scripts/run_quality_gates.py` | All gates passed |
| Release line | `.\scripts\run_release_verify.ps1` | `RELEASE VERIFY: PASSED` |
| Health | Browser `http://127.0.0.1:8090/health` | `{"status":"ok"}` |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `py -3` is 3.13 | Use `py -3.11` (see [`DEPENDENCIES.md`](DEPENDENCIES.md)) |
| Port 8090 busy | `.\scripts\stop_dev.ps1 -Port 8090` or `$env:ZOOPLUS_DEV_PORT=8080` |
| `/ready` not ready | `py -3.11 -m cli ingest` |
| OpenCode hang | Use `.opencode/config-cli` (set in `.env.example`); increase `ZOOPLUS_OPENCODE_TIMEOUT` |
| Confusing `.env` | Delete `.env`, re-run `.\scripts\setup_wizard.ps1` |

---

## Developer workflow (feature → release)

See [`GIT_WORKFLOW.md`](GIT_WORKFLOW.md) — branch from `releases`, pass smoke → quality → `run_release_verify`, then merge.

---

## Next docs

- Operations: [`RUNBOOK.md`](RUNBOOK.md)
- Chat UI: [`CHAT_UI.md`](CHAT_UI.md)
- Interview pack: [`deliverables/v0.1/README.md`](deliverables/v0.1/README.md)
