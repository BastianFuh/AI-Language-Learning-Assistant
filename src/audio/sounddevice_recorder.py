""" Module containing the Audio recording logic with the sounddevice library.
"""
import logging
import ctypes

from multiprocessing import Event
from multiprocessing.sharedctypes import Array

import sounddevice as sd


class SoundDeviceRecorderModule:
    """ This module records the specified device and provides the recorded data over a shared memory
    to other modules. New data availability is signaled through an event.
    """

    def __init__(self, duration: int = 30, device=sd.default.device[0]):
        """Constructor.

        Args:
            duration (int, optional): The length of each recorded data block in 
                                        seconds. Defaults to 30.
            device (int or str, optional): _description_. Defaults to sounddevice.default.device[0].
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        self.device_settings = sd.query_devices(device)

        # Buffer used to share the audio data
        self.audio_buffer = Array(ctypes.c_double, int(
            self.device_settings["default_samplerate"] * duration))
        # Event to signal the availability of data
        self.e_audio_ready = Event()

        self.logger.debug("Created Audio Stream with device %s", str(device))
        self._audio_input_stream = sd.InputStream(
            callback=self._audio_callback,
            device=device,
            channels=1,
            blocksize=int(
                duration * self.device_settings["default_samplerate"]),
            samplerate=self.device_settings["default_samplerate"],
        )

    # pylint: disable=unused-argument
    def _audio_callback(self, indata, frames, time, status):
        """Callback function for an audio InputStream.
        """
        self.logger.debug(
            "Created new dataset with length: %i ", int(len(indata)))
        self.audio_buffer[:] = indata[:, 0]

        # Event is set and cleared so that the current sleeping threads are awoken and next time
        # they reach wait again they block.
        self.e_audio_ready.set()
        self.e_audio_ready.clear()

    def halt(self) -> None:
        """ Immediately halt the current audio recording.
        """
        self.logger.info("Halted audio recording")
        self._audio_input_stream.abort()

    def start(self) -> None:
        """ Start the audio recording.
        """
        self.logger.info("Started audio recording")
        self._audio_input_stream.start()

    def is_active(self) -> bool:
        """ Is the audio currently being recorded.
        """
        return self._audio_input_stream.active
