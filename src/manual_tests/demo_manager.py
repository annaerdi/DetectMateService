"""
Tiny demo showing Manager <---> client interaction.
Run it with:
uv run src/manual_tests/demo_manager.py
"""
from time import sleep
import pynng

from corecomponent.core_component import CoreComponent


def main() -> None:
    # Create the component; Manager starts automatically.
    comp = CoreComponent()

    # Use the context-manager sugar so log handlers close cleanly.
    with comp:
        # Simple REQ client talking to the component's REP socket
        req = pynng.Req0()
        req.dial(comp.settings.mq_addr_in)  # same address Manager listens on

        for cmd in ("ping", "version?", "stop"):
            print(f">>> {cmd}")
            req.send(cmd.encode())
            reply = req.recv().decode()
            print(f"<<< {reply}")

            sleep(1)

        # After "stop" the Manager thread will shut down;
        # the surrounding "with" block triggers CoreComponent.__exit__

    print("Demo finished.")


if __name__ == "__main__":
    main()
