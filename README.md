# Music Streaming Client

Python clients for the enhanced music streaming server with custom metadata and gapless playback.

## Files

### Core Clients

- **`test_client.py`** - Basic test client with audio streaming and playback
- **`gapless_client.py`** - Advanced client demonstrating gapless playback between tracks
- **`metadata_client.py`** - Client for testing custom metadata features
- **`test_full_system.py`** - Comprehensive system integration tests

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

## Server Setup

The clients expect a running music server. You can use either:

### Option 1: Hybrid Server (Database + Navidrome)
```bash
cd ../server
cargo run --bin hybrid_server
```

### Option 2: Direct File Server (Database only)
```bash
cd ../server
cargo run --bin direct_server
```

### Option 3: Original Navidrome-only Server
```bash
cd ../server
cargo run --bin server
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

## Troubleshooting

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

## Next Steps

1. **Mobile Client**: Port gapless logic to React Native or Flutter
2. **Web Client**: JavaScript version using Web Audio API
3. **Advanced Shuffle**: Machine learning-based recommendation engine  
4. **Offline Mode**: Local caching and sync capabilities
5. **Multi-Room**: Synchronized playback across devices