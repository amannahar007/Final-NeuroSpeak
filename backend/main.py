"""
NeuroSpeak Backend - Real-time EMG-to-Speech System
Receives TCP stream from ESP32-C6, applies word detection, and pushes to dashboard via Socket.io
"""
import json
import logging
from typing import Optional, List, Any
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import aiohttp
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FIREBASE_URL = "https://neurospeak-fbc17-default-rtdb.europe-west1.firebasedatabase.app/"
FIREBASE_API_KEY = "AIzaSyAElgDdAVDc2hT6oAN6YtIreeO8f6eaCDo"

# Globals to track latest values for 1Hz updating
latest_emg_data = {"v1": 0, "v2": 0, "v3": 0}
aiohttp_session = None

# Real-Time UI + Architecture States
esp_connected = False
recording_active = False
recording_stats = {
    "v1": {"min": 999999, "max": -999999, "sum": 0, "count": 0},
    "v2": {"min": 999999, "max": -999999, "sum": 0, "count": 0},
    "v3": {"min": 999999, "max": -999999, "sum": 0, "count": 0}
}
ui_frame_counter = 0

# Debouncing State Dictionary (stores { "WORD": timestamp })
word_cooldowns = {}
COOLDOWN_SECONDS = 1.5

class Condition(BaseModel):
    sensor: str  # e.g., "v1", "v2", "v3"
    operator: str  # e.g., ">", "<", ">=", "<=", "==", "!="
    value: float

class WordConfig(BaseModel):
    word: str
    priority: int
    conditions: List[Condition]

class SensorRange(BaseModel):
    min: float
    max: float

class IdleRanges(BaseModel):
    v1: SensorRange
    v2: SensorRange
    v3: SensorRange

class WordsConfigResponse(BaseModel):
    idle_ranges: IdleRanges
    words: List[WordConfig]

def load_words_config(filepath: str) -> WordsConfigResponse:
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        # Sort words by priority internally
        obj = WordsConfigResponse(**data)
        obj.words = sorted(obj.words, key=lambda w: w.priority)
        return obj
    except FileNotFoundError:
        logger.warning(f"Config file {filepath} not found. Falling back to default.")
        return WordsConfigResponse(
            idle_ranges=IdleRanges(
                v1=SensorRange(min=-912, max=854),
                v2=SensorRange(min=-514, max=518),
                v3=SensorRange(min=-577, max=584),
            ),
            words=[]
        )
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise ValueError(f"Invalid JSON configuration in {filepath}")

# Load initial config
CONFIG_PATH = "words_config.json"
current_words_config = load_words_config(CONFIG_PATH)

app = FastAPI(title="NeuroSpeak Backend API")

@app.get("/words", response_model=WordsConfigResponse)
async def get_words():
    return current_words_config

