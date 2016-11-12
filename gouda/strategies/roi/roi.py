from __future__ import print_function

from .decode import Decoder
from .detect import Detector
from .filter import AreaFilter


from pprint import pprint

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

    return ('roi', list(res.values())) if res else None
