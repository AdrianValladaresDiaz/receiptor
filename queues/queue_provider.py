"""This module holds all necessary queues. Siince they are not variable at runtime
    we will just hardcode them here so they are easily accessible from the module
    like this: queue_provider.inputQueue
"""
import multiprocessing as MP
import PIL.Image as Image
import uuid

class IncomingTransaction:
    def __init__(self, image: Image.Image) -> None:
        self.id = uuid.uuid4()
        self.transaction_id = uuid.uuid4()
        self.image = image

class _CONFIG:
    MAX_Q_SIZE = -1

incoming_transaction_queue: MP.Queue[IncomingTransaction] = MP.Queue(_CONFIG.MAX_Q_SIZE)
