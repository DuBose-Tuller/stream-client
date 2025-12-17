#!/usr/bin/env python3
"""
API Client for Music Streaming Server

Handles all HTTP communication with the music streaming server,
including search, playback control, and audio streaming.
"""

import requests
import tempfile
import os
from typing import Dict, List, Optional, Callable


class MusicAPIClient:
    """API client for communicating with the music streaming server."""
    
    def __init__(self, server_url: str = "http://pi-server:8080"):
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> bool:
        """Test server health."""
        try:
            response = self.session.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def search_songs(self, query: str) -> Dict:
        """Search for songs, albums, and artists. Returns full search response."""
        try:
            response = self.session.get(
                f"{self.server_url}/api/search",
                params={"q": query},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Return full search response with songs, albums, artists
                    return data.get("data", {})
        except requests.RequestException as e:
            print(f"Search error: {e}")
        return {}
    
    def get_artists(self) -> List[Dict]:
        """Get all artists."""
        try:
            response = self.session.get(f"{self.server_url}/api/artists", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Extract artists array from response object
                    artists_data = data.get("data", {})
                    return artists_data.get("artists", [])
        except requests.RequestException as e:
            print(f"Artists error: {e}")
        return []
    
    def stream_song(self, song_id: str) -> Optional[bytes]:
        """Get song audio data."""
        try:
            response = self.session.get(f"{self.server_url}/stream/{song_id}", timeout=30)
            if response.status_code == 200:
                return response.content
        except requests.RequestException as e:
            print(f"Stream error: {e}")
        return None

    def stream_song_progressive(self, song_id: str, ready_callback: Optional[Callable[[str], None]] = None,
                                buffer_size: int = 1024 * 1024) -> Optional[str]:
        """
        Stream song to temp file with progressive loading.
        Calls ready_callback with temp file path once buffer_size bytes are downloaded.
        Returns temp file path, or None on error.
        """
        try:
            response = self.session.get(f"{self.server_url}/stream/{song_id}", stream=True, timeout=30)
            if response.status_code != 200:
                return None

            # Create temp file (no extension, let pygame auto-detect format)
            temp_fd, temp_path = tempfile.mkstemp(suffix='')
            temp_file = os.fdopen(temp_fd, 'wb')

            bytes_downloaded = 0
            callback_called = False

            # Download in chunks
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    temp_file.write(chunk)
                    bytes_downloaded += len(chunk)

                    # Call callback once we have enough buffered
                    if not callback_called and bytes_downloaded >= buffer_size and ready_callback:
                        temp_file.flush()  # Ensure data is written
                        ready_callback(temp_path)
                        callback_called = True

            temp_file.close()
            return temp_path

        except requests.RequestException as e:
            print(f"Stream error: {e}")
            return None
    
    def notify_server_play(self, song: Dict) -> bool:
        """Tell server we're playing this song (for state management)."""
        try:
            response = self.session.post(
                f"{self.server_url}/api/play/{song['id']}",
                json={"song": song},
                timeout=5
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    # Playlist operations

    def get_all_playlists(self) -> List[Dict]:
        """Get all playlists."""
        try:
            response = self.session.get(f"{self.server_url}/api/playlists", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", [])
        except requests.RequestException as e:
            print(f"Get playlists error: {e}")
        return []

    def create_playlist(self, name: str, description: Optional[str] = None) -> Optional[str]:
        """Create a new playlist. Returns playlist ID on success."""
        try:
            response = self.session.post(
                f"{self.server_url}/api/playlists",
                json={"name": name, "description": description},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data")
        except requests.RequestException as e:
            print(f"Create playlist error: {e}")
        return None

    def get_playlist(self, playlist_id: str) -> Optional[Dict]:
        """Get a playlist with all its items."""
        try:
            response = self.session.get(
                f"{self.server_url}/api/playlists/{playlist_id}",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data")
        except requests.RequestException as e:
            print(f"Get playlist error: {e}")
        return None

    def delete_playlist(self, playlist_id: str) -> bool:
        """Delete a playlist."""
        try:
            response = self.session.delete(
                f"{self.server_url}/api/playlists/{playlist_id}",
                timeout=10
            )
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Delete playlist error: {e}")
            return False

    def update_playlist(self, playlist_id: str, name: Optional[str] = None,
                        description: Optional[str] = None) -> bool:
        """Update playlist information."""
        try:
            payload = {}
            if name is not None:
                payload["name"] = name
            if description is not None:
                payload["description"] = description

            response = self.session.put(
                f"{self.server_url}/api/playlists/{playlist_id}",
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Update playlist error: {e}")
            return False

    def add_track_to_playlist(self, playlist_id: str, song_id: str, position: int = 0) -> bool:
        """Add a track to a playlist at the specified position."""
        try:
            response = self.session.post(
                f"{self.server_url}/api/playlists/{playlist_id}/items",
                json={"type": "track", "song_id": song_id, "position": position},
                timeout=10
            )
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Add track error: {e}")
            return False

    def add_track_group_to_playlist(self, playlist_id: str, name: str,
                                     song_ids: List[str], position: int = 0) -> bool:
        """Add a track group to a playlist at the specified position."""
        try:
            response = self.session.post(
                f"{self.server_url}/api/playlists/{playlist_id}/items",
                json={
                    "type": "group",
                    "name": name,
                    "song_ids": song_ids,
                    "position": position
                },
                timeout=10
            )
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Add track group error: {e}")
            return False

    def remove_playlist_item(self, playlist_id: str, position: int) -> bool:
        """Remove an item from a playlist at the specified position."""
        try:
            response = self.session.delete(
                f"{self.server_url}/api/playlists/{playlist_id}/items/{position}",
                timeout=10
            )
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Remove item error: {e}")
            return False