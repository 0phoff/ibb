import ipywidgets
import traitlets
from ._unlink_box import UnlinkBox
from ._repeat_button import RepeatButton


class PatchControls(UnlinkBox):
    """
    This widget shows 4 different buttons to control an index with regards to a width and height. |br|
    It's intended use case is to control the patch that is displayed in the :class:`~ibb.widgets.PatchViewer`.

    Args:
        TODO
    """
    total_width = traitlets.Int()
    total_height = traitlets.Int()
    index_width = traitlets.Int(0)
    index_height = traitlets.Int(0)
    frequency = traitlets.Int(5)

    def __init__(self, **kwargs):
        btn_layout = ipywidgets.Layout(width='var(--jp-widgets-inline-height)', padding='0')

        self.btn_up = RepeatButton(
            icon='caret-up',
            tooltip='Move patch up',
            delay=0.5,
            frequency=self.frequency,
            layout=btn_layout,
        )
        self.btn_up.on_click(self.click_up)

        self.btn_down = RepeatButton(
            icon='caret-down',
            tooltip='Move patch down',
            delay=0.5,
            frequency=self.frequency,
            layout=btn_layout,
        )
        self.btn_down.on_click(self.click_down)

        self.btn_left = RepeatButton(
            icon='caret-left',
            tooltip='Move patch left',
            delay=0.5,
            frequency=self.frequency,
            layout=btn_layout,
        )
        self.btn_left.on_click(self.click_left)

        self.btn_right = RepeatButton(
            icon='caret-right',
            tooltip='Move patch right',
            delay=0.5,
            frequency=self.frequency,
            layout=btn_layout,
        )
        self.btn_right.on_click(self.click_right)

        super().__init__(
            [self.btn_up, self.btn_left, self.btn_right, self.btn_down],
            type='grid',
            **kwargs,
        )
        self.add_class('ibb-patch-control')

    @traitlets.validate('total_width')
    def validate_total_width(self, proposal):
        if proposal['value'] <= 0:
            raise traitlets.TraitError('total should be greater than zero')

        self.index_width = min(self.index_width, proposal['value'])
        return proposal['value']

    @traitlets.validate('total_height')
    def validate_total_height(self, proposal):
        if proposal['value'] <= 0:
            raise traitlets.TraitError('total should be greater than zero')

        self.index_height = min(self.index_height, proposal['value'])
        return proposal['value']

    @traitlets.observe('frequency')
    def observe_frequency(self, change):
        self.btn_up.frequency = change['new']
        self.btn_down.frequency = change['new']
        self.btn_left.frequency = change['new']
        self.btn_right.frequency = change['new']

    def click_up(self, change):
        self.index_height = max(min(self.index_height - 1, self.total_height - 1), 0)

    def click_down(self, change):
        self.index_height = max(min(self.index_height + 1, self.total_height - 1), 0)

    def click_left(self, change):
        self.index_width = max(min(self.index_width - 1, self.total_width - 1), 0)

    def click_right(self, change):
        self.index_width = max(min(self.index_width + 1, self.total_width - 1), 0)
