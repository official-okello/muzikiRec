import logging
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from wordcloud import WordCloud

# Visualizing distribution of tracks accross diferent decades
def visualize_decade_distribution(data):
    if 'decade' not in data.columns:
        logging.error("Decade column not found in the dataset.")
        return

    # Plotting the distribution of tracks across different decades
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="whitegrid")
    sns.countplot(x="decade", data=data, hue="decade", palette="viridis", legend=False)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.title('Distribution of Tracks Across Different Decades')
    plt.xlabel('Decade')
    plt.ylabel('Number of Tracks')
    plt.show()

# Plotting the trends of various sound features (acousticness, danceability, energy, instrumentalness, liveness, valence) over decades
def plot_sound_features_trends(data):
    if 'decade' not in data.columns:
        logging.error("Decade column not found in the dataset.")
        return

    sound_features = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'valence']
    
    for feature in sound_features:
        if feature in data.columns:
            fig = px.line(data, x='decade', y=feature, markers=True, title=f'Trend of {feature} Over Decades')
            fig.update_layout(
                xaxis_title='Decade',
                yaxis_title=feature,
                xaxis_tickangle=45,
                template='plotly_white'
            )
            fig.show()
        else:
            logging.warning(f"{feature} column not found in the dataset.")

# Plotting the trend of loudness over decades using a line plot
def plot_loudness_trend(data):
    if 'decade' not in data.columns or 'loudness' not in data.columns:
        logging.error("Decade or loudness column not found in the dataset.")
        return

    fig = px.line(data, x='decade', y='loudness', title='Trend of Loudness Over Decades')
    fig.update_layout(
        xaxis_title='Decade',
        yaxis_title='Loudness (dB)',
        xaxis_tickangle=45,
        template='plotly_white'
    )
    fig.show()

# Identifying the top 10 genres based on popularity and plotting the trends of various sound features (valence, energy, danceability, acousticness) for these genres using a grouped bar chart
def plot_top_genres_trends(genre_data):
    if genre_data is None or genre_data.empty:
        logging.error("Genre data is not available.")
        return
    if 'genres' not in genre_data.columns:
        logging.error("Genres column not found in the genre data.")
        return
    if not all(feature in genre_data.columns for feature in ['valence', 'energy', 'danceability', 'acousticness']):
        logging.error("One or more sound feature columns not found in the genre data.")
        return
    
    # Filtering top 10 genres based on their count
    logging.info("Filtering top 10 genres based on their count...")
    top_genres = genre_data['genres'].value_counts().nlargest(10).index.tolist()
    filtered_genre_data = genre_data[genre_data['genres'].isin(top_genres)]

    sound_features = ['valence', 'energy', 'danceability', 'acousticness']
    
    for feature in sound_features:
        if feature in filtered_genre_data.columns:
            fig = px.bar(filtered_genre_data, x='genres', y=feature, color=feature, color_continuous_scale='viridis',
             title=f'Trend of {feature} for Top 10 Genres')
            fig.update_layout(
                xaxis_title='Genre',
                yaxis_title=feature,
                xaxis_tickangle=45,
                template='plotly_white'
            )
            fig.show()
        else:
            logging.warning(f"{feature} column not found in the genre data.")

# Generating a word cloud of the genres present in the data
def generate_genre_wordcloud(genre_data):
    if genre_data is None or genre_data.empty:
        logging.error("Genre data is not available.")
        return
    if 'genres' not in genre_data.columns:
        logging.error("Genres column not found in the genre data.")
        return

    # Concatenating all genres into a single string
    comment_words = ' '.join(genre_data['genres'].dropna().astype(str).tolist())
    
    # Generating the word cloud
    stopwords = set(['and', 'the', 'of', 'in', 'to', 'a', 'is', 'for', 'with', 'on', 'as', 'by', 'this', 'that'])
    wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords=stopwords, max_words=40).generate(comment_words)
    
    # Displaying the word cloud
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Genres')
    plt.show()

# Generating a word cloud of the artists present in the data
def generate_artist_wordcloud(artist_data):
    if artist_data is None or artist_data.empty:
        logging.error("Artist data is not available.")
        return
    if 'artists' not in artist_data.columns:
        logging.error("Artists column not found in the artist data.")
        return

    # Concatenating all artists into a single string
    comment_words = ' '.join(artist_data['artists'].dropna().astype(str).tolist())
    
    # Generating the word cloud
    stopwords = set(['and', 'the', 'of', 'in', 'to', 'a', 'is', 'for', 'with', 'on', 'as', 'by', 'this', 'that'])
    wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords=stopwords, max_words=40).generate(comment_words)
    
    # Displaying the word cloud
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Artists')
    plt.show()

# Identifying the top 10 artists with the most songs produced and displaying the count and artist name
def top_artists_by_song_count(artist_data):
    if artist_data is None or artist_data.empty:
        logging.error("Artist data is not available.")
        return
    if 'artists' not in artist_data.columns:
        logging.error("Artists column not found in the artist data.")
        return

    # Counting the number of songs for each artist by artist name
    top10_most_song_produced_artists = artist_data['artists'].value_counts().nlargest(10).sort_values(ascending=False)
    top10_most_song_produced_artists = top10_most_song_produced_artists.reset_index()
    
    # Displaying the top artists by song count
    print("\nTop 10 Artists by Song Count:")
    print(top10_most_song_produced_artists)

# Identifying the top 10 artists with the highest popularity score and displaying the popularity score and artist name
def top_artists_by_popularity(artist_data):
    if artist_data is None or artist_data.empty:
        logging.error("Artist data is not available.")
        return
    if 'artists' not in artist_data.columns or 'popularity' not in artist_data.columns:
        logging.error("Artists or popularity column not found in the artist data.")
        return

    # Counting the number of songs for each artist by popularity
    top10_popular_artists = artist_data.groupby('artists')['popularity'].mean().nlargest(10).sort_values(ascending=False)
    top10_popular_artists = top10_popular_artists.reset_index()
    
    # Displaying the top artists by popularity
    print("\nTop 10 Artists by Popularity Score:")
    print(top10_popular_artists)