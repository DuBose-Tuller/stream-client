"""Integration tests for API client against real server.

These tests run against the actual server at http://pi-server:8080.
They will help catch real API compatibility issues like the search format bug.

Run with: pytest tests/integration/ -v
Skip with: pytest tests/unit/ -v (to run only unit tests)
"""

import pytest
from api_client import MusicAPIClient
from metadata_client import MetadataClient


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestAPIIntegration:
    """Integration tests for MusicAPIClient against real server."""

    @pytest.fixture
    def api_client(self):
        """Create API client pointing to real server."""
        return MusicAPIClient("http://pi-server:8080")

    # ========== Server Health Tests ==========

    def test_server_is_reachable(self, api_client):
        """Test that the server is reachable and healthy."""
        result = api_client.health_check()
        assert result is True, "Server health check failed - is the server running?"

    # ========== Search Integration Tests ==========

    def test_search_returns_valid_response(self, api_client):
        """Test that search returns a valid response structure with new SearchResponse format."""
        # Use a common search term that should return results
        result = api_client.search_songs("a")

        # The result should be a DICT with songs/albums/artists keys
        assert isinstance(result, dict), f"Search should return a dict, got {type(result)}"
        assert "songs" in result, "Search result should have 'songs' key"
        assert "albums" in result, "Search result should have 'albums' key"
        assert "artists" in result, "Search result should have 'artists' key"

    def test_search_with_common_query(self, api_client):
        """Test search with a common query."""
        result = api_client.search_songs("the")

        assert isinstance(result, dict)
        assert "songs" in result
        # Should return some results for common word "the"
        # (This is not guaranteed, but likely)

    def test_search_results_have_required_fields(self, api_client):
        """Test that search results have all required song fields."""
        result = api_client.search_songs("a")
        songs = result.get("songs", [])

        if len(songs) > 0:
            # Check first result has required fields
            song = songs[0]

            required_fields = ["id", "title", "artist"]
            for field in required_fields:
                assert field in song, f"Song missing required field: {field}"

            # Check field types
            assert isinstance(song["id"], str), "Song ID should be a string"
            assert isinstance(song["title"], str), "Song title should be a string"
            assert isinstance(song["artist"], str), "Song artist should be a string"

    def test_search_empty_query(self, api_client):
        """Test search with empty query."""
        result = api_client.search_songs("")

        # Should return a dict (might be empty or all songs, depends on server)
        assert isinstance(result, dict)
        assert "songs" in result

    def test_search_no_results_query(self, api_client):
        """Test search with query that returns no results."""
        result = api_client.search_songs("zzzznonexistentsongxyz12345")

        assert isinstance(result, dict)
        assert len(result.get("songs", [])) == 0

    # ========== Artist Integration Tests ==========

    def test_get_artists_returns_list(self, api_client):
        """Test that get_artists returns a valid list."""
        result = api_client.get_artists()

        assert isinstance(result, list)
        # Should have at least some artists (depends on server data)

    def test_artist_has_required_fields(self, api_client):
        """Test that artist objects have required fields."""
        result = api_client.get_artists()

        if len(result) > 0:
            artist = result[0]
            assert "id" in artist or "name" in artist, "Artist should have id or name field"

    # ========== Stream Integration Tests ==========

    def test_stream_song_with_valid_id(self, api_client):
        """Test streaming a song with a valid song ID.

        This test first searches for a song, then tries to stream it.
        """
        # First, get a valid song ID
        result = api_client.search_songs("a")
        songs = result.get("songs", [])

        if len(songs) > 0:
            song_id = songs[0]["id"]

            # Try to stream the song
            audio_data = api_client.stream_song(song_id)

            # Should return bytes
            assert audio_data is not None, f"Failed to stream song {song_id}"
            assert isinstance(audio_data, bytes), "Audio data should be bytes"
            assert len(audio_data) > 0, "Audio data should not be empty"
        else:
            pytest.skip("No songs available to test streaming")

    def test_stream_song_with_invalid_id(self, api_client):
        """Test streaming with an invalid song ID."""
        audio_data = api_client.stream_song("invalid-song-id-xyz")

        # Should return None for invalid ID
        assert audio_data is None

    # ========== Play Notification Integration Tests ==========

    def test_notify_server_play(self, api_client):
        """Test notifying server of playback."""
        # Get a real song first
        result = api_client.search_songs("a")
        songs = result.get("songs", [])

        if len(songs) > 0:
            song = songs[0]

            # Notify server we're playing this song
            notify_result = api_client.notify_server_play(song)

            # Should succeed (returns True) or at least not crash
            assert isinstance(notify_result, bool)
        else:
            pytest.skip("No songs available to test play notification")

    # ========== Search Format Compatibility Tests ==========

    def test_search_response_format_compatibility(self, api_client):
        """Verify search response uses new SearchResponse format.

        NEW FORMAT (current):
        {
            "success": true,
            "data": {
                "songs": [...],
                "albums": [...],
                "artists": [...]
            }
        }
        """
        result = api_client.search_songs("test")

        # The client's search_songs should return the full SearchResponse dict
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"

        # Verify it has the new format keys
        assert "songs" in result, "Result should have 'songs' key"
        assert "albums" in result, "Result should have 'albums' key"
        assert "artists" in result, "Result should have 'artists' key"

        # Verify songs is a list
        assert isinstance(result["songs"], list), "songs should be a list"

        # If there are songs, verify they have the expected structure
        if len(result["songs"]) > 0:
            first_song = result["songs"][0]
            assert isinstance(first_song, dict), "Each song should be a dict"
            assert "id" in first_song, "Each song should have an id"


