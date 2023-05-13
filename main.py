from PIL import Image
import pytesseract
import receipt_processor.file_gatherer as RP
from receipt_processor.overseer import Overseer
from receipt_processor.ocr_worker import OCRWorker
from multiprocessing import Queue, Event
import logging
from receipt_processor.setup_loggers import setup_loggers


def ocr_test():

    with Image.open("./static/receipt1.jpg") as img:
        # , config='--psm 6', tessdata_dir='path/to/model/files')
        text = pytesseract.image_to_string(img, lang='eng')

        print(img.info)
        print(text)


def test():
    print("starting test")
    images = RP.gather_files("./static")
    result = Queue()
    ev = Event()
    worker = OCRWorker(inQ=images, outQ=result, target="./static", event=ev)
    worker.work()
    while not result.empty():
        print(result.get())


def q_printer(q: Queue, logger: logging.Logger):
    while not q.empty():
        logger.debug(q.get())


def random_generator(outQ: Queue, logger: logging.Logger):
    from random import random
    import time

    logger.debug("GENERATOR STARTING")
    count = 0
    while count < 30:
        count += 1
        outQ.put(random())
    logger.debug("GENERATOR TAKING A BREAK")

    time.sleep(3)
    logger.debug("GENERATOR RESTARTING")

    count = 0
    while count < 30:
        count += 1
        outQ.put(random())
    logger.debug("GENERATOR DONE")


def image_generator(outQ: Queue, logger: logging.Logger):
    """Not actually a generator"""
    import time
    import copy
    images1 = RP.gather_files("./static")
    images2 = RP.gather_files("./static")

    logger.debug("GENERATOR STARTING")
    while images1.qsize() > 0:
        try:
            imgpath = images1.get()
            with Image.open(imgpath) as img:
                img2 = img.copy()
                logger.debug(f'pushing {img2}')
                outQ.put(img2)
        except Exception as e:
            logger.debug(str(Exception.with_traceback(e)))
            break
    logger.debug("GENERATOR TAKING A BREAK")

    time.sleep(3)
    logger.debug("GENERATOR RESTARTING")

    while images2.qsize() > 0:
        try:
            imgpath = images2.get()
            with Image.open(imgpath) as img:
                img2 = img.copy()
                logger.debug(f'pushing {img2}')
                outQ.put(img2)
        except Exception as e:
            logger.debug(str(Exception.with_traceback(e)))
            break
    logger.debug("GENERATOR DONE")


def gpt_test():
    import multiprocessing
    from receipt_processor import ocr_processing
    import time

    # Setup
    [logger, listener] = setup_loggers()
    listener.start()
    try:
        inQ = Queue(-1)
        outQ = Queue(-1)
        generator_process = multiprocessing.Process(
            target=image_generator, args=(inQ, logger))
        generator_process.start()

        # Use a multiprocessing.Value object to keep track of the number of running processes
        process_count = multiprocessing.Value('i', 0)


    except Exception as e:
            logger.debug(str(Exception.with_traceback(e)))
    time.sleep(1)
    logger.debug("ABOUT TO ENTER PROCESSOR LOOP")
    while True:
        if process_count.value < 2 and inQ.qsize() > 0:
            input_process = multiprocessing.Process(
                target=ocr_processing.processOCR, args=(inQ, outQ, logger, process_count))
            input_process.start()
            # Increment the process count
            with process_count.get_lock():
                process_count.value += 1
        
        if inQ.qsize() < 1:
            logger.debug("EXITING WOOO")
            break

        time.sleep(0.2)
    logger.info(f'INFOOOO: {outQ.get()}')
    generator_process.join()
    listener.stop()


"""Trace - Only when I would be "tracing" the code and trying to find one part of a function specifically.
Debug - Information that is diagnostically helpful to people more than just developers (IT, sysadmins, etc.).
Info - Generally useful information to log (service start/stop, configuration assumptions, etc). Info I want to always have available but usually don't care about under normal circumstances. This is my out-of-the-box config level.
Warn - Anything that can potentially cause application oddities, but for which I am automatically recovering. (Such as switching from a primary to backup server, retrying an operation, missing secondary data, etc.)
Error - Any error which is fatal to the operation, but not the service or application (can't open a required file, missing data, etc.). These errors will force user (administrator, or direct user) intervention. These are usually reserved (in my apps) for incorrect connection strings, missing services, etc.
Fatal - Any error that is forcing a shutdown of the service or application to prevent data loss (or further data loss). I reserve these only for the most heinous errors and situations where there is guaranteed to have been data corruption or loss.
"""
if __name__ == "__main__":
    gpt_test()
