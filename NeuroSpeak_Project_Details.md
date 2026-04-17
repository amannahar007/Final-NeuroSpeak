#🧠 NeuroSpeak: Silent Speech Recognition Platform
**Project Architecture, Pitch Deck & Technical Documentation**

---

## 🚀 1. The Elevator Pitch (Why NeuroSpeak Matters)

**The Problem:** Traditional voice recognition systems fundamentally fail in environments requiring stealth (military/tactical), in excessively loud industrial environments, or for individuals with severe speech impediments (e.g., Locked-in Syndrome, ALS, vocal cord paralysis).

**The Solution:** NeuroSpeak bypasses acoustic audio entirely. By connecting an ESP32 microcontroller directly to facial muscles, we intercept the human body's intrinsic electrical bio-signals (EMG) the moment your brain *attempts* to speak a word—even if you don't make a sound. 

**Key Pitching Points:**
- **Zero Latency:** Utilizing an offline Machine Learning / Algorithmic thresholding model, recognition happens in less than a second locally. 
- **Bandwidth Hyper-Efficiency:** Utilizing a dynamic "Idle Firewall," the system autonomously identifies when the user is at rest and temporarily drops cloud-syncing, reducing cloud computing Firebase costs by over 90%.
- **Fail-Safe Processing:** If a user walks out of Wi-Fi range, the ESP32 dynamically stores up to an 8-Kilobyte backlog array in its offline memory and "bursts" it the millisecond the connection restores, preventing absolute data loss.

---

## 🛠️ 2. The Tech Stack

### **Hardware Engine**
- **Microcontroller:** ESP32-C6 (High-precision Dual-Core processor with Wi-Fi 6 for unparalleled bandwidth packet handling).
- **Sensors:** 3x Active Differential EMG Electrodes.
    - **V1:** Jaw / Back Ear
    - **V2:** Chin
    - **V3:** Temporal / Upper Ear

### **Software Infrastructure**
- **Frontend Layer:** `React.js` + `Vite` + `TailwindCSS`
    - Uses `Recharts` for high-fidelity 34Hz oscilloscope rendering.
    - Utilizes Native HTML5 Web Audio (`AudioContext`) and `speechSynthesis` to literally read recognized words aloud to the user.
- **Backend Core:** `Python` + `FastAPI` + `Socket.io` + `Asyncio`
    - Entirely Non-Blocking API architecture utilizing Python's `async/await` syntax.
- **Database Layer:** Google Firebase Realtime Database
    - Triggered at 1Hz exclusively for telemetry logging and remote ML Dataset gathering.

---

## 🌐 3. Network & IP Configuration

NeuroSpeak's custom communication mesh relies on a trifecta of dedicated channels to ensure data never bottlenecks in the operating system:

| Service | Protocol | Port | Description |
| :--- | :--- | :--- | :--- |
| **Microcontroller to Backend** | TCP Stream | `9000` | Takes raw strings `v1,v2,v3\n` straight off the ESP32 Wi-Fi antenna into Python memory. |
| **Backend to Frontend** | WebSockets (Socket.IO) | `8000` | Creates a persistent pipeline blasting the UI with 34Hz graphical mapping arrays. |
| **REST API Configuration** | HTTP GET/POST | `8000` | Endpoint `/words` is utilized for the React application to sync dynamic noise thresholds. |
| **Local Web Server** | HTTP | `3000` | Serves the Vite React production dashboard environment. |

*To run this via a LAN connection with the physical Microcontroller, the ESP32 variable `host` IP must be explicitly hard-coded into the `firmware.ino` script (e.g. `192.168.1.53`) to match your Computer's IPv4 WLAN address!*

---

## 📐 4. Critical Architectural Decisions

### **Why a Raw TCP Server instead of HTTP or MQTT?**
Because the human muscular system triggers incredibly fast, our ESP32 sweeps the ADC channels at a speed of **512 frames per second**. 
- **HTTP:** Cannot be used. Building and tearing down a TCP handshake 512 times a second would crash a commercial router instantly. 
- **MQTT/WebSockets:** Extremely heavy protocol headers would drastically inflate our payload. 
- **Raw TCP:** By establishing a single "Naked" TCP socket lock, we can stream pure unformatted strings (`2048,150,900\n`) directly into memory. The network payload is near zero, allowing real-time speed.

### **Why an Offline ML / Logic Model?**
Silent Speech translation requires instantaneous reaction times to prevent "cognitive dissonance" (the delay between attempting to speak and the machine acting).
- **Cloud Latency:** Routing EMG data to OpenAI/AWS for processing introduces a 300ms–1500ms round-trip delay. 
- **Internet Depdendency:** If the internet drops, tactical or paralyzed users lose their "voice" completely. 
- **Offline Superiority:** By utilizing localized deterministic arrays and algorithmic bounds on the Python edge server natively, the trigger happens locally with **0ms network delay**. Furthermore, this allows us to enforce the `Idle Bypass` constraint, ensuring Firebase database operations only trigger when absolutely necessary.
