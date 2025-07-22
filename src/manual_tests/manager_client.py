import sys
import pynng

USAGE = "Usage: python client.py <ping|start|pause|resume|stop>"


def send(cmd: str):
    with pynng.Req0(dial="ipc:///tmp/smoke_cmd.ipc") as sock:
        sock.send(cmd.encode())
        reply = sock.recv().decode()
        print(f">>> {cmd!r} -> {reply!r}")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("ping", "start", "pause", "resume", "stop"):
        print(USAGE)
        sys.exit(1)
    send(sys.argv[1])
