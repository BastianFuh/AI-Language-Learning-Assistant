"""This modules uses google text to speech API to convert the given text to speech."""

from io import BytesIO
from pygame import mixer
from gtts import gTTS
import time

from core.processing import AbstractActionProcess


class gTTSModule(AbstractActionProcess):
    def __init__(self, manager, output_queues=(), language="en", accent="com.au"):
        """This modules uses google text to speech API to convert the given text to speech.

        Args:
            language (str, optional): Language of the TTS. Defaults to "en".
            accent (str, optional): Accent of the speaker. This is determined by the top level domain. Defaults to "com.au".
        """
        self.language = language
        self.accent = accent
        super().__init__(manager, output_queues=output_queues)

    def process(self, data_in):
        #

        # self.logger.info(f"Received Data {data_in}")

        audio = gTTS(data_in["data"])

        mp3_fp = BytesIO()
        audio.write_to_fp(mp3_fp)

        mp3_fp.seek(0)

        mixer.music.load(mp3_fp)

        mixer.music.play()

        # Wait until file is played
        while mixer.music.get_busy():
            time.sleep(0.1)

        return None

    def run(self, *args, **kwargs):
        # Initialiaze the audio mixer

        super().run(*args, **kwargs)

    def clean_up(self):
        mixer.quit()
        return super().clean_up()
