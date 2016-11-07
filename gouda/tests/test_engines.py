# -*- coding: utf-8 -*-
import unittest
import sys

from pathlib import Path

import cv2

from gouda.barcode import Barcode
from gouda.engines import (AccusoftEngine, DataSymbolEngine, DTKEngine,
                           InliteEngine, LibDMTXEngine, SoftekEngine,
                           StecosEngine, ZbarEngine, ZxingEngine)


# TODO LH Can Data Matrix barcodes handle unicode?

TESTDATA = Path(__file__).parent / 'test_data'


class TestEngine(unittest.TestCase):
    """Base class for testing engines
    """
    CODE128 = cv2.imread(str(TESTDATA / 'code128.png'))
    DATAMATRIX = cv2.imread(str(TESTDATA / 'datamatrix.png'))
    QRCODE = cv2.imread(str(TESTDATA / 'qrcode.png'))
    PDF417 = cv2.imread(str(TESTDATA / 'pdf417.png'))
    NOBARCODE = cv2.imread(str(TESTDATA / 'nobarcode.png'))

    def _test_1d(self, engine, type='CODE128'):
        expected = [Barcode(type=type, data=b'Stegosaurus')]
        res = engine(self.CODE128)
        self.assertEqual(expected, res)
        self.assertEqual([], engine(self.NOBARCODE))

    def _test_dm(self, engine, type='Data Matrix'):
        expected = [Barcode(type=type, data=b'Triceratops')]
        res = engine(self.DATAMATRIX)
        self.assertEqual(expected, res)
        self.assertEqual([], engine(self.NOBARCODE))

    def _test_qr(self, engine, type='QR Code'):
        expected = [Barcode(type=type, data=b'Thalassiodracon')]
        res = engine(self.QRCODE)
        self.assertEqual(expected, res)
        self.assertEqual([], engine(self.NOBARCODE))

    def _test_pdf417(self, engine, type='PDF 417'):
        expected = [Barcode(type=type, data=b'Metasequoia')]
        res = engine(self.PDF417)
        self.assertEqual(expected, res)
        self.assertEqual([], engine(self.NOBARCODE))


@unittest.skipUnless(AccusoftEngine.available(), 'AccusoftEngine unavailable')
class TestAccusoftEngine(TestEngine):
    def test_1d(self):
        self._test_1d(AccusoftEngine(datamatrix=False), type='Code 128')

    def test_dm(self):
        self._test_dm(AccusoftEngine(datamatrix=True), type='DataMatrix')


@unittest.skipUnless(DataSymbolEngine.available(), 'DataSymbolEngine unavailable')
class TestDataSymbolEngine(TestEngine):
    # Evaluation SDK replaces the last three characters of the
    # decoded value with 'DEMO', so this test needs to do some extra work.
    def test_1d(self):
        res = DataSymbolEngine(datamatrix=False)(self.CODE128)
        self.assertEqual(1, len(res))
        self.assertEqual('Code 128', res[0].type)
        self.assertIn(res[0].data, ('StegosauDEMO', 'Stegosaurus'))


@unittest.skipUnless(DTKEngine.available(), 'DTKEngine unavailable')
class TestDTKEngine(TestEngine):
    def test_1d(self):
        self._test_1d(DTKEngine(datamatrix=False), type='Code 128')

    def test_dm(self):
        self._test_dm(DTKEngine(datamatrix=True))


@unittest.skipUnless(InliteEngine.available(), 'InliteEngine unavailable')
class TestInliteEngine(TestEngine):
    def test_1d(self):
        self._test_1d(InliteEngine(format='1d'), type='Unknown')

    def test_dm(self):
        self._test_dm(InliteEngine(format='datamatrix'))

    def test_qr(self):
        self._test_qr(InliteEngine(format='qrcode'))

    def test_pdf417(self):
        self._test_pdf417(InliteEngine(format='pdf417'))


@unittest.skipUnless(LibDMTXEngine.available(), 'LibDMTXEngine unavailable')
class TestLibDMTXEngine(TestEngine):
    def test_dm(self):
        self._test_dm(LibDMTXEngine())


@unittest.skipUnless(SoftekEngine.available(), 'SoftekEngine unavailable')
class TestSoftekEngine(TestEngine):
    # Evaluation SDK replaces the last three characters of the
    # decoded value with '???', so this test needs to do some extra work.
    @unittest.skipIf(sys.platform.startswith('win'),
                     "Windows SoftekEngine not able to decode self.CODE128")
    def test_1d(self):
        res = SoftekEngine(datamatrix=False)(self.CODE128)
        self.assertEqual(1, len(res))
        self.assertEqual('CODE128', res[0].type)
        self.assertIn(res[0].data, ('Stegosau???', 'Stegosaurus'))

    def test_dm(self):
        res = SoftekEngine(datamatrix=True)(self.DATAMATRIX)
        self.assertEqual(1, len(res))
        self.assertEqual('DATAMATRIX', res[0].type)
        self.assertIn(res[0].data, ('Tricerat???', 'Triceratops'))


@unittest.skipUnless(StecosEngine.available(), 'StecosEngine unavailable')
class TestStecosEngine(TestEngine):
    # Evaluation SDK replaces the second character of the decoded
    # value with a random character, so this test needs to do some extra work.
    def test_1d(self):
        res = StecosEngine(datamatrix=False)(self.CODE128)
        self.assertEqual(1, len(res))
        self.assertEqual('Code 128', res[0].type)
        self.assertEqual('egosaurus', res[0].data[2:])

    def test_dm(self):
        res = StecosEngine(datamatrix=True)(self.DATAMATRIX)
        self.assertEqual(1, len(res))
        self.assertEqual('Data Matrix', res[0].type)
        self.assertEqual('iceratops', res[0].data[2:])


@unittest.skipUnless(ZbarEngine.available(), 'ZbarEngine unavailable')
class TestZbarEngine(TestEngine):
    def test_1d(self):
        self._test_1d(ZbarEngine())

    def test_qr(self):
        self._test_qr(ZbarEngine(), type='QRCODE')


@unittest.skipUnless(ZxingEngine.available(), 'ZxingEngine unavailable')
class TestZxingEngine(TestEngine):
    def test_dm(self):
        self._test_dm(ZxingEngine())

if __name__ == '__main__':
    unittest.main()
