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
        self.current_file_path = None
        self.song_duration = 0
        # Pre-buffering for gapless playback
        self.next_song_path = None
        self.next_song_info = None
    
    def play_audio_data(self, audio_data: bytes, song_info: Dict) -> bool:
        """Play audio from bytes data."""
        try:
            audio_file = io.BytesIO(audio_data)
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()

            self.current_song = song_info
            self.song_duration = song_info.get('duration', 0)
            self.is_playing = True
            self.is_paused = False
            return True
        except pygame.error as e:
            print(f"Pygame error: {e}")
            return False

    def play_audio_file(self, file_path: str, song_info: Dict) -> bool:
        """Play audio from file path."""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()

            self.current_song = song_info
            self.current_file_path = file_path
            self.song_duration = song_info.get('duration', 0)
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
        self.current_file_path = None
        self.song_duration = 0
    
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)."""
        pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
    
    def get_busy(self) -> bool:
        """Check if music is currently playing."""
        return pygame.mixer.music.get_busy()

    def get_position(self) -> float:
        """Get current playback position in seconds."""
        if not self.is_playing:
            return 0.0
        pos_ms = pygame.mixer.music.get_pos()
        return pos_ms / 1000.0 if pos_ms >= 0 else 0.0

    def get_duration(self) -> int:
        """Get total song duration in seconds."""
        return self.song_duration

    def seek(self, position_seconds: float) -> bool:
        """
        Seek to a specific position in the song.

        Args:
            position_seconds: Target position in seconds

        Returns:
            True if seek was successful, False otherwise

        Note: Seeking behavior is format-dependent:
        - MP3: Generally good seeking support
        - FLAC: May have limited backward seeking support
        - OGG: Generally good seeking support
        """
        if not self.is_playing or not self.current_file_path:
            return False

        try:
            # Clamp position to valid range
            position_seconds = max(0.0, min(position_seconds, float(self.song_duration)))

            # pygame.mixer.music.set_pos() takes position in seconds (float)
            # For MP3, it seeks to the closest frame
            # For OGG, it seeks accurately
            # For some formats, it may not work at all

            # Try direct seeking first
            try:
                pygame.mixer.music.set_pos(position_seconds)
                return True
            except pygame.error:
                # If direct seeking fails, try reload and play from position
                # This is more reliable but causes a brief interruption
                try:
                    was_paused = self.is_paused
                    volume = pygame.mixer.music.get_volume()

                    pygame.mixer.music.load(self.current_file_path)
                    pygame.mixer.music.play(start=position_seconds)
                    pygame.mixer.music.set_volume(volume)

                    if was_paused:
                        pygame.mixer.music.pause()

                    return True
                except Exception as e:
                    print(f"Fallback seek error: {e}")
                    return False

        except Exception as e:
            print(f"Seek error: {e}")
            return False

    def prepare_next(self, file_path: str, song_info: Dict) -> None:
        """
        Pre-buffer next song for gapless playback.

        Args:
            file_path: Path to the pre-downloaded audio file
            song_info: Song metadata dictionary
        """
        self.next_song_path = file_path
        self.next_song_info = song_info

    def play_next_immediate(self) -> bool:
        """
        Play the pre-buffered next song immediately.

        Returns:
            True if pre-buffered song was played, False if no pre-buffered song

        Note: This is designed for near-gapless playback. The gap will be
        the time it takes to stop current track, load new track, and start playback.
        """
        if not self.next_song_path or not self.next_song_info:
            return False

        try:
            # Play the pre-buffered song
            success = self.play_audio_file(self.next_song_path, self.next_song_info)

            # Clear pre-buffer
            self.next_song_path = None
            self.next_song_info = None

            return success
        except Exception as e:
            print(f"Error playing pre-buffered song: {e}")
            # Clear pre-buffer on error
            self.next_song_path = None
            self.next_song_info = None
            return False