from pathlib import Path
import numpy as np
from PIL import Image
import ipywidgets
from brambox.util._visual import setup_boxes
from ._viewer import Viewer
from .._util import cast_alpha, box_to_coords, mask_to_coords

__all__ = ['BramboxViewer']


class BramboxViewer(Viewer):
    """
    This widget can visualize a brambox dataset as bounding boxes drawn on top of the images. |br|
    Its arguments work a lot like :class:`brambox.util.BoxDrawer`.

    Args:
        images (callable or dict-like object):
            A way to get the image or path to the image from the image labels in the dataframe
        boxes (pandas.DataFrame):
            Bounding boxes to draw
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
        The `label`, `color`, `size` and `alpha` arguments can also be tacked on to the `boxes` dataframe as columns.
        They can also be a single value, which will then be used for each bounding box. |br|
        Basically, as long as you can assign the value as a new column to the dataframe, it will work.
    """
    def __init__(self, images, boxes, label=True, color=None, size=3, alpha=0, **kwargs):
        # Metadata
        self.images = images
        self.info = False
        self.draw_box_max = 3 if 'segmentation' in boxes.columns else 2
        self.draw_box = self.draw_box_max - 1
        self.draw_box_text = ['none', 'box', 'mask']
        self.clicked = None

        # Dataframe setup
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
        if self.draw_box_max == 3:
            self.boxes['maskcoords'] = self.boxes.apply(mask_to_coords, axis=1)

        # ImageCanvas arguments
        if 'hover_style' not in kwargs:
            kwargs['hover_style'] = {'alpha': .5}
        if 'click_style' not in kwargs:
            kwargs['click_style'] = {'size': self.boxes['size'].max() + 2}

        # Widget init
        if 'total' not in kwargs:
            kwargs['total'] = len(self.boxes.image.cat.categories)

        super().__init__(**kwargs)

        # Setup handlers
        self.main[0].observe(self.on_click, 'clicked')
        self.main[0].observe(self.on_poly, 'polygons')

    def __init_header__(self, kwargs):
        btn_layout = ipywidgets.Layout(width='var(--jp-widgets-inline-height)', padding='0')

        w_btn_save = ipywidgets.Button(
            icon='picture-o',
            tooltip='save image',
            layout=btn_layout,
        )
        w_btn_save.on_click(self.on_save)

        w_btn_box = ipywidgets.Button(
            icon='square-o',
            tooltip=f'toggle none/box/mask [{self.draw_box_text[self.draw_box]}]',
            layout=btn_layout,
        )
        w_btn_box.on_click(self.on_box)

        w_btn_info = ipywidgets.Button(
            icon='bars',
            tooltip='toggle info pane',
            layout=btn_layout,
        )
        w_btn_info.on_click(self.on_info)

        return [*super().__init_header__(kwargs), ipywidgets.HBox([w_btn_save, w_btn_box, w_btn_info])]

    def __init_main__(self, kwargs):
        w_info_bar = ipywidgets.HTML(placeholder='info')
        w_info_bar.add_class('ibb-infobar')
        if not self.info:
            w_info_bar.add_class('ibb-hide')

        return [*super().__init_main__(kwargs), w_info_bar]

    def __init_side__(self, kwargs):
        self.conf_enabled = 'confidence' in self.boxes
        if not self.conf_enabled:
            return []

        w_conf_slider = ipywidgets.FloatSlider(
            value=0, min=0, max=1, step=0.01,
            orientation='vertical',
            continuous_update=False,
            readout=True,
            readout_format='.0%',
            tooltip='confidence threshold to filter objects',
            layout=ipywidgets.Layout(width='100%', height='100%', margin='0', padding='4px 2px'),
        )
        w_conf_slider.observe(self.on_threshold, 'value')

        return [w_conf_slider]

    def get_data(self, index):
        label = self.boxes.image.cat.categories[index]
        boxes = self.boxes[self.boxes.image == label].copy()

        img = self.images(label) if callable(self.images) else self.images[label]
        if isinstance(img, (str, Path)):
            img = np.asarray(Image.open(img))
        else:
            img = np.asarray(img)

        return label, img, boxes

    def draw_boxes(self, boxes):
        if self.draw_box:
            bb = boxes[['color', 'size', 'alpha']].copy()
            coord_col = 'maskcoords' if self.draw_box == 2 else 'boxcoords'
            bb['coords'] = boxes[coord_col].apply(lambda c: c.tolist())
            bb['label'] = boxes['class_label']
            if 'confidence' in boxes:
                bb['label'] += boxes['confidence'].apply(lambda num: f' ({num:.2%})')
            self.main[0].polygons = bb.to_dict('records')
        else:
            self.main[0].polygons = None

    def on_index(self, change):
        """ """
        self.header[0].value, self.main[0].image, self.current_all_boxes = self.get_data(change['new'])

        if self.conf_enabled:
            self.current_boxes = self.current_all_boxes[self.current_all_boxes['confidence'] >= self.side[0].value]
        else:
            self.current_boxes = self.current_all_boxes

        self.draw_boxes(self.current_boxes.copy())

    def on_save(self, btn):
        self.main[0].save = True

    def on_box(self, btn):
        self.draw_box = (self.draw_box + 1) % self.draw_box_max
        btn.tooltip = f'toggle none/box/mask [{self.draw_box_text[self.draw_box]}]'
        self.redraw()

    def on_info(self, btn):
        self.info = not self.info
        if self.info:
            self.main[-1].remove_class('ibb-hide')
        else:
            self.main[-1].add_class('ibb-hide')

    def on_click(self, change):
        clicked = change['new']

        if clicked is None:
            self.main[-1].value = ''
            return

        self.clicked = self.current_boxes.iloc[clicked]
        columns = (
            sorted(self.clicked.index.difference([
                'image',
                'color',
                'size',
                'label',
                'alpha',
                'fill',
                'points',
                'x_top_left', 'y_top_left', 'width', 'height',
                'boxcoords', 'maskcoords',
            ])) +
            ['x_top_left', 'y_top_left', 'width', 'height']
        )

        s = '<table>'
        for col in columns:
            if col == 'segmentation':
                numcoords = len(self.clicked[col].exterior.coords) if hasattr(self.clicked[col], 'exterior') else len(self.clicked[col].coords)
                s += f'<tr><td>{col}</td><td>{type(self.clicked[col]).__name__} ({numcoords - 1})</td></tr>'
            else:
                s += f'<tr><td>{col}</td><td>{self.clicked[col]}</td></tr>'
        s += '</table>'

        self.main[-1].value = s

    def on_poly(self, change):
        if self.clicked is None or change['new'] is None:
            return

        # Option 1 : Same object (keep clicked when toggling box/mask)
        index = self.clicked.name
        if index in self.current_boxes.index:
            self.main[0].clicked = self.current_boxes.index.get_loc(index)
            self.clicked = self.current_boxes.loc[index]
            return

        # Option 2 : Object with same class and id (useful in tracking context)
        label = self.clicked['class_label']
        id = self.clicked['id']
        new_clicked = (self.current_boxes['class_label'] == label) & (self.current_boxes['id'] == id)

        if new_clicked.any():
            index = int(new_clicked.values.argmax())
            self.main[0].clicked = index
            self.clicked = self.current_boxes.iloc[index]
            return

        # Default: Reset clicked
        self.clicked = None

    def on_threshold(self, change):
        self.redraw()
