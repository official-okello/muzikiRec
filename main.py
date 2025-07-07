import streamlit as st
import os
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from fuzzywuzzy import process
import logging

# Set Streamlit config
st.set_page_config(page_title="MuzikiRec", layout="wide", page_icon="🎵")

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Load credentials
load_dotenv()
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

# Initialize Spotify
sp_oauth = SpotifyOAuth(client_id, client_secret, redirect_uri, scope="playlist-modify-public")
spotify = spotipy.Spotify(auth_manager=sp_oauth)

# Internal modules
from loading import import_data, create_decade_column
from exploration import (
    visualize_decade_distribution, plot_sound_features_trends,
    plot_top_genres_trends, generate_genre_wordcloud, generate_artist_wordcloud,
    top_artists_by_song_count, top_artists_by_popularity
)
from clustering import (
    cluster_genres, visualize_genre_clusters,
    cluster_songs, visualize_song_clusters
)
from model import recommend_songs

# Load data once
if "data" not in st.session_state:
    st.session_state["data"], st.session_state["genre_data"], st.session_state["year_data"], st.session_state["artist_data"] = import_data()

# Extract datasets
data = st.session_state["data"]
genre_data = st.session_state["genre_data"]
year_data = st.session_state["year_data"]
artist_data = st.session_state["artist_data"]

# Add decade column if missing
if data is not None and "decade" not in data.columns:
    data = create_decade_column(data)
    st.session_state["data"] = data

# Stop if no data
if data is None or data.empty:
    st.error("Data missing or failed to load.")
    st.stop()

# Sidebar Navigation
st.sidebar.title("🎶 MuzikiRec")
menu = st.sidebar.selectbox("Navigate", ["Home", "Explore Trends", "Clustering", "Get Recommendations"])

# Home Page
if menu == "Home":
    st.header("🎵 Welcome to MuzikiRec")
    st.write("Discover music trends, cluster genres, and get personalized recommendations!")
    st.caption("Data powered by MuzikiRec ✨")

    st.subheader("Dataset Preview")
    selected_cols = st.multiselect("Select Columns to View", data.columns.tolist(), default=data.columns.tolist()[:5])
    st.dataframe(data[selected_cols].head(20))
    st.metric("Total Songs", len(data))

# Explore Trends
elif menu == "Explore Trends":
    st.header("📈 Explore Musical Trends")
    selected_visual = st.selectbox("Choose a visualization:", [
        "Decade Distribution", "Sound Features Trends", "Loudness Trend",
        "Top Genres Trends", "Genre WordCloud", "Artist WordCloud",
        "Top Artists by Song Count", "Top Artists by Popularity"
    ])

    if selected_visual == "Decade Distribution":
        visualize_decade_distribution(data)
    elif selected_visual == "Sound Features Trends":
        plot_sound_features_trends(data)
    elif selected_visual == "Top Genres Trends":
        plot_top_genres_trends(genre_data)
    elif selected_visual == "Genre WordCloud":
        generate_genre_wordcloud(genre_data)
    elif selected_visual == "Artist WordCloud":
        generate_artist_wordcloud(artist_data)
    elif selected_visual == "Top Artists by Song Count":
        top_artists_by_song_count(artist_data)
    elif selected_visual == "Top Artists by Popularity":
        top_artists_by_popularity(artist_data)

# Clustering
elif menu == "Clustering":
    st.header("🎯 Cluster Genres & Songs")

    st.sidebar.subheader("Genre Clustering")
    genre_cluster_count = st.sidebar.slider("Number of Genre Clusters", min_value=3, max_value=15, value=5, key="genre_clusters")

    st.sidebar.subheader("Song Clustering")
    song_cluster_count = st.sidebar.slider("Number of Song Clusters", min_value=5, max_value=30, value=25, key="song_clusters")

    clustered_genres = cluster_genres(genre_data, n_clusters=genre_cluster_count)
    if clustered_genres is not None:
        visualize_genre_clusters(clustered_genres)

    clustered_songs = cluster_songs(data, n_clusters=song_cluster_count)
    if clustered_songs is not None:
        visualize_song_clusters(clustered_songs)

# Recommendations
elif menu == "Get Recommendations":
    st.header("🔍 Find Song Recommendations")

    genre_options = ["All"] + genre_data["genres"].dropna().unique().tolist() if "genres" in genre_data.columns else ["All"]
    decade_options = ["All"] + sorted(data["decade"].dropna().unique().tolist()) if "decade" in data.columns else ["All"]

    genre_filter = st.selectbox("Filter by Genre", genre_options)
    decade_filter = st.selectbox("Filter by Decade", decade_options)

    user_input = st.text_input("Enter a song title")

    if user_input:
        user_song = user_input.strip()
        match_result = process.extractOne(user_song, data["name"].dropna().tolist())

        if match_result:
            validated_song_name = match_result[0]
            logging.info(f"Validated fuzzy match: '{user_song}' → '{validated_song_name}'")
            st.write(f"Generating recommendations for: {validated_song_name}")

            filtered_data = data.copy()

            # Safe merge if columns exist
            if genre_filter != "All":
                if "name" in genre_data.columns and "genres" in genre_data.columns:
                    merged = pd.merge(filtered_data, genre_data[["name", "genres"]], on="name", how="left")
                    filtered_data = merged[merged["genres"] == genre_filter]
                else:
                    st.warning("Genre data can't be filtered. Missing 'name' or 'genres' columns.")

            if decade_filter != "All":
                if "decade" in filtered_data.columns:
                    filtered_data = filtered_data[filtered_data["decade"] == decade_filter]
                else:
                    st.warning("Decade column missing in data.")

            recommended_tracks = recommend_songs(validated_song_name, filtered_data)

            if recommended_tracks is not None and not recommended_tracks.empty:
                st.write("### Recommended Songs")
                selected_songs = st.multiselect(
                    "Select songs for your playlist:",
                    recommended_tracks["name"].tolist(),
                    default=recommended_tracks["name"].tolist()
                )

                playlist_name = st.text_input("Enter Playlist Name", "My MuzikiRec Playlist")

                if st.button("Generate Playlist") and selected_songs:
                    with st.spinner("Creating playlist on Spotify..."):
                        user_id = spotify.current_user()["id"]
                        playlist = spotify.user_playlist_create(user_id, playlist_name, public=True)

                        track_uris = []
                        for song in selected_songs:
                            results = spotify.search(q=song, type="track", limit=1)["tracks"]["items"]
                            if results:
                                track_uris.append(results[0]["uri"])
                            else:
                                logging.warning(f"No URI found for '{song}'.")

                        if track_uris:
                            spotify.playlist_add_items(playlist["id"], track_uris)
                            st.success(
                                f"Playlist '{playlist_name}' created! 🎧 "
                                f"[View on Spotify]({playlist['external_urls']['spotify']})"
                            )
                            logging.info(f"✅ Playlist '{playlist_name}' created with {len(track_uris)} tracks.")
                        else:
                            st.error("Could not retrieve song URIs. Try again.")
            else:
                st.warning("No recommendations found with the selected filters.")
        else:
            st.error(f"No match found for '{user_song}'. Try a different title.")
