from collections.abc import Mapping, Sequence
import numpy as np
import ipywidgets
import brambox as bb
import pandas as pd
from brambox.util._visual import setup_boxes
from ._viewer import Viewer
from .._util import cast_alpha, box_to_coords, mask_to_coords

try:
    import torch
except ImportError:
    torch = None

__all__ = ['TorchViewer']


class TorchViewer(Viewer):
    """
    This widget can visualize a PyTorch dataset as bounding boxes drawn on top of the images. |br|
    Its arguments work a lot like :class:`ibb.BramboxViewer`.

    Args:
        data (torch.utils.data.Dataset):
            PyTorch dataset that should return images and bounding boxes (see Note).
        extract_data (calable):
            Extract image and dataframe from dataset output; Default (First Tensor and DataFrame in Sequence/Mapping)
        label (pandas.Series or callable):
            Label to write above the boxes; Default **class_label (confidence)**
        color (pandas.Series or callable):
            Color to use for drawing; Default **every class_label will get its own color, up to 10 labels**
        size (pandas.Series or callable):
            Thickness of the border of the bounding boxes; Default **3**
        alpha (pandas.Series or callable):
            Alpha fill value of the bounding boxes; Default **00**
        **kwargs (dict):
            Extra keyword arguments that will be passed to :class:`~ibb.widgets.Viewer`

    Note:
        The `label`, `color`, `size` and `alpha` arguments can also be tacked on to the `boxes` dataframe as columns.

        They can also be a single value, which will then be used for each bounding box. |br|
        Basically, as long as you can assign the value as a new column to the dataframe, it will work.

        Finally, if these values are callable, they get called with the boxes dataframe and should return a valid pandas series.
    """
    def __init__(self, data, extract_data=None, label=True, color=None, size=3, alpha=0, **kwargs):
        assert torch is not None, 'PyTorch is required for this widget'

        self.data = data
        self.extract_data = extract_data if callable(extract_data) else default_extract_data
        self.columns = (label, color, size, alpha)

        # Metadata
        self.info = False
        self.clicked = None
        self.draw_box_max = 2
        self.draw_box_text = ['none', 'box', 'mask']
        self.draw_box = self.draw_box_max - 1

        # Example dataframe for setup
        _, _, boxes = self.get_data(0)
        kwargs['_example_boxes'] = boxes
        self.draw_box_max = 3 if 'segmentation' in boxes.columns else 2

        # ImageCanvas arguments
        if 'hover_style' not in kwargs:
            kwargs['hover_style'] = {'alpha': .5}
        if 'click_style' not in kwargs:
            kwargs['click_style'] = {'size': boxes['size'].max() + 2}

        # Widget init
        if 'total' not in kwargs:
            kwargs['total'] = len(self.data)

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
        self.conf_enabled = 'confidence' in kwargs['_example_boxes']
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
        img, boxes = self.extract_data(self.data[index])

        # Image setup
        if isinstance(img, torch.Tensor):
            img = img.cpu().permute(1, 2, 0).contiguous()
        img = np.asarray(img)

        # Dataframe setup
        label, color, size, alpha = self.columns
        if callable(label):
            label = label(boxes)
        if callable(color):
            color = color(boxes)
        if callable(size):
            size = size(boxes)
        if callable(alpha):
            alpha = alpha(boxes)

        boxes = setup_boxes(boxes, label=label, color=color, size=size, alpha=alpha)
        boxes.color = 'rgb' + boxes.color.astype(str)
        boxes['alpha'] = boxes['alpha'].apply(cast_alpha)
        boxes['boxcoords'] = boxes.apply(box_to_coords, axis=1)
        if self.draw_box_max == 3:
            boxes['maskcoords'] = boxes.apply(mask_to_coords, axis=1)

        # Label
        try:
            img_names = boxes['image'].unique()
            assert len(img_names) == 1
            lbl = img_names[0]
        except BaseException:
            lbl = ''

        return lbl, img, boxes

    def draw_boxes(self, boxes):
        if self.draw_box:
            bboxes = boxes[['color', 'size', 'alpha']].copy()
            coord_col = 'maskcoords' if self.draw_box == 2 else 'boxcoords'
            bboxes['coords'] = boxes[coord_col].apply(lambda c: c.tolist())
            bboxes['label'] = boxes['class_label']
            if 'confidence' in boxes:
                bboxes['label'] += boxes['confidence'].apply(lambda num: f' ({num:.2%})')
            self.main[0].polygons = bboxes.to_dict('records')
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


def default_extract_data(output):
    if isinstance(output, torch.Tensor):
        return output, bb.util.new('anno')

    if not isinstance(output, (Sequence, Mapping)):
        raise TypeError(f'Unkown Dataset output: {type(output)}')

    if isinstance(output, Mapping):
        output = output.values()

    img, anno = None, None
    for o in output:
        if img is None and isinstance(o, torch.Tensor):
            img = o.clone()
            if anno is not None:
                break
        elif anno is None and isinstance(o, pd.DataFrame):
            anno = o.copy()
            if img is not None:
                break

    if img is None:
        raise TypeError(f'Could not find Tensor in output: {type(output)}')
    if anno is None:
        anno = bb.util.new('anno')

    return img, anno
