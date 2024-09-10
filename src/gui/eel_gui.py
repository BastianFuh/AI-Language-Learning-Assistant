"""Module for graphical user interface using eel."""

from multiprocessing.managers import SyncManager

import eel
from core.processing import AbstractActionProcess

_local_input_queue = None


def _set_queue(queue):
    global _local_input_queue
    _local_input_queue = queue


@eel.expose
def process_frontend_text(data):
    """Function to process data from the frontend."""
    print(data)
    output_data = {"data": data, "source": "frontend"}

    _local_input_queue.put(output_data)


class EelGuiModule(AbstractActionProcess):
    """Graphical user interface using eel."""

    def __init__(self, manager: SyncManager, *args, output_queues=None, **kwargs):
        super().__init__(manager, "gui", *args, output_queues=output_queues, **kwargs)

    def run(self, *args, **kwargs):
        _set_queue(self.input_queue)

        eel.init("resources/web_folder")
        eel.start("main.html", block=False)

        super().run(*args, **kwargs)

    def process(self, data_in: dict):
        self.logger.info("Test")
        eel.update(data_in)

        if "source" in data_in.keys():
            if data_in["source"] == "frontend":
                return data_in["data"]

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
