import requests
from requests.auth import *
import threading


class Queue(threading.Thread):
    def __init__(self):
        super().__init__()
        self.queue = []

    def send(self, host, data=None, auth=None):
        self.queue.append({"host": host, "data": data, "auth": auth})

    def run(self):
        if len(self.queue) > 0:
            _sd = _sender(self.queue[0])


class _sender(threading.Thread):
    def __init__(self, args: dict):
        super().__init__()
        self.req = args

    def run(self):
        try:
            self._req = requests.post(self.req["host"], data=self.req["data"], auth=self.req["auth"])
        finally:
            if "_req" in self:
                print(self._req.status_code)
            else:
                print("There was an error while trying to send the command")


class Sender():
    def __init__(self, hosts, presets, scenes):
        self.hosts = hosts
        self.presets = presets
        self.scenes = scenes
        self.queue = Queue()
        self.queue.start()

    def raw_send(self, host, scene, user="admin", pwd="admin"):
        data = '{"version": 1, "NDI_source":"' + scene + '"}'
        self.queue.send("http://" + host + "/v1/configuration", data=str(data), auth=HTTPDigestAuth(user, pwd))

    def send(self, hostname, scene_name):
        self.raw_send(self.hosts[hostname]["url"], self.scenes[scene_name]["value"])

    def sendPreset(self, preset_name):
        for host in self.presets[preset_name]["command"]:
            command = self.presets[preset_name]["command"][host]
            self.send(host, command)
