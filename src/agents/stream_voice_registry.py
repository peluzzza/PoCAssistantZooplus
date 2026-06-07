"""Conductor playbook — parse/update internal MD; fast voice + silent auto-learn."""

from __future__ import annotations

import logging
import os
import re
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

from src.rag.price_filter import parse_eur_price_range

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
PLAYBOOK_SEED = Path(__file__).resolve().parent / "conductor_playbook.md"
PLAYBOOK_PATH = ROOT / "artifacts" / "memory" / "conductor_playbook.md"
_SPANISH_ACCENT = re.compile(r"[áéíóúñ¿¡]", re.I)
_MAX_EUR_HINT = re.compile(r"(?:hasta|up\s+to|under|menos\s+de)\s*€?\s*(\d+)", re.I)
_SECTION = re.compile(r"^##\s+([a-z0-9_]+)\s*$", re.M)
_LEARNED_SECTIONS = frozenset(
    {
        "learned_forbidden",
        "learned_scope_markers",
        "learned_greeting_markers",
        "learned_species",
    }
)
_CATEGORY_TO_SECTION = {
    "forbidden_phrases": "learned_forbidden",
    "scope_markers": "learned_scope_markers",
    "greeting_markers": "learned_greeting_markers",
    "greeting_signals": "learned_greeting_markers",
    "non_catalog_species": "learned_species",
}


@dataclass(frozen=True)
class SpeciesEntry:
    pattern: re.Pattern[str]
    label_es: str
    label_en: str
    source: str = "playbook"


def _now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _ensure_playbook() -> Path:
    PLAYBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not PLAYBOOK_PATH.is_file():
        shutil.copy2(PLAYBOOK_SEED, PLAYBOOK_PATH)
    return PLAYBOOK_PATH


def _read_playbook_text() -> str:
    return _ensure_playbook().read_text(encoding="utf-8")


def _parse_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for raw in text.splitlines():
        line = raw.strip()
        head = _SECTION.match(line)
        if head:
            current = head.group(1).lower()
            sections.setdefault(current, [])
            continue
        if current is None or not line or line.startswith("<!--") or line.startswith(">"):
            continue
        if line.startswith("#"):
            continue
        sections.setdefault(current, []).append(line)
    return sections


