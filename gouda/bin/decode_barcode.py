#!/usr/bin/env python
from __future__ import print_function

import argparse
import csv
import glob
import os
import sys
import time

from functools import partial

import cv2

import gouda.util

from gouda.engines import (AccusoftEngine, DataSymbolEngine,
                           InliteEngine, LibDMTXEngine, StecosEngine,
                           SoftekEngine, ZbarEngine, ZxingEngine)
from gouda.util import expand_wildcard, read_image
from gouda.strategies import roi, resize


def decode(paths, strategies, engine, reporter, read_greyscale):
    """ Finds and decodes barcodes in the image at the given path.
    """
    for p in paths:
        if p.is_dir():
            decode(p.iterdir(), strategies, engine, reporter, read_greyscale)
        else:
            # TODO LH Read greyscale affects decoders?
            # TODO LH Read greyscale reduces memory requirements?
            # TODO LH Command-line argument for greyscale / colour
            img = read_image(p, read_greyscale)
            if img is None:
                reporter.result(p, [None, []])
            else:
                for strategy in strategies:
                    result = strategy(img, engine)
                    if result:
                        break
                reporter.result(p, result)


class BasicReporter(object):
    def result(self, path, result):
        print(path)
        strategy, barcodes = result
        print('Found [{0}] barcodes:'.format(len(barcodes)))
        for index,barcode in enumerate(barcodes):
            print('[{0}] [{1}] [{2}]'.format(index, barcode.type, barcode.data))


class TerseReporter(object):
    def result(self, path, result):
        strategy, barcodes = result
        values = [b.data for b in barcodes]
        print(path, ' '.join(['[{0}]'.format(v) for v in values]))


class CSVReporter(object):
    def __init__(self, engine, greyscale):
        self.w = csv.writer(sys.stdout)
        self.w.writerow(['OS','Engine','Directory','File','Image.conversion',
                         'Elapsed','N.found','Values','Strategy'])
        self.engine = engine
        self.image_conversion = 'Greyscale' if greyscale else 'Unchanged'
        self.start_time = time.time()

    def result(self, path, result):
        strategy, barcodes = result
        decoded = ['[{0}:{1}]'.format(b.type, b.data) for b in barcodes]
        decoded = u' '.join(decoded)
        self.w.writerow([sys.platform,
                         self.engine,
                         path.parent.name,
                         path.stem,
                         self.image_conversion,
                         time.time()-self.start_time,
                         len(barcodes),
                         decoded,
                         strategy])

def engine_choices():
    choices = {'libdmtx': LibDMTXEngine,
               'zbar': ZbarEngine,
               'zxing': ZxingEngine,
               }

    choices = {k:v for k,v in choices.iteritems() if v.available()}

    if AccusoftEngine.available():
        choices.update({'accusoft-1d':  partial(AccusoftEngine, datamatrix=False),
                        'accusoft-dm': partial(AccusoftEngine, datamatrix=True),
                      })

    if DataSymbolEngine.available():
        choices['datasymbol-1d'] = partial(DataSymbolEngine, datamatrix=False)

    if InliteEngine.available():
        choices.update({'inlite-1d': partial(InliteEngine, datamatrix=False),
                        'inlite-dm': partial(InliteEngine, datamatrix=True),
                      })

    if StecosEngine.available():
        choices.update({'stecos-1d' : partial(StecosEngine, datamatrix=False),
                        'stecos-dm' : partial(StecosEngine, datamatrix=True),
                      })

    if SoftekEngine.available():
        choices.update({'softek-1d': partial(SoftekEngine, datamatrix=False),
                        'softek-dm': partial(SoftekEngine, datamatrix=True),
                      })

    return choices


if __name__=='__main__':
    # TODO ROI candidate area max and/or min?
    # TODO Give area min and max as percentage of total image area?
    # TODO Report barcode regions  - both normalised and absolute coords?
    # TODO Swallow zbar warnings?

    parser = argparse.ArgumentParser(description='Finds and decodes barcodes on images')
    parser.add_argument('--debug', '-v', action='store_true')
    parser.add_argument('--report', '-r', choices=['basic', 'terse', 'csv'], default='basic')
    parser.add_argument('--greyscale', '-g', action='store_true')

    choices = engine_choices()
    if not choices:
        raise GoudaError('No engines are available')
    parser.add_argument('engine', choices=sorted(choices.keys()))

    parser.add_argument('image', nargs='+', help='path to an image or directory')

    args = parser.parse_args()

    gouda.util.DEBUG_PRINT = args.debug

    engine = choices[args.engine]()

    if 'csv'==args.report:
        reporter = CSVReporter(args.engine, args.greyscale)
    elif 'terse'==args.report:
        reporter = TerseReporter()
    else:
        reporter = BasicReporter()

    strategies = [resize, roi]
    decode(expand_wildcard(args.image), strategies, engine, reporter,
           args.greyscale)
