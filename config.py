import json


class Host:
    # __slots__ = ["name", "url", "user", "pass", "midiKey"]
    def __init__(self, name, url, user, pwd, midi_key):
        self.name = name
        self.url = url
        self.user = user
        self.pwd = pwd
        self.midiKey = midi_key


class Scene:
    # __slots__ = ["name", "ndi", "midiKey"]
    def __init__(self, name, ndi, midi_key):
        self.name = name
        self.ndi = ndi
        self.midiKey = midi_key


class Preset:
    # __slots__ = ["name", "assignations", "midiKey"]
    def __init__(self, name, assignations, midi_key):
        self.name = name
        self.assignations = assignations
        self.midiKey = midi_key


class Config:
    def __init__(self):
        self.hosts = {}
        self.presets = {}
        self.scenes = {}

    def import_raw(self, raw):
        self.hosts = raw["hosts"]
        self.presets = raw["presets"]
        self.scenes = raw["scenes"]

        return self

    def export_raw(self) -> dict:
        return {
            "hosts": self.hosts,
            "presets": self.presets,
            "scenes": self.scenes
        }

    def fetchPresetsNames(self):
        return [preset_name for preset_name in self.presets]

    def fetchClasses(self):
        hosts = {}
        for hostname in self.hosts:
            host_raw = self.hosts[hostname]
            host = Host(name=hostname, url=host_raw["url"], user=host_raw["user"],
                        pwd=host_raw["pass"], midi_key=host_raw["midi"])
            hosts[hostname] = host

        scenes = {}
        for scene_name in self.scenes:
            scene_raw = self.scenes[scene_name]
            scene = Scene(name=scene_name, ndi=scene_raw["value"], midi_key=scene_raw["midi"])
            scenes[scene_name] = scene

        presets = {}
        for preset_name in self.presets:
            preset_raw = self.presets[preset_name]
            assign = {}
            for host in preset_raw["command"]:
                assign[hosts[host]] = scenes[preset_raw["command"][host]]

            preset = Preset(name=preset_name, assignations=assign, midi_key=preset_raw["midi"])
            presets[preset_name] = preset

        return hosts, scenes, presets

    def fetchFromMidi(self):
        hosts, scenes, presets = self.fetchClasses()

        hosts_midi = {}
        for hostname in self.hosts:
            host_raw = self.hosts[hostname]
            host = Host(name=hostname, url=host_raw["url"], user=host_raw["user"],
                        pwd=host_raw["pass"], midi_key=host_raw["midi"])
            hosts_midi[host_raw["midi"]] = host

        scenes_midi = {}
        for scene_name in self.scenes:
            scene_raw = self.scenes[scene_name]
            scene = Scene(name=scene_name, ndi=scene_raw["value"], midi_key=scene_raw["midi"])
            scenes_midi[scene_raw["midi"]] = scene

        presets_midi = {}
        for preset_name in self.presets:
            preset_raw = self.presets[preset_name]
            assign = {}
            for host in preset_raw["command"]:
                assign[hosts[host]] = scenes[preset_raw["command"][host]]

            preset = Preset(name=preset_name, assignations=assign, midi_key=preset_raw["midi"])
            presets_midi[preset_raw["midi"]] = preset

        return hosts_midi, scenes_midi, presets_midi


class ConfigReader:
    def __init__(self, config_file="./config.json", _from=None):
        self.__config_file = config_file
        if _from is None:
            self.config = Config()
            self.readConfig()
        else:
            self.config = _from

    def read_config_raw(self):
        with open(self.__config_file) as file:
            raw = json.load(file)
        return raw

    def readConfig(self):
        raw = self.read_config_raw()
        self.config.import_raw(raw)

        return self.config

    def fetchClasses(self):
        return self.config.fetchClasses()

    def fetchFromMidi(self):
        return self.config.fetchFromMidi()

    def fetchPresetsNames(self):
        return self.config.fetchPresetsNames()

    def writeConfig(self, override=None):
        to_write = None
        if override is None:
            to_write = json.dumps(self.config.export_raw())
        elif type(override) == Config:
            to_write = json.dumps(override.export_raw())
        elif type(override) == dict:
            to_write = json.dumps(override)
        elif type(override) == str:
            to_write = override

        with open(self.__config_file, "w") as f:
            f.write(to_write)

        return to_write


if __name__ == "__main__":
    cfg = ConfigReader()

    classes = cfg.fetchClasses()
    midi = cfg.fetchFromMidi()
    print("brk point")
