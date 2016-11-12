import os
import tempfile

import cv2

try:
    from win32com import client as com
    from win32com.client import constants as c
    import win32api
    from ctypes import windll
except ImportError:
    windll = com = win32api = c = None

from gouda.barcode import Barcode
from gouda.gouda_error import GoudaError
from gouda.util import debug_print, is_clsid_registered


class AccusoftEngine(object):
    """Decode using the Accusoft BarcodeXpress SDK

    BarcodeXpress can decode many types of barcodes - currently using it just
    for Data Matrix and Code 128
    """

    IMAGE_READER_CLSID = 'Accusoft.ImagXpress'
    DECODER_CLSID = 'Accusoft.BarcodeXpress'

    def __init__(self, datamatrix):
        if not self.available():
            raise GoudaError('Accusoft unavailable')
        else:
            com.pythoncom.CoInitialize()

            # Tip from stackoverflow about how to access COM constants
            # http://stackoverflow.com/a/21534997/1773758
            self.ie = com.gencache.EnsureDispatch(self.IMAGE_READER_CLSID)
            self.be = com.gencache.EnsureDispatch(self.DECODER_CLSID)
            if datamatrix:
                self.be.BarcodeType = c.BC_TypeDataMatrix
            else:
                self.be.BarcodeType = c.BC_TypeCode128 + c.BC_TypeCode39

    @classmethod
    def available(cls):
        return (com is not None and
                is_clsid_registered(cls.IMAGE_READER_CLSID) and
                is_clsid_registered(cls.DECODER_CLSID))

    def decode_file(self, path):
        self.ie.FileName = str(path)
        dib = self.ie.CopyDIB()

        # Yikes!
        try:
            self.be.AnalyzehDib(dib)
        finally:
            if True:
                # TODO LH Who owns dib?
                res = windll.kernel32.GlobalFree(dib)
                if res:
                    debug_print('Error freeing global handle [{0}]'.format(
                        win32api.GetLastError()
                    ))
            self.ie.FileName = ''

        res = [None] * self.be.NumBarcodes
        for i in range(0, self.be.NumBarcodes):
            self.be.GetBarcode(i)
            res[i] = Barcode(self.be.BarcodeCodeName, self.be.BarcodeResult)
        return res

    def __call__(self, img):
        # Temporary files on Windows are pain
        img_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        try:
            msg = 'Writing temp file [{0}] for Accusoft BarcodeXpress'
            debug_print(msg.format(img_temp.name))
            cv2.imwrite(img_temp.name, img)
            img_temp.close()
            return self.decode_file(img_temp.name)
        finally:
            os.unlink(img_temp.name)
