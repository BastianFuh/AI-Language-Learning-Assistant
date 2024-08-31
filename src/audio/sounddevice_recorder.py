"""Module containing the Audio recording logic with the sounddevice library."""

import logging
import numpy
import torch

import sounddevice as sd


class SoundDeviceRecorderModule:
    """This module records the specified device and provides the recorded data over a shared memory
    to other modules. New data availability is signaled through an event.
    """

    def __init__(
        self,
        manager,
        model_device,
        output_queues=None,
        duration: int = 30,
        device=sd.default.device[0],
    ):
        """Constructor.

        Args:
            duration (int, optional): The length of each recorded data block in
                                        seconds. Defaults to 30.
            device (int or str, optional): _description_. Defaults to sounddevice.default.device[0].
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        self.device_settings = sd.query_devices(device)

        self.output_queues = manager.list()
        if output_queues is not None:
            self.output_queues.extend(output_queues)

        self.model_device = model_device

        self._duration = duration
        self.sampling_rate = self.device_settings["default_samplerate"]
        self.buffer = numpy.ndarray(
            int(self._duration * self.sampling_rate), dtype=numpy.float32
        )
        self._buffered_amount = 0
        self._block_size = int(1 * self.sampling_rate)

        self.logger.debug("Created Audio Stream with device %s", str(device))
        self.device = device
        self._audio_input_stream = None

    # pylint: disable=unused-argument
    def _audio_callback(self, indata, frames, time, status):
        """Callback function for an audio InputStream."""
        # self.audio_buffer[:] = indata[:, 0]

        if self._buffered_amount < self._duration * self.sampling_rate:
            self.logger.debug("Extended dataset with length: %i ", int(len(indata)))
        else:
            self.logger.debug("Send dataset with length: %i ", int(len(self.buffer)))

            shared_mem = torch.tensor(
                self.buffer, dtype=torch.float16
            )  # .to(self.model_device)

            for queue in self.output_queues:
                queue.put(shared_mem)

            self._buffered_amount = 0

        self.buffer[
            self._buffered_amount : self._buffered_amount + self._block_size
        ] = indata[:, 0]

        self._buffered_amount += self._block_size

    def halt(self) -> None:
        """Stop the current audio recording and send the buffer to the following modules."""
        self.logger.info("Halted audio recording")
        self._audio_input_stream.stop()
        self._audio_input_stream = None

        shared_mem = torch.tensor(
            self.buffer[: self._buffered_amount], dtype=torch.float16
        )

        output = dict()
        output["data"] = shared_mem

        for queue in self.output_queues:
            queue.put(output)

        self._buffered_amount = 0

    def start(self) -> None:
        """Start the audio recording."""

        if self.is_active():
            return

        self.logger.info("Started audio recording")

        self._audio_input_stream = sd.InputStream(
            callback=self._audio_callback,
            device=self.device,
            channels=1,
            blocksize=int(1 * self.sampling_rate),
            samplerate=self.sampling_rate,
        )
        self._audio_input_stream.start()

    def is_active(self) -> bool:
        """Is the audio currently being recorded."""
        if self._audio_input_stream is not None:
            return self._audio_input_stream.active
        else:
            return False
