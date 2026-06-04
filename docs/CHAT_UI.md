# Chat UI (local demo)

## Quick start

```bash
python -m cli ingest
uvicorn src.api.app:app --reload --port 8080
```

Open **http://127.0.0.1:8080/ui/** (root `/` redirects there).

## Features

- Shop selector (`site_id` 1, 3, 15)
- Calls `POST /chat` with the same contract as the Coding Task
- Product cards from `retrieved_products`
- Badge shows synthesis mode (`template` vs `opencode`)

## OpenCode LLM (optional)

1. Install [OpenCode CLI](https://opencode.ai/docs/cli/) and log in:

   ```bash
   opencode auth login
   ```

   Credentials are stored in `~/.local/share/opencode/auth.json` by default.

2. Or use a **project-local** profile (recommended for this repo):

   ```bash
   set ZOOPLUS_OPENCODE_DATA_DIR=.opencode/data
   set OPENCODE_DATA_DIR=.opencode/data
   opencode auth login
   ```

   The `.opencode/data/` folder is **gitignored** — never commit `auth.json`.

3. Enable LLM synthesis:

   ```bash
   set ZOOPLUS_SYNTHESIS_MODE=opencode
   set ZOOPLUS_OPENCODE_MODEL=opencode-go/qwen3.6-plus
   uvicorn src.api.app:app --reload --port 8080
   ```

   Pick any model your account exposes (`opencode models`). On failure, the API **falls back** to template synthesis.

See [`.env.example`](../.env.example) for all variables.
