"""Asset loading helpers: resolve paths inside assets/ and cache loaded images."""

import os

import pygame

from core import config as C

_image_cache = {}


def asset_path(name):
    """Absolute path to a file inside the assets/ directory."""
    return os.path.join(C.ASSETS_DIR, name)


def load_image(name, alpha=True):
    """Load (and cache) an image from assets/. Must be called after the display
    is created so convert()/convert_alpha() have a pixel format to target."""
    if name not in _image_cache:
        img = pygame.image.load(asset_path(name))
        _image_cache[name] = img.convert_alpha() if alpha else img.convert()
    return _image_cache[name]
