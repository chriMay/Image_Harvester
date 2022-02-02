# !/usr/bin/python3

from mvIMPACT.acquire import DeviceManager
from main_ui import HarvesterInterface

if __name__ == "__main__":
    devMgr = DeviceManager()

    gui = HarvesterInterface(devMgr)
