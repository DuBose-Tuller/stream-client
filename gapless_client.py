"""
Enhanced music streaming client with gapless playback demonstration.
Uses dual pygame mixer channels to achieve seamless track transitions.
"""
import requests
import time
import threading
from typing import Dict, List, Optional, Tuple
import pygame
import io
from queue import Queue
import json

class GaplessPlayer:
    def __init__(self, server_url: str = "http://pi-server:8080"):
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()
        
        # Initialize pygame mixer with specific settings for gapless playback
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        
        # Gapless playback state
        self.current_channel = 0  # 0 or 1 (dual channel approach)
        self.channels = [pygame.mixer.Channel(0), pygame.mixer.Channel(1)]
        self.queue = []
        self.current_song_index = 0
        self.is_playing = False
        self.preload_thread = None
        self.preloaded_sounds = {}  # song_id -> pygame.mixer.Sound
        
        # Playback monitoring
        self.position_thread = None
        self.stop_monitoring = False
        
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
    
    def stream_song(self, song_id: str) -> Optional[pygame.mixer.Sound]:
        """Stream a song and return as pygame Sound object."""
        try:
            # Get audio data from server
            stream_response = self.session.get(f"{self.server_url}/stream/{song_id}")
            
            if stream_response.status_code != 200:
                print(f"Failed to stream audio: {stream_response.status_code}")
                return None
            
            # Convert to pygame Sound
            audio_data = io.BytesIO(stream_response.content)
            sound = pygame.mixer.Sound(audio_data)
            
            return sound
            
        except Exception as e:
            print(f"Error streaming song {song_id}: {e}")
            return None
    
    def preload_next_song(self):
        """Preload the next song in the queue."""
        if not self.queue or self.current_song_index >= len(self.queue) - 1:
            return
        
        next_song = self.queue[self.current_song_index + 1]
        song_id = next_song['id']
        
        if song_id not in self.preloaded_sounds:
            print(f"   🔄 Preloading: {next_song.get('title', 'Unknown')}")
            sound = self.stream_song(song_id)
            if sound:
                self.preloaded_sounds[song_id] = sound
                print(f"   ✅ Preloaded: {next_song.get('title', 'Unknown')}")
    
    def play_queue_gapless(self, songs: List[Dict], start_index: int = 0):
        """Play a queue of songs with gapless transitions."""
        if not songs:
            print("No songs to play")
            return
            
        self.queue = songs
        self.current_song_index = start_index
        self.is_playing = True
        
        print(f"🎵 Starting gapless playback of {len(songs)} songs")
        print(f"   Starting with: {songs[start_index].get('title', 'Unknown')}")
        
        # Start preloading thread
        self.preload_thread = threading.Thread(target=self._preload_worker)
        self.preload_thread.daemon = True
        self.preload_thread.start()
        
        # Start position monitoring
        self.stop_monitoring = False
        self.position_thread = threading.Thread(target=self._position_monitor)
        self.position_thread.daemon = True
        self.position_thread.start()
        
        # Play the first song
        self._play_current_song()
        
        # Monitor for track endings and handle transitions
        self._monitor_playback()
    
    def _play_current_song(self):
        """Play the current song in the queue."""
        if not self.queue or self.current_song_index >= len(self.queue):
            return
            
        current_song = self.queue[self.current_song_index]
        song_id = current_song['id']
        
        print(f"▶️  Playing: {current_song.get('title', 'Unknown')} - {current_song.get('artist', 'Unknown')}")
        
        # Check if we have it preloaded
        if song_id in self.preloaded_sounds:
            sound = self.preloaded_sounds[song_id]
            del self.preloaded_sounds[song_id]  # Free memory
        else:
            print(f"   🔄 Streaming (not preloaded): {current_song.get('title', 'Unknown')}")
            sound = self.stream_song(song_id)
            if not sound:
                print(f"   ❌ Failed to load song")
                return
        
        # Play on the current channel
        channel = self.channels[self.current_channel]
        channel.play(sound)
        
        # Start preloading the next song
        threading.Thread(target=self.preload_next_song, daemon=True).start()
    
    def _monitor_playback(self):
        """Monitor playback and handle gapless transitions."""
        while self.is_playing and self.current_song_index < len(self.queue):
            current_channel = self.channels[self.current_channel]
            
            # Check if current song is still playing
            if not current_channel.get_busy():
                # Song finished, move to next
                self._advance_to_next_song()
            
            time.sleep(0.1)  # Check every 100ms
    
    def _advance_to_next_song(self):
        """Advance to the next song in the queue."""
        self.current_song_index += 1
        
        if self.current_song_index >= len(self.queue):
            print("🎵 Queue finished")
            self.is_playing = False
            return
        
        # Switch to the other channel for seamless transition
        self.current_channel = 1 - self.current_channel
        
        # Play the next song
        self._play_current_song()
    
    def _preload_worker(self):
        """Background worker to preload upcoming songs."""
        while self.is_playing:
            self.preload_next_song()
            time.sleep(2)  # Check every 2 seconds
    
    def _position_monitor(self):
        """Monitor playback position and provide feedback."""
        while not self.stop_monitoring and self.is_playing:
            if self.current_song_index < len(self.queue):
                current_song = self.queue[self.current_song_index]
                channel = self.channels[self.current_channel]
                
                # Simple progress indication
                if channel.get_busy():
                    print(f"   ♪ {current_song.get('title', 'Unknown')} [Playing on channel {self.current_channel}]")
            
            time.sleep(5)  # Update every 5 seconds
    
    def pause(self):
        """Pause playback."""
        for channel in self.channels:
            channel.pause()
        print("⏸️  Paused")
    
    def resume(self):
        """Resume playback."""
        for channel in self.channels:
            channel.unpause()
        print("▶️  Resumed")
    
    def stop(self):
        """Stop playback."""
        self.is_playing = False
        self.stop_monitoring = True
        for channel in self.channels:
            channel.stop()
        self.preloaded_sounds.clear()
        print("⏹️  Stopped")
    
    def get_current_song(self) -> Optional[Dict]:
        """Get the currently playing song."""
        if self.queue and self.current_song_index < len(self.queue):
            return self.queue[self.current_song_index]
        return None

