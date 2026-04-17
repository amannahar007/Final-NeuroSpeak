# Backend Idle Filtering & UI Dynamic Bands

## Goal
The system currently acts on all data. We will establish distinct "Idle Signal Bands" for each sensor based on the user-provided limits. 
If the live telemetry strictly falls within these bands, the backend will autonomously pause all Firebase network syncing to drastically save database bandwidth and operations. Furthermore, the Dashboard will visually map these noise thresholds directly onto the live charts as dashed lines, and allow live reconfiguration.

## User Constraints Provided
- Sensor 1: [-912, 854]
- Sensor 2: [-514, 518]
- Sensor 3: [-577, 584]

## Proposed Changes

### `backend/main.py` & `words_config.json`
- **[MODIFY] Config Schema:** Escalate `words_config.json` into a master configuration file that includes an `idle_ranges` core dictionary defining the 3 sensors' min/max threshold limits.
- **[MODIFY] API Restructuring:** Convert `load_words_config`, `GET /words` and `POST /words` to map and parse the composite schema `WordsConfigResponse(idle_ranges=..., words=...)`.
- **[MODIFY] Firebase Bypass:** Introduce dynamic bypassing in `firebase_realtime_updater`. If the `latest_emg_data` sits concurrently within the active `idle_ranges`, the function will `continue`, completely negating the Firebase `PATCH` action for perfect data-efficiency.

### `dashboard` (React Frontend)
- **[MODIFY] `App.jsx`:** Hook a `fetch` loop fetching `http://localhost:8000/words` upon mount to pull the `idle_ranges` into global state. Pass these threshold domains down as `idleBounds` props to the individual `<EMGChart />` components.
- **[MODIFY] `components/EMGChart.jsx`:** Inject Recharts `<ReferenceLine />` segments into the UI coordinate system plotting `y={idleBounds.max}` and `y={idleBounds.min}`. This enables researchers to instantly flag when spikes break the noise floor!
- **[MODIFY] `components/WordConfigTab.jsx`:** Develop a comprehensive "Idle Range Calibration" card at the top of the interface allowing users to natively mutate and push the `min`/`max` arrays directly to the Python backend without code edits.

## User Feedback Required
> [!IMPORTANT]
> The Firebase Sync bypass requires **ALL THREE** sensors to strictly fall within their respective ideal ranges before halting the loop. If entirely idle, the dashboard graph will remain flat, and Firebase will stagnate. Let me know if you approve this logic or if you want single-channel thresholding instead!
