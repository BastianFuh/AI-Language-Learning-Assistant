"""Module for OpenAi TTS"""

import random
import numpy as np
from openai import OpenAI
import sounddevice as sd

from core.processing import AbstractActionProcess


class OpenAITTS(AbstractActionProcess):
    """Module to convert text to speech using OpenAi TTS.
    See https://platform.openai.com/docs/guides/text-to-speech
    """

    def __init__(self, manager, output_queues=()):
        """This modules uses Open Ai text to speech API to convert the given text to speech."""
        self.client = None

        # Model, options are "tts-1" and "tts-1-hd" for higher quality and cost
        self.model = "tts-1"
        # All voice options
        self.voices = ["alloy", "echo", "fable", "nova", "onyx", "shimmer"]
        # Response format of the audio
        self.response_format = "pcm"
        super().__init__(manager, output_queues=output_queues)

    def process(self, data_in):
        # Use
        response = self.client.audio.speech.create(
            model=self.model,
            voice=self.voices[random.randint(0, len(self.voices) - 1)],
            response_format=self.response_format,
            input=data_in["data"],
        )

        # Parse the received data. Datatype is signed 16bit 24kHz
        raw_audio = np.frombuffer(response.content, dtype=np.int16)

        # Convert the data to a float representation which is need to play it
        converted_audio = raw_audio.astype(np.float32)

        # Adjust the values to bring them into a range of -1 to 1
        normalized_audio = converted_audio / 2**15

        # Play audio
        sd.play(normalized_audio, samplerate=int(24e3))

        sd.wait()

        return None

    def run(self, *args, **kwargs):
        self.client = OpenAI()
        super().run(*args, **kwargs)

    def clean_up(self):
        self.client.close()
        return super().clean_up()
