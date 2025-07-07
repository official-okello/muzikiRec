import os
import logging
import pandas as pd
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load credentials
load_dotenv()
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

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

# Interactive playlist builder (optional)
def fetch_recommendations(song_name, df, num_recommendations):
    if not df.empty and song_name:
        recommendations = recommend_songs(song_name, df, num_recommendations)
        if recommendations is not None and not recommendations.empty:
            st.subheader(f"🎵 Recommended Songs Based on '{song_name}'")

            expected_cols = ["name", "artist", "popularity"]
            display_cols = [col for col in expected_cols if col in recommendations.columns]
            st.dataframe(recommendations[display_cols] if display_cols else recommendations.head(10))

            selected_songs = st.multiselect(
                "Select songs for your playlist:",
                recommendations["name"].tolist(),
                default=recommendations["name"].tolist()
            )

            playlist_name = st.text_input("Enter Playlist Name", "My MuzikiRec Playlist")

            if st.button("Generate Playlist") and selected_songs:
                user_id = spotify.current_user()["id"]
                playlist = spotify.user_playlist_create(user_id, playlist_name, public=True)

                track_uris = []
                for song in selected_songs:
                    results = spotify.search(q=song, type="track", limit=1)["tracks"]["items"]
                    if results:
                        track_uris.append(results[0]["uri"])

                if track_uris:
                    spotify.playlist_add_items(playlist["id"], track_uris)
                    st.success(
                        f"Playlist '{playlist_name}' created with {len(track_uris)} tracks! 🎧 "
                        f"[Open on Spotify]({playlist['external_urls']['spotify']})"
                    )
                    logging.info(f"✅ Playlist '{playlist_name}' created with {len(track_uris)} songs.")
                else:
                    st.error("Could not retrieve song URIs. Try again.")
        else:
            st.warning("No matching recommendations found.")

# Prevent automatic execution when imported
if __name__ == "__main__":
    df = load_data()
    song_name = st.sidebar.text_input("Enter Song Name")
    num_recommendations = st.sidebar.slider("Number of Recommendations", 3, 15, 5)
    fetch_recommendations(song_name, df, num_recommendations)
