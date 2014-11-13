from .decode import Decoder
from .detect import Detector
from .filter import AreaFilter
from .rect import Rect

from gouda.barcode import Barcode
from gouda.util import debug_print


def roi(img, engine):
    # Regions of the image that might contain barcodes

    # Detect candidate rectangles
    detector = Detector(img)

    # Filter candidate rectangles by area
    filtered = AreaFilter().filter(detector.candidates)

    # Decode barcodes
    barcodes = list(Decoder(detector.resized, filtered, engine))

    # Remove duplicate barcodes
    res = {}
    for barcode in barcodes:
        if barcode.data not in res:
            res[barcode.data] = barcode

    return 'roi',res.values()
