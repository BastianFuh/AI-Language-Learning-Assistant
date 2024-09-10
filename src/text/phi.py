"""Module for text processing using Phi-3.5-mini.
https://huggingface.co/microsoft/Phi-3.5-mini-instruct
"""

import torch
from transformers import pipeline

from core.processing import AbstractActionProcess


class PhiMiniTextProcessingModule(AbstractActionProcess):
    """Module for processing text using the chat model from Microsoft Phi-3.5-mini.
    See, https://huggingface.co/microsoft/Phi-3.5-mini-instruct
    """

    DEFAULT_MODEL_NAME = "microsoft/Phi-3.5-mini-instruct"

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

        self.message_log = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        super().__init__(manager, "llm", output_queues=output_queues)

    def run(self, *args, **kwargs):
        self.model = pipeline(
            "text-generation",
            model=self.model_name,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device=self.get_process_device(),
        )
        super().run(*args, **kwargs)

    def process(self, data_in):
        self.message_log.append({"role": "user", "content": data_in["data"]})

        # Process the current message log
        output = self.model(self.message_log, max_new_tokens=500)

        # Update the current message log
        # the output contains the input plus the new additions of the model
        self.message_log = output[0]["generated_text"]

        self.logger.debug(f"Current message log post processing : {self.message_log}")

        # Retrive the last added text element
        return self.create_output_data(
            output[0]["generated_text"][-1]["content"].strip()
        )

    def clean_up(self):
        del self.model
