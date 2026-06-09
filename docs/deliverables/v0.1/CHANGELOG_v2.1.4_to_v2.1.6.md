# What's new — v2.1.4 → v2.1.6 (releases interview line)

**Current working tree on `releases`:** v2.1.6 + customer-voice polish.

---

## Headline

> v2.1.6 adds flexible picks, chunked product cards, and a fast social phrase index. Follow-up fixes keep first-turn greetings natural, route shopping queries to catalog (even with “can you help”), and keep replies professional — no system-manual tone.

---

## Changes

| Area | v2.1.4–5 | v2.1.6+ |
|------|----------|---------|
| Recommendation count | Fixed cap | **Default 4**, shopper can ask up to **20** (`resolve_recommendation_count`) |
| Stream UX | Progress chunks | **`product_batch`** NDJSON — UI reveals cards in chunks of 4 |
| Social routing | Playbook help detect | **`social_phrases.yaml`** index (~90 ES/EN/DE/FR) + auto-learn |
| Species | Fixed lists | Dynamic inference (iguana, capybara, …) |
| Greeting | Partial intro strip bug | First-turn **hello** preserved; no orphan “for this/our shop” |
| Help vs catalog | “can you help” → social | **Shopping intent wins** — light dog food + help → catalog |
| Shopper voice | Meta FAQ replies | **`CUSTOMER_VOICE`** — polite associate, no tech/strategy exposition |
| Interview deck | Bullets only | **FR code evidence panels** slides 3–4, 6, 9–10; **English** demo phrases |
| Internal prep | In release pack | **`QA_FOR_POC.md`** and **`PRESENTATION_15MIN.md`** — **`main` only** |

---

## Demo script (slide 9 — matches PPT)

1. **A:** `can you help me` → social help, **no** catalog progress chunk
2. **B:** `and what about iguanas` → scope reply, no duplicate greeting
3. **C:** `give me 10 dog food options` → up to ten cards in **product_batch** chunks

**Also try:** `hello` (UK shop 3) — full natural greeting; `looking for light food for my dogs… can you help me out?` → catalog, not help FAQ.

---

## Regenerate deck

```bash
py -3 scripts/patch_interview_pptx_fr1_async.py
py -3 scripts/patch_interview_pptx_v20_conductor.py
```

(`v20_conductor` includes slides 5–9, FR2–FR5 code panels, release-progress slide 14.)
