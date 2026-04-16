# NeuroSpeak Quick Reference

## 🚀 Start Commands

```bash
# Backend
cd backend && python main.py

# Dashboard
cd dashboard && npm run dev

# Docker (Production)
docker-compose up -d

# Test Data
cd backend && python test_data_generator.py | nc localhost 9000

# Health Check
cd backend && python health_check.py
```

## 🌐 URLs

- Dashboard (Dev): http://localhost:3000
- Dashboard (Prod): http://localhost
- Backend API: http://localhost:8000
- TCP Server: localhost:9000

## 📡 API Endpoints

```bash
# Get word configuration
curl http://localhost:8000/words

# Update word configuration
curl -X POST http://localhost:8000/words \
  -H "Content-Type: application/json" \
  -d @words_config.json

# Get thresholds (legacy)
curl http://localhost:8000/thresholds

# Update thresholds (legacy)
curl -X PATCH http://localhost:8000/thresholds \
  -H "Content-Type: application/json" \
  -d '{"hello_v1_min": 2000}'
```

## 🧪 Test Commands

```bash
# Test HELLO (v1 > 2200, v2 < 1500)
echo "2500,1000,1000" | nc localhost 9000

# Test WATER (v2 > 2000)
echo "1000,2500,1000" | nc localhost 9000

# Test EMERGENCY (all > 3000)
echo "3500,3500,3500" | nc localhost 9000

# Random patterns
cd backend && python test_data_generator.py | nc localhost 9000
```

## ⚙️ Configuration Files

| File | Purpose |
|------|---------|
| `backend/words_config.json` | Word detection rules |
| `firmware/firmware.ino` | WiFi + TCP settings |
| `dashboard/vite.config.js` | Backend proxy settings |
| `docker-compose.yml` | Container orchestration |

## 🔧 Word Configuration Format

```json
{
  "words": [
    {
      "word": "WORD_NAME",
      "priority": 1,
      "conditions": [
        {"sensor": "v1", "operator": ">", "value": 2500},
        {"sensor": "v2", "operator": "<", "value": 1500}
      ]
    }
  ]
}
```

**Operators:** `>`, `<`, `>=`, `<=`, `==`, `!=`  
**Priority:** 1 = highest, higher numbers = lower priority  
**Sensors:** `v1` (Jaw), `v2` (Chin), `v3` (Temporal)

## 🔌 Hardware Wiring

```
ESP32-C6 Pin → Sensor
─────────────────────
GPIO 0 (ADC) → Sensor 1 (Jaw/Back Ear)
GPIO 1 (ADC) → Sensor 2 (Chin)
GPIO 2 (ADC) → Sensor 3 (Temporal/Ear)
```

## 📊 Default Words

| Word | Conditions |
|------|------------|
| EMERGENCY | v1 > 3000 AND v2 > 3000 AND v3 > 3000 |
| WATER | v2 > 2000 |
| HELLO | v1 > 2200 AND v2 < 1500 |

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Dashboard shows "DISCONNECTED" | Check backend is running on port 8000 |
| No data in charts | Verify ESP32 is connected, check backend logs |
| ESP32 won't connect | Check WiFi credentials and backend IP |
| Word not detecting | Adjust thresholds in `words_config.json` |
| Port already in use | Kill process: `lsof -ti:8000 \| xargs kill -9` |

## 📝 Logs

```bash
# Backend logs (Docker)
docker-compose logs -f backend

# Dashboard logs (Docker)
docker-compose logs -f dashboard

# ESP32 logs
# Connect via serial monitor at 115200 baud

# Backend logs (Direct)
# Printed to stdout when running python main.py
```

## 🔄 Restart Services

```bash
# Docker
docker-compose restart

# Backend (Direct)
# Ctrl+C then python main.py

# Dashboard (Direct)
# Ctrl+C then npm run dev

# ESP32
# Press reset button or re-upload firmware
```

## 📦 Dependencies

**Backend:**
- Python 3.10+
- fastapi, python-socketio, uvicorn

**Dashboard:**
- Node.js 18+
- react, socket.io-client, recharts, tailwindcss

**Firmware:**
- Arduino IDE with ESP32 board support
- WiFi library (built-in)

## 🎯 Performance Specs

- Sampling Rate: 512Hz
- Dashboard Update: 30Hz
- Chart Window: 5 seconds
- Latency: <50ms
- ADC Resolution: 12-bit (0-4095)

## 🔐 Security Checklist

- [ ] Change CORS to specific origins
- [ ] Add API authentication
- [ ] Use HTTPS/WSS
- [ ] Secure WiFi credentials
- [ ] Enable rate limiting
- [ ] Validate all inputs

## 📚 Documentation

- `README.md` - Overview
- `DEPLOYMENT.md` - Deployment guide
- `PROJECT_STATUS.md` - Complete status
- `backend/README.md` - API docs
- `dashboard/README.md` - UI docs
- `firmware/README.md` - Hardware docs

## 💡 Tips

- Use `test_data_generator.py` for testing without hardware
- Run `health_check.py` to verify all services
- Check browser console for Socket.io connection issues
- Monitor ESP32 serial output for debugging
- Adjust chart window size in `App.jsx` if needed
- Use Docker for production deployment

---

**Quick Help:** Run `python backend/health_check.py` to verify system status
