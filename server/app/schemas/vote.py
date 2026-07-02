from datetime import datetime
from pydantic import BaseModel


class VoteCreate(BaseModel):
    ad_id: str
    vote: int  # 1 = upvote, -1 = downvote


class VoteResponse(BaseModel):
    id: str
    user_id: str
    ad_id: str
    vote: int
    created_at: datetime

    model_config = {"from_attributes": True}