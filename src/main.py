""" Main module.
"""
import logging
import os

from core.processing import DummyActionProcess
from audio.sounddevice_recorder import SoundDeviceRecorderModule
from audio.whisper_speech_recognition import WhisperSpeechRecognitionModule

import multiprocessing as mp

logging.basicConfig(level="DEBUG")

if __name__ == "__main__":
    if 'DEFAULT_SOUNDDEVICE' in os.environ.keys():
        soundDevice = SoundDeviceRecorderModule(
            duration=WhisperSpeechRecognitionModule.DEFAULT_DURATION, device=os.environ['DEFAULT_SOUNDDEVICE'])
    else:
        soundDevice = SoundDeviceRecorderModule(
            duration=WhisperSpeechRecognitionModule.DEFAULT_DURATION)

    manager = mp.Manager()

    speechRecognition = WhisperSpeechRecognitionModule(
        manager,
        in_data=soundDevice.audio_buffer,
        e_din_avail=soundDevice.e_audio_ready
    )

    processing_1 = DummyActionProcess(
        manager,
        speechRecognition.out_data,
        speechRecognition.e_dout_avail
    )

    speechRecognition.start()
    soundDevice.start()
    processing_1.start()

    while True:
        pass
