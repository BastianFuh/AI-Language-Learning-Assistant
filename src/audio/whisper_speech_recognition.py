""" Module for the Speech Recognition using whisper. See https://openai.com/index/whisper/ for more.
"""
import ctypes
from multiprocessing.sharedctypes import Array
import whisper
import scipy
import numpy as np


from core.processing import AbstractActionProcess


class WhisperSpeechRecognitionModule(AbstractActionProcess):
    """ Speech recognition using whisper model from openai.
    """
    DEFAULT_DURATION = 30

    def __init__(self, duration=DEFAULT_DURATION, data_buffer_size=1, in_data=None, e_din_avail=None):
        self.__class__.duration = duration

        self.duration = 30
        self._target_fs = 16000

        self.model = None

        super().__init__(
            buffer_type=ctypes.c_wchar_p,
            data_buffer_size=data_buffer_size,
            in_data=in_data,
            e_din_avail=e_din_avail)

    def run(self, *args, **kwargs):
        self.model = whisper.load_model("base", "cuda")
        super().run(*args, **kwargs)

    # pylint: disable=unused-argument
    def process(self, data_in, data_out):
        """ This method should process the available data in data_in and put the result into
        data out. It has to be overwritten by any child class.

        Important is also that this function is called in the main processing loop. Therefore
        is should only process the data once it is available and should not have a loop which
        waits for more data. 
        """
        self.logger().debug("Started Processing")
        
        data = np.array(data_in, dtype=np.float32)
        resampled_audio = scipy.signal.resample(
            data, self.duration * self._target_fs)
        pad_or_trim_audio = whisper.pad_or_trim(resampled_audio)

        mel = whisper.log_mel_spectrogram(
            pad_or_trim_audio).to(self.model.device)

        _, probs = self.model.detect_language(mel)
        self.logger().info(f"Detected language {max(probs, key=probs.get)}")

        options = whisper.DecodingOptions()
        result = whisper.decode(self.model, mel, options)
        self.logger().info(f"Detected Text: {result.text}")

        data_out[:] = [result.text]

    def clean_up(self):
        pass
