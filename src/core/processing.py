"""Module containing the abstract base class for the Processing modules."""

import logging

import ctypes

from abc import abstractmethod

from multiprocessing.managers import SyncManager
from torch.multiprocessing import Process


class AbstractActionProcess(Process):
    """
    This class represent an abstract processing module which runs inside
    its own process.
    """

    _logger = None

    def __init__(self, manager: SyncManager, *args, output_queues=None, **kwargs):
        self._e_stop_process = manager.Event()

        self.input_queue = manager.Queue()

        self.output_queues = manager.list()
        if output_queues is not None:
            self.output_queues.extend(output_queues)

        # Initiliase the process
        Process.__init__(self, args=args, kwargs=kwargs)

    def add_output_queue(self, queue):
        """Adds a module which will receive the output of this module."""
        self.output_queues.append(queue)

    def connect_module(self, module):
        """Connects the input of the given module to the output of this module."""
        self.output_queues.append(module.input_queue)

    def run(self, **kwargs):
        self._run(**kwargs)

    def _run(self, **kwargs):
        """Run function which executes the process method."""
        while not self._e_stop_process.is_set():
            in_data = self.input_queue.get()

            out_data = self.process(in_data)

            for queue in self.output_queues:
                queue.put(out_data)

        self.clean_up()

    @abstractmethod
    def process(self, data_in):
        """This method should process the available data in data_in and put the result into
        data out. It has to be overwritten by any child class.

        Important is also that this function is called in the main processing loop. Therefore
        is should only process the data once it is available and should not have a loop which
        waits for more data.
        """

    @abstractmethod
    def clean_up(self):
        """Cleans up the thread when it is killed."""

    def kill(self):
        self.logger().info("Send kill signal to process")
        self._e_stop_process.set()

    @classmethod
    def logger(cls):
        """Return the logger for the class."""
        if cls._logger is None:
            cls._logger = logging.getLogger(cls.__name__)

        return cls._logger


class LogActionProcess(AbstractActionProcess):
    """Dummy module which only logs the current data."""

    def __init__(self, manager, output_queues):
        super().__init__(manager, output_queues=output_queues)

    def process(self, data_in):
        self.logger().debug(f"Received data {data_in}")

    def clean_up(self):
        pass
