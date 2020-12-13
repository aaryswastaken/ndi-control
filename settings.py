class Setting:
    def __init__(self, key, title, description, _type):
        self.key = key
        # self.value = value
        self.title = title
        self.description = description
        self.type = _type


settingsList = [
    Setting(key="matrix.doesHostTurnRedWhenLocked", title="HostRedWhenLocked", _type=bool,
            description="Does the host button turn red when the line is locked"),
    Setting(key="settings.showOnStartup", title="Settings on startup", _type=bool,
            description="Does this page show on startup")
]

# EXPORT TO A USABLE VALUE
SETTINGS = {}
for stg in settingsList:
    SETTINGS[stg.key] = stg
