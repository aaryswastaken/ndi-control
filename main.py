import tkinter as tk
import sys

import api
import config
import midi

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

cfg = config.ConfigReader()
hosts, scenes, presets = cfg.fetchClasses()
presets_names = cfg.fetchPresetsNames()

sender = api.Sender(cfg)

midi_inst = midi.MidiHandler(cfg, flags, sender)
flags = midi_inst.register()
print("Registered")

root = tk.Tk()

root.geometry("500x500")
root.title("NDI-Control")

l = tk.LabelFrame(root, text="Selection du preset", padx=20, pady=20)
l.pack(fill="both", expand="yes")

preset_selection = tk.StringVar(root)
preset_selection.set(presets_names[0])

opt = tk.OptionMenu(l, preset_selection, *presets_names)
opt.config(width=90, font=('Helvetica', 12))
opt.pack(side="top")

l2 = tk.LabelFrame(root, text="Commandes", padx=20, pady=20)
l2.pack(fill="both", expand="yes")


def sendcallback():
    print("Sending commands")
    sender.applyPresetFromName(preset_selection.get())


button = tk.Button(l2, text="Envoyer", command=sendcallback)
button.pack()


def callback(*args):
    print("The selected item is {}".format(preset_selection.get()))


preset_selection.trace("w", callback)

root.mainloop()
