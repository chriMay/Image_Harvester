#!/usr/bin/python3

from mvIMPACT.acquire import DeviceManager
from gui import HarvesterInterface

if __name__ == "__main__":
    devMgr = DeviceManager()

    gui = HarvesterInterface(devMgr)
