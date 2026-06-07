# What's new — v2.0 → v2.1 (interview line)

**Tagged on releases:** `v2.0` — invisible conductor + paced stream.  
**v2.1 (current working tree):** conductor playbook + smart social/catalog ack.

---

## Headline

> “v2.0 gave us the invisible conductor. v2.1 makes it **context-aware**: greetings stay social, catalog queries get a fast protocol ack, and an internal Markdown playbook learns forbidden repeats without the shopper ever knowing.”

---

## Changes (v2.1)

| Area | Before (v2.0) | Now (v2.1) |
|------|----------------|------------|
| Instant ack | Catalog template on every turn | **Lane probe** — social vs catalog |
| `hola que tal` | Wrong catalog chunk + repeat greeting | **One** social bubble |
| Phrase policy | Hardcoded in Python | **`conductor_playbook.md`** + auto-learn |
| Language | Mostly ES/EN heuristic | **ES · EN · DE · FR** via query + shop |
| Final answer | Sometimes repeated scope/hello | Dedupe vs live chunks + synthesis hint |

**Key files:** `src/agents/conductor_playbook.md`, `artifacts/memory/conductor_playbook.md`, `src/agents/stream_voice_registry.py`, `src/lanes/stream.py`

---

## Demo script (slide 9)

1. **A:** `hola que tal` → single social reply (Spain shop 15)
2. **B:** `hamsters tortugas perros hasta 50€` → scoped ack, progress, products
3. **C:** `hello how are you` or `bonjour` → same language reply

---

## Regenerate deck

```bash
py -3 scripts/patch_interview_pptx_v20_conductor.py
```
