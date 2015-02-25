import os
import subprocess
import sys
import tempfile

from pathlib import Path

import cv2

try:
    from win32com import client as com
    from win32com.client import constants as c
except ImportError:
    com = c = None

from gouda import config
from gouda.barcode import Barcode
from gouda.gouda_error import GoudaError
from gouda.util import debug_print, is_clsid_registered


LICENSE_KEY = getattr(config, 'SOFTEK_LICENSE_KEY', '')

class Win32SoftekEngine(object):
    """Decode using the Softek Barcode SDK

    Softek can decode many types of barcodes - currently using it just
    for Data Matrix and Code 128
    """

    CLSID = "SoftekATL.Barcode"

    def __init__(self, datamatrix):
        if not self.available():
            raise GoudaError('Inlite unavailable')
        else:
            com.pythoncom.CoInitialize()

            # Tip from stackoverflow about how to access COM constants
            # http://stackoverflow.com/a/21534997/1773758
            self.d = com.gencache.EnsureDispatch(self.CLSID)

            self.d.LicenseKey = LICENSE_KEY

            self.d.ReadCode39 = False
            self.d.ReadCode25 = False
            self.d.ReadCode128 = False
            self.d.ReadEAN13 = False
            self.d.ReadEAN8 = False
            self.d.ReadUPCA = False
            self.d.ReadUPCE = False
            self.d.ReadCodabar = False
            self.d.ReadPDF417 = False
            self.d.ReadDatabar = False
            self.d.ReadDataMatrix = False
            self.d.ReadMicroPDF417 = False
            self.d.ReadQRCode = False

            if datamatrix:
                self.d.ReadDataMatrix = True
            else:
                self.d.ReadCode128 = True
                self.d.ReadCode39 = True

            # Databar Options is a mask that controls which type of databar barcodes will be read and whether or not
            # the software will look for a quiet zone around the barcode.
            # 1 = 2D-Linkage flag (handle micro-PDf417 barcodes as supplementary data - requires ReadMicroPDF417 to be true).
            # 2 = Read RSS14
            # 4 = Read RSS14 Stacked
            # 8 = Read Limited
            # 16 = Read Expanded
            # 32 = Read Expanded Stacked
            # 64 = Require quiet zone
            self.d.DatabarOptions = 0

            # If you want to read more than one barcode then set Multiple Read to True
            # Setting MutlipleRead to False will make the recognition faster
            self.d.MultipleRead = True

            # If you know the max number of barcodes for a single page then increase speed by setting MaxBarcodesPerPage
            # self.d.MaxBarcodesPerPage = 5

            # In certain conditions (MultipleRead = false or MaxBarcodesPerPage = 1) the SDK can make fast scan of an image before performing the normal scan. This is useful if only 1 bar code is expected per page.
            self.d.UseFastScan = False

            # If MultipleRead = false or MaxBarcodesPerPage = 1 and the bar code is always closer to the top of a page then set BarcodesAtTopOfPage to True to increase speed.
            #self.d.BarcodesAtTopOfPage = False

            # Noise reduction takes longer but can make it possible to read some difficult barcodes
            # When using noise reduction a typical value is 10 - the smaller the value the more effect it has.
            # A zero value turns off noise reduction.
            # If you use NoiseReduction then the ScanDirection mask must be either only horizontal or only
            # vertical (i.e 1, 2, 4, 8, 5 or 10).
            #self.d.NoiseReduction = 0

            # You may need to set a small quiet zone if your barcodes are close to text and pictures in the image.
            # A value of zero uses the default.
            self.d.QuietZoneSize = 0

            # Set the direction that the barcode reader should scan for barcodes
            # The value is a mask where 1 = Left to Right, 2 = Top to Bottom, 3 = Right To Left, 4 = Bottom to Top
            self.d.ScanDirection = 15

            # Set the page number to read from in a multi-page TIF file. The default is 0, which will make the
            # toolkit check every page.
            # self.d.PageNo = 1

            # SkewTolerance controls the angle of skew that the barcode toolkit will tolerate. By default
            # the toolkit checks for barcodes along horizontal and vertical lines in an image. This works
            # OK for most barcodes because even at an angle it is possible to pass a line through the entire
            # length. SkewTolerance can range from 0 to 5 and allows for barcodes skewed to an angle of 45
            # degrees.
            #self.d.SkewTolerance = 5

            # Read most skewed linear barcodes without the need to set SkewTolerance. Currently applies to Codabar, Code 25, Code 39 and Code 128 barcodes only.
            self.d.SkewedLinear = True

            # Read most skewed datamatrix barcodes without the need to set SkewTolerance
            self.d.SkewedDatamatrix = True

            # ColorProcessingLevel controls how much time the toolkit will searching a color image for a barcode.
            # The default value is 2 and the range of values is 0 to 5. If ColorThreshold is non-zero then 
            # ColorProcessingLevel is effectively set to 0.
            self.d.ColorProcessingLevel = 2

            # MaxLength and MinLength can be used to specify the number of characters you expect to
            # find in a barcode. This can be useful to increase accuracy or if you wish to ignore some
            # barcodes in an image.
            # self.d.MinLength = 4
            # self.d.MaxLength = 999

            # When the toolkit scans an image it records the number of hits it gets for each barcode that
            # MIGHT be in the image. If the hits recorded for any of the barcodes are >= PrefOccurrence
            # then only these barcodes are returned. Otherwise, any barcode whose hits are >= MinOccurrence
            # are reported. If you have a very poor quality image then try setting MinOccurrence to 1, but you
            # may find that some false positive results are returned.
            #self.d.MinOccurrence = 2
            #self.d.PrefOccurrence = 4

            # Read Code 39 barcodes in extended mode
            # self.d.ExtendedCode39 = True

            # Barcode string is numeric
            # self.d.ReadNumeric = True

            # Set a regular expression for the barcode
            # self.d.Pattern = "^[A-Z]{2}[0-9]{5}$"

            # If you are scanning at a high resolution and the spaces between bars are
            # larger than 1 pixel then set MinSpaceBarWidth to 2 and increase your read rate.
            self.d.MinSpaceBarWidth = 2

            # MedianFilter is a useful way to clean up higher resolution images where the black bars contain white dots
            # and the spaces contain black dots. It does not work if the space between bars is only 1 pixel wide.
            self.d.MedianFilter = False

            # ReportUnreadBarcodes can be used to warn of the presence of a barcode on a page that the SDK has not been able to decode.
            # It currently has the following important limitations:
            # 1. An unread linear barcode will only be reported if no other barcode was found in the same page.
            # 2. The height of the area for an unread linear barcode will only cover a portion of the barcode.
            # 3. Only 2-D barcodes that fail to error correct will be reported.
            # 4. The barcode type and value will both be set to UNREAD for all unread barcodes.
            # 5. The reporting of unread linear barcodes takes no account of settings for individual barcode types. For example, if ReadCode39 is True and 
            # an image contains a single Code 39 barcode then this will be reported as an unread barcode.
            # 6. 2-D barcodes are only reported as unread if the correct barcode types have been enabled.
            # 7. Not all unread barcodes will be detected. 
            #
            # The value is a mask with the following values: 1 = linear barcodes, 2 = Datamatrix, 4 = QR-Code, 8 = PDF-417
            self.d.ReportUnreadBarcodes = 0

            # Time out for reading a barcode from a page in ms. Note that this does not include the time to load the page.
            # 0 means no time out.
            self.d.TimeOut = 0

    @classmethod
    def available(cls):
        return com is not None and is_clsid_registered(cls.CLSID)

    def decode_file(self, path):
        self.d.ScanBarCode(str(path))
        barcodes = [None] * self.d.BarCodeCount
        for i in xrange(0, self.d.BarCodeCount):
            barcodes[i] = Barcode(str(self.d.BarStringType(1+i)),
                                  self.d.BarString(1+i))
        return barcodes

    def __call__(self, img):
        # Temporary files on Windows are pain
        img_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        try:
            debug_print('Writing temp file [{0}] for Softek'.format(img_temp.name))
            cv2.imwrite(img_temp.name, img)
            return self.decode_file(img_temp.name)
        finally:
            # TODO LH Logic here?
            img_temp.close()
            os.unlink(img_temp.name)


