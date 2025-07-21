import threading
import time
import pynng
from abc import ABC, abstractmethod


class Engine(ABC):
    """Engine drives a background thread that reads raw messages, calls
    'self.process()', and publishes outputs."""
    def __init__(self, settings):
        self.settings = settings

        # control flags
        self._running = False
        self._paused = threading.Event()
        self._thread = threading.Thread(
            target=self._run_loop, name="EngineLoop", daemon=True
        )

        # sockets
        self._in_sock = pynng.Sub0()
        self._in_sock.dial(str(settings.mq_addr_in))
        self._in_sock.subscribe(b"")  # receive everything

        self._out_sock = pynng.Pub0()
        self._out_sock.listen(str(settings.mq_addr_out))

    def start(self) -> str:
        if not self._running:
            self._running = True
            self._thread.start()
            return "engine started"
        return "engine already running"

    def _run_loop(self) -> None:
        while self._running:
            if self._paused.is_set():
                time.sleep(0.1)
                continue

            try:
                raw = self._in_sock.recv_msg()
                result = self.process(raw)
                if result is not None:
                    self._out_sock.send(result)
            except Exception:
                # TODO: we might want to log this
                continue

    def stop(self) -> str:
        if self._running:
            self._running = False
            self._thread.join(timeout=1.0)
            return "engine stopped"
        return "engine not running"

    def pause(self) -> str:
        self._paused.set()
        return "engine paused"

    def resume(self) -> str:
        self._paused.clear()
        return "engine resumed"

    @abstractmethod
    def process(self, raw_message: bytes) -> bytes | None:
        """Decode raw_message, run parser(s)/detector(s), and return something
        to publish (or None to skip)."""
        pass
