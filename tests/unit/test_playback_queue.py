"""Unit tests for playback_queue.py"""

import pytest
from playback_queue import PlaybackQueue, QueueItem


@pytest.fixture
def empty_queue():
    """Create an empty playback queue."""
    return PlaybackQueue()


@pytest.fixture
def sample_songs():
    """Create sample song dictionaries."""
    return [
        {'id': '1', 'title': 'Song 1', 'artist': 'Artist A', 'duration': 180},
        {'id': '2', 'title': 'Song 2', 'artist': 'Artist B', 'duration': 200},
        {'id': '3', 'title': 'Song 3', 'artist': 'Artist C', 'duration': 220},
        {'id': '4', 'title': 'Song 4', 'artist': 'Artist D', 'duration': 240},
        {'id': '5', 'title': 'Song 5', 'artist': 'Artist E', 'duration': 260},
    ]


class TestQueueItem:
    """Tests for QueueItem class."""

    def test_queue_item_creation(self):
        """Test creating a queue item."""
        song = {'id': '1', 'title': 'Test Song', 'artist': 'Test Artist'}
        item = QueueItem(song, item_type='manual', group_id=None)

        assert item.song == song
        assert item.type == 'manual'
        assert item.group_id is None

    def test_queue_item_with_group(self):
        """Test creating a queue item with a group ID."""
        song = {'id': '1', 'title': 'Test Song', 'artist': 'Test Artist'}
        item = QueueItem(song, item_type='auto', group_id='group-123')

        assert item.group_id == 'group-123'
        assert item.type == 'auto'