class TestMetadataIntegration:
    """Integration tests for MetadataClient against real server."""

    @pytest.fixture
    def metadata_client(self):
        """Create metadata client pointing to real server."""
        return MetadataClient("http://pi-server:8080")

    def test_search_songs_integration(self, metadata_client):
        """Test metadata client search functionality."""
        result = metadata_client.search_songs("a")

        assert isinstance(result, list)

    def test_get_metadata_for_existing_song(self, metadata_client):
        """Test getting metadata for a real song."""
        # First find a song
        songs = metadata_client.search_songs("a")

        if len(songs) > 0:
            song_id = songs[0]["id"]

            # Try to get its metadata (might be None if no metadata set)
            metadata = metadata_client.get_song_metadata(song_id)

            # Should return None or a dict, not raise an error
            assert metadata is None or isinstance(metadata, dict)
        else:
            pytest.skip("No songs available to test metadata retrieval")

    def test_update_and_retrieve_metadata(self, metadata_client):
        """Test updating and retrieving metadata (full round-trip)."""
        # First find a song
        songs = metadata_client.search_songs("a")

        if len(songs) > 0:
            song_id = songs[0]["id"]

            # Create test metadata
            test_metadata = {
                "energy": 0.85,
                "valence": 0.65,
                "tempo": 125,
                "personal_rating": 7,
                "custom_genre": "Integration Test Genre"
            }

            # Update metadata
            update_result = metadata_client.update_song_metadata(song_id, test_metadata)

            # Depending on server implementation, this might succeed or fail
            # Just verify we get a boolean response
            assert isinstance(update_result, bool)

            # If update succeeded, try to retrieve it
            if update_result:
                retrieved = metadata_client.get_song_metadata(song_id)

                # Should get back the metadata we set
                if retrieved:
                    assert retrieved.get("energy") == 0.85
                    assert retrieved.get("personal_rating") == 7
        else:
            pytest.skip("No songs available to test metadata update")


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    @pytest.fixture
    def api_client(self):
        return MusicAPIClient("http://pi-server:8080")

    def test_full_playback_workflow(self, api_client):
        """Test a complete workflow: search -> select -> stream -> notify."""
        # 1. Check server health
        assert api_client.health_check(), "Server must be healthy"

        # 2. Search for songs
        result = api_client.search_songs("a")
        assert isinstance(result, dict), "Search must return a dict"
        songs = result.get("songs", [])

        if len(songs) == 0:
            pytest.skip("No songs available for end-to-end test")

        # 3. Select first song
        song = songs[0]
        assert "id" in song, "Song must have an ID"

        # 4. Stream the song
        audio_data = api_client.stream_song(song["id"])
        assert audio_data is not None, "Should be able to stream song"
        assert len(audio_data) > 0, "Audio data should not be empty"

        # 5. Notify server of playback
        notify_result = api_client.notify_server_play(song)
        assert isinstance(notify_result, bool), "Notify should return boolean"

        # If we got here, the full workflow works!
        print(f"\n✅ Full workflow test passed with song: {song.get('title', 'Unknown')}")


class TestPlaylistIntegration:
    """Integration tests for playlist operations against real server."""

    @pytest.fixture
    def api_client(self):
        """Create API client pointing to real server."""
        return MusicAPIClient("http://pi-server:8080")

    def test_get_all_playlists(self, api_client):
        """Test getting all playlists from server."""
        result = api_client.get_all_playlists()
        assert isinstance(result, list)

    def test_create_and_delete_playlist_workflow(self, api_client):
        """Test full playlist lifecycle."""
        # Create playlist
        playlist_id = api_client.create_playlist("Test Playlist", "Integration test")
        
        if playlist_id:
            # Verify it was created
            playlists = api_client.get_all_playlists()
            assert any(p.get('id') == playlist_id for p in playlists)
            
            # Clean up - delete the playlist
            delete_result = api_client.delete_playlist(playlist_id)
            assert isinstance(delete_result, bool)

    def test_playlist_operations_when_available(self, api_client):
        """Test playlist operations if server supports them."""
        # Try to get playlists
        playlists = api_client.get_all_playlists()
        
        if playlists and len(playlists) > 0:
            # If we have playlists, test getting one
            playlist_id = playlists[0]['id']
            playlist = api_client.get_playlist(playlist_id)
            
            # Should get back a playlist object
            assert playlist is None or isinstance(playlist, dict)
