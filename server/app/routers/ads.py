import os
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..config import UPLOAD_DIR
from ..database import get_db
from ..middleware.auth import get_current_user
from ..models.ad import Ad
from ..models.user import User
from ..models.vote import Vote
from ..schemas.ad import AdCreate, AdResponse, AdFeedItem
from ..services.recommendation import get_recommended_ads

router = APIRouter(prefix="/api/ads", tags=["ads"])

ALLOWED_EXTENSIONS = {"mp4", "webm", "mov", "jpg", "jpeg", "png", "gif", "webp"}


def get_media_type(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext in {"mp4", "webm", "mov"}:
        return "video"
    return "image"


@router.post("/upload", response_model=AdResponse)
async def upload_ad(
    file: UploadFile = File(...),
    title: str = Form(...),
    brand: str = Form(...),
    description: str = Form(None),
    category: str = Form("general"),
    tags: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user),
):
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    media_type = get_media_type(file.filename)
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    media_url = f"/uploads/{filename}"

    ad = Ad(
        title=title,
        brand=brand,
        description=description,
        media_url=media_url,
        media_type=media_type,
        category=category,
        tags=tags,
        uploaded_by=current_user.id if current_user else None,
    )
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return AdResponse.model_validate(ad)


@router.get("/feed", response_model=list[AdFeedItem])
def get_feed(
    limit: int = Query(default=20, le=50),
    offset: int = Query(default=0),
    exclude: str = Query(default=""),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user),
):
    exclude_ids = set(exclude.split(",")) if exclude else set()

    # Get recommended ads
    ads = get_recommended_ads(db, current_user.id if current_user else None, limit=limit, exclude_ids=exclude_ids)

    # If we don't have enough, fill with fresh ads
    if len(ads) < limit:
        existing_ids = {a.id for a in ads} | exclude_ids
        remaining = limit - len(ads)
        fresh = (
            db.query(Ad)
            .filter(~Ad.id.in_(existing_ids))
            .order_by(Ad.created_at.desc())
            .limit(remaining)
            .all()
        )
        ads.extend(fresh)

    # Get user votes for these ads
    user_votes: dict[str, int] = {}
    if current_user:
        votes = db.query(Vote).filter(
            Vote.user_id == current_user.id,
            Vote.ad_id.in_([a.id for a in ads]),
        ).all()
        user_votes = {v.ad_id: v.vote for v in votes}

    result = []
    for ad in ads:
        item = AdFeedItem(
            id=ad.id,
            title=ad.title,
            brand=ad.brand,
            description=ad.description,
            media_url=ad.media_url,
            media_type=ad.media_type,
            category=ad.category,
            tags=ad.tags,
            upvotes=ad.upvotes,
            downvotes=ad.downvotes,
            score=ad.score,
            user_vote=user_votes.get(ad.id),
        )
        result.append(item)

    return result


@router.get("/search", response_model=list[AdResponse])
def search_ads(
    q: str = Query(default=""),
    tag: str = Query(default=""),
    category: str = Query(default=""),
    limit: int = Query(default=20, le=50),
    db: Session = Depends(get_db),
):
    query = db.query(Ad)

    if q:
        query = query.filter(
            or_(
                Ad.title.ilike(f"%{q}%"),
                Ad.brand.ilike(f"%{q}%"),
                Ad.description.ilike(f"%{q}%"),
            )
        )

    if tag:
        query = query.filter(Ad.tags.ilike(f"%{tag}%"))

    if category:
        query = query.filter(Ad.category == category)

    ads = query.order_by(Ad.score.desc()).limit(limit).all()
    return [AdResponse.model_validate(ad) for ad in ads]


@router.get("/{ad_id}", response_model=AdResponse)
def get_ad(ad_id: str, db: Session = Depends(get_db)):
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return AdResponse.model_validate(ad)