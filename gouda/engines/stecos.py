import subprocess
import tempfile

import cv2

from gouda import config
from gouda.barcode import Barcode
from gouda.gouda_error import GoudaError
from gouda.util import debug_print


class StecosEngine(object):
    """Decode barcodes using the Stecos decoder
    """

    DMREAD = getattr(config, 'STECOS_DMREAD', None)
    READBAR = getattr(config, 'STECOS_READBAR', None)

    def __init__(self, datamatrix):
        if not self.available():
            raise GoudaError('Stecos unavailable')
        else:
            self.command = self.DMREAD if datamatrix else self.READBAR
            self.datamatrix = datamatrix

    @classmethod
    def available(cls):
        return (
            cls.DMREAD is not None and cls.DMREAD.is_file() and cls.READBAR and
            cls.READBAR.is_file()
        )

    def decode_file(self, path):
        dmtx = [
            str(self.command),
            str(path),
        ]
        dmtxread = subprocess.Popen(
            dmtx, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdoutdata, stderrdata = dmtxread.communicate()
        if stderrdata:
            raise ValueError(stderrdata)
        elif stdoutdata:
            # TODO LH Coordinates?
            # Lines are printed in the form Type:Value
            # TODO LH regexp
            res = [l.split(':') for l in stdoutdata.strip().split('\n')]
            return [Barcode(r[0], r[1]) for r in res]
        else:
            return []

    def __call__(self, img):
        # Decode data matrix barcodes in img using dmtxread
        with tempfile.NamedTemporaryFile(suffix='.tiff') as img_temp:
            debug_print(
                'Writing temp file [{0}] for stecos'.format(img_temp.name)
            )
            cv2.imwrite(img_temp.name, img)
            return self.decode_file(img_temp.name)
