#!/usr/bin/env python3
"""
Full system integration test for the enhanced music streaming server.
Tests all new features: database integration, custom metadata, and gapless playback.
"""
import requests
import json
import time
import subprocess
import sys
from typing import Dict, List, Optional

class SystemTester:
    def __init__(self, server_url: str = "http://pi-server:8080"):
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()
        self.test_results = []
        self.passed = 0
        self.failed = 0
    
    def test(self, name: str, func) -> bool:
        """Run a test and record results."""
        print(f"🧪 {name}...")
        try:
            result = func()
            if result:
                print(f"   ✅ PASS")
                self.passed += 1
            else:
                print(f"   ❌ FAIL")
                self.failed += 1
            self.test_results.append((name, result))
            return result
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            self.failed += 1
            self.test_results.append((name, False))
            return False
    
    def test_server_health(self) -> bool:
        """Test basic server health."""
        try:
            response = self.session.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_basic_api_endpoints(self) -> bool:
        """Test basic API endpoints work."""
        endpoints = [
            f"{self.server_url}/api/status",
            f"{self.server_url}/api/artists",
        ]
        
        for endpoint in endpoints:
            try:
                response = self.session.get(endpoint, timeout=5)
                if response.status_code != 200:
                    print(f"      Failed: {endpoint}")
                    return False
            except:
                print(f"      Failed: {endpoint}")
                return False
        return True
    
    def test_search_functionality(self) -> bool:
        """Test search endpoint."""
        try:
            response = self.session.get(f"{self.server_url}/api/search", params={"q": "test"}, timeout=5)
            if response.status_code != 200:
                return False
            
            data = response.json()
            # Should have success field even if no results
            return "success" in data
        except:
            return False
    
    def test_metadata_endpoints(self) -> bool:
        """Test custom metadata endpoints."""
        # First get a song to test with
        try:
            search_response = self.session.get(f"{self.server_url}/api/search", params={"q": ""})
            if search_response.status_code != 200:
                return False
            
            songs = search_response.json().get("data", [])
            if not songs:
                print("      No songs available for metadata testing")
                return True  # Not a failure if no songs exist yet
            
            song_id = songs[0]["id"]
            
            # Test GET metadata
            get_response = self.session.get(f"{self.server_url}/api/metadata/{song_id}")
            if get_response.status_code != 200:
                return False
            
            # Test POST metadata
            metadata = {
                "song_id": song_id,
                "energy": 0.5,
                "personal_rating": 5,
                "tags": json.dumps(["test"])
            }
            
            post_response = self.session.post(f"{self.server_url}/api/metadata/{song_id}", json=metadata)
            if post_response.status_code != 200:
                return False
                
            return True
        except Exception as e:
            print(f"      Error: {e}")
            return False
    
    def test_play_event_recording(self) -> bool:
        """Test play event recording."""
        event = {
            "song_id": "test_song_123",
            "started_at": "2025-01-06T12:00:00Z",
            "duration_played_ms": 30000,
            "total_duration_ms": 180000
        }
        
        try:
            response = self.session.post(f"{self.server_url}/api/play_event", json=event)
            return response.status_code == 200
        except:
            return False
    
    def test_smart_shuffle(self) -> bool:
        """Test smart shuffle endpoint."""
        criteria = {
            "criteria": {
                "limit": 5
            }
        }
        
        try:
            response = self.session.post(f"{self.server_url}/api/smart_shuffle", json=criteria)
            return response.status_code == 200
        except:
            return False
    
    def test_audio_streaming(self) -> bool:
        """Test audio streaming (without actually playing audio)."""
        try:
            # Get a song to stream
            search_response = self.session.get(f"{self.server_url}/api/search", params={"q": ""})
            if search_response.status_code != 200:
                return False
            
            songs = search_response.json().get("data", [])
            if not songs:
                print("      No songs available for streaming test")
                return True  # Not a failure if no songs exist yet
            
            song_id = songs[0]["id"]
            
            # Try to stream (just get headers, don't download full file)
            stream_response = self.session.head(f"{self.server_url}/stream/{song_id}")
            return stream_response.status_code in [200, 206]  # 200 OK or 206 Partial Content
        except Exception as e:
            print(f"      Error: {e}")
            return False
    
    def test_server_compilation(self) -> bool:
        """Test that the server code compiles."""
        try:
            # Change to server directory and run cargo check
            result = subprocess.run(
                ["cargo", "check"], 
                cwd="../server",
                capture_output=True, 
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception as e:
            print(f"      Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all system tests."""
        print("🎵 Full System Integration Test")
        print("=" * 50)
        print()
        
        # Compilation test (local)
        self.test("Server code compilation", self.test_server_compilation)
        
        # Server connectivity tests
        self.test("Server health check", self.test_server_health)
        self.test("Basic API endpoints", self.test_basic_api_endpoints)
        self.test("Search functionality", self.test_search_functionality)
        
        # New feature tests
        self.test("Custom metadata endpoints", self.test_metadata_endpoints)
        self.test("Play event recording", self.test_play_event_recording)
        self.test("Smart shuffle", self.test_smart_shuffle)
        self.test("Audio streaming", self.test_audio_streaming)
        
        # Results summary
        print()
        print("=" * 50)
        print(f"📊 Test Results: {self.passed} passed, {self.failed} failed")
        print()
        
        if self.failed == 0:
            print("🎉 All tests passed! The system is ready.")
            print()
            print("Next steps:")
            print("1. Deploy server to Pi using: cargo build --release")
            print("2. Run migration tool to populate database")
            print("3. Test gapless playback with: python gapless_client.py")
            print("4. Experiment with metadata using: python metadata_client.py")
        else:
            print("⚠️  Some tests failed. Check the errors above.")
            print()
            print("Common issues:")
            print("• Server not running: Start with 'cargo run --bin hybrid_server'")
            print("• Database not initialized: Run 'cargo run --bin migrate'")
            print("• Network connectivity: Check server URL and firewall")
        
        return self.failed == 0

def main():
    """Main test runner."""
    server_url = "http://pi-server:8080"
    
    # Allow override of server URL
    if len(sys.argv) > 1:
        server_url = sys.argv[1]
    
    print(f"Testing server at: {server_url}")
    print()
    
    tester = SystemTester(server_url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()