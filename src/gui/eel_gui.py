"""Module for graphical user interface using eel."""

from multiprocessing.managers import SyncManager

import eel
from core.processing import AbstractActionProcess


class EelGuiModule(AbstractActionProcess):
    """Graphical user interface using eel."""

    def __init__(self, manager: SyncManager, *args, output_queues=None, **kwargs):
        super().__init__(manager, *args, output_queues=output_queues, **kwargs)

    def run(self, *args, **kwargs):
        eel.init("resources/web_folder")
        eel.start("main.html", block=False)

        super().run(*args, **kwargs)

    def process(self, data_in):
        self.logger.info("Test")
        eel.update(data_in)

        return None

    def clean_up(self):
        pass

    def _run(self, **kwargs):
        """Run function which executes the process method."""
        while not self._e_stop_process.is_set():
            # Get data to process
            eel.sleep(1)
            if not self.input_queue.empty():
                in_data = self.input_queue.get(block=False)

                # Process the data
                self.process(in_data)
