#!/usr/bin/env python3
"""
Audio Player for Music Streaming Client

Handles audio playback using pygame mixer with support for
play, pause, resume, stop, volume control, and status tracking.
"""

import pygame
import io
from typing import Dict, Optional


class AudioPlayer:
    """Audio playback manager using pygame."""
    
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        self.current_song = None
        self.is_playing = False
        self.is_paused = False
    
    def play_audio_data(self, audio_data: bytes, song_info: Dict) -> bool:
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