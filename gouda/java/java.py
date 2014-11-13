from pathlib import Path

JAR_PATH = Path(__file__).parent
JAVA = Path('/usr/bin/java')

def available():
    return JAVA.is_file()
