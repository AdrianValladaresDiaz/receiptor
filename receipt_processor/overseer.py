from multiprocessing import Queue, Process
from os import cpu_count
from PIL import Image
from uuid import uuid4
from logging import Logger
from receipt_processor.counter import Counter
from receipt_processor.ocr_worker import OCRWorker

class Request:
    def __init__(self, img:Image) -> None:
        self.id = uuid4()
        self.img = img


class Overseer:
    """Manages worker count
    
    Will spawn new workers and set them to work as long as there is
    work to do and there are less workers than available capacity.

    Attributes
    ----------
    capacity : int | None
        number of processes to spawn. If None os.cpu_count() is used
        instead.
    inputQ : multiprocessing.Queue
        queue with paths to files to be processed
    outputQ : multiprocessing.Queue
        queue with the info extracted from the queue
    logger:

    Methods
    -------
    info(additional=""):
        Prints the person's name and age.
    """
    def __init__(self, inputQ:Queue, outputQ:Queue, logger:Logger) -> None:
        self.inputQ = inputQ
        self.outputQ = outputQ
        self.capacity = self._discern_capacity()
        self.process_counter = Counter()
        self.logger = logger

    def _discern_capacity(self):
        # return capacity or cpu_count() or 1
        return 2
        
    def spawn_process(self,txt):
        self.logger.debug(txt)
        # no need for worker? maybe define function here
        worker = OCRWorker(self.inputQ, self.outputQ, "nada", None, self.process_counter, self.logger)
        process = Process(target=worker.work, name=f'PROCESS {self.process_counter.value()}')
        process.start()
        

    def push_request(self, req:str):
        """Adds an image path to the queue
        
        If the Queue size grows over threshold, more workers
        will be spawned. Adding the first item starts the engine?
        We do want put to be fast so bear that in mind.
        """
        inQ = self.inputQ
        outQ = self.outputQ

        self.logger.debug("adding item to input Q")
        inQ.put(req)
        if(inQ.qsize() > 0 and self.process_counter.value() == 0):
            self.logger.debug("No workers active, spawning...")
            self.spawn_process("first")
            
        elif(inQ.qsize()/ self.process_counter.value() < 0.1  and self.process_counter < self.capacity):
            self.logger.debug("workers active but too much work, spawning...")
            self.spawn_process("second")

        self.logger.debug(f'current worker count is {self.process_counter.value()}')

        





