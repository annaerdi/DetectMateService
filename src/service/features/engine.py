import threading
import time
from pathlib import Path
import pynng
from abc import ABC, abstractmethod


class Engine(ABC):
    """Engine drives a background thread that reads raw messages over PAIR0,
    calls 'self.process()', and sends outputs back over the same socket.

    Socket creation & binding are abstracted via
    make_engine_socket(addr). Override that method in subclasses (or
    monkeypatch it in tests) to use a custom socket implementation.
    """

    def __init__(self, settings):
        self.settings = settings

        # control flags
        self._running = False
        self._paused = threading.Event()
        self._thread = threading.Thread(
            target=self._run_loop, name="EngineLoop", daemon=True
        )

        # set up the engine socket via the abstraction
        addr = str(settings.engine_addr)
        self._pair_sock = self.make_engine_socket(addr)

        # autostart if enabled
        if getattr(settings, "engine_autostart", True):
            self.start()

    # Socket abstraction
    def make_engine_socket(self, addr: str):
        """Create and bind the engine socket.

        Default: PAIR0 listening on 'addr', with IPC file unlinked if needed.
        Subclasses/tests may override this to return a compatible object
        exposing .recv(), .send(), .close(), and .listen() (if applicable).
        """
        sock = pynng.Pair0()
        if addr.startswith("ipc://"):
            # Ensure stale IPC file is removed before binding
            Path(addr.replace("ipc://", "")).unlink(missing_ok=True)
        sock.listen(addr)
        return sock

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

            # recv phase
            try:
                raw = self._pair_sock.recv()
            except pynng.NNGException as e:
                # Socket likely closed during shutdown; leave loop if we're stopping.
                if not self._running:
                    break
                self._log_engine_error("recv", e)
                continue

            # process phase
            try:
                out = self.process(raw)
            except Exception as e:
                # Log unexpected processing errors; don't silently swallow them.
                self._log_engine_error("process", e)
                continue

            if out is None:
                continue

            # send phase
            try:
                self._pair_sock.send(out)
            except pynng.NNGException as e:
                self._log_engine_error("send", e)
                continue

    def _log_engine_error(self, phase: str, exc: Exception) -> None:
        logger = getattr(self, "log", None)
        if logger:
            logger.exception("Engine error during %s: %s", phase, exc)

    def stop(self) -> str:
        if not self._running:
            return "engine not running"
        self._running = False
        # Closing the socket will raise in the recv() and let the thread exit
        try:
            self._pair_sock.close()
        except pynng.NNGException:
            pass
        self._thread.join(timeout=1.0)
        return "engine stopped"

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
