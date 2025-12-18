# Music Streaming Client

Python clients for the enhanced music streaming server with custom metadata and gapless playback.

## Files

### GUI Client

- **`main.py`** - Entry point for the GUI application
- **`gui_client.py`** - Main tkinter GUI application class with queue management
- **`api_client.py`** - HTTP API client for server communication
- **`audio_player.py`** - pygame-based audio playback manager with pre-buffering
- **`playback_queue.py`** - Two-tier queue system (manual + auto items)
- **`music_gui_client.py`** - Original monolithic GUI client (reference)

### Configuration

- **`requirements.txt`** - Python dependencies

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Make sure the music server is running (see server README)

3. Update server URL in clients if needed (default: `http://pi-server:8080`)

## Usage

### Basic Audio Streaming Test

```bash
python test_client.py
```

Features tested:
- Server health check
- Song search
- Audio streaming and playback
- Basic playback controls (play/pause/resume/stop)
- Volume control and seeking

### Desktop GUI Client

```bash
python main.py
```

Full-featured desktop music client with:
- **Search Interface**: Real-time song search with results display
- **Playback Queue**: Two-tier queue system (manual + auto items) with visual display
- **Gapless Playback**: Smart pre-buffering for near-seamless track transitions (50-150ms gap)
- **Auto-Advance**: Automatically plays next track when current finishes
- **Playback Controls**: Play, pause, resume, stop, next with visual feedback
- **Seeking**: Interactive progress bar with drag-to-seek functionality
- **Position Tracking**: Real-time display of current position and total duration
- **Volume Control**: Interactive volume slider
- **Queue Management**: Add to queue, remove, clear all, clear auto, jump to track
- **Track Groups**: Skip entire track groups (for multi-movement works)
- **Playlist Support**: Create, view, delete, and play playlists
- **Status Updates**: Connection status and playback information
- **Modern UI**: Native macOS/Windows styling with ttk widgets
- **Threading**: Non-blocking operations for smooth user experience

### Gapless Playback Demo

```bash
python gapless_client.py
```

Demonstrates:
- **Seamless track transitions** with no gaps or clicks (this is a TODO since there is no was to play multiple tracks at once)
- **Dual-channel audio mixing** using pygame
- **Smart preloading** of upcoming tracks
- **Interactive playback controls** during gapless playback

Technical implementation:
- Uses two pygame mixer channels
- Preloads next song while current song plays
- Switches channels at track boundaries for gapless transition
- Background threads for monitoring and preloading

### Custom Metadata Demo

```bash
python metadata_client.py
```

Shows off:
- Setting custom song metadata (energy, mood, tempo, color, etc.)
- Retrieving and updating metadata
- Recording play events for analytics
- Smart shuffle based on metadata criteria

Example metadata fields:
- `energy`: 0.0-1.0 (low to high energy)
- `valence`: 0.0-1.0 (sad to happy)
- `tempo`: BPM
- `color`: Hex color for synesthesia features
- `mood`: JSON array of mood tags
- `personal_rating`: 0-10 rating
- `shuffle_weight`: Probability multiplier for shuffle

### System Integration Tests

```bash
python test_full_system.py
```

Runs comprehensive tests:
- Server compilation check
- All API endpoints
- Custom metadata functionality
- Audio streaming capabilities
- Error handling

### ✅ What's Working
- **Basic Audio Streaming**: Original test client works with all server types
- **Desktop GUI Client**: Full tkinter-based client with search, playback, volume control, and queue management
- **Modular Architecture**: GUI client split into reusable components (api_client, audio_player, gui_client, playback_queue)
- **Queue System**: Two-tier queue (manual + auto items) with visual display and management
- **Gapless Playback**: Smart pre-buffering for near-seamless track transitions
- **Auto-Advance**: Automatic progression through queue
- **Playlist Support**: Full playlist CRUD operations and playback
- **Track Group Skipping**: Skip entire groups of related tracks

### 🚧 In Progress  
- **Database Population**: Migration tool creates database but doesn't populate songs yet
- **Metadata API**: Endpoints exist but need database population to be useful
- **Smart Shuffle**: Implementation ready but requires song data

