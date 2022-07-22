import traitlets
import ipywidgets
from .._frontend import module_name, module_version


@ipywidgets.register
class RepeatButton(ipywidgets.Button):
    """
    A button that will repeat the click event when held down.

    Args:
        frequency (Float): Click event frequency in Hz when holding down the button; Default **1**
        delay (Float): Time in seconds before the repeating begins; Default **1**

    Note:
        Whenever you click the button, you get a first click event.
        After `delay` seconds, another click event gets fired repeatedly at your given `frequency`.
    """
    _model_module = traitlets.Unicode(module_name).tag(sync=True)
    _model_name = traitlets.Unicode('RepeatButtonModel').tag(sync=True)
    _model_module_version = traitlets.Unicode(module_version).tag(sync=True)
    _view_module = traitlets.Unicode(module_name).tag(sync=True)
    _view_name = traitlets.Unicode('RepeatButtonView').tag(sync=True)
    _view_module_version = traitlets.Unicode(module_version).tag(sync=True)

    frequency = traitlets.Float(1).tag(sync=True)
    delay = traitlets.Float(1).tag(sync=True)
