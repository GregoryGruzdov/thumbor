#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


from thumbor.filters import BaseFilter, filter_method
from PIL import Image
import numpy as np


def find_inscribed_opaque_rectangle(rotated_image):
    """
    Given a rotated PIL Image (in RGBA mode), find the largest rectangle
    (as defined by the following simple heuristic) where every pixel is fully opaque.

    Steps:
      1. Find the coordinate of the highest (smallest y) opaque pixel in the first column.
      2. On that row, find the rightmost opaque pixel.
      3. On that column, find the lowest (largest y) opaque pixel.
      4. On that row, find the leftmost opaque pixel.
      5. Use these coordinates as the rectangle.

    Returns: (x_left, y_top, x_right, y_bottom) such that image.crop((x_left, y_top, x_right, y_bottom))
             gives the desired region.
    """
    # Convert image to a NumPy array and extract the alpha channel.
    # (Assumes that rotated_image is already in RGBA.)
    arr = np.array(rotated_image)
    alpha = arr[:, :, 3]  # (height, width)

    height, width = alpha.shape

    # Step 1: Find the highest opaque pixel in the first column (column index 0)
    col0 = alpha[:, 1]
    y_candidates = np.where(col0 == 255)[0]
    if len(y_candidates) == 0:
        print(1)
        return None  # no opaque pixel in first column
    y_top = y_candidates[0]

    # Step 2: On row y_top, find the rightmost opaque pixel.
    row_y_top = alpha[y_top, :]
    x_candidates = np.where(row_y_top == 255)[0]
    if len(x_candidates) == 0:
        print(2)
        return None
    x_right = x_candidates[-1]

    # Step 3: On column x_right, find the lowest opaque pixel.
    col_x_right = alpha[:, x_right]
    y_candidates = np.where(col_x_right == 255)[0]
    if len(y_candidates) == 0:
        print(3)
        return None
    y_bottom = y_candidates[-1]

    # Step 4: On row y_bottom, find the leftmost opaque pixel.
    row_y_bottom = alpha[y_bottom, :]
    x_candidates = np.where(row_y_bottom == 255)[0]
    if len(x_candidates) == 0:
        print(4)
        return None
    x_left = x_candidates[0]

    # Step 5: (Optional refinement) Ensure that the top row (y_top) is the one where at x_left we also see opaque.
    # For simplicity, we assume the rectangle is (x_left, y_top, x_right, y_bottom).
    # You might further check that pixel (x_left, y_top) is opaque; if not, adjust.

    return (x_left, y_top, x_right + 1, y_bottom + 1)


class Filter(BaseFilter):
    @filter_method(BaseFilter.DecimalNumber, BaseFilter.Boolean, BaseFilter.String)
    async def rotate(self, angle, expand=False, bgcolor="white"):
        if not isinstance(angle, (int, float)):
            return
        # Ensure we are in RGBA mode to handle transparency properly
        pil_image = self.engine.image.convert("RGBA")
        if expand:
            self.engine.image = pil_image.rotate(angle, resample=Image.BICUBIC, expand=expand, fillcolor=bgcolor)
        else:
            rotated_image = pil_image.rotate(angle, resample=Image.BICUBIC, expand=expand, fillcolor=(0, 0, 0, 0))
            rect = find_inscribed_opaque_rectangle(rotated_image)
            self.engine.image = rotated_image.crop(rect)
