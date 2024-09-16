"""Module for graphical user interface using eel."""

from multiprocessing import Queue
from multiprocessing.managers import SyncManager
from typing import Iterable

import eel
from core.processing import AbstractActionProcess


class EelGuiModule(AbstractActionProcess):
    """Graphical user interface using eel."""

    def __init__(
        self,
        manager: SyncManager,
        *args,
        output_queues: Iterable[Queue] = None,
        **kwargs,
    ):
        super().__init__(manager, "gui", *args, output_queues=output_queues, **kwargs)
        self.history: list = list()

    def run(self, *args, **kwargs) -> None:
        # Set global object so that the function used for eel can also access the object
        # pylint: disable=global-statement
        global _GUI_MODULE
        _GUI_MODULE = self
        # pylint: enable=global-statement

        eel.init("resources/web_folder")
        eel.start("main.html", block=False, size=(1000, 1000))

        super().run(*args, **kwargs)

    def process(self, data_in: dict) -> None:
        self.history.append(data_in)
        eel.update(data_in)

        return None

    def clean_up(self):
        pass

    def _run(self, **kwargs) -> None:
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


_GUI_MODULE: EelGuiModule = None


@eel.expose
def process_frontend_text(data: dict) -> None:
    """Function to process data from the frontend."""
    print(data)
    output_data = {"data": data, "source": "frontend"}

    _GUI_MODULE.input_queue.put(output_data)


@eel.expose
def get_data() -> None:
    """Function for frontend to fetch data."""
    for data in _GUI_MODULE.history:
        eel.update(data)
