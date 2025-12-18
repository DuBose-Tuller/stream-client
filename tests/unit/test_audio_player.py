"""Unit tests for AudioPlayer."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from audio_player import AudioPlayer


class TestAudioPlayer:
    """Test suite for AudioPlayer class."""

    @pytest.fixture
    def mock_pygame(self):
        """Mock pygame module."""
        with patch('audio_player.pygame') as mock_pg:
            # Setup mixer mock
            mock_pg.mixer = MagicMock()
            mock_pg.mixer.init = MagicMock()
            mock_pg.mixer.music = MagicMock()
            mock_pg.error = Exception  # Define pygame.error
            yield mock_pg

    @pytest.fixture
    def audio_player(self, mock_pygame):
        """Create an AudioPlayer instance with mocked pygame."""
        return AudioPlayer()

    # ========== Initialization Tests ==========

    def test_audio_player_initialization(self, mock_pygame):
        """Test AudioPlayer initializes pygame mixer correctly."""
        player = AudioPlayer()

        # Verify mixer was initialized with correct parameters
        mock_pygame.mixer.init.assert_called_once_with(
            frequency=44100,
            size=-16,
            channels=2,
            buffer=1024
        )

        # Verify initial state
        assert player.is_playing is False
        assert player.is_paused is False
        assert player.current_song is None
        assert player.current_file_path is None
        assert player.song_duration == 0
        assert player.next_song_path is None
        assert player.next_song_info is None

    # ========== Play Audio Tests ==========

    def test_play_audio_data_success(self, audio_player, mock_pygame, sample_audio_data, sample_song):
        """Test playing audio data successfully."""
        # Setup mock
        mock_pygame.mixer.music.load = MagicMock()
        mock_pygame.mixer.music.play = MagicMock()

        # Play audio
        result = audio_player.play_audio_data(sample_audio_data, sample_song)

        # Verify success
        assert result is True
        assert audio_player.is_playing is True
        assert audio_player.is_paused is False
        assert audio_player.current_song == sample_song

        # Verify pygame calls
        mock_pygame.mixer.music.load.assert_called_once()
        mock_pygame.mixer.music.play.assert_called_once()

    def test_play_audio_data_with_none_data(self, audio_player, mock_pygame, sample_song):
        """Test playing with None audio data."""
        # This will cause pygame.error when trying to load None
        mock_pygame.mixer.music.load.side_effect = mock_pygame.error("Invalid data")

        result = audio_player.play_audio_data(None, sample_song)

        assert result is False
        assert audio_player.is_playing is False

    def test_play_audio_data_with_empty_data(self, audio_player, mock_pygame, sample_song):
        """Test playing with empty audio data."""
        # This will cause pygame.error when trying to load empty data
        mock_pygame.mixer.music.load.side_effect = mock_pygame.error("Invalid data")

        result = audio_player.play_audio_data(b"", sample_song)

        assert result is False
        assert audio_player.is_playing is False

    def test_play_audio_data_pygame_error(self, audio_player, mock_pygame, sample_audio_data, sample_song):
        """Test playing audio when pygame raises an error."""
        # Make pygame.mixer.music.load raise a pygame.error
        mock_pygame.mixer.music.load.side_effect = mock_pygame.error("Invalid audio format")

        result = audio_player.play_audio_data(sample_audio_data, sample_song)

        assert result is False
        assert audio_player.is_playing is False

    def test_play_audio_replaces_current_song(self, audio_player, mock_pygame, sample_audio_data):
        """Test that playing new audio replaces current song."""
        song1 = {"id": "1", "title": "Song 1"}
        song2 = {"id": "2", "title": "Song 2"}

        # Play first song
        audio_player.play_audio_data(sample_audio_data, song1)
        assert audio_player.current_song == song1

        # Play second song (implementation just loads new audio without stopping)
        audio_player.play_audio_data(sample_audio_data, song2)

        assert audio_player.current_song == song2
        assert audio_player.is_playing is True

    # ========== Pause Tests ==========

    def test_pause_while_playing(self, audio_player, mock_pygame, sample_audio_data, sample_song):
        """Test pausing while audio is playing."""
        # Start playing
        audio_player.play_audio_data(sample_audio_data, sample_song)
        mock_pygame.mixer.music.pause = MagicMock()

        # Pause
        audio_player.pause()

        assert audio_player.is_paused is True
        assert audio_player.is_playing is True  # Still "playing" but paused
        mock_pygame.mixer.music.pause.assert_called_once()

    def test_pause_while_not_playing(self, audio_player, mock_pygame):
        """Test pausing when nothing is playing."""
        mock_pygame.mixer.music.pause = MagicMock()

        audio_player.pause()

        # Implementation has guard clause - won't pause if not playing
        mock_pygame.mixer.music.pause.assert_not_called()
        assert audio_player.is_paused is False

    def test_pause_already_paused(self, audio_player, mock_pygame, sample_audio_data, sample_song):
        """Test pausing when already paused."""
        audio_player.play_audio_data(sample_audio_data, sample_song)
        audio_player.pause()

        mock_pygame.mixer.music.pause = MagicMock()
        audio_player.pause()

        # Implementation has guard clause - won't pause if already paused
        mock_pygame.mixer.music.pause.assert_not_called()

    # ========== Resume Tests ==========

    def test_resume_after_pause(self, audio_player, mock_pygame, sample_audio_data, sample_song):
        """Test resuming after pause."""
        # Play and pause
        audio_player.play_audio_data(sample_audio_data, sample_song)
        audio_player.pause()

        mock_pygame.mixer.music.unpause = MagicMock()

        # Resume
        audio_player.resume()

        assert audio_player.is_paused is False
        assert audio_player.is_playing is True
        mock_pygame.mixer.music.unpause.assert_called_once()

    def test_resume_while_not_paused(self, audio_player, mock_pygame, sample_audio_data, sample_song):
        """Test resuming when not paused."""
        audio_player.play_audio_data(sample_audio_data, sample_song)

        mock_pygame.mixer.music.unpause = MagicMock()
        audio_player.resume()

        # Implementation has guard clause - won't unpause if not paused
        mock_pygame.mixer.music.unpause.assert_not_called()

    def test_resume_while_not_playing(self, audio_player, mock_pygame):
        """Test resuming when nothing was playing."""
        mock_pygame.mixer.music.unpause = MagicMock()

        audio_player.resume()

        # Implementation has guard clause - won't unpause if not playing
        mock_pygame.mixer.music.unpause.assert_not_called()
        assert audio_player.is_paused is False

    # ========== Stop Tests ==========

    def test_stop_while_playing(self, audio_player, mock_pygame, sample_audio_data, sample_song):
        """Test stopping while audio is playing."""
        audio_player.play_audio_data(sample_audio_data, sample_song)

        mock_pygame.mixer.music.stop = MagicMock()

        audio_player.stop()

        assert audio_player.is_playing is False
        assert audio_player.is_paused is False
        assert audio_player.current_song is None
        assert audio_player.current_file_path is None
        assert audio_player.song_duration == 0
        mock_pygame.mixer.music.stop.assert_called_once()

    def test_stop_while_paused(self, audio_player, mock_pygame, sample_audio_data, sample_song):
        """Test stopping while audio is paused."""
        audio_player.play_audio_data(sample_audio_data, sample_song)
        audio_player.pause()

        mock_pygame.mixer.music.stop = MagicMock()

        audio_player.stop()

        assert audio_player.is_playing is False
        assert audio_player.is_paused is False
        mock_pygame.mixer.music.stop.assert_called_once()

    def test_stop_while_not_playing(self, audio_player, mock_pygame):
        """Test stopping when nothing is playing."""
        mock_pygame.mixer.music.stop = MagicMock()

        audio_player.stop()

        mock_pygame.mixer.music.stop.assert_called_once()
        assert audio_player.is_playing is False

    # ========== Volume Tests ==========

    def test_set_volume_valid_range(self, audio_player, mock_pygame):
        """Test setting volume within valid range (0.0-1.0)."""
        mock_pygame.mixer.music.set_volume = MagicMock()

        audio_player.set_volume(0.5)

        mock_pygame.mixer.music.set_volume.assert_called_once_with(0.5)

    def test_set_volume_minimum(self, audio_player, mock_pygame):
        """Test setting volume to minimum (0.0)."""
        mock_pygame.mixer.music.set_volume = MagicMock()

        audio_player.set_volume(0.0)

        mock_pygame.mixer.music.set_volume.assert_called_once_with(0.0)

    def test_set_volume_maximum(self, audio_player, mock_pygame):
        """Test setting volume to maximum (1.0)."""
        mock_pygame.mixer.music.set_volume = MagicMock()

        audio_player.set_volume(1.0)

        mock_pygame.mixer.music.set_volume.assert_called_once_with(1.0)

    def test_set_volume_above_maximum(self, audio_player, mock_pygame):
        """Test setting volume above maximum (should be clamped to 1.0)."""
        mock_pygame.mixer.music.set_volume = MagicMock()

        # Implementation clamps to 1.0
        audio_player.set_volume(1.5)

        mock_pygame.mixer.music.set_volume.assert_called_once_with(1.0)

    def test_set_volume_below_minimum(self, audio_player, mock_pygame):
        """Test setting volume below minimum (should be clamped to 0.0)."""
        mock_pygame.mixer.music.set_volume = MagicMock()

        # Implementation clamps to 0.0
        audio_player.set_volume(-0.5)

        mock_pygame.mixer.music.set_volume.assert_called_once_with(0.0)

    # ========== Get Busy Tests ==========

    def test_get_busy_while_playing(self, audio_player, mock_pygame, sample_audio_data, sample_song):
        """Test get_busy while audio is playing."""
        audio_player.play_audio_data(sample_audio_data, sample_song)

        mock_pygame.mixer.music.get_busy.return_value = True

        result = audio_player.get_busy()

        assert result is True
        mock_pygame.mixer.music.get_busy.assert_called_once()

    def test_get_busy_while_not_playing(self, audio_player, mock_pygame):
        """Test get_busy when nothing is playing."""
        mock_pygame.mixer.music.get_busy.return_value = False

        result = audio_player.get_busy()

        assert result is False

    def test_get_busy_while_paused(self, audio_player, mock_pygame, sample_audio_data, sample_song):
        """Test get_busy while audio is paused."""
        audio_player.play_audio_data(sample_audio_data, sample_song)
        audio_player.pause()

        # When paused, pygame might still report busy
        mock_pygame.mixer.music.get_busy.return_value = True

        result = audio_player.get_busy()

        assert result is True

    # ========== State Consistency Tests ==========

    def test_play_pause_resume_stop_sequence(self, audio_player, mock_pygame, sample_audio_data, sample_song):
        """Test a full sequence of play, pause, resume, stop."""
        # Play
        audio_player.play_audio_data(sample_audio_data, sample_song)
        assert audio_player.is_playing is True
        assert audio_player.is_paused is False

        # Pause
        audio_player.pause()
        assert audio_player.is_playing is True
        assert audio_player.is_paused is True

        # Resume
        audio_player.resume()
        assert audio_player.is_playing is True
        assert audio_player.is_paused is False

        # Stop
        audio_player.stop()
        assert audio_player.is_playing is False
        assert audio_player.is_paused is False
        assert audio_player.current_song is None

    def test_multiple_play_calls_update_state(self, audio_player, mock_pygame, sample_audio_data):
        """Test that multiple play calls properly update state."""
        song1 = {"id": "1", "title": "First"}
        song2 = {"id": "2", "title": "Second"}
        song3 = {"id": "3", "title": "Third"}

        audio_player.play_audio_data(sample_audio_data, song1)
        assert audio_player.current_song == song1

        audio_player.play_audio_data(sample_audio_data, song2)
        assert audio_player.current_song == song2

        audio_player.play_audio_data(sample_audio_data, song3)
        assert audio_player.current_song == song3

    # ========== Error Handling Tests ==========

    def test_pygame_not_initialized_error(self, mock_pygame):
        """Test handling when pygame initialization fails."""
        mock_pygame.mixer.init.side_effect = Exception("Pygame init failed")

        with pytest.raises(Exception):
            AudioPlayer()

    # ========== Position and Duration Tests ==========

    def test_get_position_while_playing(self, audio_player, mock_pygame, sample_audio_data, sample_song):
        """Test getting playback position while playing."""
        audio_player.play_audio_data(sample_audio_data, sample_song)

        mock_pygame.mixer.music.get_pos.return_value = 5000

        position = audio_player.get_position()

        assert position == 5.0
        mock_pygame.mixer.music.get_pos.assert_called_once()

    def test_get_position_while_not_playing(self, audio_player, mock_pygame):
        """Test getting position when nothing is playing."""
        position = audio_player.get_position()

        assert position == 0.0
        mock_pygame.mixer.music.get_pos.assert_not_called()

    def test_get_position_negative_value(self, audio_player, mock_pygame, sample_audio_data, sample_song):
        """Test getting position when pygame returns negative value."""
        audio_player.play_audio_data(sample_audio_data, sample_song)

        mock_pygame.mixer.music.get_pos.return_value = -1

        position = audio_player.get_position()

        assert position == 0.0

    def test_get_duration_after_play(self, audio_player, mock_pygame, sample_audio_data):
        """Test getting duration after playing a song."""
        song = {"id": "1", "title": "Test", "duration": 180}
        audio_player.play_audio_data(sample_audio_data, song)

        duration = audio_player.get_duration()

        assert duration == 180

    def test_get_duration_no_song(self, audio_player):
        """Test getting duration when no song is loaded."""
        duration = audio_player.get_duration()

        assert duration == 0

    def test_get_duration_song_without_duration(self, audio_player, mock_pygame, sample_audio_data):
        """Test getting duration for song without duration field."""
        song = {"id": "1", "title": "Test"}
        audio_player.play_audio_data(sample_audio_data, song)

        duration = audio_player.get_duration()

        assert duration == 0

    # ========== Seeking Tests ==========

    def test_seek_while_playing_success(self, audio_player, mock_pygame, sample_audio_data):
        """Test seeking while playing (direct seek succeeds)."""
        song = {"id": "1", "title": "Test", "duration": 180}
        audio_player.play_audio_file("/tmp/test.mp3", song)

        mock_pygame.mixer.music.set_pos = MagicMock()

        result = audio_player.seek(60.0)

        assert result is True
        mock_pygame.mixer.music.set_pos.assert_called_once_with(60.0)

    def test_seek_while_playing_fallback_reload(self, audio_player, mock_pygame, sample_audio_data):
        """Test seeking with fallback to reload when direct seek fails."""
        song = {"id": "1", "title": "Test", "duration": 180}
        audio_player.play_audio_file("/tmp/test.mp3", song)

        mock_pygame.mixer.music.set_pos = MagicMock(side_effect=mock_pygame.error("Seek not supported"))
        mock_pygame.mixer.music.load = MagicMock()
        mock_pygame.mixer.music.play = MagicMock()
        mock_pygame.mixer.music.get_volume.return_value = 0.8
        mock_pygame.mixer.music.set_volume = MagicMock()

        result = audio_player.seek(60.0)

        assert result is True
        mock_pygame.mixer.music.load.assert_called_once_with("/tmp/test.mp3")
        mock_pygame.mixer.music.play.assert_called_once_with(start=60.0)
        mock_pygame.mixer.music.set_volume.assert_called_once_with(0.8)

    def test_seek_while_playing_fallback_preserves_pause(self, audio_player, mock_pygame, sample_audio_data):
        """Test that seeking with fallback preserves pause state."""
        song = {"id": "1", "title": "Test", "duration": 180}
        audio_player.play_audio_file("/tmp/test.mp3", song)
        audio_player.pause()

        mock_pygame.mixer.music.set_pos = MagicMock(side_effect=mock_pygame.error("Seek not supported"))
        mock_pygame.mixer.music.load = MagicMock()
        mock_pygame.mixer.music.play = MagicMock()
        mock_pygame.mixer.music.get_volume.return_value = 0.5
        mock_pygame.mixer.music.pause = MagicMock()

        result = audio_player.seek(30.0)

        assert result is True
        mock_pygame.mixer.music.pause.assert_called_once()

    def test_seek_while_not_playing(self, audio_player, mock_pygame):
        """Test seeking when nothing is playing."""
        result = audio_player.seek(30.0)

        assert result is False
        mock_pygame.mixer.music.set_pos.assert_not_called()

    def test_seek_without_file_path(self, audio_player, mock_pygame, sample_audio_data):
        """Test seeking without a file path loaded."""
        song = {"id": "1", "title": "Test", "duration": 180}
        audio_player.play_audio_data(sample_audio_data, song)

        result = audio_player.seek(30.0)

        assert result is False

    def test_seek_clamps_negative_position(self, audio_player, mock_pygame):
        """Test that seeking to negative position clamps to 0."""
        song = {"id": "1", "title": "Test", "duration": 180}
        audio_player.play_audio_file("/tmp/test.mp3", song)

        mock_pygame.mixer.music.set_pos = MagicMock()

        audio_player.seek(-10.0)

        mock_pygame.mixer.music.set_pos.assert_called_once_with(0.0)

    def test_seek_clamps_position_beyond_duration(self, audio_player, mock_pygame):
        """Test that seeking beyond duration clamps to duration."""
        song = {"id": "1", "title": "Test", "duration": 180}
        audio_player.play_audio_file("/tmp/test.mp3", song)

        mock_pygame.mixer.music.set_pos = MagicMock()

        audio_player.seek(200.0)

        mock_pygame.mixer.music.set_pos.assert_called_once_with(180.0)

    def test_seek_with_exception(self, audio_player, mock_pygame):
        """Test seeking handles unexpected exceptions gracefully."""
        song = {"id": "1", "title": "Test", "duration": 180}
        audio_player.play_audio_file("/tmp/test.mp3", song)

        # Make both set_pos and the fallback load fail
        mock_pygame.mixer.music.set_pos = MagicMock(side_effect=mock_pygame.error("Seek not supported"))
        mock_pygame.mixer.music.load = MagicMock(side_effect=Exception("Load failed"))

        result = audio_player.seek(60.0)

        assert result is False

    # ========== Pre-buffering Tests ==========

    def test_prepare_next(self, audio_player, sample_song):
        """Test prepare_next stores pre-buffered song info."""
        file_path = "/tmp/next_song.mp3"

        audio_player.prepare_next(file_path, sample_song)

        assert audio_player.next_song_path == file_path
        assert audio_player.next_song_info == sample_song

    def test_prepare_next_overwrites_previous(self, audio_player, sample_song):
        """Test prepare_next overwrites previously buffered song."""
        file_path_1 = "/tmp/song1.mp3"
        file_path_2 = "/tmp/song2.mp3"
        song_2 = {'id': '2', 'title': 'Song 2', 'artist': 'Artist 2', 'duration': 200}

        audio_player.prepare_next(file_path_1, sample_song)
        audio_player.prepare_next(file_path_2, song_2)

        assert audio_player.next_song_path == file_path_2
        assert audio_player.next_song_info == song_2

    def test_play_next_immediate_with_buffered_song(self, audio_player, mock_pygame, sample_song):
        """Test play_next_immediate plays pre-buffered song."""
        file_path = "/tmp/next_song.mp3"
        audio_player.prepare_next(file_path, sample_song)

        result = audio_player.play_next_immediate()

        assert result is True
        # Verify pygame.mixer.music.load was called with pre-buffered path
        mock_pygame.mixer.music.load.assert_called_with(file_path)
        mock_pygame.mixer.music.play.assert_called()
        # Verify pre-buffer was cleared
        assert audio_player.next_song_path is None
        assert audio_player.next_song_info is None
        # Verify player state updated
        assert audio_player.is_playing is True
        assert audio_player.current_song == sample_song

    def test_play_next_immediate_without_buffered_song(self, audio_player, mock_pygame):
        """Test play_next_immediate returns False when no pre-buffered song."""
        result = audio_player.play_next_immediate()

        assert result is False
        mock_pygame.mixer.music.load.assert_not_called()
        mock_pygame.mixer.music.play.assert_not_called()

    def test_play_next_immediate_clears_buffer_on_error(self, audio_player, mock_pygame, sample_song):
        """Test play_next_immediate clears pre-buffer even on error."""
        file_path = "/tmp/next_song.mp3"
        audio_player.prepare_next(file_path, sample_song)

        # Make play fail
        mock_pygame.mixer.music.load.side_effect = Exception("Load failed")

        result = audio_player.play_next_immediate()

        assert result is False
        # Verify pre-buffer was cleared despite error
        assert audio_player.next_song_path is None
        assert audio_player.next_song_info is None

    def test_play_next_immediate_partial_buffer(self, audio_player, mock_pygame, sample_song):
        """Test play_next_immediate when only path is set (not info)."""
        audio_player.next_song_path = "/tmp/song.mp3"
        audio_player.next_song_info = None

        result = audio_player.play_next_immediate()

        assert result is False
        mock_pygame.mixer.music.load.assert_not_called()
