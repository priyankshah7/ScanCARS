import os
import sys
import time
import datetime
import ctypes
import pyvisa
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.Qt import QPalette, QColor
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QStyleFactory

from scancars.gui import dialogs
from scancars.gui.forms import main
from scancars.gui.css import setstyle
from scancars.threads import uithreads#, grating
from scancars.utils import post, toggle, savetofile
from scancars.sdk.andor import pyandor


class ScanCARS(QMainWindow, main.Ui_MainWindow):
    def __init__(self, parent=None):
        super(ScanCARS, self).__init__(parent)
        self.setupUi(self)

        # TODO Add options to take individual pump/Stokes. Will depend on being able to code up some shutters.
        # TODO If speed becomes an issue, consider using numba package with jit decorator
        # Required to use maths functions instead of numpy

        # -------STARTUP PROCESSES ---------------------------------------------------------

        # Initiating instances of a threadpool and the Andor class
        self.threadpool = QtCore.QThreadPool()
        self.andor = pyandor.Cam()

        # Variables for acquisition and temp. monitoring loops
        self.acquiring = False
        self.spectralacquiring = False
        self.hyperacquiring = False
        self.gettingtemp = False

        # Storing exposure times
        self.exposuretime = float(self.spectralRequiredTime.text())
        self.darkexposure = 0.1

        # Plot/Image settings
        self.specwinMain.plotItem.showGrid(x=True, y=True, alpha=0.2)
        self.specwinPrevious.plotItem.showGrid(x=True, y=True, alpha=0.2)
        self.specwinMain.setXRange(-10, 520, padding=0)
        self.specwinPrevious.setXRange(-10, 520, padding=0)
        self.specwinMain.plotItem.setMenuEnabled(False)
        self.specwinPrevious.plotItem.setMenuEnabled(False)

        self.imagewinMain.ui.histogram.setMinimumWidth(10)
        self.imagewinMain.ui.histogram.vb.setMinimumWidth(5)
        self.imagewinMain.ui.roiBtn.hide()
        self.imagewinMain.ui.menuBtn.hide()

        # Creating variables to store instances of the camera and track/sum dialogs
        self.wincamera = None
        self.winspectracks = None
        self.winspecsum = None

        # Connecting buttons to methods
        self.buttonMainStartAcquisition.clicked.connect(lambda: self.main_startacq())
        self.buttonMainShutdown.clicked.connect(lambda: self.main_shutdown())
        self.buttonCameratempCooler.clicked.connect(lambda: self.cameratemp_cooler())
        self.buttonDialogsDifference.clicked.connect(lambda: self.dialog_diff())
        self.buttonDialogsSum.clicked.connect(lambda: self.dialog_sum())
        self.buttonGratingUpdate.clicked.connect(lambda: self.grating_update())
        self.buttonCamtrackUpdate.clicked.connect(lambda: self.camtracks_update())
        self.buttonCamtrackView.clicked.connect(lambda: self.camtracks_view())
        self.buttonSpectralUpdate.clicked.connect(lambda: self.spectralacq_update())
        self.buttonSpectralStart.clicked.connect(lambda: self.spectralacq_start())
        self.buttonHyperspectralStart.clicked.connect(lambda: self.hyperacq_start())

        # Initialising the camera
        self.initialize_andor()
        self.width = self.andor.width

        # Initialising the PI Isoplane
        # self.isoplane = None
        # self.initialize_isoplane()
        self.buttonGratingUpdate.setDisabled(True)

        # Misc
        self.progressbar.setValue(0)

    def __del__(self):
        pass

    # Initialize: defining methods
    def initialize_andor(self):
        toggle.deactivate_buttons(self)

        # Storing the positions of the random tracks in an array
        randtrack = np.array([int(float(self.camtrackLower1.text())),
                              int(float(self.camtrackUpper1.text())),
                              int(float(self.camtrackLower2.text())),
                              int(float(self.camtrackUpper2.text()))])

        errorinitialize = self.andor.initialize()   # Initializing the detector
        if errorinitialize != 'DRV_SUCCESS':
            post.eventlog(self, 'Andor: Initialize error. ' + errorinitialize)
            return
        self.andor.getdetector()                    # Getting information from the detector
        self.andor.setshutter(1, 2, 0, 0)           # Ensuring the shutter is closed
        self.andor.setreadmode(2)                   # Setting the read mode to Random Tracks
        self.andor.setrandomtracks(2, randtrack)    # Setting the position of the random tracks
        self.andor.setadchannel(1)                  # Setting the AD channel
        self.andor.settriggermode(0)                # Setting the trigger mode to 'internal'
        self.andor.sethsspeed(1, 0)                 # Setting the horiz. shift speed
        self.andor.setvsspeed(4)                    # Setting the verti. shift speed

        self.exposuretime = float(self.spectralRequiredTime.text())
        self.andor.setexposuretime(self.exposuretime)

        time.sleep(2)

        self.andor.dim = self.andor.width * self.andor.randomtracks

        self.andor.getacquisitiontimings()
        self.spectralActualTime.setText(str(round(self.andor.exposure, 3)))

        toggle.activate_buttons(self)
        post.eventlog(self, 'Andor: Successfully initialized.')

        # Starting the temperature thread to monitor the temperature of the camera
        self.gettingtemp = True
        gettemperature = uithreads.TemperatureThread(self)
        self.threadpool.start(gettemperature)

    def initialize_isoplane(self):
        rm = pyvisa.ResourceManager()
        self.isoplane = rm.open_resource('ASRL4::INSTR')
        self.isoplane.timeout = 20
        self.isoplane.baud_rate = 9600

        self.isoplane.read_termination = '\r'
        self.isoplane.write_termination = '\r'

        post.eventlog(self, 'Isoplane: Connected.')

    # Main: defining methods
    def main_startacq(self):
        if self.acquiring is False:
            self.acquiring = True
            toggle.deactivate_buttons(self, main_start_acq_stat=True)
            post.status(self, 'Acquiring...')
            self.buttonMainStartAcquisition.setText('Stop Acquisition')

            self.specwinMain.clear()
            track1plot = self.specwinMain.plot(pen=(190, 70, 45), name='track1')
            track2plot = self.specwinMain.plot(pen=(25, 85, 120), name='track2')
            diffplot = self.specwinMain.plot(pen='w', name='trackdiff')

            cimage = (ctypes.c_int * self.andor.dim)()

            self.andor.freeinternalmemory()
            self.andor.setacquisitionmode(1)
            self.andor.setshutter(1, 1, 0, 0)
            self.andor.setexposuretime(self.exposuretime)

            while self.acquiring:
                self.andor.startacquisition()
                self.andor.waitforacquisition()
                self.andor.getacquireddata(cimage)

                track1plot.setData(self.andor.imagearray[0:self.andor.width - 1])
                track2plot.setData(self.andor.imagearray[self.andor.width:(2 * self.andor.width) - 1])
                diffplot.setData(
                    self.andor.imagearray[self.andor.width:(2 * self.andor.width) - 1] - self.andor.imagearray[
                                                                                0:self.andor.width - 1], )

                QCoreApplication.processEvents()

        elif self.acquiring is True:
            self.acquiring = False
            toggle.activate_buttons(self)
            post.status(self, '')
            self.buttonMainStartAcquisition.setText('Start Acquisition')
            self.andor.setshutter(1, 2, 0, 0)

    def main_shutdown(self):
        # Ensuring all acquiring and temperature loops have been stopped
        self.acquiring = False
        self.gettingtemp = False

        # Turning the shutter off and checking to see if the camera cooler is on
        self.andor.setshutter(1, 2, 0, 0)
        self.andor.iscooleron()
        self.andor.gettemperature()

        # If the cooler is off, proceed to shutdown the camera
        if self.andor.coolerstatus == 0 and self.andor.temperature > -20:
            self.andor.shutdown()

            post.eventlog(self, 'ScanCARS can now be safely closed.')
            post.status(self, 'ScanCARS can now be safely closed.')
            toggle.deactivate_buttons(self)

        # If the cooler is on, turn it off, wait for temp. to increase to -20C, and then shutdown camera
        else:
            self.andor.gettemperature()
            if self.andor.temperature < -20:
                post.eventlog(self, 'Andor: Waiting for camera to return to normal temp...')
            self.andor.cooleroff()
            self.buttonCameratempCooler.setText('Cooler On')
            time.sleep(1)
            while self.andor.temperature < -20:
                time.sleep(3)
                self.andor.gettemperature()
                QtCore.QCoreApplication.processEvents()

            self.andor.shutdown()

            post.eventlog(self, 'ScanCARS can now be safely closed.')
            post.status(self, 'ScanCARS can now be safely closed.')
            toggle.deactivate_buttons(self)

        # self.isoplane.close()

    # CameraTemp: defining methods
    def cameratemp_cooler(self):
        # Checking to see if the cooler is on or off
        message_iscooleron = self.andor.iscooleron()
        if message_iscooleron != 'DRV_SUCCESS':
            post.eventlog(self, 'Andor: IsCoolerOn error. ' + message_iscooleron)

        else:
            if self.andor.coolerstatus == 0:
                # Turning the cooler on and checking to see if it has been turned on
                self.andor.settemperature(int(self.cameratempRequiredTemp.text()))
                self.andor.cooleron()
                self.andor.iscooleron()
                if self.andor.coolerstatus == 1:
                    post.eventlog(self, 'Andor: Cooler on.')
                    self.cameratempActualTemp.setStyleSheet('background: #4e644e')
                    self.buttonCameratempCooler.setText('Cooler Off')

            elif self.andor.coolerstatus == 1:
                # Turning the cooler off and checking to see if it has been turned off
                self.andor.cooleroff()
                self.andor.iscooleron()
                if self.andor.coolerstatus == 0:
                    post.eventlog(self, 'Andor: Cooler off.')
                    self.cameratempActualTemp.setStyleSheet('background: #121212')
                    self.buttonCameratempCooler.setText('Cooler On')

            else:
                # Shouldn't expect this to be called, if it is then it's unlikely to be related to the Andor
                post.eventlog(self, 'An error has occured. Possibly related to the GUI itself?')

    # Dialogs: defining methods
    def dialog_sum(self):
        pass

    def dialog_diff(self):
        pass

    # Grating: defining methods
    def grating_update(self):
        grating_no = grating.get_grating(self.isoplane)
        wavelength_no = grating.get_nm(self.isoplane)

        if self.grating150.isChecked() and grating_no == 2:
            grating.set_grating(self.isoplane, 3)

        elif self.grating600.isChecked() and grating_no == 3:
            grating.set_grating(self.isoplane, 2)

        if int(self.gratingRequiredWavelength.text()) != wavelength_no:
            grating.set_nm(self.isoplane, int(self.gratingRequiredWavelength.text()))

    # CamTracks: Defining methods
    def camtracks_update(self):
        pass

    def camtracks_view(self):
        pass

    # SpectralAcq: Defining methods
    def spectralacq_update(self):
        # Storing and setting the acquisition time
        self.exposuretime = float(self.spectralRequiredTime.text())
        self.andor.setexposuretime(self.exposuretime)

        # Updating the actual acquisition time that has been set
        self.andor.getacquisitiontimings()
        self.spectralActualTime.setText(str(round(self.andor.exposure, 3)))
        post.eventlog(self, 'Andor: Exposure time set to ' + str(self.exposuretime) + 's')

    def spectralacq_start(self):
        toggle.deactivate_buttons(self)
        self.spectralacquiring = True
        post.status(self, 'Spectral acquisition in progress...')
        self.progressbar.setValue(0)

        exposuretime = float(self.exposuretime)
        frames = int(self.spectralFrames.text())
        darkcount = int(self.spectralBackgroundFrames.text())

        # Expected time
        total = (darkcount * self.darkexposure) + (frames * exposuretime)
        # progress_darkcount = ((darkcount * self.ui.darkexposure) / total) * 100

        # Darkcount acquisition
        self.andor.setshutter(1, 2, 0, 0)
        self.andor.setexposuretime(exposuretime)
        self.andor.setacquisitionmode(1)
        cimage = (ctypes.c_long * self.andor.dim)()

        time.sleep(2)
        dark_data = [0] * darkcount

        numscan = 0
        while numscan < darkcount:
            self.andor.startacquisition()
            self.andor.waitforacquisition()
            self.andor.getacquireddata(cimage, 1)
            dark_data[numscan] = self.andor.imagearray

            self.progressbar.setValue((numscan + 1) / (darkcount + frames) * 100)
            numscan += 1

        dark_data = np.asarray(dark_data)
        dark_data = np.transpose(dark_data)

        # Converting the acquisition from using Kinetic series to Single scan
        self.andor.setshutter(1, 1, 0, 0)
        self.andor.setexposuretime(exposuretime)
        self.andor.setacquisitionmode(1)
        cimage = (ctypes.c_long * self.andor.dim)()

        time.sleep(2)
        spectral_data = [0] * frames

        numscan = 0
        while numscan < frames:
            self.andor.startacquisition()
            self.andor.waitforacquisition()
            self.andor.getacquireddata(cimage, 1)
            spectral_data[numscan] = self.andor.imagearray

            self.progressbar.setValue((darkcount + numscan + 1) / (darkcount + frames) * 100)
            numscan += 1

        spectral_data = np.asarray(spectral_data)
        spectral_data = np.transpose(spectral_data)

        acquired_data = np.mean(spectral_data, 1) - np.mean(dark_data, 1)

        # # Plotting the mean spectrum
        self.specwinMain.clear()
        self.specwinMain.plot(acquired_data[0:511], pen='r')
        self.specwinMain.plot(acquired_data[512:1023], pen='g')
        self.specwinMain.plot(acquired_data[512:1023] - acquired_data[0:511], pen='w')

        self.specwinPrevious.clear()
        self.specwinPrevious.plot(acquired_data[512:1023] - acquired_data[0:511], pen='w')

        # # Saving the data to file
        now = datetime.datetime.now()
        newpath = 'C:\\Users\\CARS\\Documents\\SIPCARS\\Data\\' + now.strftime('%Y-%m-%d') + '\\'
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        filename = QFileDialog.getSaveFileName(caption='File Name', filter='H5 (*.h5)',
                                               directory=newpath)

        if filename[0]:
            acqproperties = savetofile.EmptyClass()
            acqproperties.width = self.andor.width
            acqproperties.time = exposuretime
            acqproperties.number = frames

            savetofile.save(acquired_data, str(filename[0]), acqproperties, acqtype='spectral')

            self.progressbar.setValue(100)
            post.eventlog(self, 'Spectral acquisition saved.')  # TODO Print file name saved to as well

        else:
            self.progressbar.setValue(100)
            post.eventlog(self, 'Acquisition aborted.')

        # Finishing up UI acquisition call
        self.andor.setshutter(1, 2, 0, 0)
        post.status(self, '')
        self.spectralacquiring = False
        self.progressbar.setValue(0)
        toggle.activate_buttons(self)

    def hyperacq_start(self):
        pass


def main():
    app = QApplication(sys.argv)

    # Setting the dark-themed Fusion style for the GUI
    app.setStyle(QStyleFactory.create('Fusion'))
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(23, 23, 23))
    dark_palette.setColor(QPalette.WindowText, QColor(200, 200, 200))
    dark_palette.setColor(QPalette.Base, QColor(18, 18, 18))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, QColor(200, 200, 200))
    dark_palette.setColor(QPalette.Button, QColor(33, 33, 33))
    dark_palette.setColor(QPalette.ButtonText, QColor(200, 200, 200))
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.white)
    dark_palette.setColor(QPalette.Active, QPalette.Button, QColor(33, 33, 33))
    dark_palette.setColor(QPalette.Disabled, QPalette.Button, QColor(20, 20, 20))
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(120, 120, 120))
    app.setPalette(dark_palette)

    form = ScanCARS()
    form.setWindowTitle('ScanCARS')
    form.show()
    sys.exit(app.exec_())


# If the file is run directly and not imported, this runs the main function
if __name__ == '__main__':
    main()
