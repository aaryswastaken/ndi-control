import tkinter as tk
from tkinter import messagebox
import settings
import json

SELECTED_COLOR = "#43bf64"
STANDBY_COLOR = "#dedede"
RED_COLOR = "#d65a66"
BEFORE_COLOR = "#ebc334"


class Button:
    def __init__(self, x=None, y=None, isSelected=False, isLocked=False, host=None, scene=None, root=None,
                 locker=False, line=None, cfg=None):
        self.root = root
        self.x_index = x
        self.y_index = y
        self.host = host
        self.scene = scene
        self.locker = locker
        self.isSelected = isSelected
        self.isLocked = isLocked
        self.line = line
        self.cfg = cfg

    def draw(self):
        self.button = tk.Button(
            self.root,
            width=15,
            height=5,
            bg=STANDBY_COLOR,
            bd=0,
            command=self.callback,
        )

        self.button.grid(row=self.y_index, column=self.x_index, sticky="nsew", padx=10, pady=10)

    def select(self):
        self.isSelected = True
        self.refresh()

    def unselect(self):
        self.isSelected = False
        self.refresh()

    def callback(self):
        if not self.locker:
            self.line.affectToScene(self.scene)
        else:
            self.line.toggleLock()

    def refresh(self):
        if not self.locker:
            settings = self.cfg.fetchSettings()
            color = SELECTED_COLOR
            if self.cfg.settingExists("matrix.doesHostTurnRedWhenLocked", _settings=settings):
                if settings.matrix.doesHostTurnRedWhenLocked:
                    color = RED_COLOR if self.line.locked else SELECTED_COLOR
            self.button.configure(bg=STANDBY_COLOR if not self.isSelected else color)
        else:
            self.button.configure(bg=STANDBY_COLOR if not self.line.locked else RED_COLOR)


class Line:
    def __init__(self, host, scenes, root, y_index, parent, cfg):
        self.host = host
        self.scenes = scenes
        self.root = root
        self.y_index = y_index
        self.parent = parent
        self.drawn = False
        self.locked = False
        self.selected = None
        self.cfg = cfg

    def toggleLock(self):
        if self.locked:
            self.unlock()
        else:
            self.lock()

    def refreshAll(self):
        self.locker.refresh()
        for identifier in self.buttons:  # Actually, the identifier is the scene
            self.buttons[identifier].refresh()

    def unlock(self):
        self.locked = False
        self.refreshAll()

    def lock(self):
        self.locked = True
        self.refreshAll()

    def affectToScene(self, scene, force=True) -> bool:
        if self.locked:
            return False

        if self.drawn:
            for identifier in self.buttons:  # Actually, the identifier is the scene
                self.buttons[identifier].unselect()

            self.buttons[scene].select()
            self.selected = scene
            self.parent.refreshControl()
            return True
        else:
            if force:
                print("[WARN] Had to automatically draw the line, please check the code")
                self.draw()
                return self.affectToScene(scene)  # start again
            else:
                print("[ERROR] The line wasn't drawn before affect call")
                return False

    def draw(self):  # Described by : <tk.Label> | (<gui.Button>) x nScenes | <gui.Button>
        # This is the left label, defining the line's host
        self.lineLabel = tk.Label(self.root, text=self.host.name)
        self.lineLabel.grid(row=self.y_index, column=0)

        # These are the buttons to select the source
        self.buttons = {}

        for i, sceneName in enumerate(self.scenes):
            button = Button(x=i + 1, y=self.y_index, host=self.host, scene=self.scenes[sceneName],
                            root=self.root, line=self, cfg=self.cfg)
            button.draw()
            self.buttons[self.scenes[sceneName]] = button

        # This one is the locker button
        self.locker = Button(x=len(self.scenes) + 1, y=self.y_index, host=self.host, locker=True,
                             root=self.root, line=self)
        self.locker.draw()

        self.drawn = True


class Disposition:
    def __init__(self):
        self.disposition = {}

    def fromLines(self, lines):
        self.disposition = dict({host: lines[host].selected for host in lines})
        return self

    # def toLine(self):
    #     return dict(self.disposition)


