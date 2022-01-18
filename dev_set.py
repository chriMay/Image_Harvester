from configparser import ConfigParser

class DeviceSettings:

    def __init__(self):
        config = ConfigParser()
        config.read("config.ini")
        self.frameRate = float(config.get("device", "frameRate"))
        self.exposureTime = float(config.get("device", "exposureTime"))
        self.gain = float(config.get("device", "gain")) 
        self.line = config.get("device", "line")
        self.lineSource = config.get("device", "lineSource")

        