@app.post("/words", response_model=WordsConfigResponse)
async def update_words(config: WordsConfigResponse):
    global current_words_config
    
    # Save to file
    try:
        with open(CONFIG_PATH, "w") as f:
            # We dump the model properly mapping its representation
            model_dict = config.model_dump()
            json.dump(model_dict, f, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # Reload internal state
    current_words_config = load_words_config(CONFIG_PATH)
    return current_words_config

def parse_line(line: str) -> Optional[tuple[int, int, int]]:
    """
    Parse a TCP line in format "v1,v2,v3\n" into a tuple of three integers.
    
    Args:
        line: String in format "v1,v2,v3\n" where v1, v2, v3 are integers
        
    Returns:
        Tuple of (v1, v2, v3) if valid, None otherwise
        
    Examples:
        >>> parse_line("1024,2048,512\\n")
        (1024, 2048, 512)
        >>> parse_line("invalid")
        None
    """
    try:
        line = line.strip()
        if not line:
            return None
        parts = line.split(',')
        if len(parts) != 3:
            return None
        v1 = int(parts[0])
        v2 = int(parts[1])
        v3 = int(parts[2])
        return (v1, v2, v3)
    except (ValueError, AttributeError):
        return None

def evaluate_condition(sensor_val: float, operator: str, target_val: float) -> bool:
    if operator == ">": return sensor_val > target_val
    elif operator == "<": return sensor_val < target_val
    elif operator == ">=": return sensor_val >= target_val
    elif operator == "<=": return sensor_val <= target_val
    elif operator == "==": return sensor_val == target_val
    elif operator == "!=": return sensor_val != target_val
    return False

def detect_word(v1: int, v2: int, v3: int, words_config: WordsConfigResponse) -> Optional[str]:
    """
    Detect word based on sensor values and flexible words configuration.
    Iterates over words by priority and evaluates conditions (AND logic).
    
    Args:
        v1: Sensor 1 value (Jaw/Back Ear)
        v2: Sensor 2 value (Chin)
        v3: Sensor 3 value (Temporal/Ear)
        words_config: WordsConfigResponse schema payload
        
    Returns:
        Detected word string or None if no match
    """
    sensors = {"v1": v1, "v2": v2, "v3": v3}
    
    if not words_config: return None
    
    for word_cfg in words_config.words:
        all_met = True
        for cond in word_cfg.conditions:
            sensor_val = sensors.get(cond.sensor)
            if sensor_val is None:
                all_met = False
                break
            if not evaluate_condition(sensor_val, cond.operator, cond.value):
                all_met = False
                break
        
        if all_met:
            return word_cfg.word

    return None


import asyncio
import socketio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Socket.io AsyncServer
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

@sio.on('connect')
async def on_connect(sid, environ):
    global esp_connected
    await sio.emit('esp_status', {'connected': esp_connected}, to=sid)

@sio.on('start_recording')
async def start_recording(sid):
    global recording_active, recording_stats
    recording_stats = {
        "v1": {"min": 999999, "max": -999999, "sum": 0, "count": 0},
        "v2": {"min": 999999, "max": -999999, "sum": 0, "count": 0},
        "v3": {"min": 999999, "max": -999999, "sum": 0, "count": 0}
    }
    recording_active = True
    logger.info("Recording Started by Dashboard.")

@sio.on('stop_recording')
async def stop_recording(sid):
    global recording_active, recording_stats
    recording_active = False
    logger.info("Recording Stopped by Dashboard.")
    
    results = {}
    for ch in ["v1", "v2", "v3"]:
        st = recording_stats[ch]
        if st["count"] > 0:
            results[ch] = {
                "min": st["min"], 
                "max": st["max"], 
                "envelope": round(st["sum"] / st["count"], 2)
            }
        else:
            results[ch] = {"min": 0, "max": 0, "envelope": 0}
            
    await sio.emit('recording_stats', results)

# Wrap FastAPI app with Socket.io ASGI middleware
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)


async def tcp_listener(host: str, port: int, sio_server: socketio.AsyncServer):
    """
    TCP server that listens for ESP32-C6 data stream and emits Socket.io events.
    
    Args:
        host: TCP server host (e.g., "0.0.0.0")
        port: TCP server port (e.g., 9000)
        sio_server: Socket.io AsyncServer instance
    """
    server = await asyncio.start_server(
        lambda r, w: handle_tcp_client(r, w, sio_server),
        host,
        port
    )
    
    addr = server.sockets[0].getsockname()
    logger.info(f"TCP server listening on {addr[0]}:{addr[1]}")
    
    async with server:
        await server.serve_forever()


