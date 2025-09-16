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