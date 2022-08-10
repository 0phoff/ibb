import ipywidgets
import traitlets
from ._unlink_box import UnlinkBox
from ._repeat_button import RepeatButton


class ImageControls(UnlinkBox):
    """
    This widget shows 6 different buttons to control an index with regards to a total length. |br|
    Its intended use case is to control the image that is displayed in other IBB widgets.

    Args:
        total (int): Maximum number the controls index can reach
        name (str): What the controls are used for (eg. 'image')
    """
    total = traitlets.Int()
    index = traitlets.Int(0)
    fast = traitlets.Int(10)
    frequency = traitlets.Int(24)

    def __init__(self, total, name, plural_name=None, **kwargs):
        self.total = total
        self.name = name
        self.plural_name = plural_name if plural_name is not None else f'{name}s'

        btn_layout = ipywidgets.Layout(width='var(--jp-widgets-inline-height)', padding='0')

        self.btn_begin = ipywidgets.Button(
            icon='fast-backward',
            tooltip=f'First {self.name}',
            layout=btn_layout,
        )
        self.btn_begin.on_click(lambda btn: self._index_set(0))

        self.btn_end = ipywidgets.Button(
            icon='fast-forward',
            tooltip=f'Last {self.name}',
            layout=btn_layout,
        )
        self.btn_end.on_click(lambda btn: self._index_set(self.total))

        self.btn_prev_fast = RepeatButton(
            icon='backward',
            tooltip=f'-{self.fast} {self.plural_name} (hold to repeat)',
            delay=0.5,
            frequency=self.frequency,
            layout=btn_layout,
        )
        self.btn_prev_fast.on_click(lambda btn: self._index_delta(-self.fast))

        self.btn_next_fast = RepeatButton(
            icon='forward',
            tooltip=f'+{self.fast} {self.plural_name} (hold to repeat)',
            delay=0.5,
            frequency=self.frequency,
            layout=btn_layout,
        )
        self.btn_next_fast.on_click(lambda btn: self._index_delta(self.fast))

        self.btn_prev = RepeatButton(
            icon='step-backward',
            tooltip=f'-1 {self.name} (hold to repeat)',
            delay=0.5,
            frequency=self.frequency,
            layout=btn_layout,
        )
        self.btn_prev.on_click(lambda btn: self._index_delta(-1, True))

        self.btn_next = RepeatButton(
            icon='step-forward',
            tooltip=f'+1 {self.name} (hold to repeat)',
            delay=0.5,
            frequency=self.frequency,
            layout=btn_layout,
        )
        self.btn_next.on_click(lambda btn: self._index_delta(1, True))

        super().__init__([
            self.btn_begin,
            self.btn_prev_fast,
            self.btn_prev,
            self.btn_next,
            self.btn_next_fast,
            self.btn_end,
        ], **kwargs)

    @traitlets.validate('fast')
    def validate_fast(self, proposal):
        if proposal['value'] < 0:
            raise traitlets.TraitError('fast should be greater than zero')
        return proposal['value']

    @traitlets.observe('fast')
    def observe_fast(self, change):
        self.btn_prev_fast.tooltip = f'-{change["new"]} {self.plural_name} (hold to repeat)'
        self.btn_next_fast.tooltip = f'+{change["new"]} {self.plural_name} (hold to repeat)'

    @traitlets.observe('frequency')
    def observe_frequency(self, change):
        self.btn_prev_fast.frequency = change['new']
        self.btn_prev.frequency = change['new']
        self.btn_next_fast.frequency = change['new']
        self.btn_next.frequency = change['new']

    def _index_delta(self, delta, wrap=False):
        self._index_set(self.index + delta, wrap)

    def _index_set(self, value, wrap=False):
        if wrap:
            self.index = value % self.total
        else:
            self.index = max(min(value, self.total - 1), 0)
