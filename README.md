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

## Settings
Settings consists of three files :
- ```hosts.json``` that contains all displays
- ```presets.json``` contains every presets (ex : send scene A to every screens) and midi assignation
- ```scenes.json``` defines all ndi channels 

### MIDI
The midi control can do 2 things : 
- ```Auto mode``` : activate presets (pre-written sets of "this screens shows this ndi channel")
- ```Manual mode``` : can affect a specific channel to a specific screen, without using any preset

Manual mode can be used as follow : 
1. Press the sustain button without releasing
2. Press on the key that correspond to the screen that you want to affect the channel to 
3. Press on the key that correspond to the channel you want
4. Release the sustain button

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