import sys
import time
import pynng

USAGE = "Usage: python engine_client.py <message>"


def talk(msg: bytes):
    with pynng.Pair0(dial="ipc:///tmp/smoke_engine.ipc") as sock:
        # wait briefly for socket handshake
        time.sleep(0.1)
        sock.send(msg)
        try:
            resp = sock.recv()
            print(f"-> {msg!r}  <- {resp!r}")
        except pynng.NNGException:
            print("-> no response")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(USAGE)
        sys.exit(1)
    talk(sys.argv[1].encode())
