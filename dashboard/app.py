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
# LOAD DATA (optional)
# -----------------------
try:
    movies = pd.read_csv("data/movies_clean.csv")
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

                # -------- MOVIE LIST --------
                for movie in data["recommendations"]:

                    st.markdown("---")

                    # 🎬 Title
                    st.subheader(f"🎥 {movie['movie']}")

                    # ⭐ Score
                    score = float(movie["score"])
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
                # 📊 ANALYTICS SECTION
                # ========================
                st.markdown("## 📊 Insights")

                scores = [float(m["score"]) for m in data["recommendations"]]

                if scores:
                    max_score = max(scores)
                    scores = [s / max_score * 10 for s in scores]

                    # Debug (optional)
                    st.write("Scores:", scores)

                    fig1 = px.bar(
                        x=[f"Movie {i+1}" for i in range(len(scores))],
                        y=scores,
                        title="Recommendation Scores"
                  )

                    st.plotly_chart(fig1, use_container_width=True)

    except Exception as e:
        st.error(f"Something went wrong: {e}")