# Music Streaming Client

Python clients for the enhanced music streaming server with custom metadata and gapless playback.

## Files

### Core Clients

- **`test_client.py`** - Basic test client with audio streaming and playback
- **`gapless_client.py`** - Advanced client demonstrating gapless playback between tracks
- **`metadata_client.py`** - Client for testing custom metadata features
- **`test_full_system.py`** - Comprehensive system integration tests

### GUI Client

- **`main.py`** - Entry point for the GUI application
- **`gui_client.py`** - Main tkinter GUI application class
- **`api_client.py`** - HTTP API client for server communication
- **`audio_player.py`** - pygame-based audio playback manager
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
- **Playback Controls**: Play, pause, resume, stop with visual feedback
- **Volume Control**: Interactive volume slider
- **Status Updates**: Connection status and playback information
- **Modern UI**: Native macOS/Windows styling with ttk widgets
- **Threading**: Non-blocking operations for smooth user experience

### Gapless Playback Demo

```bash
python gapless_client.py
```

Demonstrates:
- **Seamless track transitions** with no gaps or clicks
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

## Current Status (January 2025)

### ✅ What's Working
- **Basic Audio Streaming**: Original test client works with all server types
- **Desktop GUI Client**: Full tkinter-based client with search, playback, and volume control
- **Modular Architecture**: GUI client split into reusable components (api_client, audio_player, gui_client)
- **Gapless Playbook**: Dual-channel seamless track transitions implemented
- **Database Integration**: SQLite database successfully created and connected
- **Deploy Script**: Fixed hanging issues, supports all server types
- **Three Server Options**: Original, Hybrid, and Direct file servers

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
6. Add GUI client features: playlists, queue management, lyrics display

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

## Custom Metadata Schema

The metadata system supports rich song annotations:

```json
{
  "song_id": "track_123",
  "energy": 0.8,
  "valence": 0.6, 
  "tempo": 128,
  "key_signature": "C major",
  "color": "#FF6B35",
  "mood": ["energetic", "upbeat"],
  "tags": ["workout", "driving"],
  "personal_rating": 8,
  "play_count": 42,
  "skip_count": 3,
  "shuffle_weight": 1.2,
  "skip_probability": 0.1
}
```

This enables advanced features like:
- **Smart Playlists**: "High energy songs in C major"
- **Mood-Based Shuffle**: "Only happy songs when it's raining"
- **Workout Optimization**: "Songs that match my running pace"
- **Discovery**: "Songs similar to my favorites but not overplayed"

## GUI Client Architecture

The desktop GUI client uses a modular design for maintainability:

### Components

1. **`api_client.py`** - HTTP API Communication
   - Server health checking
   - Song search and artist retrieval
   - Audio streaming with timeout handling
   - Server playback state synchronization

2. **`audio_player.py`** - Audio Playback
   - pygame mixer initialization and management
   - Play, pause, resume, stop controls
   - Volume control and status tracking
   - Audio data loading from bytes

3. **`gui_client.py`** - User Interface
   - tkinter/ttk-based modern GUI
   - Search interface with results display
   - Player controls with state management
   - Threading for non-blocking operations

4. **`main.py`** - Application Entry Point
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

## Next Steps

1. **Mobile Client**: Port gapless logic to React Native or Flutter
2. **Web Client**: JavaScript version using Web Audio API
3. **Advanced Shuffle**: Machine learning-based recommendation engine  
4. **Offline Mode**: Local caching and sync capabilities
5. **Multi-Room**: Synchronized playback across devices