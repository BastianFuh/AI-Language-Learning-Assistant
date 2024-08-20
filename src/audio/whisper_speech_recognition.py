"""Module for the Speech Recognition using whisper. See https://openai.com/index/whisper/ for more."""

import time
import whisper
import scipy

from core.processing import AbstractActionProcess


class WhisperSpeechRecognitionModule(AbstractActionProcess):
    """Speech recognition using whisper model from openai."""

    DEFAULT_DURATION = 30

    def __init__(self, manager, output_queues=(), duration=DEFAULT_DURATION):
        self.__class__.duration = duration

        self.duration = 30
        self._target_fs = 16000

        self.model = None

        self.last_text = ""

        super().__init__(manager, output_queues=output_queues)

    def run(self, *args, **kwargs):
        self.model = whisper.load_model("base", self.get_process_device())

        super().run(*args, **kwargs)

    def process(self, data_in):
        self.logger.debug("Started Processing")

        data_in.to(self.model.device)

        start_time = time.time()
        data = data_in  # np.array(data_in, dtype=np.float32)
        data_conversion_time = time.time()

        resampled_audio = scipy.signal.resample(data, self.duration * self._target_fs)
        resampling_time = time.time()

        pad_or_trim_audio = whisper.pad_or_trim(resampled_audio)
        pad_or_trim_time = time.time()

        mel = whisper.log_mel_spectrogram(pad_or_trim_audio).to(self.model.device)
        mel_calc_time = time.time()

        options = whisper.DecodingOptions(
            # prompt=self.last_text,
            fp16=True
        )

        result = whisper.decode(self.model, mel, options)
        end_time = time.time()
        self.logger.debug(f"Time conversion {data_conversion_time - start_time}")
        self.logger.debug(
            f"Resampling conversion {resampling_time - data_conversion_time}"
        )
        self.logger.debug(
            f"Pad or trim conversion {pad_or_trim_time - resampling_time}"
        )
        self.logger.debug(f"Mel calc conversion {mel_calc_time - pad_or_trim_time}")
        self.logger.debug(f"Decode conversion {end_time - mel_calc_time}")
        self.logger.info(
            f"Detected language {result.language} in {end_time - start_time}"
        )
        self.logger.info(f"Detected Text: {result.text}")

        self.last_text = result.text
        return result.text

    def clean_up(self):
        del self.model
