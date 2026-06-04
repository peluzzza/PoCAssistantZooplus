# Probar en local (OpenCode + UI)

## Una vez

```powershell
cd "d:\temp\review_clones\PoC chatbot zooplus"
.\scripts\setup_opencode_local.ps1
copy .env.example .env   # si no existe
```

## Servidor + chat

```powershell
.\scripts\run_dev.ps1
```

Abre **http://127.0.0.1:8090/ui/** (puerto por defecto; en `:8080` suele quedar un uvicorn viejo en Windows).

Si necesitas 8080: cierra terminales antiguas, `.\scripts\stop_dev.ps1`, luego `$env:ZOOPLUS_DEV_PORT='8080'; .\scripts\run_dev.ps1`.

## Tests con IA real (sin mocks)

```powershell
.\scripts\run_agentic_tests.ps1
```

Requiere `opencode` en PATH y `auth.json` (global o copiado a `.opencode/data`).

**Nota:** `.env` usa `ZOOPLUS_OPENCODE_CONFIG_DIR=.opencode/config-cli` para que `opencode run` no espere el MCP en `:8080` cuando la API no está levantada.
