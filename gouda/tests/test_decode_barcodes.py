import os
import unittest
import shutil
import sys

from pathlib import Path
from contextlib import contextmanager

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


from gouda.engines import ZbarEngine
from gouda.scripts.decode_barcodes import main

from .utils import temp_directory_with_files



@contextmanager
def capture_stdout():
    sys.stdout, old_stdout = StringIO(), sys.stdout
    try:
        yield sys.stdout
    finally:
        sys.stdout = old_stdout


TESTDATA = Path(__file__).parent.joinpath('test_data')


@unittest.skipUnless(ZbarEngine.available(), 'ZbarEngine unavailable')
class TestRename(unittest.TestCase):
    def test_csv(self):
        "CSV report is printed"
        with capture_stdout() as stdout:
            main([
                'zbar',
                '--action=csv',
                str(TESTDATA.joinpath('code128.png')),
                str(TESTDATA.joinpath('BM001128287.jpg'))
            ])
        from pprint import pprint

        lines = stdout.getvalue().strip().split(os.linesep)
        self.assertEqual(3, len(lines))

        header = (
            'OS,Engine,Directory,File,Image.conversion,Elapsed,N.found,Types,'
            'Values,Strategy'
        )
        self.assertEqual(header, lines[0])

        self.assertIn('BM001128287.jpg', lines[1])
        self.assertIn('CODE128|CODE128|CODE128', lines[1])
        self.assertIn('BM001128287|BM001128286|BM001128288', lines[1])

        self.assertIn('code128.png', lines[2])
        self.assertIn('CODE128', lines[2])
        self.assertIn('Stegosaurus', lines[2])

    def test_rename(self):
        "File is renamed with value of barcode"
        with temp_directory_with_files(TESTDATA.joinpath('code128.png')) as tempdir:
            main(['zbar', '--action=rename', str(tempdir)])
            self.assertEqual(
                ['Stegosaurus.png'],
                [path.name for path in sorted(tempdir.iterdir())]
            )

    def test_rename_multiple(self):
        "File with multiple barcodes results in renamed / copied to three files"
        with temp_directory_with_files(TESTDATA.joinpath('BM001128287.jpg')) as tempdir:
            main(['zbar', '--action=rename', str(tempdir)])
            self.assertEqual(
                ['BM001128286.jpg', 'BM001128287.jpg', 'BM001128288.jpg'],
                [path.name for path in sorted(tempdir.iterdir())]
            )

    def test_rename_with_collisions(self):
        "Files with same barcode values results in just a single rename"
        with temp_directory_with_files(TESTDATA.joinpath('code128.png')) as tempdir:
            shutil.copy(
                str(TESTDATA.joinpath('code128.png')),
                str(tempdir.joinpath('first copy.png'))
            )

            shutil.copy(
                str(TESTDATA.joinpath('code128.png')),
                str(tempdir.joinpath('second copy.png'))
            )

            main(['zbar', '--action=rename', str(tempdir)])
            self.assertEqual(
                ['Stegosaurus.png', 'first copy.png', 'second copy.png'],
                [path.name for path in sorted(tempdir.iterdir(), key=lambda p: p.name)]
            )

    def test_rename_avoid_collisions(self):
        "Files with same barcode values results in new files with suffixes"
        with temp_directory_with_files(TESTDATA.joinpath('code128.png')) as tempdir:
            shutil.copy(
                str(TESTDATA.joinpath('code128.png')),
                str(tempdir.joinpath('first copy.png'))
            )

            shutil.copy(
                str(TESTDATA.joinpath('code128.png')),
                str(tempdir.joinpath('second copy.png'))
            )

            main(['zbar', '--action=rename', str(tempdir), '--avoid-collisions'])
            print([path.name for path in sorted(tempdir.iterdir())])
            self.assertEqual(
                ['Stegosaurus-1.png', 'Stegosaurus-2.png', 'Stegosaurus.png'],
                [path.name for path in sorted(tempdir.iterdir())]
            )


if __name__ == '__main__':
    unittest.main()
