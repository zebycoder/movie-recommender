import streamlit as st
import pickle
import pandas as pd
import requests
import gdown
import os
import patoolib

# --- MUST BE FIRST COMMAND ---
st.set_page_config(layout="wide")

# --- Download and Combine Split Files ---
if not os.path.exists('similarity.pk1'):
    try:
        st.warning("Downloading similarity data (2 parts)...")

        # Part 1 Download
        part1_id = "121yVL22YIJQD9uzwbtfvDrufgAexDWiT"
        gdown.download(f"https://drive.google.com/uc?id={part1_id}", "similarity.part1.rar", quiet=False)

        # Part 2 Download
        part2_id = "1sx-yf3V2yWJmm405fUavSyorWoA3P5ka"
        gdown.download(f"https://drive.google.com/uc?id={part2_id}", "similarity.part2.rar", quiet=False)

        # Combine and Extract
        st.warning("Combining parts...")
        patoolib.extract_archive("similarity.part1.rar", outdir=".")

        # Cleanup
        os.remove("similarity.part1.rar")
        os.remove("similarity.part2.rar")
        st.success("Data ready!")

    except Exception as e:
        st.error(f"Setup failed: {str(e)}")
        st.stop()

# --- Load Data ---
try:
    movies_dict = pickle.load(open('movies.pk1', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pk1', 'rb'))
except Exception as e:
    st.error(f"Load error: {str(e)}")
    st.stop()


# --- Get Posters ---
def fetch_poster(movie_id):
    try:
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            params={'api_key': '98d629168214fba4640c096223c3b08d'}
        )
        data = response.json()
        return f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get('poster_path') else None
    except:
        return None


# --- Recommendations ---
def recommend(movie):
    try:
        idx = movies[movies['title'] == movie].index[0]
        distances = similarity[idx]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        return [(movies.iloc[i[0]].title, fetch_poster(movies.iloc[i[0]].movie_id)) for i in movies_list]
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []


# --- UI ---
st.title("🎬 Movie Recommender System")

selected = st.selectbox("Choose a movie:", movies['title'].values)

if st.button('🍿 Get Recommendations'):
    recommendations = recommend(selected)
    if recommendations:
        cols = st.columns(5)
        for i, (title, poster) in enumerate(recommendations):
            with cols[i]:
                st.text(title)
                st.image(poster if poster else "https://via.placeholder.com/300x450?text=No+Poster")
    else:
        st.warning("No recommendations generated")

# --- Styling ---
st.markdown("""
<style>
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
    }
    .stSelectbox label {
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)
