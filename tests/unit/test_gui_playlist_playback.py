"""Unit tests for playlist playback functionality in gui_client.py"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from tests.fixtures.sample_responses import PLAYLIST_DETAIL_WITH_SONGS, PLAYLIST_EMPTY
import gui_client


@pytest.fixture
def mock_gui_client():
    """Create a mock GUI client for testing."""
    client = Mock(spec=gui_client.MusicGUIClient)

    # Add the actual methods we want to test
    client.convert_playlist_items_to_queue_format = gui_client.MusicGUIClient.convert_playlist_items_to_queue_format.__get__(client)
    client.play_playlist = gui_client.MusicGUIClient.play_playlist.__get__(client)
    client.play_playlist_from_list = gui_client.MusicGUIClient.play_playlist_from_list.__get__(client)

    # Mock the queue
    client.queue = Mock()
    client.queue.__len__ = Mock(return_value=1)
    client.queue.current_index = 0

    # Mock other dependencies
    client.update_queue_display = Mock()
    client.play_current_in_queue = Mock()
    client.show_status = Mock()
    client.api = Mock()
    client.root = Mock()
    client.playlists = []
    client.playlists_listbox = Mock()

    return client


class TestConvertPlaylistItemsToQueueFormat:
    """Tests for convert_playlist_items_to_queue_format method."""

    def test_convert_empty_playlist(self, mock_gui_client):
        """Test converting empty playlist items."""
        songs, groups = mock_gui_client.convert_playlist_items_to_queue_format([])
        assert songs == []
        assert groups == []

    def test_convert_tracks_only(self, mock_gui_client):
        """Test converting playlist with only tracks."""
        items = [
            {"type": "track", "song": {"id": "1", "title": "Song 1"}},
            {"type": "track", "song": {"id": "2", "title": "Song 2"}}
        ]
        songs, groups = mock_gui_client.convert_playlist_items_to_queue_format(items)

        assert len(songs) == 2
        assert groups == []
        assert songs[0]["id"] == "1"
        assert songs[1]["id"] == "2"

    def test_convert_groups_only(self, mock_gui_client):
        """Test converting playlist with only groups."""
        items = [
            {
                "type": "group",
                "name": "Album",
                "position": 0,
                "songs": [
                    {"id": "1", "title": "Song 1"},
                    {"id": "2", "title": "Song 2"}
                ]
            }
        ]
        songs, groups = mock_gui_client.convert_playlist_items_to_queue_format(items)

        assert len(songs) == 2
        assert len(groups) == 2
        assert groups[0] == (0, "group-0-Album")
        assert groups[1] == (1, "group-0-Album")

    def test_convert_mixed_items(self, mock_gui_client):
        """Test converting playlist with tracks and groups."""
        items = [
            {"type": "track", "song": {"id": "1", "title": "Song 1"}},
            {
                "type": "group",
                "name": "Album",
                "position": 1,
                "songs": [
                    {"id": "2", "title": "Song 2"},
                    {"id": "3", "title": "Song 3"}
                ]
            },
            {"type": "track", "song": {"id": "4", "title": "Song 4"}}
        ]
        songs, groups = mock_gui_client.convert_playlist_items_to_queue_format(items)

        assert len(songs) == 4
        assert len(groups) == 2
        assert songs[0]["id"] == "1"
        assert songs[1]["id"] == "2"
        assert songs[2]["id"] == "3"
        assert songs[3]["id"] == "4"
        assert groups[0] == (1, "group-1-Album")
        assert groups[1] == (2, "group-1-Album")

    def test_convert_with_missing_song_data(self, mock_gui_client):
        """Test converting playlist items with missing song data."""
        items = [
            {"type": "track", "song": {"id": "1", "title": "Song 1"}},
            {"type": "track", "song": None},  # Missing song
            {"type": "track"},  # No song field at all
            {"type": "track", "song": {"id": "2", "title": "Song 2"}}
        ]
        songs, groups = mock_gui_client.convert_playlist_items_to_queue_format(items)

        # Should only have valid songs
        assert len(songs) == 2
        assert songs[0]["id"] == "1"
        assert songs[1]["id"] == "2"

    def test_convert_with_unknown_item_type(self, mock_gui_client):
        """Test converting playlist with unknown item types."""
        items = [
            {"type": "track", "song": {"id": "1", "title": "Song 1"}},
            {"type": "unknown", "data": "something"},  # Unknown type
            {"type": "track", "song": {"id": "2", "title": "Song 2"}}
        ]
        songs, groups = mock_gui_client.convert_playlist_items_to_queue_format(items)

        # Unknown types should be ignored
        assert len(songs) == 2
        assert songs[0]["id"] == "1"
        assert songs[1]["id"] == "2"

    def test_convert_with_empty_group(self, mock_gui_client):
        """Test converting playlist with group containing no songs."""
        items = [
            {
                "type": "group",
                "name": "Empty Album",
                "position": 0,
                "songs": []
            },
            {"type": "track", "song": {"id": "1", "title": "Song 1"}}
        ]
        songs, groups = mock_gui_client.convert_playlist_items_to_queue_format(items)

        assert len(songs) == 1
        assert groups == []
        assert songs[0]["id"] == "1"


class TestPlayPlaylist:
    """Tests for play_playlist method."""

    def test_play_empty_playlist(self, mock_gui_client):
        """Test playing empty playlist shows message."""
        with patch('gui_client.messagebox.showinfo') as mock_info:
            mock_gui_client.play_playlist({"name": "Empty", "items": []})
            mock_info.assert_called_once()

    def test_play_playlist_with_invalid_items(self, mock_gui_client):
        """Test playing playlist with no valid songs shows warning."""
        with patch('gui_client.messagebox.showwarning') as mock_warning:
            # All items are invalid (no song data)
            playlist = {
                "name": "Invalid",
                "items": [
                    {"type": "track", "song": None},
                    {"type": "track"}
                ]
            }
            mock_gui_client.play_playlist(playlist)
            mock_warning.assert_called_once()

    def test_play_playlist_clears_auto_items(self, mock_gui_client):
        """Test that playing playlist clears auto items."""
        playlist = PLAYLIST_DETAIL_WITH_SONGS["data"]
        mock_gui_client.play_playlist(playlist)

        mock_gui_client.queue.clear_auto_items.assert_called_once()

    def test_play_playlist_adds_songs_to_queue(self, mock_gui_client):
        """Test that playing playlist adds songs to queue."""
        playlist = PLAYLIST_DETAIL_WITH_SONGS["data"]
        mock_gui_client.play_playlist(playlist)

        # Should call add_auto_songs with songs and groups
        mock_gui_client.queue.add_auto_songs.assert_called_once()
        args, kwargs = mock_gui_client.queue.add_auto_songs.call_args

        # Verify songs list
        songs = args[0]
        assert len(songs) == 4  # 2 tracks + 2 songs in group

        # Verify groups parameter
        groups = kwargs.get('groups')
        assert groups is not None
        assert len(groups) == 2  # 2 songs in the group

    def test_play_playlist_updates_queue_display(self, mock_gui_client):
        """Test that playing playlist updates queue display."""
        playlist = PLAYLIST_DETAIL_WITH_SONGS["data"]
        mock_gui_client.play_playlist(playlist)

        mock_gui_client.update_queue_display.assert_called_once()

    def test_play_playlist_starts_playback(self, mock_gui_client):
        """Test that playing playlist calls play_current_in_queue."""
        playlist = PLAYLIST_DETAIL_WITH_SONGS["data"]
        mock_gui_client.play_playlist(playlist)

        mock_gui_client.play_current_in_queue.assert_called_once()

    def test_play_playlist_shows_status(self, mock_gui_client):
        """Test that playing playlist shows status message."""
        playlist = PLAYLIST_DETAIL_WITH_SONGS["data"]
        mock_gui_client.play_playlist(playlist)

        mock_gui_client.show_status.assert_called()
        # Check that status includes playlist name
        call_args = mock_gui_client.show_status.call_args
        assert "Test Playlist" in call_args[0][0]

    def test_play_playlist_sets_current_index(self, mock_gui_client):
        """Test that playing playlist sets current index to 0."""
        playlist = PLAYLIST_DETAIL_WITH_SONGS["data"]
        mock_gui_client.play_playlist(playlist)

        assert mock_gui_client.queue.current_index == 0


class TestPlayPlaylistFromList:
    """Tests for play_playlist_from_list method."""

    def test_play_from_list_no_selection(self, mock_gui_client):
        """Test that no selection does nothing."""
        mock_gui_client.playlists_listbox = Mock()
        mock_gui_client.playlists_listbox.curselection.return_value = ()
        mock_gui_client.playlists = []

        mock_gui_client.play_playlist_from_list()

        # Should return early without calling API
        assert not mock_gui_client.show_status.called

    def test_play_from_list_no_playlists(self, mock_gui_client):
        """Test that no playlists does nothing."""
        mock_gui_client.playlists_listbox = Mock()
        mock_gui_client.playlists_listbox.curselection.return_value = (0,)
        mock_gui_client.playlists = None

        mock_gui_client.play_playlist_from_list()

        # Should return early without calling API
        assert not mock_gui_client.show_status.called

    def test_play_from_list_shows_loading_status(self, mock_gui_client):
        """Test that play_playlist_from_list shows loading status."""
        mock_gui_client.playlists_listbox = Mock()
        mock_gui_client.playlists_listbox.curselection.return_value = (0,)
        mock_gui_client.playlists = [{"id": "pl-1", "name": "Test"}]
        mock_gui_client.api = Mock()
        mock_gui_client.root = Mock()

        mock_gui_client.play_playlist_from_list()

        mock_gui_client.show_status.assert_called_with("Loading playlist...", "blue")

    def test_play_from_list_fetches_playlist(self, mock_gui_client):
        """Test that play_playlist_from_list fetches full playlist."""
        mock_gui_client.playlists_listbox = Mock()
        mock_gui_client.playlists_listbox.curselection.return_value = (0,)
        mock_gui_client.playlists = [{"id": "pl-1", "name": "Test"}]
        mock_gui_client.api = Mock()
        mock_gui_client.api.get_playlist.return_value = PLAYLIST_DETAIL_WITH_SONGS["data"]
        mock_gui_client.root = Mock()

        # Start the background thread
        with patch('gui_client.threading.Thread') as mock_thread:
            mock_gui_client.play_playlist_from_list()

            # Verify thread was created and started
            assert mock_thread.called
            thread_instance = mock_thread.return_value
            thread_instance.start.assert_called_once()
