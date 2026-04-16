# NeuroSpeak Deployment Guide

## Quick Start (Development)

### 1. Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Backend runs on:
- HTTP/WebSocket: http://localhost:8000
- TCP: 0.0.0.0:9000

### 2. Dashboard
```bash
cd dashboard
npm install
npm run dev
```
Dashboard runs on: http://localhost:3000

### 3. Firmware
1. Open `firmware/firmware.ino` in Arduino IDE
2. Update WiFi credentials and backend IP
3. Upload to ESP32-C6

## Production Deployment (Docker)

### Prerequisites
- Docker and Docker Compose installed
- ESP32-C6 configured with production backend IP

### Deploy with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services will be available at:
- Dashboard: http://localhost (port 80)
- Backend API: http://localhost:8000
- TCP Server: localhost:9000

### Individual Container Builds

**Backend:**
```bash
cd backend
docker build -t neurospeak-backend .
docker run -p 8000:8000 -p 9000:9000 \
  -v $(pwd)/words_config.json:/app/words_config.json \
  neurospeak-backend
```

**Dashboard:**
```bash
cd dashboard
docker build -t neurospeak-dashboard .
docker run -p 80:80 neurospeak-dashboard
```

## Configuration

### Word Detection Configuration

Edit `backend/words_config.json` to customize word detection:

```json
{
  "words": [
    {
      "word": "CUSTOM_WORD",
      "priority": 1,
      "conditions": [
        {"sensor": "v1", "operator": ">", "value": 2500},
        {"sensor": "v2", "operator": "<", "value": 1800}
      ]
    }
  ]
}
```

**Supported operators:** `>`, `<`, `>=`, `<=`, `==`, `!=`

**Priority:** Lower number = higher priority (1 is highest)

### Runtime Configuration Updates

Update word configuration without restart:

```bash
curl -X POST http://localhost:8000/words \
  -H "Content-Type: application/json" \
  -d @words_config.json
```

View current configuration:
```bash
curl http://localhost:8000/words
```

## Health Checks

Run the health check script:

```bash
cd backend
python health_check.py
```

Expected output:
```
✓ TCP server is listening on localhost:9000
✓ HTTP server is responding on localhost:8000
✓ Socket.io endpoint is accessible
✓ /words endpoint is accessible (3 words configured)
✓ All checks passed!
```

## Testing

### Test with Simulated Data

Generate synthetic EMG data:

```bash
cd backend
python test_data_generator.py | nc localhost 9000
```

This will send random EMG patterns including HELLO, WATER, and EMERGENCY triggers.

### Manual Testing

Send test data via netcat:

```bash
# Test HELLO (v1 > 2200, v2 < 1500)
echo "2500,1000,1000" | nc localhost 9000

# Test WATER (v2 > 2000)
echo "1000,2500,1000" | nc localhost 9000

# Test EMERGENCY (all > 3000)
echo "3500,3500,3500" | nc localhost 9000
```

## Monitoring

### Backend Logs

```bash
# Docker
docker-compose logs -f backend

# Direct
python main.py  # logs to stdout
```

### Dashboard Logs

```bash
# Docker
docker-compose logs -f dashboard

# Development
npm run dev  # logs to console
```

### ESP32 Logs

Connect via serial monitor (115200 baud):
- WiFi connection status
- TCP connection status
- Sample transmission status

## Troubleshooting

### Backend won't start
- Check if ports 8000 and 9000 are available
- Verify `words_config.json` is valid JSON
- Check Python version (requires 3.10+)

### Dashboard shows "DISCONNECTED"
- Verify backend is running
- Check Socket.io connection in browser console
- Ensure CORS is enabled (already configured)

### ESP32 won't connect
- Verify WiFi credentials
- Check backend IP address in firmware
- Ensure backend TCP server is listening (port 9000)
- Check firewall rules

### No word detection
- Verify EMG sensor connections
- Check sensor values in dashboard charts
- Adjust thresholds in `words_config.json`
- Test with simulated data first

## Performance Tuning

### Backend
- Adjust Socket.io emit rate (currently 30Hz)
- Tune TCP buffer sizes for high-frequency data
- Enable uvicorn workers for production

### Dashboard
- Adjust rolling window size (currently 150 points)
- Optimize chart rendering for lower-end devices
- Enable production build optimizations

### Firmware
- Verify 512Hz sampling rate with logic analyzer
- Adjust filter coefficients if needed
- Monitor WiFi signal strength

## Security Considerations

### Production Checklist
- [ ] Change default CORS settings to specific origins
- [ ] Add authentication for API endpoints
- [ ] Use HTTPS/WSS for encrypted communication
- [ ] Secure WiFi credentials (use environment variables)
- [ ] Implement rate limiting on API endpoints
- [ ] Add input validation for word configuration updates

### Network Security
- Use VPN or private network for ESP32 ↔ Backend communication
- Firewall rules to restrict TCP port 9000 access
- HTTPS reverse proxy (nginx/traefik) for dashboard

## Scaling

### Multiple ESP32 Devices
- Backend supports multiple concurrent TCP connections
- Each device streams independently
- Dashboard shows aggregated data from all devices

### Load Balancing
- Use nginx/HAProxy for multiple backend instances
- Sticky sessions required for Socket.io
- Shared Redis for Socket.io adapter (multi-instance)

## Backup and Recovery

### Configuration Backup
```bash
# Backup word configuration
cp backend/words_config.json backend/words_config.backup.json

# Restore
cp backend/words_config.backup.json backend/words_config.json
```

### Docker Volume Backup
```bash
# Backup
docker run --rm -v neurospeak_backend:/data -v $(pwd):/backup \
  alpine tar czf /backup/backend-data.tar.gz /data

# Restore
docker run --rm -v neurospeak_backend:/data -v $(pwd):/backup \
  alpine tar xzf /backup/backend-data.tar.gz -C /
```

## Support

For issues and questions:
1. Check logs (backend, dashboard, ESP32)
2. Run health check script
3. Test with simulated data
4. Review configuration files
5. Check network connectivity

## License

MIT
