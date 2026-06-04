# Agentic social behavior (instructions-aligned)

Source of truth: `docs/instructions/Coding Task.docx`, `product_catalog_dataset.json`, `ACCEPTANCE.md`.

## Architecture (no keyword routing in production)

| Layer | Role |
|-------|------|
| **Intent agent** (`src/agents/intent_agent.py`) | OpenCode JSON classifier: `conversational` \| `catalog_search` \| `decline_off_topic` |
| **Social agent** (`src/agents/social_agent.py`) | Warm replies for greetings, identity, help — no RAG |
| **Process lane** | Catalog RAG + synthesis only when intent = `catalog_search` |

Default-deny firewall is enforced by the **LLM intent agent**, not regex lists.

## Modes (`ZOOPLUS_INTENT_MODE`)

| Value | Use |
|-------|-----|
| `agentic` | **Production / manual UI** — requires OpenCode auth (`scripts/setup_opencode_local.ps1`) |
| `oracle` | CI + local fast tests — uses `tests/fixtures/intent_oracle.json` (built from 114+ use cases) |

## Sociable UX principles (CUX / research)

- Transparent AI shop assistant; introduce yourself when asked.
- Combined utterances work (`hello, who are you` → identity, **no product cards**).
- Off-topic (traffic, weather, humans) → polite redirect, **empty** `retrieved_products`.
- Catalog answers: natural prose, not rigid “Based on what you asked…” dumps.

## Tests

```bash
python scripts/build_use_case_matrix.py   # 114 cases + intent oracle
pytest -m agentic -q
pytest -m social -q
```

Markers: `agentic`, `social`, `security`, `acceptance`.
