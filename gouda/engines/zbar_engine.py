# This file is not called zbar.py to avoid collision with the zbar package

import cv2

from gouda.barcode import Barcode
from gouda.gouda_error import GoudaError
from gouda.util import debug_print

try:
    import zbar
except ImportError:
    zbar = None


class ZbarEngine(object):
    # TODO LH Rather that copying files, better to add the relevant include lib
    # paths
    """Decode using the zbar library

http://sourceforge.net/projects/zbar/
https://pypi.python.org/pypi/zbar
"""

    def __init__(self):
        if not self.available():
            raise GoudaError('zbar unavailable')

    @classmethod
    def available(cls):
        return zbar is not None

    def decode_file(self, path):
        return self(cv2.imread(str(path), cv2.IMREAD_GRAYSCALE))

    def __call__(self, img):
        # Decode barcodes in img using zbar
        # https://github.com/ZBar/ZBar/blob/master/python/README
        # https://github.com/herbyme/zbar/blob/master/python/examples/scan_image.py
        scanner = zbar.ImageScanner()
        height,width = img.shape[:2]
        if 'uint8'!=img.dtype or 2!=len(img.shape):
            debug_print('Convert to greyscale for zbar')
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        image = zbar.Image(width, height, 'Y800', img.tostring())
        scanner.scan(image)
        return [Barcode(str(s.type), unicode(s.data, 'utf8')) for s in image]
