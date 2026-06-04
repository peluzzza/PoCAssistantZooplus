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

2. **Project-local** profile (recommended; never pushed to GitHub):

   ```powershell
   .\scripts\setup_opencode_local.ps1
   ```

   Copies your existing `~/.local/share/opencode/auth.json` into `.opencode/data/` (gitignored).
   For a fresh login instead:

   ```powershell
   $env:OPENCODE_DATA_DIR = "$PWD\.opencode\data"
   opencode auth login
   ```

   The `.opencode/data/` folder is **gitignored** — never commit `auth.json`.

3. Copy your real login (never committed):

   ```powershell
   .\scripts\setup_opencode_local.ps1
   ```

4. Enable local OpenCode in `.env`:

   ```env
   ZOOPLUS_SYNTHESIS_MODE=opencode
   ZOOPLUS_OPENCODE_MODEL=opencode-go/deepseek-v4-flash
   ZOOPLUS_OPENCODE_DATA_DIR=.opencode/data
   ```

5. Restart API: `uvicorn src.api.app:app --reload --port 8080`

**Conversation:** greetings (`Hello`), thanks, and help skip catalog search and reply politely. Product questions use RAG + OpenCode (or template fallback within ~12s).

See [`.env.example`](../.env.example) for all variables.
