from datetime import datetime
from pydantic import BaseModel


class AdCreate(BaseModel):
    title: str
    brand: str
    description: str | None = None
    media_type: str  # "video" or "image"
    category: str = "general"
    tags: str | None = None  # comma-separated


class AdResponse(BaseModel):
    id: str
    title: str
    brand: str
    description: str | None = None
    media_url: str
    media_type: str
    category: str
    tags: str | None = None
    upvotes: int
    downvotes: int
    views_count: int
    score: float
    created_at: datetime

    model_config = {"from_attributes": True}


class AdFeedItem(BaseModel):
    id: str
    title: str
    brand: str
    description: str | None = None
    media_url: str
    media_type: str
    category: str
    tags: str | None = None
    upvotes: int
    downvotes: int
    score: float
    user_vote: int | None = None  # 1, -1, or None if not voted

    model_config = {"from_attributes": True}