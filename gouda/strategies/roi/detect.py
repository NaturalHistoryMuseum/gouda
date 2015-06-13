from __future__ import print_function

import subprocess
import tempfile

import cv2
import numpy as np

from pathlib import Path

from .rect import Rect
from gouda.util import debug_print

class Detector(object):
    """ Detects candidate barcode areas in an image
    """

    # Detection algorithm tested with images of this width
    WIDTH = 2048

    # Two different structuring kernels
    FIRST = (11,11)
    SECOND = (50,50)
    def __init__(self, img, structuring_kernel=FIRST):
        self._img = img
        self._candidates = None
        self._working_images = None
        self.structuring_kernel = structuring_kernel

    @property
    def resized(self):
        return self._working_images.get('resized')

    @property
    def candidates(self):
        if self._candidates is None:
            self._working_images, self._candidates = self._compute_candidates()
        return self._candidates

    def _compute_candidates(self):
        """ Returns a tuple ({'image_name':image,},
                             [(x,y,width,height),],
                            )
        """
        # Based on http://stackoverflow.com/questions/9013703/how-to-find-the-location-of-red-region-in-an-image-using-matlab/9014569#9014569
        debug_print('Computing candidate barcode areas')

        resized = self._img
        if self.WIDTH!=resized.shape[1]:
            factor = float(self.WIDTH)/resized.shape[1]
            debug_print('Resize {0}, factor of {1:.2}'.format(self.WIDTH, factor))
            resized = cv2.resize(resized, (0,0), fx=factor, fy=factor)
        grey = resized

        if 'uint8'!=grey.dtype or 2!=len(grey.shape):
            debug_print('Convert grey')
            grey = cv2.cvtColor(grey, cv2.COLOR_BGR2GRAY)

        debug_print('Equalize')
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        equalized = clahe.apply(grey)

        # http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_imgproc/py_gradients/py_gradients.html
        debug_print('High-pass filter')
        sobelx = cv2.Sobel(equalized, cv2.CV_16S, 1, 0, 3)
        sobelx = np.abs(sobelx)

        sobely = cv2.Sobel(equalized, cv2.CV_16S, 0, 1, 3)
        sobely = np.abs(sobely)

        gradient = equalized.copy()
        gradient = cv2.convertScaleAbs(sobely-sobelx, gradient)

        debug_print('Low-pass filter')
        if True:
            gradient = cv2.GaussianBlur(gradient, (3,3), 0)
        else:
            # Better than gaussian blur at preserving edges but slower
            gradient = cv2.bilateralFilter(gradient,9,75,75)        # TODO Parameter values?

        debug_print('Threshold')
        # All scans should have good, consistent lighting so apply a very high threshold
        retval,thresh = cv2.threshold(gradient, 0xd0, 0xff, cv2.THRESH_BINARY)

        debug_print('Morphology')
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, self.structuring_kernel)
        closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

        debug_print('Contours')
        cont_img = closing.copy()
        contours,hierarchy = cv2.findContours(cont_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        working_images = { 'resized':resized,
                           'grey':grey,
                           'equalized':equalized,
                           'gradient':gradient,
                           'thresh':thresh,
                           'closing':closing,
                         }

        candidates = [cv2.boundingRect(c) for c in contours]
        candidates = [Rect(x, y, width, height) for x, y, width, height in candidates]
        return (working_images, candidates)
