import json
import random
import time
import urllib.request
import urllib.error
from datetime import datetime

FIREBASE_URL = "https://neurospeak-fbc17-default-rtdb.europe-west1.firebasedatabase.app"
FIREBASE_API_KEY = "AIzaSyAElgDdAVDc2hT6oAN6YtIreeO8f6eaCDo"

# Target the new path: /dummy_testing
TARGET_URL = f"{FIREBASE_URL}/dummy_testing.json?auth={FIREBASE_API_KEY}"

print(f"Target URL: {TARGET_URL}")
print("Starting continuous transmission. Press Ctrl+C to stop.")

def send_dummy_data():
    while True:
        try:
            # Generate dummy payload
            payload = {
                "v1": random.randint(1000, 3000),
                "v2": random.randint(1000, 3000),
                "v3": random.randint(1000, 3000),
                "timestamp": datetime.utcnow().isoformat(),
                "status": "testing"
            }
            
            data = json.dumps(payload).encode('utf-8')
            
            # Using POST to continuously append to the list
            req = urllib.request.Request(TARGET_URL, data=data, method='POST')
            req.add_header('Content-Type', 'application/json')
            
            with urllib.request.urlopen(req) as response:
                response_body = response.read().decode('utf-8')
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Success! Sent dummy values. Response: {response_body}")
                
        except urllib.error.URLError as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Error sending data: {e}")
        except KeyboardInterrupt:
            print("\nStopped by user.")
            break
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Unexpected error: {e}")
            
        # Send approx once per second
        time.sleep(1)

if __name__ == "__main__":
    try:
        send_dummy_data()
    except KeyboardInterrupt:
        print("\nTransmission stopped.")
