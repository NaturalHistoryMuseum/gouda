import subprocess
import tempfile

from pathlib import Path

import cv2

from gouda import config
from gouda.barcode import Barcode
from gouda.gouda_error import GoudaError
from gouda.util import debug_print


class LibDMTXEngine(object):
    """Decode Data Matrix barcodes using the libdmtx decoder
    """

    DTMXREAD = getattr(config, 'LIBDMTX_DTMXREAD', None)

    def __init__(self, timeout_ms=300):
        if not self.available():
            raise GoudaError('libdmtx unavailable')
        elif timeout_ms<0:
            raise GoudaError('Bad timeout [{0}]'.format(timeout_ms))
        else:
            self.timeout_ms = timeout_ms

    @classmethod
    def available(cls):
        return cls.DTMXREAD and cls.DTMXREAD.is_file()

    def decode_file(self, path):
        dmtx = [str(self.DTMXREAD),
                '--newline',
                '--stop-after=1',
                '--milliseconds={0}'.format(self.timeout_ms),
                str(path),
               ]
        # dmtxread returns a non-zero exit code if no barcodes are
        # found - this is bone-headed.
        dmtxread = subprocess.Popen(dmtx,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdoutdata, stderrdata = dmtxread.communicate()
        if stderrdata:
            raise ValueError(stderrdata)
        elif stdoutdata:
            # TODO Coordinates?
            stdoutdata = stdoutdata.strip().split('\n')
            return [Barcode('Data Matrix', l) for l in stdoutdata]
        else:
            return []

    def __call__(self, img):
        # Decode data matrix barcodes in img using dmtxread
        with tempfile.NamedTemporaryFile(suffix='.png') as img_temp:
            debug_print('Writing temp file [{0}] for dmtxread'.format(img_temp.name))
            cv2.imwrite(img_temp.name, img)
            return self.decode_file(img_temp.name)
