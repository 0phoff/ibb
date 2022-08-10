import math
from pathlib import Path
import numpy as np
from PIL import Image
import ipywidgets
from brambox.util._visual import setup_boxes
from ._unlink_box import UnlinkBox
from ._image_canvas import ImageCanvas
from .._util import cast_alpha, box_to_coords, mask_to_coords

try:
    from pygeos import box as pygeos_box
except ImportError:
    pygeos_box = None


__all__ = ['PatchViewer']


class PatchViewer(UnlinkBox):
    """
    This widget works in a similar way as the :class:`~ibb.BramboxViewer`,
    but is meant to be used with large images and splits it in smaller patches with overlap. |br|
    It's arguments work a lot like brambox's `brambox.util.BoxDrawer` class.

    Args:
        images (callable or dict-like object): A way to get the image or path to the image from the image labels in the dataframe
        boxes (pandas.DataFrame): Bounding boxes to draw
        patch (int or tuple of int): Width and height of the patch
        overlap (int, or tuple of int, optional): width and height overlap between patches; Default **computed automatically**
        label (pandas.Series): Label to write above the boxes; Default **class_label (confidence)**
        color (pandas.Series): Color to use for drawing; Default **every class_label will get its own color, up to 10 labels**
        size (pandas.Series): Thickness of the border of the bounding boxes; Default **3**
        alpha (pandas.Series): Alpha fill value of the bounding boxes; Default **00**
        show_empty (boolean): Whether to also show images without bounding boxes; Default **True**
        info (boolean): Whether or not to show a side-pane with extra information about the clicked bounding box; Default **False**
        draw_box (int): Whether or to draw the bounding box or mask (see Note); Default **mask if available, else bounding box**
        width (Integer): Width of the widget in pixels; Default **750**
        height (Integer): Height of the widget in pixels; Default **500**
        **kwargs (dict): Extra keyword arguments that can be passed to the default `ImageCanvas`

    Note:
        If the `images` argument is callable, the image or path to the image will be retrieved in the following way:
        >>> image = images(image_label)

        Otherwise the image or path is retrieved as:
        >>> image = images[image_label]

    Note:
        The `label`, `color`, `size` and `alpha` arguments can also be tacked on to the `boxes` dataframe as columns.
        They can also be a single value, which will then be used for each bounding box. |br|
        Basically, as long as you can assign the value as a new column to the dataframe, it will work.

    Note:
        The `draw_box` variable can be one of 3 different values:

        - 0 : Draw nothing
        - 1 : Draw bounding boxes
        - 2 : Draw segmentation masks (only available if 'segmentation' column is found in boxes)

        You can also change this value by clicking on the "toggle box/mask" button.
    """
    def __init__(self, images, boxes, patch, overlap=None, label=True, color=None, size=3, alpha=0.5, info=False, draw_box=None, width=800, height=500, **kwargs):
        self.images = images
        self.info = info
        self.clicked = None
        self._draw_box_max = 3 if pygeos_box is not None and 'segmentation' in boxes.columns else 2
        self.draw_box = self._draw_box_max - 1
        self._draw_box_tt = ['none', 'box', 'mask']
        self._img = None
        self.patch = (patch, patch) if isinstance(patch, int) else tuple(patch[:2])

        # Setup boxes
        self.boxes = setup_boxes(
            boxes,
            label=label,
            color=color,
            size=size,
            alpha=alpha,
        )
        self.boxes.color = 'rgb' + self.boxes.color.astype(str)
        self.boxes['alpha'] = self.boxes['alpha'].apply(cast_alpha)
        self.boxes['boxcoords'] = self.boxes.apply(box_to_coords, axis=1)
        if self._draw_box_max == 3:
            self.boxes['maskcoords'] = self.boxes.apply(mask_to_coords, axis=1)

        self.conf = 'confidence' in self.boxes

        # Get image patch information
        self._img_data = []
        patch_w, patch_h = self.patch
        for img in self.boxes.image.cat.categories:
            if callable(self.images):
                img = self.images(img)
            else:
                img = self.images[img]

            if isinstance(img, (str, Path)):
                img_w, img_h = Image.open(img).size
            else:
                img_h, img_w = img.shape[:2]

            if overlap is None:
                num_w = math.ceil(img_w / patch_w)
                ov_w = math.ceil(((patch_w * num_w) - img_w) / (num_w - 1))
                num_h = math.ceil(img_h / patch_h)
                ov_h = math.ceil(((patch_h * num_h) - img_h) / (num_h - 1))
                self._img_data.append((num_w * num_h, num_w, num_h, ov_w, ov_h))
            else:
                if isinstance(overlap, int):
                    ov_w, ov_h = overlap, overlap
                else:
                    ov_w, ov_h = overlap[:2]

                num_w = math.ceil(img_w / (patch_w - ov_w) - 1)
                num_h = math.ceil(img_h / (patch_h - ov_h) - 1)
                self._img_data.append((num_w * num_h, num_w, num_h, ov_w, ov_h))

        # ImageCanvas arguments
        if 'hover_style' not in kwargs:
            kwargs['hover_style'] = {'alpha': .5}
        if 'click_style' not in kwargs:
            kwargs['click_style'] = {'size': self.boxes['size'].max() + 2}

        # Create elements
        width += 2
        height += 2
        info_width = 200
        slide_width = 30

        if self.info:
            cvs_width = width - info_width
        else:
            cvs_width = width

        if self.conf:
            cvs_width -= slide_width

        self.lbl_img = ipywidgets.HTML(placeholder='image', layout=ipywidgets.Layout(height='28px'))
        self.lbl_box = ipywidgets.HTML(placeholder='label', layout=ipywidgets.Layout(height='28px'))
        self.lbl_patch = ipywidgets.HTML(placeholder='patch', layout=ipywidgets.Layout(height='28px', width='34px', text_align='center'))
        self.btn_prev_img = ipywidgets.Button(icon='backward', tooltip='previous image')
        self.btn_next_img = ipywidgets.Button(icon='forward', tooltip='next image')
        self.btn_left = ipywidgets.Button(icon='caret-left', layout=ipywidgets.Layout(height='28px', width='34px'))
        self.btn_right = ipywidgets.Button(icon='caret-right', layout=ipywidgets.Layout(height='28px', width='34px'))
        self.btn_up = ipywidgets.Button(icon='caret-up', layout=ipywidgets.Layout(height='28px', width='34px'))
        self.btn_down = ipywidgets.Button(icon='caret-down', layout=ipywidgets.Layout(height='28px', width='34px'))
        self.btn_save = ipywidgets.Button(icon='fa-picture-o', tooltip='save image', layout=ipywidgets.Layout(width='34px'))
        self.btn_info = ipywidgets.Button(icon='fa-bars', tooltip='toggle info', layout=ipywidgets.Layout(width='34px'))
        self.btn_box = ipywidgets.Button(icon='fa-square-o', tooltip=f'toggle box/mask [{self._draw_box_tt[self.draw_box]}]', layout=ipywidgets.Layout(width='34px'))
        self.inp_idx = ipywidgets.IntText(0, layout=ipywidgets.Layout(width='75px'))
        self.lbl_len = ipywidgets.HTML(f'/ {sum(imgdata[0] for imgdata in self._img_data)-1}')
        self.cvs_img = ImageCanvas(width=cvs_width, height=height, **kwargs)
        self.lbl_info = ipywidgets.HTML(
            placeholder='info',
            layout=ipywidgets.Layout(
                overflow_y='auto',
                padding='2px',
                width=str(info_width + 1) + 'px',
                height=str(height) + 'px',
                border='1px solid lightgray',
                margin='0 0 0 -1px',
            ),
        )
        self.slide_conf = ipywidgets.IntSlider(
            value=0, min=0, max=100, step=1,
            orientation='vertical', readout=True, continuous_update=False,
            layout=ipywidgets.Layout(width=str(slide_width) + 'px', height=str(height) + 'px', margin='0', padding='2px'),
        )

        # Place elements
        w = str(min(200, width // 3)) + 'px'
        ww = str(width - slide_width if self.conf else width) + 'px'
        margin = '0 0 0 -' + str(slide_width) + 'px' if self.conf else '0'

        midSection = [self.cvs_img]
        if self.info:
            midSection.append(self.lbl_info)
        if self.conf:
            midSection.append(self.slide_conf)

        items = [
            ipywidgets.HBox([
                self.lbl_img,
                ipywidgets.HBox([self.lbl_box, self.btn_save, self.btn_box, self.btn_info]),
            ], layout=ipywidgets.Layout(width=ww, margin=margin, justify_content='space-between')),
            ipywidgets.HBox(
                midSection,
                layout=ipywidgets.Layout(width=str(width) + 'px'),
            ),
            ipywidgets.HBox([
                ipywidgets.HBox([self.btn_prev_img, self.btn_next_img], layout=ipywidgets.Layout(width=w)),
                ipywidgets.HBox([
                    self.btn_left,
                    ipywidgets.VBox([self.btn_up, self.lbl_patch, self.btn_down], layout=ipywidgets.Layout(justify_content='center', align_items='center')),
                    self.btn_right,
                ], layout=ipywidgets.Layout(width=w, justify_content='center', align_items='center')),
                ipywidgets.HBox([self.inp_idx, self.lbl_len], layout=ipywidgets.Layout(width=w, justify_content='flex-end')),
            ], layout=ipywidgets.Layout(width=ww, margin=margin, justify_content='space-between', align_items='center')),
        ]

        super().__init__(items, type='vbox', layout=ipywidgets.Layout(width='100%', align_items='center'))

        # Actions
        self.inp_idx.observe(self.observe_index, 'value')
        self.cvs_img.observe(self.observe_hover, 'hovered')
        self.cvs_img.observe(self.observe_click, 'clicked')
        self.btn_left.on_click(self.click_left)
        self.btn_right.on_click(self.click_right)
        self.btn_up.on_click(self.click_up)
        self.btn_down.on_click(self.click_down)
        self.btn_prev_img.on_click(self.click_prev_img)
        self.btn_next_img.on_click(self.click_next_img)
        self.btn_save.on_click(self.click_save)
        self.btn_box.on_click(self.click_box)
        self.btn_info.on_click(self.click_info)

        # Start
        self.draw(0)

    def draw(self, index):
        self.cvs_img.image = None

        # Get current image index
        idx = self.inp_idx.value
        for _img_idx, imgdata in enumerate(self._img_data):
            if idx >= imgdata[0]:
                idx -= imgdata[0]
            else:
                break

        # Get patch coordinates
        idx_w = idx % imgdata[1]
        idx_h = idx // imgdata[1]
        x0 = idx_w * (self.patch[0] - imgdata[3])
        x1 = x0 + self.patch[0]
        y0 = idx_h * (self.patch[1] - imgdata[4])
        y1 = y0 + self.patch[1]
        self.lbl_patch.value = f'<div style="text-align: center; width: 100%">{idx_w},{idx_h}</div>'

        # Image
        lbl = str(self.boxes.image.cat.categories[_img_idx])
        if self._img is not None and self._img[0] == lbl:
            img = self._img[1]
        else:
            self.lbl_img.value = f'{lbl} ({imgdata[1]-1},{imgdata[2]-1})'
            if callable(self.images):
                img = self.images(lbl)
            else:
                img = self.images[lbl]
            if isinstance(img, (str, Path)):
                img = np.asarray(Image.open(img))

            self._img = (lbl, img)
        self.cvs_img.image = img[y0:y1, x0:x1]

        # Boxes
        self.patch_all_boxes = self.boxes[self.boxes.image == lbl].copy()
        if self._draw_box_max == 3:
            boundary = pygeos_box(x0, y0, x1, y1)
            self.patch_all_boxes = self.patch_all_boxes[self.patch_all_boxes.segmentation.apply(lambda s: s.intersects(boundary))]
        else:
            self.patch_all_boxes = self.patch_all_boxes[
                ((self.patch_all_boxes.x_top_left <= x1) & ((self.patch_all_boxes.x_top_left + self.patch_all_boxes.width) >= x0)) &
                ((self.patch_all_boxes.y_top_left <= y1) & ((self.patch_all_boxes.y_top_left + self.patch_all_boxes.height) >= y0))
            ]

        if self.conf:
            self.patch_boxes = self.patch_all_boxes[self.patch_all_boxes.confidence >= self.slide_conf.value / 100]
        else:
            self.patch_boxes = self.patch_all_boxes

        # Draw
        if self.draw_box == 2:
            bb = self.patch_boxes[['color', 'size', 'alpha']].copy()
            bb['coords'] = self.patch_boxes.maskcoords.apply(lambda c: (c - (x0, y0)).tolist())
            self.cvs_img.polygons = bb.to_dict('records')
        elif self.draw_box == 1:
            bb = self.patch_boxes[['color', 'size', 'alpha']].copy()
            bb['coords'] = self.patch_boxes.boxcoords.apply(lambda c: (c - (x0, y0)).tolist())
            self.cvs_img.polygons = bb.to_dict('records')
        else:
            self.cvs_img.polygons = None

    def observe_index(self, change):
        idx = max(0, min(change['new'], sum(imgdata[0] for imgdata in self._img_data) - 1))
        self.inp_idx.value = idx
        self.draw(idx)

    def observe_hover(self, change):
        val = change['new']
        if val is None:
            if self.clicked is None:
                self.lbl_box.value = ''
            else:
                self.lbl_box.value = self.patch_boxes.iat[self.clicked, self.patch_boxes.columns.get_loc('label')]
        else:
            self.lbl_box.value = self.patch_boxes.iat[val, self.patch_boxes.columns.get_loc('label')]

    def observe_click(self, change):
        self.clicked = change['new']
        self.observe_hover(change)

        if self.clicked is None:
            self.lbl_info.value = ''
        else:
            box = self.patch_boxes.iloc[self.clicked].copy()

            s = '<dl>'
            columns = sorted(box.index.difference(['image', 'color', 'size', 'label', 'alpha', 'x_top_left', 'y_top_left', 'width', 'height', 'boxcoords', 'maskcoords'])) + ['x_top_left', 'y_top_left', 'width', 'height']
            for col in columns:
                if col == 'segmentation':
                    numcoords = len(box[col].exterior.coords) if hasattr(box[col], 'exterior') else len(box[col].coords)
                    s += f'<dt>{col}</dt><dd style="text-align:right; margin-bottom:5px">{type(box[col]).__name__} ({numcoords - 1})</dd>'
                else:
                    s += f'<dt>{col}</dt><dd style="text-align:right; margin-bottom:5px">{box[col]}</dd>'
            s += '</dl>'
            self.lbl_info.value = s

    def observe_conf(self, change):
        threshold = change['new']
        if change['old'] == threshold:
            return

        self.patch_boxes = self.patch_all_boxes[self.patch_boxes.confidence >= threshold / 100]
        if self.draw_box == 2:
            bb = self.boxes[['color', 'size', 'alpha']].copy()
            bb['coords'] = self.boxes.maskcoords.apply(lambda c: c.tolist())
            self.cvs_img.polygons = bb.to_dict('records')
        elif self.draw_box == 1:
            bb = self.boxes[['color', 'size', 'alpha']].copy()
            bb['coords'] = self.boxes.boxcoords.apply(lambda c: c.tolist())
            self.cvs_img.polygons = bb.to_dict('records')
        else:
            self.cvs_img.polygons = None

    def click_left(self, btn):
        # Get current image index
        idx = self.inp_idx.value
        for imgdata in self._img_data:
            if idx >= imgdata[0]:
                idx -= imgdata[0]
            else:
                break

        if idx > 0:
            self.inp_idx.value -= 1

    def click_right(self, btn):
        # Get current image index
        idx = self.inp_idx.value
        for imgdata in self._img_data:
            if idx >= imgdata[0]:
                idx -= imgdata[0]
            else:
                break

        if idx < imgdata[0] - 1:
            self.inp_idx.value += 1

    def click_up(self, btn):
        # Get current image index
        idx = self.inp_idx.value
        for imgdata in self._img_data:
            if idx >= imgdata[0]:
                idx -= imgdata[0]
            else:
                break

        if (idx // imgdata[1]) > 0:
            self.inp_idx.value -= imgdata[1]
        elif idx > 0:
            self.inp_idx.value += imgdata[1] * (imgdata[2] - 1) - 1

    def click_down(self, btn):
        # Get current image index
        idx = self.inp_idx.value
        for imgdata in self._img_data:
            if idx >= imgdata[0]:
                idx -= imgdata[0]
            else:
                break

        if (idx // imgdata[1]) < imgdata[2] - 1:
            self.inp_idx.value += imgdata[1]
        elif idx < imgdata[0] - 1:
            self.inp_idx.value += 1 - (imgdata[1] * (imgdata[2] - 1))

    def click_prev_img(self, btn):
        # Get current image index
        idx = self.inp_idx.value
        for _img_idx, imgdata in enumerate(self._img_data):
            idx -= imgdata[0]
            if idx < 0:
                break

        # Compute previous image index
        _img_idx -= 1
        if _img_idx < 0:
            _img_idx = len(self._img_data) - 1

        self.inp_idx.value = sum(imgdata[0] for imgdata in self._img_data[:_img_idx])

    def click_next_img(self, btn):
        # Get current image index
        idx = self.inp_idx.value
        for _img_idx, imgdata in enumerate(self._img_data):
            idx -= imgdata[0]
            if idx < 0:
                break

        # Compute next image index
        _img_idx += 1
        if _img_idx >= len(self._img_data) - 1:
            _img_idx = 0

        self.inp_idx.value = sum(imgdata[0] for imgdata in self._img_data[:_img_idx])

    def click_save(self, btn):
        self.cvs_img.save = True

    def click_info(self, btn):
        self.info = not self.info

        if self.info:
            self.cvs_img.width -= 200
            self.children[1].children = (self.cvs_img, self.lbl_info)
        else:
            self.cvs_img.width += 200
            self.children[1].children = (self.cvs_img,)

    def click_box(self, btn):
        self.draw_box = (self.draw_box + 1) % self._draw_box_max
        btn.tooltip = f'toggle box/mask [{self._draw_box_tt[self.draw_box]}]'
        self.draw(int(self.inp_idx.value))
