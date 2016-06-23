#!/usr/bin/env python
from __future__ import print_function

import argparse
import csv
import sys
import time
import traceback

import cv2

import gouda
import gouda.util

from gouda.engines.options import engine_options
from gouda.gouda_error import GoudaError
from gouda.rect import Rect
from gouda.util import expand_wildcard, read_image
from gouda.strategies.roi.roi import roi
from gouda.strategies.resize import resize


# TODO LH Visitor that copies file p to a new file for each decoded barcode
#         value (see Chris' process)

def decode(paths, strategies, engine, visitors, read_greyscale):
    """Finds and decodes barcodes in images given in paths
    """
    for p in paths:
        if p.is_dir():
            # Descend into directory
            decode(p.iterdir(), strategies, engine, visitors, read_greyscale)
        else:
            # Process file
            try:
                img = read_image(p, read_greyscale)
                if img is None:
                    # Most likely not an image
                    for visitor in visitors:
                        visitor.result(p, [None, []])
                else:
                    # Read barcodes
                    for strategy in strategies:
                        result = strategy(img, engine)
                        if result:
                            # Found a barcode
                            break
                    else:
                        # No barcode was found
                        result = [None, []]

                    for visitor in visitors:
                        visitor.result(p, result)
            except Exception:
                print('Error processing [{0}]'.format(p))
                traceback.print_exc()


class BasicReportVisitor(object):
    """Writes a line-per-file and a line-per-barcode to stdout
    """
    def result(self, path, result):
        print(path)
        strategy, barcodes = result
        print('Found [{0}] barcodes:'.format(len(barcodes)))
        for index, barcode in enumerate(barcodes):
            print('[{0}] [{1}] [{2}]'.format(index, barcode.type, barcode.data))


class TerseReportVisitor(object):
    """Writes a line-per-file to stdout
    """
    def result(self, path, result):
        strategy, barcodes = result
        values = [b.data for b in barcodes]
        print(path, ' '.join(['[{0}]'.format(v) for v in values]))


class CSVReportVisitor(object):
    """Writes a CSV report
    """
    def __init__(self, engine, greyscale, file=sys.stdout):
        self.w = csv.writer(file, lineterminator='\n')
        self.w.writerow([
            'OS', 'Engine', 'Directory', 'File', 'Image.conversion',
            'Elapsed', 'N.found', 'Types', 'Values', 'Strategy',
            'Coordinates',
        ])
        self.engine = engine
        self.image_conversion = 'Greyscale' if greyscale else 'Unchanged'
        self.start_time = time.time()

    def result(self, path, result):
        strategy, barcodes = result
        types = '|'.join(b.type for b in barcodes)
        values = '|'.join(b.data for b in barcodes)
        rects = (b.rect for b in barcodes)
        coordinates = '|'.join(
            str(tuple(r.coordinates)) if r else '' for r in rects
        )
        self.w.writerow([sys.platform,
                         self.engine,
                         path.parent.name,
                         path.name,
                         self.image_conversion,
                         time.time()-self.start_time,
                         len(barcodes),
                         types,
                         values,
                         strategy,
                         coordinates])


class RenameReporter(object):
    """Renames files based on their barcodes
    """
    def result(self, path, result):
        strategy, barcodes = result
        print(path)
        if not barcodes:
            print('  No barcodes')
        else:
            barcodes = [
                b.data.replace('(', '-').replace(')', '') for b in barcodes
            ]
            fname = '_'.join(barcodes)
            dest = path.parent / (fname + path.suffix)
            if path == dest:
                print('  Already correctly named')
            elif dest.is_file():
                msg = '  Cannot rename to [{0}] because destination exists'
                print(msg.format(dest))
            else:
                path.rename(dest)
                print('  Renamed to [{0}]'.format(dest))


class ShowBarcodesVisitor(object):
    """Shows in a window the image with locations of barcodes and waits for a
    keypress
    """
    def result(self, path, result):
        strategy, barcodes = result
        img = cv2.imread(str(path))

        # Bounding boxes around barcodes
        # Add some padding and round coords to ints
        rects = (Rect(*map(int, b.rect.padded(10))) for b in barcodes if b.rect)
        for rect in rects:
            cv2.rectangle(
                img, rect.topleft, rect.bottomright, (0xff, 0x00, 0x00), 5
            )

        # Resize to fit screen
        factor = 800.0 / max(img.shape[:2])
        img = cv2.resize(img, (0, 0), fx=factor, fy=factor)
        cv2.imshow('barcodes', img)
        cv2.waitKey(0)


if __name__ == '__main__':
    # TODO ROI candidate area max and/or min?
    # TODO Give area min and max as percentage of total image area?
    # TODO Report barcode regions  - both normalised and absolute coords?
    # TODO Swallow zbar warnings?

    parser = argparse.ArgumentParser(
        description='Finds and decodes barcodes on images'
    )
    parser.add_argument('--debug', '-d', action='store_true')
    parser.add_argument(
        '--action', '-a',
        choices=['basic', 'terse', 'csv', 'rename', 'show'], default='basic'
    )
    parser.add_argument('--greyscale', '-g', action='store_true')

    options = engine_options()
    if not options:
        raise GoudaError('No engines are available')
    parser.add_argument('engine', choices=sorted(options.keys()))

    parser.add_argument('image', nargs='+', help='path to an image or directory')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + gouda.__version__)

    args = parser.parse_args()

    gouda.util.DEBUG_PRINT = args.debug

    engine = options[args.engine]()

    if 'csv' == args.action:
        visitor = CSVReportVisitor(args.engine, args.greyscale)
    elif 'terse' == args.action:
        visitor = TerseReportVisitor()
    elif 'rename' == args.action:
        visitor = RenameReporter()
    elif 'show' == args.action:
        visitor = ShowBarcodesVisitor()
    else:
        visitor = BasicReportVisitor()

    strategies = [resize, roi]
    decode(
        expand_wildcard(args.image), strategies, engine, [visitor], args.greyscale
    )
