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

    Each of the different \\_\\_init_*\\_\\_ methods has different keyword arguments that are used to control the base implementations. |br|
    See their documentation for more information.

    Warning:
        It is important to note that you can only add widgets in the various init methods and cannot change them afterwards!
    """
    def __init__(self, **kwargs):
        # Create child widgets
        self.__header = tuple(self.__init_header__(kwargs))
        self.__main = tuple(self.__init_main__(kwargs))
        self.__side = tuple(self.__init_side__(kwargs))
        self.__footer = tuple(self.__init_footer__(kwargs))

        items = [
            ipywidgets.HBox(
                self.__header,
                layout=ipywidgets.Layout(grid_area='header', justify_content='space-between', align_items='center'),
            ),

            ipywidgets.HBox(
                self.__main,
                layout=ipywidgets.Layout(grid_area='main', align_items='center', justify_self='stretch', align_self='stretch'),
            ),

            ipywidgets.HBox(
                self.__footer,
                layout=ipywidgets.Layout(grid_area='footer', justify_content='space-between', align_items='center'),
            ),
        ]

        if len(self.__side):
            items.append(ipywidgets.HBox(
                self.__side,
                layout=ipywidgets.Layout(grid_area='side', align_items='center', justify_self='stretch', align_self='stretch'),
            ))

        super().__init__(items, type='grid', **kwargs)

        # Add CSS
        self.add_class('ibb-viewer')
        if len(self.__side):
            self.add_class('ibb-side')

        # Start first
        self.on_index(0)

    def __init_header__(self, kwargs):
        """
        Initialize widgets that are placed above the main area. |br|
        The default implementation places a label widget, which can be accessed through :prop:`Viewer.header`.
        """
        w_label = ipywidgets.Label(
            placeholder='label',
        )

        return [w_label]

    def __init_main__(self, kwargs):
        """
        Initialize widgets that are placed in the main area. |br|
        The default implementation places an :class:`~ibb.widgets.ImageCanvas`, which can be accessed through :prop:`Viewer.main`.
        """
        canvas_names = {'enable_poly', 'auto_clear', 'enlarge', 'color', 'alpha', 'size', 'hover_style', 'click_style'}
        canvas_kwargs = {k: v for k, v in kwargs.items() if k in canvas_names}
        w_canvas = ImageCanvas(
            **canvas_kwargs,
            layout=ipywidgets.Layout(flex='0 1 auto', height='100%'),
        )

        return [w_canvas]

    def __init_side__(self, kwargs):
        """
        Initialize widgets that are placed on the right of the main area. |br|
        The default implementation does not use this side gutter.
        """
        return []

    def __init_footer__(self, kwargs):
        """
        Initialize widgets that are placed below the main area. |br|
        The default implementation places :class:`~ibb.widgets.ImageControls` and an :class:`~ibb.widgets.IndexCounter`, which can be accessed through :prop:`Viewer.footer`.

        Args:
            total (number, kw-only): Maximum number for the :class:`~ibb.widgets.IndexCounter`; Default **1**
            control_total (number, kw-only): Maximum number for the :class:`~ibb.widgets.ImageControls`; Default **value from total**
        """
        w_ctrl = ImageControls(
            total=kwargs.get('control_total', kwargs.get('total', 1)),
            name='image',
        )
        w_ctrl.observe(lambda change: self.on_control(change['new']), 'index')

        self.__w_idx = IndexCounter(
            total=kwargs.get('total', 1),
        )
        self.__w_idx.observe(lambda change: self.on_index(change['new']), 'index')

        return [w_ctrl, self.__w_idx]

    def on_control(self, value):
        """
        Method that runs whenever the index of the button controls change. |br|
        The default implementation simply sets the index input to the new control value, which in turn runs the :meth:`Viewer.on_index` method.
        """
        self.__w_idx.index = value

    def on_index(self, value):
        """
        Method that runs whenever the index number changes. |br|
        This method should be implemented by every widget that inherits from this class.
        """
        raise NotImplementedError('abstractmethod')

    @property
    def header(self):
        """ Returns a tuple with the elements from :meth:`Viewer.__init_header__`. """
        return self.__header

    @property
    def main(self):
        """ Returns a tuple with the elements from :meth:`Viewer.__init_main__`. """
        return self.__main

    @property
    def side(self):
        """ Returns a tuple with the elements from :meth:`Viewer.__init_side__`. """
        return self.__side

    @property
    def footer(self):
        """ Returns a tuple with the elements from :meth:`Viewer.__init_footer__`. """
        return self.__footer
