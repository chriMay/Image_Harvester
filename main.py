# !/usr/bin/python3

from mvIMPACT.acquire import DeviceManager
from main_ui import HarvesterInterface

devMgr = DeviceManager()

gui = HarvesterInterface(devMgr)
