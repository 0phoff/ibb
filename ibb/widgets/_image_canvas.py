import traitlets
import traittypes
import ipywidgets
import numpy as np
from .._frontend import module_name, module_version
from .._util import cast_alpha

__all__ = ['ImageCanvas']


def array_to_binary(ar, obj=None):
    if ar is not None:
        mv = memoryview(ar)
        return {'data': mv, 'shape': ar.shape[:-1]}
    else:
        return None


@ipywidgets.register
class ImageCanvas(ipywidgets.DOMWidget):
    """
    This widget is capable of displaying numpy array as images and draw polygons on them.
    It scales the images to fit in the view and ensures the polygons are scaled accordingly as well.
    It is also capable to provide hover/click statuses for the displayed polygons.

    Args:
        enable_rect (Boolean): Whether to enable the rectangle functionality; Default **True**
        auto_clear (Boolean): Whether to clear the polygons when drawing a new image; Default **True**
        enlarge (Boolean): Whether to enlarge an image to take up the most space in the canvas; Default **True**
        color (String): Default color to draw polygons; Default **#1F77B4**
        alpha (String): Default alpha fill value for the polygons; Default **00**
        size (Integer): Default border thickness for the polygons; Default **2**
        hover_style (Dict): Default hover style (can contain color,alpha and/or size properties); Default **None**
        click_style (Dict): Default click style (can contain color,alpha and/or size properties); Default **None**

    Attributes:
        image (numpy.ndarray): Image data in HWC order. See :meth:`ImageCanvas.validate_image` for more information
        polygons (dict): polygons to draw. See :meth:`ImageCanvas.validate_polygons` for more information
        clicked (Integer): Index of the clicked rectangle
        hovered (Integer): Index of the hovered rectangle
        save (Bool): Save image and polygons
    """
    _model_module = traitlets.Unicode(module_name).tag(sync=True)
    _model_name = traitlets.Unicode('ImageCanvasModel').tag(sync=True)
    _model_module_version = traitlets.Unicode(module_version).tag(sync=True)
    _view_module = traitlets.Unicode(module_name).tag(sync=True)
    _view_name = traitlets.Unicode('ImageCanvasView').tag(sync=True)
    _view_module_version = traitlets.Unicode(module_version).tag(sync=True)

    # Settings
    enable_poly = traitlets.Bool(True).tag(sync=True)
    auto_clear = traitlets.Bool(True)
    enlarge = traitlets.Bool(True).tag(sync=True)
    color = traitlets.Unicode('#1F77B4').tag(sync=True)
    alpha = traitlets.Unicode('00').tag(sync=True)
    size = traitlets.Int(2).tag(sync=True)
    hover_style = traitlets.Dict(default_value=None, allow_none=True).tag(sync=True)
    click_style = traitlets.Dict(default_value=None, allow_none=True).tag(sync=True)

    # Attributes
    image = traittypes.Array(None, allow_none=True).tag(sync=True, to_json=array_to_binary)
    polygons = traitlets.List(None, allow_none=True).tag(sync=True)
    clicked = traitlets.Int(None, allow_none=True).tag(sync=True)
    hovered = traitlets.Int(None, allow_none=True).tag(sync=True)
    save = traitlets.Bool(False).tag(sync=True)

    def __init__(self, **kwargs):
        for attr in ('color', 'alpha', 'size'):
            if attr in kwargs:
                kwargs[attr] = getattr(self, f'_validate_{attr}')({'value': kwargs[attr]})

        if 'hover_style' in kwargs and kwargs['hover_style'] is not None:
            try:
                kwargs['hover_style'] = self._validate_fx(kwargs['hover_style'])
            except Exception as err:
                raise ValueError(f'Wrong value in hover_style: {err}') from err

        if 'click_style' in kwargs and kwargs['click_style'] is not None:
            try:
                kwargs['click_style'] = self._validate_fx(kwargs['click_style'])
            except Exception as err:
                raise ValueError(f'Wrong value in click_style: {err}') from err

        super().__init__(**kwargs)

    @traitlets.validate('image')
    def validate_image(self, proposal):
        """
        Validate correct image shape and dtype and cast to RGBA uint8 (0-255)

        Valid data types:
            - RGBA uint8 (0-255)
            - RGB uint8 (0-255)
            - Grayscale uint8 (0-255)
            - RGBA float (0-1)
            - RGB float (0-1)
            - Grayscale float (0-1)
        """
        img = proposal['value']
        if self.auto_clear:
            self.polygons = None
            self.hovered = None
            self.clicked = None

        if img is None:
            return img
        if not isinstance(img, np.ndarray):
            raise TypeError(f'image should by a numpy array or None [{type(img)}]')

        if img.dtype == np.uint8:
            if img.ndim == 2:
                img = np.dstack((img, img, img, 255 * np.ones(img.shape, dtype=np.uint8)))
                return img
            elif img.ndim == 3 and img.shape[2] in (3, 4):
                if img.shape[2] == 3:
                    img = np.dstack((img, 255 * np.ones(img.shape[:-1], dtype=np.uint8)))
                return img
            else:
                raise ValueError(f'Image shape not supported [{img.shape}, {img.dtype}]')
        elif img.dtype in (np.float32, np.float64):
            if img.ndim == 2:
                img = np.dstack((img, img, img, np.ones(img.shape, dtype=img.dtype)))
            elif img.ndim == 3 and img.shape[2] == 3:
                img = np.dstack((img, np.ones(img.shape[:-1], dtype=img.dtype)))

            if img.ndim == 3 and img.shape[2] == 4:
                return (img * 255).astype(np.uint8)
            else:
                raise ValueError(f'Image shape not supported [{img.shape}, {img.dtype}]')
        else:
            raise TypeError(f'Image type not supported [{img.dtype}]')

    @traitlets.validate('polygons')
    def validate_polygons(self, proposal):
        """
        Validate correct polygon data

        Valid data types:
            - list of dictionaries with keys: coords, color<optional>, alpha<optional>, size<optional>
            - None (clears)

        Warning:
            The individual data values are not validated, as that would slow down everything!
            It is up to the user to ensure that the values have the following types:
                - coords: 2D numpy array with X,Y coordinates
                - color: RGB string
                - alpha: 2 character HEX string (00-FF)
                - size: Integer
        """
        poly = proposal['value']
        self.hovered = None
        self.clicked = None
        if poly is None:
            return poly

        if isinstance(poly, list):
            for p in poly:
                if ('coords' not in p) or (not isinstance(p['coords'], list)):
                    raise ValueError('polygon coords attribute not a np.ndarray or missing')
            return poly
        else:
            raise TypeError(f'Polygons should be a list<dict> [{type(poly)}]')

    @traitlets.validate('color')
    def _validate_color(self, proposal):
        """ Validate correct color type

        Valid data types:
            - RGB String: '#XXXXXX' or 'rgb(xx, xx, xx)' (any JS compatible RGB string)
        """
        col = proposal['value']
        if not isinstance(col, str):
            raise TypeError(f'Color should be an RGB string [{type(col)}]')
        return col

    @traitlets.validate('alpha')
    def _validate_alpha(self, proposal):
        """ Validate default fill alpha

        Valid types:
            - String: Hex alpha value (00 - ff)
            - Integer: integer alpha (0-255)
            - Float: percentage alpha (0-1)
        """
        return cast_alpha(proposal['value'])

    @traitlets.validate('size')
    def _validate_size(self, proposal):
        """ Validate default border size. """
        size = proposal['value']
        if size < 0:
            raise ValueError('Border size should be bigger or equal than zero [{size}]')
        return size

    def _validate_fx(self, val):
        """ Validate hover/clicked attributes.
        These attributes should be dicts that can contain color, alpha and/or size values
        """
        if 'color' in val:
            val['color'] = self._validate_color({'value': val['color']})
        else:
            val['color'] = None

        if 'alpha' in val:
            val['alpha'] = self._validate_alpha({'value': val['alpha']})
        else:
            val['alpha'] = None

        if 'size' in val:
            val['size'] = self._validate_size({'value': val['size']})
        else:
            val['size'] = None

        return val
