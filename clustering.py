from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
import logging
from sklearn.manifold import TSNE
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer

# Setting up logging to handle errors and information
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Clustering function to group similar genres and assign cluster labels
def cluster_genres(genre_data, n_clusters=5):
    if genre_data is None or genre_data.empty:
        logging.error("Genre data is not available for clustering.")
        return None

    required_columns = ['valence', 'energy', 'danceability', 'acousticness']
    missing_cols = [col for col in required_columns if col not in genre_data.columns]
    if missing_cols:
        logging.error(f"Missing columns in genre data: {missing_cols}")
        return None

    # Selecting features and handling NaN values
    features = genre_data[required_columns]
    imputer = SimpleImputer(strategy="mean")
    features_imputed = imputer.fit_transform(features)

    # Standardizing features
    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(features_imputed)

    # Applying KMeans clustering with optimized initialization
    kmeans = KMeans(n_clusters=n_clusters, init="k-means++", n_init=10, random_state=42)
    genre_data['cluster'] = kmeans.fit_predict(scaled_features)

    logging.info(f"Clustering completed with {n_clusters} clusters.")
    return genre_data

# Assigning cluster labels to genre data
def assign_cluster_labels(genre_data):
    if genre_data is None or 'cluster' not in genre_data.columns:
        logging.error("Genre data is not available or does not contain cluster labels.")
        return None

    cluster_labels = genre_data.groupby('cluster')['genres'].apply(lambda x: ', '.join(x.unique())).reset_index()
    cluster_labels.columns = ['cluster', 'genres']

    logging.info("Cluster labels assigned to genres.")
    return cluster_labels

# Visualizing clusters using t-SNE
def visualize_clusters(genre_data):
    if genre_data is None or 'cluster' not in genre_data.columns:
        logging.error("Genre data is not available or does not contain cluster labels.")
        return None

    required_cols = ['valence', 'energy', 'danceability', 'acousticness']
    missing_cols = [col for col in required_cols if col not in genre_data.columns]
    if missing_cols:
        logging.error(f"Missing columns in genre data: {missing_cols}")
        return None

    # Standardizing and imputing missing values
    scaler = MinMaxScaler()
    imputer = SimpleImputer(strategy="mean")
    features_scaled = scaler.fit_transform(imputer.fit_transform(genre_data[required_cols]))

    # Applying PCA before t-SNE if dataset has high dimensionality
    if features_scaled.shape[1] > 50:
        logging.info(f"Applying PCA to reduce {features_scaled.shape[1]} features before t-SNE.")
        pca = PCA(n_components=0.95, random_state=42)
        features_reduced = pca.fit_transform(features_scaled)

        logging.info(f"PCA Explained Variance: {sum(pca.explained_variance_ratio_):.2f}")
    else:
        features_reduced = features_scaled

    # Subsampling for efficient t-SNE execution
    subset_size = min(5000, features_reduced.shape[0])
    tsne = TSNE(n_components=2, perplexity=min(30, subset_size // 10), random_state=42)
    tsne_results = tsne.fit_transform(features_reduced[:subset_size])

    tsne_df = pd.DataFrame(tsne_results, columns=['x', 'y'])
    tsne_df['cluster'] = genre_data['cluster'].iloc[:subset_size]
    tsne_df['genres'] = genre_data['genres'].fillna("Unknown").iloc[:subset_size]

    fig = px.scatter(tsne_df, x='x', y='y', color='cluster', hover_data=['genres'], title='t-SNE Visualization of Genre Clusters')
    fig.update_layout(template='plotly_white')
    fig.show()

    logging.info("Clusters visualized successfully.")
    return fig

# Clustering songs with optimized KMeans
def cluster_songs(data, n_clusters=25):
    if data is None or data.empty:
        logging.error("Song data is not available for clustering.")
        return None

    required_columns = ['valence', 'energy', 'danceability', 'acousticness']
    missing_cols = [col for col in required_columns if col not in data.columns]
    if missing_cols:
        logging.error(f"Missing columns in song data: {missing_cols}")
        return None

    imputer = SimpleImputer(strategy="mean")
    features_imputed = imputer.fit_transform(data[required_columns])
    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(features_imputed)

    kmeans = KMeans(n_clusters=n_clusters, init="k-means++", n_init=10, random_state=42)
    data['cluster'] = kmeans.fit_predict(scaled_features)

    logging.info(f"Clustering completed with {n_clusters} clusters.")
    return data

# Visualizing song clusters using PCA
def visualize_song_clusters(data):
    if data is None or 'cluster' not in data.columns:
        logging.error("Song data is not available or does not contain cluster labels.")
        return None

    required_cols = ['valence', 'energy', 'danceability', 'acousticness']
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        logging.error(f"Missing columns in song data: {missing_cols}")
        return None

    imputer = SimpleImputer(strategy="mean")
    features_imputed = imputer.fit_transform(data[required_cols])
    scaler = MinMaxScaler()
    features_scaled = scaler.fit_transform(features_imputed)

    logging.info("Applying PCA for dimensionality reduction.")
    pca = PCA(n_components=2, random_state=42)
    pca_results = pca.fit_transform(features_scaled)

    pca_df = pd.DataFrame(pca_results, columns=['x', 'y'])
    pca_df['cluster'] = data['cluster']
    pca_df['song_name'] = data['name'].fillna("Unknown")

    fig = px.scatter(pca_df, x='x', y='y', color='cluster', hover_data=['song_name'], title='PCA Visualization of Song Clusters')
    fig.update_layout(template='plotly_white')
    fig.show()

    logging.info("Song clusters visualized successfully.")
    return fig