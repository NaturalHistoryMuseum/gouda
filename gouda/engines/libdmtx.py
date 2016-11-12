import subprocess
import tempfile

from PIL import Image

from gouda import config
from gouda.barcode import Barcode
from gouda.gouda_error import GoudaError
from gouda.util import debug_print

try:
    from pylibdmtx import pylibdmtx
except ImportError:
    pylibdmtx = None



class LibDMTXEngine(object):
    """Decode Data Matrix barcodes using the libdmtx decoder via pylibdmtx
    """

    def __init__(self, timeout_ms=300, max_count=None):
        if not self.available():
            raise GoudaError('libdmtx unavailable')

        self.timeout_ms = timeout_ms
        self.max_count = max_count

    @classmethod
    def available(cls):
        return pylibdmtx is not None

    def decode_file(self, path):
        return self(Image.open(str(path)))

    def __call__(self, img):
        res = pylibdmtx.decode(
            img, timeout=self.timeout_ms, max_count=self.max_count
        )

        return [Barcode('Data Matrix', r.data) for r in res]
