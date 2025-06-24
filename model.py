import os
import logging
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Configure logging for error tracking
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Load environment variables
load_dotenv()

# Retrieve Spotify credentials
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

# Ensure credentials are set
if not all([client_id, client_secret, redirect_uri]):
    logging.error("Spotify credentials are missing in environment variables.")
    raise ValueError("Spotify client ID, secret, and redirect URI are required.")

# Initialize Spotify API clients
sp_oauth = SpotifyOAuth(client_id, client_secret, redirect_uri, scope="playlist-modify-public")
spotify = spotipy.Spotify(auth_manager=sp_oauth)

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("spotify_music_data.csv")

df = load_data()

# Streamlit UI setup
st.set_page_config(page_title="MuzikiRec Recommendation", layout="wide")
st.title("🎧 MuzikiRec - Song Recommendations & Playlist Creator")

# Sidebar inputs
st.sidebar.title("Search & Customize 🎛")
song_name = st.sidebar.text_input("Enter Song Name")
playlist_name = st.sidebar.text_input("Playlist Name", "My MuzikiRec Playlist")
num_recommendations = st.sidebar.slider("Number of Recommendations", 3, 15, 5)

# Function to search for a song
def search_song(song_name, data):
    return data[data["name"].str.contains(song_name, case=False, na=False)]

# Function to recommend songs
def recommend_songs(song_name, data, num_recommendations):
    song = search_song(song_name, data)
    if song.empty:
        st.error(f"Song '{song_name}' not found. Try a different title.")
        return None
    
    features = song.iloc[0][["valence", "energy", "danceability", "acousticness"]]
    recommended = data.copy()
    
    for feature in features.index:
        recommended = recommended[
            recommended[feature].between(features[feature] - 0.1, features[feature] + 0.1)
        ]

    return recommended.nlargest(num_recommendations, "popularity")

# Fetch recommendations
if song_name:
    recommendations = recommend_songs(song_name, df, num_recommendations)
    if recommendations is not None:
        st.subheader(f"🎵 Recommended Songs Based on '{song_name}'")
        selected_songs = st.multiselect("Select songs for your playlist:", recommendations["name"].tolist(), default=recommendations["name"].tolist())

        # Display song recommendations
        st.dataframe(recommendations[["name", "artist", "popularity"]])

        # Create Spotify playlist
        if st.button("Generate Playlist"):
            user_id = spotify.current_user()["id"]
            playlist = spotify.user_playlist_create(user_id, playlist_name, public=True)
            track_uris = [spotify.search(q=song, type="track", limit=1)["tracks"]["items"][0]["uri"] for song in selected_songs]

            if track_uris:
                spotify.playlist_add_items(playlist["id"], track_uris)
                st.success(f"Playlist '{playlist_name}' created! 🎧 [View on Spotify]({playlist['external_urls']['spotify']})")
            else:
                st.error("Could not retrieve song URIs. Try again.")