class POSIXSoftekEngine(object):
    """ Interface to Softek's bardecode library """

    BARDECODE = getattr(config, 'SOFTEK_BARDECODE', None)

    def __init__(self, datamatrix):
        if not self.available():
            raise GoudaError('Softek unavailable')
        else:
            self.datamatrix = datamatrix

    @classmethod
    def available(cls):
        return cls.BARDECODE is not None and cls.BARDECODE.is_file()

    def decode_file(self, path):
        args = [str(self.BARDECODE),
                '-m',
                '-K', 
                LICENSE_KEY,
                '-b',
                ('--ReadDataMatrix=1' if self.datamatrix else 
                 '--ReadCode128=1 --ReadCode39=1'),
                str(path),
               ]
        softek = subprocess.Popen(args, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

        stdoutdata, stderrdata = softek.communicate()
        if stdoutdata:
            # TODO LH Coordinates?
            # Lines are printed in the form Type:Value
            # TODO LH regexp
            res = [l.split(':') for l in stdoutdata.strip().split('\n')]
            return [ Barcode(r[0], r[1]) for r in res]
        else:
            return []

    def __call__(self, img):
        with tempfile.NamedTemporaryFile(suffix='.tiff') as img_temp:
            debug_print('Writing temp file [{0}] for Softek'.format(img_temp.name))
            cv2.imwrite(img_temp.name, img)
            return self.decode_file(img_temp.name)

SoftekEngine = Win32SoftekEngine if 'win32'==sys.platform else POSIXSoftekEngine
