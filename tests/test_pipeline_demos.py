from __future__ import annotations

import json
import threading
import time
from collections import deque
from dataclasses import asdict
from typing import List, Optional, Tuple

import pynng

from corecomponent.core_component import CoreComponent
from corecomponent.settings import CoreComponentSettings
from corecomponent.schemas.schemas import ParserSchema


# Minimal app logic classes
class Parser1:
    """Mirrors basic_methods/methods.py."""
    def parse(self, raw_log: str) -> ParserSchema:
        # Expected format: "LEVEL YYYY-MM-DD HH:MM:SS - message"
        format_part, msg = raw_log.split(" - ", 1)
        level, date, time_ = format_part.split(" ", 2)

        out = ParserSchema(
            parserType="demo-parser",
            parserID=0,
            logID=0,
            log=raw_log,
            logFormatVariables={"LEVEL": level, "DATE": date, "TIME": time_},
        )

        if "Server" in msg:
            # "Server started" or "Server running"
            out.template = "Server<*>"
            out.variables = [msg.split(" ")[1]]
            out.EventID = 0
        elif "Connection failed" in msg:
            out.template = "Connection failed"
            out.variables = []
            out.EventID = 1
        elif "New log message" in msg:
            out.template = "New log message:<*>"
            out.variables = [msg.split(": ", 1)[1]]
            out.EventID = 2
        else:
            # any unknown template -> new ID 99 for this test
            out.template = "UNKNOWN"
            out.variables = [msg]
            out.EventID = 99

        return out


class Detector1:
    """Anomaly-based detector: alerts on EventIDs NOT in known_events."""

    def __init__(self, known_events: Optional[set[int]] = None) -> None:
        self.known_events: set[int] = set() if known_events is None else set(known_events)

    def detect(self, parsed: ParserSchema) -> Tuple[bool, float]:
        if parsed.EventID not in self.known_events:
            # score 0.8
            return True, 0.8
        return False, 0.0

    def train_union(self, new_events: set[int]) -> None:
        self.known_events |= set(new_events)


class Detector2:
    """Signature-based detector: count target_event in a rolling window (> limit_count)."""

    def __init__(self, limit_count: int = 2, target_event: int = 1, window_size: int = 3) -> None:
        self.limit_count = limit_count
        self.target_event = target_event
        self.window_size = window_size
        self._window: deque[int] = deque(maxlen=window_size)

    def set_limit(self, limit_count: int) -> None:
        self.limit_count = int(limit_count)

    def detect(self, parsed: ParserSchema) -> Tuple[bool, float]:
        self._window.append(parsed.EventID)
        count = sum(1 for eid in self._window if eid == self.target_event)
        return (count > self.limit_count), float(count)


# CoreComponent-based demo class
class Demo1Component(CoreComponent):
    """Demo 1: two detectors; D1 (unknown events) and D2 (windowed count)."""

    component_type = "demo1"

    def __init__(self, settings: CoreComponentSettings) -> None:
        super().__init__(settings=settings)
        self.parser = Parser1()
        self.det1 = Detector1(known_events={0, 1})  # known: Server and Connection failed
        self.det2 = Detector2(limit_count=2, target_event=1, window_size=3)

    def process(self, raw_message: bytes) -> bytes | None:
        text = raw_message.decode("utf-8", "ignore").strip()
        parsed = self.parser.parse(text)

        d1_alert, d1_score = self.det1.detect(parsed)
        d2_alert, d2_score = self.det2.detect(parsed)

        winner = (
            "detector_1" if d1_alert
            else "detector_2" if d2_alert
            else "none"
        )
        payload = {
            "input": text,
            "parsed": asdict(parsed),
            "alerts": {
                "detector_1": {"prediction": d1_alert, "score": d1_score},
                "detector_2": {"prediction": d2_alert, "score": d2_score},
            },
            "winner": winner,
        }
        return json.dumps(payload).encode("utf-8")


# pytest infrastructure
def run_component_in_thread(comp: CoreComponent) -> threading.Thread:
    t = threading.Thread(target=comp.run, daemon=True)
    t.start()
    time.sleep(0.2)  # let sockets/threads spin up
    return t


def dial_pair(addr: str) -> pynng.Pair0:
    sock = pynng.Pair0(dial=addr)
    # wait brief handshake
    time.sleep(0.1)
    return sock


# Demo 1 test
def test_demo1_pipeline(tmp_path):
    """End-to-end: Parser + two Detectors riding on CoreComponent Engine."""
    settings = CoreComponentSettings(
        manager_addr=f"ipc://{tmp_path}/d1_cmd.ipc",
        engine_addr=f"ipc://{tmp_path}/d1_engine.ipc",
        engine_autostart=True,
        log_level="DEBUG",
    )
    comp = Demo1Component(settings=settings)
    thread = run_component_in_thread(comp)

    logs = [
        "INFO 2025-02-01 12:00:00 - Server started",
        "ERROR 2025-02-01 12:05:00 - Connection failed",
        "INFO 2025-02-01 12:10:00 - Server running",
        "INFO 2025-02-01 12:20:00 - Server running",
        "INFO 2025-02-01 12:30:00 - Server running",
        "INFO 2025-02-01 12:40:00 - Server running",
        "INFO 2025-02-01 12:41:00 - New log message: Lol I hacked you <3",
        "ERROR 2025-02-01 12:05:00 - Connection failed",
        "ERROR 2025-02-01 12:05:00 - Connection failed",
        "ERROR 2025-02-01 12:05:00 - Connection failed",
        "ERROR 2025-02-01 12:05:00 - Connection failed",
        "ERROR 2025-02-01 12:05:00 - Connection failed",
        "ERROR 2025-02-01 12:05:00 - Connection failed",
    ]

    winners: List[str] = []

    with dial_pair(comp.settings.engine_addr) as sock:
        for log in logs:
            sock.send(log.encode("utf-8"))
            resp = sock.recv()
            obj = json.loads(resp.decode("utf-8"))
            winners.append(obj["winner"])

    assert winners == [
        "none", "none", "none", "none", "none", "none",
        "detector_1",  # unknown EventID 2
        "none", "none",
        "detector_2", "detector_2", "detector_2", "detector_2",
    ]

    comp.stop()
    time.sleep(0.1)
    assert not thread.is_alive() or comp._stop_flag
