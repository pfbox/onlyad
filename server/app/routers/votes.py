from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..middleware.auth import get_current_user, require_user
from ..models.ad import Ad
from ..models.user import User
from ..models.vote import Vote
from ..schemas.vote import VoteCreate, VoteResponse

router = APIRouter(prefix="/api/votes", tags=["votes"])


def _update_ad_score(db: Session, ad_id: str):
    """Recalculate ad score based on votes."""
    upvotes = db.query(func.count(Vote.id)).filter(Vote.ad_id == ad_id, Vote.vote == 1).scalar() or 0
    downvotes = db.query(func.count(Vote.id)).filter(Vote.ad_id == ad_id, Vote.vote == -1).scalar() or 0
    total = upvotes + downvotes
    # Wilson-like score
    if total > 0:
        score = (upvotes / total) * 100
    else:
        score = 0

    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if ad:
        ad.upvotes = upvotes
        ad.downvotes = downvotes
        ad.score = score
        db.commit()


@router.post("/", response_model=VoteResponse)
def cast_vote(
    vote_data: VoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    if vote_data.vote not in (1, -1):
        raise HTTPException(status_code=400, detail="Vote must be 1 (upvote) or -1 (downvote)")

    # Check ad exists
    ad = db.query(Ad).filter(Ad.id == vote_data.ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    # Check existing vote
    existing = db.query(Vote).filter(
        Vote.user_id == current_user.id,
        Vote.ad_id == vote_data.ad_id,
    ).first()

    if existing:
        # Update vote
        existing.vote = vote_data.vote
        db.commit()
        db.refresh(existing)
        _update_ad_score(db, vote_data.ad_id)
        return VoteResponse.model_validate(existing)

    # Create new vote
    vote = Vote(
        user_id=current_user.id,
        ad_id=vote_data.ad_id,
        vote=vote_data.vote,
    )
    db.add(vote)
    db.commit()
    db.refresh(vote)
    _update_ad_score(db, vote_data.ad_id)
    return VoteResponse.model_validate(vote)


@router.get("/history", response_model=list[VoteResponse])
def get_vote_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    votes = db.query(Vote).filter(Vote.user_id == current_user.id).order_by(Vote.created_at.desc()).all()
    return [VoteResponse.model_validate(v) for v in votes]