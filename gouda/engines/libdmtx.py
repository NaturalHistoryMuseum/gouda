import cv2

from gouda.barcode import Barcode
from gouda.gouda_error import GoudaError
from gouda.util import debug_print

try:
    from pydmtx import DataMatrix
except ImportError:
    DataMatrix = None


class LibDMTXEngine(object):
    """Decode Data Matrix barcodes using the libdmtx decoder
    """

    def __init__(self):
        if not self.available():
            raise GoudaError('libdmtx unavailable')

    @classmethod
    def available(cls):
        return DataMatrix is not None

    def decode_file(self, path):
        return self(cv2.imread(str(path)))

    def __call__(self, img):
        d = DataMatrix()
        d.decode(img.shape[0], img.shape[1], img)
        res = [None] * d.count()
        for i in range(0, d.count()):
            res[i] = Barcode('Data Matrix', d.message(1+i))
        return res
