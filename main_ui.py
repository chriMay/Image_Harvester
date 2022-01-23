from tkinter import Tk, Frame, OptionMenu, Button, Label, Toplevel, Entry
from tkinter import StringVar, filedialog
from PIL import Image, ImageTk
from dev_set import DeviceSettings
import os
from helper import deviceHandler


class HarvesterInterface:
    """Main interface for the ImageHarvester"""

    def __init__(self, devMgr) -> None:
        self.devMgr = devMgr
        self.device_settings = DeviceSettings()
        self.root = Tk()
        self.root.title("Image Harvester")

        # Creating frames for Input, displaying information and displaying images
        self.input_frame = Frame(self.root)
        self.information_frame = Frame(self.root)
        self.image_frame = Frame(self.root)

        self.input_frame.grid(row=0, column=0, sticky="ns")
        self.information_frame.grid(row=1, column=0, sticky="nswe")
        self.image_frame.grid(row=0, column=1, rowspan=2)

        # Populating input_frame

        # Declare a StringVar to store selected device
        self.clicked_device = StringVar()

        # DropdownMenu with available devices
        # Button to refresh available devices, Button to choose devices
        self.list_devices()
        self.devices_om = OptionMenu(
            self.input_frame, self.clicked_device, *self.devices_list
        )
        self.devices_om.grid(row=0, column=0)

        # Button to refresh the dropdown menu
        self.refresh_button = Button(
            self.input_frame, text="Aktualisieren", command=self.refresh_devices
        )
        self.refresh_button.grid(row=0, column=1)

        # Declare a StringVar to store the path to directory where to save images
        self.saving_path = StringVar()
        self.saving_path.set(os.environ["HOME"])

        # Label which shows the selected path to directory where to save images
        # Button to select path to directory where to save images
        self.path_label = Label(
            self.input_frame, text=self.saving_path.get(), relief="sunken"
        )
        self.path_button = Button(
            self.input_frame, text="Speicherort wählen", command=self.select_path
        )

        self.path_label.grid(row=1, column=0, sticky="we")
        self.path_button.grid(row=1, column=1)

        # Button to write settings to the selected device
        self.settings_button = Button(
            self.input_frame, text="Einstellungen", command=self.device_settings_menu
        )
        self.settings_button.grid(row=2, column=0, sticky="we")

        # Button to make a test image
        self.test_button = Button(
            self.input_frame, text="Testbild", command=self.image_test
        )
        self.test_button.grid(row=3, column=0, sticky="we")

        # Buttons to start/stop the image harvesting
        self.start_button = Button(
            self.input_frame, text="Start", command=self.start_harvesting
        )
        self.stop_button = Button(
            self.input_frame, text="Stop", command=self.stop_harvesting
        )

        self.start_button.grid(row=4, column=0, sticky="we")
        self.stop_button.grid(row=4, column=1, sticky="we")

        # Populating the information frame
        self.frameRate_info_label = Label(
            self.information_frame,
            text=f"Bildfrequenz: {self.device_settings.frameRate} Hz",
        )
        self.exposureTime_info_label = Label(
            self.information_frame,
            text=f"Belichtungszeit: {self.device_settings.exposureTime} \u03BCs",
        )
        self.gain_info_label = Label(
            self.information_frame, text=f"Gain(ISO): {self.device_settings.gain}"
        )
        self.active_label = Label(
            self.information_frame, text="Bildaufnahme nicht aktiv"
        )
        self.info_label = Label(self.information_frame, text="")

        self.frameRate_info_label.grid(row=0, column=0, sticky="w")
        self.exposureTime_info_label.grid(row=1, column=0, sticky="w")
        self.gain_info_label.grid(row=2, column=0, sticky="w")
        self.active_label.grid(row=3, column=0, sticky="w")
        self.info_label.grid(row=4, column=0, sticky="w")

        # Populating the image frame
        self.image = Image.open("temp_img/temp.bmp").resize((616, 514))
        self.image = ImageTk.PhotoImage(self.image)
        self.image_label = Label(self.image_frame, image=self.image)
        self.image_label.grid(row=0, column=0)

        # Mainloop
        self.root.mainloop()

    def refresh_devices(self):
        """Refresh devices dropdown menu"""

        self.devMgr.updateDeviceList()

        self.list_devices()
        menu = self.devices_om["menu"]
        menu.delete(0, "end")

        for device in self.devices_list:
            menu.add_command(
                label=device,
                command=lambda value=device: self.clicked_device.set(value),
            )

        self.info_label.configure(text="")

    def list_devices(self):
        """Create a list of available devices"""

        self.devices_list = []
        for i in range(self.devMgr.deviceCount()):
            pDev = self.devMgr.getDevice(i)
            self.devices_list.append(
                f"[{i}] {pDev.serial.read()} {pDev.product.read()}"
            )
            self.clicked_device.set(self.devices_list[0])

        if len(self.devices_list) == 0:
            self.devices_list = ["keine Geräte gefunden"]

        self.clicked_device.set(self.devices_list[0])

    def select_path(self):
        """Select path to directory where images shall be stored"""

        temp_path = filedialog.askdirectory(initialdir=self.saving_path.get())
        self.saving_path.set(temp_path)
        self.path_label.configure(text=self.saving_path.get())

    def device_settings_menu(self):
        """Opens a subwindow where some device settings can be changed"""

        self.top = Toplevel()
        self.top.title("Einstellungen")

        # Labels describing the settings
        self.frameRate_label = Label(self.top, text="Bildfrequenz: ")
        self.exposureTime_label = Label(self.top, text="Belichtungszeit: ")
        self.gain_label = Label(self.top, text="Gain(ISO): ")

        self.frameRate_label.grid(row=0, column=0)
        self.exposureTime_label.grid(row=1, column=0)
        self.gain_label.grid(row=2, column=0)

        # Entries for the Settings-Subwindow
        self.frameRate_entry = Entry(self.top, width=20, borderwidth=3)
        self.frameRate_entry.insert(0, self.device_settings.frameRate)

        self.exposureTime_entry = Entry(self.top, width=20, borderwidth=3)
        self.exposureTime_entry.insert(0, self.device_settings.exposureTime)

        self.gain_entry = Entry(self.top, width=20, borderwidth=3)
        self.gain_entry.insert(0, self.device_settings.gain)

        self.frameRate_entry.grid(row=0, column=1)
        self.exposureTime_entry.grid(row=1, column=1)
        self.gain_entry.grid(row=2, column=1)

        # Labels for the Units
        self.frameRate_unit_label = Label(self.top, text="Hz")
        self.exposureTime_unit_label = Label(self.top, text="\u03BCs")

        self.frameRate_unit_label.grid(row=0, column=2)
        self.exposureTime_unit_label.grid(row=1, column=2)

        # Buttons to apply the settings to the selected device
        self.apply_button = Button(
            self.top, text="Übernehmen", command=self.apply_settings
        )
        self.back_button = Button(self.top, text="Zurück", command=self.top.destroy)

        self.apply_button.grid(row=3, column=0)
        self.back_button.grid(row=3, column=1)

    def apply_settings(self):
        """Apply settings to the selected device"""
        self.device_settings.frameRate = float(self.frameRate_entry.get())
        self.device_settings.exposureTime = float(self.exposureTime_entry.get())
        self.device_settings.gain = float(self.gain_entry.get())

        self.frameRate_info_label.configure(
            text=f"Bildfrequenz: {self.device_settings.frameRate} Hz"
        )
        self.exposureTime_info_label.configure(
            text=f"Belichtungszeit: {self.device_settings.exposureTime} \u03BCs"
        )
        self.gain_info_label.configure(text=f"Gain(ISO): {self.device_settings.gain}")

    def image_test(self):
        """Make a test image and display it in the main window"""
        index = int(self.clicked_device.get()[1])
        devHand = deviceHandler(
            self.devMgr, index, self.device_settings, self.saving_path.get()
        )
        devHand.get_single_image()

        self.image = Image.open("temp_img/temp.bmp").resize((616, 514))
        self.image = ImageTk.PhotoImage(self.image)
        self.image_label.configure(image=self.image)
        self.image_label.image = self.image

    def start_harvesting(self):
        """Start the harvesting process"""

        if self.devices_list[0][1] == "0":  # Check if devices are found
            # Disable buttons during harvesting process
            self.refresh_button.configure(state="disabled")
            self.path_button.configure(state="disabled")
            self.settings_button.configure(state="disabled")
            self.test_button.configure(state="disabled")
            self.active_label.configure(text="Bildaufnahme aktiv")

            index = int(self.clicked_device.get()[1])
            self.devHand = deviceHandler(
                self.devMgr, index, self.device_settings, self.saving_path.get()
            )
            self.devHand.start_image_stream()

            # self.image = Image.open("temp_img/temp.bmp").resize((616, 514))
            # elf.image = ImageTk.PhotoImage(self.image)
            # self.image_label.configure(image=self.image)
            # self.image_label.image=self.image
        else:
            self.info_label.configure(text="Gerät nicht erreichbar")

    def stop_harvesting(self):
        """Stop the harvesting process"""
        self.devHand.stop_image_stream()

        # Enable buttons again
        self.refresh_button.configure(state="normal")
        self.path_button.configure(state="normal")
        self.settings_button.configure(state="normal")
        self.test_button.configure(state="normal")
        self.active_label.configure(text="Bildaufnahme nicht aktiv")
