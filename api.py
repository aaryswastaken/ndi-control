import requests
from requests.auth import *

class Sender():
    def __init__(self, hosts, presets, scenes):
        self.hosts = hosts
        self.presets = presets
        self.scenes = scenes

    def raw_send(self, host, scene, user="admin", pwd="admin"):
        data = '{"version": 1, "NDI_source":"'+scene+'"}'
        req = requests.post("http://" + host + "/v1/configuration", data=str(data), auth=HTTPDigestAuth(user, pwd))
        print(req.status_code, " ", req.text)

    def send(self, hostname, scene_name):
        self.raw_send(self.hosts[hostname]["url"], self.scenes[scene_name]["value"])

    def sendPreset(self, preset_name):
        for host in self.presets[preset_name]["command"]:
            command = self.presets[preset_name]["command"][host]
            self.send(host, command)