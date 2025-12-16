#!/usr/bin/env python3
"""
GUI Music Streaming Client

Main application window and user interface logic for the music
streaming client using tkinter and ttk widgets.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Dict, List

from api_client import MusicAPIClient
from audio_player import AudioPlayer


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
        self.is_loading = False
        
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
                                                                       "Cannot connect to music server.\\nPlease check that the server is running."))
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
        # Prevent multiple simultaneous loads
        if self.is_loading:
            return

        selection = self.results_listbox.curselection()
        if not selection or not self.search_results:
            messagebox.showwarning("No Selection", "Please select a song to play")
            return

        song_index = selection[0]
        if song_index >= len(self.search_results):
            return

        song = self.search_results[song_index]

        # Stop any existing playback
        self.player.stop()

        # Set loading state
        self.is_loading = True
        self.play_btn.configure(state=tk.DISABLED)
        self.show_status("Loading song...", "blue")

        def play_song():
            temp_path = None
            try:
                # Notify server
                self.api.notify_server_play(song)

                title = song.get('title', 'Unknown')
                artist = song.get('artist', 'Unknown')
                started_playing = False

                def ready_to_play(file_path: str):
                    """Called when enough data is buffered to start playing."""
                    nonlocal started_playing
                    if not started_playing:
                        success = self.player.play_audio_file(file_path, song)
                        if success:
                            started_playing = True
                            self.root.after(0, lambda: self.current_song_var.set(f"♪ {title} - {artist}"))
                            self.root.after(0, lambda: self.show_status("Playing (buffering...)", "green"))
                            self.root.after(0, self.update_button_states)

                # Stream song progressively (starts playing after 1MB buffered)
                temp_path = self.api.stream_song_progressive(song['id'], ready_callback=ready_to_play)

                if not temp_path:
                    self.root.after(0, lambda: self.show_status("Failed to load song", "red"))
                    return

                # If callback wasn't called (song smaller than buffer), play now
                if not started_playing:
                    success = self.player.play_audio_file(temp_path, song)
                    if success:
                        self.root.after(0, lambda: self.current_song_var.set(f"♪ {title} - {artist}"))
                        self.root.after(0, lambda: self.show_status("Playing", "green"))
                        self.root.after(0, self.update_button_states)
                    else:
                        self.root.after(0, lambda: self.show_status("Failed to play song", "red"))
                else:
                    # Update status once download completes
                    self.root.after(0, lambda: self.show_status("Playing", "green"))

            finally:
                # Re-enable play button
                self.is_loading = False
                self.root.after(0, lambda: self.play_btn.configure(state=tk.NORMAL))

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