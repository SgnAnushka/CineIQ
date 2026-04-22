import streamlit as st
import requests
import plotly.express as px
import pandas as pd

# -----------------------
# CONFIG
# -----------------------
st.set_page_config(page_title="CINEIQ 🎬", layout="wide")
st.title("🎬 CINEIQ - Smart Movie Recommender")

# -----------------------
# LOAD DATA
# -----------------------
try:
    movies = pd.read_csv("../data/movies_clean.csv")
except:
    movies = pd.DataFrame()

# -----------------------
# INPUT
# -----------------------
user_id = st.number_input("Enter User ID", min_value=1, step=1)

# =========================
# 🎯 RECOMMENDATIONS
# =========================
if st.button("Get Recommendations 🚀"):

    try:
        rec_url = f"http://127.0.0.1:8000/recommend?user_id={user_id}"
        response = requests.get(rec_url)

        if response.status_code != 200:
            st.error("❌ API Error")
        else:
            data = response.json()

            if "error" in data:
                st.error(data["error"])
            else:
                st.markdown("## 🎯 Recommended Movies")

                for movie in data["recommendations"]:

                    st.markdown("---")

                    # 🎬 Title
                    st.subheader(f"🎥 {movie['movie']}")

                    # ⭐ Score
                    score = movie["score"]
                    st.markdown(f"⭐ **Score:** {score:.2f}")

                    # 📊 Progress bar
                    st.progress(min(score / 10, 1.0))

                    # 🔥 Badge
                    if score > 5:
                        st.success("🔥 Highly Recommended")
                    elif score > 3:
                        st.info("👍 Good Match")
                    else:
                        st.warning("🤔 Worth Exploring")

                    # 🤖 Explanation
                    st.markdown("### 🤖 Why this recommendation?")
                    for r in movie.get("reason", []):
                        st.markdown(f"👉 {r}")

                # ========================
                # 📊 ANALYTICS
                # ========================
                st.markdown("## 📊 Insights")

                scores = [m["score"] for m in data["recommendations"]]

                fig1 = px.histogram(
                    scores,
                    nbins=10,
                    title="Score Distribution"
                )
                st.plotly_chart(fig1, use_container_width=True)

                # ---- GENRES ----
                if not movies.empty and "genres" in movies.columns:

                    movie_titles = [m["movie"] for m in data["recommendations"]]
                    subset = movies[movies["title"].isin(movie_titles)]

                    all_genres = []
                    for g in subset["genres"]:
                        if isinstance(g, str):
                            all_genres.extend(g.split("|"))

                    if all_genres:
                        genre_df = pd.DataFrame(all_genres, columns=["genre"])
                        genre_counts = genre_df["genre"].value_counts().reset_index()
                        genre_counts.columns = ["genre", "count"]

                        fig2 = px.bar(
                            genre_counts,
                            x="genre",
                            y="count",
                            title="Top Genres"
                        )
                        st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"Something went wrong: {e}")