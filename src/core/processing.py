""" Module containing the abstract base class for the Processing modules.
"""
from abc import abstractmethod
from multiprocessing import Process, Event
from multiprocessing.sharedctypes import Array

import logging


class AbstractActionProcess(Process):
    """
        This class represent an abstract processing module which runs inside
        its own process. 
    """

    _logger = None

    def __init__(self, *args, data_buffer_size=1024, buffer_type="d", in_data=None,
                 e_din_avail=None, **kwargs):
        # Public Events
        self.e_dout_avail = Event()

        # Private Events
        self._e_stop_process = Event()

        # Public Shared Data
        self.out_data = Array(buffer_type, int(data_buffer_size))

        # Update the key word arguements to include the events

        self._e_din_avail = e_din_avail
        self._in_data = in_data


        # Initiliase the process
        Process.__init__(self, args=args, kwargs=kwargs)

    def run(self, **kwargs):
        self._run(**kwargs)

    def _run(self, **kwargs):
        """ Run function which executes the process method.
        """
        while not self._e_stop_process.is_set():

            self._e_din_avail.wait()

            self.process(
                self._in_data,
                self.out_data
            )

            self.e_dout_avail.set()
            self.e_dout_avail.clear()

        self.clean_up()

    @abstractmethod
    def process(self, data_in : Array, data_out : Array):
        """ This method should process the available data in data_in and put the result into
        data out. It has to be overwritten by any child class.

        Important is also that this function is called in the main processing loop. Therefore
        is should only process the data once it is available and should not have a loop which
        waits for more data. 
        """

    @abstractmethod
    def clean_up(self):
        """ Cleans up the thread when it is killed.
        """

    def kill(self):
        self.logger().info("Send kill signal to process")
        self._e_stop_process.set()

    @classmethod
    def logger(cls):
        """ Return the logger for the class.
        """
        if cls._logger is None:
            cls._logger = logging.getLogger(cls.__name__)

        return cls._logger


class DummyActionProcess(AbstractActionProcess):
    """Dummy module which only logs the current data.
    """

    def __init__(self, in_data=None, e_din_avail=None,):
        super().__init__(
            data_buffer_size=0,
            in_data=in_data,
            e_din_avail=e_din_avail)

    def process(self, data_in, data_out):
        self.logger().info(f"Received data { data_in}")

    def clean_up(self):
        pass
