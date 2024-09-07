"""Module for OpenAi TTS"""

import os
import random
import numpy as np
from openai import OpenAI
import scipy
import scipy.signal
import sounddevice as sd

from core.processing import AbstractActionProcess


class OpenAITTS(AbstractActionProcess):
    """Module to convert text to speech using OpenAi TTS.
    See https://platform.openai.com/docs/guides/text-to-speech
    """

    def __init__(self, manager, output_queues=(), audio_output_device=None):
        """This modules uses Open Ai text to speech API to convert the given text to speech."""
        self.client = None

        self.audio_output_device = audio_output_device
        self.output_sampling_rate = None

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

        resample_scale = self.output_sampling_rate / 24e3

        # Resample audio to sample rate of the audio output device
        resampled_audio = scipy.signal.resample_poly(
            normalized_audio, resample_scale * 4, 4
        )

        # Play audio
        sd.play(resampled_audio)

        sd.wait()

        return None

    def run(self, *args, **kwargs):
        self.client = OpenAI()
        self.audio_output_device = os.environ.get("DEFAULT_AUDIODEVICE_OUTPUT", None)
        sd.default.device = self.audio_output_device
        print(sd.query_devices(self.audio_output_device))
        self.output_sampling_rate = sd.query_devices(self.audio_output_device)[
            "default_samplerate"
        ]
        super().run(*args, **kwargs)

    def clean_up(self):
        self.client.close()
        return super().clean_up()
