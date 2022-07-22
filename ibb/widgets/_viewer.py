import ipywidgets
from ._unlink_box import UnlinkBox
from ._image_canvas import ImageCanvas
from ._image_controls import ImageControls
from ._index_counter import IndexCounter


class Viewer(UnlinkBox):
    """
    Base Viewer class, not intended for end use.

    Create your own superclass of this Viewer and override the \\_\\_init_*\\_\\_ methods. |br|
    Additionaly, you should provide an `on_index` method that does whatever necessary when the index changes.
    """
    def __init__(self, **kwargs):
        super().__init__(
            [
                ipywidgets.HBox(
                    self.__init_header__(kwargs),
                    layout=ipywidgets.Layout(grid_area='header', justify_content='space-between', align_items='center'),
                ),

                ipywidgets.HBox(
                    self.__init_main__(kwargs),
                    layout=ipywidgets.Layout(grid_area='main', align_items='center', width='100%'),
                ),

                ipywidgets.HBox(
                    self.__init_footer__(kwargs),
                    layout=ipywidgets.Layout(grid_area='footer', justify_content='space-between', align_items='center'),
                ),
            ],
            type='grid',
            layout=ipywidgets.Layout(
                width=f'{kwargs["width"]}px' if 'width' in kwargs else '100%',
                grid_template_columns='auto 32px',
                grid_template_rows='32px auto 32px',
                grid_gap='5px',
                grid_template_areas=self.__init_grid_area__(),
            ),
        )

        # Start first
        self.on_index(0)

    def __init_grid_area__(self):
        return """
        "header header"
        "main main"
        "footer footer"
        """

    def __init_header__(self, kwargs):
        self.w_img_label = ipywidgets.Label(
            placeholder='label',
        )

        return [self.w_img_label]

    def __init_footer__(self, kwargs):
        self.w_img_ctrl = ImageControls(
            kwargs.get('total', 1),
            layout=ipywidgets.Layout(),
        )
        self.w_img_ctrl.observe(self._observe_img_ctrl_index, 'index')

        self.w_img_idx = IndexCounter(
            kwargs.get('total', 1),
            layout=ipywidgets.Layout(),
        )
        self.w_img_idx.observe(lambda change: self.on_index(change['new']), 'index')

        return [self.w_img_ctrl, self.w_img_idx]

    def __init_main__(self, kwargs):
        self.w_img_cvs = ImageCanvas(
            height=kwargs.get('height', ImageCanvas.height.default_value),
            layout=ipywidgets.Layout(flex='0 1 100%'),
        )

        return [self.w_img_cvs]

    def _observe_img_ctrl_index(self, change):
        self.w_img_idx.index = change['new']

    def on_index(self, value):
        raise NotImplementedError('abstractmethod')
