# Not final version, but functional

# Important Information

- The language of the GUI is german
- It is written on a Linux-based system and not tested on other OS.

## Task

HMI to connect to a linked Camera from MatrixVision, to make changes on some settings, get images and save them to a given path.
The currently used camera in the field is mvBlueCOUGAR-X105bG
For testing the Software I got a mvBlueFOX3-2051G.

## Parameters which can be set (with device specific default settings):

1. FrameRate (Frequenz mit der Bilder aufgenommen werden)
   BlueFox3: 5450 Hz

2. Exposure Time
   BlueFox3: 20000 us (Microseconds)

3. Gain
   BlueFox3: 0 absolute physical value!

4. Trigger
   There are free lines on the camera which can be used to send a trigger signal. For example to trigger an external light source. (see _config.ini_)

# How to use

## How to run the code

1. $ git clone https://github.com/chriMay/Image_Harvester.git
2. $ cd ../Image_Harvester
3. $ python main.py

## Usage of GUI

There is a main-window and a subwindow for the settings.

### Mainwindow

![Screenshot](pictures/noted_mainwindow.png)

1. At the top you can choose between the cameras linked to the PC. If you link devices to the PC after starting the _Image Harvester_ they won't show up. Therefore you has to press the _Aktualisieren_-Button. If you face unusual behavior for example after disconnecting a device and pressing _Aktualisieren_ afterwards, you may have a look at the **Known Issues** section.

2. In this row you can see the current path where the images should be stored. With the button _Speicherort wählen_ you can change the path.

3. In the next row you can choose the path where the images will be stored
   With the Button _Einstellungen_ the **Settings-Subwindow** will pop up.

4. With the button _Testbild_ you can make a test image to check if your settings are correct and the device points in the right direction.

5. Pressing the _Start_-button starts the Harvesting Process of the images. If its active an information (Bildaufnahme aktiv) is displayed on the _Information-frame_. A folder will be created which is named in the format _YYYY-MM-DD_hh-mm_. The images are stored in this folder and named after the timestamp when they were taken. If there is not device found an information is displayed on the _Information-frame_.

### Settings-Subwindow

# Important Information

## DeviceManager

Once the _DeviceManager_ is initialized, new connected devices are appended to the internal devices list but never deleted. For example you connect a device and initialize a _DeviceManager_-class, it will recognize the device properly -> when you disconnect the device and call the method _updateDeviceList_, the device is still available in the _DeviceManager_-instance.

## Settings

Once the settings(frameRate, exposureTime, gain, etc) are applied, they are "stored" independent of opening and closing the device. As long the device stays connected to the host. Once the connection to the host is lost, the settings of the device jump back to default settings. Therefore the "default-settings" can be changed in the _config.ini_

# Some useful Info before Starting

To get the current values of some settings there are two functions depending on the type of the value (string or float/integer)

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
  1.  Download [Drivers & Software](https://www.matrix-vision.com/de/downloads/treiber-software) and follow the [instructions](https://www.matrix-vision.com/de/downloads/setup/mvbluecougar-family/quickstart-mvbluecougar-linux)
  2.  Follow instructions of the [mvIMPACT Acquire SDK Manual](https://www.matrix-vision.com/manuals/SDK_PYTHON/Building_page.html#Python_BuildingLinux)

# Open Questions

# ToDo

- Statistics von Kamera in Info frame (live die frequenz angeben)
- nur bildausschnitt übernehmen (Größe des Ausschnitts übernehmen und Position[xy]-> linke obere Ecke als Referenz)
- Check if the driver & software package for COUGAR and BlueFox3 are the same
