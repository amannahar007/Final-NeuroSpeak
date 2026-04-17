# NeuroSpeak Architectural Design - Firebase Integration

## Proposed Structural Layout
We are decoupling the slow internet database operations from the high-speed ESP32 data-acquisition microcontroller.

**Before:**
1. ESP32 Collects Data
2. ESP32 Pauses to upload to Firebase via WiFi API 
3. ESP32 Returns to tracking data (potentially missing 50-100 Samples and losing fidelity)

**After (New Design based on TCP streaming):**
1. ESP32 Collects Data and blindly streams it on a raw TCP socket at 512Hz with ZERO pausing or blocking.
2. Python backend captures the stream efficiently on LAN.
3. Python backend asynchronously spawns coroutines to safely bundle data strings into HTTP requests and sends them to Firebase WITHOUT blocking the TCP sensor data reception.

## Continuous Database Testing
To ensure the raw connection to Firebase stands up, an automated `firebase_dummy_sender.py` script mimics independent nodes writing to a new testing path `/dummy_testing`. It continuously bombards the path with HTTP POST/PUT requests to test rate limits and quotas without impacting the main backend flow.
