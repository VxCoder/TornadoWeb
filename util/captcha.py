# -*- coding: utf-8 -*-

import random, string, math

from PIL import Image, ImageDraw, ImageFont


class Captcha():
    
    StringBase = string.digits + string.ascii_letters
    
    def __init__(self, width, height, line_num, line_width, font_color, back_color, font_type):
        
        self._width = width
        self._height = height
        
        self._line_num = line_num
        self._line_width = line_width
        
        self._font_color = font_color
        self._back_color = back_color
        
        self._font_type = font_type
        self._font_size = round(min(width, height) * 0.618)
        
        self._code, self._image = self._create_image()
        
    def _create_image(self):
        
        chars = random.sample(self.StringBase, 4)
        
        img_code = r''.join(chars)
        txt_code = r''.join(chars).lower()
        
        image = Image.new(r'RGB', (self._width, self._height), self._back_color)
        
        draw = ImageDraw.Draw(image)
        
        for index in range(1, self._line_num):
            pos_begin = (random.randint(0, self._width), random.randint(0, self._height))
            pos_end = (random.randint(0, self._width), random.randint(0, self._height))
            draw.line((pos_begin, pos_end), self._font_color, random.randint(*self._line_width))
        
        font = ImageFont.truetype(self._font_type, self._font_size)
        
        font_width, font_height = font.getsize(img_code)
        offset_x = random.randint(0, abs(self._width - font_width))
        offset_y = random.randint(0, abs(self._height - font_height))
        
        draw.text((offset_x, offset_y), img_code, self._font_color, font)
        
        return txt_code, image
    
    @property
    def code(self):
        
        return self._code
    
    def save(self, stream):
        
        self._image.save(stream, r'PNG')

