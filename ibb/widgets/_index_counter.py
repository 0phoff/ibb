import ipywidgets
import traitlets
from ._unlink_box import UnlinkBox


class IndexCounter(UnlinkBox):
    """
    Small widget that has a number input field and a label to set the index of something. |br|
    For end users, the range of the index is [1, total], but when accessing the `index` value, it is rescaled to [0, total).

    Args:
        total (Integer): Maximum index value
    """
    total = traitlets.Int()
    index = traitlets.Int()

    def __init__(self, total, **kwargs):
        self.input = ipywidgets.BoundedIntText(min=1, max=total, layout=ipywidgets.Layout(max_width='75px', flex='0 1 auto'))
        self.label = ipywidgets.Label(f'/ {total}')
        self.total = total

        self.input.observe(self.observe_input_value, 'value')

        super().__init__([
            self.input,
            self.label,
        ], **kwargs)

    @traitlets.validate('total')
    def validate_total(self, proposal):
        if proposal['value'] <= 0:
            raise traitlets.TraitError('Total should be greater than zero')
        return proposal['value']

    @traitlets.observe('total')
    def observe_total(self, change):
        value = change['new']
        self.label.value = f'/ {value}'
        self.input.max = value

    @traitlets.validate('index')
    def validate_index(self, proposal):
        return max(min(proposal['value'], self.total - 1), 0)

    @traitlets.observe('index')
    def observe_index(self, change):
        self.input.value = change['new'] + 1

    def observe_input_value(self, change):
        self.index = change['new'] - 1
