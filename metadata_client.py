"""
Music metadata client for testing custom metadata features.
Demonstrates setting and retrieving custom song metadata.
"""
import requests
import json
from typing import Dict, List, Optional

class MetadataClient:
    def __init__(self, server_url: str = "http://pi-server:8080"):
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()
    
    def search_songs(self, query: str) -> List[Dict]:
        """Search for songs."""
        try:
            response = self.session.get(
                f"{self.server_url}/api/search",
                params={"q": query}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", [])
        except requests.RequestException as e:
            print(f"Error searching: {e}")
        return []
    
    def get_song_metadata(self, song_id: str) -> Optional[Dict]:
        """Get custom metadata for a song."""
        try:
            response = self.session.get(f"{self.server_url}/api/metadata/{song_id}")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data")
        except requests.RequestException as e:
            print(f"Error getting metadata: {e}")
        return None
    
    def update_song_metadata(self, song_id: str, metadata: Dict) -> bool:
        """Update custom metadata for a song."""
        try:
            response = self.session.post(
                f"{self.server_url}/api/metadata/{song_id}",
                json=metadata
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
        except requests.RequestException as e:
            print(f"Error updating metadata: {e}")
        return False
    
    def record_play_event(self, song_id: str, duration_played: int, total_duration: int, skip_reason: str = None) -> bool:
        """Record a play event."""
        event = {
            "song_id": song_id,
            "started_at": "2025-01-06T12:00:00Z",  # In real app, use current time
            "duration_played_ms": duration_played,
            "total_duration_ms": total_duration,
            "skip_reason": skip_reason
        }
        
        try:
            response = self.session.post(f"{self.server_url}/api/play_event", json=event)
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
        except requests.RequestException as e:
            print(f"Error recording play event: {e}")
        return False
    
    def smart_shuffle(self, criteria: Optional[Dict] = None) -> List[Dict]:
        """Get smart shuffled songs based on criteria."""
        request = {"criteria": criteria} if criteria else {}
        
        try:
            response = self.session.post(f"{self.server_url}/api/smart_shuffle", json=request)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", [])
        except requests.RequestException as e:
            print(f"Error with smart shuffle: {e}")
        return []

def run_metadata_demo():
    """Run metadata demonstration."""
    client = MetadataClient()
    
    print("📊 Custom Metadata Demo")
    print("========================")
    
    # Health check
    print("1. Checking server connection...")
    try:
        response = client.session.get(f"{client.server_url}/health")
        if response.status_code == 200:
            print("   ✅ Server is healthy")
        else:
            print("   ❌ Server not responding")
            return
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return
    
    # Search for songs
    print("\n2. Finding songs to add metadata...")
    search_query = input("   Enter search query (or press Enter for empty search): ").strip()
    
    songs = client.search_songs(search_query)
    if not songs:
        print("   ❌ No songs found")
        return
    
    print(f"   Found {len(songs)} songs:")
    for i, song in enumerate(songs[:5], 1):  # Show first 5
        print(f"   {i}. {song.get('title', 'Unknown')} - {song.get('artist', 'Unknown')}")
    
    # Select a song for metadata demo
    if songs:
        selected_song = songs[0]  # Use first song for demo
        song_id = selected_song['id']
        
        print(f"\n3. Working with song: {selected_song.get('title', 'Unknown')}")
        
        # Get existing metadata
        print("   Getting existing metadata...")
        existing_metadata = client.get_song_metadata(song_id)
        if existing_metadata:
            print("   Existing custom metadata:")
            print(f"      {json.dumps(existing_metadata, indent=6)}")
        else:
            print("   No existing custom metadata")
        
        # Demo: Add custom metadata
        print("\n4. Adding custom metadata...")
        sample_metadata = {
            "song_id": song_id,
            "energy": 0.8,           # High energy song
            "valence": 0.6,          # Moderately happy
            "tempo": 128,            # BPM
            "color": "#FF6B35",      # Orange color (synesthesia)
            "mood": json.dumps(["energetic", "upbeat", "motivational"]),
            "tags": json.dumps(["workout", "driving", "favorite"]),
            "personal_rating": 8,     # Rating out of 10
            "shuffle_weight": 1.2,    # Higher chance in shuffle
            "skip_probability": 0.1,  # Low chance of being skipped
            "custom_genre": "Electronic Rock"
        }
        
        print("   Setting metadata:")
        for key, value in sample_metadata.items():
            if key != "song_id":
                print(f"      {key}: {value}")
        
        if client.update_song_metadata(song_id, sample_metadata):
            print("   ✅ Metadata updated successfully")
        else:
            print("   ❌ Failed to update metadata")
        
        # Verify the update
        print("\n5. Verifying metadata update...")
        updated_metadata = client.get_song_metadata(song_id)
        if updated_metadata:
            print("   Updated metadata:")
            print(f"      {json.dumps(updated_metadata, indent=6)}")
        
        # Demo: Record play event
        print("\n6. Recording play event...")
        if client.record_play_event(song_id, 120000, 180000, None):  # Played 2 min of 3 min song
            print("   ✅ Play event recorded")
        else:
            print("   ❌ Failed to record play event")
        
        # Demo: Smart shuffle
        print("\n7. Testing smart shuffle...")
        shuffle_criteria = {
            "min_energy": 0.5,
            "max_energy": 1.0,
            "min_rating": 5,
            "limit": 10
        }
        
        print("   Shuffle criteria:")
        for key, value in shuffle_criteria.items():
            print(f"      {key}: {value}")
        
        shuffled_songs = client.smart_shuffle(shuffle_criteria)
        if shuffled_songs:
            print(f"   ✅ Smart shuffle returned {len(shuffled_songs)} songs:")
            for i, song in enumerate(shuffled_songs[:3], 1):
                print(f"      {i}. {song.get('title', 'Unknown')} - {song.get('artist', 'Unknown')}")
        else:
            print("   ❌ Smart shuffle returned no results")
        
        print("\n✅ Metadata demo completed!")
        print("\nCustom metadata allows you to:")
        print("  • Tag songs with energy levels, moods, and colors")
        print("  • Create sophisticated shuffle algorithms")
        print("  • Track listening patterns and preferences")
        print("  • Build personalized music discovery systems")
        print("  • Implement features like 'workout playlists' or 'chill vibes'")

if __name__ == "__main__":
    run_metadata_demo()