import logging
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from wordcloud import WordCloud

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Tracks per Decade
def visualize_decade_distribution(data):
    st.subheader("Tracks Distribution Across Decades")
    if "decade" in data.columns and not data.empty:
        decade_counts = data.groupby("decade").size().reset_index(name="track_count")
        fig = px.line(decade_counts, x="decade", y="track_count", markers=True,
                      hover_data=["decade", "track_count"], title="Track Count by Decade",
                      template="plotly_white")
        fig.update_layout(xaxis_title="Decade", yaxis_title="Track Count")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("🛑 'decade' column missing or no data found.")

# Feature Trends by Decade
def plot_sound_features_trends(data):
    st.subheader("Sound Feature Trends Over Decades")
    sound_features = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'valence']
    if "decade" not in data.columns or data.empty:
        st.warning("🛑 Cannot generate trends — missing 'decade' column or data is empty.")
        return

    for feature in sound_features:
        if feature in data.columns:
            trend = data.groupby("decade")[feature].mean().reset_index()
            fig = px.line(trend, x="decade", y=feature, markers=True,
                          title=f"{feature.capitalize()} Trend by Decade", template="plotly_white")
            fig.update_layout(xaxis_tickangle=0)
            st.plotly_chart(fig, use_container_width=True)
        else:
            logging.warning(f"Missing feature: {feature}")
            st.warning(f"🛑 '{feature}' column not found.")

# Top Genres - Feature Comparison
def plot_top_genres_trends(genre_data):
    st.subheader("Top Genres Sound Features")
    if genre_data.empty or "genres" not in genre_data.columns:
        st.warning("🛑 No genre data available.")
        return

    top_genres = genre_data["genres"].value_counts().nlargest(10).index.tolist()
    filtered = genre_data[genre_data["genres"].isin(top_genres)]
    for feature in ["valence", "energy", "danceability", "acousticness"]:
        if feature in filtered.columns:
            fig = px.bar(filtered, x="genres", y=feature, color=feature,
                         color_continuous_scale="viridis", title=f"{feature.capitalize()} in Top Genres",
                         template="plotly_white")
            fig.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            logging.warning(f"Missing feature: {feature}")
            st.warning(f"🛑 '{feature}' column not found.")

# Genre Word Cloud
def generate_genre_wordcloud(genre_data):
    st.subheader("Genre Word Cloud")
    if "genres" in genre_data.columns:
        text = ' '.join(genre_data["genres"].dropna().astype(str).tolist())
        wordcloud = WordCloud(width=800, height=400, background_color="white", max_words=40).generate(text)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        ax.set_title("Genres Distribution")
        st.pyplot(fig)
    else:
        st.warning("🛑 'genres' column missing.")

# Artist Word Cloud
def generate_artist_wordcloud(data):
    st.subheader("Artist Word Cloud")
    if "artists" in data.columns:
        text = ' '.join(data["artists"].dropna().astype(str).tolist())
        wordcloud = WordCloud(width=800, height=400, background_color="white", max_words=40).generate(text)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        ax.set_title("Artists Distribution")
        st.pyplot(fig)
    else:
        st.warning("🛑 'artists' column missing.")

# Top Artists by Track Volume
def top_artists_by_song_count(data):
    st.subheader("Top Artists by Song Count")
    if "artists" in data.columns:
        top = data["artists"].value_counts().nlargest(10).reset_index()
        top.columns = ["Artist", "Song Count"]
        fig = px.bar(top, x="Artist", y="Song Count", color="Song Count",
                     title="Top 10 Artists by Song Count", template="plotly_white")
        fig.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("🛑 'artists' column missing.")

# Top Artists by Popularity
def top_artists_by_popularity(data):
    st.subheader("Top Artists by Popularity")
    if "artists" in data.columns and "popularity" in data.columns:
        top = data.groupby("artists")["popularity"].mean().nlargest(10).reset_index()
        fig = px.bar(top, x="artists", y="popularity", color="popularity",
                     title="Top 10 Artists by Popularity", template="plotly_white")
        fig.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("🛑 'artists' or 'popularity' column missing.")
