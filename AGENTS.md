# OnlyAd — Architecture

TikTok-style ad browsing and rating app. Users swipe through ads, upvote/downvote, and get personalized recommendations via a hybrid collaborative+content-based engine.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.13, FastAPI, SQLAlchemy 2.x ORM |
| Database | PostgreSQL 16 (Docker), psycopg2-binary |
| Auth | JWT (python-jose + passlib/bcrypt) |
| Recommendation | scikit-learn (cosine similarity), numpy |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Package mgmt | uv (server), npm (client) |
| Migrations | Alembic (in deps, not yet configured) |

---

## Project layout

```
onlyad/
├── docker-compose.yml          # PostgreSQL 16-alpine, port 5432, volume pgdata/
├── .gitignore                  # pgdata/, *.db, .env, __pycache__, node_modules/
├── server/
│   ├── pyproject.toml          # Python deps (uv)
│   ├── .env                    # DATABASE_URL, SECRET_KEY
│   ├── seed.py                 # Seed 39 sample ads
│   ├── uploads/                # Uploaded media files (gitignored)
│   └── app/
│       ├── main.py             # FastAPI app, CORS, static mounts, routers
│       ├── config.py           # DATABASE_URL, SECRET_KEY, JWT settings, UPLOAD_DIR
│       ├── database.py         # SQLAlchemy engine + session factory
│       ├── models/
│       │   ├── __init__.py     # Re-exports User, Ad, Vote, View
│       │   ├── user.py         # User model (id, email, name, hashed_password, avatar)
│       │   ├── ad.py           # Ad model (title, brand, media, category, tags, vote counts, score)
│       │   ├── vote.py         # Vote model (user_id, ad_id, vote=1|-1, unique per user+ad)
│       │   └── view.py         # View model (user_id, ad_id, watch_duration)
│       ├── schemas/
│       │   ├── __init__.py     # Re-exports all Pydantic schemas
│       │   ├── user.py         # UserCreate, UserResponse, Token, LoginRequest
│       │   ├── ad.py           # AdCreate, AdResponse, AdFeedItem (includes user_vote)
│       │   └── vote.py         # VoteCreate, VoteResponse
│       ├── routers/
│       │   ├── __init__.py     # Empty
│       │   ├── auth.py         # POST /api/auth/register, /login, GET /me
│       │   ├── ads.py          # POST /api/ads/upload, GET /feed, /search, /{id}
│       │   └── votes.py        # POST /api/votes/, GET /history
│       ├── middleware/
│       │   └── auth.py         # get_current_user (optional), require_user (required)
│       └── services/
│           └── recommendation.py  # Hybrid recommendation engine
└── client/
    ├── package.json
    ├── vite.config.ts          # Dev server on :5173
    ├── tailwind.config.js      # Custom colors (primary=#ff2d55, dark=#121212)
    ├── index.html
    └── src/
        ├── main.tsx            # React entry point
        ├── App.tsx             # Tab navigation (Feed, Search, Upload, Profile)
        ├── api/
        │   ├── client.ts       # fetch wrapper, Bearer token management, apiRequest(), apiUpload()
        │   ├── endpoints.ts    # Typed API functions (getFeed, castVote, login, etc.)
        │   └── types.ts        # Ad, AdFeedItem, User, AuthResponse, VoteResponse interfaces
        ├── hooks/
        │   └── useAuth.ts      # Auth state (user, loading, login, register, logout)
        └── components/
            ├── SwipeFeed.tsx   # Card stack, swipe gestures (touch+keyboard), vote/skip
            ├── SearchPage.tsx  # Search/filter ads by text, tag, category
            ├── UploadPage.tsx  # Upload new ad with form
            └── AuthModal.tsx   # Login/register modal
```

---

## Database schema

### `users`
| Column | Type | Notes |
|--------|------|-------|
| id | VARCHAR(36) PK | UUID4 |
| email | VARCHAR(255) UNIQUE, INDEX | |
| name | VARCHAR(255) | |
| hashed_password | VARCHAR(255) | bcrypt |
| avatar | VARCHAR(500) NULL | |
| created_at | TIMESTAMPTZ | server_default=now() |

