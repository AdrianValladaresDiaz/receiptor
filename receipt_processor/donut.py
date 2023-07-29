import re
from multiprocessing import Queue, Value
from logging import Logger
import torch
from typing import  Any

from loggers import logger
from transformers import DonutProcessor, VisionEncoderDecoderModel # type: ignore

multiprocessingValueAlias: Any

# Define model, processors, etc to be reused
model_name = "naver-clova-ix/donut-base-finetuned-cord-v2"
donut_processor = DonutProcessor.from_pretrained(model_name)
model = VisionEncoderDecoderModel.from_pretrained(model_name)
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
tensor_type = "pt" # choosing pytorch 

"""
Decoder_input_ids will be a tensor (PyTorch tensor in this case) containing the token IDs of the task prompt "<s_cord-v2>" 
after it has been processed by the tokenizer. These decoder_input_ids will later serve as the initial input to the decoder 
(text generator) part of the image parsing model during the generation process.
"""
task_prompt = "<s_cord-v2>" 
decoder_input_ids = donut_processor.tokenizer(
    task_prompt,
    add_special_tokens=False,
    return_tensors=tensor_type).input_ids


def apply_donut_to_image(image):
    """Gets a PIL Image and runs it though donut. Returns whatever is
    extracted from said image. The prompt is defaulted, modify the module
    if you want different prompts"""
    pixel_values = donut_processor(image, return_tensors=tensor_type).pixel_values

    outputs = model.generate(
            pixel_values.to(device),
                decoder_input_ids=decoder_input_ids.to(device),
                max_length=model.decoder.config.max_position_embeddings,
                early_stopping=True,
                pad_token_id=donut_processor.tokenizer.pad_token_id,
                eos_token_id=donut_processor.tokenizer.eos_token_id,
                use_cache=True,
                num_beams=1,
                bad_words_ids=[[donut_processor.tokenizer.unk_token_id]],
                return_dict_in_generate=True,
            )

    sequence = donut_processor.batch_decode(outputs.sequences)[0]
    sequence = sequence.replace(donut_processor.tokenizer.eos_token, "").replace(donut_processor.tokenizer.pad_token, "")
    sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()  # remove first task start token
    imageInfo = (donut_processor.token2json(sequence))
    logger.debug(imageInfo)
    return imageInfo

def runDONUT(inQ: Queue, outQ: Queue, logger: Logger, process_counter: multiprocessingValueAlias):
    """Gets image from the input Queue and applies the DONUT
        model to it. Image is removed from memory after reading
    """
    logger.debug("PROCESS STARTED")
    try:
        processor = DonutProcessor.from_pretrained(
            "naver-clova-ix/donut-base-finetuned-cord-v2")
        model = VisionEncoderDecoderModel.from_pretrained(
            "naver-clova-ix/donut-base-finetuned-cord-v2")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)
        
        tensor_type = "pt"


        while inQ.qsize() > 0:
            img = inQ.get()
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
            logger.debug(imageInfo)
            outQ.put(imageInfo)

        logger.debug('PROCESS DONE. EXITING...')
        with process_counter.get_lock():
            process_counter.value -= 1

    except Exception as e:
        # Decrement the process count when this process terminates
        logger.error(f'PROCESS EXIT DUE TO ERROR: {str(e.with_traceback())}')
        with process_counter.get_lock():
            process_counter.value -= 1
