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
        kwargs.update(
            {
                "_e_stop_process"       : self._e_stop_process,

                "e_din_avail"           : e_din_avail,
                "in_data"               : in_data,

                "out_data"              : self.out_data,
                "e_dout_avail"          : self.e_dout_avail,
            }
        )

        # Initiliase the process
        Process.__init__(self, target=self._init, args=args, kwargs=kwargs)

    @classmethod
    def _init(cls, *args, **kwargs):
        cls._run(*args, **kwargs)

    @classmethod
    def _run(cls, **kwargs):
        """ Run function which executes the process method.
        """
        while not kwargs["_e_stop_process"].is_set():

            e_data_avail = kwargs["e_din_avail"]
            e_data_processed = kwargs["e_dout_avail"]
            e_data_avail.wait()

            cls.process(
                kwargs["in_data"],
                kwargs["out_data"]
            )

            e_data_avail.clear()
            e_data_processed.set()

        cls.clean_up()

    @classmethod
    @abstractmethod
    def process(cls, data_in, data_out):
        """ This method should process the available data in data_in and put the result into
        data out. It has to be overwritten by any child class.
        
        Important is also that this function is called in the main processing loop. Therefore
        is should only process the data once it is available and should not have a loop which
        waits for more data. 
        """

    @classmethod
    @abstractmethod
    def clean_up(cls):
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

    def __init__(self, data_buffer_size=1024, in_data=None, e_din_avail=None,):
        super().__init__(data_buffer_size, in_data, e_din_avail)

    @classmethod
    def process(cls, data_in, data_out):
        cls.logger().debug(f"Received data {data_in}")

    @classmethod
    def clean_up(cls):
        pass
