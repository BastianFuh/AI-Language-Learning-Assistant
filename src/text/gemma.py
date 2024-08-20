"""Module for text processing using Gemma 2.
https://huggingface.co/collections/google/gemma-2-release-667d6600fd5220e7b967f315
"""

import torch
from transformers import pipeline

from core.processing import AbstractActionProcess


class GemmaTextProcessingModule(AbstractActionProcess):
    """Module for processing text using the chat model from Google Gemma 2.
    See, https://huggingface.co/collections/google/gemma-2-release-667d6600fd5220e7b967f315
    """

    DEFAULT_MODEL_NAME = "google/gemma-2-2b-it"

    SYSTEM_PROMPT = """
        You are now a translator. 
        You will get a text and translate it.
        You will be translating the text from english to german.
        ONLY translate the text of the most recent user message.
        DO NOT return anything other than the translated text.
    """

    def __init__(self, manager, output_queues=(), model_name=DEFAULT_MODEL_NAME):
        self.model = None
        self.model_name = model_name

        # System role is not supported by gemma
        self.message_log = [{"role": "user", "content": self.SYSTEM_PROMPT}]

        super().__init__(manager, output_queues=output_queues)

    def run(self, *args, **kwargs):
        self.model = pipeline(
            "text-generation",
            model=self.model_name,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device=self.get_process_device(),
        )
        super().run(*args, **kwargs)

    def process(self, data_in):
        # Update current message history
        if len(self.message_log) == 1:
            # If first message just add the new data to the current prompt.
            # This needs to be done because the order needs to be user/assistant/user/...
            self.message_log[0]["content"] = (
                self.message_log[0]["content"] + " " + data_in
            )
        else:
            self.message_log.append({"role": "user", "content": data_in})

        # Process the current message log
        output = self.model(self.message_log, max_new_tokens=500)

        # Update the current message log
        # the output contains the input plus the new additions of the model
        self.message_log = output[0]["generated_text"]

        self.logger.debug(f"Current message log post processing : {self.message_log}")

        # Retrive the last added text element
        return output[0]["generated_text"][-1]["content"].strip()

    def clean_up(self):
        del self.model
