import streamlit as st
import logging

def create_spotify_playlist(spotify_client, user_id, playlist_name, song_names):
    try:
        playlist = spotify_client.user_playlist_create(user=user_id, name=playlist_name)
        playlist_id = playlist["id"]
        playlist_url = playlist["external_urls"]["spotify"]

        track_uris = []
        for name in song_names:
            results = spotify_client.search(q=f"track:{name}", type="track", limit=1)
            items = results["tracks"]["items"]
            if items:
                track_uris.append(items[0]["uri"])

        if track_uris:
            spotify_client.playlist_add_items(playlist_id, track_uris)

        return {
            "success": True,
            "name": playlist_name,
            "track_count": len(track_uris),
            "url": playlist_url
        }
    except Exception as e:
        logging.error(f"Playlist creation failed: {e}")
        return {"success": False}