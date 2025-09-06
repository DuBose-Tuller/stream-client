# Music Streaming Server

A Rust-based music streaming server that acts as a proxy between clients and music services like Navidrome. Provides HTTP APIs for remote music streaming with transcoding support, seeking, and real-time WebSocket updates.

## Setup

1. Build the server:
   ```bash
   cargo build --bin server --release
   ```

2. Update the server configuration in `src/bin/server.rs`:
   ```rust
   let navidrome_service = NavidromeClient::new(
       "http://your-navidrome-server:4533".to_string(),
       "your_username".to_string(),
       "your_password".to_string(),
   );
   ```

3. Run the server:
   ```bash
   ./target/release/server
   ```
   
   The server will start on `0.0.0.0:8080` by default.

## API Reference

The server provides REST endpoints and WebSocket connections for real-time updates.

### HTTP API Endpoints

#### Music Discovery
- `GET /api/status` - Get current player status
- `GET /api/search?q=<query>` - Search for songs
- `GET /api/artists` - Get all artists from music library

#### Playback Control  
- `POST /api/play/:song_id` - Play a specific song (with song JSON in body)
- `POST /api/pause` - Pause current playback
- `POST /api/resume` - Resume paused playback  
- `POST /api/stop` - Stop playback completely
- `POST /api/seek` - Seek to position (body: `{"position_ms": 30000}`)
- `POST /api/volume` - Set volume (body: `{"volume": 0.8}`)

#### Audio Streaming
- `GET /stream/:song_id` - Stream song audio with HTTP Range support
- `GET /health` - Server health check

#### Real-time Updates
- `WS /ws/player` - WebSocket for real-time player events

### API Response Format

All API endpoints return JSON in this format:
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

On errors:
```json
{
  "success": false, 
  "data": null,
  "error": "Error message"
}
```

### WebSocket Events

The player WebSocket sends these event types:
```json
{
  "StatusUpdate": {
    "status": {
      "state": "Playing|Paused|Stopped",
      "current_song": { "id": "...", "title": "...", ... },
      "position": 45.2,
      "duration": 180.0,
      "volume": 0.8
    }
  }
}
```

### Example Usage

#### Start playback:
```bash
curl -X POST http://localhost:8080/api/play/song123 \
  -H "Content-Type: application/json" \
  -d '{"song": {"id": "song123", "title": "Song Title", "artist": "Artist", "album": "Album", "duration": 180}}'
```

#### Stream audio with seeking:
```bash
curl -H "Range: bytes=1000000-2000000" \
  http://localhost:8080/stream/song123 > partial_song.mp3
```

#### Search for songs:
```bash
curl "http://localhost:8080/api/search?q=the%20beatles"
```

## Server Features

### Core Functionality
- 🎵 **Music Service Integration** - Pluggable support for Navidrome (more services coming)
- 🌐 **HTTP/REST API** - Complete REST interface for remote clients  
- 🔌 **WebSocket Updates** - Real-time player status and event streaming
- 🎧 **Centralized Playback** - Server manages playback state across clients
- 🔍 **Music Discovery** - Search songs and browse artists through API

### Advanced Streaming
- 🎶 **Audio Transcoding** - FLAC→MP3 conversion with configurable bitrate
- ⏯️ **Perfect Seeking** - HTTP Range requests with MP3 frame-accurate seeking
- 📡 **Bandwidth Optimization** - Partial content streaming and range support
- 🔄 **Format Conversion** - Automatic format conversion for client compatibility

### Architecture
- 🧩 **Service Abstraction** - Generic MusicService trait for extensibility
- ⚡ **Async/Await** - High-performance async Rust with Tokio
- 🛡️ **Error Handling** - Comprehensive error handling and status reporting
- 🧪 **Comprehensive Tests** - Full test coverage for reliability

## Transcoding Configuration

Enable MP3 transcoding with custom bitrate:
```rust
let navidrome_service = NavidromeClient::new(
    "http://your-server:4533".to_string(),
    "username".to_string(), 
    "password".to_string(),
).enable_mp3_transcoding(320); // 320kbps MP3

// Or custom format
let service = navidrome_service.with_transcoding("mp3".to_string(), 256);
```

## Client Development

This server provides a complete HTTP API for building web, mobile, or desktop music clients. The API handles:

- **Authentication** - Proxies authentication to upstream music services
- **Music Library** - Search, browse, and discovery endpoints
- **Playback Control** - Play, pause, stop, seek, volume control
- **Audio Streaming** - Direct audio streaming with range request support
- **Real-time Updates** - WebSocket events for live UI updates

See the API Reference above for implementation details.

## Requirements

- Rust (latest stable)
- Access to a Navidrome server (or compatible Subsonic API server)
- Network access for remote client connections

## Testing the Server

Once the server is running, you can test it using curl or any HTTP client:

### Health Check
```bash
curl http://localhost:8080/health
```

### Search for Songs
```bash
curl "http://localhost:8080/api/search?q=the%20beatles"
```

### Get Player Status
```bash
curl http://localhost:8080/api/status
```

### Stream Audio (with seeking support)
```bash
# Get full song
curl http://localhost:8080/stream/song_id > song.mp3

# Get specific byte range (for seeking)
curl -H "Range: bytes=1000000-2000000" \
  http://localhost:8080/stream/song_id > partial_song.mp3
```

### WebSocket Testing
Use a WebSocket client like `wscat` to test real-time updates:
```bash
npm install -g wscat
wscat -c ws://localhost:8080/ws/player
```