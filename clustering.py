import logging
import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer

# Setting up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("music_data.csv")

df = load_data()

# Streamlit UI setup
st.set_page_config(page_title="MuzikiRec Clustering", layout="wide")
st.title("🎶 MuzikiRec Genre & Song Clustering")

# Sidebar settings
st.sidebar.title("Clustering Controls 🎛")
n_clusters = st.sidebar.slider("Select Number of Clusters", 3, 25, 5)

# Cluster genres
def cluster_genres(data, n_clusters):
    required_columns = ['valence', 'energy', 'danceability', 'acousticness']
    if any(col not in data.columns for col in required_columns):
        st.error("Missing essential columns for clustering!")
        return None

    imputer = SimpleImputer(strategy="mean")
    scaler = MinMaxScaler()
    features = scaler.fit_transform(imputer.fit_transform(data[required_columns]))

    kmeans = KMeans(n_clusters=n_clusters, init="k-means++", n_init=10, random_state=42)
    data["cluster"] = kmeans.fit_predict(features)

    return data

df_clustered = cluster_genres(df, n_clusters)

# Visualizing clusters using t-SNE
st.subheader("Genre Clusters Visualization")
if df_clustered is not None:
    tsne = TSNE(n_components=2, perplexity=30, random_state=42)
    tsne_results = tsne.fit_transform(df_clustered[['valence', 'energy', 'danceability', 'acousticness']])

    tsne_df = pd.DataFrame(tsne_results, columns=['x', 'y'])
    tsne_df['cluster'] = df_clustered['cluster']
    tsne_df['genres'] = df_clustered['genres'].fillna("Unknown")

    fig = px.scatter(tsne_df, x='x', y='y', color='cluster', hover_data=['genres'], title="t-SNE Visualization of Genre Clusters")
    st.plotly_chart(fig, use_container_width=True)

# Cluster songs
def cluster_songs(data, n_clusters):
    required_columns = ['valence', 'energy', 'danceability', 'acousticness']
    if any(col not in data.columns for col in required_columns):
        st.error("Missing essential columns for clustering!")
        return None

    imputer = SimpleImputer(strategy="mean")
    scaler = MinMaxScaler()
    features = scaler.fit_transform(imputer.fit_transform(data[required_columns]))

    kmeans = KMeans(n_clusters=n_clusters, init="k-means++", n_init=10, random_state=42)
    data["cluster"] = kmeans.fit_predict(features)

    return data

df_songs_clustered = cluster_songs(df, n_clusters)

# Visualizing song clusters using PCA
st.subheader("Song Clusters Visualization")
if df_songs_clustered is not None:
    pca = PCA(n_components=2, random_state=42)
    pca_results = pca.fit_transform(df_songs_clustered[['valence', 'energy', 'danceability', 'acousticness']])

    pca_df = pd.DataFrame(pca_results, columns=['x', 'y'])
    pca_df['cluster'] = df_songs_clustered['cluster']
    pca_df['song_name'] = df_songs_clustered['name'].fillna("Unknown")

    fig = px.scatter(pca_df, x='x', y='y', color='cluster', hover_data=['song_name'], title="PCA Visualization of Song Clusters")
    st.plotly_chart(fig, use_container_width=True)
