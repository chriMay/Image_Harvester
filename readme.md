# Task

Programming a HMI to connect to an installed Camera from MatrixVision, to make changes on some settings and to get images and save them to a given path.
The currently used camera in the field is mvBlueCOUGAR-X105bG-POE-IP67
For testing the Software I got a mvBlueFOX3-2051G.

## Parameters to be set (with device specific default settings):

1. FrameRate (Frequenz mit der Bilder aufgenommen werden)
   BlueFox3: 5450 Hz

2. Exposure Time
   BlueFox3: 20000 us (Microseconds)

3. Gain
   BlueFox3: 0 absolute physical value!

4. Trigger
   There are free lines on the camera which can be used to send a trigger signal. For example to trigger an external light source.

The device specific setting will be an XML file with the serial number of the device as the file name, the product specific setting will be an XML file with the product string as the filename, the device family specific setting will be an XML file with the device family name as the file name. All other XML files containing settings will be ignored

# How to run the code

1.       $ git clone https://github.com/chriMay/Image_Harvester.git
2.       $ cd ../Image_Harvester
3.       $ python main.py

# Important Information

## DeviceManager

Once the _DeviceManager_ is initialized, new connected devices are appended to the internal devices list but never deleted. For example you connect a device and initialize a _DeviceManager_-class, it will recognize the device properly -> when you disconnect the device and call the method _updateDeviceList_, the device is still available in the _DeviceManager_-instance.

## Settings

Once the settings(frameRate, exposureTime, etc) are applied, they are "stored" independent of opening and closing the device as long the device stays connected to the host. Once the connection to the host is lost, the settings of the device jump back to default settings.

# Some useful Info before Starting

To get the current values of some settings there are mostly used to functions depending on the type of the value (string or float/integer)

- read() ... read floats/integer
- readS() ... read a string

In a similar way you can write the Values

- write()
- writeS()

### Example:

- pDev.interfaceLayout.write(2)
  changes interfaceLayout to GenICam interface

- pDev.interfaceLayout.readS()
  returns the current interfaceLayout als string zurück ("GenICam")

# Important classes in acquire-package with important methods

## DeviceManager

- getDevice(index)

## ImageDisplayWindow

- GetImageDisplay()
- SetRefreshTime()

## FunctionInterface

- getRequest()

# Known issues

## Bug beim Aktualisieren des Dropdown-Menus zum auswählen der Kamera

**Ausgangssituation:** Wenn Kameras angesteckt sind und das Programm gestartet wird oder wenn Kameras nach dem Start des Programms angesteckt werden
**Bug:** Werden verbundene Kameras abgehängt und auf den Aktualisieren Button gedrückt bleiben alle bis dahin angesteckten Kameras im Dropdown sichtbar
**bekannte Auswirkungen:**

- set_device() in gui.py: kann evtl vereinfacht werden wenn behoben(siehe try-except)
- update_deviceDropdown() in gui.py: unmittelbar betroffene Funktion

# Used Packages

### PyPi

- tkinter
- pillow
- numpy
- ctypes

### Other sources

- mvIMPACT:
  1.  Download [Drives & Software](https://www.matrix-vision.com/de/downloads/treiber-software) and follow the [instructions](https://www.matrix-vision.com/de/downloads/setup/mvbluecougar-family/quickstart-mvbluecougar-linux)
  2.  Follow instructions of the [mvIMPACT Acquire SDK Manual](https://www.matrix-vision.com/manuals/SDK_PYTHON/Building_page.html#Python_BuildingLinux)

# Open Questions

- How to handle Subwindow?
- How to handle config file

# ToDo

- Information Frame: Info ob Aufnahme läuft oder nicht
- Foto-Format in config.infi übernehmen
- Statistics von Kamera in Info frame (live die frequenz angeben)
- nur bildausschnitt übernehmen (Größe des Ausschnitts übernehmen und Position[xy]-> linke obere Ecke als Referenz)
- Check if the driver & software package for COUGAR and BlueFox3 are the same
- Improve function for image harvesting (not running well at the Moment)

I'm writing a readme file in vs code and i noticed an annoying behavior, which i don't know how to deal with. When i save the file with ctrl+s an whitespace is added before the code. I had a look at the shortcuts and it shows me two commands for this keybinding. One is the common **File: save** and **Create issue** which refers to  
 {
"key": "ctrl+s",
"command": "issue.createIssueFromFile",
"when": "!issues.creatingFromFile && resourceScheme == 'newIssue' && config.files.autoSave != 'off'"
}
I don't really know what this does and would appreciate any quick help on this.