class TestPlaybackQueue:
    """Tests for PlaybackQueue class."""

    def test_empty_queue_initialization(self, empty_queue):
        """Test that a new queue is empty."""
        assert len(empty_queue) == 0
        assert empty_queue.current_index == -1
        assert empty_queue.get_current() is None
        assert empty_queue.get_next() is None
        assert not empty_queue.has_next()

    def test_add_manual_single(self, empty_queue, sample_songs):
        """Test adding a single manual item."""
        empty_queue.add_manual(sample_songs[0])

        assert len(empty_queue) == 1
        assert empty_queue.items[0].type == 'manual'
        assert empty_queue.items[0].song == sample_songs[0]

    def test_add_multiple_manual(self, empty_queue, sample_songs):
        """Test adding multiple manual items."""
        empty_queue.add_manual(sample_songs[0])
        empty_queue.add_manual(sample_songs[1])
        empty_queue.add_manual(sample_songs[2])

        assert len(empty_queue) == 3
        assert all(item.type == 'manual' for item in empty_queue.items)
        assert empty_queue.items[0].song['id'] == '1'
        assert empty_queue.items[1].song['id'] == '2'
        assert empty_queue.items[2].song['id'] == '3'

    def test_add_auto_songs(self, empty_queue, sample_songs):
        """Test adding auto songs."""
        empty_queue.add_auto_songs(sample_songs[:3])

        assert len(empty_queue) == 3
        assert all(item.type == 'auto' for item in empty_queue.items)

    def test_manual_before_auto_ordering(self, empty_queue, sample_songs):
        """Test that manual items come before auto items."""
        # Add some auto items first
        empty_queue.add_auto_songs([sample_songs[3], sample_songs[4]])

        # Add manual items
        empty_queue.add_manual(sample_songs[0])
        empty_queue.add_manual(sample_songs[1])

        assert len(empty_queue) == 4
        # First two should be manual
        assert empty_queue.items[0].type == 'manual'
        assert empty_queue.items[0].song['id'] == '1'
        assert empty_queue.items[1].type == 'manual'
        assert empty_queue.items[1].song['id'] == '2'
        # Last two should be auto
        assert empty_queue.items[2].type == 'auto'
        assert empty_queue.items[2].song['id'] == '4'
        assert empty_queue.items[3].type == 'auto'
        assert empty_queue.items[3].song['id'] == '5'

    def test_add_auto_songs_with_groups(self, empty_queue, sample_songs):
        """Test adding auto songs with track groups."""
        # Group songs 0 and 1 together
        groups = [(0, 'group-1'), (1, 'group-1')]
        empty_queue.add_auto_songs(sample_songs[:3], groups=groups)

        assert len(empty_queue) == 3
        assert empty_queue.items[0].group_id == 'group-1'
        assert empty_queue.items[1].group_id == 'group-1'
        assert empty_queue.items[2].group_id is None

    def test_clear_auto_items_preserves_manual(self, empty_queue, sample_songs):
        """Test that clearing auto items keeps manual items."""
        # Add manual items
        empty_queue.add_manual(sample_songs[0])
        empty_queue.add_manual(sample_songs[1])

        # Add auto items
        empty_queue.add_auto_songs([sample_songs[2], sample_songs[3]])

        assert len(empty_queue) == 4

        # Clear auto items
        empty_queue.clear_auto_items()

        assert len(empty_queue) == 2
        assert all(item.type == 'manual' for item in empty_queue.items)
        assert empty_queue.items[0].song['id'] == '1'
        assert empty_queue.items[1].song['id'] == '2'

    def test_add_auto_songs_clears_previous_auto(self, empty_queue, sample_songs):
        """Test that adding auto songs clears previous auto items."""
        # Add first set of auto songs
        empty_queue.add_auto_songs([sample_songs[0], sample_songs[1]])
        assert len(empty_queue) == 2

        # Add second set of auto songs
        empty_queue.add_auto_songs([sample_songs[2], sample_songs[3]])

        # Should have replaced the first set
        assert len(empty_queue) == 2
        assert empty_queue.items[0].song['id'] == '3'
        assert empty_queue.items[1].song['id'] == '4'

    def test_clear(self, empty_queue, sample_songs):
        """Test clearing the entire queue."""
        empty_queue.add_manual(sample_songs[0])
        empty_queue.add_auto_songs([sample_songs[1], sample_songs[2]])

        empty_queue.clear()

        assert len(empty_queue) == 0
        assert empty_queue.current_index == -1

    def test_remove_at(self, empty_queue, sample_songs):
        """Test removing an item at a specific index."""
        empty_queue.add_auto_songs(sample_songs[:3])
        empty_queue.current_index = 1

        empty_queue.remove_at(2)

        assert len(empty_queue) == 2
        assert empty_queue.items[0].song['id'] == '1'
        assert empty_queue.items[1].song['id'] == '2'
        assert empty_queue.current_index == 1

    def test_remove_before_current_adjusts_index(self, empty_queue, sample_songs):
        """Test that removing before current index adjusts the index."""
        empty_queue.add_auto_songs(sample_songs[:3])
        empty_queue.current_index = 2

        empty_queue.remove_at(0)

        assert len(empty_queue) == 2
        assert empty_queue.current_index == 1  # Adjusted down

    def test_get_current(self, empty_queue, sample_songs):
        """Test getting the current item."""
        empty_queue.add_auto_songs(sample_songs[:3])
        empty_queue.current_index = 1

        current = empty_queue.get_current()

        assert current is not None
        assert current.song['id'] == '2'

    def test_get_current_invalid_index(self, empty_queue):
        """Test getting current with invalid index."""
        assert empty_queue.get_current() is None

    def test_get_next(self, empty_queue, sample_songs):
        """Test getting the next item."""
        empty_queue.add_auto_songs(sample_songs[:3])
        empty_queue.current_index = 0

        next_item = empty_queue.get_next()

        assert next_item is not None
        assert next_item.song['id'] == '2'

    def test_get_next_at_end(self, empty_queue, sample_songs):
        """Test getting next when at the end."""
        empty_queue.add_auto_songs(sample_songs[:3])
        empty_queue.current_index = 2

        assert empty_queue.get_next() is None

    def test_has_next(self, empty_queue, sample_songs):
        """Test checking if there's a next item."""
        empty_queue.add_auto_songs(sample_songs[:3])
        empty_queue.current_index = 0

        assert empty_queue.has_next()

        empty_queue.current_index = 2
        assert not empty_queue.has_next()

    def test_advance(self, empty_queue, sample_songs):
        """Test advancing to the next item."""
        empty_queue.add_auto_songs(sample_songs[:3])
        empty_queue.current_index = 0

        next_item = empty_queue.advance()

        assert next_item is not None
        assert next_item.song['id'] == '2'
        assert empty_queue.current_index == 1

    def test_advance_at_end(self, empty_queue, sample_songs):
        """Test advancing when at the end."""
        empty_queue.add_auto_songs(sample_songs[:3])
        empty_queue.current_index = 2

        result = empty_queue.advance()

        assert result is None
        assert empty_queue.current_index == 2  # Stays at end

    def test_skip_current_group_without_group(self, empty_queue, sample_songs):
        """Test skipping when not in a group (should just advance by one)."""
        empty_queue.add_auto_songs(sample_songs[:3])
        empty_queue.current_index = 0

        empty_queue.skip_current_group()

        assert empty_queue.current_index == 1

    def test_skip_current_group_with_group(self, empty_queue, sample_songs):
        """Test skipping all songs in a track group."""
        # Create a group with songs 1, 2, 3
        groups = [(1, 'group-1'), (2, 'group-1'), (3, 'group-1')]
        empty_queue.add_auto_songs(sample_songs, groups=groups)
        empty_queue.current_index = 1  # Start at second song (in group)

        empty_queue.skip_current_group()

        # Should skip to song at index 4 (first after group)
        assert empty_queue.current_index == 4
        current = empty_queue.get_current()
        assert current.song['id'] == '5'
        assert current.group_id is None

    def test_skip_current_group_at_end(self, empty_queue, sample_songs):
        """Test skipping group when group extends to end of queue."""
        groups = [(0, 'group-1'), (1, 'group-1'), (2, 'group-1')]
        empty_queue.add_auto_songs(sample_songs[:3], groups=groups)
        empty_queue.current_index = 0

        empty_queue.skip_current_group()

        # Should clamp to last valid index
        assert empty_queue.current_index == 2

    def test_move_item(self, empty_queue, sample_songs):
        """Test moving an item."""
        empty_queue.add_auto_songs(sample_songs[:3])
        empty_queue.current_index = 1

        empty_queue.move_item(0, 2)

        # Song 1 should now be at index 2
        assert empty_queue.items[0].song['id'] == '2'
        assert empty_queue.items[1].song['id'] == '3'
        assert empty_queue.items[2].song['id'] == '1'
        # Current index should be adjusted
        assert empty_queue.current_index == 0

    def test_get_queue_display(self, empty_queue, sample_songs):
        """Test getting formatted display strings."""
        empty_queue.add_manual(sample_songs[0])
        empty_queue.add_auto_songs([sample_songs[1], sample_songs[2]])
        empty_queue.current_index = 1

        display = empty_queue.get_queue_display()

        assert len(display) == 3
        # Check format
        assert display[0][0].startswith('  Song 1')  # Not current
        assert display[1][0].startswith('► Song 2')  # Current (has arrow)
        assert display[2][0].startswith('  Song 3')  # Not current
        # Check types
        assert display[0][1] == 'manual'
        assert display[1][1] == 'auto'
        assert display[2][1] == 'auto'
        # Check is_current flags
        assert not display[0][2]
        assert display[1][2]
        assert not display[2][2]

    def test_manual_items_persist_across_auto_changes(self, empty_queue, sample_songs):
        """Test that manual items persist when auto items are replaced."""
        # Add manual items
        empty_queue.add_manual(sample_songs[0])
        empty_queue.add_manual(sample_songs[1])

        # Add first playlist
        empty_queue.add_auto_songs([sample_songs[2], sample_songs[3]])

        assert len(empty_queue) == 4

        # Add second playlist (should replace auto items only)
        empty_queue.add_auto_songs([sample_songs[4]])

        assert len(empty_queue) == 3
        # Manual items still there
        assert empty_queue.items[0].song['id'] == '1'
        assert empty_queue.items[0].type == 'manual'
        assert empty_queue.items[1].song['id'] == '2'
        assert empty_queue.items[1].type == 'manual'
        # New auto item
        assert empty_queue.items[2].song['id'] == '5'
        assert empty_queue.items[2].type == 'auto'

    def test_current_index_adjustment_on_clear_auto(self, empty_queue, sample_songs):
        """Test that current_index is adjusted when clearing auto items."""
        empty_queue.add_manual(sample_songs[0])
        empty_queue.add_auto_songs([sample_songs[1], sample_songs[2]])
        empty_queue.current_index = 2  # On an auto item

        empty_queue.clear_auto_items()

        # Current index should be clamped to valid range
        assert empty_queue.current_index == 0  # Last valid index

    def test_add_manual_while_playing_fifo_behavior(self, empty_queue, sample_songs):
        """Test that manual items added while playing maintain FIFO (queue) order."""
        # Start with a playing song and some auto items
        empty_queue.add_auto_songs([sample_songs[0], sample_songs[3], sample_songs[4]])
        empty_queue.current_index = 0  # Song 0 is playing

        # Queue manual songs A, B, C
        empty_queue.add_manual(sample_songs[1])  # Queue A
        empty_queue.add_manual(sample_songs[2])  # Queue B

        # Expected order: [Song 0 (playing), A, B, Song 3, Song 4]
        assert len(empty_queue) == 5
        assert empty_queue.items[0].song['id'] == '1'  # Playing
        assert empty_queue.items[1].song['id'] == '2'  # A (first queued)
        assert empty_queue.items[1].type == 'manual'
        assert empty_queue.items[2].song['id'] == '3'  # B (second queued)
        assert empty_queue.items[2].type == 'manual'
        assert empty_queue.items[3].song['id'] == '4'  # Auto item
        assert empty_queue.items[3].type == 'auto'

    def test_add_manual_while_playing_with_existing_manual(self, empty_queue, sample_songs):
        """Test adding manual items when manual items already exist after current."""
        # Current song with manual items already queued
        empty_queue.add_manual(sample_songs[0])
        empty_queue.add_manual(sample_songs[1])
        empty_queue.add_auto_songs([sample_songs[4]])
        empty_queue.current_index = 0  # Song 0 is playing

        # Queue another manual song
        empty_queue.add_manual(sample_songs[2])

        # Expected: [Song 0 (playing), Song 1 (manual), Song 2 (manual, new), Song 4 (auto)]
        assert len(empty_queue) == 4
        assert empty_queue.items[0].song['id'] == '1'  # Playing
        assert empty_queue.items[1].song['id'] == '2'  # First manual
        assert empty_queue.items[2].song['id'] == '3'  # Newly added manual (at end of manual section)
        assert empty_queue.items[2].type == 'manual'
        assert empty_queue.items[3].song['id'] == '5'  # Auto item
        assert empty_queue.items[3].type == 'auto'