### 📋 Next Steps
1. Complete migration tool to populate database with music data
2. Test all metadata features with real data
3. Implement advanced shuffle algorithms
4. Add systemd service setup
5. Create web client version
6. Add GUI client features: lyrics display, album art, advanced metadata
7. Optimize gapless playback gap (currently 50-150ms)
8. Add playlist editing capabilities (reorder, remove items)

## Server Setup

The clients expect a running music server. You can use any of the three server types:

### Option 1: Hybrid Server (Recommended)
```bash
cd ../server
./deploy.sh hybrid
```
**Features**: Database + Navidrome integration, custom metadata, gapless playback

### Option 2: Direct File Server  
```bash
cd ../server
./deploy.sh direct
```
**Features**: Direct file access, transcoding, full independence from Navidrome

### Option 3: Original Server (Basic)
```bash  
cd ../server
./deploy.sh original
```
**Features**: Simple Navidrome proxy, basic streaming only

### Database Setup (for Hybrid/Direct)
```bash
cd ../server
./deploy.sh migrate    # First time only - creates and initializes database
```

## Gapless Playback Technical Details

The gapless client achieves seamless track transitions using:

1. **Dual Channel Architecture**: Two pygame mixer channels alternate
2. **Preloading Pipeline**: Next track loads while current plays
3. **Precise Timing**: Monitors playback position for optimal switching
4. **Memory Management**: Clears old audio data to prevent memory leaks

### Audio Settings
- Sample rate: 44.1kHz
- Bit depth: 16-bit
- Channels: Stereo
- Buffer size: 512 samples (low latency)

### Performance Considerations
- Preloads 1-2 tracks ahead
- Uses streaming for reduced memory usage
- Background threads for non-blocking operation
- Automatic cleanup of unused audio data

## GUI Client Architecture

The desktop GUI client uses a modular design for maintainability:

### Components

1. **`api_client.py`** - HTTP API Communication
   - Server health checking
   - Song search and artist retrieval
   - Audio streaming with timeout handling
   - Playlist CRUD operations
   - Server playback state synchronization

2. **`audio_player.py`** - Audio Playback
   - pygame mixer initialization and management
   - Play, pause, resume, stop controls
   - Seeking with format-aware fallback strategies
   - Position tracking and duration management
   - Volume control and status tracking
   - Audio data loading from bytes or file paths
   - Pre-buffering support for gapless playback

3. **`playback_queue.py`** - Queue Management
   - Two-tier queue system (manual + auto items)
   - Manual items: user-queued songs (play first)
   - Auto items: from playlists/albums (play after manual)
   - Track group support for skipping entire groups
   - Queue operations: add, remove, clear, advance, skip

4. **`gui_client.py`** - User Interface
   - tkinter/ttk-based modern GUI
   - Search interface with results display
   - Queue display panel with management buttons
   - Playlist management (create, view, delete, play)
   - Interactive seeking progress bar with time display
   - Real-time position updates (100ms refresh)
   - Auto-advance with pre-buffering (triggers at 80% or 15s remaining)
   - Player controls with state management
   - Threading for non-blocking operations

5. **`main.py`** - Application Entry Point
   - Launches the GUI application
   - Simple, clean entry point for users

### Technical Highlights

- **Threading**: All network operations run in background threads to prevent UI freezing
- **Error Handling**: Comprehensive error dialogs and connection status feedback
- **State Management**: Proper button state updates based on player status
- **Cross-Platform**: Uses ttk widgets for native OS appearance
- **Memory Efficient**: Streams audio data without excessive memory usage

### Requirements Fixed

The GUI client addresses a critical compatibility issue:
- **macOS Tkinter**: Upgraded from system Tk 8.5 to Tkinter 9.0 (Python 3.13)
- **Widget Rendering**: ttk widgets now display properly with modern styling
- **Stability**: No more blank windows or invisible UI elements

## Troubleshooting

### GUI Client Issues
- **Blank window**: Ensure Python 3.13+ with modern Tkinter (not system Tk 8.5)
- **Widget styling**: Use `python3.13` specifically if multiple Python versions installed
- **Import errors**: Run from client directory so modules can find each other

### Audio Issues
- **No sound**: Check pygame mixer initialization and system audio
- **Choppy playback**: Increase buffer size in pygame.mixer.pre_init()
- **Gapless gaps**: Verify dual-channel switching logic

### Server Connection
- **Connection refused**: Ensure server is running and accessible
- **404 errors**: Check API endpoints match server version
- **Timeouts**: Verify network connectivity and server performance

