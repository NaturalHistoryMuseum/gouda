"""Barcode decoding engines
"""
# TODO LH Expose each decoders capabilities - do not restrict to Code 128 +
# Code 39 or Data Matrix

# LH TODO A way to provide licence keys

# LH TODO A way to provide paths of external programs

from accusoft import AccusoftEngine
from datasymbol import DataSymbolEngine
from dtk import DTKEngine
from libdmtx import LibDMTXEngine
from inlite import InliteEngine
from softek import SoftekEngine
from stecos import StecosEngine
from zbar_engine import ZbarEngine
from zxing import ZxingEngine
