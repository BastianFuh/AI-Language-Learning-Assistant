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
        eel.start("main.html", block=False, size=(1000, 1000))

        super().run(*args, **kwargs)

    def process(self, data_in: dict):
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

                if "source" in in_data.keys():
                    if in_data["source"] == "frontend":
                        out_data = self.create_output_data(
                            in_data["data"], language="en"
                        )

                        # Update the output data set with the metadata contained inside the input
                        in_data.pop("data", None)
                        out_data.update(in_data)
                        out_data["source"] = self.label

                        for queue in self.output_queues:
                            queue.put(out_data)
