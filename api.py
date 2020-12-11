import requests
from requests.auth import *
import threading
import time

TIMEOUTWARNING = 3000


class Queue():
    def __init__(self):
        pass

    def send(self, host, data=None, auth=None, method="post"):
        _sd = _sender({"host": host, "data": data, "auth": auth, "method": method})
        _sd.start()


class _sender(threading.Thread):
    def __init__(self, args: dict):
        super().__init__()
        self.req = args

    def run(self):
        _req = None
        try:
            self.start = time.time()
            if self.req["method"] == "post":
                _req = requests.post(self.req["host"], data=self.req["data"], auth=self.req["auth"])
            elif self.req["method"] == "get":
                _req = requests.get(self.req["host"])
        except ConnectionError or requests.exceptions.ConnectionError:
            pass
        finally:
            if _req is not None:
                print(f'Request to {self.req["host"]} ended up with code {_req.status_code}')
                if time.time() - self.start > (TIMEOUTWARNING / 1000):
                    print(f'[WARN] Host took more than {TIMEOUTWARNING / 1000}s to answer')

                return

        print("An error occurred while trying to send "+str(self.req["host"]))


class Sender:
    def __init__(self, configuration):
        self.conf = configuration
        self.refresh()
        self.queue = Queue()

    def refresh(self):
        _, _, self.presets = self.conf.fetchClasses()

    def changeConf(self, conf):
        self.conf = conf
        self.refresh()

    def applySceneToHost(self, scene, host):
        print(f'Applying scene {scene.name} to host {host.name}')

    def applyPresetFromName(self, name):
        preset = self.presets[name]
        print(f'Applying preset {preset.name}')

    def applyPreset(self, preset):
        print(f'Applying preset {preset.name}')


# class Sender():
#     def __init__(self, hosts, presets, scenes):
#         self.hosts = hosts
#         self.presets = presets
#         self.scenes = scenes
#         self.queue = Queue()
#         self.queue.start()
#
#     def raw_send(self, host, scene, user="admin", pwd="admin"):
#         data = '{"version": 1, "NDI_source":"' + scene + '"}'
#         self.queue.send("http://" + host + "/v1/configuration", data=str(data), auth=HTTPDigestAuth(user, pwd))
#
#     def send(self, hostname, scene_name):
#         self.raw_send(self.hosts[hostname]["url"], self.scenes[scene_name]["value"])
#
#     def sendPreset(self, preset_name):
#         for host in self.presets[preset_name]["command"]:
#             command = self.presets[preset_name]["command"][host]
#             self.send(host, command)


if __name__ == "__main__":
    queue = Queue()
    queue.send(host="https://127.0.0.1", method="get")
    time.sleep(1)
    queue.send(host="https://www.google.com", method="get")
