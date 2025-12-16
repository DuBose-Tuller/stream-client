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
                    return data.get("data", {}).get("songs", [])
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