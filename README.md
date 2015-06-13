# gouda

<!---
Disabled due to lack of availability of recent Open CV build
[![Travis status](https://travis-ci.org/NaturalHistoryMuseum/gouda.svg?branch=master)](https://travis-ci.org/NaturalHistoryMuseum/gouda)
-->

A python package for decoding barcodes, possibly more than one, in complex
images such as scans of museum specimens.

## gouda/engines
Barcode decoding engines. An engine is an interface to a barcode reading 
library. Engines for both open-source and commercial libraries are provided.

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
The easiest way is to install the current Python 2.7 release of
[Anaconda](https://store.continuum.io/cshop/anaconda/):

    conda update --all
    conda update --all
    pip install --upgrade pip
    python <Anaconda dir>\Scripts\pywin32_postinstall.py -install
    pip install -r requirements.txt

## Install [OpenCV](http://www.opencv.org/)
Linux

    conda install -c https://conda.binstar.org/menpo opencv

OS X

    conda install -c https://conda.binstar.org/jjhelmus opencv

Windows

Download [OpenCV 2.4.10](http://opencv.org/) and extract to c:\opencv\
If you installed 32-bit Anaconda:

    copy C:\opencv\build\python\2.7\x86\cv2.pyd C:\Users\lawh\Anaconda\DLLs`

If you installed 64-bit Anaconda:

    copy C:\opencv\build\python\2.7\x64\cv2.pyd C:\Users\lawh\Anaconda\DLLs`

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

#### Windows

Download and install the appropriate build of `pydmtx` from
[dmtx-wrapper](https://github.com/NaturalHistoryMuseum/dmtx-wrappers/):

    pip install pydmtx-<whatever>.whl

Test

    python -c "import pydmtx; print(pydmtx)"

#### Linux

Library and utils

    sudo apt-get install libdmtx-dev libdmtx-utils

Python lib

    git clone git://libdmtx.git.sourceforge.net/gitroot/libdmtx/dmtx-wrappers
    cd dmtx-wrappers/python
    python setup.py install
    python -c "import pydmtx; print(pydmtx)"
    python test.py

#### OS X

Source

    git clone git://libdmtx.git.sourceforge.net/gitroot/libdmtx/libdmtx
    git clone git://libdmtx.git.sourceforge.net/gitroot/libdmtx/dmtx-wrappers
    git clone git://libdmtx.git.sourceforge.net/gitroot/libdmtx/dmtx-utils

Library

    cd libdmtx
    git checkout v0.7.4
    ./autogen.sh
    ./configure
    make
    make install

Python lib

    cd ../dmtx-wrappers/
    ./autogen.sh
    ./configure
    make

    cd python
    python setup.py install
    python -c "import pydmtx; print(pydmtx)"

Command-line tools (not used but might be useful to you)

    cd ../dmtx-utils
    brew install imagemagick
    git checkout v0.7.4
    ./autogen.sh
    ./configure
    make

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
#### Linux without anaconda

    sudo apt-get install libzbar-dev
    pip install zbar

#### Linux anaconda

    conda install --channel https://conda.binstar.org/weiyan zbar

#### Windows 32-bit
Download and run the `zbar-0.10` [windows installer](http://zbar.sourceforge.net/download.html); 
check 'Development Headers and Libraries'. Modify your `PATH` to include
`C:\Program Files (x86)\ZBar\bin`

    pip install --global-option=build_ext --global-option="-IC:/Program Files (x86)/ZBar/include" --global-option="-LC:/Program Files (x86)/ZBar/lib" zbar

#### Windows 64-bit
Download and install the build from
[zbar](https://github.com/NaturalHistoryMuseum/ZBarWin64/):

    pip install zbar-<whatever>.whl

Test

    python -c "import zbar; print(zbar)"

#### Mac
The pip install of zbar on my Mac resulted in a segfault on `import zbar`.
I compiled zbar-0.10.tar.bz2 from [source](http://zbar.sourceforge.net/download.html).

### zxing
Install a JDK.

    cd gouda/java/decode_data_matrix/
    ./build.sh

## Test

    python -m unittest discover

## Examples
Print values of all 1d (Code 128) barcodes using the zbar library:

    ./gouda/bin/decode_barcode.py zbar gouda/test/test_data/code128.png 

A terse (file per line) report of two files:

    ./gouda/bin/decode_barcode.py zbar --report=terse gouda/test/test_data/code128.png gouda/test/test_data/BM001128287.jpg

A rich csv report (file per line):

    ./gouda/bin/decode_barcode.py zbar --report=csv gouda/test/test_data/code128.png gouda/test/test_data/BM001128287.jpg

Reading images as greyscale

    ./gouda/bin/decode_barcode.py zbar --report=csv --greyscale gouda/test/test_data/code128.png gouda/test/test_data/BM001128287.jpg

Greyscale can improve or degrade chances of finding barcodes, dependent upon 
the image and engine.
