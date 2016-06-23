import sys

from pathlib import Path

JAR_PATH = Path(__file__).parent

if 'win32' == sys.platform:
    JAVA = Path('/Program Files/Java/jdk1.8.0_40/bin/java.exe')
else:
    JAVA = Path('/usr/bin/java')


def available():
    return JAVA.is_file()
