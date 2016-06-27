# Temporary solution until I get round to writing a makefile

set -e  # Exit on failure

echo Clean
find . -name "*pyc" -print0 | xargs -0 rm -rf
find . -name __pycache__ -print0 | xargs -0 rm -rf
rm -rf *spec dist build cover

echo Tests
nosetests --with-coverage --cover-html --cover-inclusive --cover-erase --cover-tests --cover-package=gouda

echo Build
./setup.py sdist
pyinstaller --onefile --specpath=build gouda/scripts/decode_barcodes.py
