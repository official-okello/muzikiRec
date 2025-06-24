import streamlit as st

st.set_page_config(page_title="MuzikiRec", layout="wide", page_icon="🎵")

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from dotenv import load_dotenv
import os
from fuzzywuzzy import process
from loading import import_data, create_decade_column
from exploration import (
    visualize_decade_distribution, plot_sound_features_trends, plot_loudness_trend,
    plot_top_genres_trends, generate_genre_wordcloud, generate_artist_wordcloud,
    top_artists_by_song_count, top_artists_by_popularity
)
from clustering import cluster_genres, visualize_clusters, cluster_songs, visualize_song_clusters
from model import recommend_songs, get_spotify_track

# Load environment variables for Spotify API
load_dotenv()
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

# Initialize Spotify API client
sp_oauth = SpotifyOAuth(client_id, client_secret, redirect_uri, scope="playlist-modify-public")
spotify = spotipy.Spotify(auth_manager=sp_oauth)

# Sidebar Navigation
st.sidebar.image("logo.png", width=200)
st.sidebar.title("🎶 MuzikiRec")
menu = st.sidebar.selectbox("Navigate", ["Home", "Explore Trends", "Clustering", "Get Recommendations"])

# Load datasets into session state
if "data" not in st.session_state:
    st.session_state["data"], st.session_state["genre_data"], st.session_state["year_data"], st.session_state["artist_data"] = import_data()

data = st.session_state["data"]
genre_data = st.session_state["genre_data"]
year_data = st.session_state["year_data"]
artist_data = st.session_state["artist_data"]

# Stop execution if data isn't loaded
if data is None or data.empty:
    st.error("Data missing or failed to load.")
    st.stop()

# Home Section
if menu == "Home":
    st.header("🎵 Welcome to MuzikiRec")
    st.write("Discover music trends, cluster genres, and get personalized recommendations!")

    st.subheader("Dataset Preview")
    selected_cols = st.multiselect("Select Columns to View", data.columns.tolist(), default=data.columns.tolist()[:5])
    st.dataframe(data[selected_cols].head(20))

    data = create_decade_column(data)
    st.session_state["data"] = data

# Explore Trends Section
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
    elif selected_visual == "Loudness Trend":
        plot_loudness_trend(data)
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

# Clustering Section
elif menu == "Clustering":
    st.header("🎯 Cluster Genres & Songs")

    genre_data = cluster_genres(genre_data, n_clusters=5)
    if genre_data is not None:
        visualize_clusters(genre_data)

    song_data = cluster_songs(data, n_clusters=25)
    if song_data is not None:
        visualize_song_clusters(song_data)

# Recommendations Section
elif menu == "Get Recommendations":
    st.header("🔍 Find Song Recommendations")

    genre_filter = st.selectbox("Filter by Genre", ["All"] + genre_data["genres"].unique().tolist())
    decade_filter = st.selectbox("Filter by Decade", ["All"] + sorted(data["decade"].unique().tolist()))

    user_input = st.text_input("Enter at least 2 song titles separated by a comma (,)", "")

    if user_input:
        user_songs = [song.strip() for song in user_input.split(',') if song.strip()]
        validated_songs = [process.extractOne(song, data["name"].dropna().tolist())[0] for song in user_songs if process.extractOne(song, data["name"].dropna().tolist())]

        if len(validated_songs) < 2:
            st.error("Please provide at least 2 valid song titles.")
        else:
            st.write(f"Generating recommendations for: {validated_songs}")
            recommended_tracks = recommend_songs(validated_songs, data)

            if recommended_tracks:
                st.write("### Recommended Songs")
                selected_songs = st.multiselect("Select songs for your playlist:", [track["name"] for track in recommended_tracks], default=[track["name"] for track in recommended_tracks])

                # Create Spotify playlist
                playlist_name = st.text_input("Enter Playlist Name", "My MuzikiRec Playlist")

                if st.button("Generate Playlist"):
                    user_id = spotify.current_user()["id"]
                    playlist = spotify.user_playlist_create(user_id, playlist_name, public=True)
                    track_uris = [spotify.search(q=song, type="track", limit=1)["tracks"]["items"][0]["uri"] for song in selected_songs]

                    if track_uris:
                        spotify.playlist_add_items(playlist["id"], track_uris)
                        st.success(f"Playlist '{playlist_name}' created! 🎧 [View on Spotify]({playlist['external_urls']['spotify']})")
                    else:
                        st.error("Could not retrieve song URIs. Try again.")
