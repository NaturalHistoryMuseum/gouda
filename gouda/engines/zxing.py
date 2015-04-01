import os
import subprocess
import tempfile

from pathlib import Path

import cv2


from gouda.barcode import Barcode
from gouda.java import java
from gouda.gouda_error import GoudaError
from gouda.util import debug_print


# TODO LH Support all types of barcode that zxing does

class ZxingEngine(object):
    """Decode Data Matrix barcodes using the zxing java library

    https://github.com/zxing/zxing
    """

    JARS = ['zxing/core-3.1.0.jar',
            'zxing/javase-3.1.0.jar',
            'decode_data_matrix/decode_data_matrix.jar']
    JARS = [java.JAR_PATH / p for p in JARS]

    def __init__(self):
        if not self.available():
            raise GoudaError('zxing unavailable')

    @classmethod
    def available(cls):
        return java.available() and all([p.is_file() for p in cls.JARS])

    def decode_file(self, path):
        if not self.available():
            raise GoudaError('zxing unavailable')
        else:
            args = [str(java.JAVA),
                    '-cp', os.pathsep.join(map(str, self.JARS)),
                    'decode_data_matrix',
                    str(path)]
            dmtxread = subprocess.Popen(args,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
            stdoutdata, stderrdata = dmtxread.communicate()
            if stderrdata:
                raise GoudaError('zxing error [{0}]'.format(repr(stderrdata)))
            else:
                # TODO Coordinates?
                stdoutdata = [l for l in stdoutdata.strip().split('\n') if l]
                return [Barcode('Data Matrix', l) for l in stdoutdata]

    def __call__(self, img):
        img_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        try:
            debug_print('Writing temp file [{0}] for zxing'.format(img_temp.name))
            cv2.imwrite(img_temp.name, img)
            return self.decode_file(img_temp.name)
        finally:
            # TODO LH Logic here?
            img_temp.close()
            os.unlink(img_temp.name)
