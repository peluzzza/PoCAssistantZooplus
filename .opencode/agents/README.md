# OpenCode agents — zooplus PoC

**Source of truth:** `docs/instructions/AGENT_BUNDLE.md`

All live agents use **`opencode-go/*`** only. Model order follows the **official OpenCode Go speed/cost ladder** ([opencode.ai/docs/go](https://opencode.ai/docs/go/) — requests per 5h). Fastest agents get the highest rank.

## OpenCode Go — official speed rank (14 models)

| Rank | Model | req / 5h (official) | $/1M in/out |
|------|-------|---------------------|-------------|
| 1 | `deepseek-v4-flash` | **31,650** | $0.14 / $0.28 |
| 2 | `mimo-v2.5` | **30,100** | $0.14 / $0.28 |
| 3 | `minimax-m2.5` | 6,300 | $0.30 / $1.20 |
| 4 | `qwen3.7-plus` | 4,300 | $0.40 / $1.60 |
| 5 | `deepseek-v4-pro` | 3,450 | $1.74 / $3.48 |
| 6 | `minimax-m2.7` | 3,400 | $0.30 / $1.20 |
| 7 | `qwen3.6-plus` | 3,300 | $0.50 / $3.00 |
| 8 | `mimo-v2.5-pro` | 3,250 | $1.74 / $3.48 |
| 9 | `kimi-k2.5` | 1,850 | $0.60 / $3.00 |
| 10 | `minimax-m3` | 1,400 | $0.60 / $2.40 |
| 11 | `glm-5` / `kimi-k2.6` | 1,150 | — |
| 12 | `qwen3.7-max` | 950 | $2.50 / $7.50 |
| 13 | `glm-5.1` | 880 | $1.40 / $4.40 |

External latency (Singapore, independent benchmark): DeepSeek V4 Flash ~**120 ms TTFT**, **240 tok/s** — fastest measured tier.

## Agent assignment (rank → latency-sensitive role)

| Agent | Go rank | Model |
|-------|---------|-------|
| `zooplus-social-agent` | #1 | `opencode-go/deepseek-v4-flash` |
| `zooplus-intent-agent` | #2 | `opencode-go/mimo-v2.5` |
| `zooplus-conductor` | #3 | `opencode-go/minimax-m2.5` |
| `zooplus-topic-guard` | #4 | `opencode-go/qwen3.7-plus` |
| `zooplus-rag-worker` | #5 | `opencode-go/deepseek-v4-pro` |
| `zooplus-logic-worker` | #6 | `opencode-go/minimax-m2.7` |
| `zooplus-synthesis` | #7 | `opencode-go/qwen3.6-plus` |

Runtime: `.opencode/config-cli/opencode.json` (`ZOOPLUS_OPENCODE_CONFIG_DIR`).

Override: `ZOOPLUS_AGENT_MODEL_ZOOPLUS_SOCIAL_AGENT=opencode-go/deepseek-v4-flash`
