import unittest
import shutil

from pathlib import Path

from gouda.engines import ZbarEngine
from gouda.scripts.decode_barcodes import main

from utils import temp_directory_with_files


TESTDATA = Path(__file__).parent.joinpath('test_data')


@unittest.skipUnless(ZbarEngine.available(), 'ZbarEngine unavailable')
class TestRename(unittest.TestCase):
    def test_rename(self):
        "File is renamed with value of barcode"
        with temp_directory_with_files(TESTDATA.joinpath('code128.png')) as tempdir:
            main(['zbar', '--action=rename', unicode(tempdir)])
            self.assertEqual(
                ['Stegosaurus.png'],
                [path.name for path in sorted(tempdir.iterdir())]
            )

    def test_rename_multiple(self):
        "File with multiple barcodes results in renamed / copied to three files"
        with temp_directory_with_files(TESTDATA.joinpath('BM001128287.jpg')) as tempdir:
            main(['zbar', '--action=rename', unicode(tempdir)])
            self.assertEqual(
                ['BM001128286.jpg', 'BM001128287.jpg', 'BM001128288.jpg'],
                [path.name for path in sorted(tempdir.iterdir())]
            )

    def test_rename_with_collisions(self):
        "Files with same barcode values results in just a single rename"
        with temp_directory_with_files(TESTDATA.joinpath('code128.png')) as tempdir:
            shutil.copy(
                unicode(TESTDATA.joinpath('code128.png')),
                unicode(tempdir.joinpath('first copy.png'))
            )

            shutil.copy(
                unicode(TESTDATA.joinpath('code128.png')),
                unicode(tempdir.joinpath('second copy.png'))
            )

            main(['zbar', '--action=rename', unicode(tempdir)])
            self.assertEqual(
                ['Stegosaurus.png', 'first copy.png', 'second copy.png'],
                [path.name for path in sorted(tempdir.iterdir(), key=lambda p: p.name)]
            )

    def test_rename_avoid_collisions(self):
        "Files with same barcode values results in new files with suffixes"
        with temp_directory_with_files(TESTDATA.joinpath('code128.png')) as tempdir:
            shutil.copy(
                unicode(TESTDATA.joinpath('code128.png')),
                unicode(tempdir.joinpath('first copy.png'))
            )

            shutil.copy(
                unicode(TESTDATA.joinpath('code128.png')),
                unicode(tempdir.joinpath('second copy.png'))
            )

            main(['zbar', '--action=rename', unicode(tempdir), '--avoid-collisions'])
            print([path.name for path in sorted(tempdir.iterdir())])
            self.assertEqual(
                ['Stegosaurus-1.png', 'Stegosaurus-2.png', 'Stegosaurus.png'],
                [path.name for path in sorted(tempdir.iterdir())]
            )


if __name__ == '__main__':
    unittest.main()
