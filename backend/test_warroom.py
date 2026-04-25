#!/usr/bin/env python3
"""Test War Room SSE endpoint."""

import requests
import sys

def test_warroom_endpoint():
    """Test that the War Room SSE endpoint is accessible."""
    url = "http://localhost:5000/api/stream/warroom"
    
    print(f"Testing War Room SSE endpoint: {url}")
    print("Connecting to stream...")
    print("-" * 60)
    
    try:
        response = requests.get(url, stream=True, timeout=120)
        
        if response.status_code != 200:
            print(f"❌ Error: Status code {response.status_code}")
            return False
        
        print("✓ Connected successfully!")
        print("Receiving events:\n")
        
        event_count = 0
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                if decoded.startswith('data:'):
                    event_count += 1
                    print(f"[Event {event_count}] {decoded}")
                    
                    # Stop after 10 events for testing
                    if event_count >= 10:
                        print("\n✓ Received 10 events successfully!")
                        print("War Room SSE endpoint is working correctly.")
                        return True
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to backend.")
        print("Make sure the Flask server is running on port 5000.")
        return False
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_warroom_endpoint()
    sys.exit(0 if success else 1)
