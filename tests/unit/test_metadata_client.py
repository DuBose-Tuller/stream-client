"""Unit tests for MetadataClient."""

import pytest
import responses
from metadata_client import MetadataClient
from tests.fixtures import sample_responses


class TestMetadataClient:
    """Test suite for MetadataClient class."""

    @pytest.fixture
    def metadata_client(self, server_url):
        """Create a MetadataClient instance."""
        return MetadataClient(server_url)

    # ========== Initialization Tests ==========

    def test_metadata_client_initialization(self, server_url):
        """Test MetadataClient initializes correctly."""
        client = MetadataClient(server_url)

        assert client.server_url == server_url
        assert client.session is not None

    def test_default_server_url(self):
        """Test default server URL."""
        client = MetadataClient()
        assert client.server_url == "http://pi-server:8080"

    # ========== Search Songs Tests ==========

    @responses.activate
    def test_search_songs_success(self, metadata_client, server_url, sample_songs_list):
        """Test successful song search."""
        responses.add(
            responses.GET,
            f"{server_url}/api/search",
            json={"success": True, "data": {"songs": sample_songs_list, "albums": [], "artists": []}},
            status=200
        )

        result = metadata_client.search_songs("test")

        assert len(result) == 3
        assert result[0]["title"] == "First Song"

    @responses.activate
    def test_search_songs_empty(self, metadata_client, server_url):
        """Test search with no results."""
        responses.add(
            responses.GET,
            f"{server_url}/api/search",
            json={"success": True, "data": {"songs": [], "albums": [], "artists": []}},
            status=200
        )

        result = metadata_client.search_songs("nonexistent")
        assert result == []

    @responses.activate
    def test_search_songs_error(self, metadata_client, server_url):
        """Test search with server error."""
        responses.add(
            responses.GET,
            f"{server_url}/api/search",
            status=500
        )

        result = metadata_client.search_songs("test")
        assert result == []

    # ========== Get Song Metadata Tests ==========

    @responses.activate
    def test_get_song_metadata_success(self, metadata_client, server_url, sample_metadata):
        """Test successful metadata retrieval."""
        responses.add(
            responses.GET,
            f"{server_url}/api/metadata/song-123",
            json=sample_responses.METADATA_SUCCESS,
            status=200
        )

        result = metadata_client.get_song_metadata("song-123")

        assert result is not None
        assert result["energy"] == 0.9
        assert result["tempo"] == 128
        assert result["color"] == "#FF6B35"
        assert result["personal_rating"] == 9

    @responses.activate
    def test_get_song_metadata_not_found(self, metadata_client, server_url):
        """Test getting metadata for non-existent song."""
        responses.add(
            responses.GET,
            f"{server_url}/api/metadata/invalid-id",
            json={"success": False, "error": "Song not found"},
            status=404
        )

        result = metadata_client.get_song_metadata("invalid-id")
        assert result is None

    @responses.activate
    def test_get_song_metadata_no_metadata(self, metadata_client, server_url):
        """Test getting metadata when song has no custom metadata."""
        responses.add(
            responses.GET,
            f"{server_url}/api/metadata/song-123",
            json={"success": True, "data": None},
            status=200
        )

        result = metadata_client.get_song_metadata("song-123")
        assert result is None

    @responses.activate
    def test_get_song_metadata_connection_error(self, metadata_client):
        """Test metadata retrieval with connection error."""
        result = metadata_client.get_song_metadata("song-123")
        assert result is None

    # ========== Update Song Metadata Tests ==========

    @responses.activate
    def test_update_song_metadata_success(self, metadata_client, server_url, sample_metadata):
        """Test successful metadata update."""
        responses.add(
            responses.POST,
            f"{server_url}/api/metadata/song-123",
            json={"success": True},
            status=200
        )

        result = metadata_client.update_song_metadata("song-123", sample_metadata)

        assert result is True
        # Verify request was made with correct data
        assert len(responses.calls) == 1
        assert responses.calls[0].request.body is not None

    @responses.activate
    def test_update_song_metadata_partial_fields(self, metadata_client, server_url):
        """Test updating only some metadata fields."""
        partial_metadata = {
            "energy": 0.7,
            "personal_rating": 8
        }

        responses.add(
            responses.POST,
            f"{server_url}/api/metadata/song-123",
            json={"success": True},
            status=200
        )

        result = metadata_client.update_song_metadata("song-123", partial_metadata)
        assert result is True

    @responses.activate
    def test_update_song_metadata_server_error(self, metadata_client, server_url, sample_metadata):
        """Test metadata update with server error."""
        responses.add(
            responses.POST,
            f"{server_url}/api/metadata/song-123",
            json={"success": False, "error": "Database error"},
            status=500
        )

        result = metadata_client.update_song_metadata("song-123", sample_metadata)
        assert result is False

    @responses.activate
    def test_update_song_metadata_connection_error(self, metadata_client, sample_metadata):
        """Test metadata update with connection error."""
        result = metadata_client.update_song_metadata("song-123", sample_metadata)
        assert result is False

    @responses.activate
    def test_update_song_metadata_invalid_json_response(self, metadata_client, server_url, sample_metadata):
        """Test metadata update with invalid JSON response."""
        responses.add(
            responses.POST,
            f"{server_url}/api/metadata/song-123",
            body="INVALID JSON",
            status=200
        )

        result = metadata_client.update_song_metadata("song-123", sample_metadata)
        assert result is False

    # ========== Record Play Event Tests ==========

    @responses.activate
    def test_record_play_event_complete_playback(self, metadata_client, server_url):
        """Test recording a complete playback event."""
        responses.add(
            responses.POST,
            f"{server_url}/api/play_event",
            json={"success": True},
            status=200
        )

        result = metadata_client.record_play_event(
            song_id="song-123",
            duration_played=180000,  # 3 minutes
            total_duration=180000,   # 3 minutes (complete)
            skip_reason=None
        )

        assert result is True

        # Verify the request payload
        request_body = responses.calls[0].request.body
        assert b"song-123" in request_body
        assert b"180000" in request_body

    @responses.activate
    def test_record_play_event_partial_playback(self, metadata_client, server_url):
        """Test recording a partial playback (user skipped)."""
        responses.add(
            responses.POST,
            f"{server_url}/api/play_event",
            json={"success": True},
            status=200
        )

        result = metadata_client.record_play_event(
            song_id="song-456",
            duration_played=30000,   # 30 seconds
            total_duration=180000,   # 3 minutes total
            skip_reason="User skipped"
        )

        assert result is True

    @responses.activate
    def test_record_play_event_with_skip_reason(self, metadata_client, server_url):
        """Test recording play event with various skip reasons."""
        responses.add(
            responses.POST,
            f"{server_url}/api/play_event",
            json={"success": True},
            status=200
        )

        skip_reasons = [
            "User skipped",
            "Low energy",
            "Wrong mood",
            "Played too recently"
        ]

        for reason in skip_reasons:
            result = metadata_client.record_play_event(
                song_id="song-789",
                duration_played=15000,
                total_duration=200000,
                skip_reason=reason
            )
            assert result is True

    @responses.activate
    def test_record_play_event_server_error(self, metadata_client, server_url):
        """Test recording play event with server error."""
        responses.add(
            responses.POST,
            f"{server_url}/api/play_event",
            json={"success": False, "error": "Database unavailable"},
            status=500
        )

        result = metadata_client.record_play_event("song-123", 60000, 180000)
        assert result is False

    @responses.activate
    def test_record_play_event_connection_error(self, metadata_client):
        """Test recording play event with connection error."""
        result = metadata_client.record_play_event("song-123", 60000, 180000)
        assert result is False

    # ========== Smart Shuffle Tests ==========

    @responses.activate
    def test_smart_shuffle_with_criteria(self, metadata_client, server_url):
        """Test smart shuffle with specific criteria."""
        criteria = {
            "min_energy": 0.7,
            "max_energy": 1.0,
            "min_rating": 8,
            "limit": 10
        }

        responses.add(
            responses.POST,
            f"{server_url}/api/smart_shuffle",
            json=sample_responses.SMART_SHUFFLE_RESPONSE,
            status=200
        )

        result = metadata_client.smart_shuffle(criteria)

        assert len(result) == 3
        assert result[0]["title"] == "High Energy Track"

        # Verify criteria was sent in request
        request_body = responses.calls[0].request.body
        assert b"min_energy" in request_body
        assert b"0.7" in request_body

    @responses.activate
    def test_smart_shuffle_without_criteria(self, metadata_client, server_url):
        """Test smart shuffle without specific criteria (random shuffle)."""
        responses.add(
            responses.POST,
            f"{server_url}/api/smart_shuffle",
            json=sample_responses.SMART_SHUFFLE_RESPONSE,
            status=200
        )

        result = metadata_client.smart_shuffle()

        assert len(result) == 3
        assert isinstance(result, list)

    @responses.activate
    def test_smart_shuffle_empty_results(self, metadata_client, server_url):
        """Test smart shuffle with no matching songs."""
        criteria = {
            "min_energy": 0.99,
            "min_rating": 10,
            "custom_genre": "Nonexistent Genre"
        }

        responses.add(
            responses.POST,
            f"{server_url}/api/smart_shuffle",
            json={"success": True, "data": []},
            status=200
        )

        result = metadata_client.smart_shuffle(criteria)
        assert result == []

    @responses.activate
    def test_smart_shuffle_complex_criteria(self, metadata_client, server_url):
        """Test smart shuffle with complex criteria."""
        criteria = {
            "min_energy": 0.5,
            "max_energy": 0.8,
            "min_valence": 0.6,  # Happy songs
            "mood": ["chill", "relaxed"],
            "exclude_recently_played": True,
            "shuffle_weight_multiplier": 1.5,
            "limit": 20
        }

        responses.add(
            responses.POST,
            f"{server_url}/api/smart_shuffle",
            json={"success": True, "data": []},
            status=200
        )

        result = metadata_client.smart_shuffle(criteria)
        assert isinstance(result, list)

    @responses.activate
    def test_smart_shuffle_server_error(self, metadata_client, server_url):
        """Test smart shuffle with server error."""
        responses.add(
            responses.POST,
            f"{server_url}/api/smart_shuffle",
            json={"success": False, "error": "Shuffle algorithm failed"},
            status=500
        )

        result = metadata_client.smart_shuffle()
        assert result == []

    @responses.activate
    def test_smart_shuffle_connection_error(self, metadata_client):
        """Test smart shuffle with connection error."""
        result = metadata_client.smart_shuffle({"min_energy": 0.5})
        assert result == []

    # ========== Edge Cases ==========

    @responses.activate
    def test_update_metadata_with_extreme_values(self, metadata_client, server_url):
        """Test updating metadata with extreme values."""
        extreme_metadata = {
            "energy": 0.0,           # Minimum
            "valence": 1.0,          # Maximum
            "tempo": 300,            # Very fast
            "personal_rating": 10,   # Maximum
            "shuffle_weight": 100.0, # Very high
            "skip_probability": 0.0  # Never skip
        }

        responses.add(
            responses.POST,
            f"{server_url}/api/metadata/song-123",
            json={"success": True},
            status=200
        )

        result = metadata_client.update_song_metadata("song-123", extreme_metadata)
        assert result is True

    @responses.activate
    def test_record_play_event_zero_duration(self, metadata_client, server_url):
        """Test recording play event with zero duration (instant skip)."""
        responses.add(
            responses.POST,
            f"{server_url}/api/play_event",
            json={"success": True},
            status=200
        )

        result = metadata_client.record_play_event(
            song_id="song-123",
            duration_played=0,
            total_duration=180000,
            skip_reason="Instant skip"
        )

        assert result is True

    @responses.activate
    def test_metadata_with_special_characters(self, metadata_client, server_url):
        """Test metadata with special characters in fields."""
        special_metadata = {
            "custom_genre": "Rock & Roll / Metal",
            "color": "#FF00FF",
            "mood": '["happy", "excited!", "100% energy"]'
        }

        responses.add(
            responses.POST,
            f"{server_url}/api/metadata/song-123",
            json={"success": True},
            status=200
        )

        result = metadata_client.update_song_metadata("song-123", special_metadata)
        assert result is True
