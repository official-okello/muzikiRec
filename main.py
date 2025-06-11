import logging
import pandas as pd
from loading import import_data, display_data, data_info, create_decade_column
from exploration import (
    visualize_decade_distribution, plot_sound_features_trends, plot_loudness_trend,
    plot_top_genres_trends, generate_genre_wordcloud, generate_artist_wordcloud,
    top_artists_by_song_count, top_artists_by_popularity
)
from clustering import (
    cluster_genres, assign_cluster_labels, visualize_clusters,
    cluster_songs, visualize_song_clusters
)

def main():
    print("Welcome to MuzikiRec - Music Recommendation System")
    logging.info("Importing data...")

    # Import data
    data, genre_data, year_data, artist_data = import_data()

    if data is not None and not data.empty:
        display_data(data=data)
        data_info(data=data, genre_data=genre_data)

        # Creating decade column
        data = create_decade_column(data)
        display_data(data=data)

        # Displaying genre, year, and artist data
        display_data(genre_data=genre_data, year_data=year_data, artist_data=artist_data)

        # **Clustering Process**
        logging.info("Applying clustering to genre and song data...")
        
        # Genre Clustering
        genre_data = cluster_genres(genre_data, n_clusters=5)
        if genre_data is not None:
            assigned_labels = assign_cluster_labels(genre_data)
            if assigned_labels is not None:
                logging.info("Cluster labels assigned successfully.")
        
            visualize_clusters(genre_data)

        # Song Clustering
        song_data = cluster_songs(data, n_clusters=25)
        if song_data is not None:
            visualize_song_clusters(song_data)

        # **Visualizations and insights**
        visualize_decade_distribution(data)
        plot_sound_features_trends(data)
        plot_loudness_trend(data)
        plot_top_genres_trends(genre_data)
        generate_genre_wordcloud(genre_data)
        generate_artist_wordcloud(artist_data)
        top_artists_by_song_count(artist_data)
        top_artists_by_popularity(artist_data)

    else:
        logging.error("No data to display. Please check the import process.")

if __name__ == "__main__":
    main()