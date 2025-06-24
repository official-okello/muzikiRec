import logging
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
from wordcloud import WordCloud
import pandas as pd

# Setting up logging to handle errors
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("C:/Users/USER/OneDrive/Desktop/DS_GOMYCODE/ML/scripts/Music Recommendation System/datasets/data.csv")

df = load_data()

# Streamlit page setup
st.title("🎶 MuzikiRec Exploration Dashboard")

# Sidebar Filters
st.sidebar.title("Filters 🎛")
selected_decade = st.sidebar.selectbox("Select Decade", sorted(df["decade"].unique()))
selected_genre = st.sidebar.selectbox("Select Genre", df["genres"].unique())
popularity_range = st.sidebar.slider("Popularity", 0, 100, (30, 80))

# Filter data based on selections
filtered_df = df[
    (df["decade"] == selected_decade) & 
    (df["genres"] == selected_genre) & 
    (df["popularity"].between(*popularity_range))
]

# Visualizing Decade Distribution
st.subheader("Tracks Distribution Across Decades")
if 'decade' in df.columns:
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.countplot(x="decade", data=df, hue="decade", palette="viridis", legend=False, ax=ax)
    ax.set_title("Tracks Distribution Across Decades")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.warning("Decade column not found in dataset.")

# Trend of Sound Features Over Decades
st.subheader("Sound Feature Trends Over Decades")
sound_features = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'valence']
for feature in sound_features:
    if feature in df.columns:
        fig = px.line(df, x="decade", y=feature, markers=True, title=f'Trend of {feature} Over Decades')
        fig.update_layout(xaxis_tickangle=45, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"{feature} column not found in dataset.")

# Top 10 Genres Trend
st.subheader("Top 10 Genres - Sound Features Comparison")
top_genres = df["genres"].value_counts().nlargest(10).index.tolist()
filtered_genre_data = df[df["genres"].isin(top_genres)]
for feature in ["valence", "energy", "danceability", "acousticness"]:
    if feature in filtered_genre_data.columns:
        fig = px.bar(filtered_genre_data, x="genres", y=feature, color=feature, color_continuous_scale="viridis",
                     title=f'Trend of {feature} for Top 10 Genres')
        fig.update_layout(xaxis_tickangle=45, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"{feature} column not found in dataset.")

# Genre Word Cloud
st.subheader("Genre Word Cloud")
if "genres" in df.columns:
    comment_words = ' '.join(df["genres"].dropna().astype(str).tolist())
    wordcloud = WordCloud(width=800, height=400, background_color="white", max_words=40).generate(comment_words)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Word Cloud of Genres")
    st.pyplot(fig)
else:
    st.warning("Genres column not found in dataset.")

# Export Options
st.sidebar.subheader("Export Options")
export_format = st.sidebar.selectbox("Choose Export Format", ["CSV", "PNG"])
if st.sidebar.button("Export Data"):
    if export_format == "CSV":
        filtered_df.to_csv("filtered_data.csv", index=False)
        st.sidebar.success("Data exported successfully as CSV! ✅")
    elif export_format == "PNG":
        fig.write_image("chart.png")
        st.sidebar.success("Chart saved as PNG! ✅")

st.write("🚀 Enjoy exploring MuzikiRec's data-driven insights!")
