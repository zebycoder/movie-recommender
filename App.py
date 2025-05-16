import streamlit as st
import pickle
import pandas as pd
import requests


def fetch_poster(movie_id):
    try:
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=98d629168214fba4640c096223c3b08d&language=en-US'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'poster_path' in data and data['poster_path']:
            return f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
        return None
    except:
        return None


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies = []
    recommended_movie_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movie_posters


# Load data
movies_dict = pickle.load(open('movies.pk1', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pk1', 'rb'))

# Streamlit UI
st.title("Movie Recommender System")

selected_movie_name = st.selectbox(
    "Select a movie to get recommendations:",
    movies['title'].values,
    key="movie_selectbox"  # Added unique key
)

if st.button('Recommend', key="recommend_button"):  # Added unique key
    names, posters = recommend(selected_movie_name)

    # Display recommendations safely
    if names and posters:  # Check if we have both names and posters
        cols = st.columns(min(5, len(names)))
        for i in range(min(5, len(names))):
            with cols[i]:
                st.text(names[i])
                if i < len(posters):  # Ensure we don't exceed posters list
                    st.image(posters[i] if posters[i] else "default_poster.jpg")
                else:
                    st.image("default_poster.jpg")