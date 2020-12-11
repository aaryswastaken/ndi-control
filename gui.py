import tkinter as tk


class GUI:
    def __init__(self, cfg, sender):
        self.cfg = cfg
        self.sender = sender
        hosts, scenes, presets = cfg.fetchClasses()
        presets_names = cfg.fetchPresetsNames()
        self.root = tk.Tk()

        self.root.geometry("500x500")
        self.root.title("NDI-Control")

        self.l = tk.LabelFrame(self.root, text="Selection du preset", padx=20, pady=20)
        self.l.pack(fill="both", expand="yes")

        self.preset_selection = tk.StringVar(self.root)
        self.preset_selection.set(presets_names[0])

        self.opt = tk.OptionMenu(self.l, self.preset_selection, *presets_names)
        self.opt.config(width=90, font=('Helvetica', 12))
        self.opt.pack(side="top")

        self.l2 = tk.LabelFrame(self.root, text="Commandes", padx=20, pady=20)
        self.l2.pack(fill="both", expand="yes")

        self.button = tk.Button(self.l2, text="Envoyer", command=self.sendcallback)
        self.button.pack()

        self.preset_selection.trace("w", self.callback)

        self.root.mainloop()

    def sendcallback(self):
        print("Sending commands")
        self.sender.applyPresetFromName(self.preset_selection.get())

    def callback(self, *args):
        print("The selected item is {}".format(self.preset_selection.get()))


class GUI_experimental:
    def __init__(self, cfg, sender):
        pass
