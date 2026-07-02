import numpy as np
from sqlalchemy.orm import Session
from sklearn.metrics.pairwise import cosine_similarity

from ..models.ad import Ad
from ..models.vote import Vote


def _tags_to_vector(tags: str | None, all_tags: list[str]) -> np.ndarray:
    if not tags:
        return np.zeros(len(all_tags), dtype=float)
    ad_tags = [t.strip().lower() for t in tags.split(",")]
    return np.array([1.0 if t in ad_tags else 0.0 for t in all_tags], dtype=float)


def _compute_content_score(
    ad: Ad,
    ad_vec: np.ndarray,
    user_profile: np.ndarray,
    downvoted_tags: set[str],
) -> float:
    if np.any(ad_vec) and np.any(user_profile):
        similarity = cosine_similarity([user_profile], [ad_vec])[0][0]
    else:
        similarity = 0.0

    penalty = 0.0
    if ad.tags:
        ad_tag_list = [t.strip().lower() for t in ad.tags.split(",")]
        penalty = 0.3 * len(set(ad_tag_list) & downvoted_tags)

    total_votes = ad.upvotes + ad.downvotes
    trending = ad.upvotes / (total_votes + 1) if total_votes > 0 else 0.0

    return 0.5 * similarity + 0.3 * trending - penalty + 0.2 * (ad.score / 100.0)


def _build_user_vote_matrix(
    db: Session,
) -> tuple[dict[str, int], dict[str, int], np.ndarray]:
    votes = db.query(Vote).all()
    if not votes:
        return {}, {}, np.array([]).reshape(0, 0)

    user_ids = sorted({v.user_id for v in votes})
    ad_ids = sorted({v.ad_id for v in votes})
    user_idx = {uid: i for i, uid in enumerate(user_ids)}
    ad_idx = {aid: i for i, aid in enumerate(ad_ids)}

    matrix = np.zeros((len(user_ids), len(ad_ids)), dtype=float)
    for v in votes:
        ui = user_idx[v.user_id]
        ai = ad_idx[v.ad_id]
        matrix[ui, ai] = v.vote

    # Center each user's votes (subtract mean), replace NaN (no-vote users) with 0
    user_means = matrix.mean(axis=1, keepdims=True)
    centered = matrix - user_means
    centered = np.nan_to_num(centered)

    return user_idx, ad_idx, centered


def _collaborative_score(
    user_id: str,
    ad_id: str,
    user_idx: dict[str, int],
    ad_idx: dict[str, int],
    vote_matrix: np.ndarray,
    user_similarities: np.ndarray | None,
    top_k: int = 20,
) -> float:
    if user_id not in user_idx or ad_id not in ad_idx:
        return 0.0

    ui = user_idx[user_id]
    ai = ad_idx[ad_id]

    if user_similarities is not None:
        sim_row = user_similarities[ui]
    else:
        sim_row = cosine_similarity(vote_matrix[ui:ui + 1], vote_matrix)[0]
        sim_row[ui] = 0.0

    # Top-K most similar neighbors (positive similarity only)
    neighbor_indices = np.argsort(sim_row)[::-1]
    total_weight = 0.0
    weighted_sum = 0.0
    count = 0

    for ni in neighbor_indices:
        if count >= top_k:
            break
        sim = sim_row[ni]
        if sim <= 0:
            break
        neighbor_vote = vote_matrix[ni, ai]
        if neighbor_vote != 0:
            weighted_sum += sim * neighbor_vote
            total_weight += abs(sim)
            count += 1

    if total_weight > 0:
        return weighted_sum / total_weight
    return 0.0


def get_recommended_ads(
    db: Session,
    user_id: str | None,
    limit: int = 20,
    exclude_ids: set[str] | None = None,
) -> list[Ad]:
    exclude_ids = exclude_ids or set()

    all_ads = db.query(Ad).all()
    if not all_ads:
        return []

    # --- Build collaborative data once ---
    cf_user_idx, cf_ad_idx, vote_matrix = _build_user_vote_matrix(db)
    user_similarities = None
    if user_id and user_id in cf_user_idx and vote_matrix.shape[0] > 1:
        user_similarities = cosine_similarity(vote_matrix)

    # --- Unauthenticated / no votes: trending ---
    if user_id is None:
        sorted_ads = sorted(all_ads, key=lambda a: a.score, reverse=True)
        return [a for a in sorted_ads if a.id not in exclude_ids][:limit]

    user_votes = db.query(Vote).filter(Vote.user_id == user_id).all()
    voted_ad_ids = {v.ad_id for v in user_votes}

    if not user_votes:
        sorted_ads = sorted(all_ads, key=lambda a: a.score, reverse=True)
        return [a for a in sorted_ads if a.id not in exclude_ids][:limit]

    # --- Content profile ---
    upvoted_ad_ids = {v.ad_id for v in user_votes if v.vote == 1}
    downvoted_ad_ids = {v.ad_id for v in user_votes if v.vote == -1}
    upvoted_ads = [a for a in all_ads if a.id in upvoted_ad_ids]
    downvoted_ads = [a for a in all_ads if a.id in downvoted_ad_ids]

    downvoted_tags: set[str] = set()
    for ad in downvoted_ads:
        if ad.tags:
            downvoted_tags.update(t.strip().lower() for t in ad.tags.split(","))

    all_tags_set: set[str] = set()
    for ad in all_ads:
        if ad.tags:
            all_tags_set.update(t.strip().lower() for t in ad.tags.split(","))
    all_tags_list = sorted(all_tags_set)

    if upvoted_ads:
        upvoted_vectors = np.array([_tags_to_vector(a.tags, all_tags_list) for a in upvoted_ads])
        user_profile = upvoted_vectors.mean(axis=0)
    else:
        user_profile = np.zeros(len(all_tags_list), dtype=float)

    # --- Score candidates ---
    candidates = [a for a in all_ads if a.id not in exclude_ids and a.id not in voted_ad_ids]
    has_collaborative = user_id in cf_user_idx and vote_matrix.shape[0] > 1
    scored = []

    for ad in candidates:
        ad_vec = _tags_to_vector(ad.tags, all_tags_list)
        content = _compute_content_score(ad, ad_vec, user_profile, downvoted_tags)

        if has_collaborative:
            cf = _collaborative_score(
                user_id, ad.id, cf_user_idx, cf_ad_idx, vote_matrix, user_similarities,
            )
        else:
            cf = 0.0

        # Blend: 60% collaborative, 40% content when collaborative is available;
        # fallback to 100% content when no collaborative signal exists
        if cf != 0.0:
            final = 0.6 * cf + 0.4 * content
        else:
            final = content

        scored.append((ad, final))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [ad for ad, _ in scored[:limit]]
