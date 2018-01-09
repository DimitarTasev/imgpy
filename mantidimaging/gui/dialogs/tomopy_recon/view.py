from __future__ import absolute_import, division, print_function

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from mantidimaging.gui.mvp_base import BaseDialogView
from mantidimaging.gui.utility import BlockQtSignals

from .navigation_toolbar import TomopyReconNavigationToolbar
from .presenter import TomopyReconDialogPresenter
from .presenter import Notification as PresNotification


class TomopyReconDialogView(BaseDialogView):

    def __init__(self, main_window, cmap='Greys_r'):
        super(TomopyReconDialogView, self).__init__(
                main_window, 'gui/ui/tomopy_recon_dialog.ui')

        self.presenter = TomopyReconDialogPresenter(self, main_window)

        self.cmap = cmap

        # Handle stack selection
        self.stackSelector.subscribe_to_main_window(main_window)
        self.stackSelector.stack_selected_uuid.connect(
                self.presenter.set_stack_uuid)

        # Handle reconstruct buttons
        self.reconstructSlice.clicked.connect(
                lambda: self.presenter.notify(
                    PresNotification.RECONSTRUCT_SLICE))
        self.reconstructVolume.clicked.connect(
                lambda: self.presenter.notify(
                    PresNotification.RECONSTRUCT_VOLUME))

        # Handle preview slice selection
        self.previewSlice.valueChanged[int].connect(
                self.presenter.set_preview_slice_idx)

        def add_mpl_figure(layout, add_toolbar=False):
            figure = Figure()
            canvas = FigureCanvasQTAgg(figure)
            canvas.setParent(self)
            if add_toolbar:
                toolbar = TomopyReconNavigationToolbar(canvas, self)
                layout.addWidget(toolbar)
            layout.addWidget(canvas)
            return (figure, canvas)

        # Projection image
        self.proj_figure, self.proj_canvas = \
            add_mpl_figure(self.projectionLayout)
        self.proj_plot = self.proj_figure.add_subplot(111)
        self.proj_canvas.mpl_connect(
                'button_press_event', self.proj_on_button_press)
        self.proj_canvas.mpl_connect(
                'scroll_event', self.proj_handle_scroll_wheel)

        # Reconstructed slice image
        self.recon_figure, self.recon_canvas = \
            add_mpl_figure(self.reconLayout, True)
        self.recon_plot = self.recon_figure.add_subplot(111)

    def proj_on_button_press(self, event):
        if event.button == 1 and event.ydata is not None:
            self.presenter.set_preview_slice_idx(int(event.ydata))

    def proj_handle_scroll_wheel(self, event):
        if event.button == 'up':
            self.presenter.notify(PresNotification.PREVIEW_SLICE_NEXT)
        elif event.button == 'down':
            self.presenter.notify(PresNotification.PREVIEW_SLICE_PREVIOUS)

    def update_projection_preview(self,
                                  proj_image_data=None,
                                  indicated_slice=None):
        self.proj_plot.cla()

        if proj_image_data is not None:
            # Plot the image data
            self.proj_plot.imshow(proj_image_data, cmap=self.cmap)

            if indicated_slice is not None:
                # Plot the slice indicator
                x_max = proj_image_data.shape[1] - 1
                self.proj_plot.plot(
                        [0, x_max], [indicated_slice, indicated_slice],
                        c='y')

        self.proj_canvas.draw()

    def update_recon_preview(self, recon_image_data=None):
        # Record the image axis range from the existing preview image
        image_axis_ranges = (
            self.recon_plot.get_xlim(), self.recon_plot.get_ylim()
        ) if self.recon_plot.images else None

        self.recon_plot.cla()

        if recon_image_data is not None:
            self.recon_plot.imshow(recon_image_data, cmap=self.cmap)

        if image_axis_ranges:
            self.recon_plot.set_xlim(image_axis_ranges[0])
            self.recon_plot.set_ylim(image_axis_ranges[1])

        self.recon_canvas.draw()

    def set_preview_slice_idx(self, idx):
        with BlockQtSignals([self.previewSlice]):
            self.previewSlice.setValue(idx)

    def set_preview_slice_max_idx(self, max_idx):
        self.previewSlice.setMaximum(max_idx)

    def get_cor(self):
        return self.cor.value()

    def set_cor(self, value):
        self.cor.setValue(value)

    def get_tilt(self):
        return self.tilt.value()

    def set_tilt(self, value):
        self.tilt.setValue(value)

    def get_max_proj_angle(self):
        return self.maxProjAngle.value()