"""Main module."""

import logging
import os
import queue

from pynput import keyboard

import multiprocessing as mp

from core.processing import LogActionProcess
from audio.sounddevice_recorder import SoundDeviceRecorderModule
from audio.whisper_speech_recognition import WhisperSpeechRecognitionModule
from text.gpt4o_mini import GPT4oMiniTextProcessingModule


logging.basicConfig(level="DEBUG")

key_queue = queue.Queue()


def on_press(key):
    """Key pressed callback."""
    key_queue.put(("pressed", key))


def on_release(key):
    """Key release callback."""
    key_queue.put(("released", key))


RECORD_SOUND_KEY_COMBINATION = {
    keyboard.Key.alt,
    keyboard.Key.ctrl,
    keyboard.KeyCode.from_char("r"),
}
STOP_SOUND_KEY_COMBINATION = {
    keyboard.Key.alt,
    keyboard.Key.ctrl,
    keyboard.KeyCode.from_char("s"),
}

STOP_APPLICATION = {
    keyboard.Key.ctrl,
    keyboard.KeyCode.from_char("c"),
}


if __name__ == "__main__":
    manager = mp.Manager()

    if "DEFAULT_SOUNDDEVICE" in os.environ.keys():
        soundDevice = SoundDeviceRecorderModule(
            manager,
            WhisperSpeechRecognitionModule.get_process_device(),
            duration=WhisperSpeechRecognitionModule.SEGMENT_DURATION,
            device=os.environ["DEFAULT_SOUNDDEVICE"],
        )
    else:
        soundDevice = SoundDeviceRecorderModule(
            manager,
            WhisperSpeechRecognitionModule.get_process_device(),
            duration=WhisperSpeechRecognitionModule.SEGMENT_DURATION,
        )

    speechRecognition = WhisperSpeechRecognitionModule(
        manager, soundDevice.sampling_rate
    )

    text_processing = GPT4oMiniTextProcessingModule(manager)

    processing_1 = LogActionProcess(manager, None)

    soundDevice.output_queues.append(speechRecognition.input_queue)

    speechRecognition.connect_module(processing_1)
    speechRecognition.connect_module(text_processing)

    text_processing.connect_module(processing_1)

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    speechRecognition.start()
    soundDevice.start()
    processing_1.start()
    text_processing.start()

    pressend_keys = set()

    while True:
        keys = key_queue.get()

        normalized_key = listener.canonical(keys[1])
        if keys[0] == "released":
            pressend_keys.remove(normalized_key)

        if keys[0] == "pressed":
            pressend_keys.add(normalized_key)

        if all(k in pressend_keys for k in RECORD_SOUND_KEY_COMBINATION):
            soundDevice.start()

        if all(k in pressend_keys for k in STOP_SOUND_KEY_COMBINATION):
            soundDevice.halt()

        if all(k in pressend_keys for k in STOP_APPLICATION):
            speechRecognition.kill()
            processing_1.kill()
            text_processing.kill()

            exit()
