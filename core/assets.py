"""Asset loading helpers: resolve paths inside assets/ and cache loaded images."""

import os

import pygame

from core import config as C

_image_cache = {}
_scaled_cache = {}


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


def load_scaled(name, box, alpha=True):
    """Load an image scaled to fit a ``box``x``box`` square, keeping aspect ratio.
    Results are cached per (name, box) so the smoothscale runs only once."""
    key = (name, box)
    if key not in _scaled_cache:
        img = load_image(name, alpha)
        w, h = img.get_size()
        s = min(box / w, box / h)
        size = (max(1, round(w * s)), max(1, round(h * s)))
        _scaled_cache[key] = pygame.transform.smoothscale(img, size)
    return _scaled_cache[key]
