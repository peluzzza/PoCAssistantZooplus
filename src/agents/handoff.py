"""Internal routing context between OpenCode steps (invisible to shopper)."""

from __future__ import annotations

from dataclasses import dataclass

TOPIC_SHOP_SOCIAL = "shop_social"
TOPIC_PET_CATALOG = "pet_catalog"
TOPIC_OFF_TOPIC = "off_topic"


@dataclass(frozen=True)
class AgentHandoff:
    site_id: int
    user_message: str
    lane: str
    topic: str
    social_kind: str | None
    reason: str
    source: str

    def brief(self) -> str:
        parts = [
            f"site_id={self.site_id}",
            f"topic={self.topic}",
            f"lane={self.lane}",
            f"step={self._step()}",
        ]
        if self.social_kind:
            parts.append(f"social_kind={self.social_kind}")
        if self.reason:
            parts.append(f"reason={self.reason}")
        parts.append(f'user_message="{self.user_message[:500]}"')
        return "Internal routing: " + "; ".join(parts)

    def _step(self) -> str:
        if self.lane == "catalog_search":
            return "catalog_retrieve_then_synthesis"
        if self.lane == "decline_off_topic":
            return "polite_boundary"
        return "conversational_reply"


def normalize_topic(value: str | None, *, lane: str) -> str:
    v = (value or "").strip().lower().replace("-", "_")
    if v in (TOPIC_PET_CATALOG, "catalog", "product_search", "products"):
        return TOPIC_PET_CATALOG
    if v in (TOPIC_OFF_TOPIC, "off_topic", "blocked", "decline"):
        return TOPIC_OFF_TOPIC
    if v in (TOPIC_SHOP_SOCIAL, "shop_social", "social", "assistant", "capabilities", "help"):
        return TOPIC_SHOP_SOCIAL
    if lane == "catalog_search":
        return TOPIC_PET_CATALOG
    if lane == "decline_off_topic":
        return TOPIC_OFF_TOPIC
    return TOPIC_SHOP_SOCIAL


def build_handoff(
    *,
    query: str,
    site_id: int,
    lane: str,
    topic: str | None,
    social_kind: str | None,
    reason: str,
    source: str,
) -> AgentHandoff:
    return AgentHandoff(
        site_id=site_id,
        user_message=query,
        lane=lane,
        topic=normalize_topic(topic, lane=lane),
        social_kind=social_kind,
        reason=reason,
        source=source,
    )
