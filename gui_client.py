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
        self.position_update_job = None
        self.is_seeking = False
        
        # Setup GUI
        self.setup_gui()
        
        # Check server connection
        self.check_server_connection()
    
    def setup_gui(self):
        """Create the GUI layout."""
        # Main container with two columns
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left column - Search and Results
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Right column - Playlists
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(5, 0))
        right_frame.config(width=250)
        
        # Top section - Search (in left frame)
        search_frame = ttk.LabelFrame(left_frame, text="Search")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=("TkDefaultFont", 12))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10), pady=10)
        search_entry.bind('<Return>', self.search_music)
        
        search_btn = ttk.Button(search_frame, text="Search", command=self.search_music)
        search_btn.pack(side=tk.RIGHT, padx=(0, 10), pady=10)
        
        # Middle section - Results (in left frame)
        results_frame = ttk.LabelFrame(left_frame, text="Search Results")
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

        # Add button to add song to playlist
        results_btn_frame = ttk.Frame(results_frame)
        results_btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.add_to_playlist_btn = ttk.Button(results_btn_frame, text="Add to Playlist",
                                               command=self.add_to_playlist, state=tk.DISABLED)
        self.add_to_playlist_btn.pack(side=tk.LEFT, padx=5)

        # Right column - Playlists section
        playlists_frame = ttk.LabelFrame(right_frame, text="Playlists")
        playlists_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Playlist buttons
        playlist_btn_frame = ttk.Frame(playlists_frame)
        playlist_btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(playlist_btn_frame, text="New", command=self.create_playlist_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(playlist_btn_frame, text="Refresh", command=self.load_playlists).pack(side=tk.LEFT, padx=2)

        # Playlists listbox
        playlist_list_frame = ttk.Frame(playlists_frame)
        playlist_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.playlists_listbox = tk.Listbox(playlist_list_frame, font=("TkDefaultFont", 10))
        playlist_scrollbar = ttk.Scrollbar(playlist_list_frame, orient=tk.VERTICAL,
                                          command=self.playlists_listbox.yview)
        self.playlists_listbox.configure(yscrollcommand=playlist_scrollbar.set)

        self.playlists_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        playlist_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.playlists_listbox.bind('<Double-Button-1>', self.view_playlist)

        # Playlist action buttons
        playlist_action_frame = ttk.Frame(playlists_frame)
        playlist_action_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Button(playlist_action_frame, text="View", command=self.view_playlist).pack(side=tk.LEFT, padx=2)
        ttk.Button(playlist_action_frame, text="Delete", command=self.delete_playlist).pack(side=tk.LEFT, padx=2)

        # Bottom section - Player controls (in left frame)
        player_frame = ttk.LabelFrame(left_frame, text="Player")
        player_frame.pack(fill=tk.X)
        
        # Current song display
        self.current_song_var = tk.StringVar(value="No song playing")
        current_song_label = ttk.Label(player_frame, textvariable=self.current_song_var, font=("TkDefaultFont", 11, "bold"))
        current_song_label.pack(pady=(10, 5))

        # Seeking controls
        seek_frame = ttk.Frame(player_frame)
        seek_frame.pack(fill=tk.X, padx=20, pady=(5, 10))

        # Time labels
        self.current_time_var = tk.StringVar(value="0:00")
        self.total_time_var = tk.StringVar(value="0:00")

        ttk.Label(seek_frame, textvariable=self.current_time_var, font=("TkDefaultFont", 9)).pack(side=tk.LEFT)

        # Progress bar
        self.seek_var = tk.DoubleVar(value=0.0)
        self.seek_scale = ttk.Scale(
            seek_frame,
            from_=0.0,
            to=100.0,
            variable=self.seek_var,
            orient=tk.HORIZONTAL,
            command=self.on_seek_drag
        )
        self.seek_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.seek_scale.bind('<ButtonRelease-1>', self.on_seek_release)

        ttk.Label(seek_frame, textvariable=self.total_time_var, font=("TkDefaultFont", 9)).pack(side=tk.RIGHT)
        
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
                # Load playlists on startup
                self.root.after(0, self.load_playlists)
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
    
    def display_search_results(self, results: Dict):
        """Display search results in the listbox."""
        # Extract all result types from the new SearchResponse structure
        songs = results.get('songs', []) if isinstance(results, dict) else []
        albums = results.get('albums', []) if isinstance(results, dict) else []
        artists = results.get('artists', []) if isinstance(results, dict) else []

        self.search_results = songs
        self.results_listbox.delete(0, tk.END)

        if not songs and not albums and not artists:
            self.results_listbox.insert(tk.END, "No results found")
            self.play_btn.configure(state=tk.DISABLED)
            self.add_to_playlist_btn.configure(state=tk.DISABLED)
            self.show_status("No results found", "orange")
            return

        for song in songs:
            title = song.get('title', 'Unknown Title')
            artist = song.get('artist', 'Unknown Artist')
            album = song.get('album', 'Unknown Album')
            duration = song.get('duration', 0)

            duration_str = f"{duration//60}:{duration%60:02d}" if duration else "Unknown"
            display_text = f"{title} - {artist} [{album}] ({duration_str})"
            self.results_listbox.insert(tk.END, display_text)

        self.play_btn.configure(state=tk.NORMAL if songs else tk.DISABLED)
        self.add_to_playlist_btn.configure(state=tk.NORMAL if songs else tk.DISABLED)

        # Show detailed status with counts for all result types
        status_parts = []
        if songs:
            status_parts.append(f"{len(songs)} song{'s' if len(songs) != 1 else ''}")
        if albums:
            status_parts.append(f"{len(albums)} album{'s' if len(albums) != 1 else ''}")
        if artists:
            status_parts.append(f"{len(artists)} artist{'s' if len(artists) != 1 else ''}")

        self.show_status(f"Found {', '.join(status_parts)}", "green")
    
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
                            self.root.after(0, self.start_position_updates)

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
                        self.root.after(0, self.start_position_updates)
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
        self.stop_position_updates()
        self.reset_seek_controls()
    
    def volume_changed(self, value):
        """Handle volume slider changes."""
        volume = float(value)
        self.current_volume = volume
        self.player.set_volume(volume)
        self.volume_label.configure(text=f"{int(volume*100)}%")

    def format_time(self, seconds: float) -> str:
        """Format seconds as M:SS."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"

    def update_position(self):
        """Update the seek bar and time labels with current position."""
        if not self.player.is_playing:
            return

        position = self.player.get_position()
        duration = self.player.get_duration()

        if duration > 0 and not self.is_seeking:
            percentage = (position / duration) * 100
            self.seek_var.set(percentage)
            self.current_time_var.set(self.format_time(position))

        # Check if song has ended
        if not self.player.get_busy() and self.player.is_playing:
            self.stop_music()
            return

        # Schedule next update
        self.position_update_job = self.root.after(100, self.update_position)

    def start_position_updates(self):
        """Start the position update loop."""
        self.stop_position_updates()
        duration = self.player.get_duration()
        if duration > 0:
            self.total_time_var.set(self.format_time(duration))
        self.update_position()

    def stop_position_updates(self):
        """Stop the position update loop."""
        if self.position_update_job:
            self.root.after_cancel(self.position_update_job)
            self.position_update_job = None

    def reset_seek_controls(self):
        """Reset seek controls to initial state."""
        self.seek_var.set(0.0)
        self.current_time_var.set("0:00")
        self.total_time_var.set("0:00")

    def on_seek_drag(self, value):
        """Handle seek bar dragging."""
        if not self.player.is_playing:
            return

        self.is_seeking = True
        duration = self.player.get_duration()
        if duration > 0:
            position = (float(value) / 100.0) * duration
            self.current_time_var.set(self.format_time(position))

    def on_seek_release(self, event):
        """Handle seek bar release (perform actual seek)."""
        if not self.player.is_playing:
            self.is_seeking = False
            return

        duration = self.player.get_duration()
        if duration > 0:
            percentage = self.seek_var.get()
            target_position = (percentage / 100.0) * duration

            success = self.player.seek(target_position)
            if not success:
                messagebox.showwarning("Seek Failed",
                                     "Unable to seek in this audio format. Try MP3 for better seeking support.")

        self.is_seeking = False
    
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
    
    def load_playlists(self):
        """Load all playlists from the server."""
        def do_load():
            try:
                playlists = self.api.get_all_playlists()
                self.root.after(0, lambda: self.display_playlists(playlists))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Load Error",
                                                                f"Failed to load playlists: {str(e)}"))

        threading.Thread(target=do_load, daemon=True).start()

    def display_playlists(self, playlists: List[Dict]):
        """Display playlists in the listbox."""
        self.playlists = playlists
        self.playlists_listbox.delete(0, tk.END)

        if not playlists:
            self.playlists_listbox.insert(tk.END, "No playlists")
            return

        for playlist in playlists:
            name = playlist.get('name', 'Unknown')
            item_count = len(playlist.get('items', []))
            self.playlists_listbox.insert(tk.END, f"{name} ({item_count} items)")

    def create_playlist_dialog(self):
        """Show dialog to create a new playlist."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Playlist")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()

        # Name field
        ttk.Label(dialog, text="Playlist Name:").pack(pady=(20, 5))
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=40)
        name_entry.pack(pady=5)
        name_entry.focus()

        # Description field
        ttk.Label(dialog, text="Description (optional):").pack(pady=(10, 5))
        desc_var = tk.StringVar()
        desc_entry = ttk.Entry(dialog, textvariable=desc_var, width=40)
        desc_entry.pack(pady=5)

        def create():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Invalid Input", "Please enter a playlist name")
                return

            description = desc_var.get().strip() or None
            dialog.destroy()

            # Create playlist in background
            def do_create():
                try:
                    playlist_id = self.api.create_playlist(name, description)
                    if playlist_id:
                        self.root.after(0, lambda: messagebox.showinfo("Success",
                                                                       f"Playlist '{name}' created!"))
                        self.root.after(0, self.load_playlists)
                    else:
                        self.root.after(0, lambda: messagebox.showerror("Error",
                                                                        "Failed to create playlist"))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Error: {str(e)}"))

            threading.Thread(target=do_create, daemon=True).start()

        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Create", command=create).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Bind Enter key
        name_entry.bind('<Return>', lambda e: create())
        desc_entry.bind('<Return>', lambda e: create())

    def view_playlist(self, event=None):
        """View playlist contents."""
        selection = self.playlists_listbox.curselection()
        if not selection or not self.playlists:
            messagebox.showwarning("No Selection", "Please select a playlist to view")
            return

        playlist_index = selection[0]
        if playlist_index >= len(self.playlists):
            return

        playlist = self.playlists[playlist_index]

        # Fetch full playlist details
        def do_view():
            try:
                full_playlist = self.api.get_playlist(playlist['id'])
                if full_playlist:
                    self.root.after(0, lambda: self.show_playlist_dialog(full_playlist))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error",
                                                                    "Failed to load playlist"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error: {str(e)}"))

        threading.Thread(target=do_view, daemon=True).start()

    def show_playlist_dialog(self, playlist: Dict):
        """Show dialog with playlist contents."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Playlist: {playlist.get('name', 'Unknown')}")
        dialog.geometry("600x400")
        dialog.transient(self.root)

        # Description
        desc = playlist.get('description', '')
        if desc:
            ttk.Label(dialog, text=desc, font=("TkDefaultFont", 10, "italic")).pack(pady=10)

        # Items listbox
        items_frame = ttk.Frame(dialog)
        items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        items_listbox = tk.Listbox(items_frame, font=("TkDefaultFont", 10))
        items_scrollbar = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=items_listbox.yview)
        items_listbox.configure(yscrollcommand=items_scrollbar.set)

        items_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        items_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Populate items
        items = playlist.get('items', [])
        if not items:
            items_listbox.insert(tk.END, "No items in this playlist")
        else:
            for item in items:
                item_type = item.get('type', 'unknown')
                if item_type == 'track':
                    song = item.get('song', {})
                    title = song.get('title', 'Unknown')
                    artist = song.get('artist', 'Unknown')
                    items_listbox.insert(tk.END, f"  {title} - {artist}")
                elif item_type == 'group':
                    group_name = item.get('name', 'Unknown Group')
                    songs = item.get('songs', [])
                    items_listbox.insert(tk.END, f"[{group_name}] ({len(songs)} tracks)")

        # Close button
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

    def delete_playlist(self):
        """Delete selected playlist."""
        selection = self.playlists_listbox.curselection()
        if not selection or not self.playlists:
            messagebox.showwarning("No Selection", "Please select a playlist to delete")
            return

        playlist_index = selection[0]
        if playlist_index >= len(self.playlists):
            return

        playlist = self.playlists[playlist_index]
        name = playlist.get('name', 'Unknown')

        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}'?"):
            return

        # Delete in background
        def do_delete():
            try:
                if self.api.delete_playlist(playlist['id']):
                    self.root.after(0, lambda: messagebox.showinfo("Success",
                                                                   f"Playlist '{name}' deleted"))
                    self.root.after(0, self.load_playlists)
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error",
                                                                    "Failed to delete playlist"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error: {str(e)}"))

        threading.Thread(target=do_delete, daemon=True).start()

    def add_to_playlist(self):
        """Add selected song to a playlist."""
        # Get selected song
        selection = self.results_listbox.curselection()
        if not selection or not self.search_results:
            messagebox.showwarning("No Selection", "Please select a song to add")
            return

        song_index = selection[0]
        if song_index >= len(self.search_results):
            return

        song = self.search_results[song_index]

        # Get list of playlists
        if not self.playlists:
            messagebox.showinfo("No Playlists", "Please create a playlist first")
            return

        # Show selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Add to Playlist")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Select playlist:", font=("TkDefaultFont", 11)).pack(pady=10)

        # Playlist listbox
        list_frame = ttk.Frame(dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        playlist_select_listbox = tk.Listbox(list_frame, font=("TkDefaultFont", 10))
        pl_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=playlist_select_listbox.yview)
        playlist_select_listbox.configure(yscrollcommand=pl_scrollbar.set)

        playlist_select_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        pl_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for playlist in self.playlists:
            playlist_select_listbox.insert(tk.END, playlist.get('name', 'Unknown'))

        def add():
            sel = playlist_select_listbox.curselection()
            if not sel:
                messagebox.showwarning("No Selection", "Please select a playlist")
                return

            playlist = self.playlists[sel[0]]
            dialog.destroy()

            # Add to playlist in background
            def do_add():
                try:
                    if self.api.add_track_to_playlist(playlist['id'], song['id']):
                        song_title = song.get('title', 'Unknown')
                        playlist_name = playlist.get('name', 'Unknown')
                        self.root.after(0, lambda: messagebox.showinfo("Success",
                                                                       f"Added '{song_title}' to '{playlist_name}'"))
                        self.root.after(0, self.load_playlists)
                    else:
                        self.root.after(0, lambda: messagebox.showerror("Error",
                                                                        "Failed to add track"))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Error: {str(e)}"))

            threading.Thread(target=do_add, daemon=True).start()

        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add", command=add).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

        playlist_select_listbox.bind('<Double-Button-1>', lambda e: add())

    def run(self):
        """Start the GUI application."""
        self.root.mainloop()