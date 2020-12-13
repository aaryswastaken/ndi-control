import json


class Host:
    # __slots__ = ["name", "url", "user", "pass", "midiKey"]
    def __init__(self, name, url, user, pwd, midi_key, dummy):
        self.name = name
        self.url = url
        self.user = user
        self.pwd = pwd
        self.midiKey = midi_key
        self.dummy = dummy


class Scene:
    # __slots__ = ["name", "ndi", "midiKey"]
    def __init__(self, name, ndi, midi_key, dummy):
        self.name = name
        self.ndi = ndi
        self.midiKey = midi_key
        self.dummy = dummy


class Preset:
    # __slots__ = ["name", "assignations", "midiKey"]
    def __init__(self, name, assignations, midi_key):
        self.name = name
        self.assignations = assignations
        self.midiKey = midi_key


class General:
    def __init__(self):
        pass


class Section:
    def __init__(self):
        pass


class Config:
    def __init__(self):
        self.hosts = {}
        self.presets = {}
        self.scenes = {}
        self.general = {}

    def import_raw(self, raw):
        self.hosts = raw["hosts"]
        self.presets = raw["presets"]
        self.scenes = raw["scenes"]
        self.general = raw["general"]

        return self

    def export_raw(self) -> dict:
        return {
            "hosts": self.hosts,
            "presets": self.presets,
            "scenes": self.scenes,
            "general": self.general
        }

    def fetchPresetsNames(self):
        return [preset_name for preset_name in self.presets]

    def fetchSettings(self):
        settings = General()

        # setattr() is just a magic function that create a class property from a string

        for sectionName in self.general:
            section = Section()
            for setting in self.general[sectionName]:
                setattr(section, setting, self.general[sectionName][setting])

            setattr(settings, sectionName, section)

        return settings

    def settingExists(self, name, _settings=None):
        if _settings is None:
            settings = self.fetchSettings()
        else:
            settings = _settings

        splt = name.split(".")
        exists = True
        check = _settings
        for deepness in splt:
            exists = exists and hasattr(check, deepness)
            if not exists:
                break
            else:
                check = getattr(check, deepness)

        return exists

    def fetchClasses(self):
        hosts = {}
        for hostname in self.hosts:
            host_raw = self.hosts[hostname]
            dummy = host_raw["dummy"] if "dummy" in host_raw else False
            host = Host(name=hostname, url=host_raw["url"], user=host_raw["user"],
                        pwd=host_raw["pass"], midi_key=host_raw["midi"], dummy=dummy)
            hosts[hostname] = host

        scenes = {}
        for scene_name in self.scenes:
            scene_raw = self.scenes[scene_name]
            dummy = scene_raw["dummy"] if "dummy" in scene_raw else False
            scene = Scene(name=scene_name, ndi=scene_raw["value"], midi_key=scene_raw["midi"], dummy=dummy)
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
            # host_raw = self.hosts[hostname]
            # host = Host(name=hostname, url=host_raw["url"], user=host_raw["user"],
            #             pwd=host_raw["pass"], midi_key=host_raw["midi"])
            # hosts_midi[host_raw["midi"]] = host
            hosts_midi[hosts[hostname].midiKey] = hosts[hostname]

        scenes_midi = {}
        for scene_name in self.scenes:
            # scene_raw = self.scenes[scene_name]
            # scene = Scene(name=scene_name, ndi=scene_raw["value"], midi_key=scene_raw["midi"])
            # scenes_midi[scene_raw["midi"]] = scene
            scenes_midi[scenes[scene_name].midiKey] = scenes[scene_name]


        presets_midi = {}
        for preset_name in self.presets:
            # preset_raw = self.presets[preset_name]
            # assign = {}
            # for host in preset_raw["command"]:
            #     assign[hosts[host]] = scenes[preset_raw["command"][host]]
            #
            # preset = Preset(name=preset_name, assignations=assign, midi_key=preset_raw["midi"])
            # presets_midi[preset_raw["midi"]] = preset
            presets_midi[presets[preset_name].midiKey] = presets[preset_name]

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

    def fetchSettings(self):
        if hasattr(self, "settings"):  # This is used only to have the same Hosts ... instances every call
            return self.settings
        else:
            self.settings = self.config.fetchSettings()
            return self.fetchSettings()

    def settingExists(self, name, _settings=None):
        return self.config.settingExists(name=name, _settings=_settings)

    def fetchClasses(self):
        if hasattr(self, "hosts") and hasattr(self, "presets") and hasattr(self, "scenes"):  # This is used only to have the same Hosts ... instances every call
            return self.hosts, self.presets, self.scenes
        else:
            self.hosts, self.presets, self.scenes = self.config.fetchClasses()
            return self.fetchClasses()

    def fetchFromMidi(self):
        if hasattr(self, "hosts_midi") and hasattr(self, "presets_midi") and hasattr(self, "scenes_midi"):  # This is used only to have the same Hosts ... instances every call
            return self.hosts_midi, self.presets_midi, self.scenes_midi
        else:
            self.hosts_midi, self.presets_midi, self.scenes_midi = self.config.fetchFromMidi()
            return self.fetchFromMidi()

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
    settings = cfg.fetchSettings()
    print(cfg.settingExists("matrix.doesHostTurnRedWhenLocked", _settings=settings))
    print("brk point")
