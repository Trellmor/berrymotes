# --------------------------------------------------------------------
#
# Copyright (C) 2013 Marminator <cody_y@shaw.ca>
# Copyright (C) 2013 pao <patrick.oleary@gmail.com>
# Copyright (C) 2013 Daniel Triendl <daniel@pew.cc>
#
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# COPYING for more details.
#
# --------------------------------------------------------------------

from .abstract_emotes_processor import AbstractEmotesProcessorFactory, AbstractEmotesProcessor
from ..filenameutils import FileNameUtils
from PIL import Image
from StringIO import StringIO
import os

import logging

logger = logging.getLogger(__name__)


class BasicEmotesProcessorFactory(AbstractEmotesProcessorFactory):
    def __init__(self, single_emotes_filename=None):
        super(BasicEmotesProcessorFactory, self).__init__()
        self.single_emotes_filename = single_emotes_filename

    def new_processor(self, scraper=None, image_url=None, group=None):
        return BasicEmotesProcessor(scraper=scraper,
                                    image_url=image_url,
                                    group=group,
                                    single_emotes_filename=self.single_emotes_filename)


class BasicEmotesProcessor(AbstractEmotesProcessor, FileNameUtils):
    def __init__(self, scraper=None, image_url=None, group=None, single_emotes_filename=None):
        AbstractEmotesProcessor.__init__(self, scraper=scraper, image_url=image_url, group=group)

        self.single_emotes_filename = single_emotes_filename
        self.image_data = None
        self.image = None


    def process_group(self):
        self.load_image(self.get_file_path(self.image_url, self.scraper.cache_dir))
        AbstractEmotesProcessor.process_group(self)

    def process_emote(self, emote):
        file_name = self.single_emotes_filename.format(emote['sr'], max(emote['names'], key=len))
        if not os.path.exists(file_name):
            try:
                cropped = self.extract_single_image(emote, self.image)
                if not cropped:
                    return

                if not cropped.getbbox():
                    logger.warn("{} might be empty".format(file_name))

                if not os.path.exists(os.path.dirname(file_name)):
                    try:
                        os.makedirs(os.path.dirname(file_name))
                    except OSError:
                        pass

                f = open(file_name, 'wb')
                cropped.save(f)
                f.close()
            except Exception, e:
                logger.exception(e)
                logger.error("Emote file: {}".format(file_name))

    def load_image(self, image_file):
        f = open(image_file, 'rb')
        self.image_data = f.read()
        f.close()

        self.image = Image.open(StringIO(self.image_data))

    def extract_single_image(self, emote, image):
        x = 0
        y = 0
        width = emote['width']
        height = emote['height']
        if 'background-position' in emote:
            if len(emote['background-position']) > 0:
                x = int(emote['background-position'][0].strip('px').strip('%'))
                if emote['background-position'][0].endswith('%'):
                    x = width * x / 100;

            if len(emote['background-position']) > 1:
                y = int(emote['background-position'][1].strip('px').strip('%'))
                if emote['background-position'][1].endswith('%'):
                    y = height * y / 100;

        # Convert css coordinates to image coordiantes
        if x > 0:
            # Positives values appear from the left side of the image
            x = image.size[0] - x
        else:
            # Negative values are converted to positive
            x *= -1;

        # If they exceed the image, shift them down, because css background images repeat
        while x >= image.size[0]:
            x -= image.size[0]

        if y > 0:
            y = image.size[1] - y
        else:
            y *= -1;

        while y >= image.size[1]:
            y -= image.size[1]

        # If the crop area equals the image, return it
        if x == 0 and width == image.size[0] and y == 0 and height == image.size[1]:
            return image

        # If the crop area fits inside the image, return the cropped image
        if x + width < image.size[0] and y + height < image.size[1]:
            return image.crop((x, y, x + width, y + height))

        if x + width > image.size[0] and y + height > image.size[1]:
            logger.warn("Emote {}, SR {}: Both width and height exceed image.size".format(max(emote['names'], key=len), emote['sr']))

        single_image = Image.new(image.mode, (width, height))
        if image.mode in ['P', 'L']:
            palette = image.getpalette()
            if palette:
                single_image.putpalette(image.getpalette())
                if 'transparency' in image.info:
                    single_image.info['transparency'] = image.info['transparency']

        # Crop to image borders
        crop_width = width
        if x + width > image.size[0]:
            crop_width = image.size[0] - x

        crop_height = height
        if y + height > image.size[1]:
            crop_height = image.size[1] - y

        crop = image.crop((x, y, x + crop_width, y + crop_height))
        # Paste area 1
        single_image.paste(crop, (0, 0, crop_width, crop_height))

        # Wrap around
        crop_x = x
        crop_width = x + width
        paste_x = 0
        if x + width > image.size[0]:
            crop_x = 0
            crop_width = x
            paste_x = crop.size[0]

        crop_y = y
        crop_height = y + height
        paste_y = 0
        if y + height > image.size[1]:
            crop_y = 0
            crop_height = y
            paste_y = crop.size[1]

        crop = image.crop((crop_x, crop_y, crop_width, crop_height))
        # Paste area 2
        single_image.paste(crop, (paste_x, paste_y, paste_x + crop.size[0], paste_y + crop.size[1]))
        return single_image
