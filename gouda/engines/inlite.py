
import os
import tempfile

import cv2

try:
    from win32com import client as com
    from win32com.client import constants as c
except ImportError:
    com = c = None

from gouda.barcode import Barcode
from gouda.gouda_error import GoudaError
from gouda.util import debug_print, is_clsid_registered


class InliteEngine(object):
    """Decode using the Inline ClearImage SDK

    __init__ takes an argument 'format' which should be one of 'datamatrix',
    '1d', 'qrcode' and 'pdf417'
    """

    CLSID = "ClearImage.ClearImage"

    def __init__(self, format):
        choices = ('1d', 'datamatrix', 'pdf417', 'qrcode')
        if not self.available():
            raise GoudaError('Inlite unavailable')
        elif format not in choices:
            raise ValueError('Unrecognised barcode format [{0}]'.format(format))
        else:
            com.pythoncom.CoInitialize()

            # Tip from stackoverflow about how to access COM constants
            # http://stackoverflow.com/a/21534997/1773758
            self.ci = com.gencache.EnsureDispatch(self.CLSID)

            if '1d' == format:
                self.d = self.ci.CreateBarcodePro()
                self.d.Type = c.cibfCode39 | c.cibfCode128
            elif 'datamatrix' == format:
                self.d = self.ci.CreateDataMatrix()
            elif 'pdf417' == format:
                self.d = self.ci.CreatePdf417()
            else:
                self.d = self.ci.CreateQR()

            self.d.Algorithm = c.cibBestRecognition
            self.d.Directions = c.cibHorz | c.cibVert | c.cibDiag

            # Map values in EBarcodeType to text
            # This should be a class member but the enumeration is visible only
            # after the call to EnsureDispatch.
            self.types = {
                c.cibf4State: 'PostBar / CPC 4-State',
                c.cibfAddon2: 'Addon-2',
                c.cibfAddon5: 'Addon-5',
                c.cibfAirline2of5: 'IATA',
                c.cibfCodabar: 'Codabar',
                c.cibfCode128: 'Code 128',
                c.cibfCode32: 'Code 32',
                c.cibfCode39: 'Code 39',
                c.cibfCode93: 'Code 93',
                c.cibfDatalogic2of5: 'Datalogic',
                c.cibDataMatrix: 'Data Matrix',
                c.cibfEan13: 'EAN-13',
                c.cibfEan8: 'EAN-8',
                c.cibfIndustrial2of5: 'Industrial 2 of 5',
                c.cibfInterleaved2of5: 'Interleaved 2 of 5',
                c.cibfMatrix2of5: 'Matrix 2 of 5',
                c.cibfPatch: 'Patch code',
                c.cibPdf417: 'PDF 417',
                c.cibPlanet: 'Planet',
                c.cibfPostnet: 'Postnet or Planet',
                c.cibQR: 'QR Code',
                c.cibSingaporePost: 'Singapore Post',
                c.cibfUcc128: 'UCC-128',
                c.cibfUpca: 'UPC-A',
                c.cibfUpce: 'UPC-E',
                c.cibUspsIntelligentMail: 'USPS Intelligent mail',
            }

    @classmethod
    def available(cls):
        return com is not None and is_clsid_registered(cls.CLSID)

    def decode_file(self, path):
        self.d.Image.Open(str(path))
        self.d.Find()
        barcodes = [None] * len(self.d.Barcodes)
        for i, b in enumerate(self.d.Barcodes):
            # TODO Coordinates
            barcodes[i] = Barcode(
                self.types.get(b.Type, 'Unknown'), b.Text, None
            )
        return barcodes

    def __call__(self, img):
        # Temporary files on Windows are pain
        img_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        try:
            debug_print(
                'Writing temp file [{0}] for ClearImage'.format(img_temp.name)
            )
            cv2.imwrite(img_temp.name, img)
            return self.decode_file(img_temp.name)
        finally:
            # TODO LH Logic here?
            img_temp.close()
            os.unlink(img_temp.name)
