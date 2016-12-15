# gouda

<!---
Disabled due to lack of availability of recent Open CV build
[![Travis status](https://travis-ci.org/NaturalHistoryMuseum/gouda.svg?branch=master)](https://travis-ci.org/NaturalHistoryMuseum/gouda)
-->

A python package for decoding barcodes, possibly more than one, in complex
images such as scans of museum specimens.

Gouda supports Python 2.7, 3.4 and 3.5. A universal wheel build is available
on the [releases](https://github.com/NaturalHistoryMuseum/gouda/releases) page.

A command-line program `decode_barcodes` is available for Windows 64-bit and
Mac OS X. It reads barcode values in individual images and in batches of images
files in a directory. It can print values to CSV and can rename files with
the value(s) or barcode(s). Download from the
[releases](https://github.com/NaturalHistoryMuseum/gouda/releases) page.
For help run

    decode_barcodes --help

See also the [examples](#decode_barcodes-script) below.

## `gouda/engines`
An engine is an interface to a barcode reading library.
Gouda has engines for a number of open-source and commercial libraries.

### Open source
* [libdmtx](http://www.libdmtx.org/)
* [zbar](http://zbar.sourceforge.net/)
* [zxing](https://github.com/zxing/zxing/)

### Commercial
* [Accusoft](http://www.accusoft.com/)
* [Data Symbol](http://www.datasymbol.com/)
* [Inlite](http://www.inliteresearch.com/)
* [Stecos](http://www.stecos.net/)
* [Softek](http://www.bardecode.com/)

Not all libraries are available on all OSes. Gouda engines are currently
hard-coded to detect either Data Matrix or Code 128 + Code 39 barcodes -
those used by the [Natural History Musem](http://www.nhm.ac.uk/).

## gouda/strategies
No engines are capable of reliably locating and decoding (possibly multiple)
barcodes. Gouda provides two strategies to help the decoding engines.
If strategy A finds no barcodes, strategy B is attempted.

* Strategy A - shrink image until a barcode is found
    * this algorithm exits as soon as one or more barcodes are reported by the
      engine:
        * Present the image to the decoding library at 100%, 95%, 90%, 85%...5%
          of its original size
        * Sharpen the image and repeat 1
        * Sharpen the image even more and repeat 1
    * Strategy B
        * Use [OpenCV](http://www.opencv.org) to identify areas of the image
          that might contain barcodes
        * Present each candidate area to the engines

# Installation

## Python
**TODO** These instructions need updating for Python 3.
The easiest way is to install the current Python 2.7 release of
[Anaconda](https://store.continuum.io/cshop/anaconda/):

    conda update --all
    pip install --upgrade pip
    pip install -r requirements.pip
    conda install pywin32=220
    FOR /F %a IN ('python -c "import sys; print(sys.exec_prefix)"') DO %a\python %a\Scripts\pywin32_postinstall.py -install

## Install [OpenCV](http://www.opencv.org/)
### Linux

    conda install -c https://conda.binstar.org/menpo opencv

### OS X

    conda install -c https://conda.binstar.org/jjhelmus opencv

### Windows

Download [OpenCV 2.4.13](http://opencv.org/) and extract to `c:\opencv\`
If you installed 32-bit Anaconda:

    FOR /F %a IN ('python -c "import sys; print(sys.exec_prefix)"') DO copy C:\opencv\build\python\2.7\x86\cv2.pyd %a\DLLs

If you installed 64-bit Anaconda:

    FOR /F %a IN ('python -c "import sys; print(sys.exec_prefix)"') DO copy C:\opencv\build\python\2.7\x64\cv2.pyd %a\DLLs

Test by start Anaconda prompt and running

    python -c "import cv2; print cv2"

## Install decoders
### Accusoft
Windows only. Download and install their [SDK](http://www.accusoft.com/).

### DataSymbol
Windows only. Download and install their [SDK](http://www.datasymbol.com/).

### DTK
Windows 32-bit only. You must run 32-bit Python.
Download and install their [SDK](http://www.dtksoft.com/barreader.php).

### Inlite
Windows only. Download and install their [SDK](http://www.inliteresearch.com/).

### libdmtx

The [pylibdmtx](https://pypi.python.org/pypi/pylibdmtx/) Python package is
a dependency of `gouda` and is listed in `requirements.pip`.

The `libdmtx` `DLL`s are included with the Windows Python wheel builds
of `pylibdmtx`.
On other operating systems, you will need to install the `libdmtx` shared
library.

#### Linux

Install the `libdmtx` shared lib.

    sudo apt-get install libdmtx0a

#### OS X

Install the `libdmtx` shared lib.

    brew install libdmtx

### Softek
Linux, OS X and Windows.
Download and install their [SDK](http://www.bardecode.com/).

If on OS X or Linux, set `SOFTEK_BARDECODE` in `gouda/config.py` to the path
to the `bardecode` app provided with the SDK.

Enter your licence key in `SOFTEK_LICENSE_KEY` in `gouda/config.py`.

#### Windows

You may need to install the
[Visual C++ Redistributable Packages for Visual Studio 2013](http://www.microsoft.com/en-us/download/confirmation.aspx?id=40784)
before registering the COM controls.

You may need to use 'Run As Administrator' when registering the controls.

### Stecos
Tested on OS X only. Download and install their [SDK](http://www.stecos.net/).

On OS X:

    sudo cp ScMac64SDK/bin/*dylib /usr/lib/

Alter the readDM and readbar programs to print decoded data in the form 
'TYPE:DATA\\n' and recompile them. If on OS X or Linux, set `STECOS_DMREAD` and
`STECOS_READBAR` in `gouda/config.py` to the paths to the `readDM` and `readbar`
apps respectively, provided with the SDK.

### zbar

The [pyzbar](https://pypi.python.org/pypi/pyzbar/) Python package is
a dependency of `gouda` and is listed in `requirements.pip`.

The `zbar` `DLL`s are included with the Windows Python wheel builds
of `pyzbar`.
On other operating systems, you will need to install the `zbar` shared
library.

#### Linux

    sudo apt-get install libzbar-dev

#### Mac

Install the `zbar` library

    brew install zbar

#### Test

    python -c "import zbar; print(zbar)"

### zxing
Install a JDK.

    cd gouda/java/decode_data_matrix/
    ./build.sh

## Unit tests

    python -m unittest discover

## `decode_barcodes` script
These examples illustrate running the script from source.
If you downloaded `decode_barcodes` you should replace
`python -m gouda.scripts.decode_barcodes` with `decode_barcodes` in the
following examples.

### Print values of all 1d (Code 128) barcodes using the zbar library:

    python -m gouda.scripts.decode_barcodes zbar gouda/tests/test_data/code128.png
    gouda/tests/test_data/code128.png
    Found [1] barcodes:
    [0] [CODE128] [b'Stegosaurus']


### A terse (file per line) report of two files:

    python -m gouda.scripts.decode_barcodes zbar --action terse gouda/tests/test_data/code128.png gouda/tests/test_data/BM001128287.jpg
    gouda/tests/test_data/BM001128287.jpg [b'BM001128287'] [b'BM001128286'] [b'BM001128288']
    gouda/tests/test_data/code128.png [b'Stegosaurus']


### A rich csv report (file per line):

    python -m gouda.scripts.decode_barcodes zbar --action csv gouda/tests/test_data/code128.png gouda/tests/test_data/BM001128287.jpg
    OS,Engine,Directory,File,Image.conversion,Elapsed,N.found,Types,Values,Strategy
    darwin,zbar,test_data,BM001128287.jpg,Unchanged,0.7893128395080566,3,CODE128|CODE128|CODE128,BM001128287|BM001128286|BM001128288,resize: scaling factor [1.0] sharpening [0]
    darwin,zbar,test_data,code128.png,Unchanged,0.7991600036621094,1,CODE128,Stegosaurus,resize: scaling factor [1.0] sharpening [0]

### Reading images as greyscale
Greyscale can improve or degrade chances of finding barcodes, dependent upon 
the image and engine.

    python -m gouda.scripts.decode_barcodes zbar --action csv --greyscale gouda/tests/test_data/code128.png gouda/tests/test_data/BM001128287.jpg
    OS,Engine,Directory,File,Image.conversion,Elapsed,N.found,Types,Values,Strategy
    darwin,zbar,test_data,BM001128287.jpg,Greyscale,0.9049880504608154,3,CODE128|CODE128|CODE128,BM001128287|BM001128286|BM001128288,resize: scaling factor [1.0] sharpening [0]
    darwin,zbar,test_data,code128.png,Greyscale,0.9112460613250732,1,CODE128,Stegosaurus,resize: scaling factor [1.0] sharpening [0]

## Building a release

Mac OS X

    ./build.sh

On Windows

    build.bat
