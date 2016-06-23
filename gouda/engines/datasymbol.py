import os
import tempfile

import cv2

try:
    from win32com import client as com
    from win32com.client import constants as c
    import win32api
except ImportError:
    com = win32api = c = None

from gouda.barcode import Barcode
from gouda.gouda_error import GoudaError
from gouda.util import debug_print, is_clsid_registered


class DataSymbolEngine(object):
    """Decode using the DataSymbol's BarcodeReader SDK

    BarcodeReader can decode many types of barcodes - currently using it just
    for Data Matrix and Code 128 + Code 129
    """

    CLSID = "BarcodeReader.BarcodeDecoder"

    def __init__(self, datamatrix, n_barcodes=None):
        if not self.available():
            raise GoudaError('Data Symbol unavailable')
        else:
            com.pythoncom.CoInitialize()

            # Tip from stackoverflow about how to access COM constants
            # http://stackoverflow.com/a/21534997/1773758
            self.d = com.gencache.EnsureDispatch(self.CLSID)

            if datamatrix:
                self.d.BarcodeTypes = c.DataMatrix
            else:
                self.d.BarcodeTypes = c.Code128 | c.Code39

            if n_barcodes is None:
                n_barcodes = 1 if datamatrix else 10
            self.d.LinearFindBarcodes = n_barcodes

        # Map values in EBarcodeTypes to text
        # This should be a class member but the enumeration is visible only
        # after the call to EnsureDispatch.
        self.types = {
            c.Code128: 'Code 128',
            c.Code39: 'Code 39',
            c.Interl25: 'Interleaved 2 of 5',
            c.EAN13: 'EAN-13',
            c.EAN8: 'EAN-8',
            c.Codabar: 'Codabar',
            c.Code11: 'Code 11',
            c.UPCA: 'UPC-A',
            c.UPCE: 'UPC-E',
            c.DataMatrix: 'Data Matrix',
        }

    @classmethod
    def available(cls):
        return com is not None and is_clsid_registered(cls.CLSID)

    def decode_file(self, path):
        # DecodeStream?
        self.d.DecodeFile(str(path))
        res = [None] * self.d.Barcodes.length
        for i in range(0, self.d.Barcodes.length):
            b = self.d.Barcodes.item(i)
            # TODO Coordinates
            res[i] = Barcode(
                self.types.get(b.BarcodeType, 'Unknown'), b.Text, None
            )
        return res

    def __call__(self, img):
        # Temporary files on Windows are pain
        img_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        try:
            msg = 'Writing temp file [{0}] for Data Symbol'
            debug_print(msg.format(img_temp.name))
            cv2.imwrite(img_temp.name, img)
            img_temp.close()
            return self.decode_file(img_temp.name)
        finally:
            os.unlink(img_temp.name)
