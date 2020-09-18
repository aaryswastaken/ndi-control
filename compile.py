# TO COMPILE :
#  pip install mido python-rtmidi cx-freeze
#  python compile.py build

from cx_Freeze import setup, Executable

setup(
    name = "NDI-Control",
    version = "1",
    description = "console de gestion pour ndi",
    executables = [Executable("main.py")],
    options = {
        "build_exe": {
            "packages": [
                "mido",
                "rtmidi"
            ]
        }
    }
)