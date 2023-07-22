from PIL import Image
import pytesseract
import receipt_processor.file_gatherer as RP
from multiprocessing import Queue, Event
import logging
from receipt_processor.setup_loggers import setup_loggers
import server.Server as OCRServer


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
    images1 = RP.gather_files("./static")
    images2 = RP.gather_files("./static")

    logger.debug("GENERATOR STARTING")
    while images1.qsize() > 0:
        try:
            imgpath = images1.get()
            with Image.open(imgpath) as img:
                img2 = img.copy() # Copying the image because  otherwise
                logger.debug(f'pushing {img2}')
                outQ.put(img)
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


def OCR_TEST():
    import multiprocessing
    from receipt_processor import ocr_processing
    import time

    # Setup
    [logger, listener] = setup_loggers()
    [serverLogger, serverLoggerListener] = setup_loggers()
    
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

def DONUT_TEST():
    import torch
    import re
    from transformers import DonutProcessor, VisionEncoderDecoderModel

    processor = DonutProcessor.from_pretrained(
            "naver-clova-ix/donut-base-finetuned-cord-v2", use_fast= False)
    print("PROCESSOR DONE")
    model = VisionEncoderDecoderModel.from_pretrained(
            "naver-clova-ix/donut-base-finetuned-cord-v2")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
        
    tensor_type = "pt"

    images= RP.gather_files("./static")
    imgpath = images.get()
    print("FILES RDY")
    with Image.open(imgpath) as img:
        print(img.info)
        task_prompt = "<s_cord-v2>"
        decoder_input_ids = processor.tokenizer(
            task_prompt,
            add_special_tokens=False,
            return_tensors=tensor_type).input_ids
        pixel_values = processor(img, return_tensors=tensor_type).pixel_values
        outputs = model.generate(
        pixel_values.to(device),
            decoder_input_ids=decoder_input_ids.to(device),
            max_length=model.decoder.config.max_position_embeddings,
            early_stopping=True,
            pad_token_id=processor.tokenizer.pad_token_id,
            eos_token_id=processor.tokenizer.eos_token_id,
            use_cache=True,
            num_beams=1,
            bad_words_ids=[[processor.tokenizer.unk_token_id]],
            return_dict_in_generate=True,
        )
        sequence = processor.batch_decode(outputs.sequences)[0]
        sequence = sequence.replace(processor.tokenizer.eos_token, "").replace(processor.tokenizer.pad_token, "")
        sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()  # remove first task start token
        imageInfo = (processor.token2json(sequence))
        print(imageInfo)
    
def BLEH():
    import providers.queue_provider as Queues
    print(Queues.Queues)

def SERVER_TEST():
    server = OCRServer.Server().start()

"""Trace - Only when I would be "tracing" the code and trying to find one part of a function specifically.
Debug - Information that is diagnostically helpful to people more than just developers (IT, sysadmins, etc.).
Info - Generally useful information to log (service start/stop, configuration assumptions, etc). Info I want to always have available but usually don't care about under normal circumstances. This is my out-of-the-box config level.
Warn - Anything that can potentially cause application oddities, but for which I am automatically recovering. (Such as switching from a primary to backup server, retrying an operation, missing secondary data, etc.)
Error - Any error which is fatal to the operation, but not the service or application (can't open a required file, missing data, etc.). These errors will force user (administrator, or direct user) intervention. These are usually reserved (in my apps) for incorrect connection strings, missing services, etc.
Fatal - Any error that is forcing a shutdown of the service or application to prevent data loss (or further data loss). I reserve these only for the most heinous errors and situations where there is guaranteed to have been data corruption or loss.
"""
if __name__ == "__main__":
    # OCR_TEST()
    # SERVER_TEST()
    DONUT_TEST()