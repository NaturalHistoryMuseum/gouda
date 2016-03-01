from functools import partial

from gouda.engines import (AccusoftEngine, DataSymbolEngine, DTKEngine,
                           InliteEngine, LibDMTXEngine, StecosEngine,
                           SoftekEngine, ZbarEngine, ZxingEngine)


def engine_options():
    """Returns a dict mapping textual descriptions to functions that return an
    engine.
    """
    options = {
        'libdmtx': LibDMTXEngine,
        'zbar': ZbarEngine,
        'zxing': ZxingEngine,
    }

    options = {k: v for k, v in options.iteritems() if v.available()}

    if AccusoftEngine.available():
        options.update({
            'accusoft-1d': partial(AccusoftEngine, datamatrix=False),
            'accusoft-dm': partial(AccusoftEngine, datamatrix=True),
        })

    if DataSymbolEngine.available():
        options.update({
            'datasymbol-1d': partial(DataSymbolEngine, datamatrix=False),
            'datasymbol-dm': partial(DataSymbolEngine, datamatrix=True),
        })

    if DTKEngine.available():
        options.update({
            'dtk-1d': partial(DTKEngine, datamatrix=False),
            'dtk-dm': partial(DTKEngine, datamatrix=True),
        })

    if InliteEngine.available():
        options.update({
            'inlite-1d': partial(InliteEngine, format='1d'),
            'inlite-dm': partial(InliteEngine, format='datamatrix'),
            'inlite-pdf417': partial(InliteEngine, format='pdf417'),
            'inlite-qrcode': partial(InliteEngine, format='qrcode'),
        })

    if StecosEngine.available():
        options.update({
            'stecos-1d': partial(StecosEngine, datamatrix=False),
            'stecos-dm': partial(StecosEngine, datamatrix=True),
        })

    if SoftekEngine.available():
        options.update({
            'softek-1d': partial(SoftekEngine, datamatrix=False),
            'softek-dm': partial(SoftekEngine, datamatrix=True),
        })

    return options
