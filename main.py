import json
import tkinter as tk
import sys

import api

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

try:
    with open("hosts.json") as host_file:
        hosts = json.load(host_file)

    with open("presets.json") as presets_file:
        presets = json.load(presets_file)

    with open("scenes.json") as scene_file:
        scenes = json.load(scene_file)
except FileNotFoundError:
    throw_error(
        "An error occured when parsing differents config files, please check README to know how to troubleshoot")

sender = api.Sender(hosts, presets, scenes)

presets_name = []

for preset in presets:
    presets_name.append(preset)

midi_mapping = {}

for preset in presets:
    midi_mapping[presets[preset]["midi"]] = preset

hostnames = []
midi_host_mapping = {}

for host in hosts:
    hostnames.append(host)
    midi_host_mapping[hosts[host]["midi"]] = host

scene_midi = {}

for scene in scenes:
    scene_midi[scenes[scene]["midi"]] = scene

sustain = False
isInProcess = False
processHost = ""


def on_key_touch(message):
    global sustain, isInProcess, processHost
    # print(message)
    if message.type == "control_change" and message.control == 64:
        sustain = message.value > 64
    elif message.type == "note_on" and message.velocity != 0:
        # print("As the key n {} is pressed, ".format(message.note))
        if sustain:
            if not isInProcess:
                try:
                    processHost = midi_host_mapping[message.note]
                    print("And the sustain, the host {} will be affected by the following scene".format(processHost))
                    isInProcess = True
                except:
                    print("Unknown host ... aborting")
            else:
                try:
                    scene = scene_midi[message.note]
                    print("The scene {} will be applied".format(scene))
                    sender.send(processHost, scene)
                    isInProcess = False
                except:
                    print("Unknown scene ... continuing")
        else:
            if isInProcess:
                print("Aborted")
                isInProcess = False
            else:
                try:
                    preset = midi_mapping[message.note]
                    print("The preset {} will be applied".format(preset))
                    preset_selection.set(preset)
                    sender.sendPreset(preset)
                except:
                    print("Sorry, there is no key defined with this one")


if not "nomidi" in flags:
    import mido

    midi = mido.open_input(callback=on_key_touch)

root = tk.Tk()

root.geometry("500x500")
root.title("NDI-Control")

l = tk.LabelFrame(root, text="Selection du preset", padx=20, pady=20)
l.pack(fill="both", expand="yes")

preset_selection = tk.StringVar(root)
preset_selection.set(presets_name[0])

opt = tk.OptionMenu(l, preset_selection, *presets_name)
opt.config(width=90, font=('Helvetica', 12))
opt.pack(side="top")

l2 = tk.LabelFrame(root, text="Commandes", padx=20, pady=20)
l2.pack(fill="both", expand="yes")


def sendcallback():
    print("Sending commands")
    sender.sendPreset(preset_selection.get())


button = tk.Button(l2, text="Envoyer", command=sendcallback)
button.pack()


def callback(*args):
    print("The selected item is {}".format(preset_selection.get()))


preset_selection.trace("w", callback)

root.mainloop()
