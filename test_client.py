"""
Basic test client for the music streaming server.
Tests core API functionality including search, playback control, and streaming.
"""
import requests # pyright: ignore[reportMissingModuleSource]
import json
import time
from typing import Dict, List, Optional
import pygame
import io
import threading

class MusicStreamingClient:
    def __init__(self, server_url: str = "http://pi-server:8080"):
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()
        pygame.mixer.init()
        self._current_song = None
        self._is_playing = False
    
    def health_check(self) -> bool:
        """Test server health."""
        try:
            response = self.session.get(f"{self.server_url}/health")
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_status(self) -> Optional[Dict]:
        """Get current player status."""
        try:
            response = self.session.get(f"{self.server_url}/api/status")
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            print(f"Error getting status: {e}")
        return None
    
    def search_songs(self, query: str) -> List[Dict]:
        """Search for songs."""
        try:
            response = self.session.get(
                f"{self.server_url}/api/search",
                params={"q": query}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", [])
        except requests.RequestException as e:
            print(f"Error searching: {e}")
        return []
    
    def get_artists(self) -> List[Dict]:
        """Get all artists."""
        try:
            response = self.session.get(f"{self.server_url}/api/artists")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", [])
        except requests.RequestException as e:
            print(f"Error getting artists: {e}")
        return []
    
    def stream_and_play_song(self, song: Dict) -> bool:
        """Stream and play a specific song."""
        try:
            # First, tell server we want to play this song (for state management)
            control_response = self.session.post(
                f"{self.server_url}/api/play/{song['id']}",
                json={"song": song}
            )
            
            if control_response.status_code != 200:
                print(f"Failed to set server play state: {control_response.status_code}")
                return False
            
            # Now stream the actual audio
            stream_response = self.session.get(f"{self.server_url}/stream/{song['id']}", stream=True)
            
            if stream_response.status_code != 200:
                print(f"Failed to stream audio: {stream_response.status_code}")
                return False
            
            # Load audio data into pygame
            audio_data = b''.join(stream_response.iter_content(chunk_size=8192))
            audio_file = io.BytesIO(audio_data)
            
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            self._current_song = song
            self._is_playing = True
            
            print(f"   ✅ Now playing: {song.get('title', 'Unknown')} - {song.get('artist', 'Unknown')}")
            return True
            
        except requests.RequestException as e:
            print(f"Error streaming song: {e}")
        except pygame.error as e:
            print(f"Error playing audio: {e}")
        return False

    def play_song(self, song: Dict) -> bool:
        """Legacy method - redirects to stream_and_play_song."""
        return self.stream_and_play_song(song)
    
    def pause(self) -> bool:
        """Pause playback."""
        try:
            # Pause locally
            pygame.mixer.music.pause()
            self._is_playing = False
            
            # Update server state
            response = self.session.post(f"{self.server_url}/api/pause")
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def resume(self) -> bool:
        """Resume playback."""
        try:
            # Resume locally
            pygame.mixer.music.unpause()
            self._is_playing = True
            
            # Update server state
            response = self.session.post(f"{self.server_url}/api/resume")
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def stop(self) -> bool:
        """Stop playback."""
        try:
            # Stop locally
            pygame.mixer.music.stop()
            self._is_playing = False
            self._current_song = None
            
            # Update server state
            response = self.session.post(f"{self.server_url}/api/stop")
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def seek(self, position_ms: int) -> bool:
        """Seek to position in milliseconds."""
        try:
            response = self.session.post(
                f"{self.server_url}/api/seek",
                json={"position_ms": position_ms}
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def set_volume(self, volume: float) -> bool:
        """Set volume (0.0 to 1.0)."""
        try:
            # Set volume locally
            pygame.mixer.music.set_volume(volume)
            
            # Update server state
            response = self.session.post(
                f"{self.server_url}/api/volume",
                json={"volume": volume}
            )
            return response.status_code == 200
        except requests.RequestException:
            return False


def run_tests():
    """Run basic API tests."""
    client = MusicStreamingClient()
    
    print("🎵 Music Streaming Server Test Client")
    print("=" * 40)
    
    # Health check
    print("1. Health Check...")
    if client.health_check():
        print("   ✅ Server is healthy")
    else:
        print("   ❌ Server not responding")
        return
    
    # Get status
    print("\n2. Player Status...")
    status = client.get_status()
    if status:
        print(f"   Status: {status}")
    else:
        print("   ❌ Could not get status")
    
    # Search test
    print("\n3. Search Test...")
    search_query = input("   Enter search query (or press Enter for 'test'): ").strip()
    if not search_query:
        search_query = "test"
    
    songs = client.search_songs(search_query)
    print(f"   Found {len(songs)} songs")
    for i, song in enumerate(songs[:5]):  # Show first 5
        print(f"   {i+1}. {song.get('title', 'Unknown')} - {song.get('artist', 'Unknown')}")
    
    # Play test
    if songs:
        print("\n4. Playback Test...")
        play_choice = input("   Play first song? (y/n): ").strip().lower()
        if play_choice == 'y':
            first_song = songs[0]
            if client.play_song(first_song):
                print("   ✅ Song started playing")
                
                time.sleep(2)
                
                # Test pause
                print("   Testing pause...")
                if client.pause():
                    print("   ✅ Paused")
                
                time.sleep(1)
                
                # Test resume
                print("   Testing resume...")
                if client.resume():
                    print("   ✅ Resumed")
                
                time.sleep(2)
                
                # Test seek
                print("   Testing seek to 30 seconds...")
                if client.seek(30000):
                    print("   ✅ Seeked")
                
                time.sleep(2)
                
                # Test volume
                print("   Testing volume to 50%...")
                if client.set_volume(0.5):
                    print("   ✅ Volume set")
                
                time.sleep(2)
                
                # Stop
                print("   Stopping playback...")
                if client.stop():
                    print("   ✅ Stopped")
                
            else:
                print("   ❌ Could not play song")
    
    # Artists test
    print("\n5. Artists Test...")
    artists = client.get_artists()
    print(f"   Found {len(artists)} artists")
    for artist in artists[:5]:  # Show first 5
        print(f"   - {artist.get('name', 'Unknown')}")
    
    print("\n✅ Test complete!")


if __name__ == "__main__":
    run_tests()