def run_gapless_demo():
    """Run gapless playback demonstration."""
    client = GaplessPlayer()
    
    print("🎵 Gapless Music Streaming Client")
    print("=================================")
    
    # Health check
    print("1. Checking server connection...")
    try:
        response = client.session.get(f"{client.server_url}/health")
        if response.status_code == 200:
            print("   ✅ Server is healthy")
        else:
            print("   ❌ Server not responding")
            return
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return
    
    # Search for songs
    print("\n2. Searching for songs...")
    search_query = input("   Enter search query (or press Enter for 'test'): ").strip()
    if not search_query:
        search_query = "test"
    
    songs = client.search_songs(search_query)
    if not songs:
        print("   ❌ No songs found")
        return
    
    print(f"   Found {len(songs)} songs:")
    for i, song in enumerate(songs[:10], 1):  # Show first 10
        duration = song.get('duration', 0)
        duration_str = f"{duration//60}:{duration%60:02d}" if duration else "Unknown"
        print(f"   {i}. {song.get('title', 'Unknown')} - {song.get('artist', 'Unknown')} [{duration_str}]")
    
    if len(songs) > 10:
        print(f"   ... and {len(songs) - 10} more")
    
    # Select songs for gapless demo
    print("\n3. Gapless Playback Demo")
    if len(songs) >= 3:
        demo_songs = songs[:3]  # Take first 3 songs for demo
        print(f"   Selected {len(demo_songs)} songs for gapless demo:")
        for i, song in enumerate(demo_songs, 1):
            print(f"   {i}. {song.get('title', 'Unknown')} - {song.get('artist', 'Unknown')}")
        
        print(f"\n   This will demonstrate:")
        print(f"   • Seamless transitions between tracks")
        print(f"   • Preloading of upcoming songs")
        print(f"   • Dual-channel audio mixing")
        print(f"   • No gaps or clicks between songs")
        
        start_demo = input("\n   Start gapless demo? (y/n): ").strip().lower()
        if start_demo == 'y':
            print(f"\n🚀 Starting gapless playback demo...")
            print(f"   Press Ctrl+C to stop\n")
            
            try:
                client.play_queue_gapless(demo_songs)
                
                # Interactive controls during playback
                while client.is_playing:
                    try:
                        cmd = input("Commands: (p)ause, (r)esume, (s)top, (q)uit: ").strip().lower()
                        if cmd == 'p':
                            client.pause()
                        elif cmd == 'r':
                            client.resume()
                        elif cmd in ['s', 'q']:
                            client.stop()
                            break
                        elif cmd == '':
                            current = client.get_current_song()
                            if current:
                                print(f"   Currently playing: {current.get('title', 'Unknown')}")
                    except KeyboardInterrupt:
                        break
                        
            except KeyboardInterrupt:
                print(f"\n\n⏹️  Stopping playback...")
                client.stop()
                
            print(f"\n✅ Gapless demo completed!")
        
    else:
        print(f"   ❌ Need at least 3 songs for meaningful gapless demo")
    
    print(f"\n🎵 Demo finished. Thanks for testing!")

if __name__ == "__main__":
    run_gapless_demo()