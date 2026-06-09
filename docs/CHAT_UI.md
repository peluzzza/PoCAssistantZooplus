# Chat UI (local demo)

## Quick start

```powershell
.\scripts\setup_wizard.ps1   # first time
.\scripts\run_dev.ps1
```

Open **http://127.0.0.1:8090/ui/** (default dev port; root `/` redirects there).

See [`QUICKSTART.md`](QUICKSTART.md) for template vs OpenCode profiles.

## Features

- Shop selector (`site_id` 1, 3, 15)
- Calls **`POST /chat/stream`** (NDJSON) for live progress and **`product_batch`** card chunks; Swagger uses `POST /chat`
- Product cards from `retrieved_products` (default 4 picks; up to 20 if the shopper asks)
- Badge shows active agent/model from response `meta`

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
   ZOOPLUS_OPENCODE_MODEL=opencode/deepseek-v4-flash-free
   ZOOPLUS_OPENCODE_DATA_DIR=.opencode/data
   ```

5. Restart API: `.\scripts\run_dev.ps1` (port **8090**)

**Conversation:** greetings and pure help (`can you help me`) stay social — polite, concise, no system-manual tone. **Shopping queries** (even with “can you help me out?”) use catalog RAG + OpenCode (or template fallback). Stream shows progress chunks; larger result sets arrive via `product_batch`.

See [`.env.example`](../.env.example) for all variables.
