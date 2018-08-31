import os
import sys
import time
import datetime
import configparser
import ctypes
import pyvisa
import nidaqmx as daq
import numpy as np
from PyQt5 import QtCore
from PyQt5.Qt import QPalette, QColor
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QStyleFactory

from scancars.gui import dialogs
from scancars.gui.forms import main
from scancars.threads import grating, liveacquire, spectralacquire, monitortemp
from scancars.utils import post, toggle, savetofile
from scancars.sdk.andor import pyandor


class ScanCARS(QMainWindow, main.Ui_MainWindow):
    def __init__(self, parent=None):
        super(ScanCARS, self).__init__(parent)
        self.setupUi(self)
        self.showMaximized()
        self.setWindowTitle('ScanCARS')

        # TODO Add options to take individual pump/Stokes. Will depend on being able to code up some shutters.
        # TODO Add control for the Nikon microscope with micro-manager

        # NOTE To build, run: pyinstaller --onefile --windowed build.spec

        # ------- STARTUP PROCESSES ---------------------------------------------------------

        # Retrieving config values
        config = configparser.ConfigParser()
        config.read('config.ini')
        default_vals = config['DEFAULT']
        self.camtrackLower1.setValue(default_vals.getint('camtrackLower1'))
        self.camtrackUpper1.setValue(default_vals.getint('camtrackUpper1'))
        self.camtrackLower2.setValue(default_vals.getint('camtrackLower2'))
        self.camtrackUpper2.setValue(default_vals.getint('camtrackUpper2'))
        self.spectralRequiredTime.setValue(default_vals.getfloat('spec_exposuretime'))
        self.spectralBackgroundFrames.setValue(default_vals.getint('spec_background_frames'))
        self.spectralFrames.setValue(default_vals.getint('spec_spectral_frames'))
        self.hyperspectralRequiredTime.setValue(default_vals.getfloat('hyp_exposuretime'))
        self.hyperspectralBackgroundFrames.setValue(default_vals.getint('hyp_background_frames'))
        self.hyperspectralXPix.setValue(default_vals.getint('num_x_pix'))
        self.hyperspectralYPix.setValue(default_vals.getint('num_y_pix'))
        self.hyperspectralZPix.setValue(default_vals.getint('num_z_pix'))
        self.hyperspectralXYStep.setValue(default_vals.getfloat('xy_step'))
        self.hyperspectralZStep.setValue(default_vals.getfloat('z_step'))
        self.cameratempRequiredTemp.setValue(default_vals.getint('temp'))

        # Initiating instances of a threadpool and the Andor class
        self.threadpool = QtCore.QThreadPool()
        self.andor = pyandor.Cam()

        # Variables for acquisition and temp. monitoring loops
        self.acquiring = False
        self.spectralacquiring = False
        self.hyperacquiring = False
        self.camtrackacquiring = False
        self.gettingtemp = False

        # Storing exposure times
        self.exposuretime = float(self.spectralRequiredTime.text())
        self.darkexposure = 0.1

        # Creating variables to store instances of the camera and track/sum dialogs
        self.winspecsum = dialogs.SPECSUM()
        self.winspecsum.setWindowTitle('Sum Track Spectrum')
        self.winspecdiff = dialogs.SPECDIFF()
        self.winspecdiff.setWindowTitle('Difference Track Spectrum')

        # Plot/Image settings
        self.specwinMain.plotItem.showGrid(x=True, y=True, alpha=0.2)
        self.specwinPrevious.plotItem.showGrid(x=True, y=True, alpha=0.2)
        self.specwinMain.setXRange(-10, 530, padding=0)
        self.specwinPrevious.setXRange(-10, 530, padding=0)
        self.specwinMain.plotItem.setMenuEnabled(False)
        self.specwinPrevious.plotItem.setMenuEnabled(False)
        self.imagewinMain.ui.histogram.setMinimumWidth(10)
        self.imagewinMain.ui.histogram.vb.setMinimumWidth(5)
        self.imagewinMain.ui.roiBtn.hide()
        self.imagewinMain.ui.menuBtn.hide()

        self.specwinMain.clear()
        self.winspecsum.specwinSum.clear()
        self.winspecdiff.specwinDiff.clear()
        self.track1plot = self.specwinMain.plot(pen=(190, 70, 45), name='track1')
        self.track2plot = self.specwinMain.plot(pen=(25, 85, 120), name='track2')
        self.diffplot = self.specwinMain.plot(pen='w', name='trackdiff')
        self.sumdialogplot = self.winspecsum.specwinSum.plot(pen=(25, 85, 120), name='sum')
        self.diffdialogplot = self.winspecdiff.specwinDiff.plot(pen=(25, 85, 120), name='difference')
        self.previousplot = self.specwinPrevious.plot(pen='w', name='previousdiff')

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

        # Initialising the PI Isoplane if it is able to connect
        self.isoplane = None
        self.initialize_isoplane()

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
        gettemperature = monitortemp.MonitorTemperatureThread(self)
        self.threadpool.start(gettemperature)

    def initialize_isoplane(self):
        rm = pyvisa.ResourceManager()
        try:
            # 'ASRL4::INSTR' is the port which the Isoplane is connected to. Change as required.
            self.isoplane = rm.open_resource('ASRL4::INSTR')
            self.isoplane.timeout = 300000
            self.isoplane.baud_rate = 9600

            self.isoplane.read_termination = ' ok\r\n'
            self.isoplane.write_termination = '\r'

            self.finished_grating_query()

            post.eventlog(self, 'Isoplane: Connected.')

        except pyvisa.errors.VisaIOError as error:
            self.buttonGratingUpdate.setDisabled(True)
            post.eventlog(self, 'Isoplane: Could not connect. Possibly being used in another process.')
            print(error)

    # Main: defining methods
    def main_startacq(self):
        # Creating an instance of the live acquisition thread
        acquirethread = liveacquire.LiveAcquireThread(self)

        # If there's no current live acquisition taking place, then start one
        if self.acquiring is False:
            self.acquiring = True
            self.andor.setshutter(1, 1, 0, 0)
            toggle.deactivate_buttons(self, main_start_acq_stat=True)
            post.status(self, 'Acquiring...')
            self.buttonMainStartAcquisition.setText('Stop Acquisition')

            # Camera parameters from live acquisition
            self.andor.freeinternalmemory()
            self.andor.setacquisitionmode(1)
            self.andor.setexposuretime(self.exposuretime)

            time.sleep(1)

            # Starting live acquisition thread and connecting to plot function
            self.threadpool.start(acquirethread)
            acquirethread.signals.dataLiveAcquire.connect(lambda: plot())

            def plot():
                self.track1plot.setData(self.andor.imagearray[0:self.width - 1])
                self.track2plot.setData(self.andor.imagearray[self.width:(2 * self.width) - 1])
                self.diffplot.setData(self.andor.imagearray[self.andor.width:(2 * self.andor.width) - 1] -
                                      self.andor.imagearray[0:self.andor.width - 1])

                self.sumdialogplot.setData(self.andor.imagearray[self.width:(2 * self.width) - 1] +
                                           self.andor.imagearray[0:self.width - 1])

                self.diffdialogplot.setData(self.andor.imagearray[self.width:(2 * self.width) - 1] -
                                            self.andor.imagearray[0:self.width - 1])

                QCoreApplication.processEvents()

        # If there's a live acquisition taking place, then stop it
        elif self.acquiring is True:
            self.acquiring = False
            self.andor.setshutter(1, 2, 0, 0)
            acquirethread.stop()
            toggle.activate_buttons(self)
            post.status(self, '')
            self.buttonMainStartAcquisition.setText('Start Acquisition')
            self.andor.setshutter(1, 2, 0, 0)

    def main_shutdown(self):
        toggle.deactivate_buttons(self)

        # Saving the event logger contents to a textfile
        now = datetime.datetime.now()
        newpath = 'C:\\Users\\CARS\\Documents\\SIPCARS\\Data\\' + now.strftime('%Y-%m-%d') + '\\'
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        with open(newpath + 'eventlog--' + now.strftime('%H-%M-%S') + '.txt', 'w') as eventfile:
            eventfile.write(str(self.eventLogger.toPlainText()))

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
            self.isoplane.close()

            post.eventlog(self, 'ScanCARS can now be safely closed.')
            post.status(self, 'ScanCARS can now be safely closed.')

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
                self.cameratempActualTemp.setText(str(self.andor.temperature))
                QCoreApplication.processEvents()

            self.andor.shutdown()
            self.isoplane.close()

            post.eventlog(self, 'ScanCARS can now be safely closed.')
            post.status(self, 'ScanCARS can now be safely closed.')

    def closeEvent(self, event):
        # Method to carry out operations upon closing the main window
        self.andor.iscooleron()
        error_setshutter = self.andor.setshutter(1, 2, 0, 0)
        if self.andor.coolerstatus == 1 or error_setshutter == 'DRV_SUCCESS':
            event.ignore()
            post.eventlog(self, 'ScanCARS needs to SHUTDOWN first.')

        else:
            if self.winspecsum.isVisible() or self.winspecdiff.isVisible():
                self.winspecsum.close()
                self.winspecdiff.close()

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
        self.winspecsum.show()

    def dialog_diff(self):
        self.winspecdiff.show()

    # Grating: defining methods
    def grating_update(self):
        post.eventlog(self, 'Isoplane: Updating...')
        self.isoplane.clear()
        grating_no = self.isoplane.ask('?GRATING')
        grating_no = int(grating_no[1])

        self.isoplane.clear()
        wavelength_no = self.isoplane.ask('?NM')
        wavelength_no = round(float(wavelength_no[0:-3]))

        if self.grating150.isChecked() and grating_no == 2:
            setgrating = grating.GratingThread(self.isoplane, query='grating', value=3)
            self.threadpool.start(setgrating)
            message = 'Isoplane: Grating set to 150 lines/mm'
            setgrating.signals.finished.connect(lambda: self.finished_grating_query(message))

        elif self.grating600.isChecked() and grating_no == 3:
            setgrating = grating.GratingThread(self.isoplane, query='grating', value=2)
            self.threadpool.start(setgrating)
            message = 'Isoplane: Grating set to 600 lines/mm'
            setgrating.signals.finished.connect(lambda: self.finished_grating_query(message))

        if int(self.gratingRequiredWavelength.text()) != wavelength_no:
            reqwavelength = int(self.gratingRequiredWavelength.text())
            setwavelength = grating.GratingThread(self.isoplane, query='wavelength', value=reqwavelength)
            self.threadpool.start(setwavelength)
            message = 'Isoplane: Wavelength set to ' + str(reqwavelength) + ' nm'
            setwavelength.signals.finished.connect(lambda: self.finished_grating_query(message))

    def finished_grating_query(self, message=None):
        self.isoplane.clear()
        grating_no = self.isoplane.ask('?GRATING')
        grating_no = int(grating_no[1])

        self.isoplane.clear()
        wavelength_no = self.isoplane.ask('?NM')
        wavelength_no = round(float(wavelength_no[0:-3]))

        if self.grating150.isChecked() and grating_no == 2:
            self.grating600.setChecked(True)

        elif self.grating600.isChecked() and grating_no == 3:
            self.grating150.setChecked(True)

        self.gratingActualWavelength.setText(str(wavelength_no))

        if message is not None:
            post.eventlog(self, message)

    # CamTracks: Defining methods
    def camtracks_update(self):
        # Reading in the required track position values from the gui
        randtrack = np.array([int(float(self.camtrackLower1.text())),
                              int(float(self.camtrackUpper1.text())),
                              int(float(self.camtrackLower2.text())),
                              int(float(self.camtrackUpper2.text()))])

        # Setting the random track positions on the camera
        errormessage = self.andor.setrandomtracks(2, randtrack)

        # Checking to make sure that the camera has successfully set the random tracks
        if errormessage != 'DRV_SUCCESS':
            post.eventlog(self, 'Andor: SetRandomTracks error. ' + errormessage)

        else:
            post.eventlog(self, 'Andor: Random track positions updated.')

    def camtracks_view(self):
        if self.camtrackacquiring is False:
            # Setting the read mode to image to get a full image from the CCD chip
            self.andor.setacquisitionmode(1)
            self.andor.setreadmode(4)
            self.andor.setexposuretime(0.1)

            cimage = (ctypes.c_long * self.andor.height * self.andor.width)()

            self.andor.setshutter(1, 1, 0, 0)
            self.camtrackacquiring = True
            while self.camtrackacquiring:
                self.andor.startacquisition()
                self.andor.waitforacquisition()
                self.andor.getacquireddata(cimage, numscans=1, acqtype='image')

                self.imagewinMain.clear()
                self.imagewinMain.setImage(self.andor.imagearray)

                QCoreApplication.processEvents()

        elif self.camtrackacquiring is True:
            self.camtrackacquiring = False
            # Storing the positions of the random tracks in an array
            randtrack = np.array([int(float(self.camtrackLower1.text())),
                                  int(float(self.camtrackUpper1.text())),
                                  int(float(self.camtrackLower2.text())),
                                  int(float(self.camtrackUpper2.text()))])

            self.andor.setshutter(1, 2, 0, 0)  # Ensuring the shutter is closed
            self.andor.setreadmode(2)  # Setting the read mode to Random Tracks
            self.andor.setrandomtracks(2, randtrack)
            self.andor.setexposuretime(self.exposuretime)

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

        # Setting acquisition parameters
        exposuretime = float(self.exposuretime)
        frames = int(self.spectralFrames.text())
        darkcount = int(self.spectralBackgroundFrames.text())

        # Dark acquisition
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

            self.track1plot.setData(self.andor.imagearray[0:self.width-1])
            self.track2plot.setData(self.andor.imagearray[self.width:(2*self.width)-1])
            self.diffplot.setData(
                self.andor.imagearray[self.width:(2*self.width)-1]-self.andor.imagearray[0:self.width-1])

            self.progressbar.setValue((numscan + 1) / (darkcount + frames) * 100)
            numscan += 1

            QCoreApplication.processEvents()

        dark_data = np.asarray(dark_data)
        dark_data = np.transpose(dark_data)

        # Spectral acquisition
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

            self.track1plot.setData(self.andor.imagearray[0:self.width - 1])
            self.track2plot.setData(self.andor.imagearray[self.width:(2 * self.width) - 1])
            self.diffplot.setData(
                self.andor.imagearray[self.width:(2 * self.width) - 1] - self.andor.imagearray[0:self.width - 1])

            self.progressbar.setValue((darkcount + numscan + 1) / (darkcount + frames) * 100)
            numscan += 1

            QCoreApplication.processEvents()

        spectral_data = np.asarray(spectral_data)
        spectral_data = np.transpose(spectral_data)

        acquired_data = np.mean(spectral_data, 1) - np.mean(dark_data, 1)

        # # Plotting the mean spectrum
        self.track1plot.setData(acquired_data[0:self.width - 1])
        self.track2plot.setData(acquired_data[self.width:(2 * self.width) - 1])
        self.diffplot.setData(acquired_data[self.width:(2 * self.width) - 1] - acquired_data[0:self.width - 1])

        self.previousplot.setData(acquired_data[self.width:(2 * self.width) - 1] - acquired_data[0:self.width - 1])

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

    # HyperspectralAcq: Defining methods
    def hyperacq_start(self):
        # Storing values of hyperspectral acquisition
        x_required = self.hyperspectralXPix
        y_required = self.hyperspectralYPix
        z_required = self.hyperspectralZPix

        xystep_required = self.hyperspectralXYStep
        zstep_required = self.hyperspectralZStep

        exposuretime = self.hyperspectralRequiredTime
        background_frames = self.hyperspectralBackgroundFrames

        cimage = (ctypes.c_long * self.andor.dim)()


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
    form.show()
    sys.exit(app.exec_())


# If the file is run directly and not imported, this runs the main function
if __name__ == '__main__':
    main()
sys.exit(1)
