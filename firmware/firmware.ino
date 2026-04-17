/**
 * NeuroSpeak Firmware for ESP32-C6
 * Samples 3 EMG channels at 512Hz, applies IIR filters, streams over TCP
 */

#include <WiFi.h>

// ===== CONFIGURATION =====
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* TCP_HOST = "192.168.1.100";  // Replace with your backend IP
const int TCP_PORT = 9000;

// ADC pins for EMG sensors
const int SENSOR_1_PIN = 0;  // Jaw/Back Ear
const int SENSOR_2_PIN = 1;  // Chin
const int SENSOR_3_PIN = 2;  // Temporal/Ear

// Sampling rate
const int SAMPLE_RATE_HZ = 512;

// ===== FILTER STATE =====
struct FilterState {
  float a1 = 0.0f;  // notch: delayed input x[n-1]
  float a2 = 0.0f;  // notch: delayed input x[n-2]
  float z1 = 0.0f;  // high-pass: delayed input x[n-1]
  float z2 = 0.0f;  // high-pass: delayed input x[n-2]
};

// One filter state per channel
FilterState ch[3];

// ISR communication
volatile bool sample_ready = false;
volatile int raw[3];

// TCP client
WiFiClient client;

// Hardware timer
hw_timer_t* timer = NULL;

// ===== TIMER ISR =====
void IRAM_ATTR onTimer() {
  // Read all three ADC channels synchronously
  raw[0] = analogRead(SENSOR_1_PIN);
  raw[1] = analogRead(SENSOR_2_PIN);
  raw[2] = analogRead(SENSOR_3_PIN);
  
  // Set flag for main loop
  sample_ready = true;
}

// ===== FILTER FUNCTIONS =====
float apply_notch_filter(float in, FilterState& state) {
  // 50Hz notch filter coefficients
  // x = in - (-1.5869*a1) - (0.9650*a2)
  // y = 0.9658*x + (-1.5798*a1) + 0.9658*a2
  
  float x = in - (-1.5869f * state.a1) - (0.9650f * state.a2);
  float y = 0.9658f * x + (-1.5798f * state.a1) + 0.9658f * state.a2;
  
  // Update state
  state.a2 = state.a1;
  state.a1 = x;
  
  return y;
}

float apply_highpass_filter(float in, FilterState& state) {
  // 20Hz high-pass filter coefficients
  // x = in - (-0.8508*z1) - (0.3025*z2)
  // y = 0.5383*x + (-1.0766*z1) + 0.5383*z2
  
  float x = in - (-0.8508f * state.z1) - (0.3025f * state.z2);
  float y = 0.5383f * x + (-1.0766f * state.z1) + 0.5383f * state.z2;
  
  // Update state
  state.z2 = state.z1;
  state.z1 = x;
  
  return y;
}

// ===== WIFI FUNCTIONS =====
void WiFiEvent(WiFiEvent_t event) {
  switch(event) {
    case ARDUINO_EVENT_WIFI_STA_DISCONNECTED:
      Serial.println("WiFi disconnected, reconnecting...");
      WiFi.reconnect();
      break;
    default:
      break;
  }
}

void setup_wifi() {
  Serial.println("Connecting to WiFi...");
  WiFi.mode(WIFI_STA);
  WiFi.onEvent(WiFiEvent);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

// ===== TCP FUNCTIONS =====
void connect_tcp() {
  if (!client.connected()) {
    Serial.println("Connecting to TCP server...");
    if (client.connect(TCP_HOST, TCP_PORT)) {
      Serial.println("TCP connected");
    } else {
      Serial.println("TCP connection failed, retrying in 1s");
      delay(1000);
    }
  }
}

// ===== SETUP =====
void setup() {
  Serial.begin(115200);
  Serial.println("NeuroSpeak Firmware Starting...");
  
  // Configure ADC pins
  analogReadResolution(12);  // 12-bit ADC (0-4095)
  pinMode(SENSOR_1_PIN, INPUT);
  pinMode(SENSOR_2_PIN, INPUT);
  pinMode(SENSOR_3_PIN, INPUT);
  
  // Setup WiFi
  setup_wifi();
  
  // Setup hardware timer for 512Hz sampling
  timer = timerBegin(1000000);  // 1MHz timer
  timerAttachInterrupt(timer, &onTimer);
  timerAlarm(timer, 1000000 / SAMPLE_RATE_HZ, true, 0);  // 512Hz = 1953.125us period
  
  Serial.println("Firmware ready");
}

// ===== MAIN LOOP =====
void loop() {
  // Ensure TCP connection
  connect_tcp();
  
  // Process sample when ready
  if (sample_ready) {
    sample_ready = false;
    
    // Apply filters to each channel
    int filtered[3];
    for (int i = 0; i < 3; i++) {
      float val = (float)raw[i];
      
      // Apply notch filter first
      val = apply_notch_filter(val, ch[i]);
      
      // Then apply high-pass filter
      val = apply_highpass_filter(val, ch[i]);
      
      // Convert back to int
      filtered[i] = (int)val;
    }
    
    // Format and transmit over TCP
    if (client.connected()) {
      char buffer[64];
      snprintf(buffer, sizeof(buffer), "%d,%d,%d\n", 
               filtered[0], filtered[1], filtered[2]);
      
      int written = client.print(buffer);
      if (written == 0) {
        Serial.println("TCP send failed, disconnecting");
        client.stop();
      }
    }
  }
  
  // Small delay to prevent watchdog issues
  delay(1);
}
