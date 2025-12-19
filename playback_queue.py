"""
Playback queue management for the music streaming client.

Manages a two-tier queue system:
- Manual items: Explicitly queued by user, play first, persist across playlist changes
- Auto items: From playlists/albums, play after manual items, replaced when playing new playlist
"""

from typing import Dict, List, Optional, Tuple


class QueueItem:
    """Represents a single item in the playback queue."""

    def __init__(self, song: Dict, item_type: str = 'manual', group_id: Optional[str] = None):
        """
        Initialize a queue item.

        Args:
            song: Song dictionary from API
            item_type: 'manual' or 'auto'
            group_id: Optional track group ID for group skipping
        """
        self.song = song
        self.type = item_type
        self.group_id = group_id

    def __repr__(self):
        title = self.song.get('title', 'Unknown')
        return f"QueueItem(title={title}, type={self.type}, group_id={self.group_id})"


class PlaybackQueue:
    """
    Manages the playback queue with support for manual and auto items.

    Queue ordering: Manual items → Auto items
    """

    def __init__(self):
        """Initialize an empty queue."""
        self.items: List[QueueItem] = []
        self.current_index: int = -1

    def add_manual(self, song: Dict) -> None:
        """
        Add a song to the manual queue.

        Manual items are added after the currently playing song if one exists,
        otherwise at the end of the manual section (before any auto items).

        Args:
            song: Song dictionary from API
        """
        queue_item = QueueItem(song, item_type='manual', group_id=None)

        # If a song is currently playing, insert after it
        if 0 <= self.current_index < len(self.items):
            insert_index = self.current_index + 1
            self.items.insert(insert_index, queue_item)
            # No need to adjust current_index since we inserted after it
        else:
            # No current song, insert at end of manual section (before auto items)
            insert_index = 0
            for i, item in enumerate(self.items):
                if item.type == 'manual':
                    insert_index = i + 1
                else:
                    break

            self.items.insert(insert_index, queue_item)

            # Adjust current_index if we inserted before it
            if self.current_index >= insert_index:
                self.current_index += 1

    def add_auto_songs(self, songs: List[Dict], groups: Optional[List[Tuple[int, str]]] = None) -> None:
        """
        Add auto items from a playlist, appending after manual items.

        This clears existing auto items first, then adds new ones after manual items.

        Args:
            songs: List of song dictionaries
            groups: Optional list of (song_index, group_id) tuples for track grouping
        """
        # Clear existing auto items
        self.clear_auto_items()

        # Create group_id lookup
        group_lookup = {}
        if groups:
            for song_idx, group_id in groups:
                group_lookup[song_idx] = group_id

        # Add new auto items at the end (after manual items)
        for i, song in enumerate(songs):
            group_id = group_lookup.get(i, None)
            queue_item = QueueItem(song, item_type='auto', group_id=group_id)
            self.items.append(queue_item)

    def clear_auto_items(self) -> None:
        """Remove all auto items from the queue, keeping manual items."""
        # Filter out auto items
        self.items = [item for item in self.items if item.type == 'manual']

        # Adjust current_index if it was pointing to an auto item
        if self.current_index >= len(self.items):
            self.current_index = len(self.items) - 1

    def clear(self) -> None:
        """Clear the entire queue."""
        self.items = []
        self.current_index = -1

    def remove_at(self, index: int) -> None:
        """
        Remove item at the specified index.

        Args:
            index: Index of item to remove
        """
        if 0 <= index < len(self.items):
            self.items.pop(index)

            # Adjust current_index
            if index < self.current_index:
                self.current_index -= 1
            elif index == self.current_index:
                # Removed current item, stay at same index (next item)
                # But clamp to valid range
                if self.current_index >= len(self.items):
                    self.current_index = len(self.items) - 1

    def get_current(self) -> Optional[QueueItem]:
        """
        Get the current queue item.

        Returns:
            Current QueueItem or None if index is invalid
        """
        if 0 <= self.current_index < len(self.items):
            return self.items[self.current_index]
        return None

    def get_next(self) -> Optional[QueueItem]:
        """
        Get the next queue item without advancing.

        Returns:
            Next QueueItem or None if no next item
        """
        next_index = self.current_index + 1
        if 0 <= next_index < len(self.items):
            return self.items[next_index]
        return None

    def has_next(self) -> bool:
        """
        Check if there's a next item in the queue.

        Returns:
            True if there's a next item, False otherwise
        """
        return self.get_next() is not None

    def advance(self) -> Optional[QueueItem]:
        """
        Advance to the next queue item.

        Returns:
            New current QueueItem or None if no next item
        """
        if self.has_next():
            self.current_index += 1
            return self.get_current()
        return None

    def skip_current_group(self) -> None:
        """
        Skip all remaining songs in the current track group.

        If current song is in a group, advances past all songs with the same group_id.
        If not in a group, just advances by one.
        """
        current = self.get_current()
        if not current or not current.group_id:
            # Not in a group, just advance by one
            self.advance()
            return

        # Find the next item that's NOT in the same group
        target_group_id = current.group_id
        next_index = self.current_index + 1

        while next_index < len(self.items):
            if self.items[next_index].group_id != target_group_id:
                break
            next_index += 1

        # Set current_index to the first item outside the group
        # If we've gone past the end, that's okay - get_current() will return None
        self.current_index = next_index

    def move_item(self, from_index: int, to_index: int) -> None:
        """
        Move an item from one index to another.

        Args:
            from_index: Source index
            to_index: Destination index
        """
        if not (0 <= from_index < len(self.items) and 0 <= to_index < len(self.items)):
            return

        item = self.items.pop(from_index)
        self.items.insert(to_index, item)

        # Adjust current_index
        if from_index == self.current_index:
            self.current_index = to_index
        elif from_index < self.current_index <= to_index:
            self.current_index -= 1
        elif to_index <= self.current_index < from_index:
            self.current_index += 1

    def get_queue_display(self) -> List[Tuple[str, str, bool]]:
        """
        Get formatted queue items for display in UI.

        Returns:
            List of (display_text, item_type, is_current) tuples
        """
        result = []
        for i, item in enumerate(self.items):
            title = item.song.get('title', 'Unknown')
            artist = item.song.get('artist', 'Unknown')
            duration = item.song.get('duration')

            # Format duration
            duration_str = ''
            if duration:
                minutes = duration // 60
                seconds = duration % 60
                duration_str = f' ({minutes}:{seconds:02d})'

            # Format display text
            if i == self.current_index:
                display_text = f"► {title} - {artist}{duration_str}"
            else:
                display_text = f"  {title} - {artist}{duration_str}"

            is_current = (i == self.current_index)
            result.append((display_text, item.type, is_current))

        return result

    def __len__(self) -> int:
        """Return the number of items in the queue."""
        return len(self.items)

    def __repr__(self):
        return f"PlaybackQueue(items={len(self.items)}, current={self.current_index})"
