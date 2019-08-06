import ipywidgets
from pathlib import Path
from PIL import Image
import brambox as bb
from ._image_canvas import *
from ._util import cast_alpha

__all__ = ['BramboxViewer']


class IBoxDrawer(bb.util.BoxDrawer):
    """ Temporarily copy new __getitem__ and draw functions, as they will be in V2.1.1

    TODO:
        The plan is to only release this package to PyPi once Brambox V2.1.1 gets released and then remove this class.
    """
    def __getitem__(self, idx):
        if isinstance(idx, int):
            lbl = self.image_labels[idx]
        else:
            lbl = idx

        if callable(self.images):
            img = self.images(lbl)
        else:
            img = self.images[lbl]

        return self.draw(lbl, img, self.boxes[self.boxes.image == lbl])

    def draw(self, lbl, img, boxes):
        raise NotImplementedError('Actual function will be overridden')


class BramboxViewer(ipywidgets.VBox):
    """ This widget can visualize a brambox dataset.
    It's arguments work a lot like brambox's `brambox.util.BoxDrawer` class.

    Args:
        images (callable or dict-like object): A way to get the image or path to the image from the image labels in the dataframe
        boxes (pandas.DataFrame): Bounding boxes to draw
        label (pandas.Series): Label to write above the boxes; Default **nothing**
        color (pandas.Series): Color to use for drawing; Default **every class_label will get its own color, up to 10 labels**
        size (pandas.Series): Thickness of the border of the bounding boxes; Default **3**
        alpha (pandas.Series): Alpha fill value of the bounding boxes; Default **00**
        show_empty (boolean): Whether to also show images without bounding boxes; Default **True**
        info (boolean): Whether or not to show a side-pane with extra information about the clicked bounding box; Default **False**
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
    """
    def __init__(self, images, boxes, label=True, color=None, size=None, alpha=None, show_empty=True, info=False, width=800, height=500, **kwargs):
        self.bbdrawer = IBoxDrawer(images, boxes, label, color, size, show_empty)
        self.bbdrawer.draw = self.draw
        self.bbdrawer.boxes.color = 'rgb' + self.bbdrawer.boxes.color.astype(str)
        if 'alpha' not in self.bbdrawer.boxes.columns:
            if alpha is not None:
                self.bbdrawer.boxes['alpha'] = alpha
                self.bbdrawer.boxes['alpha'] = self.bbdrawer.boxes['alpha'].apply(cast_alpha)
            else:
                self.bbdrawer.boxes['alpha'] = '00'
        
        self.info = info
        self.clicked = None
        
        if 'hover_style' not in kwargs:
            kwargs['hover_style'] = {'alpha': .5}
        if 'click_style' not in kwargs:
            kwargs['click_style'] = {'size': self.bbdrawer.boxes['size'].max() + 2}
        
        # Create elements
        if self.info:
            info_width = 200
            cvs_width = width - info_width
            self.lbl_info = ipywidgets.HTML(
                placeholder='info',
                layout=ipywidgets.Layout(overflow_y='auto', padding='2px', width=str(info_width+1)+'px', height=str(height+2)+'px', border='1px solid lightgray', margin='0 0 0 -1px')
            )
        else:
            cvs_width = width
                
        self.lbl_img = ipywidgets.HTML(placeholder='image', layout=ipywidgets.Layout(height='28px'))
        self.lbl_box = ipywidgets.HTML(placeholder='label', layout=ipywidgets.Layout(height='28px'))
        self.btn_prev = ipywidgets.Button(icon='backward')
        self.btn_next = ipywidgets.Button(icon='forward')
        self.inp_idx = ipywidgets.IntText(0, layout=ipywidgets.Layout(width='75px'))
        self.lbl_len = ipywidgets.HTML(f'/ {len(self.bbdrawer)-1}')
        self.cvs_img = ImageCanvas(width=cvs_width, height=height, **kwargs)
        
        # Place elements
        w = str(min(200, width//2)) + 'px'
        items = [
            ipywidgets.HBox([self.lbl_img, self.lbl_box], layout=ipywidgets.Layout(width=str(width)+'px', justify_content='space-between')),
            None,
            ipywidgets.HBox([
                ipywidgets.HBox([self.btn_prev, self.btn_next], layout=ipywidgets.Layout(width=w)),
                ipywidgets.HBox([self.inp_idx, self.lbl_len], layout=ipywidgets.Layout(width=w, justify_content='flex-end'))
            ], layout=ipywidgets.Layout(justify_content='space-between', width=str(width)+'px'))
        ]
        
        if self.info:
            items[1] = ipywidgets.HBox(
                [self.cvs_img, self.lbl_info],
                layout=ipywidgets.Layout(width=str(width)+'px')
            )
        else:
            items[1] = self.cvs_img
        
        super().__init__(items, layout=ipywidgets.Layout(width='100%', align_items='center'))
        
        # Actions
        self.inp_idx.observe(self.observe_index, 'value')
        self.btn_prev.on_click(self.click_prev)
        self.btn_next.on_click(self.click_next)
        self.cvs_img.observe(self.observe_hover, 'hovered')
        self.cvs_img.observe(self.observe_click, 'clicked')
        
        # Start
        self.bbdrawer[0]
        
    def draw(self, lbl, img, boxes):
        self._lbl_img.value = lbl
        
        if isinstance(img, (str, Path)):
            self._cvs_img.image = np.asarray(Image.open(img))
        else:
            self._cvs_img.image = np.asarray(img)
            
        self.boxes = boxes
        self.cvs_img.rectangles = boxes[['x_top_left', 'y_top_left', 'width', 'height', 'color', 'size', 'alpha']].to_dict('records')
    
    def observe_index(self, change):
        idx = max(0, min(change['new'], len(self.bbdrawer)-1))
        self.inp_idx.value = idx
        self.bbdrawer[idx]        
        
    def observe_hover(self, change):
        val = change['new']
        if val is None:
            if self.info or self.clicked is None:
                self.lbl_box.value = ''
            else:
                self.lbl_box.value = self.boxes.iat[self.clicked, self.boxes.columns.get_loc('label')]
        else:
            self.lbl_box.value = self.boxes.iat[val, self.boxes.columns.get_loc('label')]
    
    def observe_click(self, change):
        self.clicked = change['new']
        self.observe_hover(change)
        
        if self.info:
            if self.clicked is None:
                self.lbl_info.value = ''
            else:
                box = self.boxes.iloc[self.clicked].copy()

                s = '<dl>'
                columns = sorted(box.index.difference(['image', 'color', 'size', 'label', 'alpha', 'x_top_left', 'y_top_left', 'width', 'height'])) + ['x_top_left', 'y_top_left', 'width', 'height']
                for col in columns:
                    s += f'<dt>{col}</dt><dd style="text-align:right; margin-bottom:5px">{box[col]}</dd>'
                s += '</dl>'
                self.lbl_info.value = s

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
