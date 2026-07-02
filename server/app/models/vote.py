import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Integer, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (UniqueConstraint("user_id", "ad_id", name="uq_user_ad_vote"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    ad_id: Mapped[str] = mapped_column(String(36), ForeignKey("ads.id"), nullable=False)
    vote: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 = upvote, -1 = downvote
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="votes")
    ad = relationship("Ad", back_populates="votes")