import sys

import api
import config
import midi
import gui

flags = []

flags_definition = {
    "--no-midi": "nomidi",
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
    print(" -h  --help     : Shows help")
    print(" --no-midi      : Deactivate midi input")
    exit(0)

# ---------- CONFIG READ ----------
cfg = config.ConfigReader()

# ---------- SENDER ----------
sender = api.Sender(cfg)

# ---------- MIDI ----------
midi_inst = midi.MidiHandler(cfg, flags, sender)
flags = midi_inst.register()
# print("Registered")

# ---------- GUI ----------
gui.GUI(cfg, sender)  # [WARN] This is a blocking function
