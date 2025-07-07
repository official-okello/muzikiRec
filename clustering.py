import logging
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
import plotly.express as px
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Cluster genres based on sound features
@st.cache_data
def cluster_genres(data, n_clusters=5):
    required = ['valence', 'energy', 'danceability', 'acousticness']
    missing = [col for col in required if col not in data.columns]

    if missing:
        st.error("Missing essential columns for clustering!")
        logging.warning(f"Missing columns for genre clustering: {missing}")
        return None

    features = MinMaxScaler().fit_transform(SimpleImputer(strategy="mean").fit_transform(data[required]))
    kmeans = KMeans(n_clusters=n_clusters, init="k-means++", n_init="auto", random_state=42)
    data = data.copy()
    data["cluster"] = kmeans.fit_predict(features)
    return data

# Visualize genre clusters using t-SNE
@st.cache_data
def visualize_genre_clusters(data):
    st.subheader("Genre Clusters Visualization")

    if data is not None and "cluster" in data.columns:
        if len(data) > 1000:
            data = data.sample(n=1000, random_state=42)
            logging.info("📉 Sampled 1000 rows for t-SNE visualization.")

        tsne = TSNE(n_components=2, perplexity=30, random_state=42)
        embed = tsne.fit_transform(data[['valence', 'energy', 'danceability', 'acousticness']])

        tsne_df = pd.DataFrame(embed, columns=['x', 'y'])
        tsne_df['cluster'] = data['cluster']
        tsne_df['genres'] = data.get('genres', pd.Series(["Unknown"] * len(data))).fillna("Unknown")

        fig = px.scatter(tsne_df, x='x', y='y', color='cluster',
                         hover_data=['genres'], title="t-SNE Visualization of Genre Clusters")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Clustering not performed or missing 'cluster' column.")

# Cluster songs based on sound features
@st.cache_data
def cluster_songs(data, n_clusters=25):
    required = ['valence', 'energy', 'danceability', 'acousticness']
    missing = [col for col in required if col not in data.columns]

    if missing:
        st.error("Missing essential columns for clustering!")
        logging.warning(f"Missing columns for song clustering: {missing}")
        return None

    features = MinMaxScaler().fit_transform(SimpleImputer(strategy="mean").fit_transform(data[required]))
    kmeans = KMeans(n_clusters=n_clusters, init="k-means++", n_init="auto", random_state=42)
    data = data.copy()
    data["cluster"] = kmeans.fit_predict(features)
    return data

# Visualize song clusters using PCA
@st.cache_data
def visualize_song_clusters(data):
    st.subheader("Song Clusters Visualization")

    if data is not None and "cluster" in data.columns:
        pca = PCA(n_components=2, random_state=42)
        embed = pca.fit_transform(data[['valence', 'energy', 'danceability', 'acousticness']])

        pca_df = pd.DataFrame(embed, columns=['x', 'y'])
        pca_df['cluster'] = data['cluster']
        pca_df['song_name'] = data.get('name', pd.Series(["Unknown"] * len(data))).fillna("Unknown")

        fig = px.scatter(pca_df, x='x', y='y', color='cluster',
                         hover_data=['song_name'], title="PCA Visualization of Song Clusters")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Clustering not performed or missing 'cluster' column.")
