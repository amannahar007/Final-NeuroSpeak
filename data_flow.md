# NeuroSpeak Data Flow Architecture

## 1. Edge Capture (ESP32-C6 Firmware)
1. At precisely **512 times per second (512Hz)**, the ESP32 samples three analog EMG pins. 
2. It passes the raw values through a multi-stage software DSP (Digital Signal Processing):
   - A **50Hz Notch Filter** removes electrical mains power noise.
   - A **20Hz High-Pass Filter** removes baseline wandering from skin resistance.
3. The ESP32 does *not* do database operations or aggregations; it simply strings the three integers together (`v1,v2,v3\n`) and blindly fires them over a TCP socket to the backend to maximize speed and fidelity.

## 2. Server Pipeline (Python Backend)
1. **Reception**: A background asynchronous TCP loop (on port `9000`) reads every incoming line instantly.
2. **Splitting the Path**:
   - **Path A (Dashboard Output)**: It broadcasts every data point at native 30-50 FPS speeds via `Socket.io` out to the React Frontend.
   - **Path B (Word Detection Engine)**: Every single dataset is processed against the patient's personal JSON word threshold configuration. If sensors breach the configuration logic, a "Detection Event" triggers.

## 3. The Firebase Integration 
Instead of the ESP32 halting its sensor polling to talk to the cloud, the Python backend takes over:
   - **Real-Time Database Tracking (1Hz)**: The Python server accumulates the latest TCP sensor metrics into a variable. Every 1.0 second, a parallel background process (`aiohttp` task) wakes up and silently fires an HTTP `PATCH` payload to Firebase `.../EMG/realtime.json`. 
   - **Persistent Event Logs**: Let's say the patient flexes to trigger the word `"WATER"`. The Word Detection Engine catches it and instantly spawns a detached database sync sub-shell that performs an HTTP `POST` to `.../EMG/logs.json`. Using `POST` generates an auto-incrementing ID row containing the precise TimeStamp UTC, the triggered word ("WATER"), and the sensor flex intensities that caused it. 

### Why Highlight Detected Words This Way?
When you log detected words to Firebase independently of the real-time stream, doctors or machine learning pipelines can later query *only* the specific log-table of timestamps when words were detected, without having to scrape blindly through thousands of lines of useless idle background noise in the realtime stream. This is significantly cheaper, faster, and more robust.
