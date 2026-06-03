"""API contracts — aligned with Coding Task.docx."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    site_id: int = Field(..., ge=1, description="Shop context")
    query: str = Field(..., min_length=1, description="Customer question")


class RetrievedProduct(BaseModel):
    article_id: int
    product_id: int
    variant_id: str
    product_name: str
    variant_name: str | None = None
    price: float
    currency: str = "EUR"
    pet_type: str
    brands: str
    relevance_score: float | None = None
    recommendation_reason: str | None = None


class ChatResponse(BaseModel):
    answer: str
    retrieved_products: list[RetrievedProduct]
