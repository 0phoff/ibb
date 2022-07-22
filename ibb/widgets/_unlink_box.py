import traitlets
import ipywidgets
from .._frontend import module_name, module_version


@ipywidgets.register
class UnlinkBox(ipywidgets.Box):
    """
    This class is a small wrapper around a Box, which is used internally.
    It adds extra styling to hide the "unlinked" symbols from its children.

    Args:
        type (Unicode): Control with kind of box we have ('hbox', 'vbox', 'grid'); Default **hbox**

    Note:
        The `type` traitlet can only be set during initialization as a keyword argument.
        Changing the value afterwards has no effect!
    """
    _model_module = traitlets.Unicode(module_name).tag(sync=True)
    _model_name = traitlets.Unicode('UnlinkBoxModel').tag(sync=True)
    _model_module_version = traitlets.Unicode(module_version).tag(sync=True)
    _view_module = traitlets.Unicode(module_name).tag(sync=True)
    _view_name = traitlets.Unicode('UnlinkBoxView').tag(sync=True)
    _view_module_version = traitlets.Unicode(module_version).tag(sync=True)
    type = traitlets.Unicode('hbox').tag(sync=True)

    @traitlets.validate('type')
    def validate_type(self, proposal):
        if proposal['value'] in ('hbox', 'vbox', 'grid'):
            return proposal['value']
        else:
            return 'hbox'
