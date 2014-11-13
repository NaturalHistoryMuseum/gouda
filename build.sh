coverage run -m unittest discover &&
    coverage report &&
    coverage html &&
    ./setup.py sdist &&
    pyinstaller --onefile --specpath=build gouda/bin/decode_barcode.py
