"""
Advanced data collector for passive behavioral sensing.

Captures keyboard and mouse events using ``pynput`` while offloading file
writing to a background thread via a queue to avoid blocking listeners.
"""

from __future__ import annotations

import json
import math
import os
import queue
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from pynput import keyboard, mouse


class AdvancedDataCollector:
    """
    Collect keyboard and mouse dynamics and persist them as JSON lines.

    The collector writes session files under ``sessions/YYYY-MM-DD/`` with
    names like ``session_140522.json``. Events are enqueued and flushed to disk
    by a dedicated writer thread to keep listeners non-blocking.
    """

    def __init__(self, base_dir: str | os.PathLike[str] = "sessions") -> None:
        self.base_dir = Path(base_dir)
        self.session_dir = self.base_dir / time.strftime("%Y-%m-%d")
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.session_dir / f"session_{time.strftime('%H%M%S')}.json"

        self.event_queue: queue.Queue[Optional[Dict[str, Any]]] = queue.Queue()
        self.writer_thread: Optional[threading.Thread] = None

        self.keyboard_listener: Optional[keyboard.Listener] = None
        self.mouse_listener: Optional[mouse.Listener] = None

        self.key_press_times: Dict[str, float] = {}
        self.last_key_release_time: Optional[float] = None

        self.last_mouse_pos: Optional[Tuple[int, int]] = None
        self.last_mouse_move_time: Optional[float] = None
        self.last_click_time: Optional[float] = None

        self._running = False

    def start(self) -> None:
        """Start listeners and writer thread."""
        if self._running:
            return
        self._running = True

        self.writer_thread = threading.Thread(target=self._writer_loop, daemon=True)
        self.writer_thread.start()

        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self.mouse_listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll,
        )

        self.keyboard_listener.start()
        self.mouse_listener.start()

    def stop(self) -> None:
        """Stop listeners and writer thread gracefully."""
        if not self._running:
            return
        self._running = False

        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None

        # Signal writer thread to finish.
        self.event_queue.put(None)
        if self.writer_thread:
            self.writer_thread.join(timeout=5)
            self.writer_thread = None

    def _on_press(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        """Handle key press events, including flight time computation."""
        event_time = time.time()
        key_str = self._key_to_str(key)
        flight_time = (
            event_time - self.last_key_release_time
            if self.last_key_release_time is not None
            else None
        )
        self.key_press_times[key_str] = event_time
        self._enqueue_event(
            {
                "timestamp": event_time,
                "event_type": "key_press",
                "data": {
                    "key": key_str,
                    "press_time": event_time,
                    "flight_time": flight_time,
                },
            }
        )

    def _on_release(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        """Handle key release events, including dwell time computation."""
        event_time = time.time()
        key_str = self._key_to_str(key)
        press_time = self.key_press_times.pop(key_str, None)
        dwell_time = event_time - press_time if press_time is not None else None

        self.last_key_release_time = event_time
        self._enqueue_event(
            {
                "timestamp": event_time,
                "event_type": "key_release",
                "data": {
                    "key": key_str,
                    "press_time": press_time,
                    "release_time": event_time,
                    "dwell_time": dwell_time,
                },
            }
        )

    def _on_move(self, x: int, y: int) -> None:
        """Handle mouse move events and estimate velocity with throttling."""
        event_time = time.time()
        velocity = None

        if self.last_mouse_pos is not None and self.last_mouse_move_time is not None:
            dx = x - self.last_mouse_pos[0]
            dy = y - self.last_mouse_pos[1]
            distance = math.hypot(dx, dy)
            dt = event_time - self.last_mouse_move_time
            # Throttle to reduce excessive logging: require time or distance threshold.
            if dt < 0.1 and distance < 5:
                return
            velocity = distance / dt if dt > 0 else None

        self.last_mouse_pos = (x, y)
        self.last_mouse_move_time = event_time

        self._enqueue_event(
            {
                "timestamp": event_time,
                "event_type": "mouse_move",
                "data": {
                    "x": x,
                    "y": y,
                    "velocity": velocity,
                },
            }
        )

    def _on_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        """Handle mouse click events and compute click intervals."""
        event_time = time.time()
        click_interval = (
            event_time - self.last_click_time if self.last_click_time is not None else None
        )
        self.last_click_time = event_time

        self._enqueue_event(
            {
                "timestamp": event_time,
                "event_type": "mouse_click",
                "data": {
                    "x": x,
                    "y": y,
                    "button": str(button),
                    "pressed": pressed,
                    "click_interval": click_interval,
                },
            }
        )

    def _on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        """Handle mouse scroll events."""
        event_time = time.time()
        self._enqueue_event(
            {
                "timestamp": event_time,
                "event_type": "mouse_scroll",
                "data": {"x": x, "y": y, "dx": dx, "dy": dy},
            }
        )

    def _enqueue_event(self, event: Dict[str, Any]) -> None:
        """Place an event into the queue with basic protection."""
        try:
            self.event_queue.put_nowait(event)
        except queue.Full:
            # Drop the event if the queue is unexpectedly full.
            pass

    def _writer_loop(self) -> None:
        """Continuously write queued events to the session file."""
        try:
            with self.session_file.open("a", encoding="utf-8") as fp:
                while True:
                    event = self.event_queue.get()
                    if event is None:
                        break
                    json.dump(event, fp, ensure_ascii=False)
                    fp.write("\n")
                    fp.flush()
        except OSError:
            # Swallow I/O errors to avoid crashing listeners; in production,
            # integrate with a logging mechanism.
            return

    @staticmethod
    def _key_to_str(key: keyboard.Key | keyboard.KeyCode) -> str:
        """Convert a pynput key object to a readable string."""
        try:
            if hasattr(key, "char") and key.char is not None:
                return str(key.char)
            return str(key)
        except Exception:
            return "unknown"


__all__ = ["AdvancedDataCollector"]

