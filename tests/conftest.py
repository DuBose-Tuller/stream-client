"""Shared pytest fixtures for all tests."""

import pytest
import io
from typing import Dict, List


@pytest.fixture
def server_url():
    """Return the test server URL."""
    return "http://pi-server:8080"


@pytest.fixture
def sample_song():
    """Return a sample song dictionary."""
    return {
        "id": "song-123",
        "title": "Test Song",
        "artist": "Test Artist",
        "album": "Test Album",
        "duration": 180,
        "file_path": "/music/test.mp3"
    }


@pytest.fixture
def sample_songs_list():
    """Return a list of sample songs."""
    return [
        {
            "id": "song-1",
            "title": "First Song",
            "artist": "Artist One",
            "album": "Album A",
            "duration": 200
        },
        {
            "id": "song-2",
            "title": "Second Song",
            "artist": "Artist Two",
            "album": "Album B",
            "duration": 240
        },
        {
            "id": "song-3",
            "title": "Third Song",
            "artist": "Artist One",
            "album": "Album A",
            "duration": 180
        }
    ]


@pytest.fixture
def sample_search_response_old_format(sample_songs_list):
    """Return a sample search response in OLD API format (flat array)."""
    return {
        "success": True,
        "data": sample_songs_list
    }


@pytest.fixture
def sample_search_response_new_format(sample_songs_list):
    """Return a sample search response in NEW API format (SearchResponse structure)."""
    return {
        "success": True,
        "data": {
            "songs": sample_songs_list,
            "albums": [
                {"id": "album-1", "name": "Album A", "artist": "Artist One"},
                {"id": "album-2", "name": "Album B", "artist": "Artist Two"}
            ],
            "artists": [
                {"id": "artist-1", "name": "Artist One"},
                {"id": "artist-2", "name": "Artist Two"}
            ]
        }
    }


@pytest.fixture
def sample_artists():
    """Return a list of sample artists."""
    return [
        {"id": "artist-1", "name": "Artist One", "song_count": 10},
        {"id": "artist-2", "name": "Artist Two", "song_count": 5}
    ]


@pytest.fixture
def sample_audio_data():
    """Return sample audio data (mock MP3 bytes)."""
    # This is just dummy data; real tests with pygame will need valid audio
    return b"MOCK_AUDIO_DATA_" + b"\x00" * 1024


@pytest.fixture
def sample_metadata():
    """Return sample song metadata."""
    return {
        "energy": 0.8,
        "valence": 0.6,
        "tempo": 120,
        "color": "#FF5733",
        "mood": ["happy", "energetic"],
        "personal_rating": 8,
        "shuffle_weight": 1.2,
        "skip_probability": 0.1,
        "custom_genre": "Electronic"
    }


@pytest.fixture
def sample_playlist():
    """Return a sample playlist."""
    return {
        "id": "playlist-123",
        "name": "My Test Playlist",
        "description": "A playlist for testing",
        "items": [
            {"type": "track", "song_id": "song-1", "position": 0},
            {"type": "track", "song_id": "song-2", "position": 1}
        ]
    }


@pytest.fixture
def sample_playlists_list():
    """Return a list of sample playlists."""
    return [
        {
            "id": "playlist-1",
            "name": "Chill Vibes",
            "description": "Relaxing music",
            "item_count": 10
        },
        {
            "id": "playlist-2",
            "name": "Workout Mix",
            "description": "High energy tracks",
            "item_count": 25
        }
    ]
