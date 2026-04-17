# Word Configuration Guide

This guide explains the example word configurations and the muscle gestures that trigger them.

## Configuration Format

```json
{
  "word": "WORD_NAME",
  "priority": 1,
  "conditions": [
    {"sensor": "v1", "operator": ">", "value": 2000}
  ]
}
```

- **word**: The text to display when detected
- **priority**: Lower number = higher priority (1 is highest)
- **conditions**: List of conditions that must ALL be true (AND logic)
- **sensor**: `v1` (Jaw), `v2` (Chin), `v3` (Temporal)
- **operator**: `>`, `<`, `>=`, `<=`, `==`, `!=`
- **value**: Threshold value (0-4095 for 12-bit ADC)

## Example Words and Gestures

### 1. EMERGENCY (Priority 1)
**Gesture**: Strong clenching of all muscles simultaneously

**Conditions**:
- v1 > 3000 (Strong jaw clench)
- v2 > 3000 (Strong chin tension)
- v3 > 3000 (Strong temporal muscle activation)

**Use Case**: Critical situations requiring immediate attention

---

### 2. WATER (Priority 2)
**Gesture**: Swallowing motion or tongue press

**Conditions**:
- v2 > 2000 (Chin/throat muscle activation)

**Use Case**: Request for water or drink

---

### 3. HELLO (Priority 3)
**Gesture**: Smile or mouth opening with relaxed chin

**Conditions**:
- v1 > 2200 (Jaw movement)
- v2 < 1500 (Relaxed chin)

**Use Case**: Greeting or acknowledgment

---

### 4. YES (Priority 4)
**Gesture**: Jaw clench with temporal muscle activation

**Conditions**:
- v1 > 2500 (Moderate jaw clench)
- v3 > 2500 (Temporal muscle activation)

**Use Case**: Affirmative response

---

### 5. NO (Priority 5)
**Gesture**: Chin tension with relaxed temporal muscles

**Conditions**:
- v2 > 2500 (Chin tension)
- v3 < 1500 (Relaxed temporal)

**Use Case**: Negative response

---

### 6. HELP (Priority 6)
**Gesture**: Moderate jaw clench with moderate chin tension

**Conditions**:
- v1 > 2800 (Moderate-strong jaw)
- v2 > 1800 AND v2 < 2500 (Moderate chin)

**Use Case**: Request for assistance

---

### 7. STOP (Priority 7)
**Gesture**: Strong temporal muscle activation (ear wiggle or temple clench)

**Conditions**:
- v3 > 3000 (Strong temporal activation)

**Use Case**: Stop current action

---

### 8. FOOD (Priority 8)
**Gesture**: Chewing motion (moderate jaw + chin)

**Conditions**:
- v1 > 1800 AND v1 < 2200 (Moderate jaw)
- v2 > 1800 (Moderate chin)

**Use Case**: Request for food

---

### 9. PAIN (Priority 9)
**Gesture**: Grimace (jaw + temporal tension)

**Conditions**:
- v1 > 2000 (Jaw tension)
- v3 > 2000 (Temporal tension)

**Use Case**: Indicate discomfort or pain

---

### 10. TIRED (Priority 10)
**Gesture**: Relaxed state (all muscles below threshold)

**Conditions**:
- v1 < 1500 (Relaxed jaw)
- v2 < 1500 (Relaxed chin)
- v3 < 1500 (Relaxed temporal)

**Use Case**: Indicate fatigue or need for rest

---

## Calibration Tips

### Finding Your Baseline
1. Sit relaxed with sensors attached
2. Monitor sensor values in dashboard
3. Note resting values (typically 500-1500)

### Setting Thresholds
1. Perform desired gesture
2. Note peak sensor values
3. Set threshold 10-20% below peak for reliability
4. Test and adjust as needed

### Avoiding False Positives
- Ensure sufficient gap between word thresholds
- Use priority ordering (higher priority words checked first)
- Combine multiple conditions (AND logic) for specificity

### Muscle Fatigue
- Thresholds may need adjustment after extended use
- Lower thresholds if muscles become fatigued
- Take breaks to maintain consistent signal quality

## Advanced Patterns

### Range Detection
```json
{
  "word": "MEDIUM",
  "conditions": [
    {"sensor": "v1", "operator": ">", "value": 2000},
    {"sensor": "v1", "operator": "<", "value": 3000}
  ]
}
```

### Inverse Detection (Relaxation)
```json
{
  "word": "RELAX",
  "conditions": [
    {"sensor": "v1", "operator": "<", "value": 1000}
  ]
}
```

### Multi-Sensor Patterns
```json
{
  "word": "COMPLEX",
  "conditions": [
    {"sensor": "v1", "operator": ">", "value": 2500},
    {"sensor": "v2", "operator": "<", "value": 1500},
    {"sensor": "v3", "operator": ">", "value": 2000}
  ]
}
```

## Testing Your Configuration

### Using the API
```bash
# Get current configuration
curl http://localhost:8000/words

# Update configuration
curl -X POST http://localhost:8000/words \
  -H "Content-Type: application/json" \
  -d @words_config.example.json
```

### Using Test Data Generator
```bash
# Generate test patterns
python test_data_generator.py | nc localhost 9000
```

### Manual Testing
1. Attach sensors
2. Open dashboard
3. Perform gestures
4. Observe detected words
5. Adjust thresholds in `words_config.json`
6. Reload configuration via API or restart backend

## Troubleshooting

**Word not detected:**
- Check sensor values in dashboard
- Lower threshold values
- Verify conditions are correct
- Check priority ordering

**Wrong word detected:**
- Increase threshold values
- Add more specific conditions
- Adjust priority ordering
- Check for sensor noise

**Inconsistent detection:**
- Improve electrode placement
- Check sensor connections
- Add filtering (already implemented in firmware)
- Calibrate for current muscle state
