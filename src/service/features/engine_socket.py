from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

import pynng


@runtime_checkable
class EngineSocket(Protocol):
    """Minimal socket interface the Engine depends on."""
    def recv(self) -> bytes: ...
    def send(self, data: bytes) -> None: ...
    def close(self) -> None: ...
    def listen(self, addr: str) -> None: ...


class EngineSocketFactory(Protocol):
    """Factory that creates bound EngineSocket instances for a given
    address."""
    def create(self, addr: str) -> EngineSocket: ...


class NngPairSocketFactory:
    """Default factory using pynng.Pair0 and binding to the given address."""
    def create(self, addr: str) -> EngineSocket:
        sock = pynng.Pair0()
        if addr.startswith("ipc://"):
            # Ensure stale IPC file is removed before binding
            Path(addr.replace("ipc://", "")).unlink(missing_ok=True)
        sock.listen(addr)
        return sock
