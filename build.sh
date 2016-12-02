# Temporary solution until I get round to writing a makefile

set -e  # Exit on failure

echo Clean
find . -name "*pyc" -print0 | xargs -0 rm -rf
find . -name __pycache__ -print0 | xargs -0 rm -rf
rm -rf dist build cover

echo Check for presence of barcode engines
python -c "from gouda.engines import ZbarEngine; assert ZbarEngine.available()" || exit /b
python -c "from gouda.engines import LibDMTXEngine; assert LibDMTXEngine.available()" || exit /b

echo Tests
nosetests --with-coverage --cover-html --cover-inclusive --cover-erase --cover-tests --cover-package=gouda

echo Build
./setup.py sdist bdist_wheel --universal
pyinstaller --onefile --clean decode_barcodes.spec
