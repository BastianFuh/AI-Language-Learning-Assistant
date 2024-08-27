"""Module for the Speech Recognition using whisper. See https://openai.com/index/whisper/ for more."""

import time
import whisper
import scipy

from core.processing import AbstractActionProcess


class WhisperSpeechRecognitionModule(AbstractActionProcess):
    """Speech recognition using whisper model from openai."""

    # Duration of one segment. This should be longer than the processing
    SEGMENT_DURATION = 10  # seconds

    def __init__(self, manager, input_fs, output_queues=(), target_language="en"):
        self._target_fs = 16000
        self.input_fs = input_fs
        self.model = None

        self.last_text = ""

        self.target_language = target_language

        super().__init__(manager, output_queues=output_queues)

    def run(self, *args, **kwargs):
        self.model = whisper.load_model("base", self.get_process_device())

        super().run(*args, **kwargs)

    def process(self, data_in):
        self.logger.debug("Started Processing")

        data_in.to(self.model.device)

        start_time = time.time()
        data = data_in
        data_conversion_time = time.time()

        # Calculate the duration based on sampling rate and length of data
        duration = int(len(data_in) / self.input_fs)

        # Resample audio to the correct input sampling rate
        resampled_audio = scipy.signal.resample(data, duration * self._target_fs)
        resampling_time = time.time()

        # Trim or pad the data to 30s
        pad_or_trim_audio = whisper.pad_or_trim(resampled_audio)
        pad_or_trim_time = time.time()

        # Calculate the mel spectrogram
        mel = whisper.log_mel_spectrogram(pad_or_trim_audio).to(self.model.device)
        mel_calc_time = time.time()

        options = whisper.DecodingOptions(
            # prompt=self.last_text,
            fp16=True
        )

        # Do the actual inteference
        result = whisper.decode(self.model, mel, options)
        end_time = time.time()

        # Debut time outputs
        self.logger.debug(f"Time conversion {data_conversion_time - start_time}")
        self.logger.debug(
            f"Resampling conversion {resampling_time - data_conversion_time}"
        )
        self.logger.debug(
            f"Pad or trim conversion {pad_or_trim_time - resampling_time}"
        )
        self.logger.debug(f"Mel calc conversion {mel_calc_time - pad_or_trim_time}")
        self.logger.debug(f"Decode conversion {end_time - mel_calc_time}")
        self.logger.debug(
            f"Detected language {result.language} in {end_time - start_time}"
        )
        self.logger.debug(f"Detected Text: {result.text}")

        if result.language is self.target_language:
            self.last_text = result.text
            return result.text
        else:
            return None

    def clean_up(self):
        del self.model
