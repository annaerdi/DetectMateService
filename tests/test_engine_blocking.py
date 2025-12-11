import pytest
import time
import pynng
from service.settings import ServiceSettings
from service.features.engine import Engine
from library.processor import BaseProcessor


class SimpleProcessor(BaseProcessor):
    def __call__(self, raw_message: bytes) -> bytes:
        return b"PROCESSED: " + raw_message.upper()


@pytest.fixture
def temp_ipc_paths(tmp_path):
    return {
        'engine': f"ipc://{tmp_path}/engine.ipc",
        'out1': f"ipc://{tmp_path}/out1.ipc",
        'manager': f"ipc://{tmp_path}/manager.ipc",
    }


class TestEngineBlocking:
    def test_engine_stalls_until_output_online(self, temp_ipc_paths):
        """Verify that the engine stalls (blocks) when the output socket is not
        ready, and resumes once it becomes ready."""
        settings = ServiceSettings(
            engine_addr=temp_ipc_paths['engine'],
            manager_addr=temp_ipc_paths['manager'],
            out_addr=[temp_ipc_paths['out1']],
            engine_autostart=False,
            out_dial_timeout=1000,  # Ensure dial doesn't hang forever if something is wrong
            out_buffer_size=2,  # Set very small buffer
        )

        processor = SimpleProcessor()
        engine = Engine(settings=settings, processor=processor)

        # Start engine (output is offline)
        engine.start()

        sender = pynng.Pair0()
        sender.dial(temp_ipc_paths['engine'])

        try:
            # 1. Send a message. Since out1 is offline, the engine should try to send and BLOCK.
            # We can't easily check "is it blocked" directly, but we can check that it hasn't
            # processed a subsequent message or that the message
            # hasn't disappeared if we were using a different protocol.
            # But, we want to ensure that NO message is dropped
            sender.send(b"msg1")

            # Wait a bit. In the OLD behavior (drop), this would just be dropped and engine continues.
            # In the NEW behavior (block), the engine thread should be stuck in `send()`.
            time.sleep(0.5)

            # 2. Bring up the output.
            receiver = pynng.Pair0()
            receiver.listen(temp_ipc_paths['out1'])
            receiver.recv_timeout = 2000

            # 3. The engine should now unblock and deliver the message.
            result = receiver.recv()
            assert result == b"PROCESSED: MSG1"

            # 4. Verify engine is still alive and can process more
            sender.send(b"msg2")
            result2 = receiver.recv()
            assert result2 == b"PROCESSED: MSG2"

        finally:
            engine.stop()
            sender.close()
            if 'receiver' in locals():
                receiver.close()
