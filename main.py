import sys
import tkinter as tk

import api
import config
import midi
import gui

# ACTUAL EXPERIMENTAL STATE :
# Beggining of the implementation of the settings page at the beginning
# -> Not loading actual parameters
# -> Has no effect on then (no saving)
# But global mechanic of gui switching is done

# TODO : Implement the "Before" Button
# For other TODOs, check in the files

flags = []

flags_definition = {
    "--no-midi": "nomidi",
    "--experimental": "exp",
    "-e": "exp",
    "-h": "help",
    "--help": "help"
}


def throw_error(error_msg):
    print(error_msg)
    print()
    input("Press any key to continue ... ")
    exit(1)


if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        if arg in flags_definition:
            flag = flags_definition[arg]
            if flag in flags:
                pass
            else:
                flags.append(flag)
        else:
            throw_error("Unrecognised argument \"{}\"".format(arg))

if "help" in flags:
    print("Welcome to the NDI-Control help command")
    print()
    print(" -h  --help          : Shows help")
    print(" --no-midi           : Deactivate midi input")
    print(" -e --experimental   : Force experimental features /!\\ DO NOT USE IT IN PRODUCTION")
    exit(0)

# ---------- CONFIG READ ----------
cfg = config.ConfigReader()

# ---------- SENDER ----------
sender = api.Sender(cfg)

# ---------- GUI ----------
dispController = gui.DispositionControl(cfg=cfg)
mainGUI = gui.GUI(cfg=cfg, control=dispController, sender=sender)  # [WARN] This is a blocking function
if "exp" in flags:
    settingsGUI = gui.SettingsGUI(cfg=cfg)

# ---------- MIDI ----------
if "nomidi" not in flags:
    midi_inst = midi.MidiHandler(cfg, flags, sender, gui=mainGUI)
    flags = midi_inst.register()


# print("Registered")


# START
def onSettingsFinished():
    mainGUI.presets()
    mainGUI.controls()
    mainGUI.matrix()
    mainGUI.main_loop()


if "exp" in flags:
    settings = cfg.fetchSettings()
    if cfg.settingExists("settings.showOnStartup", _settings=settings):
        if settings.settings.showOnStartup:
            settingsGUI.show(callback=onSettingsFinished)
else:
    onSettingsFinished()
