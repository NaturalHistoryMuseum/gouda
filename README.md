# gouda
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

    pip install -r requirements.txt

## Install [OpenCV](http://www.opencv.org/)
Linux

    conda install -c https://conda.binstar.org/menpo opencv

OS X

    conda install -c https://conda.binstar.org/jjhelmus opencv

Windows
    Download and install [OpenCV 2.4.9](http://opencv.org/)

## Install decoders
### Accusoft
Windows only. Download and install their [SDK](http://www.accusoft.com/).

### DataSymbol
Windows only. Download and install their [SDK](http://www.datasymbol.com/).

### Inlite
Windows only. Download and install their [SDK](http://www.inliteresearch.com/).

### libdmtx
Tested on OS X and Linux only.

    git clone git://libdmtx.git.sourceforge.net/gitroot/libdmtx/libdmtx
    git clone git://libdmtx.git.sourceforge.net/gitroot/libdmtx/dmtx-utils

    cd libdmtx
    ./autogen.sh
    ./configure
    make
    make install

    cd ../libdmtx-dmtx-utils
    brew install imagemagick
    ./autogen.sh
    ./configure
    make

    ./dmtxread/dmtxread -n -N1 Untitled.jpg

Set `LIBDMTX_DTMXREAD` in `gouda/config.py` to the path to the `dmtxread` app
provided with the SDK.

The Python wrappers are not required by gouda (I have not investigated these)
but you may wish to get them for completeness.

    git clone git://libdmtx.git.sourceforge.net/gitroot/libdmtx/dmtx-wrappers

    cd ../dmtx-wrappers/
    ./autogen.sh
    ./configure
    make

    cd python
    ./autogen.sh
    ./configure
    make
    python setup.py install
    python -c "import pydmtx; print(pydmtx)"


## Softek
Linux, OS X and Windows.
Download and install their [SDK](http://www.bardecode.com/).

If on OS X or Linux, set `SOFTEK_BARDECODE` in `gouda/config.py` to the path
to the `bardecode` app provided with the SDK.

Enter your licence key in `SOFTEK_LICENSE_KEY` in `gouda/config.py`.

### Stecos
Tested on OS X only. Download and install their [SDK](http://www.stecos.net/).

On OS X:

    sudo cp ScMac64SDK/bin/*dylib /usr/lib/

Alter the readDM and readbar programs to print decoded data in the form 
'TYPE:DATA\\n' and recompile them. If on OS X or Linux, set `STECOS_DMREAD` and
`STECOS_READBAR` in `gouda/config.py` to the paths to the `readDM` and `readbar`
apps respectively, provided with the SDK.

### zbar
The pip install of zbar on my Mac resulted in a segfault on `import zbar`.
I compiled zbar from [source](http://zbar.sourceforge.net/).

Linux:

    conda install --channel https://conda.binstar.org/weiyan zbar

Windows:

It would be better to set include and link paths rather than copy files around.

* Download and run the `zbar-0.10` [windows installer](http://zbar.sourceforge.net/download.html)
* Copy contents of `C:\Program Files\ZBar\include to `C:\Users\<yourname>\appdata\Local\Continuum\Anaconda\include\`
* Copy `C:\Program Files\ZBar\lib\libzbar.dll.a` to `C:\Users\<yourname>\appdata\Local\Continuum\Anaconda\libs\`
* Copy dlls in `C:\Program Files\ZBar\bin` to `C:\Users\<yourname>\appdata\Local\Continuum\Anaconda\`
* pip install zbar

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
