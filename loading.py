# Importing Libraries
import pandas as pd
import os
import numpy as np
import logging
from wordcloud import WordCloud

# Setting up logging to handle errors and information
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Import Data
def import_data():
    try:
        paths = {
            'data': 'C:/Users/USER/OneDrive/Desktop/DS_GOMYCODE/ML/scripts/Music Recommendation System/datasets/data.csv',
            'genre_data': 'C:/Users/USER/OneDrive/Desktop/DS_GOMYCODE/ML/scripts/Music Recommendation System/datasets/data_by_genres.csv',
            'year_data': 'C:/Users/USER/OneDrive/Desktop/DS_GOMYCODE/ML/scripts/Music Recommendation System/datasets/data_by_year.csv',
            'artist_data': 'C:/Users/USER/OneDrive/Desktop/DS_GOMYCODE/ML/scripts/Music Recommendation System/datasets/data_by_artist.csv'
        }

        datasets = {}

        for name, path in paths.items():
            if not os.path.exists(path):
                raise FileNotFoundError(f"{name} file not found at {path}")
            datasets[name] = pd.read_csv(path, on_bad_lines='warn')

        return datasets['data'], datasets['genre_data'], datasets['year_data'], datasets['artist_data']

    except FileNotFoundError as e:
        logging.error(e)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    except pd.errors.EmptyDataError:
        logging.error("One or more files is empty.")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None

# Displaying Dataset Rows
def display_data(**datasets):
    for name, data in datasets.items():
        if data is not None and not data.empty:
            print(f"\nDisplaying the first two rows of the {name} dataset:")
            print(data.head(2))
        else:
            logging.warning(f"No data available for {name} dataset.")

# Data Information
def data_info(**datasets):
    for name, data in datasets.items():
        if data is not None and not data.empty:
            print(f"\n{name} dataset information:")
            print(data.info())
        else:
            logging.warning(f"No data available for {name} dataset.")

# Data Preprocessing - Creating Decade Column
def create_decade_column(data):
    if 'year' in data.columns:
        data['decade'] = data['year'].apply(lambda x: (x // 10) * 10 if pd.notnull(x) else np.nan)
        data['decade'] = data['decade'].astype('Int64')  # Ensuring correct data type
        logging.info("Decade column created successfully.")
    else:
        logging.error("Year column not found in the dataset.")
    
    return data