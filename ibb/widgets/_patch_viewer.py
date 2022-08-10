from math import ceil
from pathlib import Path
import numpy as np
from PIL import Image
from ._brambox_viewer import BramboxViewer
from ._patch_controls import PatchControls

try:
    from pygeos import box as pygeos_box
except ImportError:
    pygeos_box = None

__all__ = ['PatchViewer']


class PatchViewer(BramboxViewer):
    """
    This widget works in a similar way as the :class:`~ibb.BramboxViewer`,
    but is meant to be used with large images and splits it in smaller patches with overlap. |br|
    It's arguments work a lot like brambox's `brambox.util.BoxDrawer` class.

    Args:
        images (callable or dict-like object):
            A way to get the image or path to the image from the image labels in the dataframe
        boxes (pandas.DataFrame):
            Bounding boxes to draw
        patch (int or tuple of int):
            Width and height of the patch
        overlap (int, or tuple of int, optional):
            width and height overlap between patches; Default **computed automatically**
        label (pandas.Series):
            Label to write above the boxes; Default **class_label (confidence)**
        color (pandas.Series):
            Color to use for drawing; Default **every class_label will get its own color, up to 10 labels**
        size (pandas.Series):
            Thickness of the border of the bounding boxes; Default **3**
        alpha (pandas.Series):
            Alpha fill value of the bounding boxes; Default **00**
        pad (int, float or tuple of 2 int/float):
            Padding to add around the width and height (see Note); Default **10**
        **kwargs (dict):
            Extra keyword arguments that will be passed to :class:`~ibb.widgets.Viewer`

    Note:
        If the `images` argument is callable, the image or path to the image will be retrieved in the following way:
        >>> image = images(image_label)

        Otherwise the image or path is retrieved as:
        >>> image = images[image_label]

    Note:
        The overlap property can be one of 3 possible types:
        - *int*         : A fixed pixel overlap is added to each side.
        - *(int, int)*  : Separate pixel overlap for the width and height.
        - None          : Automatically compute overlap so all patches contain full image data

    Note:
        The `label`, `color`, `size` and `alpha` arguments can also be tacked on to the `boxes` dataframe as columns.
        They can also be a single value, which will then be used for each bounding box. |br|
        Basically, as long as you can assign the value as a new column to the dataframe, it will work.
    """
    def __init__(self, images, boxes, patch, overlap=None, label=True, color=None, size=3, alpha=0, **kwargs):
        self.patch = (patch, patch) if isinstance(patch, int) else tuple(patch[:2])
        self.cache = {'label': None, 'img': None}

        # Get image data
        self.img_data = []
        patch_w, patch_h = self.patch
        for label in boxes.image.cat.categories:
            img = images(label) if callable(images) else images[label]
            if isinstance(img, (str, Path)):
                img_w, img_h = Image.open(img).size
            else:
                img_h, img_w = np.asarray(img).shape[:2]

            if overlap is None:
                num_w = ceil(img_w / patch_w)
                ov_w = ceil(((patch_w * num_w) - img_w) / (num_w - 1))
                num_h = ceil(img_h / patch_h)
                ov_h = ceil(((patch_h * num_h) - img_h) / (num_h - 1))
                self.img_data.append((num_w * num_h, num_w, num_h, ov_w, ov_h))
            else:
                if isinstance(overlap, int):
                    ov_w, ov_h = overlap, overlap
                else:
                    ov_w, ov_h = overlap[:2]

                num_w = ceil(img_w / (patch_w - ov_w) - 1)
                num_h = ceil(img_h / (patch_h - ov_h) - 1)
                self.img_data.append((num_w * num_h, num_w, num_h, ov_w, ov_h))

        kwargs['total'] = sum(data[0] for data in self.img_data)
        kwargs['control_total'] = len(boxes.image.cat.categories)
        super().__init__(
            images,
            boxes,
            label,
            color,
            size,
            alpha,
            **kwargs,
        )

        self.add_class('patch-viewer')

    def __init_footer__(self, kwargs):
        w_img_ctrl, w_index_ctrl = super().__init_footer__(kwargs)
        w_patch_ctrl = PatchControls(total_width=self.img_data[0][1], total_height=self.img_data[0][2])

        def _patch_to_index(change):
            patch_index = w_index_ctrl.index
            for _image_index, imgdata in enumerate(self.img_data):
                if patch_index >= imgdata[0]:
                    patch_index -= imgdata[0]
                else:
                    break

            w_index_ctrl.index = (
                sum(data[0] for data in self.img_data[:_image_index]) +
                w_patch_ctrl.total_width * w_patch_ctrl.index_height +
                w_patch_ctrl.index_width
            )

        def _index_to_patch(change):
            patch_index = change['new']
            for _image_index, imgdata in enumerate(self.img_data):
                if patch_index >= imgdata[0]:
                    patch_index -= imgdata[0]
                else:
                    break

            with self.hold_trait_notifications():
                w_patch_ctrl.total_width = self.img_data[_image_index][1]
                w_patch_ctrl.total_height = self.img_data[_image_index][2]
                w_patch_ctrl.index_width = patch_index % self.img_data[_image_index][1]
                w_patch_ctrl.index_height = patch_index // self.img_data[_image_index][1]

        w_patch_ctrl.observe(_patch_to_index, ['index_height', 'index_width'])
        w_index_ctrl.observe(_index_to_patch, 'index')

        return [w_img_ctrl, w_patch_ctrl, w_index_ctrl]

    def control_to_index(self, value):
        return sum(data[0] for data in self.img_data[:value])

    def index_to_control(self, value):
        for _image_index, imgdata in enumerate(self.img_data):
            if value >= imgdata[0]:
                value -= imgdata[0]
            else:
                break
        return _image_index

    def get_data(self, patch_index):
        # Reset image (clears screen before loading new image, so it does not look like the process is stuck)
        # This causes a slight flicker, but as this class is usually used with huge images that take a while to load, I prefer this behaviour
        self.main[0].image = None

        # Get current image and patch index
        for _image_index, imgdata in enumerate(self.img_data):
            if patch_index >= imgdata[0]:
                patch_index -= imgdata[0]
            else:
                break

        # Get patch coordinates
        idx_w = patch_index % imgdata[1]
        idx_h = patch_index // imgdata[1]
        x0 = idx_w * (self.patch[0] - imgdata[3])
        x1 = x0 + self.patch[0]
        y0 = idx_h * (self.patch[1] - imgdata[4])
        y1 = y0 + self.patch[1]

        # Get data
        label = str(self.boxes.image.cat.categories[_image_index])

        # Get Image
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
        self.cache['pad'] = [x0, y0]

        # Get boxes
        boxes = self.boxes[self.boxes.image == label].copy()

        if self.draw_box_max == 3:
            boundary = pygeos_box(x0, y0, x1, y1)
            boxes = boxes[boxes.segmentation.apply(lambda s: s.intersects(boundary))]
        else:
            boxes = boxes[
                ((boxes.x_top_left <= x1) & ((boxes.x_top_left + boxes.width) >= x0)) &
                ((boxes.y_top_left <= y1) & ((boxes.y_top_left + boxes.height) >= y0))
            ]

        return f'{label} (x={idx_w}, y={idx_h})', img[y0:y1, x0:x1], boxes

    def draw_boxes(self, boxes):
        boxes['boxcoords'] = boxes['boxcoords'].apply(lambda c: c - self.cache['pad'])
        if 'maskcoords' in boxes:
            boxes['maskcoords'] = boxes['maskcoords'].apply(lambda c: c - self.cache['pad'])

        super().draw_boxes(boxes)
