import traitlets
import ipywidgets
from ._frontend import module_name, module_version


@ipywidgets.register
class MainContainer(ipywidgets.VBox):
    """
    This class is a small wrapper around a VBox, which is used internally.
    It adds extra styling to hide the "unlinked" symbols from its children.
    """
    _model_module = traitlets.Unicode(module_name).tag(sync=True)
    _model_name = traitlets.Unicode('MainContainerModel').tag(sync=True)
    _model_module_version = traitlets.Unicode(module_version).tag(sync=True)
    _view_module = traitlets.Unicode(module_name).tag(sync=True)
    _view_name = traitlets.Unicode('MainContainerView').tag(sync=True)
    _view_module_version = traitlets.Unicode(module_version).tag(sync=True)
