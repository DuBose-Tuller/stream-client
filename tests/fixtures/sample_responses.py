"""Sample API response data for testing."""

# Health check responses
HEALTH_SUCCESS = {"status": "ok"}
HEALTH_ERROR = {"error": "Service unavailable"}

# Search responses - OLD FORMAT (what current code expects)
SEARCH_SUCCESS_OLD = {
    "success": True,
    "data": [
        {
            "id": "song-abc123",
            "title": "Bohemian Rhapsody",
            "artist": "Queen",
            "album": "A Night at the Opera",
            "duration": 354
        },
        {
            "id": "song-def456",
            "title": "Stairway to Heaven",
            "artist": "Led Zeppelin",
            "album": "Led Zeppelin IV",
            "duration": 482
        }
    ]
}

# Search responses - NEW FORMAT (what broke the client)
SEARCH_SUCCESS_NEW = {
    "success": True,
    "data": {
        "songs": [
            {
                "id": "song-abc123",
                "title": "Bohemian Rhapsody",
                "artist": "Queen",
                "album": "A Night at the Opera",
                "duration": 354
            },
            {
                "id": "song-def456",
                "title": "Stairway to Heaven",
                "artist": "Led Zeppelin",
                "album": "Led Zeppelin IV",
                "duration": 482
            }
        ],
        "albums": [
            {
                "id": "album-123",
                "name": "A Night at the Opera",
                "artist": "Queen"
            },
            {
                "id": "album-456",
                "name": "Led Zeppelin IV",
                "artist": "Led Zeppelin"
            }
        ],
        "artists": [
            {
                "id": "artist-queen",
                "name": "Queen"
            },
            {
                "id": "artist-zeppelin",
                "name": "Led Zeppelin"
            }
        ]
    }
}

SEARCH_EMPTY_OLD = {
    "success": True,
    "data": []
}

SEARCH_EMPTY_NEW = {
    "success": True,
    "data": {
        "songs": [],
        "albums": [],
        "artists": []
    }
}

SEARCH_ERROR = {
    "success": False,
    "error": "Invalid query"
}

# Artist responses
ARTISTS_SUCCESS = {
    "success": True,
    "data": [
        {"id": "artist-1", "name": "The Beatles", "song_count": 213},
        {"id": "artist-2", "name": "Pink Floyd", "song_count": 165}
    ]
}

# Playlist responses
PLAYLISTS_SUCCESS = {
    "success": True,
    "data": [
        {
            "id": "pl-1",
            "name": "Favorites",
            "description": "My favorite songs",
            "item_count": 50
        },
        {
            "id": "pl-2",
            "name": "Study Music",
            "description": "Focus and concentration",
            "item_count": 30
        }
    ]
}

PLAYLIST_DETAIL = {
    "success": True,
    "data": {
        "id": "pl-1",
        "name": "Favorites",
        "description": "My favorite songs",
        "items": [
            {"type": "track", "song_id": "song-1", "position": 0},
            {"type": "track", "song_id": "song-2", "position": 1},
            {
                "type": "group",
                "name": "Album: Dark Side of the Moon",
                "song_ids": ["song-3", "song-4", "song-5"],
                "position": 2
            }
        ]
    }
}

CREATE_PLAYLIST_SUCCESS = {
    "success": True,
    "data": "pl-new-123"
}

# Playlist detail with full song data (for playback testing)
PLAYLIST_DETAIL_WITH_SONGS = {
    "success": True,
    "data": {
        "id": "pl-1",
        "name": "Test Playlist",
        "description": "Test playlist with songs",
        "items": [
            {
                "type": "track",
                "song_id": "song-1",
                "position": 0,
                "song": {
                    "id": "song-1",
                    "title": "Track One",
                    "artist": "Artist A",
                    "album": "Album A",
                    "duration": 180
                }
            },
            {
                "type": "track",
                "song_id": "song-2",
                "position": 1,
                "song": {
                    "id": "song-2",
                    "title": "Track Two",
                    "artist": "Artist B",
                    "album": "Album B",
                    "duration": 200
                }
            },
            {
                "type": "group",
                "name": "Album: Best Of",
                "position": 2,
                "song_ids": ["song-3", "song-4"],
                "songs": [
                    {
                        "id": "song-3",
                        "title": "Track Three",
                        "artist": "Artist C",
                        "album": "Best Of",
                        "duration": 220
                    },
                    {
                        "id": "song-4",
                        "title": "Track Four",
                        "artist": "Artist C",
                        "album": "Best Of",
                        "duration": 240
                    }
                ]
            }
        ]
    }
}

PLAYLIST_EMPTY = {
    "success": True,
    "data": {
        "id": "pl-empty",
        "name": "Empty Playlist",
        "description": "",
        "items": []
    }
}

# Metadata responses
METADATA_SUCCESS = {
    "success": True,
    "data": {
        "energy": 0.9,
        "valence": 0.7,
        "tempo": 128,
        "color": "#FF6B35",
        "mood": ["energetic", "happy"],
        "personal_rating": 9,
        "shuffle_weight": 1.5,
        "skip_probability": 0.05,
        "custom_genre": "Rock"
    }
}

SMART_SHUFFLE_RESPONSE = {
    "success": True,
    "data": [
        {"id": "song-1", "title": "High Energy Track"},
        {"id": "song-2", "title": "Another Good Song"},
        {"id": "song-3", "title": "Perfect Match"}
    ]
}
