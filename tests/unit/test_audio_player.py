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
