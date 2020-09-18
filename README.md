# ndi-control
A python interface for ndi.tv tools "Studio Monitor" with gui and midi support

## Setup
#### Windows launching
1. Go to [the release page](https://github.com/CofeDrink68/ndi-control/releases) and download the latest release for windows
2. Decompress the zip archive
3. Add your config files (please refer to the config section)
4. Run ```main.exe```

#### Python launch
1. Go to [the release page](https://github.com/CofeDrink68/ndi-control/releases) and download the latest source code release
2. Decompress the archive
3. Run ```pip install mido python-rtmidi tkinter requests``` 
4. Add your config files
5. Run ```python main.py```

## Commands
```shell script
main.exe <args>
```
or
``` python main.py``` depending of your installation choices
Arguments are :

- ```-h``` or ```--help``` for help
- ```--no-midi``` to disable midi support

## Troubleshooting
|Error Code | Error |
|---|---|
| Unrecognised argument | An argument could not be parsed correctly |
| Config File | Watch the setup guide |