from corecomponent.settings import CoreComponentSettings
from corecomponent.core_component import CoreComponent


class SmokeComponent(CoreComponent):
    def __init__(self, settings: CoreComponentSettings | None = None):
        # override the Manager's listen address just for this smoke test:
        settings = settings or CoreComponentSettings(mq_addr_in="ipc:///tmp/smoke_cmd.ipc")
        super().__init__(settings=settings)

    def setup_io(self) -> None:
        # no real I/O, just notify
        self.log.info("SmokeComponent ready to receive commands")

    def process(self, raw_message: bytes) -> bytes | None:
        # Engine requires this, but we do nothing
        return None

    def _handle_cmd(self, cmd: str) -> str:
        # print everything that comes in, then defer to Manager/CoreComponent
        print(f"[smoke] Received command: {cmd!r}")
        return super()._handle_cmd(cmd)


if __name__ == "__main__":
    comp = SmokeComponent()
    print("[smoke] listening on", comp.settings.mq_addr_in)
    try:
        comp.run()
    except KeyboardInterrupt:
        print("\n[smoke] KeyboardInterrupt, shutting down")
