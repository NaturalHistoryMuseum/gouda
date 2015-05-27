import unittest

from pathlib import Path

from gouda.engines import InliteEngine, LibDMTXEngine, ZbarEngine, SoftekEngine
from gouda.strategies.roi.roi import roi
from gouda.strategies.resize import resize

import cv2


TESTDATA = Path(__file__).parent / 'test_data'


class TestStrategies(unittest.TestCase):
    """Test strategies on real-world scans of specimens
    """
    # An engine that can read 1d barcodes
    ONED_ENGINE = ( (InliteEngine('1d') if InliteEngine.available() else None) or
                    (ZbarEngine() if ZbarEngine.available() else None) or 
                    (SoftekEngine(False) if SoftekEngine.available() else None)
                  )

    # An engine that can read Data Matrix barcodes
    DM_ENGINE = ( (InliteEngine('datamatrix') if InliteEngine.available() else None) or
                  (LibDMTXEngine() if LibDMTXEngine.available() else None) or 
                  (SoftekEngine(True) if SoftekEngine.available() else None)
                )

    def _test(self, file, engine, strategy, expected):
        img = cv2.imread(str(TESTDATA / file))
        method,barcodes = strategy(img, engine)
        actual = sorted([b.data for b in barcodes])
        self.assertEqual(sorted(expected), actual)
        return method,barcodes

    def _test_1d(self, strategy):
        expected = ['BM001128286','BM001128287','BM001128288']
        return self._test('BM001128287.jpg',
                          self.ONED_ENGINE,
                          strategy,
                          expected)

    def _test_dm(self, strategy):
        expected = ['1265025']
        return self._test('BMNHE_1265025.jpg',
                          self.DM_ENGINE,
                          strategy,
                          expected)

    @unittest.skipUnless(ONED_ENGINE,
                         'No available engine for reading 1d codes')
    def test_1d_resize(self):
        self._test_1d(resize)

    @unittest.skipUnless(ONED_ENGINE,
                         'No available engine for reading 1d codes')
    def test_1d_roi(self):
        self._test_1d(roi)

    @unittest.skipUnless(DM_ENGINE,
                         'No available engine for reading Data Matrix codes')
    def test_dm_resize(self):
        self._test_dm(resize)

    @unittest.skipUnless(DM_ENGINE,
                         'No available engine for reading Data Matrix codes')
    def test_dm_roi(self):
        self._test_dm(roi)

    @unittest.skipUnless(ONED_ENGINE,
                         'No available engine for reading 1d codes')
    def test_no_barcode_resize(self):
        img = cv2.imread(str(TESTDATA / 'nobarcode.png'))
        self.assertIsNone(resize(img, self.ONED_ENGINE))

    @unittest.skipUnless(ONED_ENGINE,
                         'No available engine for reading 1d codes')
    def test_no_barcode_roi(self):
        img = cv2.imread(str(TESTDATA / 'nobarcode.png'))
        self.assertIsNone(roi(img, self.ONED_ENGINE))


if __name__=='__main__':
    unittest.main()
