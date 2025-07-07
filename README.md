```markdown
# 🎶 MuzikiRec

_MuzikiRec_ is a Streamlit-powered music intelligence app that lets users explore sonic trends, visualize genre clusters, and generate personalized playlists using audio features and Spotify integration.

Built for data lovers, music creatives, and curious minds alike, MuzikiRec transforms raw music datasets into interactive insights and real-time playlist creation.

---

## 🚀 Features

- **Trend Exploration:** 
  - Visualize feature evolution across decades.
  - Discover top genres and artists by sound and popularity.
  - Generate genre and artist word clouds.

- **Clustering Engine:**
  - Cluster genres and songs by acoustic similarity.
  - Dynamic t-SNE and PCA plots for genre/song embeddings.

- **Recommendations:**
  - Input any song title → get smart recommendations based on feature proximity.
  - Filter by genre and decade.
  - Export selected songs into a public Spotify playlist.

---

## 🛠 Tech Stack

| Layer          | Tools Used                                               |
|----------------|----------------------------------------------------------|
| Frontend UI    | [Streamlit](https://streamlit.io)                        |
| Data Handling  | Pandas, NumPy                                            |
| Clustering     | KMeans, MinMaxScaler, PCA, t-SNE                         |
| Visualizations | Plotly, Seaborn, Matplotlib                              |
| Spotify API    | Spotipy + Spotify OAuth                                  |
| Utils          | FuzzyWuzzy for smart text matching                       |

---

## 📁 Project Structure

```
music-rec-system/
├── main.py                  # Streamlit entry point
├── loading.py              # Dataset loading & transformation
├── model.py                # Recommendation logic & playlist creation
├── clustering.py           # Clustering models & visualizations
├── exploration.py          # Trend analysis & wordclouds
├── datasets/               # CSV files for songs, genres, artists
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🔧 Setup Guide

1. **Clone the Repository**

```bash
git clone https://github.com/yourusername/muzikirec.git
cd muzikirec
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Add `.env` File**

Create a `.env` with the following variables:

```ini
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8501
```

4. **Run the App**

```bash
streamlit run main.py
```

---

## 🎤 Sample Dataset

Place your song and genre data in the `datasets/` folder. Expected files include:

- `data.csv`
- `data_by_genres.csv`
- `data_by_year.csv`
- `data_by_artist.csv`

Make sure key columns like `valence`, `energy`, `danceability`, `acousticness`, and `name` are present.

---

## 🙌 Contributions Welcome

Whether it's new clustering ideas, better Spotify UX, or visual storytelling, all contributions are welcome!

1. Fork the repo.
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push and open a Pull Request.

---

## 📜 License

Distributed under the MIT License.

---

## ✨ Credits

Built by [Julius](https://www.linkedin.com/in/julius-okello-3889b2270/)  
Inspired by data, driven by rhythm.
```
