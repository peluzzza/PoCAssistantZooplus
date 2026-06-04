# Mínimo funcional (smoke + UI)

## Requisito: espacio en disco

Si pytest falla con `ENOSPC`, libera espacio en `%TEMP%` y en el disco del proyecto antes de correr tests.

## Smoke rápido (~2 min, sin OpenCode)

```powershell
cd "d:\temp\review_clones\PoC chatbot zooplus"
.\scripts\smoke_minimal.ps1
```

Comprueba: unit (synthesis, conversation, variety, intent), fallback agentic, y 3 casos de matriz (social + catálogo).

## Matriz completa (173 casos, ~5–15 min)

```powershell
py -3 scripts/run_use_case_matrix.py
```

Usa `oracle` + `template` + cascade desactivado (ver `scripts/run_use_case_matrix.py`).

## UI local

```powershell
.\scripts\run_dev.ps1
```

Abre **http://127.0.0.1:8080/ui/**

### Perfil recomendado en `.env`

| Variable | Smoke / CI | UI sociable (con OpenCode) |
|----------|------------|----------------------------|
| `ZOOPLUS_INTENT_MODE` | `oracle` | `agentic` |
| `ZOOPLUS_SYNTHESIS_MODE` | `template` | `opencode` |
| `ZOOPLUS_SOCIAL_SYNTHESIS` | `agentic` (matrix mocks agents) | `agentic` |
| `ZOOPLUS_AGENT_CASCADE` | `0` | `1` |

Sin auth OpenCode, `agentic` sigue funcionando vía **topic fallback** + plantillas variadas.

## Checklist manual UI

1. `hello, what can you tell me about your services` → ayuda, sin decline.
2. `what products do you have available` → productos.
3. `show me about dogs` → productos, texto sin lista 1.2.3. duplicada.
4. `do you have product about horses?` → decline amable (perros/gatos).
5. `how is the traffic today` → decline, sin productos.
