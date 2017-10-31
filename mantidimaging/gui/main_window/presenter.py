from __future__ import absolute_import, division, print_function

from enum import Enum
from logging import getLogger

from mantidimaging.core.utility.progress_reporting import Progress
from mantidimaging.gui.async_task_dialog import AsyncTaskDialogView

from .model import MainWindowModel


class Notification(Enum):
    LOAD = 1
    SAVE = 2


class MainWindowPresenter(object):
    def __init__(self, view, config):
        super(MainWindowPresenter, self).__init__()
        self.view = view
        self.model = MainWindowModel(config)

        # directly forward the reference
        self.apply_to_data = self.model.apply_to_data

    def notify(self, signal):
        try:
            if signal == Notification.LOAD:
                self.load_stack()
            elif signal == Notification.SAVE:
                self.save()

        except Exception as e:
            self.show_error(e)
            raise  # re-raise for full stack trace

    def show_error(self, error):
        self.view.show_error_dialog(error)

    def remove_stack(self, uuid):
        self.model.do_remove_stack(uuid)
        self.view.active_stacks_changed.emit()

    def load_stack(self):
        log = getLogger(__name__)

        kwargs = {}
        kwargs['selected_file'] = self.view.load_dialogue.sample_file()
        kwargs['sample_path'] = self.view.load_dialogue.sample_path()
        kwargs['image_format'] = self.view.load_dialogue.image_format
        kwargs['parallel_load'] = self.view.load_dialogue.parallel_load()
        kwargs['indices'] = self.view.load_dialogue.indices()
        kwargs['custom_name'] = self.view.load_dialogue.window_title()

        if not kwargs['sample_path']:
            log.debug("No sample path provided, cannot load anything")
            return

        atd = AsyncTaskDialogView(self.view, auto_close=True)
        kwargs['progress'] = Progress()
        kwargs['progress'].add_progress_handler(atd.presenter)

        atd.presenter.set_task(self.model.do_load_stack)
        atd.presenter.set_on_complete(self._on_stack_load_done)
        atd.presenter.set_parameters(**kwargs)
        atd.presenter.do_start_processing()

    def _on_stack_load_done(self, task):
        log = getLogger(__name__)

        if task.was_successful():
            custom_name = task.kwargs['custom_name']
            title = self.model.create_name(task.kwargs['selected_file']) if \
                not custom_name else custom_name

            dock_widget = self.view.create_stack_window(
                    task.result, title=title)

            stack_visualiser = dock_widget.widget()
            self.model.add_stack(stack_visualiser, dock_widget)
            self.view.active_stacks_changed.emit()

        else:
            log.error("Failed to load stack: %s", str(task.error))
            self.show_error("Failed to load stack. See log for details.")

    def save(self, indices=None):
        kwargs = {}
        kwargs['stack_uuid'] = self.view.save_dialogue.selected_stack
        kwargs['output_dir'] = self.view.save_dialogue.save_path()
        kwargs['name_prefix'] = self.view.save_dialogue.name_prefix()
        kwargs['image_format'] = self.view.save_dialogue.image_format()
        kwargs['overwrite'] = self.view.save_dialogue.overwrite()
        kwargs['swap_axes'] = self.view.save_dialogue.swap_axes()
        kwargs['indices'] = indices

        atd = AsyncTaskDialogView(self.view, auto_close=True)
        kwargs['progress'] = Progress()
        kwargs['progress'].add_progress_handler(atd.presenter)

        atd.presenter.set_task(self.model.do_saving)
        atd.presenter.set_on_complete(self._on_save_done)
        atd.presenter.set_parameters(**kwargs)
        atd.presenter.do_start_processing()

    def _on_save_done(self, task):
        log = getLogger(__name__)

        if not task.was_successful():
            log.error("Failed to save stack: %s", str(task.error))
            self.show_error("Failed to save stack. See log for details.")

    def stack_names(self):
        return self.model.stack_names()

    def stack_list(self):
        return self.model.stack_list()