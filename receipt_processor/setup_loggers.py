from multiprocessing import Queue
import logging
from logging.handlers import QueueListener, QueueHandler


def setup_loggers()->tuple[logging.Logger, QueueListener]:
    """Sets upd this service's logging
    
    Returns a tuple with a reference to the root logger and a queue listener.
    Call listener.start() to begin listening to the log queue, and listener.stop()
    when done listening.
    The root logger is set to pass messages to this queue, so it can be used by 
    all processes. 
    """
    # Define a queue and a queue handler, that will send logs to that queue.
    logs_queue = Queue(-1)
    queue_handler = QueueHandler(logs_queue)

    # Add handler to logger. This passes the generated logs to that queue.
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(queue_handler)

    # Define a stream handler. This will send the logs it receives to a stream.
    # If no specific stream is passed to the handler logs are sent to sys.stderr
    # We use this to display the logs in our console
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(processName)s - %(levelname)s - %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)

    # Define a queue listener. This one will listen to the logs queue that receives
    # logs from the logger, and pass those to the specified handlers. We use this to
    # to pass logs from that queue to our console
    queue_listener = QueueListener(logs_queue, stream_handler, respect_handler_level=True)

    return (logger, queue_listener)