### `ads`
| Column | Type | Notes |
|--------|------|-------|
| id | VARCHAR(36) PK | UUID4 |
| title | VARCHAR(255) | |
| brand | VARCHAR(255) | |
| description | TEXT NULL | |
| media_url | VARCHAR(500) | e.g. /uploads/abc.mp4 |
| media_type | VARCHAR(10) | "video" or "image" |
| category | VARCHAR(100) | default "general" |
| tags | TEXT NULL | comma-separated |
| uploaded_by | VARCHAR(36) NULL | FK→users.id |
| upvotes | INTEGER | denormalized counter |
| downvotes | INTEGER | denormalized counter |
| views_count | INTEGER | denormalized counter |
| score | FLOAT | Wilson-like score (upvotes/total * 100) |
| created_at | TIMESTAMPTZ | server_default=now() |

### `votes`
| Column | Type | Notes |
|--------|------|-------|
| id | VARCHAR(36) PK | UUID4 |
| user_id | VARCHAR(36) FK→users | |
| ad_id | VARCHAR(36) FK→ads | |
| vote | INTEGER | 1 (upvote) or -1 (downvote) |
| created_at | TIMESTAMPTZ | server_default=now() |

Unique constraint: `(user_id, ad_id)`. Vote updates (upsert) on re-vote.

### `views`
| Column | Type | Notes |
|--------|------|-------|
| id | VARCHAR(36) PK | UUID4 |
| user_id | VARCHAR(36) NULL FK→users | nullable for anonymous |
| ad_id | VARCHAR(36) FK→ads | |
| watch_duration | INTEGER NULL | seconds |
| created_at | TIMESTAMPTZ | server_default=now() |

---

## API endpoints

### Auth (`/api/auth`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /register | No | Create user, return JWT |
| POST | /login | No | Login, return JWT |
| GET | /me | Required | Get current user |

### Ads (`/api/ads`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /feed | Optional | Personalized feed (recommendation engine) |
| GET | /search | No | Search by q/tag/category, ordered by score |
| GET | /{ad_id} | No | Single ad |
| POST | /upload | Optional | Multipart upload (file + form fields) |

### Votes (`/api/votes`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | / | Required | Cast/update vote, recalculates ad score |
| GET | /history | Required | User's vote history |

### Health
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/health | No | `{"status": "ok"}` |

---

## Recommendation engine

`server/app/services/recommendation.py`

**Hybrid approach: 60% collaborative + 40% content-based.**

### Content-based
- Builds a user profile vector from tags of upvoted ads (mean of one-hot tag vectors)
- Computes cosine similarity between user profile and candidate ad vectors
- Applies penalty for tags present in downvoted ads
- Adds trending score: `upvotes / (total + 1)`

### Collaborative filtering
- Builds user-vote matrix (centered: subtracts each user's mean vote)
- Computes user-user cosine similarity
- Predicts score via Top-K weighted neighbor votes

### Fallback
- Unauthenticated users: sorted by `score` descending
- Users with no votes: sorted by `score` descending
- No collaborative neighbors: 100% content-based score

### Current scalability limitation
Every feed request loads **all votes** and **all ads** into memory to build the similarity matrix. Fine for <1000 ads, needs rewriting (precomputed matrix/Redis pgvector) at scale.

---

## Auth flow

1. Client stores JWT in `localStorage('token')`
2. `api/client.ts` attaches `Authorization: Bearer <token>` to requests
3. `middleware/auth.py` decodes JWT via `python-jose`, looks up user in DB
4. `get_current_user` returns `User | None` (optional auth for feed)
5. `require_user` raises 401 if unauthenticated (for votes, profile)

---

## Running the app

```bash
# 1. Start PostgreSQL
docker compose up -d

# 2. Install deps
cd server && uv sync
cd client && npm install

# 3. Seed database
cd server && uv run python seed.py --force

# 4. Start backend (port 8000)
cd server && uv run uvicorn app.main:app --reload

# 5. Start frontend (port 5173)
cd client && npm run dev
```

CORS is configured for `localhost:5173` and `localhost:3000`.

---

## Key conventions

- **UUIDs**: All primary keys are `VARCHAR(36)` UUID4 strings (no auto-increment integers)
- **Denormalized counters**: `ads.upvotes`, `ads.downvotes`, `ads.score` are recalculated on every vote via `_update_ad_score()`
- **Tags**: Stored as comma-separated strings in a TEXT column (not normalized)
- **Media**: Uploaded to local disk (`server/uploads/`), served via FastAPI `StaticFiles` mount
- **Optional auth**: Feed and search endpoints work without login; voting requires auth
- **No pagination cursor**: Feed uses `exclude` query param (comma-separated IDs of already-seen ads)
