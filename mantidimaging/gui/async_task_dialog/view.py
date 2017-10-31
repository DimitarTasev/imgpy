from __future__ import absolute_import, division, print_function

from PyQt5 import Qt

from mantidimaging.core.utility import gui_compile_ui

from .presenter import AsyncTaskDialogPresenter


class AsyncTaskDialogView(Qt.QDialog):
    def __init__(self, parent, auto_close=False):
        super(AsyncTaskDialogView, self).__init__(parent)
        gui_compile_ui.execute('gui/ui/async_task_dialog.ui', self)

        self.parent_view = parent
        self.presenter = AsyncTaskDialogPresenter(self)

        self.auto_close = auto_close

        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1000)

        self.progress_text = self.infoText.text()

    def handle_completion(self, successful):
        """
        Updates the UI after the task has been completed.

        :param successful: If the task was successful
        """
        # Set info text to "Complete"
        self.infoText.setText("Complete")

        # If auto close is enabled and the task was sucesfull then hide the UI
        if self.auto_close and successful:
            self.hide()

    def set_progress(self, progress, message):
        # Set status message
        if message:
            self.infoText.setText(message)

        # Update progress bar
        self.progressBar.setValue(progress * 1000)