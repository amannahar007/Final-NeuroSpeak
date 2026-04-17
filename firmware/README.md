# NeuroSpeak Firmware

ESP32-C6 firmware for real-time EMG sampling, filtering, and TCP streaming.

## Requirements

### Hardware
- ESP32-C6 development board
- 3x EMG sensors (surface electrodes)
- USB cable for programming
- WiFi network (2.4GHz)

### Software
- Arduino IDE 2.0 or higher
- ESP32 board support package

## Arduino IDE Setup

### 1. Install ESP32 Board Support

1. Open Arduino IDE
2. Go to **File → Preferences**
3. Add to "Additional Board Manager URLs":
```
https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
```
4. Go to **Tools → Board → Boards Manager**
5. Search for "esp32"
6. Install "esp32 by Espressif Systems"

### 2. Select Board

1. Go to **Tools → Board → esp32**
2. Select **ESP32C6 Dev Module**

### 3. Configure Board Settings

- **USB CDC On Boot**: Enabled
- **CPU Frequency**: 160MHz
- **Flash Size**: 4MB (or your board's flash size)
- **Partition Scheme**: Default
- **Upload Speed**: 921600

## Hardware Wiring

### EMG Sensor Connections

| Sensor | Location | ESP32-C6 Pin | ADC Channel |
|--------|----------|--------------|-------------|
| Sensor 1 | Jaw/Back Ear | GPIO 0 | ADC1_CH0 |
| Sensor 2 | Chin | GPIO 1 | ADC1_CH1 |
| Sensor 3 | Temporal/Ear | GPIO 2 | ADC1_CH2 |

### Power
- Connect EMG sensor ground to ESP32 GND
- Power ESP32 via USB or external 5V supply

### Wiring Diagram
```
EMG Sensor 1 (Jaw)
  Signal → GPIO 0
  GND → GND
  VCC → 3.3V

EMG Sensor 2 (Chin)
  Signal → GPIO 1
  GND → GND
  VCC → 3.3V

EMG Sensor 3 (Temporal)
  Signal → GPIO 2
  GND → GND
  VCC → 3.3V
```

## Configuration

### 1. WiFi Credentials

Edit `firmware.ino`:

```cpp
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
```

### 2. Backend Server

Edit `firmware.ino`:

```cpp
const char* TCP_HOST = "192.168.1.100";  // Your backend IP
const int TCP_PORT = 9000;
```

**Finding your backend IP:**
- Linux/Mac: `ifconfig` or `ip addr`
- Windows: `ipconfig`
- Look for IP address on your local network (usually 192.168.x.x)

### 3. Sensor Pins (Optional)

If using different GPIO pins, edit:

```cpp
const int SENSOR_1_PIN = 0;
const int SENSOR_2_PIN = 1;
const int SENSOR_3_PIN = 2;
```

## Upload Instructions

1. Connect ESP32-C6 to computer via USB
2. Open `firmware.ino` in Arduino IDE
3. Select correct board and port:
   - **Tools → Board → ESP32C6 Dev Module**
   - **Tools → Port → [Your ESP32 Port]**
4. Click **Upload** button (→)
5. Wait for upload to complete
6. Open **Serial Monitor** (Ctrl+Shift+M) at 115200 baud

## Serial Monitor Output

Expected output on successful startup:

```
NeuroSpeak Firmware Starting...
Connecting to WiFi...
.....
WiFi connected
IP address: 192.168.1.150
Connecting to TCP server...
TCP connected
Firmware ready
```

## Troubleshooting

### WiFi Connection Issues

**"WiFi disconnected, reconnecting..."**
- Check SSID and password are correct
- Ensure 2.4GHz WiFi (ESP32 doesn't support 5GHz)
- Move closer to router

**WiFi connects but disconnects repeatedly:**
- Check router settings (disable AP isolation)
- Ensure stable power supply to ESP32
- Try different WiFi channel on router

### TCP Connection Issues

**"TCP connection failed, retrying in 1s"**
- Verify backend is running on specified IP and port
- Check firewall allows port 9000
- Ensure ESP32 and backend are on same network
- Ping backend IP from another device to verify connectivity

### Upload Issues

**"Failed to connect to ESP32"**
- Press and hold BOOT button while clicking Upload
- Try different USB cable
- Check USB drivers are installed
- Try lower upload speed (115200)

**"Port not found"**
- Install CH340/CP2102 USB drivers
- Check USB cable supports data (not charge-only)
- Try different USB port

### Sampling Issues

**Erratic readings:**
- Check sensor connections
- Ensure proper electrode placement
- Check ADC reference voltage (should be 3.3V)
- Add external filtering capacitors if needed

## Filter Specifications

### 50Hz Notch Filter
Removes power-line interference.

**Coefficients:**
```cpp
x = in - (-1.5869*a1) - (0.9650*a2)
y = 0.9658*x + (-1.5798*a1) + 0.9658*a2
```

### 20Hz High-Pass Filter
Removes DC drift and low-frequency noise.

**Coefficients:**
```cpp
x = in - (-0.8508*z1) - (0.3025*z2)
y = 0.5383*x + (-1.0766*z1) + 0.5383*z2
```

## Performance

- **Sampling Rate**: 512 Hz (1.953ms period)
- **ADC Resolution**: 12-bit (0-4095)
- **Filter Processing**: ~50μs per sample
- **TCP Transmission**: ~100μs per sample
- **Total Latency**: <200μs per sample

## Advanced Configuration

### Changing Sampling Rate

Edit in `firmware.ino`:

```cpp
const int SAMPLE_RATE_HZ = 512;  // Change to desired rate
```

**Note**: Backend expects ~512Hz. Changing this may affect word detection.

### Adjusting Filter Coefficients

If you need different filter characteristics, recalculate coefficients using:
- MATLAB: `butter()`, `iirnotch()`
- Python: `scipy.signal.butter()`, `scipy.signal.iirnotch()`
- Online tools: [Filter Design Tool](http://t-filter.engineerjs.com/)

## Development

### Adding Debug Output

```cpp
Serial.print("Sensor 1: ");
Serial.println(filtered[0]);
```

### Monitoring Performance

```cpp
unsigned long start = micros();
// ... code to measure ...
unsigned long elapsed = micros() - start;
Serial.print("Time: ");
Serial.print(elapsed);
Serial.println(" us");
```

## Safety Notes

- EMG sensors are for research/educational use only
- Not for medical diagnosis or treatment
- Ensure proper electrode placement and skin preparation
- Disconnect from power when adjusting electrodes
- Follow local regulations for biomedical devices
