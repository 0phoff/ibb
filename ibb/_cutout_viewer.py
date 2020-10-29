from math import floor, ceil
from pathlib import Path
from PIL import Image
import numpy as np
import brambox as bb
import ipywidgets
from brambox.util._visual import setup_boxes
from ._image_canvas import *
from ._util import cast_alpha, box_to_coords, mask_to_coords

__all__ = ['CutoutViewer']


class CutoutViewer(ipywidgets.VBox):
    """ This widget can visualize a brambox dataset as bounding boxes drawn on top of the images as cutouts.
    It's arguments work a lot like brambox's `brambox.util.BoxDrawer` class.

    Args:
        images (callable or dict-like object): A way to get the image or path to the image from the image labels in the dataframe
        boxes (pandas.DataFrame): Bounding boxes to draw
        label (pandas.Series): Label to write above the boxes; Default **class_label (confidence)**
        color (pandas.Series): Color to use for drawing; Default **every class_label will get its own color, up to 10 labels**
        size (pandas.Series): Thickness of the border of the bounding boxes; Default **3**
        alpha (pandas.Series): Alpha fill value of the bounding boxes; Default **50**
        info (boolean): Whether or not to show a side-pane with extra information about the clicked bounding box; Default **False**
        draw_box (int): Whether or to draw the bounding box or mask (see Note); Default **mask if available, else bounding box**
        pad (int, float or tuple of 2 int/float): Padding to add around the width and height (see Note); Default **10**
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
        The padding property can be one of 4 possible types:
        - *int*             : A fixed pixel padding is added to each side.
        - *float*           : A fixed pixel padding is added to each side. The padding is computed as ``pad*box_width``.
        - *(int, int)*      : Separate pixel padding for the width and height.
        - *(float, float)*  : Separate pixel padding for the width and height. The padding is computed as ``(pad[0]*box_width, pad[1]*box_height)``.

        Note that the padding is clipped inside of the image boundaries.

    Note:
        The `draw_box` variable can be one of 3 different values:

        - 0 : Draw nothing
        - 1 : Draw bounding boxes
        - 2 : Draw segmentation masks (only available if 'segmentation' column is found in boxes)

        You can also change this value by clicking on the "toggle box/mask" button.
    """
    def __init__(self, images, boxes, label=True, color=None, size=None, alpha=50, info=False, draw_box=None, pad=10, width=800, height=500, **kwargs):
        self.images = images
        self.info = info
        self._draw_box_max = 3 if 'segmentation' in boxes.columns else 2
        self.draw_box = self._draw_box_max - 1
        self._draw_box_tt = ['none', 'box', 'mask']
        self._img = None
        if isinstance(pad, int):
            self.pad = (pad, pad)
        else:
            self.pad = pad

        # Setup boxes
        self.boxes = setup_boxes(boxes, label, color, size)
        self.boxes.color = 'rgb' + self.boxes.color.astype(str)
        if 'alpha' not in self.boxes.columns:
            self.boxes['alpha'] = alpha
            self.boxes['alpha'] = self.boxes['alpha'].apply(cast_alpha)
        self.boxes['boxcoords'] = self.boxes.apply(box_to_coords, axis=1)
        if self._draw_box_max == 3:
            self.boxes['maskcoords'] = self.boxes.apply(mask_to_coords, axis=1)
        
        # Create elements
        width += 2
        height += 2
        info_width = 200
        if self.info:
            cvs_width = width - info_width
        else:
            cvs_width = width

        self.lbl_img = ipywidgets.HTML(placeholder='image', layout=ipywidgets.Layout(height='28px'))
        self.lbl_box = ipywidgets.HTML(placeholder='label', layout=ipywidgets.Layout(height='28px'))
        self.btn_prev = ipywidgets.Button(icon='backward')
        self.btn_next = ipywidgets.Button(icon='forward')
        self.btn_save = ipywidgets.Button(icon='fa-picture-o', tooltip='save image', layout=ipywidgets.Layout(width='34px'))
        self.btn_info = ipywidgets.Button(icon='fa-bars', tooltip='toggle info', layout=ipywidgets.Layout(width='34px'))
        self.btn_box = ipywidgets.Button(icon='fa-square-o', tooltip=f'toggle box/mask [{self._draw_box_tt[self.draw_box]}]', layout=ipywidgets.Layout(width='34px'))
        self.inp_idx = ipywidgets.IntText(0, layout=ipywidgets.Layout(width='75px'))
        self.lbl_len = ipywidgets.HTML(f'/ {len(self.boxes)-1}')
        self.cvs_img = ImageCanvas(width=cvs_width, height=height, **kwargs)
        self.lbl_info = ipywidgets.HTML(placeholder='info',
            layout=ipywidgets.Layout(overflow_y='auto', padding='2px', width=str(info_width+1)+'px', height=str(height)+'px', border='1px solid lightgray', margin='0 0 0 -1px')
        )
        
        # Place elements
        w = str(min(200, width//2)) + 'px'
        items = [
            ipywidgets.HBox([
                self.lbl_img,
                ipywidgets.HBox([self.lbl_box, self.btn_save, self.btn_box, self.btn_info])
            ], layout=ipywidgets.Layout(width=str(width)+'px', justify_content='space-between')),
            ipywidgets.HBox(
                [self.cvs_img, self.lbl_info] if self.info else [self.cvs_img],
                layout=ipywidgets.Layout(width=str(width)+'px')
            ),
            ipywidgets.HBox([
                ipywidgets.HBox([self.btn_prev, self.btn_next], layout=ipywidgets.Layout(width=w)),
                ipywidgets.HBox([self.inp_idx, self.lbl_len], layout=ipywidgets.Layout(width=w, justify_content='flex-end'))
            ], layout=ipywidgets.Layout(justify_content='space-between', width=str(width)+'px'))
        ]
        
        super().__init__(items, layout=ipywidgets.Layout(width='100%', align_items='center'))
        
        # Actions
        self.inp_idx.observe(self.observe_index, 'value')
        self.btn_prev.on_click(self.click_prev)
        self.btn_next.on_click(self.click_next)
        self.btn_save.on_click(self.click_save)
        self.btn_box.on_click(self.click_box)
        self.btn_info.on_click(self.click_info)
        
        # Start
        self.draw(0)
        
    def draw(self, index):
        self.cvs_img.image = None
        box = self.boxes.iloc[index].copy()
        lbl = str(box.image)

        # Setup labels
        self.lbl_img.value = lbl
        self.lbl_box.value = box.label
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
            
        # Image
        if self._img is not None and self._img[0] == lbl:
            img = self._img[1]
        else:
            if callable(self.images):
                img = self.images(lbl)
            else:
                img = self.images[lbl]
            if isinstance(img, (str, Path)):
                img = np.asarray(Image.open(img))

            self._img = (lbl, img)

        if isinstance(self.pad, float):
            pad = int(self.pad*box.width)
            pad = (pad, pad)
        else:
            pad = tuple(int(p*box) if isinstance(p, float) else p for p, box in zip(self.pad, list(box[['width', 'height']].values)))

        x0 = floor(max(0, box.x_top_left - pad[0]))
        y0 = floor(max(0, box.y_top_left - pad[1]))
        x1 = ceil(min(img.shape[1], box.x_top_left + box.width + pad[0]))
        y1 = ceil(min(img.shape[0], box.y_top_left + box.height + pad[1]))

        self.cvs_img.image = img[y0:y1, x0:x1]
        if self.draw_box == 2:
            box = box[['maskcoords', 'color', 'size', 'alpha']].to_dict()
            box['coords'] = box.pop('maskcoords').copy()
            box['coords'][:, 0] -= x0
            box['coords'][:, 1] -= y0
            box['coords'] = box['coords'].tolist()
            self.cvs_img.polygons = [box]
        elif self.draw_box == 1:
            box = box[['boxcoords', 'color', 'size', 'alpha']].to_dict()
            box['coords'] = box.pop('boxcoords').copy()
            box['coords'][:, 0] -= x0
            box['coords'][:, 1] -= y0
            box['coords'] = box['coords'].tolist()
            self.cvs_img.polygons = [box]
        else:
            self.cvs_img.polygons = None
    
    def observe_index(self, change):
        idx = max(0, min(change['new'], len(self.boxes)-1))
        self.inp_idx.value = idx
        self.draw(idx)       

    def click_prev(self, btn):
        idx = self.inp_idx.value - 1
        if idx < 0:
            self.inp_idx.value = len(self.boxes) - 1
        else:
            self.inp_idx.value = idx
             
    def click_next(self, btn):
        idx = self.inp_idx.value + 1
        if idx >= len(self.boxes):
            self.inp_idx.value = 0
        else:
            self.inp_idx.value = idx

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
