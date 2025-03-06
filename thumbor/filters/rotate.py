#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


from thumbor.filters import BaseFilter, filter_method
from PIL import Image

class Filter(BaseFilter):
    @filter_method(BaseFilter.Number, BaseFilter.Boolean, BaseFilter.String)  # Angle, expand flag, and background color
    async def rotate(self, angle, expand=False, bgcolor="white"):
        if not isinstance(angle, (int, float)):
            return

        # Ensure we are in RGBA mode to handle transparency properly
        pil_image = self.engine.image.convert("RGBA")

        # Rotate the image
        rotated_image = pil_image.rotate(angle, resample=Image.BICUBIC, expand=expand)

        # Convert hex background color to RGB
        if bgcolor.startswith("#"):
            bgcolor = Image.new("RGB", (1, 1), bgcolor).getpixel((0, 0))

        # Create a solid background image
        bg_image = Image.new("RGB", rotated_image.size, bgcolor)

        # Extract alpha channel (create a mask)
        mask = rotated_image.split()[3] if "A" in rotated_image.getbands() else None

        # Apply transparency mask if available
        if mask:
            bg_image.paste(rotated_image.convert("RGB"), (0, 0), mask)
        else:
            bg_image.paste(rotated_image.convert("RGB"), (0, 0))

        self.engine.image = bg_image.convert("RGB")
