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

        print("An error occurred while trying to send " + str(self.req["host"]))


class Sender:
    def __init__(self, configuration):
        self.conf = configuration
        self.refresh()
        self.queue = Queue()

    def refresh(self):
        self.hosts, self.scenes, self.presets = self.conf.fetchClasses()

    def changeConf(self, conf):
        self.conf = conf
        self.refresh()

    def applySceneToHost(self, scene, host):
        print(f'Applying scene {scene.name} to host {host.name}')
        self.queue.send(host=f'{host.url}/v1/configuration',
                        data=str('{"version": 1, "NDI_source":"' + scene.ndi + '"}'),
                        auth=HTTPDigestAuth(host.user, host.pwd),
                        method="post")

    def applyPreset(self, preset):
        print(f'Applying preset {preset.name}')
        for host in preset.assignations:
            self.applySceneToHost(host=host, scene=preset.assignations[host])

    def applyPresetFromName(self, name):
        preset = self.presets[name]
        self.applyPreset(preset)

    def setAsPIP(self, host, scene):
        self.queue.send(host=f'{host.url}/v1/configuration',
                        data=str('{"version": 1, "NDI_overlay":"' + scene.ndi + '"}'),
                        auth=HTTPDigestAuth(host.user, host.pwd),
                        method="post")

    def setPIP(self, host, state):
        self.queue.send(host=f'{host.url}/v1/configuration',
                        data=str('{"version": 1, "decorations":{"picture_in_picture": ' + str(state).lower() + '}}'),
                        auth=HTTPDigestAuth(host.user, host.pwd),
                        method="post")

    def showPIP(self, host):
        self.setPIP(host, True)

    def hidePIP(self, host):
        self.setPIP(host, False)


if __name__ == "__main__":
    import config

    cfg = config.ConfigReader()
    sender = Sender(cfg)
    time.sleep(5)
    hosts, _, _ = cfg.fetchClasses()
    sender.showPIP(hosts["host1"])
