import ipywidgets
from pathlib import Path
import numpy as np
from PIL import Image
from ._image_canvas import *

__all__ = ['ImageViewer']
        

class ImageViewer(ipywidgets.VBox):
    """ This widget is a basic image browser.

    Args:
        images (list-like): This list-like (iterable with len) should contain your images (See Note below)
        lambda_image (function, optional): This function gets the value from the `images` and should return a numpy array that is readable by the ImageCanvas; Default **See Note**
        width (Integer): Width of the widget in pixels; Default **750**
        height (Integer): Height of the widget in pixels; Default **500**
        enlarge (Boolean): Whether to enlarge an image to take up the most space in the canvas; Default **True**

    Note:
        The default `lambda_image` function can work with 2 types of data:
            - String/Path: If the images contain strings/Path-objects, it will consider them as paths to images and read them.
            - Other: If it is anything else it will pass the data to the `ImageCanvas` as follows: **np.assaray(<DATA>)**
    """
    def __init__(self, images, lambda_image=None, width=750, height=500, enlarge=True):
        self.images = images
        if lambda_image is not None:
            self.get_img = lambda_image
        
        # Create elements
        self.lbl_img = ipywidgets.HTML(placeholder='label', layout=ipywidgets.Layout(height='28px'))
        self.btn_prev = ipywidgets.Button(icon='backward')
        self.btn_next = ipywidgets.Button(icon='forward')
        self.inp_idx = ipywidgets.IntText(0, layout=ipywidgets.Layout(width='75px'))
        self.lbl_len = ipywidgets.HTML(f'/ {len(self.images)-1}')
        self.cvs_img = ImageCanvas(width=width, height=height, enlarge=enlarge, enable_rect=False)
        
        # Place elements
        w = str(min(200, width//2)) + 'px'
        super().__init__([
            self.lbl_img,
            self.cvs_img,
            ipywidgets.HBox([
                ipywidgets.HBox([self.btn_prev, self.btn_next], layout=ipywidgets.Layout(width=w)),
                ipywidgets.HBox([self.inp_idx, self.lbl_len], layout=ipywidgets.Layout(width=w, justify_content='flex-end'))
            ], layout=ipywidgets.Layout(justify_content='space-between', width=str(width)+'px', align_self='center'))
        ])
        
        # Actions
        self.inp_idx.observe(self.observe_index, 'value')
        self.btn_prev.on_click(self.click_prev)
        self.btn_next.on_click(self.click_next)
        
        # Start
        self.index = 0
            
    @property
    def index(self):
        return self.inp_idx.value;
        
    @index.setter
    def index(self, idx):
        idx = max(0, min(idx, len(self.images)-1))
        self._index = idx
        self.inp_idx.value = idx
        
        img = self.images[idx]
        if isinstance(img, (str, Path)):
            self.set_title(str(img))
        else:
            self.lbl_img.value = ''
        self.cvs_img.image = self.get_img(img)
    
    def get_img(self, img):
        if isinstance(img, (str, Path)):
            return np.asarray(Image.open(img))
        else:
            return np.asarray(img)
    
    def set_title(self, string):
        self.lbl_img.value = f'<div style="text-align: center">{string}</div>'
        
    def observe_index(self, change):
        self.index = change['new']

    def click_prev(self, btn):
        idx = self.index - 1
        if idx < 0:
            self.index = len(self.images) - 1
        else:
            self.index = idx
             
    def click_next(self, btn):
        idx = self.index + 1
        if idx >= len(self.images):
            self.index = 0
        else:
            self.index = idx
