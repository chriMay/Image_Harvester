from datetime import datetime
import os
from threading import Thread
from mvIMPACT.acquire import *
from PIL import Image
import numpy
import ctypes


class deviceHandler:
    def __init__(self, devMgr, index, settings, save_path):
        self.devMgr = devMgr
        self.settings = settings
        self.index = index
        self.save_path = save_path

    def save_to_path(self, image):
        """
        Make directory with name of format YYYY-MM-DD_hh:mm
        """

        dir_name = datetime.now().strftime("%Y-%m-%d_%H-%M")

        current_time = datetime.now().strftime("%H-%M-%S-%f")
        file_name = f"{current_time}.bmp"

        save_path = f"{self.save_path}/{dir_name}"
        print(save_path)
        if not os.path.isdir(save_path):
            os.mkdir(save_path)

        image.save(f"{save_path}/{file_name}")

    def init_device(self):
        """
        Initialize a device with the given settings
        index: Index of selected device from the deviceslist
        """
        self.pDev = self.devMgr.getDevice(self.index)
        # interfaceLayout decides if [1]deviceSpecific interface or [2]GenICam interface will be used
        # The following if-statement makes sure that the GenICam interface is used

        if self.pDev.interfaceLayout.read() != 2:
            self.pDev.interfaceLayout.write(2)

        self.acqui_control = AcquisitionControl(self.pDev)
        self.analog_control = AnalogControl(self.pDev)
        self.digitalIO_control = DigitalIOControl(self.pDev)

        # Write the given settings to the device
        self.acqui_control.acquisitionFrameRate.write(self.settings.frameRate)
        self.acqui_control.exposureTime.write(self.settings.exposureTime)
        self.analog_control.gain.write(self.settings.gain)
        # self.digitalIO_control.lineSelector.writeS(self.settings.line)
        # self.digitalIO_control.lineSource.writeS(self.settings.lineSource)

        self.fi = FunctionInterface(self.pDev)

    def harvesting_process(self, single):
        """
        sugprocess in the image acquisition process
        single: if True only one image shall be taken
        """
        pPreviousRequest = None
        requestNr = self.fi.imageRequestWaitFor(10000)
        if self.fi.isRequestNrValid(requestNr):
            pRequest = self.fi.getRequest(requestNr)
            if pRequest.isOK:
                cbuf = (ctypes.c_char * pRequest.imageSize.read()).from_address(
                    int(pRequest.imageData.read())
                )
                print(cbuf[0:4])
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
                print(pRequest.imageChannelBitDepth.readS())
                if pRequest.imageChannelCount.read() == 1:
                    img = Image.frombytes("L", (2464, 2056), cbuf)
                else:
                    img = Image.fromarray(arr, "RGBA" if 0.8 else "RGB")

                img_temp_path = f"temp_img/temp.bmp"
                img.save(img_temp_path)

                if single == False:
                    self.save_to_path(img)

            if pPreviousRequest != None:
                pPreviousRequest.unlock()
            pPreviousRequest = pRequest
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

    def get_single_image(self):
        """
        Function to acquire images
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
        Function to acquire images
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
        """Start the image stream"""
        self.running = True
        newthread = Thread(target=self.image_stream)
        newthread.start()

    def stop_image_stream(self):
        """Stop the imaage stream and close device"""
        self.running = False
        self.pDev.close()
