"""Module for text processing using GPT-4o mini.
https://huggingface.co/collections/google/gemma-2-release-667d6600fd5220e7b967f315
"""

from openai import OpenAI
from core.processing import AbstractActionProcess


class GPT4oMiniTextProcessingModule(AbstractActionProcess):
    """Module for processing text using the chat model from Microsoft Phi-3.5-mini.
    See, https://huggingface.co/microsoft/Phi-3.5-mini-instruct
    """

    DEFAULT_MODEL_NAME = "gpt-4o-mini"

    SYSTEM_PROMPT = """ Keep yourself short.
    """

    def __init__(self, manager, output_queues=(), model_name=DEFAULT_MODEL_NAME):
        self.client = None
        self.model = model_name

        self.message_log = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        super().__init__(manager, "llm", output_queues=output_queues)

    def run(self, *args, **kwargs):
        self.client = OpenAI()

        super().run(*args, **kwargs)

    def process(self, data_in):
        self.message_log.append({"role": "user", "content": data_in["data"]})

        output = self.client.chat.completions.create(
            model=self.model, messages=self.message_log
        )

        return self.create_output_data(output.choices[0].message.content)

    def clean_up(self):
        del self.client