class DispositionControl:
    def __init__(self, cfg):
        self.actual = Disposition()
        self.last = Disposition()
        self.cfg = cfg

    def loadFromLines(self, lines):
        return self.actual.fromLines(lines)

    def archiveVersion(self):
        # self.last.disposition = dict(self.actual.disposition)
        self.saveToJson(self.actual)
        for host in self.actual.disposition:
            self.last.disposition[host] = self.actual.disposition[host]

    def saveToJson(self, disposition, filename="./autosave.json"):
        with open(filename, "w") as f:
            finalJSON = {}
            for host in disposition.disposition:
                finalJSON[host.name] = disposition.disposition[host].name
            json.dump(finalJSON, f)

    def loadFromJson(self, filename="./autosave.json"):
        with open(filename) as f:
            hosts, scenes, presets = self.cfg.fetchClasses()
            final = {}
            js = json.load(f)
            for hostname in js:
                final[hosts[hostname]] = scenes[js[hostname]]

        return final

    def loadFromDict(self, _dict):
        self.actual.disposition = _dict

    # def dumpToLine(self, js):
    #     finalJSON = {}
    #     hosts, scenes, presets = self.cfg.fetchClasses()
    #
    #     for host in js:
    #         finalJSON[hosts] = hosts[host]
    #
    #     return finalJSON

    def computeDifferences(self, a=None, b=None):  # Return parts of a when different of b
        a = self.actual if a is None else a
        b = self.last if b is None else b

        d = {}

        if b.disposition is None:
            return a.disposition

        for host in a.disposition:
            if host in b.disposition:
                if a.disposition[host] != b.disposition[host]:
                    d[host] = a.disposition[host]
            else:
                d[host] = a.disposition[host]

        return d

    def computeInverseDifference(self, a=None, b=None):
        a = self.actual if a is None else a
        b = self.last if b is None else b

        return self.computeDifferences(a=b, b=a)


class GUI:
    def __init__(self, cfg, control, sender=None, root=None, width=10):
        self.root = root
        self.cfg = cfg
        self.sender = sender
        self.control = control
        self.__hosts, self.__scenes, self.__presets = self.cfg.fetchClasses()
        self.generalButtonSettings = {
            "width": width,
            "height": int(width / 3),
            "bd": 0,
            "background": STANDBY_COLOR,
            "activebackground": RED_COLOR
        }

    def check(self):
        if self.root is None:
            self.root = tk.Tk()
        return self.root

    def main_loop(self):
        self.root.mainloop()

    def controls(self):
        self.check()
        self.preset_root = tk.LabelFrame(self.root, text="Commands")
        self.preset_root.grid(row=0, rowspan=2, column=1, padx=10, pady=10, sticky="ns")

        self.sendButton = tk.Button(self.preset_root, text="Send", **self.generalButtonSettings,
                                    command=self.applyMatrix)
        self.sendButton.grid(row=99, column=0, pady=10, padx=5, sticky="nesw")

        self.undoButton = tk.Button(self.preset_root, text="Undo", **self.generalButtonSettings,
                                    command=self.undoMatrix)
        self.undoButton.grid(row=1, column=0, pady=10, padx=5, sticky="nesw")

        self.beforeButton = tk.Button(self.preset_root, text="Before", **self.generalButtonSettings)
        self.beforeButton.grid(row=2, column=0, pady=10, padx=5, sticky="nesw")

    def presets(self):
        self.check()
        self.preset_root = tk.LabelFrame(self.root, text="Presets")
        self.preset_root.grid(row=0, column=0, padx=10, pady=10, sticky="we")

        presets_names = self.cfg.fetchPresetsNames()

        self.presetLabel = tk.Label(self.preset_root, text="Preset : ")
        self.presetLabel.grid(row=0, column=0, padx=5)

        self.preset_selection = tk.StringVar(self.preset_root)
        self.preset_selection.set(presets_names[0])

        # self.preset_selection.trace("w", self.presetCallback)

        self.opt = tk.OptionMenu(self.preset_root, self.preset_selection, *presets_names)
        self.opt.config(font=('Helvetica', 11))
        self.opt.grid(row=0, column=1)

        custom = self.generalButtonSettings
        custom["heigh"] = 2

        self.presetApply = tk.Button(self.preset_root, text="Apply", **self.generalButtonSettings,
                                     command=self.applySelectedPreset)
        self.presetApply.grid(row=0, column=2, padx=5, pady=2)

    def affectHostToScene(self, host, scene):
        self.lines[host].affectToScene(scene)

    def applySelectedPreset(self, *args):
        presetName = self.preset_selection.get()
        _, _, presets = self.cfg.fetchClasses()

        preset = presets[presetName]

        self.applyPreset(preset)

    def applyMatrix(self):  # Callback of the (send) button
        d = self.control.computeDifferences()

        for host in d:
            self.sender.applySceneToHost(scene=d[host], host=host)

        self.control.archiveVersion()

    def undoMatrix(self):
        d = self.control.computeInverseDifference()

        for host in d:
            scene = d[host]
            # print(f'{host} -> {scene}')
            self.affectHostToScene(scene=scene, host=host)

    def refreshControl(self):
        self.control.loadFromLines(self.lines)

    def applyPreset(self, preset):
        print(f'Applying preset {preset.name}')
        for host, scene in preset.assignations.items():
            self.affectHostToScene(host, scene)

    def matrix(self, load=None):
        self.check()
        self.matrix_root = tk.LabelFrame(self.root, text="Matrix")
        self.matrix_root.grid(row=1, column=0, padx=10, pady=10)

        hosts, scenes, presets = self.cfg.fetchClasses()
        self.lines = {}

        # Mix scene names with "Locker" which is the last column
        for i, sceneName in enumerate([*list(scenes), "Locker"]):
            lbl = tk.Label(self.matrix_root, text=sceneName)
            lbl.grid(row=0, column=i + 1)

        for i, hostname in enumerate(hosts):  # Initialise all lines
            line = Line(host=hosts[hostname], scenes=scenes, root=self.matrix_root, y_index=i + 1, parent=self,
                        cfg=self.cfg)
            self.lines[hosts[hostname]] = line
            line.draw()

        if load is None:
            # Load latest send configuration
            try:
                data = self.control.loadFromJson()
                for host in data:
                    self.affectHostToScene(host, data[host])
                # self.control.archiveVersion()
            except:
                for hostname in hosts:
                    self.affectHostToScene(hosts[hostname], scenes[list(scenes)[0]])
                self.control.last.disposition = {}


