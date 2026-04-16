# NeuroSpeak Prototype

Real-time EMG-to-Speech system using ESP32-C6, Python backend, and React dashboard.

## Project Structure

```
neurospeak-prototype/
├── firmware/           # ESP32-C6 Arduino firmware
│   └── firmware.ino
├── backend/            # Python FastAPI + Socket.io backend
│   ├── main.py
│   ├── requirements.txt
│   └── words_config.json
├── dashboard/          # React + Vite frontend
│   ├── src/
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Quick Start

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend will start on:
- HTTP/WebSocket: `http://localhost:8000`
- TCP server: `0.0.0.0:9000`

### 2. Dashboard Setup

```bash
cd dashboard
npm install
npm run dev
```

Dashboard will start on: `http://localhost:3000`

### 3. Firmware Setup

1. Open `firmware/firmware.ino` in Arduino IDE
2. Update configuration:
   - `WIFI_SSID` - Your WiFi network name
   - `WIFI_PASSWORD` - Your WiFi password
   - `TCP_HOST` - IP address of your backend (e.g., "192.168.1.100")
3. Install ESP32 board support in Arduino IDE
4. Select board: ESP32-C6
5. Upload to ESP32-C6

## Hardware Wiring

Connect EMG sensors to ESP32-C6:
- Sensor 1 (Jaw/Back Ear) → GPIO 0 (ADC)
- Sensor 2 (Chin) → GPIO 1 (ADC)
- Sensor 3 (Temporal/Ear) → GPIO 2 (ADC)

## System Flow

1. **ESP32-C6** samples 3 EMG channels at 512Hz
2. Applies 50Hz notch + 20Hz high-pass IIR filters
3. Streams filtered data over TCP: `v1,v2,v3\n`
4. **Python backend** receives TCP stream
5. Applies threshold-based word detection
6. Pushes data + detected words to dashboard via Socket.io
7. **React dashboard** displays:
   - 3 real-time EMG waveform charts
   - Detected word with flash animation
   - Connection status indicator

## Default Word Detection

- **HELLO**: v1 > 2200 AND v2 < 1500
- **WATER**: v2 > 2000
- **EMERGENCY**: v1 > 3000 AND v2 > 3000 AND v3 > 3000

## API Endpoints

- `GET /` - Dashboard (placeholder)
- `GET /thresholds` - Get current thresholds
- `PATCH /thresholds` - Update thresholds at runtime

Example threshold update:
```bash
curl -X PATCH http://localhost:8000/thresholds \
  -H "Content-Type: application/json" \
  -d '{"hello_v1_min": 2000}'
```

## Development Notes

- Backend uses asyncio for concurrent TCP + HTTP/WebSocket
- Dashboard uses Recharts for real-time charts with 5-second rolling window
- Firmware uses hardware timer ISR for precise 512Hz sampling
- All components support auto-reconnection

## Troubleshooting

**ESP32 won't connect to WiFi:**
- Check SSID and password in firmware
- Ensure 2.4GHz WiFi (ESP32 doesn't support 5GHz)

**Dashboard shows "DISCONNECTED":**
- Ensure backend is running on port 8000
- Check browser console for Socket.io errors

**No data in charts:**
- Verify ESP32 is connected to backend (check backend logs)
- Ensure TCP_HOST in firmware matches backend IP

## Next Steps

See `tasks-parallel.md` for additional features being developed in parallel:
- Configurable word detection via JSON file
- Documentation and examples
- Deployment tools

## License

MIT
