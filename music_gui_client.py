#!/usr/bin/env python3
"""
GUI Music Streaming Client
A simple tkinter-based client for the music streaming server.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import pygame
import io
import threading
import time
from typing import Dict, List, Optional
import json


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


class AudioPlayer:
    """Audio playback manager using pygame."""
    
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        self.current_song = None
        self.is_playing = False
        self.is_paused = False
    
    def play_audio_data(self, audio_data: bytes, song_info: Dict):
        """Play audio from bytes data."""
        try:
            audio_file = io.BytesIO(audio_data)
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            self.current_song = song_info
            self.is_playing = True
            self.is_paused = False
            return True
        except pygame.error as e:
            print(f"Pygame error: {e}")
            return False
    
    def pause(self):
        """Pause playback."""
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
    
    def resume(self):
        """Resume playback."""
        if self.is_playing and self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
    
    def stop(self):
        """Stop playback."""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.current_song = None
    
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)."""
        pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
    
    def get_busy(self) -> bool:
        """Check if music is currently playing."""
        return pygame.mixer.music.get_busy()


class MusicGUIClient:
    """Main GUI application."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Music Streaming Client")
        self.root.geometry("800x600")
        
        # Initialize components
        self.api = MusicAPIClient()
        self.player = AudioPlayer()
        
        # State
        self.search_results = []
        self.current_volume = 0.8
        
        # Setup GUI
        self.setup_gui()
        
        
        # Check server connection
        self.check_server_connection()
    
    def setup_gui(self):
        """Create the GUI layout."""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top section - Search
        search_frame = ttk.LabelFrame(main_frame, text="Search")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=("TkDefaultFont", 12))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10), pady=10)
        search_entry.bind('<Return>', self.search_music)
        
        search_btn = ttk.Button(search_frame, text="Search", command=self.search_music)
        search_btn.pack(side=tk.RIGHT, padx=(0, 10), pady=10)
        
        # Middle section - Results
        results_frame = ttk.LabelFrame(main_frame, text="Search Results")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Results listbox with scrollbar
        listbox_frame = ttk.Frame(results_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.results_listbox = tk.Listbox(listbox_frame, font=("TkDefaultFont", 10))
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.results_listbox.yview)
        self.results_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_listbox.bind('<Double-Button-1>', self.play_selected_song)
        
        # Bottom section - Player controls
        player_frame = ttk.LabelFrame(main_frame, text="Player")
        player_frame.pack(fill=tk.X)
        
        # Current song display
        self.current_song_var = tk.StringVar(value="No song playing")
        current_song_label = ttk.Label(player_frame, textvariable=self.current_song_var, font=("TkDefaultFont", 11, "bold"))
        current_song_label.pack(pady=(10, 10))
        
        # Control buttons
        controls_frame = ttk.Frame(player_frame)
        controls_frame.pack(pady=(0, 10))
        
        self.play_btn = ttk.Button(controls_frame, text="Play Selected", command=self.play_selected_song, state=tk.DISABLED)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = ttk.Button(controls_frame, text="Pause", command=self.pause_music, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.resume_btn = ttk.Button(controls_frame, text="Resume", command=self.resume_music, state=tk.DISABLED)
        self.resume_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(controls_frame, text="Stop", command=self.stop_music, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Volume control
        volume_frame = ttk.Frame(player_frame)
        volume_frame.pack(pady=(10, 10))
        
        ttk.Label(volume_frame, text="Volume:").pack(side=tk.LEFT)
        self.volume_var = tk.DoubleVar(value=self.current_volume)
        volume_scale = ttk.Scale(volume_frame, from_=0.0, to=1.0, variable=self.volume_var, 
                                orient=tk.HORIZONTAL, length=200, command=self.volume_changed)
        volume_scale.pack(side=tk.LEFT, padx=(5, 5))
        self.volume_label = ttk.Label(volume_frame, text=f"{int(self.current_volume*100)}%")
        self.volume_label.pack(side=tk.LEFT)
    
    def check_server_connection(self):
        """Check if server is accessible."""
        def check_connection():
            if self.api.health_check():
                self.root.after(0, lambda: self.show_status("Connected to server", "green"))
            else:
                self.root.after(0, lambda: self.show_status("Server not accessible", "red"))
        
        threading.Thread(target=check_connection, daemon=True).start()
    
    def show_status(self, message: str, color: str = "black"):
        """Show status message in title bar."""
        self.root.title(f"Music Streaming Client - {message}")
    
    def search_music(self, event=None):
        """Search for music."""
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a search term")
            return
        
        self.show_status("Searching...", "blue")
        
        def do_search():
            try:
                results = self.api.search_songs(query)
                if results:
                    self.root.after(0, lambda: self.display_search_results(results))
                else:
                    # Test if it's a connection issue by checking health
                    if not self.api.health_check():
                        self.root.after(0, lambda: messagebox.showerror("Connection Error", 
                                                                       "Cannot connect to music server.\nPlease check that the server is running."))
                        self.root.after(0, lambda: self.show_status("Server not accessible", "red"))
                    else:
                        self.root.after(0, lambda: self.display_search_results([]))
                        self.root.after(0, lambda: self.show_status("No results found", "orange"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Search Error", f"Search failed: {str(e)}"))
                self.root.after(0, lambda: self.show_status("Search failed", "red"))
        
        threading.Thread(target=do_search, daemon=True).start()
    
    def display_search_results(self, results: List[Dict]):
        """Display search results in the listbox."""
        self.search_results = results
        self.results_listbox.delete(0, tk.END)
        
        if not results:
            self.results_listbox.insert(tk.END, "No results found")
            self.play_btn.configure(state=tk.DISABLED)
            self.show_status("No results found", "orange")
            return
        
        for song in results:
            title = song.get('title', 'Unknown Title')
            artist = song.get('artist', 'Unknown Artist')
            album = song.get('album', 'Unknown Album')
            duration = song.get('duration', 0)
            
            duration_str = f"{duration//60}:{duration%60:02d}" if duration else "Unknown"
            display_text = f"{title} - {artist} [{album}] ({duration_str})"
            self.results_listbox.insert(tk.END, display_text)
        
        self.play_btn.configure(state=tk.NORMAL)
        self.show_status(f"Found {len(results)} songs", "green")
    
    def play_selected_song(self, event=None):
        """Play the currently selected song."""
        selection = self.results_listbox.curselection()
        if not selection or not self.search_results:
            messagebox.showwarning("No Selection", "Please select a song to play")
            return
        
        song_index = selection[0]
        if song_index >= len(self.search_results):
            return
        
        song = self.search_results[song_index]
        self.show_status("Loading song...", "blue")
        
        def play_song():
            # Notify server
            self.api.notify_server_play(song)
            
            # Get audio data
            audio_data = self.api.stream_song(song['id'])
            if not audio_data:
                self.root.after(0, lambda: self.show_status("Failed to load song", "red"))
                return
            
            # Play audio
            success = self.player.play_audio_data(audio_data, song)
            if success:
                title = song.get('title', 'Unknown')
                artist = song.get('artist', 'Unknown')
                self.root.after(0, lambda: self.current_song_var.set(f"♪ {title} - {artist}"))
                self.root.after(0, lambda: self.show_status("Playing", "green"))
                self.root.after(0, self.update_button_states)
            else:
                self.root.after(0, lambda: self.show_status("Failed to play song", "red"))
        
        threading.Thread(target=play_song, daemon=True).start()
    
    def pause_music(self):
        """Pause current playback."""
        self.player.pause()
        self.show_status("Paused", "orange")
        self.update_button_states()
    
    def resume_music(self):
        """Resume paused playback."""
        self.player.resume()
        self.show_status("Playing", "green")
        self.update_button_states()
    
    def stop_music(self):
        """Stop current playback."""
        self.player.stop()
        self.current_song_var.set("No song playing")
        self.show_status("Stopped", "black")
        self.update_button_states()
    
    def volume_changed(self, value):
        """Handle volume slider changes."""
        volume = float(value)
        self.current_volume = volume
        self.player.set_volume(volume)
        self.volume_label.configure(text=f"{int(volume*100)}%")
    
    def update_button_states(self):
        """Update button enabled/disabled states based on player state."""
        if self.player.is_playing:
            if self.player.is_paused:
                self.pause_btn.configure(state=tk.DISABLED)
                self.resume_btn.configure(state=tk.NORMAL)
            else:
                self.pause_btn.configure(state=tk.NORMAL)
                self.resume_btn.configure(state=tk.DISABLED)
            self.stop_btn.configure(state=tk.NORMAL)
        else:
            self.pause_btn.configure(state=tk.DISABLED)
            self.resume_btn.configure(state=tk.DISABLED)
            self.stop_btn.configure(state=tk.DISABLED)
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def main():
    """Entry point."""
    app = MusicGUIClient()
    app.run()


if __name__ == "__main__":
    main()