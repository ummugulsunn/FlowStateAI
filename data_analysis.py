"""
Data quality checker for FlowStateAI event logs.

Reads newline-delimited JSON event logs and reports:
- JSON validity (integrity)
- Event counts by type (keyboard, mouse move, mouse click, mouse scroll)
- Anomaly checks: timestamp ordering, extreme velocities, negative timings
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


EXTREME_VELOCITY_THRESHOLD = 50_000  # px/s


def analyze_log(file_path: Path) -> Dict[str, Any]:
    """
    Analyze a newline-delimited JSON log file.

    Args:
        file_path: Path to the JSON log file.

    Returns:
        A dictionary containing counts and anomaly summaries.
    """
    stats = {
        "total_lines": 0,
        "valid_json": 0,
        "invalid_json": 0,
        "event_counts": {
            "key_press": 0,
            "key_release": 0,
            "mouse_move": 0,
            "mouse_click": 0,
            "mouse_scroll": 0,
            "other": 0,
        },
        "anomalies": {
            "timestamp_order": 0,
            "extreme_velocity": 0,
            "negative_dwell_or_flight": 0,
        },
        "examples": {
            "extreme_velocity": [],  # type: List[Tuple[float, float]]
            "negative_dwell_or_flight": [],  # type: List[Tuple[str, float]]
            "timestamp_order": [],  # type: List[Tuple[float, float]]
        },
    }

    previous_ts: Optional[float] = None

    with file_path.open("r", encoding="utf-8") as fp:
        for line in fp:
            stats["total_lines"] += 1
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                stats["valid_json"] += 1
            except json.JSONDecodeError:
                stats["invalid_json"] += 1
                continue

            timestamp = _safe_number(event.get("timestamp"))
            if timestamp is not None and previous_ts is not None and timestamp < previous_ts:
                stats["anomalies"]["timestamp_order"] += 1
                stats["examples"]["timestamp_order"].append((previous_ts, timestamp))
            if timestamp is not None:
                previous_ts = timestamp

            event_type = event.get("event_type", "other")
            stats["event_counts"].setdefault(event_type, 0)
            if event_type in stats["event_counts"]:
                stats["event_counts"][event_type] += 1
            else:
                stats["event_counts"]["other"] += 1

            data = event.get("data", {})
            if event_type == "mouse_move":
                velocity = _safe_number(data.get("velocity"))
                if velocity is not None and velocity > EXTREME_VELOCITY_THRESHOLD:
                    stats["anomalies"]["extreme_velocity"] += 1
                    stats["examples"]["extreme_velocity"].append((timestamp, velocity))
            if event_type in {"key_press", "key_release"}:
                dwell = _safe_number(data.get("dwell_time"))
                flight = _safe_number(data.get("flight_time"))
                if dwell is not None and dwell < 0:
                    stats["anomalies"]["negative_dwell_or_flight"] += 1
                    stats["examples"]["negative_dwell_or_flight"].append(("dwell_time", dwell))
                if flight is not None and flight < 0:
                    stats["anomalies"]["negative_dwell_or_flight"] += 1
                    stats["examples"]["negative_dwell_or_flight"].append(("flight_time", flight))

    return stats


def _safe_number(value: Any) -> Optional[float]:
    """Convert to float if possible; return None otherwise."""
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _print_report(stats: Dict[str, Any]) -> None:
    """Print a concise report to stdout."""
    print("=== FlowStateAI Log Analysis ===")
    print(f"Total lines: {stats['total_lines']}")
    print(f"Valid JSON: {stats['valid_json']} | Invalid JSON: {stats['invalid_json']}")

    counts = stats["event_counts"]
    print(
        "Event counts -> "
        f"key_press: {counts.get('key_press', 0)}, "
        f"key_release: {counts.get('key_release', 0)}, "
        f"mouse_move: {counts.get('mouse_move', 0)}, "
        f"mouse_click: {counts.get('mouse_click', 0)}, "
        f"mouse_scroll: {counts.get('mouse_scroll', 0)}, "
        f"other: {counts.get('other', 0)}"
    )

    anomalies = stats["anomalies"]
    print("Anomalies:")
    print(f"- Timestamp order violations: {anomalies['timestamp_order']}")
    print(f"- Extreme velocity (> {EXTREME_VELOCITY_THRESHOLD} px/s): {anomalies['extreme_velocity']}")
    print(f"- Negative dwell/flight times: {anomalies['negative_dwell_or_flight']}")

    if stats["examples"]["extreme_velocity"]:
        ts, vel = stats["examples"]["extreme_velocity"][0]
        print(f"  Example extreme velocity -> ts: {ts}, velocity: {vel}")
    if stats["examples"]["negative_dwell_or_flight"]:
        name, val = stats["examples"]["negative_dwell_or_flight"][0]
        print(f"  Example negative timing -> {name}: {val}")
    if stats["examples"]["timestamp_order"]:
        prev_ts, ts = stats["examples"]["timestamp_order"][0]
        print(f"  Example timestamp order violation -> prev: {prev_ts}, current: {ts}")


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Analyze FlowStateAI JSON log for integrity and anomalies."
    )
    parser.add_argument("log_path", type=Path, help="Path to JSON log file (newline-delimited).")
    args = parser.parse_args()

    if not args.log_path.exists():
        raise FileNotFoundError(f"Log file not found: {args.log_path}")

    stats = analyze_log(args.log_path)
    _print_report(stats)


if __name__ == "__main__":
    main()



