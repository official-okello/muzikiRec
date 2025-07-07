import pandas as pd
import os
import numpy as np
import logging
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Normalize string columns
def convert_non_numeric_to_string(data):
    if data is None:
        logging.error("⚠️ Data missing for conversion.")
        return data

    non_numeric_cols = data.select_dtypes(exclude=[np.number]).columns
    for col in non_numeric_cols:
        data[col] = data[col].astype(str).str.lower()

    logging.info("✅ Non-numeric columns converted to lowercase strings.")
    return data

# Add decade column
@st.cache_data
def create_decade_column(data):
    if data is None:
        logging.error("⚠️ No data provided for decade creation.")
        return data

    if "year" not in data.columns:
        logging.error("⚠️ Year column missing in dataset.")
        return data

    data["decade"] = data["year"].apply(lambda x: (x // 10) * 10 if pd.notnull(x) else np.nan).astype("Int64")
    data.to_csv("datasets/data.csv", index=False)
    logging.info("✅ Decade column added and saved.")
    return data

# Load and preprocess datasets
@st.cache_data
def import_data():
    paths = {
        "Data": "datasets/data.csv",
        "Genre Data": "datasets/data_by_genres.csv",
        "Year Data": "datasets/data_by_year.csv",
        "Artist Data": "datasets/data_by_artist.csv"
    }

    datasets = {}

    for name, path in paths.items():
        if not os.path.exists(path):
            logging.warning(f"⚠️ {name} file not found at {path}.")
            datasets[name] = None
            continue

        try:
            df = pd.read_csv(path, on_bad_lines="warn")

            if df.empty:
                logging.warning(f"⚠️ {name} is empty.")
                datasets[name] = None
                continue

            if name == "Data":
                df = create_decade_column(df)
                df = convert_non_numeric_to_string(df)

            datasets[name] = df

        except Exception as e:
            logging.error(f"❌ Error loading {name}: {e}")
            datasets[name] = None

    return datasets.get("Data"), datasets.get("Genre Data"), datasets.get("Year Data"), datasets.get("Artist Data")

#  Standalone preview if run directly
if __name__ == "__main__":
    data, genre_data, year_data, artist_data = import_data()

    datasets = {
        "Data": data,
        "Genre Data": genre_data,
        "Year Data": year_data,
        "Artist Data": artist_data
    }

    st.title("📊 MuzikiRec - Dataset Loader & Structure Overview")
    selected_dataset = st.sidebar.selectbox("Select Dataset to Preview", list(datasets.keys()))

    st.subheader(f"🔍 {selected_dataset} Preview")
    preview_df = datasets[selected_dataset]

    if preview_df is not None:
        st.dataframe(preview_df.head(10))
        st.subheader(f"🛠 Structure of {selected_dataset}")
        buffer = st.empty()
        buffer.text(preview_df.info(verbose=True))
    else:
        st.warning(f"⚠️ No data or structure available for '{selected_dataset}'.")
