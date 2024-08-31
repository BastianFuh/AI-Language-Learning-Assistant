"""Module to convert text to speech using xTTS v2."""

import sounddevice as sd
from TTS.api import TTS

from core.processing import AbstractActionProcess


import random


class xTTSV2Module(AbstractActionProcess):
    """Module to convert text to speech using xTTS v2.
    See https://huggingface.co/coqui/XTTS-v2.

    Args:
        AbstractActionProcess (_type_): _description_
    """

    def __init__(self, manager, output_queues=(), language="en"):
        """This modules uses google text to speech API to convert the given text to speech.

        Args:
            language (str, optional): Language of the TTS. Defaults to "en".
        """
        self.language = language

        self.module = None
        self.speakers = None

        super().__init__(manager, output_queues=output_queues)

    def process(self, data_in):
        audio = self.module.tts(
            data_in["data"],
            speaker=self.module.speakers[
                random.randint(0, len(self.module.speakers) - 1)
            ],
            language=data_in["language"],
            speed=2,
        )

        sd.play(audio, samplerate=int(24e3))

        sd.wait()

        return None

    def run(self, *args, **kwargs):
        self.module = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(
            self.get_process_device()
        )
        self.speakers = self.module.speakers[29]

        super().run(*args, **kwargs)

    def clean_up(self):
        del self.module
        return super().clean_up()
