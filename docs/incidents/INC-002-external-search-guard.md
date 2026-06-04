# INC-002 — External internet search not declined

**Severity:** P1  
**Found:** 2026-06-04 (UI + guardrail test design)  
**Status:** FIXED

## Symptom

Queries like “can you search in internet about pet products” entered the RAG path instead of a clear **catalog-only** decline, causing slow failures and user confusion.

## Root cause

Topic guard had no pattern for external web / internet search intents (OWASP LLM — excessive agency / off-domain tools).

## Fix

Added `off_topic_external_web` patterns and dedicated decline copy in `src/guardian/engine.py`.

## Verification

`guardrail_queries.json` → `decline_internet_search`, `decline_web_search` pass with empty `retrieved_products`.
