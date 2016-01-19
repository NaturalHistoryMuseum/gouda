import subprocess
import tempfile

from pathlib import Path

import cv2
import numpy as np

from PIL import Image

from gouda import config
from gouda.barcode import Barcode
from gouda.gouda_error import GoudaError
from gouda.util import debug_print

try:
    from pydmtx import DataMatrix
except ImportError:
    DataMatrix = None

# Two interfaces to libdmtx - WrapperLibDMTXEngine uses pydmtx
# SubprocessLibDMTXEngine uses the dmtxread command-line tool
# WrapperLibDMTXEngine preferred - both kept here for reference

class WrapperLibDMTXEngine(object):
    """Decode Data Matrix barcodes using the libdmtx decoder via pydmtx
    """

    def __init__(self, timeout_ms=300, max_count=1):
        if not self.available():
            raise GoudaError('libdmtx unavailable')

        self.timeout_ms = timeout_ms
        self.max_count = max_count

    @classmethod
    def available(cls):
        return DataMatrix is not None

    def decode_file(self, path):
        return self(cv2.imread(str(path)))

    def __call__(self, img):
        d = DataMatrix(timeout=self.timeout_ms, max_count=self.max_count)

        # PIL RGB image from BGR np.ndarray
        # http://stackoverflow.com/a/4661652/1773758
        img = Image.fromarray(np.roll(img, 1, axis=-1))
        img = img.convert('RGB')

        res = d.decode(img.size[0], img.size[1], buffer(img.tobytes()))

        res = [None] * d.count()
        for i in xrange(0, d.count()):
            res[i] = Barcode('Data Matrix', d.message(1+i))
        return res


class SubprocessLibDMTXEngine(object):
    """Decode Data Matrix barcodes using the libdmtx decoder via dmtxread
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
        return cls.DTMXREAD is not None and cls.DTMXREAD.is_file()

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

# Use the more more elegant and flexible solution
LibDMTXEngine = WrapperLibDMTXEngine
