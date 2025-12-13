# FlowStateAI — Week 1 Setup

## Purpose
Initial scaffolding for FlowStateAI with core utilities:
- `flow_logger.py`: centralized logging to console and file.
- `calculator.py`: typed arithmetic helpers with safe division.
- `user_reg.py`: minimal in-memory user registration with validation.

## Requirements
- Python 3.11+

## Setup
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

## Usage
- Configure logging:
  ```python
  from flow_logger import setup_logger

  logger = setup_logger()
  logger.info("FlowStateAI logger ready.")
  ```
- Arithmetic helpers:
  ```python
  from calculator import add, divide

  total = add(2, 3)
  quotient = divide(10, 2)
  ```
- User registration:
  ```python
  from user_reg import UserRegistry

  registry = UserRegistry()
  registry.add_user("Ada", "Lovelace", "ada@example.com")
  print(registry.list_users())
  ```

## Notes
- Logs are written to `flowstate.log` by default (ignored via `.gitignore`).
- Replace the in-memory registry with persistent storage as the project evolves.

## 🔬 Technical Architecture & Methodology
- **Core concept — Passive sensing:** Infer cognitive load and focus from standard computer interaction (keystroke dynamics and mouse dynamics) instead of intrusive signals such as EEG or eye-tracking.
- **Data pipeline:**  
  `User Input (keystroke + mouse streams)` -> `Feature Extraction (flight time, dwell time, velocity, acceleration, click intervals, scroll rhythm)` -> `Labeling (NASA-TLX: Low / Medium / High)` -> `Time-Series Models (RF, XGBoost, LSTM, Bi-LSTM, CNN-LSTM)` -> `Evaluation & Selection` -> `Real-time Desktop Deployment`
- **Input features:** Keystroke timing (flight, dwell), mouse velocity, acceleration, click intervals, and scroll rhythm.
- **Ground truth:** NASA-TLX scores mapped to Low / Medium / High cognitive load classes.
- **Model strategy:** Compare classical (Random Forest, XGBoost) and deep sequence models (LSTM, Bi-LSTM, CNN-LSTM) for time-series classification; select the best-performing model for embedding.
- **Deployment target:** Embed the selected model into a real-time desktop application to infer cognitive load from passive interaction data.

## Week 2: Advanced Data Collection
- `data_collector.py`: Asenkron klavye/fare dinleyicileriyle (pynput) pasif etkileşim verisini toplar; Queue + writer thread ile JSON satırlarına kaydeder, mouse hareketlerini 0.1s/5px eşiğiyle filtreler.
- `data_analysis.py`: Toplanan logların bütünlüğünü ve anomalilerini (timestamp sırası, aşırı velocity, negatif dwell/flight) kontrol eden analiz aracı.
- `library_usage_guide.md`: Pynput tabanlı listener mimarisini ve bilişsel yük tahmini bağlamında klavye/fare metriklerinin önemini açıklayan teknik rehber.


