import collections

from gouda.gouda_error import GoudaError

class Barcode(collections.namedtuple('Barcode', ['type', 'data'])):
    """A simple representation of a barcode
    """
    def __new__(cls, type, data):
        if not type:
            raise GoudaError('No type')
        elif not data:
            raise GoudaError('No data')
        else:
            return super(Barcode, cls).__new__(cls, type, data)
