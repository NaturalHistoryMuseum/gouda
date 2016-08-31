REM Temporary solution until I get round to writing a makefile

echo Clean
del /S *pyc
rmdir /Q /S dist build

echo Check for presence of barcode engines
python -c "from gouda.engines import ZbarEngine; assert ZbarEngine.available()" || exit /b
python -c "from gouda.engines import LibDMTXEngine; assert LibDMTXEngine.available()" || exit /b
python -c "from gouda.engines import InliteEngine; assert InliteEngine.available()" || exit /b

echo Tests
nosetests --with-coverage --cover-html --cover-inclusive --cover-erase --cover-tests --cover-package=gouda || exit /b

pyinstaller --onefile --clean decode_barcodes.spec || exit /b