class SettingInput:
    def __init__(self, _type, setting, root, n, cfg):
        self.type = _type
        self.setting = setting
        self.root = root
        self.y_index = n
        self.cfg = cfg

    def draw(self):
        # TODO : Implement loading of the actual preferences

        self.label = tk.Label(self.root, text=self.setting.title+(" "*10))
        self.label.grid(column=0, row=self.y_index)

        if self.type == bool:
            self.var = tk.IntVar()
            self.input = tk.Checkbutton(self.root, variable=self.var)

        self.input.grid(column=1, row=self.y_index, sticky="e")


class SettingsGUI:
    def __init__(self, cfg, root=None):
        self.root = root
        self.cfg = cfg

    def on_closing(self):
        MsgBox = tk.messagebox.askquestion('Exit Application', 'Are you sure you want to exit the configuration\nand discard all changes ?',
                                           icon='warning')
        if MsgBox == 'yes':
            self.root.destroy()
            self.callback()
        else:
            pass

    def show(self, callback):
        if self.root is None:
            self.root = tk.Tk()
        self.callback = callback

        self.__show()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def saveAndContinue(self):
        # TODO : Implement saving
        self.root.destroy()
        self.callback()

    def __show(self):
        self.settingsList = {}
        self.roots = {}
        self.rootsN = {}
        for key in settings.SETTINGS:
            split = key.split(".")  # -> ["general", "sommeSettingsNameWeDontCare"]
            if split[0] not in self.roots:
                title = [k.lower() if i > 0 else k.upper() for i, k in enumerate(split[0])]
                self.roots[split[0]] = tk.LabelFrame(self.root, text=title)
                self.roots[split[0]].grid(row=len(self.roots), column=0, padx=10, pady=10, sticky="nesw")

            self.rootsN[split[0]] = self.rootsN[split[0]]+1 if split[0] in self.rootsN else 1  # 1 because of the 0 + 1
            self.settingsList[key] = SettingInput(_type=settings.SETTINGS[key].type,
                                                  setting=settings.SETTINGS[key],
                                                  root=self.roots[split[0]],
                                                  n=self.rootsN[split[0]],
                                                  cfg=self.cfg)
            self.settingsList[key].draw()

        self.ctn = tk.Button(self.root, text="Save and Continue", command=self.saveAndContinue)
        self.ctn.grid(column=0, row=len(self.roots)+1, padx=20, pady=20, sticky="nsew")


if __name__ == "__main__":
    import config
    import api

    root = tk.Tk()
    cfg = config.ConfigReader()
    sender = api.Sender(configuration=cfg)
    control = DispositionControl(cfg=cfg)
    gui = GUI(cfg=cfg, control=control, root=root, sender=sender)
    gui.presets()
    gui.controls()
    gui.matrix()
    gui.main_loop()
