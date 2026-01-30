# FlowStateAI

**Passive Behavioral Sensing for Cognitive Load Estimation**

FlowStateAI captures keyboard and mouse interactions to predict cognitive load levels (Low / Medium / High) using machine learning. Unlike invasive methods such as EEG or eye-tracking, this approach uses passive sensing—analyzing natural computer interactions without interrupting the user.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Data Format](#data-format)
- [Modules](#modules)
- [Architecture](#architecture)
- [Sample Data](#sample-data)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Team](#team)
- [License](#license)

---

## Features

- **Real-time event capture**: Keyboard (press/release) and mouse (move/click/scroll) events
- **Behavioral metrics**: Dwell time, flight time, velocity, click intervals
- **Thread-safe I/O**: Queue-based writer thread prevents listener blocking
- **Session management**: Auto-organized as `sessions/YYYY-MM-DD/session_HHMMSS.json`
- **Data validation**: Built-in analysis tool for integrity and anomaly detection
- **CLI interface**: Easy-to-use command-line tool with duration control

---

## Installation

### Prerequisites

- Python 3.11 or higher
- macOS, Linux, or Windows

### Setup

```bash
# Clone the repository
git clone https://github.com/ummugulsunn/FlowStateAI.git
cd FlowStateAI

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Platform-Specific Notes

**macOS**: Accessibility permission required
1. System Preferences → Security & Privacy → Privacy → Accessibility
2. Add your terminal application (Terminal, iTerm, or Cursor)

**Linux**: X11 library may be required
```bash
sudo apt-get install python3-xlib
```

---

## Quick Start

### Collect Data

```bash
# Run until Ctrl+C
python data_collector.py

# Run for specific duration (e.g., 60 seconds)
python data_collector.py --duration 60

# Custom output directory
python data_collector.py --output-dir my_sessions
```

### Analyze Data

```bash
# Analyze a session file
python data_analysis.py sessions/2026-01-30/session_143803.json
```

**Example output:**
```
=== FlowStateAI Log Analysis ===
Total lines: 327
Valid JSON: 327 | Invalid JSON: 0
Event counts -> key_press: 3, key_release: 3, mouse_move: 271, mouse_click: 8, mouse_scroll: 42
Anomalies:
- Timestamp order violations: 0
- Extreme velocity (> 50000 px/s): 15
- Negative dwell/flight times: 0
```

---

## Data Format

Events are stored as newline-delimited JSON (NDJSON). Each line is a self-contained JSON object:

### Keyboard Event

```json
{
  "timestamp": 1738234567.123,
  "event_type": "key_press",
  "data": {
    "key": "a",
    "press_time": 1738234567.123,
    "flight_time": 0.056
  }
}
```

### Mouse Event

```json
{
  "timestamp": 1738234570.256,
  "event_type": "mouse_move",
  "data": {
    "x": 150,
    "y": 220,
    "velocity": 391.5
  }
}
```

### Captured Metrics

| Metric | Description | Cognitive Load Correlation |
|--------|-------------|---------------------------|
| **Dwell Time** | Key hold duration (press → release) | Increases with stress/fatigue |
| **Flight Time** | Time between consecutive keystrokes | Increases with cognitive load |
| **Velocity** | Mouse speed (px/s) | Fluctuates with fatigue |
| **Click Interval** | Time between consecutive clicks | Varies with attention state |

---

## Modules

### `data_collector.py` — Data Collection

Core module for real-time behavioral data capture.

**Programmatic Usage:**

```python
from data_collector import AdvancedDataCollector

collector = AdvancedDataCollector(base_dir="sessions")
collector.start()

# ... data collection in progress ...

collector.stop()
```

**CLI Usage:**

```bash
python data_collector.py [--duration SECONDS] [--output-dir PATH]
```

### `data_analysis.py` — Data Validation

Validates JSON integrity and detects anomalies in collected data.

```bash
python data_analysis.py <log_file>
```

**Checks performed:**
- JSON parsing validity
- Timestamp ordering
- Extreme velocity detection (> 50,000 px/s)
- Negative timing values

### `flow_logger.py` — Logging Utility

Centralized logging with console and file output.

```python
from flow_logger import setup_logger

logger = setup_logger(name="flowstate", log_file="flowstate.log")
logger.info("Application started")
```

---

## Architecture

### Data Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA COLLECTION                          │
├─────────────────────────────────────────────────────────────────┤
│  User Input (keyboard + mouse)                                  │
│         ↓                                                       │
│  pynput Listeners (event capture)                               │
│         ↓                                                       │
│  Thread-safe Queue (buffer)                                     │
│         ↓                                                       │
│  Writer Thread (JSON serialization)                             │
│         ↓                                                       │
│  Session File (NDJSON)                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      FEATURE EXTRACTION                         │
├─────────────────────────────────────────────────────────────────┤
│  Dwell Time | Flight Time | Velocity | Click Intervals         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       MODEL TRAINING                            │
├─────────────────────────────────────────────────────────────────┤
│  Random Forest | XGBoost | LSTM | Bi-LSTM | CNN-LSTM           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         PREDICTION                              │
├─────────────────────────────────────────────────────────────────┤
│  Cognitive Load Classification: Low | Medium | High             │
└─────────────────────────────────────────────────────────────────┘
```

### Why Passive Sensing?

| Approach | Pros | Cons |
|----------|------|------|
| **EEG** | High accuracy | Expensive, intrusive, requires setup |
| **Eye Tracking** | Detailed attention data | Requires special hardware |
| **Passive Sensing** | Non-intrusive, scalable, low cost | Indirect measurement |

FlowStateAI uses passive sensing to enable **scalable, non-intrusive** cognitive load estimation that works on any standard computer.

---

## Project Structure

```
FlowStateAI/
├── data_collector.py        # Main data collection module
├── data_analysis.py         # Data validation and analysis
├── flow_logger.py           # Logging configuration
├── calculator.py            # Arithmetic helper functions
├── user_reg.py              # User registration (in-memory)
├── requirements.txt         # Python dependencies
├── README.md                # Documentation (English)
├── README_TR.md             # Documentation (Turkish)
├── library_usage_guide.md   # Library usage guide
├── data_collector_report.md # Technical report
└── sessions/                # Collected data
    └── YYYY-MM-DD/
        └── session_HHMMSS.json
```

---

## Sample Data

Three sample data files are included for testing:

| File | Content | Events |
|------|---------|--------|
| `session_sample_keyboard.json` | Keyboard events only | 22 |
| `session_sample_mouse.json` | Mouse events only | 20 |
| `session_sample_mixed.json` | Mixed (keyboard + mouse) | 23 |

**Test with sample data:**

```bash
python data_analysis.py sessions/2026-01-30/session_sample_mixed.json
```

---

## Troubleshooting

### "This process is not trusted" (macOS)

Grant Accessibility permission:
1. System Preferences → Security & Privacy → Privacy → Accessibility
2. Click the lock icon and enter your password
3. Add and enable your terminal application

### No events captured

- Verify Accessibility permission is granted
- Restart the terminal application after granting permission
- Check if another application is capturing input events

### High CPU usage

- Mouse move events are throttled (0.1s / 5px threshold)
- If still high, increase throttling in `_on_move()` method

---

## Roadmap

- [ ] Real-time model integration
- [ ] NASA-TLX labeling interface
- [ ] Flutter frontend integration
- [ ] REST API endpoints
- [ ] Dashboard visualization

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Team

**Backend (Python)**
- Havin
- Ümmügülsün

**Frontend (Flutter)**
- Elif
- Hiranur

---

## License

This project is for educational purposes.

---

## Acknowledgments

- [pynput](https://github.com/moses-palmer/pynput) — Input monitoring library
- NASA-TLX — Task Load Index for ground truth labeling

---

**[Turkish Documentation (README_TR.md)](README_TR.md)**
