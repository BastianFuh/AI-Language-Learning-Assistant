"""Module for the Speech Recognition using whisper. See https://openai.com/index/whisper/ for more."""

import time
import whisper
import scipy

from core.processing import AbstractActionProcess


class WhisperSpeechRecognitionModule(AbstractActionProcess):
    """Speech recognition using whisper model from openai."""

    # Duration of one segment. This should be longer than the processing
    SEGMENT_DURATION = 30  # seconds

    def __init__(
        self, manager, input_fs, output_queues=(), target_languages=("en", "de", "ja")
    ):
        self._target_fs = 16000
        self.input_fs = input_fs
        self.model = None

        self.target_languages = target_languages

        super().__init__(manager, "stt", output_queues=output_queues)

    def run(self, *args, **kwargs):
        self.model = whisper.load_model("base", self.get_process_device())

        super().run(*args, **kwargs)

    def process(self, data_in):
        self.logger.debug("Started Audio Processing")

        start_time = time.time()
        data = data_in["data"]

        data.to(self.get_process_device())

        # Calculate the duration based on sampling rate and length of data
        duration = int(len(data) / self.input_fs)

        # Resample audio to the correct input sampling rate
        resampled_audio = scipy.signal.resample(data, duration * self._target_fs)

        # Trim or pad the data to 30s
        pad_or_trim_audio = whisper.pad_or_trim(resampled_audio)

        # Calculate the mel spectrogram
        mel = whisper.log_mel_spectrogram(pad_or_trim_audio).to(self.model.device)

        options = whisper.DecodingOptions(fp16=True)

        # Do the actual inteference
        result = whisper.decode(self.model, mel, options)
        end_time = time.time()

        # Debut time outputs
        self.logger.debug(
            f"Detected language {result.language} in {end_time - start_time}"
        )
        self.logger.debug(f"Detected Text: {result.text}")

        if result.language in self.target_languages:
            self.logger.debug("Send Data")

            return self.create_output_data(result.text, language=result.language)
        else:
            self.logger.debug(
                f"Dropped Data. Detection {result.language} vs Target {self.target_languages}"
            )
            return None

    def clean_up(self):
        del self.model
