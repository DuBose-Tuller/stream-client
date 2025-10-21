#!/usr/bin/env python3
"""
API Client for Music Streaming Server

Handles all HTTP communication with the music streaming server,
including search, playback control, and audio streaming.
"""

import requests
from typing import Dict, List, Optional


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
    
    def search_songs(self, query: str) -> List[Dict]:
        """Search for songs."""
        try:
            response = self.session.get(
                f"{self.server_url}/api/search",
                params={"q": query},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", [])
        except requests.RequestException as e:
            print(f"Search error: {e}")
        return []
    
    def get_artists(self) -> List[Dict]:
        """Get all artists."""
        try:
            response = self.session.get(f"{self.server_url}/api/artists", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", [])
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
            payload = {"name": name}
            if description is not None:
                payload["description"] = description

            response = self.session.post(
                f"{self.server_url}/api/playlists",
                json=payload,
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

    def add_track_to_playlist(self, playlist_id: str, song_id: str, position: Optional[int] = None) -> bool:
        """Add a track to a playlist. If position is None, appends to the end."""
        try:
            payload = {"type": "track", "song_id": song_id}
            if position is not None:
                payload["position"] = position

            response = self.session.post(
                f"{self.server_url}/api/playlists/{playlist_id}/items",
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Add track error: {e}")
            return False

    def add_track_group_to_playlist(self, playlist_id: str, name: str,
                                     song_ids: List[str], position: Optional[int] = None) -> bool:
        """Add a track group to a playlist. If position is None, appends to the end."""
        try:
            payload = {
                "type": "group",
                "name": name,
                "song_ids": song_ids
            }
            if position is not None:
                payload["position"] = position

            response = self.session.post(
                f"{self.server_url}/api/playlists/{playlist_id}/items",
                json=payload,
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