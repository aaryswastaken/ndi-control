class MidiHandler:
    def __init__(self, cfg, flags, sender):
        self.sustain = False
        self.isInProcess = False
        self.processHost = ""

        self.cfg = cfg
        self.hosts_midi, self.scenes_midi, self.presets_midi = cfg.fetchFromMidi()
        self.flags = flags
        self.sender = sender

    def register(self):
        self.midi = None

        if "nomidi" not in self.flags:
            try:
                import mido
                self.midi = mido.open_input(callback=self.on_key_touch)
            except OSError or IOError:
                print("[WARN] No midi device connected ! Use the argument --no-midi to disable this warning")
                self.flags.append("nomidi")

        return self.flags

    def on_key_touch(self, message):
        print("Key touched !")
        # print(message)
        if message.type == "control_change" and message.control == 64:
            sustain = message.value > 64
        elif message.type == "note_on" and message.velocity != 0:
            # print("As the key n {} is pressed, ".format(message.note))
            if self.sustain:
                if not self.isInProcess:
                    try:
                        # processHost = midi_host_mapping[message.note]
                        processHost = self.hosts_midi[message.note]
                        print("And the sustain, the host {} will be affected by the following scene".format(processHost.name))
                        isInProcess = True
                    except:
                        print("Unknown host ... aborting")
                else:
                    try:
                        # scene = scene_midi[message.note]
                        scene = self.scenes_midi[message.note]
                        print("The scene {} will be applied".format(scene.name))
                        self.sender.applySceneToHost(host=self.processHost, scene=scene)
                        isInProcess = False
                    except:
                        print("Unknown scene ... continuing")
            else:
                if self.isInProcess:
                    print("Aborted")
                    isInProcess = False
                else:
                    try:
                        # preset = midi_mapping[message.note]
                        preset = self.presets_midi[message.note]
                        print("The preset {} will be applied".format(preset.name))
                        self.sender.applyPreset(preset=preset)
                    except:
                        print("Sorry, there is no key defined with this one")
        print("Exited")
