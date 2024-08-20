"""Main module."""

import logging
import os

import multiprocessing as mp

from core.processing import LogActionProcess
from audio.sounddevice_recorder import SoundDeviceRecorderModule
from audio.whisper_speech_recognition import WhisperSpeechRecognitionModule
from text.gemma import GemmaTextProcessingModule


logging.basicConfig(level="INFO")

if __name__ == "__main__":
    manager = mp.Manager()

    speechRecognition = WhisperSpeechRecognitionModule(manager)

    text_processing = GemmaTextProcessingModule(manager)

    processing_1 = LogActionProcess(manager, None)

    if "DEFAULT_SOUNDDEVICE" in os.environ.keys():
        soundDevice = SoundDeviceRecorderModule(
            manager,
            WhisperSpeechRecognitionModule.get_process_device(),
            duration=WhisperSpeechRecognitionModule.DEFAULT_DURATION,
            device=os.environ["DEFAULT_SOUNDDEVICE"],
        )
    else:
        soundDevice = SoundDeviceRecorderModule(
            manager,
            speechRecognition.model_device,
            duration=WhisperSpeechRecognitionModule.DEFAULT_DURATION,
        )

    soundDevice.output_queues.append(speechRecognition.input_queue)

    speechRecognition.connect_module(processing_1)
    speechRecognition.connect_module(text_processing)

    text_processing.connect_module(processing_1)

    speechRecognition.start()
    soundDevice.start()
    processing_1.start()
    text_processing.start()

    while True:
        pass
