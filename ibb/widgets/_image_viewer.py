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
        width (Integer, optional):
            width of the widget in pixels; Default **100%**
        height (Integer, optional):
            height of the widget in pixels; Default **500px**

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

    def on_index(self, value):
        img = self.images[value]

        if isinstance(img, (str, Path)):
            self.w_img_label.value = str(img)
        else:
            self.w_img_label.value = ''

        self.w_img_cvs.image = self.get_img(img)
