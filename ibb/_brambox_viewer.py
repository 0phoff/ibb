import ipywidgets
from pathlib import Path
from PIL import Image
import numpy as np
import brambox as bb
from ._image_canvas import *
from ._util import cast_alpha, box_to_coords, mask_to_coords

__all__ = ['BramboxViewer']


class BramboxViewer(ipywidgets.VBox):
    """ This widget can visualize a brambox dataset as bounding boxes drawn on top of the images.
    It's arguments work a lot like brambox's `brambox.util.BoxDrawer` class.

    Args:
        images (callable or dict-like object): A way to get the image or path to the image from the image labels in the dataframe
        boxes (pandas.DataFrame): Bounding boxes to draw
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
    def __init__(self, images, boxes, label=True, color=None, size=None, alpha=None, show_empty=True, info=False, draw_box=None, width=800, height=500, **kwargs):
        self._draw_box_max = 3 if 'segmentation' in boxes.columns else 2
        self.draw_box = self._draw_box_max - 1
        self._draw_box_tt = ['none', 'box', 'mask']

        self.bbdrawer = bb.util.BoxDrawer(images, boxes, label, color, size, show_empty)
        self.bbdrawer.draw = self.draw
        self.bbdrawer.boxes.color = 'rgb' + self.bbdrawer.boxes.color.astype(str)
        if 'alpha' not in self.bbdrawer.boxes.columns:
            if alpha is not None:
                self.bbdrawer.boxes['alpha'] = alpha
                self.bbdrawer.boxes['alpha'] = self.bbdrawer.boxes['alpha'].apply(cast_alpha)
            else:
                self.bbdrawer.boxes['alpha'] = '00'
        self.bbdrawer.boxes['boxcoords'] = self.bbdrawer.boxes.apply(box_to_coords, axis=1)
        if self._draw_box_max == 3:
            self.bbdrawer.boxes['maskcoords'] = self.bbdrawer.boxes.apply(mask_to_coords, axis=1)
        
        self.info = info
        self.clicked = None
        self.conf = 'confidence' in self.bbdrawer.boxes
        
        # ImageCanvas arguments
        if 'hover_style' not in kwargs:
            kwargs['hover_style'] = {'alpha': .5}
        if 'click_style' not in kwargs:
            kwargs['click_style'] = {'size': self.bbdrawer.boxes['size'].max() + 2}
        
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
        self.btn_prev = ipywidgets.Button(icon='backward')
        self.btn_next = ipywidgets.Button(icon='forward')
        self.btn_save = ipywidgets.Button(icon='fa-picture-o', tooltip='save image', layout=ipywidgets.Layout(width='34px'))
        self.btn_info = ipywidgets.Button(icon='fa-bars', tooltip='toggle info', layout=ipywidgets.Layout(width='34px'))
        self.btn_box = ipywidgets.Button(icon='fa-square-o', tooltip=f'toggle box/mask [{self._draw_box_tt[self.draw_box]}]', layout=ipywidgets.Layout(width='34px'))
        self.inp_idx = ipywidgets.IntText(0, layout=ipywidgets.Layout(width='75px'))
        self.lbl_len = ipywidgets.HTML(f'/ {len(self.bbdrawer)-1}')
        self.cvs_img = ImageCanvas(width=cvs_width, height=height, **kwargs)
        self.lbl_info = ipywidgets.HTML(placeholder='info',
            layout=ipywidgets.Layout(overflow_y='auto', padding='2px', width=str(info_width+1)+'px', height=str(height)+'px', border='1px solid lightgray', margin='0 0 0 -1px')
        )
        self.slide_conf = ipywidgets.IntSlider(value=0, min=0, max=100, step=1, orientation='vertical', readout=True, continuous_update=False,
            layout=ipywidgets.Layout(width=str(slide_width)+'px', height=str(height)+'px', margin='0', padding='2px')
        )
        
        # Place elements
        w = str(min(200, width//2)) + 'px'
        ww = str(width-slide_width if self.conf else width) + 'px'
        margin = '0 0 0 -' + str(slide_width) + 'px' if self.conf else '0'

        midSection = [self.cvs_img]
        if self.info:
            midSection.append(self.lbl_info)
        if self.conf:
            midSection.append(self.slide_conf)

        items = [
            ipywidgets.HBox([
                self.lbl_img,
                ipywidgets.HBox([self.lbl_box, self.btn_save, self.btn_box, self.btn_info])
            ], layout=ipywidgets.Layout(width=ww, margin=margin, justify_content='space-between')),
            ipywidgets.HBox(
                midSection,
                layout=ipywidgets.Layout(width=str(width)+'px')
            ),
            ipywidgets.HBox([
                ipywidgets.HBox([self.btn_prev, self.btn_next], layout=ipywidgets.Layout(width=w)),
                ipywidgets.HBox([self.inp_idx, self.lbl_len], layout=ipywidgets.Layout(width=w, justify_content='flex-end'))
            ], layout=ipywidgets.Layout(justify_content='space-between', width=ww, margin=margin))
        ]
        
        super().__init__(items, layout=ipywidgets.Layout(width='100%', align_items='center'))
        
        # Actions
        self.inp_idx.observe(self.observe_index, 'value')
        self.cvs_img.observe(self.observe_hover, 'hovered')
        self.cvs_img.observe(self.observe_click, 'clicked')
        self.btn_prev.on_click(self.click_prev)
        self.btn_next.on_click(self.click_next)
        self.btn_save.on_click(self.click_save)
        self.btn_box.on_click(self.click_box)
        self.btn_info.on_click(self.click_info)
        if self.conf:
            self.slide_conf.observe(self.observe_conf, 'value')
        
        # Start
        self.bbdrawer[0]
        
    def draw(self, lbl, img, boxes):
        self.cvs_img.image = None
        self.lbl_img.value = str(lbl)
        
        if isinstance(img, (str, Path)):
            self.cvs_img.image = np.asarray(Image.open(img))
        else:
            self.cvs_img.image = np.asarray(img)
            
        self.img_boxes = boxes
        if self.conf:
            self.boxes = boxes[boxes.confidence >= self.slide_conf.value/100]
        else:
            self.boxes = boxes

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
    
    def observe_index(self, change):
        idx = max(0, min(change['new'], len(self.bbdrawer)-1))
        self.inp_idx.value = idx
        self.bbdrawer[idx]        
        
    def observe_hover(self, change):
        val = change['new']
        if val is None:
            if self.clicked is None:
                self.lbl_box.value = ''
            else:
                self.lbl_box.value = self.boxes.iat[self.clicked, self.boxes.columns.get_loc('label')]
        else:
            self.lbl_box.value = self.boxes.iat[val, self.boxes.columns.get_loc('label')]
    
    def observe_click(self, change):
        self.clicked = change['new']
        self.observe_hover(change)
        
        if self.clicked is None:
            self.lbl_info.value = ''
        else:
            box = self.boxes.iloc[self.clicked].copy()

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

        self.boxes = self.img_boxes[self.img_boxes.confidence >= threshold/100]
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

    def click_prev(self, btn):
        idx = self.inp_idx.value - 1
        if idx < 0:
            self.inp_idx.value = len(self.bbdrawer) - 1
        else:
            self.inp_idx.value = idx
             
    def click_next(self, btn):
        idx = self.inp_idx.value + 1
        if idx >= len(self.bbdrawer):
            self.inp_idx.value = 0
        else:
            self.inp_idx.value = idx

    def click_save(self, btn):
        self.cvs_img.save = True

    def click_info(self, btn):
        self.info = not self.info

        if self.info:
            self.cvs_img.width -= 200
            self.children[1].children = (self.cvs_img, self.lbl_info, self.slide_conf) if self.conf else (self.cvs_img, self.lbl_info)
        else:
            self.cvs_img.width += 200
            self.children[1].children = (self.cvs_img, self.slide_conf) if self.conf else (self.cvs_img, )

    def click_box(self, btn):
        self.draw_box = (self.draw_box + 1) % self._draw_box_max
        btn.tooltip = f'toggle box/mask [{self._draw_box_tt[self.draw_box]}]'
        self.bbdrawer[int(self.inp_idx.value)]        
