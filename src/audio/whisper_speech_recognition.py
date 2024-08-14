""" Module for the Speech Recognition using whisper. See https://openai.com/index/whisper/ for more.
"""
import ctypes
import whisper
import scipy
import numpy as np

from core.processing import AbstractActionProcess


class WhisperSpeechRecognitionModule(AbstractActionProcess):
    """ Speech recognition using whisper model from openai.
    """

    model = None
    duration = 30
    _target_fs = 16000

    def __init__(self, duration=30, data_buffer_size=1024, in_data=None, e_din_avail=None):
        self.__class__.duration = duration

        super().__init__(
            target=self.run,
            buffer_type=ctypes.c_char,
            data_buffer_size=data_buffer_size,
            in_data=in_data,
            e_din_avail=e_din_avail)

    @classmethod
    def _init(cls, *args, **kwargs):
        cls.model = whisper.load_model("base", "cuda")
        cls._run(*args, **kwargs)

    @classmethod
    # pylint: disable=unused-argument
    def process(cls, data_in, data_out):
        """ This method should process the available data in data_in and put the result into
        data out. It has to be overwritten by any child class.

        Important is also that this function is called in the main processing loop. Therefore
        is should only process the data once it is available and should not have a loop which
        waits for more data. 
        """

        data = np.array(data_in, dtype=np.float32)
        resampled_audio = scipy.signal.resample(
            data, cls.duration * cls._target_fs)
        pad_or_trim_audio = whisper.pad_or_trim(resampled_audio)

        mel = whisper.log_mel_spectrogram(
            pad_or_trim_audio).to(cls.model.device)

        _, probs = cls.model.detect_language(mel)
        cls.logger().info(f"Detected language {max(probs, key=probs.get)}")

        options = whisper.DecodingOptions()
        result = whisper.decode(cls.model, mel, options)
        cls.logger().info(f"Detected Text: {result.text}")
        data_out = result.text

    @classmethod
    def clean_up(cls):
        pass