### Dependencies
- **pygame import error**: Install with `pip install pygame`
- **requests issues**: Update with `pip install --upgrade requests`
- **tkinter issues**: Use Python 3.13+ with modern tkinter, not system Python

## Seeking Functionality

The client now supports full seeking functionality with format-aware fallback strategies:

### Features
- **Interactive Progress Bar**: Drag the slider to seek to any position
- **Real-time Position Display**: Shows current time and total duration (e.g., "2:34 / 4:12")
- **Format Support**: Works with MP3, OGG, and other formats
- **Fallback Strategy**: Automatically handles formats with limited seek support

### Implementation Details

#### Seeking Methods
1. **Direct Seeking**: Uses `pygame.mixer.music.set_pos()` for instant seeking
2. **Reload Fallback**: If direct seeking fails, reloads the file and plays from position
3. **State Preservation**: Maintains volume and pause state during fallback seeking

#### Format Compatibility
- **MP3**: Excellent seeking support (seeks to nearest frame)
- **OGG/Vorbis**: Good seeking accuracy
- **FLAC**: May have limited backward seeking (uses fallback)
- **M4A/AAC**: Format-dependent (pygame mixer support varies)

#### Progressive Streaming
- Client downloads complete song to temp file for full seeking capability
- Playback can start after 1MB buffered for quick startup
- Complete buffering enables unlimited seek operations

### Technical Notes

From TECHNICAL_LEARNINGS.md:
- Direct seeking is format-dependent in pygame.mixer
- Complete song buffering provides best seeking experience
- Fallback method causes brief interruption but works reliably
- Position tracking uses 100ms update interval for smooth UI

## Queue System

The GUI client now features a sophisticated two-tier queue system with gapless playback:

### Queue Architecture

**Two Queue Types:**
1. **Manual Queue** - Songs explicitly added by the user
   - Appears first in the queue
   - Persists when playing new playlists/songs
   - Added via "Add to Queue" button

2. **Auto Queue** - Songs from playlists or albums
   - Appears after manual queue items
   - Replaced when playing a new playlist/song
   - Automatically populated when you hit "Play Selected"

### Features

- **Visual Queue Display**: Shows all upcoming tracks with current indicator (►)
- **Queue Management**:
  - Add to Queue - Manually queue selected search results
  - Remove - Remove individual queue items
  - Clear All - Clear entire queue
  - Clear Auto - Clear only auto items, keep manual queue
  - Jump to Track - Double-click to skip to any queue item

- **Smart Ordering**: Manual items always play before auto items

### Gapless Playback

The queue system includes smart pre-buffering for near-gapless transitions:

**How It Works:**
1. **Pre-buffering Trigger**: When current song reaches 80% or 15 seconds remaining
2. **Background Download**: Next track downloads in parallel (doesn't interrupt playback)
3. **Instant Transition**: When song ends, pre-buffered track plays immediately
4. **Expected Gap**: 50-150ms (time to stop/load/play)

**Technical Details:**
- Downloads to temp file in background thread
- Uses pygame mixer's `play_audio_file()` for fast loading
- Monitors playback position every 100ms
- Automatic cleanup of temp files

### Track Groups

Support for multi-movement classical works or album sides:

- **Skipping**: "Next" button skips entire track group (e.g., all movements of a symphony)
- **Grouping**: Tracks with same `group_id` are treated as a unit
- **Display**: Group information shown in queue

### Usage Examples

**Playing a Single Song:**
```
1. Search for a song
2. Click "Play Selected" → Clears auto queue, adds song, starts playback
3. Song auto-advances to next queued item when finished
```

**Building a Manual Queue:**
```
1. Search for songs
2. Click "Add to Queue" for each song you want
3. Manual queue persists even if you play other things
4. Your queued songs play first
```

**Playing a Playlist:**
```
1. View a playlist
2. Click "Play Playlist" → Clears auto queue, adds all playlist songs
3. Playlist songs play after any manual queue items
4. Gapless transitions between tracks
```

## Next Steps

1. Test queue system with large playlists
2. Add playlist editing (reorder items, remove tracks)
3. Display album art in queue
4. Optimize gapless gap (explore alternatives to pygame for <10ms gaps)
5. Add queue persistence (save/restore across sessions)