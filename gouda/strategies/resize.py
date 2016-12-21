import cv2
import numpy as np

from gouda.util import debug_print


def _unsharpmask(img):
    img = np.array(img, copy=True)
    blur = cv2.GaussianBlur(img, (0, 0), 10)
    return cv2.addWeighted(img, 3, blur, -2, 0)


# Minimum number of pixel along each edge. What is a sensible minimum?
MINIMUM_PIXELS = 10

def resize(img, engine):
    # Entire image at different fractions of original size

    # TODO LH try more sharpening, equalisation, other stuff?
    for sharpening in (0, 1, 2):
        if sharpening > 0:
            img = _unsharpmask(img)
        height, width = img.shape[1], img.shape[0]
        for factor in [round(x * 0.01, 2) for x in range(100, 0, -5)]:
            msg = 'resize: scaling factor [{0}] sharpening [{1}]'
            msg = msg.format(factor, sharpening)
            debug_print(msg)
            if 1 == factor:
                resized = img
            else:
                # Resize from the original image, only if resized height and
                # width are greater than the minimum.
                # cv2.resize raises an error if either dimension is zero.
                dsize = (int(round(height * factor)), int(round(width * factor)))
                if dsize[0] >= MINIMUM_PIXELS and dsize[1] >= MINIMUM_PIXELS:
                    resized = cv2.resize(img, dsize)
                else:
                    # No point in continuing to shrink
                    break
            barcodes = engine(resized)
            if barcodes:
                return msg, barcodes

    return None
