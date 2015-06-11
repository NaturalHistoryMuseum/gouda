
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


class DTKEngine(object):
    """Decode using the DTK Barcode Reader SDK

    DTK can decode many types of barcodes - currently using it just for
    Data Matrix
    """

    CLSID = "DTKBarReader.BarcodeReader"

    def __init__(self, datamatrix):
        if not self.available():
            raise GoudaError('DTK unavailable')
        else:
            com.pythoncom.CoInitialize()

            # Tip from stackoverflow about how to access COM constants
            # http://stackoverflow.com/a/21534997/1773758
            self.d = com.gencache.EnsureDispatch(self.CLSID)
            if datamatrix:
               self.d.BarcodeTypes = c.BT_DataMatrix
            else:
                self.d.BarcodeTypes = c.BT_Code128 | c.BT_Code39

        # Map values in EBarcodeType to text
        # This would ideally be a class member but the enumeration
        # is visible only after the call to EnsureDispatch.
        self.types = { c.BT_AustraliaPost : 'Australia Post',
                       c.BT_Codabar : 'Codabar',
                       c.BT_Code11 : 'Code 11',
                       c.BT_Code128 : 'Code 128',
                       c.BT_Code39 : 'Code 39',
                       c.BT_Code39Extended : 'Code 39 Extended',
                       c.BT_Code93 : 'Code 93',
                       c.BT_DataMatrix : 'Data Matrix',
                       c.BT_EAN13 : 'EAN-13',
                       c.BT_EAN8 : 'EAN-8',
                       c.BT_IntelligentMail : 'Intelligent Mail',
                       c.BT_Inter2of5 : 'Interleaved 2 of 5',
                       c.BT_MicroQRCode : 'Micro QR Code',
                       c.BT_PatchCode : 'Patch code',
                       c.BT_PDF417 : 'PDF 417',
                       c.BT_PharmaCode : 'Pharma Code',
                       c.BT_Planet : 'Planet',
                       c.BT_Plus2 : 'Plus 2',
                       c.BT_Plus5 : 'Plus 5',
                       c.BT_Postnet : 'Postnet',
                       c.BT_QRCode : 'QR Code',
                       c.BT_RM4SCC : 'RM 4 SCC',
                       c.BT_RSS14 : 'RSS 14',
                       c.BT_RSSExpanded : 'RSS Expanded',
                       c.BT_RSSLimited : 'RSS Limited',
                       c.BT_UCC128 : 'UCC 128',
                       c.BT_Unknown : 'Unknown',
                       c.BT_UPCA : 'UPCA',
                       c.BT_UPCE : 'UPCE',
                     }

    @classmethod
    def available(cls):
        return com is not None and is_clsid_registered(cls.CLSID)

    def decode_file(self, path):
        self.d.ReadFromFile(str(path))
        barcodes = [None] * self.d.Barcodes.Count
        for i in xrange(0, self.d.Barcodes.Count):
            b = self.d.Barcodes.Item(i)
            barcodes[i] = Barcode(self.types.get(b.Type, 'Unknown'),
                                  b.BarcodeString)
        return barcodes

    def __call__(self, img):
        # Temporary files on Windows are pain
        img_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        try:
            debug_print('Writing temp file [{0}] for DTK'.format(img_temp.name))
            cv2.imwrite(img_temp.name, img)
            return self.decode_file(img_temp.name)
        finally:
            # TODO LH Logic here?
            img_temp.close()
            os.unlink(img_temp.name)
