from math import floor, ceil
from pathlib import Path
import numpy as np
from PIL import Image
from ._brambox_viewer import BramboxViewer

__all__ = ['CutoutViewer']


class CutoutViewer(BramboxViewer):
    """
    This widget can visualize a brambox dataset as bounding boxes drawn on top of the images. |br|
    Its arguments work a lot like :class:`brambox.util.BoxDrawer`.
    The main difference with :class:`~ibb.BramboxViewer` is that each polygon is shown as a separate cutout.

    Args:
        images (callable or dict-like object):
            A way to get the image or path to the image from the image labels in the dataframe
        boxes (pandas.DataFrame):
            Bounding boxes to draw
        pad (int, float or tuple of 2 int/float):
            Padding to add around the width and height (see Note); Default **10**
        label (pandas.Series):
            Label to write above the boxes; Default **class_label (confidence)**
        color (pandas.Series):
            Color to use for drawing; Default **every class_label will get its own color, up to 10 labels**
        size (pandas.Series):
            Thickness of the border of the bounding boxes; Default **3**
        alpha (pandas.Series):
            Alpha fill value of the bounding boxes; Default **00**
        **kwargs (dict):
            Extra keyword arguments that will be passed to :class:`~ibb.widgets.Viewer`

    Note:
        If the `images` argument is callable, the image or path to the image will be retrieved in the following way:
        >>> image = images(image_label)

        Otherwise the image or path is retrieved as:
        >>> image = images[image_label]

    Note:
        The padding property can be one of 4 possible types:
        - *int*             : A fixed pixel padding is added to each side.
        - *float*           : A fixed pixel padding is added to each side. The padding is computed as ``pad*box_width``.
        - *(int, int)*      : Separate pixel padding for the width and height.
        - *(float, float)*  : Separate pixel padding for the width and height. The padding is computed as ``(pad[0]*box_width, pad[1]*box_height)``.

        Note that the padding is clipped inside of the image boundaries.

    Note:
        The `label`, `color`, `size` and `alpha` arguments can also be tacked on to the `boxes` dataframe as columns.
        They can also be a single value, which will then be used for each bounding box. |br|
        Basically, as long as you can assign the value as a new column to the dataframe, it will work.
    """
    def __init__(self, images, boxes, pad=10, label=True, color=None, size=3, alpha=0, **kwargs):
        if isinstance(pad, int):
            self.pad = (pad, pad)
        else:
            self.pad = pad

        self.cache = {'label': None}

        if 'total' not in kwargs:
            kwargs['total'] = len(boxes)

        super().__init__(
            images,
            boxes,
            label,
            color,
            size,
            alpha,
            control_name='object',
            **kwargs,
        )

    def __init_side__(self, kwargs):
        self.conf_enabled = False
        return []

    def get_data(self, index):
        # Get data
        box = self.boxes.iloc[index]
        label = box['image']
        if self.cache['label'] == label:
            img = self.cache['img']
        else:
            img = self.images(label) if callable(self.images) else self.images[label]
            if isinstance(img, (str, Path)):
                img = np.asarray(Image.open(img))
            else:
                img = np.asarray(img)

            self.cache = {
                'label': label,
                'img': img,
            }

        # Compute crop
        if isinstance(self.pad, float):
            pad_x = int(self.pad * box.width)
            pad_y = pad_x
        else:
            pad_x = self.pad[0] if isinstance(self.pad[0], int) else int(self.pad[0] * box.width)
            pad_y = self.pad[1] if isinstance(self.pad[1], int) else int(self.pad[1] * box.height)

        x0 = floor(max(0, box.x_top_left - pad_x))
        y0 = floor(max(0, box.y_top_left - pad_y))
        x1 = ceil(min(img.shape[1], box.x_top_left + box.width + pad_x))
        y1 = ceil(min(img.shape[0], box.y_top_left + box.height + pad_y))
        self.cache['pad'] = [x0, y0]

        # Set self.clicked to automatically click on new cutout
        self.clicked = box

        return label, img[y0:y1, x0:x1], self.boxes.iloc[index:index + 1]

    def draw_boxes(self, boxes):
        boxes['boxcoords'] = boxes['boxcoords'].apply(lambda c: c - self.cache['pad'])
        if 'maskcoords' in boxes:
            boxes['maskcoords'] = boxes['maskcoords'].apply(lambda c: c - self.cache['pad'])

        super().draw_boxes(boxes)
