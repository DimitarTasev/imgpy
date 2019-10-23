from enum import Enum
from logging import getLogger
from typing import TYPE_CHECKING

from mantidimaging.core.data import Images
from mantidimaging.core.reconstruct.utility import get_cor_tilt_from_images
from mantidimaging.core.utility.progress_reporting import Progress
from mantidimaging.gui.dialogs.async_task import AsyncTaskDialogView
from mantidimaging.gui.mvp_base import BasePresenter
from .model import TomopyReconWindowModel

LOG = getLogger(__name__)

if TYPE_CHECKING:
    from mantidimaging.gui.windows.tomopy_recon import TomopyReconWindowView


class Notification(Enum):
    UPDATE_PROJECTION_PREVIEW = 1
    PREVIEW_SLICE_NEXT = 2
    PREVIEW_SLICE_PREVIOUS = 3
    RECONSTRUCT_SLICE = 4
    RECONSTRUCT_VOLUME = 5


class TomopyReconWindowPresenter(BasePresenter):

    def __init__(self, view: 'TomopyReconWindowView', main_window):
        super(TomopyReconWindowPresenter, self).__init__(view)
        self.view = view
        self.model = TomopyReconWindowModel()
        self.main_window = main_window

    def notify(self, signal):
        try:
            if signal == Notification.UPDATE_PROJECTION_PREVIEW:
                self.do_update_previews()
            elif signal == Notification.PREVIEW_SLICE_NEXT:
                self.set_preview_slice_idx(self.model.preview_slice_idx - 1)
            elif signal == Notification.PREVIEW_SLICE_PREVIOUS:
                self.set_preview_slice_idx(self.model.preview_slice_idx + 1)
            elif signal == Notification.RECONSTRUCT_SLICE:
                self.do_reconstruct_slice()
            elif signal == Notification.RECONSTRUCT_VOLUME:
                self.do_reconstruct_volume()

        except Exception as e:
            self.show_error(e)
            LOG.exception("Notification handler failed")

    def set_stack_uuid(self, uuid):
        self.set_stack(
            self.main_window.get_stack_visualiser(uuid)
            if uuid is not None else None)

    def set_stack(self, stack):
        self.model.initial_select_data(stack)

        self.view.set_preview_slice_idx(0)
        if self.model.sample is not None:
            self.view.set_preview_slice_max_idx(self.model.sample.shape[0] - 1)

        # Update projection preview
        self.notify(Notification.UPDATE_PROJECTION_PREVIEW)

        # Remove existing reconstructed preview
        self.view.update_recon_preview(None)

        # Pre-populate COR and tilt options
        cor, _, m = get_cor_tilt_from_images(self.model.images)
        self.view.rotation_centre = cor
        self.view.cor_gradient = m

    def set_preview_slice_idx(self, idx):
        max_idx = \
            self.model.sample.shape[0] if self.model.sample is not None else 0
        idx = max(0, min(max_idx, idx))
        self.model.preview_slice_idx = idx
        self.view.set_preview_slice_idx(idx)
        self.notify(Notification.UPDATE_PROJECTION_PREVIEW)

    def do_update_previews(self):
        proj = self.model.projection
        self.view.update_projection_preview(
            proj[0] if proj is not None else None,
            self.model.preview_slice_idx)

    def prepare_reconstruction(self):
        self.model.generate_cors(self.view.rotation_centre, self.view.cor_gradient)
        self.model.current_algorithm = self.view.algorithm_name
        self.model.current_filter = self.view.filter_name
        self.model.generate_projection_angles(self.view.max_proj_angle)

    def do_reconstruct_slice(self):
        self.prepare_reconstruction()
        self._create_recon_task(self.model.reconstruct_slice, self._on_reconstruct_slice_done)

    def do_reconstruct_volume(self):
        self.prepare_reconstruction()
        self._create_recon_task(self.model.reconstruct_volume, self._on_reconstruct_volume_done)

    def _create_recon_task(self, task, on_complete):
        atd = AsyncTaskDialogView(self.view, auto_close=True)
        kwargs = {'progress': Progress()}
        kwargs['progress'].add_progress_handler(atd.presenter)
        atd.presenter.set_task(task)
        atd.presenter.set_on_complete(on_complete)
        atd.presenter.set_parameters(**kwargs)
        atd.presenter.do_start_processing()

    def _on_reconstruct_slice_done(self, task):
        if task.was_successful():
            slice_data = task.result
            self.view.update_recon_preview(slice_data[0])
        else:
            LOG.error('Reconstruction failed: %s', str(task.error))
            self.show_error('Reconstruction failed. See log for details.')

    def _on_reconstruct_volume_done(self, task):
        if task.was_successful():
            volume_data = task.result
            volume_stack = Images(volume_data)
            name = '{}_recon'.format(self.model.stack.name)
            self.main_window.presenter.create_new_stack(volume_stack, name)
        else:
            LOG.error('Reconstruction failed: %s', str(task.error))
            self.show_error('Reconstruction failed. See log for details.')