async def handle_tcp_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    sio_server: socketio.AsyncServer
):
    """
    Handle individual TCP client connection from ESP32-C6.
    
    Args:
        reader: asyncio StreamReader for reading data
        writer: asyncio StreamWriter for writing data
        sio_server: Socket.io AsyncServer instance
    """
    global esp_connected, recording_active, recording_stats, ui_frame_counter, current_words_config
    
    addr = writer.get_extra_info('peername')
    logger.info(f"TCP client connected from {addr}")
    esp_connected = True
    asyncio.create_task(sio_server.emit('esp_status', {'connected': esp_connected}))
    
    try:
        while True:
            # Read line from TCP stream with 3-second timeout. 
            # ESP32 streams at ~512Hz, so 3 seconds implies a hard disconnect (power loss/WiFi drop)
            try:
                data = await asyncio.wait_for(reader.readline(), timeout=3.0)
            except asyncio.TimeoutError:
                logger.warning(f"TCP stream timed out for {addr}. Assuming ESP disconnected.")
                break
                
            if not data:
                break
                
            line = data.decode('utf-8')
            
            # Parse line
            parsed = parse_line(line)
            if parsed is None:
                logger.warning(f"Malformed line from {addr}: {line.strip()}")
                continue
            
            v1, v2, v3 = parsed
            
            # Update globals for Firebase 1Hz loop
            latest_emg_data["v1"] = v1
            latest_emg_data["v2"] = v2
            latest_emg_data["v3"] = v3
            
            # Update Recording Stats
            if recording_active:
                for var, ch in [(v1, "v1"), (v2, "v2"), (v3, "v3")]:
                    if var < recording_stats[ch]["min"]: recording_stats[ch]["min"] = var
                    if var > recording_stats[ch]["max"]: recording_stats[ch]["max"] = var
                    recording_stats[ch]["sum"] += var
                    recording_stats[ch]["count"] += 1
            
            # Emit emg_data event to all connected dashboard clients AT 34Hz (Decimation)
            ui_frame_counter += 1
            if ui_frame_counter >= 15:
                ui_frame_counter = 0
                await sio_server.emit('emg_data', {
                    'v1': v1,
                    'v2': v2,
                    'v3': v3
                })
            
            word = detect_word(v1, v2, v3, current_words_config)
            
            # Enforce 1.5-second temporal cooldown to prevent 512Hz TTS Spam
            current_time = datetime.now().timestamp()
            can_trigger = False
            
            if word:
                last_time = word_cooldowns.get(word, 0)
                if (current_time - last_time) >= COOLDOWN_SECONDS:
                    can_trigger = True
                    word_cooldowns[word] = current_time

            if can_trigger:
                # Emit word_detected event
                await sio_server.emit('word_detected', {
                    'word': word
                })
                # Log to Firebase asynchronously
                asyncio.create_task(log_word_to_firebase(word, v1, v2, v3))
                logger.info(f"Detected word: {word} (v1={v1}, v2={v2}, v3={v3})")
                
    except Exception as e:
        logger.error(f"Error handling TCP client {addr}: {e}")
    finally:
        logger.info(f"TCP client disconnected from {addr}")
        esp_connected = False
        asyncio.create_task(sio_server.emit('esp_status', {'connected': esp_connected}))
        writer.close()
        await writer.wait_closed()


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve dashboard HTML (placeholder for now, will be replaced with React build)"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NeuroSpeak Dashboard</title>
    </head>
    <body>
        <h1>NeuroSpeak Backend Running</h1>
        <p>Dashboard will be served here after React build.</p>
        <p>For development, run the React dev server separately on port 3000.</p>
    </body>
    </html>
    """


@app.on_event("startup")
async def startup_event():
    """Launch TCP listener as background task on startup"""
    global aiohttp_session
    aiohttp_session = aiohttp.ClientSession()
    asyncio.create_task(tcp_listener("0.0.0.0", 9000, sio))
    asyncio.create_task(firebase_realtime_updater())
    logger.info("NeuroSpeak backend started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global aiohttp_session
    if aiohttp_session:
        await aiohttp_session.close()
    logger.info("NeuroSpeak backend shutting down")


async def firebase_realtime_updater():
    """Background task to push latest EMG data to Firebase every 1 second"""
    while True:
        await asyncio.sleep(1.0)
        
        # Idle Bypassing Check
        if current_words_config and current_words_config.idle_ranges:
            idle = current_words_config.idle_ranges
            v1, v2, v3 = latest_emg_data["v1"], latest_emg_data["v2"], latest_emg_data["v3"]
            if (idle.v1.min <= v1 <= idle.v1.max) and \
               (idle.v2.min <= v2 <= idle.v2.max) and \
               (idle.v3.min <= v3 <= idle.v3.max):
                   # We are cleanly inside the idle threshold zone across all 3 electrodes. 
                   # Neglect this frame and save backend bandwidth!
                   continue

        if aiohttp_session:
            url = f"{FIREBASE_URL}/EMG/realtime.json?auth={FIREBASE_API_KEY}"
            payload = {
                "v1": latest_emg_data["v1"],
                "v2": latest_emg_data["v2"],
                "v3": latest_emg_data["v3"],
                "timestamp": datetime.utcnow().isoformat()
            }
            try:
                # PATCH updates only the fields we pass
                await aiohttp_session.patch(url, json=payload)
            except Exception as e:
                logger.error(f"Error updating Firebase Realtime: {e}")

async def log_word_to_firebase(word: str, v1: int, v2: int, v3: int):
    """Log detected words to Firebase"""
    if aiohttp_session:
        url = f"{FIREBASE_URL}/EMG/logs.json?auth={FIREBASE_API_KEY}"
        payload = {
            "word": word,
            "v1": v1,
            "v2": v2,
            "v3": v3,
            "timestamp": datetime.utcnow().isoformat()
        }
        try:
            # POST appends a new unique ID record to the node
            await aiohttp_session.post(url, json=payload)
        except Exception as e:
            logger.error(f"Error logging word to Firebase: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8000, log_level="info")
