""" Main module.
"""
import logging
import os

import multiprocessing as mp

from core.processing import DummyActionProcess
from audio.sounddevice_recorder import SoundDeviceRecorderModule
from audio.whisper_speech_recognition import WhisperSpeechRecognitionModule


logging.basicConfig(level="DEBUG")

if __name__ == "__main__":
    manager = mp.Manager()
    
    speechRecognition = WhisperSpeechRecognitionModule(
        manager,
        output_queues=()
    )

    processing_1 = DummyActionProcess(
        manager,
        None
    )

    if 'DEFAULT_SOUNDDEVICE' in os.environ.keys():
        soundDevice = SoundDeviceRecorderModule(
            manager,
            speechRecognition.model_device,
            duration=WhisperSpeechRecognitionModule.DEFAULT_DURATION,
            device=os.environ['DEFAULT_SOUNDDEVICE'])
    else:
        soundDevice = SoundDeviceRecorderModule(
            manager,
            speechRecognition.model_device,
            duration=WhisperSpeechRecognitionModule.DEFAULT_DURATION)



    soundDevice.output_queues.append(speechRecognition.input_queue)
    speechRecognition.connect_module(processing_1)


    speechRecognition.start()
    soundDevice.start()
    processing_1.start()

    while True:
        pass
