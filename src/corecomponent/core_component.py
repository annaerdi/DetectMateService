from __future__ import annotations
import logging
import sys
from abc import ABC
from pathlib import Path

from corecomponent.settings import CoreComponentSettings
from corecomponent.features.manager import Manager


class CoreComponent(Manager, ABC):
    """
    Abstract base for every DetectMate component.
    """
    # hard-code component type as class variable, overwrite in subclasses
    component_type: str = "core"

    def __init__(self, settings: CoreComponentSettings | None = None):
        # Defaults first, then start Manager (opens REP socket & thread)
        settings = settings or CoreComponentSettings()
        Manager.__init__(self, settings=settings)

        self.settings = settings
        self.component_id = settings.component_id
        self.log = self._build_logger()
        self._stop_flag = False

        self.log.debug("%s[%s] created", self.component_type, self.component_id)

    # public API
    def setup_io(self) -> None:
        """
        Override in subclasses to open data sockets, load models, etc.
        Called automatically by the context-manager.
        """
        self.log.info("setup_io() placeholder - no data sockets yet")

    def run(self) -> None:
        """
        Placeholder main loop. Override in a subclass.
        Stops when `stop()` sets `_stop_flag` or a 'stop' Manager command arrives.
        """
        self.log.info("Entering placeholder run() loop")
        while not self._stop_flag:
            pass  # do useful work here
        self.log.info("Stop flag detected, exiting run() loop")

    def stop(self) -> None:
        """Ask component to shut down asap"""
        self._stop_flag = True
        self.log.info("Stop flag set for %s[%s]", self.component_type, self.component_id)

    # helpers
    def _build_logger(self) -> logging.Logger:
        Path(self.settings.log_dir).mkdir(parents=True, exist_ok=True)
        name = f"{self.component_type}.{self.component_id}"
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, self.settings.log_level.upper(), logging.INFO))

        fmt = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
        if self.settings.log_to_console:
            sh = logging.StreamHandler(sys.stdout)
            sh.setFormatter(fmt)
            logger.addHandler(sh)
        if self.settings.log_to_file:
            fh = logging.FileHandler(
                Path(self.settings.log_dir) /
                f"{self.component_type}_{self.component_id}.log"
            )
            fh.setFormatter(fmt)
            logger.addHandler(fh)
        return logger

    # context-manager sugar
    def __enter__(self) -> "CoreComponent":
        self.setup_io()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.stop() # shut down gracefully
        self._close_manager()   # close REP socket & thread

        # close log handlers
        for h in list(self.log.handlers):
            h.close()
            self.log.removeHandler(h)
        self.log.info("Bye")
        return False  # propagate exceptions
