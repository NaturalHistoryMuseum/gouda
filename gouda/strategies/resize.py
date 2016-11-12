import cv2
import numpy as np

from gouda.util import debug_print


def _unsharpmask(img):
    img = np.array(img, copy=True)
    blur = cv2.GaussianBlur(img, (0, 0), 10)
    return cv2.addWeighted(img, 3, blur, -2, 0)


def resize(img, engine):
    # Entire image at different fractions of original size

    # TODO LH try more sharpening, equalisation, other stuff?
    for sharpening in (0, 1, 2):
        if sharpening > 0:
            img = _unsharpmask(img)
        for f in [round(x * 0.01, 2) for x in range(100, 0, -5)]:
            msg = 'resize: scaling factor [{0}] sharpening [{1}]'
            msg = msg.format(f, sharpening)
            debug_print(msg)
            if 1 == f:
                i = img
            else:
                # Resize from the original image
                i = cv2.resize(img, (0, 0), fx=f, fy=f)
            barcodes = engine(i)
            if barcodes:
                return msg, barcodes

    return None