def _parse_kv_bullets(rows: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for row in rows:
        if not row.startswith("- "):
            continue
        body = row[2:].strip()
        if ":" not in body:
            continue
        key, _, val = body.partition(":")
        out[key.strip()] = val.strip()
    return out


def _parse_species_rows(rows: list[str]) -> tuple[SpeciesEntry, ...]:
    entries: list[SpeciesEntry] = []
    for row in rows:
        if not row.startswith("- "):
            continue
        body = row[2:].strip()
        if "→" not in body:
            continue
        match_part, _, labels = body.partition("→")
        match_tok = match_part.strip()
        if "|" in labels:
            es, _, en = labels.partition("|")
            label_es, label_en = es.strip(), en.strip()
        else:
            label_es = label_en = labels.strip()
        if match_tok:
            entries.append(
                SpeciesEntry(
                    pattern=re.compile(match_tok, re.I),
                    label_es=label_es,
                    label_en=label_en,
                )
            )
    return tuple(entries)


def _parse_learned_phrases(rows: list[str]) -> tuple[str, ...]:
    phrases: list[str] = []
    for row in rows:
        if not row.startswith("- "):
            continue
        body = row[2:].strip()
        if "|" in body:
            phrase = body.split("|", 1)[0].strip()
        elif "×" in body:
            phrase = body.rsplit("(", 1)[0].strip()
        else:
            phrase = body
        if phrase and not phrase.startswith("["):
            phrases.append(phrase.lower())
    return tuple(dict.fromkeys(phrases))


def _parse_playbook(text: str) -> dict[str, Any]:
    sec = _parse_sections(text)
    species = _parse_species_rows(sec.get("non_catalog_species", []))
    species += _parse_species_rows(sec.get("learned_species", []))
    scope = tuple(
        x[2:].strip().lower()
        for x in sec.get("scope_markers", [])
        if x.startswith("- ")
    )
    learned_scope = _parse_learned_phrases(sec.get("learned_scope_markers", []))
    greeting_sig = tuple(
        x[2:].strip().lower()
        for x in sec.get("greeting_signals", [])
        if x.startswith("- ")
    )
    greeting = tuple(
        x[2:].strip().lower()
        for x in sec.get("greeting_markers", [])
        if x.startswith("- ")
    )
    learned_greeting = _parse_learned_phrases(sec.get("learned_greeting_markers", []))
    forbidden = _parse_learned_phrases(sec.get("learned_forbidden", []))
    hints = tuple(
        x[2:].strip().lower()
        for x in sec.get("spanish_hints", [])
        if x.startswith("- ")
    )
    return {
        "sections": sec,
        "species": species,
        "scope_markers": tuple(dict.fromkeys([*scope, *learned_scope])),
        "greeting_signals": greeting_sig,
        "greeting_markers": tuple(dict.fromkeys([*greeting, *learned_greeting])),
        "forbidden_phrases": forbidden,
        "spanish_hints": hints,
        "catalog_scope": _parse_kv_bullets(sec.get("catalog_scope", [])),
        "pet_focus": {
            lang: _parse_kv_bullets(sec.get(f"pet_focus_{lang}", []))
            for lang in ("es", "en", "de", "fr")
        },
        "progress": {
            lang: [x[2:].strip() for x in sec.get(f"progress_{lang}", []) if x.startswith("- ")]
            for lang in ("es", "en", "de", "fr")
        },
        "opening": {
            f"{lang}_{kind}": _single_line(sec.get(f"opening_{lang}_{kind}", []))
            for lang in ("es", "en", "de", "fr")
            for kind in ("excluded", "plain", "suffix_price", "suffix_focus")
        },
    }


def _single_line(rows: list[str]) -> str:
    for row in rows:
        if row and not row.startswith("<!--"):
            return row.strip()
    return ""


@lru_cache(maxsize=1)
def load_stream_voice_registry() -> dict[str, Any]:
    """Load conductor playbook MD (cached until reload)."""
    text = _read_playbook_text()
    parsed = _parse_playbook(text)
    parsed["playbook_path"] = str(PLAYBOOK_PATH)
    return parsed


def reload_stream_voice_registry() -> dict[str, Any]:
    load_stream_voice_registry.cache_clear()
    return load_stream_voice_registry()


def learning_enabled() -> bool:
    return os.environ.get("ZOOPLUS_STREAM_VOICE_LEARN", "1").lower() not in ("0", "false", "no")


def _append_playbook_line(section: str, line: str) -> None:
    text = _read_playbook_text()
    marker = f"## {section}"
    if marker not in text:
        text = text.rstrip() + f"\n\n{marker}\n\n{line}\n"
        PLAYBOOK_PATH.write_text(text, encoding="utf-8")
        return
    parts = text.split(marker, 1)
    tail = parts[1]
    next_sec = re.search(r"\n## ", tail)
    if next_sec:
        body = tail[: next_sec.start()]
        rest = tail[next_sec.start() :]
    else:
        body, rest = tail, ""
    norm_new = line.lower()
    for existing in body.splitlines():
        if existing.strip().startswith("- ") and norm_new in existing.lower():
            m = re.search(r"×(\d+)\)", existing)
            count = int(m.group(1)) + 1 if m else 2
            updated = re.sub(r"×\d+\)", f"×{count})", existing)
            if updated == existing:
                updated = existing.rstrip(")") + f" ×{count})"
            text = parts[0] + marker + body.replace(existing, updated, 1) + rest
            PLAYBOOK_PATH.write_text(text, encoding="utf-8")
            reload_stream_voice_registry()
            logger.info("conductor playbook +1 [%s]: %s", section, line[:80])
            return
    insert = body.rstrip() + f"\n{line}\n"
    text = parts[0] + marker + insert + rest
    PLAYBOOK_PATH.write_text(text, encoding="utf-8")
    reload_stream_voice_registry()
    logger.info("conductor playbook learn [%s]: %s", section, line[:80])


def record_stream_voice_learning(
    *,
    category: str,
    phrase: str,
    reason: str,
    source: str = "conductor_dedupe",
) -> None:
    """Conductor silently appends to internal playbook MD — never shown to shopper."""
    if not learning_enabled():
        return
    text = phrase.strip()
    if len(text) < 6:
        return
    section = _CATEGORY_TO_SECTION.get(category, "learned_forbidden")
    line = f"- {text[:200]} | {reason} | ×1 | {source} | {_now_iso()}"
    _append_playbook_line(section, line)


def resolve_lang(query: str, site_id: int) -> str:
    """Query-first language; falls back to shop locale (site 1=de, 3=en, 15=es)."""
    from src.llm.language import resolve_shopper_language

    code, _ = resolve_shopper_language(query, None, site_id=site_id)
    return code if code in ("es", "en", "de", "fr") else "en"


def is_spanish_query(query: str) -> bool:
    return resolve_lang(query, 15) == "es"


def probe_instant_lane(query: str, site_id: int) -> str:
    """
    Fast lane probe before LLM intent — avoids wrong catalog ack on social turns.
    Returns: social | catalog | pending
    """
    from src.agents.intent_agent import try_obvious_social_intent
    from src.agents.intent_hints import looks_like_catalog_search

    text = (query or "").strip()
    if not text:
        return "pending"
    obvious = try_obvious_social_intent(text)
    if obvious is not None and obvious.lane == "conversational":
        return "social"
    if (
        looks_like_catalog_search(text)
        or mentions_non_catalog_species(text, site_id)
        or price_hint(text, lang=resolve_lang(text, site_id))
    ):
        return "catalog"
    return "pending"


def has_catalog_intent_signals(query: str, *, lang: str, site_id: int) -> bool:
    from src.agents.intent_hints import looks_like_catalog_search

    if looks_like_catalog_search(query):
        return True
    if mentions_non_catalog_species(query, site_id) or price_hint(query, lang=lang):
        return True
    q = query.lower()
    return bool(re.search(r"perro|gato|dog|cat|food|comida|futter|nourriture|precio|price|€", q))


_IN_SCOPE_PET_ALIASES = frozenset(
    {
        "perro",
        "perros",
        "perra",
        "perras",
        "gato",
        "gatos",
        "gata",
        "gatas",
        "dog",
        "dogs",
        "cat",
        "cats",
        "puppy",
        "puppies",
        "kitten",
        "kittens",
        "cachorro",
        "cachorros",
        "gatito",
        "gatitos",
        "hund",
        "hunde",
        "hunde",
        "katze",
        "katzen",
        "chat",
        "chats",
        "chien",
        "chiens",
        "canino",
        "caninos",
        "felino",
        "felinos",
        "hund",
        "hund",
    }
)

_SPECIES_EXTRACT_SKIP = frozenset(
    {
        "los",
        "las",
        "mis",
        "tus",
        "unos",
        "unas",
        "the",
        "my",
        "your",
        "productos",
        "producto",
        "products",
        "product",
        "opciones",
        "available",
        "disponible",
        "disponibles",
        "anything",
        "something",
        "comida",
        "food",
        "algo",
        "something",
        "tienes",
        "tenéis",
        "have",
        "sell",
        "esto",
        "esa",
        "ese",
        "entre",
        "hasta",
        "menos",
        "euros",
        "eur",
        "precio",
        "price",
        "estomago",
        "estómago",
        "sensitive",
        "stomach",
        "seco",
        "dry",
        "wet",
        "humedo",
        "húmedo",
        "grain",
        "free",
        "puppy",
        "adult",
        "senior",
    }
)

_PET_NOUN_PATTERNS = (
    re.compile(
        r"(?:y\s+)?(?:para|for|pour|für)\s+(?:los|las|mis|de|el|la|le|les)?\s*"
        r"([a-záéíóúñäöüß]{3,})",
        re.I,
    ),
    re.compile(r"(?:what|how)\s+about\s+([a-záéíóúñ]{3,})", re.I),
    re.compile(r"\b(?:about|acerca\s+de)\s+([a-záéíóúñ]{3,})", re.I),
    re.compile(
        r"\b(?:tienes|tenéis)\s+(?:algo\s+)?(?:para\s+)?(?:los|las|el|la)?\s*([a-záéíóúñ]{3,})",
        re.I,
    ),
)


def _catalog_vocab_tokens(site_id: int) -> frozenset[str]:
    """Brands + product tokens from ingest — not treated as out-of-scope species."""
    from src.rag.catalog_lexicon import load_lexicon

    lex = load_lexicon()
    vocab: set[str] = set()
    for brand in lex.get("brands", []):
        for part in re.split(r"[\s\-]+", str(brand).lower()):
            if len(part) >= 3:
                vocab.add(part)
    for tok in lex.get("product_tokens", []):
        vocab.add(str(tok).lower())
    for pet in lex.get("pet_types", []):
        vocab.add(str(pet).lower())
    return frozenset(vocab)


def _normalize_species_token(token: str) -> str:
    return token.lower().strip().strip("¿?¡!.,;")


def _is_in_scope_pet(token: str) -> bool:
    norm = _normalize_species_token(token)
    if norm in _IN_SCOPE_PET_ALIASES:
        return True
    if norm.endswith("s") and norm[:-1] in _IN_SCOPE_PET_ALIASES:
        return True
    return False


def _extract_out_of_scope_pet_tokens(query: str, site_id: int) -> tuple[str, ...]:
    """Infer pet nouns in query that are not dogs/cats — works for species absent from playbook."""
    text = (query or "").strip()
    if not text:
        return ()
    catalog_vocab = _catalog_vocab_tokens(site_id)
    found: list[str] = []
    for pattern in _PET_NOUN_PATTERNS:
        for match in pattern.finditer(text):
            raw = _normalize_species_token(match.group(1))
            if not raw or raw in _SPECIES_EXTRACT_SKIP or raw in catalog_vocab:
                continue
            if _is_in_scope_pet(raw):
                continue
            if raw not in found:
                found.append(raw)
    return tuple(found)


def _playbook_species_hits(query: str) -> tuple[SpeciesEntry, ...]:
    reg = load_stream_voice_registry()
    return tuple(e for e in reg["species"] if e.pattern.search(query))


def _learn_discovered_species(token: str) -> None:
    """Append newly inferred species to learned_species (conductor auto-learn)."""
    if not learning_enabled():
        return
    norm = _normalize_species_token(token)
    if not norm or _is_in_scope_pet(norm):
        return
    reg = load_stream_voice_registry()
    if any(e.pattern.search(norm) for e in reg["species"]):
        return
    stem = norm[:-1] if norm.endswith("s") and len(norm) > 4 else norm
    match_expr = f"{stem}|{norm}"
    line = f"- {match_expr} → {norm} | {norm}"
    _append_playbook_line("learned_species", line)


def infer_non_catalog_species_labels(
    query: str,
    site_id: int = 3,
    *,
    lang: str = "es",
    learn: bool = True,
) -> tuple[str, ...]:
    """Playbook + dynamic inference — handles species never seen before."""
    labels: list[str] = []
    for entry in _playbook_species_hits(query):
        labels.append(entry.label_es if lang in ("es", "fr") else entry.label_en)
    for token in _extract_out_of_scope_pet_tokens(query, site_id):
        if learn:
            _learn_discovered_species(token)
        if token not in labels:
            labels.append(token)
    return tuple(dict.fromkeys(labels))


def mentions_non_catalog_species(query: str, site_id: int = 3) -> bool:
    return bool(infer_non_catalog_species_labels(query, site_id, learn=True))


def non_catalog_labels(query: str, *, lang: str = "es", site_id: int = 3) -> tuple[str, ...]:
    return infer_non_catalog_species_labels(query, site_id, lang=lang, learn=True)


def _join_labels(items: tuple[str, ...] | list[str], *, lang: str) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    joiners = {"es": "ni", "en": "or", "de": "oder", "fr": "ou"}
    j = joiners.get(lang, "or")
    return ", ".join(items[:-1]) + f" {j} {items[-1]}"


def price_hint(query: str, *, lang: str = "es") -> str | None:
    band = parse_eur_price_range(query)
    if band:
        lo, hi = band
        if lang == "es":
            return f"entre {lo:.0f}€ y {hi:.0f}€"
        return f"between €{lo:.0f} and €{hi:.0f}"
    m = _MAX_EUR_HINT.search(query)
    if m:
        val = int(m.group(1))
        return f"hasta {val}€" if lang == "es" else f"up to €{val}"
    return None


def pet_focus(query: str, *, lang: str = "es") -> str:
    reg = load_stream_voice_registry()
    cfg = reg["pet_focus"].get(lang) or reg["pet_focus"].get("en", {})
    q = query.lower()
    has_dog = bool(re.search(r"perro|dog", q))
    has_cat = bool(re.search(r"gato|cat|felin", q))
    if has_dog and has_cat:
        return cfg.get("both", cfg.get("default", ""))
    if has_cat:
        return cfg.get("cat", cfg.get("default", ""))
    if has_dog:
        return cfg.get("dog", cfg.get("default", ""))
    return cfg.get("default", "")


def catalog_scope_label(*, lang: str = "es") -> str:
    reg = load_stream_voice_registry()
    scope = reg["catalog_scope"]
    return scope.get(lang, scope.get("en", "dogs and cats"))


def progress_phrase(query: str, tick_index: int, *, site_id: int = 3) -> str:
    reg = load_stream_voice_registry()
    lang = resolve_lang(query, site_id)
    pool = reg["progress"].get(lang) or reg["progress"].get("en", [])
    if not pool:
        return ""
    idx = min(max(0, tick_index - 1), len(pool) - 1)
    return pool[idx]


def format_catalog_opening(query: str, site_id: int) -> str:
    """Catalog-only opening — contextual suffix only when query has catalog signals."""
    reg = load_stream_voice_registry()
    op = reg["opening"]
    lang = resolve_lang(query, site_id)
    scope = catalog_scope_label(lang=lang)
    excluded = non_catalog_labels(query, lang=lang)
    focus = pet_focus(query, lang=lang)
    price = price_hint(query, lang=lang)

    if excluded:
        exc = _join_labels(excluded, lang=lang)
        line = op.get(f"{lang}_excluded", op.get("en_excluded", "")).format(
            catalog_scope=scope, excluded=exc
        )
    else:
        line = op.get(f"{lang}_plain", op.get("en_plain", ""))

    if has_catalog_intent_signals(query, lang=lang, site_id=site_id):
        if price:
            suffix = op.get(f"{lang}_suffix_price", op.get("en_suffix_price", "")).format(
                focus=focus, price=price
            )
        else:
            suffix = op.get(f"{lang}_suffix_focus", op.get("en_suffix_focus", "")).format(
                focus=focus
            )
        return (line + suffix).strip()
    return line.strip()


def format_opening_line(query: str, site_id: int) -> str:
    """Alias — catalog opening only (call after lane probe)."""
    return format_catalog_opening(query, site_id)


def scope_markers() -> tuple[str, ...]:
    return load_stream_voice_registry()["scope_markers"]


def greeting_signals() -> tuple[str, ...]:
    return load_stream_voice_registry()["greeting_signals"]


def greeting_markers() -> tuple[str, ...]:
    return load_stream_voice_registry()["greeting_markers"]


def forbidden_phrases() -> tuple[str, ...]:
    return load_stream_voice_registry()["forbidden_phrases"]


def non_catalog_tokens() -> tuple[str, ...]:
    reg = load_stream_voice_registry()
    tokens: list[str] = []
    for entry in reg["species"]:
        for part in entry.pattern.pattern.split("|"):
            tokens.append(part.strip().lower())
    return tuple(dict.fromkeys(t for t in tokens if t))


def chunk_is_redundant(text: str, prior: tuple[str, ...]) -> bool:
    if not prior:
        return False
    norm = text.strip().lower()
    if not norm:
        return True
    markers = scope_markers()
    for prev in prior:
        prev_l = prev.strip().lower()
        if norm == prev_l:
            record_stream_voice_learning(
                category="forbidden_phrases", phrase=text, reason="duplicate_chunk"
            )
            return True
        if len(norm) > 20 and (norm in prev_l or prev_l in norm):
            record_stream_voice_learning(
                category="forbidden_phrases", phrase=text, reason="near_duplicate_chunk"
            )
            return True
        if any(m in norm and m in prev_l for m in markers):
            record_stream_voice_learning(
                category="scope_markers", phrase=text, reason="repeated_scope_in_chunk"
            )
            return True
    return False


_INTRO_GREETING_RE = re.compile(
    r"^(?:¡?\s*)?(?:hola|hello|hi|hey|buenas)\b"
    r"(?:\s*[,!.])?\s*(?:soy el|soy la|i['']?m the|i am the|i'm)\s+"
    r"(?:the\s+)?zooplus\s+assistant\b",
    re.I,
)

_CONTINUATION_QUERY_RE = re.compile(
    r"^(?:y\s+|and\s+|also\s+|además\s+|otra\s+cosa[,:]?\s+|"
    r"what\s+about\s+|how\s+about\s+|para\s+(?:los|las|mis|mis\s+)?)\b",
    re.I,
)


def is_continuation_query(query: str) -> bool:
    """Follow-up turn — shopper already spoke; no re-introduction in final answer."""
    text = (query or "").strip()
    if not text:
        return False
    if _CONTINUATION_QUERY_RE.search(text):
        return True
    return text.lower().startswith(("y ", "and ", "also ", "además "))


def _sentence_has_greeting(pl: str, g_markers: tuple[str, ...]) -> bool:
    if pl.startswith("hola") or pl.startswith("hello") or pl.startswith("hi "):
        return True
    if _INTRO_GREETING_RE.search(pl):
        return True
    return any(m in pl for m in g_markers)


def strip_leading_assistant_intro(answer: str) -> str:
    """Remove redundant zooplus Assistant self-intro from answer start."""
    text = answer.strip()
    if not text:
        return answer
    m = _INTRO_GREETING_RE.match(text)
    if m:
        rest = text[m.end() :].lstrip(" ,.—-")
        if rest:
            record_stream_voice_learning(
                category="greeting_markers",
                phrase=text[: m.end()].strip(),
                reason="leading_intro_stripped",
            )
            return rest
    return answer


def dedupe_answer_against_chunks(answer: str, chunks: tuple[str, ...]) -> str:
    if not chunks or not answer:
        return answer
    blob = " ".join(chunks).lower()
    scope_said = any(m in blob for m in scope_markers())
    # Any live chunk means the shopper already saw stream messages — no re-greeting.
    conversation_started = True
    greeted = conversation_started or any(x in blob for x in greeting_signals())
    g_markers = greeting_markers()
    forbidden = forbidden_phrases()
    species_tokens = non_catalog_tokens()
    parts = re.split(r"(?<=[.!?])\s+", answer.strip())
    kept: list[str] = []
    for part in parts:
        pl = part.lower()
        drop = False
        if scope_said and any(m in pl for m in scope_markers()):
            drop = True
            record_stream_voice_learning(
                category="scope_markers", phrase=part, reason="scope_repeated_in_final"
            )
        if scope_said and any(s in pl for s in species_tokens):
            drop = True
            record_stream_voice_learning(
                category="forbidden_phrases", phrase=part, reason="non_catalog_repeated_in_final"
            )
        if greeted and _sentence_has_greeting(pl, g_markers):
            drop = True
            record_stream_voice_learning(
                category="greeting_markers", phrase=part, reason="greeting_repeated_in_final"
            )
        if any(f in pl for f in forbidden):
            drop = True
            record_stream_voice_learning(
                category="forbidden_phrases", phrase=part, reason="learned_forbidden_in_final"
            )
        if not drop:
            kept.append(part)
    merged = " ".join(kept).strip()
    merged = strip_leading_assistant_intro(merged)
    return merged or strip_leading_assistant_intro(answer)


def stream_context_for_synthesis(
    status_chunks: tuple[str, ...],
    *,
    query: str | None = None,
) -> str:
    if not status_chunks:
        return ""
    forbidden = forbidden_phrases()
    lines = "\n".join(f"- {c}" for c in status_chunks)
    extra = ""
    if forbidden:
        extra = "\nBanned phrases (conductor playbook): " + "; ".join(forbidden[:10])
    continuation = ""
    if query and is_continuation_query(query):
        continuation = (
            "\nThis is a FOLLOW-UP turn in an ongoing chat — "
            "never say Hola/hello or re-introduce yourself as zooplus Assistant."
        )
    return (
        "Live stream messages already shown to the shopper (conversation in progress):\n"
        f"{lines}\n"
        "Final answer: continue the conversation — no greeting, no self-intro, "
        "no scope repeat, no ambiguity — products or one clear next step."
        f"{continuation}{extra}"
    )
