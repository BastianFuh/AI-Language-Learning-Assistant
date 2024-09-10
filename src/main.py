"""Main module."""

import logging
import multiprocessing as mp
import os
import queue

from anyio import Path
from pynput import keyboard
import requests

from audio.openai_tts import OpenAITTS
from audio.sounddevice_recorder import SoundDeviceRecorderModule
from audio.whisper_speech_recognition import WhisperSpeechRecognitionModule
from core.processing import LogActionProcess
from gui.eel_gui import EelGuiModule
from text.gpt4o_mini import GPT4oMiniTextProcessingModule

logging.basicConfig(level="INFO")

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
    keyboard.Key.alt,
    keyboard.Key.ctrl,
    keyboard.KeyCode.from_char("c"),
}


if __name__ == "__main__":
    # if not Path("/css/bootstrap/bootstrap.min.css").exists():
    # requests.get()

    manager = mp.Manager()

    default_soundevice_input = os.environ.get("DEFAULT_SOUNDDEVICE", None)

    if default_soundevice_input is not None:
        soundDevice = SoundDeviceRecorderModule(
            manager,
            WhisperSpeechRecognitionModule.get_process_device(),
            duration=WhisperSpeechRecognitionModule.SEGMENT_DURATION,
            device=default_soundevice_input,
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

    audio_out = OpenAITTS(manager)

    gui = EelGuiModule(manager)

    soundDevice.output_queues.append(speechRecognition.input_queue)

    speechRecognition.connect_output_to(processing_1)
    speechRecognition.connect_output_to(text_processing)
    speechRecognition.connect_output_to(gui)

    text_processing.connect_output_to(processing_1)
    text_processing.connect_output_to(audio_out)
    text_processing.connect_output_to(gui)

    gui.connect_output_to(text_processing)

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    # soundDevice.start()
    gui.start()
    speechRecognition.start()
    processing_1.start()
    text_processing.start()
    audio_out.start()

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
