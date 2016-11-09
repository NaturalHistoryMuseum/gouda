# This file is not called zbar.py to avoid collision with the zbar package

from gouda.barcode import Barcode
from gouda.gouda_error import GoudaError
from gouda.util import debug_print

from PIL import Image

try:
    from pyzbar import pyzbar
except ImportError:
    pyzbar = None


class ZbarEngine(object):
    """Decode using the zbar library

    http://sourceforge.net/projects/zbar/
    https://pypi.python.org/pypi/pyzbar
    """
    def __init__(self):
        if not self.available():
            raise GoudaError('zbar unavailable')

    @classmethod
    def available(cls):
        return pyzbar is not None

    def decode_file(self, path):
        return self(Image.open(str(path)))

    def __call__(self, img):
        # Decode barcodes in img using pyzbar
        return [Barcode(r.type, r.data) for r in pyzbar.decode(img)]
