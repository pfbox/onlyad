import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, Float, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Ad(Base):
    __tablename__ = "ads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_url: Mapped[str] = mapped_column(String(500), nullable=False)
    media_type: Mapped[str] = mapped_column(String(10), nullable=False)  # "video" or "image"
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="general")
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # comma-separated tags
    uploaded_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    upvotes: Mapped[int] = mapped_column(Integer, default=0)
    downvotes: Mapped[int] = mapped_column(Integer, default=0)
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    votes = relationship("Vote", back_populates="ad")
    views = relationship("View", back_populates="ad")