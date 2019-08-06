from ._version import version_info, __version__

from ._image_canvas import *
from ._image_viewer import *
from ._brambox_viewer import *

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'itop',
        'require': 'itop/extension'
    }]
