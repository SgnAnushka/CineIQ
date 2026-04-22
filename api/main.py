from fastapi import FastAPI
import joblib
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# =======================
# LOAD MODELS & DATA
# =======================

svd = joblib.load("../models/svd.pkl")
tfidf_matrix = joblib.load("../models/tfidf_matrix.pkl")
indices = joblib.load("../models/indices.pkl")  # movieId → index

movies = pd.read_csv("../data/movies_clean.csv")

# ensure correct column name
if 'title' not in movies.columns:
    title_col = [c for c in movies.columns if 'title' in c.lower()][0]
    movies.rename(columns={title_col: 'title'}, inplace=True)
data = pd.read_csv("../data/processed_data.csv")

# =======================
# NORMALIZATION
# =======================

def normalize(x):
    return str(x).lower().strip()

movie_dict = dict(zip(movies['movieId'], movies['title']))

title_to_id = {
    normalize(title): movie_id
    for title, movie_id in zip(movies['title'], movies['movieId'])
}

# =======================
# HELPERS
# =======================

def get_user_likes(user_id):
    user_data = data[data['userId'] == user_id]
    liked = user_data[user_data['rating'] >= 3.5]

    merged = liked.merge(movies, on='movieId')

    if merged.empty:
        return []

    # auto-detect title column
    title_col = [col for col in merged.columns if 'title' in col.lower()][0]

    return merged[title_col].dropna().tolist()


def get_similar_movies(title, top_n=10):
    movie_id = title_to_id.get(normalize(title))

    if movie_id is None:
        return []

    idx = indices.get(movie_id)

    if idx is None:
        return []

    sim_scores = cosine_similarity(
        tfidf_matrix[idx:idx+1], tfidf_matrix
    ).flatten()

    sim_indices = sim_scores.argsort()[-top_n:][::-1]

    return movies.iloc[sim_indices]['title'].tolist()


def get_sentiment_score(movie_id):
    movie_data = data[data['movieId'] == movie_id]

    if movie_data.empty:
        return 0

    avg_rating = movie_data['rating'].mean()

    return (avg_rating - 3) / 2


# =======================
# EXPLAINABILITY
# =======================

def explain_recommendation(user_id, movie_title, score):

    reasons = []

    movie_id = title_to_id.get(normalize(movie_title))
    if movie_id is None:
        return ["Popular among users with similar taste"]

    target_idx = indices.get(movie_id)
    if target_idx is None:
        return ["Popular among users with similar taste"]

    user_likes = get_user_likes(user_id)

    best_match = None
    best_score = 0

    # ---------- CONTENT ----------
    for liked_movie in user_likes[:5]:

        liked_id = title_to_id.get(normalize(liked_movie))
        if liked_id is None:
            continue

        liked_idx = indices.get(liked_id)
        if liked_idx is None:
            continue

        sim = cosine_similarity(
            tfidf_matrix[target_idx:target_idx+1],
            tfidf_matrix[liked_idx:liked_idx+1]
        )[0][0]

        if sim > best_score:
            best_score = sim
            best_match = liked_movie

    if best_match and best_score > 0.3:
        reasons.append(f"Similar to '{best_match}'")

    # ---------- SENTIMENT ----------
    sentiment = get_sentiment_score(movie_id)

    if sentiment > 0.5:
        reasons.append("Highly rated by audience")
    elif sentiment > 0.2:
        reasons.append("Generally liked by viewers")

    # ---------- FALLBACK ----------
    if not reasons:
        reasons.append("Matches your overall preferences")

    # 👉 LIMIT TO 2 REASONS ONLY
    # ---------- ENSURE 2 REASONS ----------
    if len(reasons) == 1:
        reasons.append("Popular among users with similar taste")

    if len(reasons) == 0:
        reasons = [
            "Matches your overall preferences",
            "Popular among users with similar taste"
    ]

    return reasons[:2]

# =======================
# HYBRID ENGINE
# =======================

def hybrid_recommend(user_id):

    movie_ids = movies['movieId'].tolist()

    # ---- SVD ----
    svd_scores = {}
    for movie_id in movie_ids[:500]:
        pred = svd.predict(user_id, movie_id)
        svd_scores[movie_id] = pred.est

    # ---- USER LIKES ----
    user_likes = get_user_likes(user_id)

    # ---- CONTENT ----
    content_scores = {}

    for movie in user_likes[:5]:
        similar = get_similar_movies(movie, top_n=10)

        for rank, m in enumerate(similar):
            content_scores[m] = content_scores.get(m, 0) + (10 - rank)

    # ---- COMBINE ----
    results = []

    for movie_id, svd_score in svd_scores.items():

        title = movie_dict.get(movie_id)
        if not title:
            continue

        content_score = content_scores.get(title, 0)

        sentiment = get_sentiment_score(movie_id)
        sentiment_scaled = sentiment * 5

        final_score = (
            0.4 * svd_score +
            0.4 * content_score +
            0.2 * sentiment_scaled
        )

        results.append((title, final_score))

    # ---- UNIQUE ----
    unique = {}
    for t, s in results:
        unique[t] = max(s, unique.get(t, 0))

    results = list(unique.items())
    results = sorted(results, key=lambda x: x[1], reverse=True)[:10]

    return results


# =======================
# ROUTES
# =======================

@app.get("/")
def home():
    return {"message": "CINEIQ running 🚀"}


@app.get("/recommend")
def recommend(user_id: int):
    try:
        results = hybrid_recommend(user_id)

        return {
            "recommendations": [
                {
                    "movie": m,
                    "score": float(s),
                    "reason": explain_recommendation(user_id, m, s)
                }
                for m, s in results
            ]
        }

    except Exception as e:
        print("ERROR:", e)
        return {"error": str(e)}
@app.get("/similar")
def similar(movie_title: str):

    movie_id = title_to_id.get(normalize(movie_title))

    if movie_id is None:
        return {"error": "Movie not found"}

    idx = indices.get(movie_id)

    if idx is None:
        return {"error": "Movie not found in similarity index"}

    sim_scores = cosine_similarity(
        tfidf_matrix[idx:idx+1],
        tfidf_matrix
    ).flatten()

    sim_indices = sim_scores.argsort()[-11:][::-1]

    similar_movies = []

    for i in sim_indices:
        title = movies.iloc[i]["title"]
        if normalize(title) != normalize(movie_title):
            similar_movies.append(title)

    return {
        "input_movie": movie_title,
        "similar_movies": similar_movies[:10]
    }