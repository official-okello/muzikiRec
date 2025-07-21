import os
from pathlib import Path
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import logging
from dotenv import load_dotenv
import streamlit as st

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

def get_spotify_oauth():
    """Returns a SpotifyOAuth object initialized with credentials from environment variables."""
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

    if not all([client_id, client_secret, redirect_uri]):
        raise EnvironmentError("Spotify credentials not properly set in .env file.")

    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="playlist-modify-public"
    )

def authenticate_spotify():
    """Handles Spotify OAuth and stores access token and Spotify client in Streamlit session state."""
    sp_oauth = get_spotify_oauth()
    query_params = st.query_params

    if "access_token" not in st.session_state:
        code = query_params.get("code", [None])[0]

        if not code:
            auth_url = sp_oauth.get_authorize_url()
            st.markdown(f"[🔐 Click here to login with Spotify]({auth_url})")
            st.stop()

        try:
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info.get("access_token")

            if not access_token:
                st.error("⚠️ Failed to obtain access token from Spotify.")
                st.stop()

            # Save access token and create Spotify client
            st.session_state.access_token = access_token
            st.session_state.spotify = spotipy.Spotify(auth=access_token)
            st.success("✅ Spotify authenticated successfully.")

        except Exception as e:
            st.error("❌ Spotify authentication failed.")
            logging.exception(e)
            st.stop()
    else:
        # Use existing access token
        st.session_state.spotify = spotipy.Spotify(auth=st.session_state.access_token)
        st.success("✅ Using existing Spotify session.")
    return st.session_state.spotify