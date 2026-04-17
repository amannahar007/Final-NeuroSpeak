# NeuroSpeak Backend

Python FastAPI + Socket.io backend for real-time EMG data processing and word detection.

## Requirements

- Python 3.10 or higher
- pip package manager

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Configuration

### TCP Server
- **Host**: `0.0.0.0` (listens on all interfaces)
- **Port**: `9000`

### HTTP/WebSocket Server
- **Host**: `0.0.0.0`
- **Port**: `8000`

### Word Detection Configuration

Edit `words_config.json` to customize word detection:

```json
{
  "words": [
    {
      "word": "HELLO",
      "priority": 3,
      "conditions": [
        {"sensor": "v1", "operator": ">", "value": 2200},
        {"sensor": "v2", "operator": "<", "value": 1500}
      ]
    }
  ]
}
```

**Supported operators**: `>`, `<`, `>=`, `<=`, `==`, `!=`

**Priority**: Lower number = higher priority (1 is highest)

## Running

### Development
```bash
python main.py
```

### Production
```bash
uvicorn main:socket_app --host 0.0.0.0 --port 8000 --workers 1
```

**Note**: Use only 1 worker to maintain TCP server state.

## API Endpoints

### GET /
Returns a placeholder HTML page.

### GET /words
Get current word detection configuration.

**Response:**
```json
{
  "words": [
    {
      "word": "HELLO",
      "priority": 3,
      "conditions": [...]
    }
  ]
}
```

### POST /words
Update word detection configuration at runtime.

**Request Body:**
```json
{
  "words": [...]
}
```

**Response:** Updated configuration

### GET /thresholds (Legacy)
Get current threshold configuration (for backward compatibility).

### PATCH /thresholds (Legacy)
Update threshold configuration (for backward compatibility).

## Socket.io Events

### Emitted by Server

**emg_data**
```json
{
  "v1": 1024,
  "v2": 2048,
  "v3": 512
}
```
Emitted for every parsed sample from ESP32.

**word_detected**
```json
{
  "word": "HELLO"
}
```
Emitted when a word is detected based on threshold conditions.

## Architecture

```
ESP32-C6 (TCP :9000) → Backend → Socket.io → Dashboard
                         ↓
                    Word Detection
                         ↓
                   words_config.json
```

## Troubleshooting

**Port already in use:**
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

**TCP connection refused:**
- Ensure firewall allows port 9000
- Check ESP32 is configured with correct backend IP

**No word detection:**
- Check `words_config.json` thresholds
- Monitor backend logs for sensor values
- Use `GET /words` to verify configuration

## Development

### Adding New Words

1. Edit `words_config.json`
2. Add new word with conditions
3. Set appropriate priority
4. Restart backend or use `POST /words` endpoint

### Testing Without Hardware

Use netcat to simulate ESP32:
```bash
echo "2500,1000,1000" | nc localhost 9000
```

## Logging

Backend logs include:
- TCP client connections/disconnections
- Malformed line warnings
- Detected words with sensor values
- Configuration updates

Set log level in `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```
