import os
import logging
import pandas as pd
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load credentials
load_dotenv()
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

# Credential check
if not all([client_id, client_secret, redirect_uri]):
    st.error("❌ Spotify credentials missing. Please check your .env file.")
    raise ValueError("Spotify client ID, secret, and redirect URI are required.")

# Initialize Spotify client
@st.cache_data
def get_spotify_client():
    sp_oauth = SpotifyOAuth(client_id, client_secret, redirect_uri, scope="playlist-modify-public")
    return spotipy.Spotify(auth_manager=sp_oauth)

spotify = get_spotify_client()

# Load dataset
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("datasets/data.csv")
        return df.dropna(subset=["valence", "energy", "danceability", "acousticness"])
    except FileNotFoundError:
        st.error("❌ 'datasets/data.csv' not found. Please check your file path.")
        return pd.DataFrame()

# Search helper
def search_song(song_name, data):
    if "name" not in data.columns:
        st.warning("⚠️ 'name' column not found in dataset.")
        return pd.DataFrame()
    return data[data["name"].str.contains(song_name, case=False, na=False)]

# Recommendation logic
def recommend_songs(song_name, data, num_recommendations=10):
    song = search_song(song_name, data)
    if song.empty:
        st.error(f"Song '{song_name}' not found. Try a different title.")
        return pd.DataFrame()

    features = song.iloc[0][["valence", "energy", "danceability", "acousticness"]]
    if features.isnull().any():
        st.error("Selected song is missing sound features needed for recommendation.")
        return pd.DataFrame()

    recommended = data.copy()
    for feature in features.index:
        if feature in recommended.columns:
            recommended = recommended[
                recommended[feature].between(features[feature] - 0.1, features[feature] + 0.1)
            ]
    return recommended.drop_duplicates().nlargest(num_recommendations, "popularity")