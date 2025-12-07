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

