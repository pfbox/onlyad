from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import UPLOAD_DIR
from .database import engine, Base
from .routers import auth, ads, votes

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OnlyAds",
    description="TikTok-style ad browsing and rating application",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Routers
app.include_router(auth.router)
app.include_router(ads.router)
app.include_router(votes.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}