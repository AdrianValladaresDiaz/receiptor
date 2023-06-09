import re
from multiprocessing import Queue, Value
from logging import Logger
import torch

from transformers import DonutProcessor, VisionEncoderDecoderModel


def runDONUT(inQ: Queue, outQ: Queue, logger: Logger, process_counter: Value):
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
