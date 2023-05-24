from multiprocessing import Queue, Value
import pytesseract
from logging import Logger


def processOCR(inQ: Queue, outQ: Queue, logger: Logger, process_counter: Value):
    """ Gets Image from the input Queue and applies OCR to it.
        Images are removed from memory after reading.
    """
    logger.debug("PROCESS STARTED")
    try:
        while inQ.qsize() > 0:
            img = inQ.get()

            text = pytesseract.image_to_string(img, lang='eng')
            outQ.put(text)

        logger.debug('PROCESS DONE. EXITING...')
        with process_counter.get_lock():
            process_counter.value -= 1

    except Exception as e:
        # Decrement the process count when this process terminates
        logger.error(f'PROCESS EXIT DUE TO ERROR: {str(e.with_traceback())}')
        with process_counter.get_lock():
            process_counter.value -= 1

