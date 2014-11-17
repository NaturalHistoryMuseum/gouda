import cv2
import numpy as np

from gouda.barcode import Barcode
from gouda.util import debug_print
from .rect import Rect


class Decoder(object):
    """ Decodes barcodes within rectangular regions of an image
    """

    # TODO Stop after n barcodes?

    def __init__(self, img, candidates, engine, expected=None):
        self._img = img
        self._candidates = candidates
        self._barcodes = None
        self._engine = engine

    def __iter__(self):
        """ Iterate Barcode objects
        """
        if self._barcodes is None:
            self._barcodes = self._compute_barcodes()
        return iter(self._barcodes)

    def _compute_barcodes(self):
        # Convert to greyscale if required
        img = self._img
        if 'uint8'!=img.dtype or 2!=len(img.shape):
            debug_print('Convert grey')
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        res = []
        for r in self._candidates:
            crop = img[r.y:(r.y+r.height), r.x:(r.x+r.width)]

            # Unsharp mask
            blur = cv2.GaussianBlur(crop, (0,0), 10)
            crop = cv2.addWeighted(crop, 1.5, blur, -0.5, 0)

            # Equalisation/contrast sometimes causes libdtmx to fail, sometimes causes
            # it to succeed.
            decoded = self._engine(crop)
            if not decoded:
                if False:
                    debug_print('equalisation')
                    # Try equalized image
                    #crop = cv2.equalizeHist(crop)    # An alternative technique
                    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                    crop = clahe.apply(crop)
                    #cv2.imwrite('crop{0}_equalised.jpg'.format(i), crop)
                else:
                    debug_print('contrast')
                    # Contrast
                    # http://stackoverflow.com/questions/10549245/how-can-i-adjust-contrast-in-opencv-in-c
                    bigmask = cv2.compare(crop, np.uint8([0x80]), cv2.CMP_GE)
                    smallmask = cv2.bitwise_not(bigmask)
                    big = cv2.add(crop, 0x10, mask=bigmask)
                    small = cv2.subtract(crop, 0x5a, mask=smallmask)
                    crop = cv2.add(big, small)
                decoded = self._engine(crop)

            for b in decoded:
                res.append(Barcode(b.type, b.data))

        return res
