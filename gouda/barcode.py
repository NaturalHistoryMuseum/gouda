import collections

from gouda.gouda_error import GoudaError

class Barcode(collections.namedtuple('Barcode', ['type', 'data'])):
    """A simple representation of a barcode
    """
    pass
