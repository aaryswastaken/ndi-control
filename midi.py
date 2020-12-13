class MidiHandler:
    def __init__(self, cfg, flags, sender, gui):
        self.sustain = False
        self.isInProcess = False
        self.processHost = ""

        self.cfg = cfg
        self.hosts_midi, self.scenes_midi, self.presets_midi = cfg.fetchFromMidi()
        # This is a non robust but only way to get it working :
        # get the host from the midi key
        # get the REAL host class from the previous host's name and host thing
        self.hosts, self.scenes, self.presets = cfg.fetchClasses()
        self.flags = flags
        self.sender = sender
        self.gui = gui

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
        # print("Key touched !")
        # print(message)
        if message.type == "control_change" and message.control == 64:
            self.sustain = message.value > 64
        elif message.type == "note_on" and message.velocity != 0:
            if self.sustain:
                if not self.isInProcess:
                    try:
                        # self.processHost = midi_host_mapping[message.note]
                        self.processHost = self.hosts[self.hosts_midi[message.note].name]
                        print("And the sustain, the host {} will be affected by the following scene".format(self.processHost.name))
                        self.isInProcess = True
                    except:
                        print("Unknown host ... aborting")
                else:
                    try:
                        # scene = scene_midi[message.note]
                        print(f'{str(type(message.note))} {str(type(self.scenes_midi[message.note]))} '
                              f'{str(type(self.scenes[self.scenes_midi[message.note].name]))}')
                        scene = self.scenes[self.scenes_midi[message.note].name]
                        print("The scene {} will be applied to the host {}".format(scene.name, self.processHost.name))
                        # self.sender.applySceneToHost(host=self.processHost, scene=scene)
                        self.gui.affectHostToScene(host=self.processHost, scene=scene)
                        self.isInProcess = False
                    except:
                        print("Unknown scene ... continuing")
            else:
                if self.isInProcess:
                    print("Aborted")
                    self.isInProcess = False
                else:
                    try:
                        # preset = midi_mapping[message.note]
                        preset = self.presets[self.presets_midi[message.note].name]
                        print("The preset {} will be applied".format(preset.name))
                        # self.sender.applyPreset(preset=preset)
                        self.gui.applyPreset(preset)
                    except:
                        print("Sorry, there is no key defined with this one")
        # print("Exited")
