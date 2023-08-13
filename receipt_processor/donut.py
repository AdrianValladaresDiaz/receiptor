import re
from multiprocessing import Queue, Value
from loggers import logger
import torch
from typing import  Any
import time
from loggers import logger
from transformers import DonutProcessor, VisionEncoderDecoderModel # type: ignore

multiprocessingValueAlias: Any



class Donut:
    def __init__(self) -> None:
        model_name = "naver-clova-ix/donut-base-finetuned-cord-v2"
        self.donut_processor = DonutProcessor.from_pretrained(model_name, use_fast= False)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.tensor_type = "pt" # choosing pytorch 

        """
        Decoder_input_ids will be a tensor (PyTorch tensor in this case) containing the token IDs of the task prompt "<s_cord-v2>" 
        after it has been processed by the tokenizer. These decoder_input_ids will later serve as the initial input to the decoder 
        (text generator) part of the image parsing model during the generation process.
        """
        task_prompt = "<s_cord-v2>" 
        self.decoder_input_ids = self.donut_processor.tokenizer(
            task_prompt,
            add_special_tokens=False,
            return_tensors=self.tensor_type).input_ids


    def parse_image(self, image):
        """Gets a PIL Image and runs it though donut. Returns whatever is
        extracted from said image. The prompt is defaulted, modify the module
        if you want different prompts"""
        
        logger.debug("parse called")
        pixel_values = self.donut_processor(image, return_tensors=self.tensor_type).pixel_values
        logger.debug("got pixeñ values")
        
        outputs = self.model.generate(
                pixel_values.to(self.device),
                    decoder_input_ids=self.decoder_input_ids.to(self.device),
                    max_length=self.model.decoder.config.max_position_embeddings,
                    early_stopping=True,
                    pad_token_id=self.donut_processor.tokenizer.pad_token_id,
                    eos_token_id=self.donut_processor.tokenizer.eos_token_id,
                    use_cache=True,
                    num_beams=1,
                    bad_words_ids=[[self.donut_processor.tokenizer.unk_token_id]],
                    return_dict_in_generate=True,
                )
        logger.debug("got outputs")
        sequence = self.donut_processor.batch_decode(outputs.sequences)[0]
        sequence = sequence.replace(self.donut_processor.tokenizer.eos_token, "").replace(self.donut_processor.tokenizer.pad_token, "")
        sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()  # remove first task start token
        imageInfo = (self.donut_processor.token2json(sequence))
        logger.debug("finished parsing")
        logger.debug(imageInfo)
        return imageInfo



def runDONUT(inQ: Queue, outQ: Queue, process_counter: Any):
    """Gets image from the input Queue and applies the DONUT
        model to it. Image is removed from memory after reading
    """
    logger.debug("DONUT PROCESS STARTED")
    try:
        donut = Donut()
        # while inQ.qsize() > 0:
        while True:
            logger.debug("WAITING...")
            time.sleep(1)
            if inQ.qsize()>0:
                logger.debug("ABOUT TO FETCH IMAGE")
                receipt_processing_request = inQ.get()
                logger.debug(f"got request {receipt_processing_request.id}")
                img_info = donut.parse_image(receipt_processing_request.image)

                logger.debug(img_info)
                outQ.put(img_info)

        # teardown of the process
        logger.debug('PROCESS DONE. EXITING...')
        with process_counter.get_lock():
            process_counter.value -= 1

    except Exception as e:
        # Decrement the process count when this process terminates
        logger.error(f'PROCESS EXIT DUE TO ERROR: {str(e)}')
        with process_counter.get_lock():
            process_counter.value -= 1
