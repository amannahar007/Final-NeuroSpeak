"""
NeuroSpeak Backend - Real-time EMG-to-Speech System
Receives TCP stream from ESP32-C6, applies word detection, and pushes to dashboard via Socket.io
"""
import json
import logging
from typing import Optional, List, Any
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Condition(BaseModel):
    sensor: str  # e.g., "v1", "v2", "v3"
    operator: str  # e.g., ">", "<", ">=", "<=", "==", "!="
    value: float

class WordConfig(BaseModel):
    word: str
    priority: int
    conditions: List[Condition]

class WordsConfigResponse(BaseModel):
    words: List[WordConfig]

def load_words_config(filepath: str) -> List[WordConfig]:
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        words = []
        for w_data in data.get("words", []):
            words.append(WordConfig(**w_data))
        # Sort by priority (1 = highest)
        return sorted(words, key=lambda w: w.priority)
    except FileNotFoundError:
        logger.warning(f"Config file {filepath} not found. Falling back to default.")
        # Default config based on previous ThresholdConfig
        return [
            WordConfig(
                word="EMERGENCY",
                priority=1,
                conditions=[
                    Condition(sensor="v1", operator=">", value=3000),
                    Condition(sensor="v2", operator=">", value=3000),
                    Condition(sensor="v3", operator=">", value=3000)
                ]
            ),
            WordConfig(
                word="WATER",
                priority=2,
                conditions=[
                    Condition(sensor="v2", operator=">", value=2000)
                ]
            ),
            WordConfig(
                word="HELLO",
                priority=3,
                conditions=[
                    Condition(sensor="v1", operator=">", value=2200),
                    Condition(sensor="v2", operator="<", value=1500)
                ]
            )
        ]
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise ValueError(f"Invalid JSON configuration in {filepath}")

# Load initial config
CONFIG_PATH = "words_config.json"
current_words_config = load_words_config(CONFIG_PATH)

app = FastAPI(title="NeuroSpeak Backend API")

@app.get("/words", response_model=WordsConfigResponse)
async def get_words():
    return WordsConfigResponse(words=current_words_config)

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
    return WordsConfigResponse(words=current_words_config)

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

def detect_word(v1: int, v2: int, v3: int, words_config: List[WordConfig]) -> Optional[str]:
    """
    Detect word based on sensor values and flexible words configuration.
    Iterates over words by priority and evaluates conditions (AND logic).
    
    Args:
        v1: Sensor 1 value (Jaw/Back Ear)
        v2: Sensor 2 value (Chin)
        v3: Sensor 3 value (Temporal/Ear)
        words_config: List of WordConfig instances to evaluate
        
    Returns:
        Detected word string or None if no match
    """
    sensors = {"v1": v1, "v2": v2, "v3": v3}
    
    for word_cfg in words_config:
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

# Wrap FastAPI app with Socket.io ASGI middleware
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)


async def tcp_listener(host: str, port: int, sio_server: socketio.AsyncServer, words_cfg: List[WordConfig]):
    """
    TCP server that listens for ESP32-C6 data stream and emits Socket.io events.
    
    Args:
        host: TCP server host (e.g., "0.0.0.0")
        port: TCP server port (e.g., 9000)
        sio_server: Socket.io AsyncServer instance
        words_cfg: List of WordConfig for word detection
    """
    server = await asyncio.start_server(
        lambda r, w: handle_tcp_client(r, w, sio_server, words_cfg),
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
    sio_server: socketio.AsyncServer,
    words_cfg: List[WordConfig]
):
    """
    Handle individual TCP client connection from ESP32-C6.
    
    Args:
        reader: asyncio StreamReader for reading data
        writer: asyncio StreamWriter for writing data
        sio_server: Socket.io AsyncServer instance
        words_cfg: List of WordConfig for word detection
    """
    addr = writer.get_extra_info('peername')
    logger.info(f"TCP client connected from {addr}")
    
    try:
        while True:
            # Read line from TCP stream
            data = await reader.readline()
            if not data:
                break
                
            line = data.decode('utf-8')
            
            # Parse line
            parsed = parse_line(line)
            if parsed is None:
                logger.warning(f"Malformed line from {addr}: {line.strip()}")
                continue
            
            v1, v2, v3 = parsed
            
            # Emit emg_data event to all connected dashboard clients
            await sio_server.emit('emg_data', {
                'v1': v1,
                'v2': v2,
                'v3': v3
            })
            
            # Detect word using current config
            word = detect_word(v1, v2, v3, words_cfg)
            if word:
                # Emit word_detected event
                await sio_server.emit('word_detected', {
                    'word': word
                })
                logger.info(f"Detected word: {word} (v1={v1}, v2={v2}, v3={v3})")
                
    except Exception as e:
        logger.error(f"Error handling TCP client {addr}: {e}")
    finally:
        logger.info(f"TCP client disconnected from {addr}")
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
    asyncio.create_task(tcp_listener("0.0.0.0", 9000, sio, current_words_config))
    logger.info("NeuroSpeak backend started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("NeuroSpeak backend shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8000, log_level="info")
