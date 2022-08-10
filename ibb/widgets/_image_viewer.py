from pathlib import Path
import numpy as np
from PIL import Image
from ._viewer import Viewer

__all__ = ['ImageViewer']


class ImageViewer(Viewer):
    """
    This widget is a basic image browser.

    Args:
        images (list-like):
            This list-like (iterable with len) should contain your images (See Note below)
        lambda_image (function, optional):
            This function gets the value from the `images` and should return a numpy array that is readable by the ImageCanvas; Default **See Note**
        **kwargs (dict):
            Extra keyword arguments that can be passed to :class:`~ibb.widgets.Viewer`

    Note:
        The default `lambda_image` function can work with 2 types of data:

        - String/Path: If the images contain strings/Path-objects, it will consider them as paths to images and try to read them.
        - Other: If it is anything else it will pass the data to the `ImageCanvas` as follows: **np.asaray(<DATA>)**
    """
    def __init__(self, images, get_image_fn=None, **kwargs):
        self.images = images

        if get_image_fn is not None:
            self.get_img = get_image_fn

        super().__init__(
            total=len(self.images),
            **kwargs,
        )

    def get_img(self, img):
        if isinstance(img, (str, Path)):
            return np.asarray(Image.open(img))
        else:
            return np.asarray(img)

    def on_index(self, change):
        """ """
        img = self.images[change['new']]

        if isinstance(img, (str, Path)):
            self.header[0].value = str(img)
        else:
            self.header[0].value = ''

        self.main[0].image = self.get_img(img)
