import numpy as np


def cast_alpha(alpha):
    if isinstance(alpha, str):
        if len(alpha) == 0:
            return '00'
        elif len(alpha) == 1:
            return '0' + alpha
        else:
            return alpha[-2:]
    elif isinstance(alpha, int):
        if not 0 <= alpha <= 255:
            raise ValueError(f'Alpha should be between 0 and 255 [{alpha}]')
        return '%02x' % alpha
    elif isinstance(alpha, float):
        if not 0 <= alpha <= 1:
            raise ValueError(f'Alpha should be between 0 and 1 [{alpha}]')
        return '%02x' % int(alpha * 255)
    else:
        raise TypeError(f'Alpha should be a HEX string, integer or float [{type(alpha)}]')


def box_to_coords(row):
    return np.array([
        [row.x_top_left, row.y_top_left],
        [row.x_top_left + row.width, row.y_top_left],
        [row.x_top_left + row.width, row.y_top_left + row.height],
        [row.x_top_left, row.y_top_left + row.height],
    ])


def mask_to_coords(row):
    if hasattr(row.segmentation, 'exterior'):
        return np.array(row.segmentation.exterior.coords)
    return np.array(row.segmentation.coords)
