Itop
====

Top notch IPython widgets for deep learning and computer vision.
These widgets help with doing computer vision research in IPython Notebooks.


## Widget List
You can find more information about each widget by checking its doc-string:
```python
import itop

# Python
help(itop.<WIDGET_NAME>)

# Alternative in Notebook
?itop.<WIDGET_NAME>
```

- **ImageCanvas**: Barebones widget to draw numpy arrays as images and rectangles. Use this to create your own widgets.
- **ImageViewer**: Image list browser.
- **BramboxViewer**: Brambox dataset browser. Browse through your annotations or detections for visual inspection.


## Installation

To install use pip:

**WIP** This package is still under development and thus not yet released on PyPi!

```bash
> pip install itop
> jupyter nbextension enable --py --sys-prefix itop
```


For a development installation (requires npm),

```bash
> git clone https://github.com/0phoff/itop.git
> cd itop 
> pip install -e .
> jupyter nbextension install --py --symlink --sys-prefix itop
> jupyter nbextension enable --py --sys-prefix itop
```
