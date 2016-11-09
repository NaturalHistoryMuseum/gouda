from __future__ import print_function

import glob

from pathlib import Path

import cv2

try:
    from _winreg import OpenKey, HKEY_LOCAL_MACHINE
except ImportError:
    OpenKey = HKEY_LOCAL_MACHINE = None


DEBUG_PRINT = False


def debug_print(*args, **kwargs):
    # TODO LH Duplicated in inselect
    if DEBUG_PRINT:
        print(*args, **kwargs)


def read_image(path, greyscale):
    if greyscale:
        return cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    else:
        return cv2.imread(str(path))


def expand_wildcard(args):
    # Crummy solution to crummy windows shell behaviour
    paths = []
    for p in args:
        if '*' in p:
            paths += glob.glob(p)
        else:
            paths += [p]
    return [Path(p) for p in paths]


def is_clsid_registered(clsid):
    """Returns True if clsid is registered
    Returns False if the clsid is not registered or if not running on Windows
    """
    if OpenKey and HKEY_LOCAL_MACHINE:
        try:
            with OpenKey(HKEY_LOCAL_MACHINE, 'SOFTWARE\\Classes\\' + clsid):
                pass
        except WindowsError:
            # Key could not be opened => clsid is not registered
            return False
        else:
            # Key could be opened
            return True
    else:
        # Most likely not running on Windows
        return False
