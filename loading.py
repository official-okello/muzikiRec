import pandas as pd
import os
import numpy as np
import logging
import streamlit as st

# Setting up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Define dataset paths dynamically
@st.cache_data
def import_data():
    """Load multiple datasets with enhanced error handling."""
    paths = {
        "Data": "datasets/data.csv",
        "Genre Data": "datasets/data_by_genres.csv",
        "Year Data": "datasets/data_by_year.csv",
        "Artist Data": "datasets/data_by_artist.csv"
    }

    datasets = {}

    for name, path in paths.items():
        try:
            if not os.path.exists(path):
                logging.warning(f"⚠️ {name} file missing at {path}.")
                datasets[name] = None
                continue

            df = pd.read_csv(path, on_bad_lines="warn")
            datasets[name] = None if df.empty else df

        except Exception as e:
            logging.error(f"❌ Error loading {name}: {e}")
            datasets[name] = None

    return datasets

# Load datasets
datasets = import_data()

# Streamlit UI for dataset selection
st.title("📊 MuzikiRec - Dataset Loader & Structure Overview")

selected_dataset = st.sidebar.selectbox("Select Dataset to Preview", list(datasets.keys()))

# Display dataset preview
st.subheader(f"🔍 {selected_dataset} Preview")
if datasets[selected_dataset] is not None:
    st.dataframe(datasets[selected_dataset].head(10))
else:
    st.warning(f"⚠️ No data available for {selected_dataset}.")

# Display dataset info
st.subheader(f"🛠 Structure of {selected_dataset}")
if datasets[selected_dataset] is not None:
    st.text(datasets[selected_dataset].info())
else:
    st.warning(f"⚠️ No structure available for {selected_dataset}.")

# Create Decade Column and save as the new dataset
@st.cache_data
def create_decade_column(data):
    """Adds a 'decade' column for historical analysis."""
    if data is None or "year" not in data.columns:
        logging.error("⚠️ Year column missing in dataset.")
        return data

    data["decade"] = data["year"].apply(lambda x: (x // 10) * 10 if pd.notnull(x) else np.nan).astype("Int64")

    # Save the modified dataset
    data.to_csv("datasets/data_by_year.csv", index=False)
    
    logging.info("✅ Decade column created successfully.")
    return data

# Normalize String Columns
def convert_non_numeric_to_string(data):
    """Ensure non-numeric columns are lowercase strings for consistency."""
    if data is None:
        logging.error("⚠️ Data missing for conversion.")
        return data

    non_numeric_cols = data.select_dtypes(exclude=[np.number]).columns
    for col in non_numeric_cols:
        data[col] = data[col].astype(str).str.lower()

    logging.info("✅ Non-numeric columns converted to lowercase strings.")
    return data
