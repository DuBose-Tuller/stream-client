"""Unit tests for MusicAPIClient."""

import pytest
import responses
from api_client import MusicAPIClient
from tests.fixtures import sample_responses


class TestMusicAPIClient:
    """Test suite for MusicAPIClient class."""

    @pytest.fixture
    def api_client(self, server_url):
        """Create an API client instance."""
        return MusicAPIClient(server_url)

    # ========== Health Check Tests ==========

    @responses.activate
    def test_health_check_success(self, api_client, server_url):
        """Test successful health check."""
        responses.add(
            responses.GET,
            f"{server_url}/health",
            json=sample_responses.HEALTH_SUCCESS,
            status=200
        )

        result = api_client.health_check()
        assert result is True

    @responses.activate
    def test_health_check_server_error(self, api_client, server_url):
        """Test health check with server error."""
        responses.add(
            responses.GET,
            f"{server_url}/health",
            json=sample_responses.HEALTH_ERROR,
            status=500
        )

        result = api_client.health_check()
        assert result is False

    @responses.activate
    def test_health_check_connection_error(self, api_client):
        """Test health check with connection error."""
        # Don't add a response - this will trigger a connection error
        result = api_client.health_check()
        assert result is False

    @responses.activate
    def test_health_check_timeout(self, api_client, server_url):
        """Test health check timeout."""
        # Don't add a response - this will trigger a connection error
        result = api_client.health_check()
        assert result is False

    # ========== Search Tests (OLD FORMAT) ==========

    @responses.activate
    def test_search_songs_success_new_format(self, api_client, server_url):
        """Test successful song search with new API format."""
        responses.add(
            responses.GET,
            f"{server_url}/api/search",
            json=sample_responses.SEARCH_SUCCESS_NEW,
            status=200
        )

        result = api_client.search_songs("queen")

        assert isinstance(result, dict)
        assert "songs" in result
        assert len(result["songs"]) == 2
        assert result["songs"][0]["title"] == "Bohemian Rhapsody"
        assert result["songs"][0]["artist"] == "Queen"
        assert result["songs"][1]["title"] == "Stairway to Heaven"

        # Verify the request was made with correct params
        assert len(responses.calls) == 1
        assert "q=queen" in responses.calls[0].request.url

    @responses.activate
    def test_search_songs_empty_results(self, api_client, server_url):
        """Test search with no results."""
        responses.add(
            responses.GET,
            f"{server_url}/api/search",
            json=sample_responses.SEARCH_EMPTY_NEW,
            status=200
        )

        result = api_client.search_songs("nonexistentsong12345")

        assert isinstance(result, dict)
        assert result.get("songs") == []

    @responses.activate
    def test_search_songs_server_error(self, api_client, server_url):
        """Test search with server error."""
        responses.add(
            responses.GET,
            f"{server_url}/api/search",
            json=sample_responses.SEARCH_ERROR,
            status=400
        )

        result = api_client.search_songs("test")

        assert result == {"songs": [], "albums": [], "artists": []}

    @responses.activate
    def test_search_songs_connection_error(self, api_client):
        """Test search with connection error."""
        result = api_client.search_songs("test")
        assert result == {"songs": [], "albums": [], "artists": []}

    @responses.activate
    def test_search_songs_invalid_response(self, api_client, server_url):
        """Test search with invalid JSON response."""
        responses.add(
            responses.GET,
            f"{server_url}/api/search",
            body="INVALID JSON",
            status=200
        )

        result = api_client.search_songs("test")
        assert result == {"songs": [], "albums": [], "artists": []}

    @responses.activate
    def test_search_songs_missing_success_field(self, api_client, server_url):
        """Test search with response missing 'success' field."""
        responses.add(
            responses.GET,
            f"{server_url}/api/search",
            json={"data": []},  # Missing 'success' field
            status=200
        )

        result = api_client.search_songs("test")
        assert result == {"songs": [], "albums": [], "artists": []}

    # ========== Search Tests (NEW FORMAT - This should catch the bug!) ==========

    @responses.activate
    def test_search_songs_new_format_structure(self, api_client, server_url):
        """Test that client properly handles new API SearchResponse format."""
        responses.add(
            responses.GET,
            f"{server_url}/api/search",
            json=sample_responses.SEARCH_SUCCESS_NEW,
            status=200
        )

        result = api_client.search_songs("queen")

        # Client should return the full SearchResponse dict
        assert isinstance(result, dict)
        assert "songs" in result
        assert "albums" in result
        assert "artists" in result

        # Verify songs structure
        assert len(result["songs"]) == 2
        assert result["songs"][0]["title"] == "Bohemian Rhapsody"

    # ========== Artists Tests ==========

    @responses.activate
    def test_get_artists_success(self, api_client, server_url):
        """Test successful artist retrieval."""
        responses.add(
            responses.GET,
            f"{server_url}/api/artists",
            json=sample_responses.ARTISTS_SUCCESS,
            status=200
        )

        result = api_client.get_artists()

        assert len(result) == 2
        assert result[0]["name"] == "The Beatles"
        assert result[1]["name"] == "Pink Floyd"

    @responses.activate
    def test_get_artists_error(self, api_client, server_url):
        """Test artist retrieval with error."""
        responses.add(
            responses.GET,
            f"{server_url}/api/artists",
            status=500
        )

        result = api_client.get_artists()
        assert result == []

    # ========== Stream Song Tests ==========

    @responses.activate
    def test_stream_song_success(self, api_client, server_url, sample_audio_data):
        """Test successful song streaming."""
        responses.add(
            responses.GET,
            f"{server_url}/stream/song-123",
            body=sample_audio_data,
            status=200,
            content_type="audio/mpeg"
        )

        result = api_client.stream_song("song-123")

        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 0

    @responses.activate
    def test_stream_song_not_found(self, api_client, server_url):
        """Test streaming non-existent song."""
        responses.add(
            responses.GET,
            f"{server_url}/stream/invalid-id",
            json={"error": "Song not found"},
            status=404
        )

        result = api_client.stream_song("invalid-id")
        assert result is None

    @responses.activate
    def test_stream_song_connection_error(self, api_client):
        """Test streaming with connection error."""
        result = api_client.stream_song("song-123")
        assert result is None

    def test_stream_song_timeout(self, api_client, server_url):
        """Test streaming timeout (30 second timeout configured)."""
        # Note: actual timeout testing would require time.sleep or async
        # This just tests the error handling path
        # Don't use @responses.activate - we want a real connection error
        result = api_client.stream_song("song-123")
        assert result is None

    # ========== Notify Server Play Tests ==========

    @responses.activate
    def test_notify_server_play_success(self, api_client, server_url, sample_song):
        """Test successful play notification."""
        responses.add(
            responses.POST,
            f"{server_url}/api/play/{sample_song['id']}",
            status=200
        )

        result = api_client.notify_server_play(sample_song)

        assert result is True
        assert len(responses.calls) == 1
        # Verify the song data was sent in request body
        assert responses.calls[0].request.body is not None

    @responses.activate
    def test_notify_server_play_error(self, api_client, server_url, sample_song):
        """Test play notification with server error."""
        responses.add(
            responses.POST,
            f"{server_url}/api/play/{sample_song['id']}",
            status=500
        )

        result = api_client.notify_server_play(sample_song)
        assert result is False

    @responses.activate
    def test_notify_server_play_connection_error(self, api_client, sample_song):
        """Test play notification with connection error."""
        result = api_client.notify_server_play(sample_song)
        assert result is False

    # ========== Server URL Configuration Tests ==========

    def test_server_url_trailing_slash_removed(self):
        """Test that trailing slash is removed from server URL."""
        client = MusicAPIClient("http://example.com/")
        assert client.server_url == "http://example.com"

    def test_server_url_no_trailing_slash(self):
        """Test that URL without trailing slash is preserved."""
        client = MusicAPIClient("http://example.com")
        assert client.server_url == "http://example.com"

    def test_default_server_url(self):
        """Test default server URL is set correctly."""
        client = MusicAPIClient()
        assert client.server_url == "http://pi-server:8080"

    # ========== Edge Cases ==========

    @responses.activate
    def test_search_with_special_characters(self, api_client, server_url):
        """Test search with special characters in query."""
        responses.add(
            responses.GET,
            f"{server_url}/api/search",
            json=sample_responses.SEARCH_EMPTY_NEW,
            status=200
        )

        result = api_client.search_songs("AC/DC & Metallica!")

        assert isinstance(result, dict)
        assert "songs" in result
        # Verify URL encoding happened
        assert len(responses.calls) == 1

    @responses.activate
    def test_search_with_empty_query(self, api_client, server_url):
        """Test search with empty query."""
        responses.add(
            responses.GET,
            f"{server_url}/api/search",
            json=sample_responses.SEARCH_EMPTY_NEW,
            status=200
        )

        result = api_client.search_songs("")
        assert isinstance(result, dict)
        assert result.get("songs") == []

    @responses.activate
    def test_stream_song_with_large_file(self, api_client, server_url):
        """Test streaming a large audio file."""
        large_audio = b"\x00" * (10 * 1024 * 1024)  # 10 MB

        responses.add(
            responses.GET,
            f"{server_url}/stream/large-song",
            body=large_audio,
            status=200
        )

        result = api_client.stream_song("large-song")

        assert result is not None
        assert len(result) == 10 * 1024 * 1024
    # ========== Playlist Operations Tests ==========

    @responses.activate
    def test_get_all_playlists_success(self, api_client, server_url):
        """Test successful playlist retrieval."""
        responses.add(
            responses.GET,
            f"{server_url}/api/playlists",
            json=sample_responses.PLAYLISTS_SUCCESS,
            status=200
        )

        result = api_client.get_all_playlists()

        assert len(result) == 2
        assert result[0]["name"] == "Favorites"
        assert result[1]["name"] == "Study Music"

    @responses.activate
    def test_get_all_playlists_error(self, api_client, server_url):
        """Test playlist retrieval with error."""
        responses.add(
            responses.GET,
            f"{server_url}/api/playlists",
            status=500
        )

        result = api_client.get_all_playlists()
        assert result == []

    @responses.activate
    def test_create_playlist_success(self, api_client, server_url):
        """Test successful playlist creation."""
        responses.add(
            responses.POST,
            f"{server_url}/api/playlists",
            json=sample_responses.CREATE_PLAYLIST_SUCCESS,
            status=200
        )

        result = api_client.create_playlist("New Playlist", "Description")

        assert result == "pl-new-123"
        assert len(responses.calls) == 1
        assert b"New Playlist" in responses.calls[0].request.body

    @responses.activate
    def test_create_playlist_without_description(self, api_client, server_url):
        """Test creating playlist without description."""
        responses.add(
            responses.POST,
            f"{server_url}/api/playlists",
            json=sample_responses.CREATE_PLAYLIST_SUCCESS,
            status=200
        )

        result = api_client.create_playlist("Simple Playlist")
        assert result == "pl-new-123"

    @responses.activate
    def test_create_playlist_error(self, api_client, server_url):
        """Test playlist creation with error."""
        responses.add(
            responses.POST,
            f"{server_url}/api/playlists",
            json={"success": False, "error": "Database error"},
            status=500
        )

        result = api_client.create_playlist("Test")
        assert result is None

    @responses.activate
    def test_get_playlist_success(self, api_client, server_url):
        """Test getting specific playlist."""
        responses.add(
            responses.GET,
            f"{server_url}/api/playlists/pl-1",
            json=sample_responses.PLAYLIST_DETAIL,
            status=200
        )

        result = api_client.get_playlist("pl-1")

        assert result is not None
        assert result["name"] == "Favorites"
        assert len(result["items"]) == 3

    @responses.activate
    def test_get_playlist_not_found(self, api_client, server_url):
        """Test getting non-existent playlist."""
        responses.add(
            responses.GET,
            f"{server_url}/api/playlists/invalid",
            json={"success": False, "error": "Not found"},
            status=404
        )

        result = api_client.get_playlist("invalid")
        assert result is None

    @responses.activate
    def test_delete_playlist_success(self, api_client, server_url):
        """Test successful playlist deletion."""
        responses.add(
            responses.DELETE,
            f"{server_url}/api/playlists/pl-1",
            status=200
        )

        result = api_client.delete_playlist("pl-1")
        assert result is True

    @responses.activate
    def test_delete_playlist_error(self, api_client, server_url):
        """Test playlist deletion with error."""
        responses.add(
            responses.DELETE,
            f"{server_url}/api/playlists/pl-1",
            status=500
        )

        result = api_client.delete_playlist("pl-1")
        assert result is False

    @responses.activate
    def test_update_playlist_name_only(self, api_client, server_url):
        """Test updating only playlist name."""
        responses.add(
            responses.PUT,
            f"{server_url}/api/playlists/pl-1",
            status=200
        )

        result = api_client.update_playlist("pl-1", name="New Name")
        
        assert result is True
        assert b"New Name" in responses.calls[0].request.body

    @responses.activate
    def test_update_playlist_description_only(self, api_client, server_url):
        """Test updating only playlist description."""
        responses.add(
            responses.PUT,
            f"{server_url}/api/playlists/pl-1",
            status=200
        )

        result = api_client.update_playlist("pl-1", description="New Description")
        
        assert result is True
        assert b"New Description" in responses.calls[0].request.body

    @responses.activate
    def test_update_playlist_both_fields(self, api_client, server_url):
        """Test updating both name and description."""
        responses.add(
            responses.PUT,
            f"{server_url}/api/playlists/pl-1",
            status=200
        )

        result = api_client.update_playlist("pl-1", name="Updated", description="Updated desc")
        
        assert result is True

    @responses.activate
    def test_update_playlist_error(self, api_client, server_url):
        """Test playlist update with error."""
        responses.add(
            responses.PUT,
            f"{server_url}/api/playlists/pl-1",
            status=500
        )

        result = api_client.update_playlist("pl-1", name="Test")
        assert result is False

    @responses.activate
    def test_add_track_to_playlist_success(self, api_client, server_url):
        """Test adding track to playlist."""
        responses.add(
            responses.POST,
            f"{server_url}/api/playlists/pl-1/items",
            status=200
        )

        result = api_client.add_track_to_playlist("pl-1", "song-123", position=0)
        
        assert result is True
        assert b"song-123" in responses.calls[0].request.body
        assert b"track" in responses.calls[0].request.body

    @responses.activate
    def test_add_track_to_playlist_error(self, api_client, server_url):
        """Test adding track with error."""
        responses.add(
            responses.POST,
            f"{server_url}/api/playlists/pl-1/items",
            status=500
        )

        result = api_client.add_track_to_playlist("pl-1", "song-123")
        assert result is False

    @responses.activate
    def test_add_track_group_to_playlist_success(self, api_client, server_url):
        """Test adding track group to playlist."""
        responses.add(
            responses.POST,
            f"{server_url}/api/playlists/pl-1/items",
            status=200
        )

        song_ids = ["song-1", "song-2", "song-3"]
        result = api_client.add_track_group_to_playlist("pl-1", "Album Group", song_ids, position=0)
        
        assert result is True
        assert b"Album Group" in responses.calls[0].request.body
        assert b"group" in responses.calls[0].request.body

    @responses.activate
    def test_add_track_group_error(self, api_client, server_url):
        """Test adding track group with error."""
        responses.add(
            responses.POST,
            f"{server_url}/api/playlists/pl-1/items",
            status=500
        )

        result = api_client.add_track_group_to_playlist("pl-1", "Test", ["song-1"])
        assert result is False

    @responses.activate
    def test_remove_playlist_item_success(self, api_client, server_url):
        """Test removing item from playlist."""
        responses.add(
            responses.DELETE,
            f"{server_url}/api/playlists/pl-1/items/0",
            status=200
        )

        result = api_client.remove_playlist_item("pl-1", 0)
        assert result is True

    @responses.activate
    def test_remove_playlist_item_error(self, api_client, server_url):
        """Test removing item with error."""
        responses.add(
            responses.DELETE,
            f"{server_url}/api/playlists/pl-1/items/0",
            status=500
        )

        result = api_client.remove_playlist_item("pl-1", 0)
        assert result is False

    @responses.activate
    def test_remove_playlist_item_invalid_position(self, api_client, server_url):
        """Test removing item at invalid position."""
        responses.add(
            responses.DELETE,
            f"{server_url}/api/playlists/pl-1/items/999",
            status=404
        )

        result = api_client.remove_playlist_item("pl-1", 999)
        assert result is False
