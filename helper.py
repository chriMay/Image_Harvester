from datetime import datetime
from os import path, mkdir
from pathlib import Path
from threading import Thread
from mvIMPACT.acquire import *
from PIL import Image
import numpy
import ctypes
import sys


class deviceHandler:
    def __init__(self, devMgr, index, configuration, save_path):
        self.devMgr = devMgr
        self.configuration = configuration
        # Index of selected device from the deviceslist
        self.index = index
        self.save_path = save_path

    def save_to_path(self, image):
        """
        Make directory with name of format YYYY-MM-DD_hh:mm .
        """

        dir_name = datetime.now().strftime("%Y-%m-%d_%H-%M")

        current_time = datetime.now().strftime("%H-%M-%S-%f")
        file_name = f"{current_time}{self.configuration.image_format}"

        save_path = Path(self.save_path, dir_name)
        print(save_path)
        if not path.isdir(save_path):
            mkdir(save_path)

        image.save(Path(save_path, file_name))

    def init_device(self):
        """
        Initialize a device with the given configuration.
        """
        self.pDev = self.devMgr.getDevice(self.index)
        # interfaceLayout decides if [1]deviceSpecific interface or [2]GenICam interface will be used
        # The following if-statement makes sure that the GenICam interface is used

        if self.pDev.interfaceLayout.read() != 2:
            self.pDev.interfaceLayout.write(2)

        self.acqui_control = AcquisitionControl(self.pDev)
        self.analog_control = AnalogControl(self.pDev)
        self.digitalIO_control = DigitalIOControl(self.pDev)

        # Write the given configuration to the device
        self.acqui_control.acquisitionFrameRate.write(self.configuration.frameRate)
        self.acqui_control.exposureTime.write(self.configuration.exposureTime)
        self.analog_control.gain.write(self.configuration.gain)
        self.digitalIO_control.lineSelector.writeS(self.configuration.line)
        self.digitalIO_control.lineSource.writeS(self.configuration.lineSource)

        self.fi = FunctionInterface(self.pDev)

    def harvesting_process(self, single):
        """
        Subprocess in the image acquisition process.
        single: if True only one image shall be taken
        """

        requestNr = self.fi.imageRequestWaitFor(35000)
        if self.fi.isRequestNrValid(requestNr):
            pRequest = self.fi.getRequest(requestNr)
            if pRequest.isOK:
                cbuf = (ctypes.c_char * pRequest.imageSize.read()).from_address(
                    int(pRequest.imageData.read())
                )
                channelType = (
                    numpy.uint16
                    if pRequest.imageChannelBitDepth.read() > 8
                    else numpy.uint8
                )
                arr = numpy.frombuffer(cbuf, dtype=channelType)
                arr.shape = (
                    pRequest.imageHeight.read(),
                    pRequest.imageWidth.read(),
                    pRequest.imageChannelCount.read(),
                )
                if pRequest.imageChannelCount.read() == 1:
                    img = Image.frombytes("L", (2464, 2056), cbuf)
                else:
                    img = Image.fromarray(arr, "RGBA" if 0.8 else "RGB")

                img_temp_path = Path(
                    "temp_img", "temp" + self.configuration.image_format
                )
                img.save(img_temp_path)

                if single == False:
                    self.save_to_path(img)

            if pRequest.unlock() is not DMR_NO_ERROR:
                print("unlock unsuccesfull", file=sys.stderr)

            self.fi.imageRequestSingle()
        else:
            # Please note that slow systems or interface technologies in combination with high resolution sensors
            # might need more time to transmit an image than the timeout value which has been passed to imageRequestWaitFor().
            # If this is the case simply wait multiple times OR increase the timeout(not recommended as usually not necessary
            # and potentially makes the capture thread less responsive) and rebuild this application.
            # Once the device is configured for triggered image acquisition and the timeout elapsed before
            # the device has been triggered this might happen as well.
            # The return code would be -2119(DEV_WAIT_FOR_REQUEST_FAILED) in that case, the documentation will provide
            # additional information under TDMR_ERROR in the interface reference.
            # If waiting with an infinite timeout(-1) it will be necessary to call 'imageRequestReset' from another thread
            # to force 'imageRequestWaitFor' to return when no data is coming from the device/can be captured.
            print(
                "imageRequestWaitFor failed ("
                + str(requestNr)
                + ", "
                + ImpactAcquireException.getErrorCodeAsString(requestNr)
                + ")"
            )

        print(f"done for Request: {requestNr}")

    def get_single_image(self):
        """
        Function to acquire one single image.
        save_path: the path where the images shall be stored
        test: if True, only one test image will be made
        """
        self.init_device()

        while self.fi.imageRequestSingle() == DMR_NO_ERROR:
            print("Buffer queued")

        if self.pDev.acquisitionStartStopBehaviour.read() == assbUser:
            result = self.fi.acquisitionStop()
            if result != DMR_NO_ERROR:
                print(
                    "'FunctionInterface.acquisitionStop' returned with an unexpected result: "
                    + str(result)
                    + "("
                    + ImpactAcquireException.getErrorCodeAsString(result)
                    + ")"
                )

        self.harvesting_process(single=True)

        if self.pDev.acquisitionStartStopBehaviour.read() == assbUser:
            result = self.fi.acquisitionStop()
            if result != DMR_NO_ERROR:
                print(
                    "'FunctionInterface.acquisitionStart' returned with an unexpected result: "
                    + str(result)
                    + "("
                    + ImpactAcquireException.getErrorCodeAsString(result)
                    + ")"
                )

        self.pDev.close()

    def image_stream(self):
        """
        Function to acquire multiple images.
        Can be started with start_image_strem() and stopped with stop_image_stream()
        save_path: the path where the images shall be stored
        test: if True, only one test image will be made
        """

        self.init_device()

        while self.fi.imageRequestSingle() == DMR_NO_ERROR:
            print("Buffer queued")

        if self.pDev.acquisitionStartStopBehaviour.read() == assbUser:
            result = self.fi.acquisitionStart()
            if result != DMR_NO_ERROR:
                print(
                    "'FunctionInterface.acquisitionStop' returned with an unexpected result: "
                    + str(result)
                    + "("
                    + ImpactAcquireException.getErrorCodeAsString(result)
                    + ")"
                )

        while self.running:
            self.harvesting_process(single=False)

        if self.pDev.acquisitionStartStopBehaviour.read() == assbUser:
            result = self.fi.acquisitionStop()
            if result != DMR_NO_ERROR:
                print(
                    "'FunctionInterface.acquisitionStop' returned with an unexpected result: "
                    + str(result)
                    + "("
                    + ImpactAcquireException.getErrorCodeAsString(result)
                    + ")"
                )

    def start_image_stream(self):
        """Start the image stream."""
        self.running = True
        newthread = Thread(target=self.image_stream)
        newthread.start()

    def stop_image_stream(self):
        """Stop the imaage stream and close device."""
        self.running = False
        self.pDev.close()
