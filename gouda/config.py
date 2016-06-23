import importlib
import sys

from .util import debug_print

# TODO LH Licences for other engines?
# TODO LH Move to json or ini file?

_DEV = '.config_dev'
try:
    dev = importlib.import_module(_DEV, 'gouda')
except ImportError:
    # SOFTEK_LICENSE_KEY = ''
    # SOFTEK_BARDECODE = Path('')

    # LIBDMTX_DTMXREAD = Path('')

    # STECOS_DMREAD = Path('')
    # STECOS_READBAR = Path('')
    debug_print('Default config')
else:
    debug_print('Read config from [{0}]'.format(_DEV))

    thismodule = sys.modules[__name__]
    items = (
        'SOFTEK_LICENSE_KEY', 'SOFTEK_BARDECODE', 'LIBDMTX_DTMXREAD',
        'STECOS_DMREAD', 'STECOS_READBAR'
    )
    for item in items:
        value = getattr(dev, item, None)
        if value:
            setattr(thismodule, item, value)
