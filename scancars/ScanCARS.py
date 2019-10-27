import os
import time
import datetime
import sys
import pyvisa
import configparser
import subprocess
import numpy as np
from PyQt5 import QtCore
from PyQt5.Qt import QPalette, QColor
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QStyleFactory, QFileDialog

from scancars.gui import dialogs
from scancars.gui.forms import main as main_window
from scancars.utils import post, toggle, savetofile
from scancars.sdk.andor import pyandor as pyandor
from scancars.threads import hyperacquire, liveacquire, monitortemp, ccdacquire, grating, spectralacquire


class ScanCARS(QMainWindow, main_window.Ui_MainWindow):
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
        self.ccdacquiring = False
        self.spectralacquiring = False
        self.hyperacquiring = False
        self.acquisition_cancelled = False
        self.gettingtemp = False
        self.grating = False

        # Data variables
        self.spectral_data = None
        self.hyperspectral_data = None

        # Storing exposure times
        self.exposuretime = float(self.spectralRequiredTime.text())
        self.darkexposure = 0.1

        # Creating variables to store instances of the camera and track/sum dialogs
        self.winspecsum = dialogs.SPECSUM()
        self.winspecsum.setWindowTitle('Sum Track Spectrum')
        self.winspecdiff = dialogs.SPECDIFF()
        self.winspecdiff.setWindowTitle('Difference Track Spectrum')
        self.winccdlive = dialogs.CCDLIVE()
        self.winccdlive.setWindowTitle('Live CCD View')

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

        self.specwinMain.clear()
        self.winspecsum.specwinSum.clear()
        self.winspecdiff.specwinDiff.clear()
        self.track1plot = self.specwinMain.plot(pen=(190, 70, 45), name='track1')
        self.track2plot = self.specwinMain.plot(pen=(25, 85, 120), name='track2')
        self.diffplot = self.specwinMain.plot(pen='w', name='trackdiff')
        self.sumdialogplot = self.winspecsum.specwinSum.plot(pen=(25, 85, 120), name='sum')
        self.diffdialogplot = self.winspecdiff.specwinDiff.plot(pen=(25, 85, 120), name='difference')
        self.previousplot = self.specwinPrevious.plot(pen='w', name='previousdiff')
        self.imageplot = self.imagewinMain.getImageItem()

        # Hyperspectral imaging settings
        self.hyperacq_update_time()

        # Connecting buttons to methods
        self.buttonMainStartAcquisition.clicked.connect(self.main_startacq)
        self.buttonMainShutdown.clicked.connect(self.main_shutdown)
        self.buttonCameratempCooler.clicked.connect(self.cameratemp_cooler)
        self.buttonDialogsDifference.clicked.connect(lambda: self.winspecdiff.show())
        self.buttonDialogsSum.clicked.connect(lambda: self.winspecsum.show())
        self.buttonGratingUpdate.clicked.connect(self.grating_update)
        self.buttonGratingState.clicked.connect(self.grating_state)
        self.buttonCamtrackUpdate.clicked.connect(self.camtracks_update)
        self.buttonCamtrackView.clicked.connect(self.camtracks_view)
        self.buttonSpectralUpdate.clicked.connect(self.spectralacq_update)
        self.buttonSpectralStart.clicked.connect(self.spectralacq_start)
        self.buttonHyperspectralStart.clicked.connect(self.hyperacq_start)
        self.buttonHyperspectralTime.clicked.connect(self.hyperacq_update_time)
        self.buttonUserChange.clicked.connect(self.user_change)
        self.buttonUserOpen.clicked.connect(self.user_open_folder)
        self.buttonGain.clicked.connect(self.gain_update)
        self.dialGain.valueChanged.connect(self.gain_dial_change)
        self.actionOpen_Data_Folder.triggered.connect(lambda: self.open_data_folder())

        # Initialising the camera
        self.initialize_andor()
        self.width = self.andor.width

        # Initialising the PI Isoplane if it is able to connect
        # self.isoplane = None
        # self.initialize_isoplane()

        # Misc
        self.progressbar.setValue(0)

        # User details
        self.userDropdown.clear()
        self.userDropdown.addItem('Guest')
        self.userDropdown.addItem('Priyank')
        self.userDropdown.addItem('Tao')
        self.user_directory = None
        self.user_change()

    # Menu functions
    @staticmethod
    def open_data_folder():
        subprocess.Popen('explorer "F:\\SIPCARS\\Data"')

    def user_change(self):
        user = str(self.userDropdown.currentText())
        self.userName.setText(user)
        self.user_directory = "F:\\SIPCARS\\Data\\" + user

        if not os.path.exists(self.user_directory):
            os.makedirs(self.user_directory)

    def user_open_folder(self):
        subprocess.Popen('explorer "' + self.user_directory + '"')

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

    def initialize_andor(self):
        toggle.deactivate_buttons(self)

        # Storing the positions of the random tracks in an array
        randtrack = np.array([int(self.camtrackLower1.text()),
                              int(self.camtrackUpper1.text()),
                              int(self.camtrackLower2.text()),
                              int(self.camtrackUpper2.text())])

        errorinitialize = self.andor.initialize()  # Initializing the detector
        if errorinitialize != 'DRV_SUCCESS':
            post.eventlog(self, 'Andor: Initialize error. ' + errorinitialize)
            return
        self.andor.getdetector()  # Getting information from the detector
        self.andor.setshutter(1, 2, 0, 0)  # Ensuring the shutter is closed
        self.andor.setreadmode(2)  # Setting the read mode to Random Tracks
        self.andor.setrandomtracks(2, randtrack)  # Setting the position of the random tracks
        self.andor.setadchannel(1)  # Setting the AD channel
        self.andor.settriggermode(0)  # Setting the trigger mode to 'internal'
        self.andor.sethsspeed(0, 0)  # Setting the horiz. shift speed
        self.andor.setvsspeed(4)  # Setting the verti. shift speed

        self.exposuretime = float(self.spectralRequiredTime.text())
        self.andor.setexposuretime(self.exposuretime)

        # Setting camera to gain mode and setting the initial gain
        gain_to_set = 10
        self.andor.setemccdgainmode(0)
        self.andor.setemccdgain(gain_to_set)
        self.dialGain.setValue(gain_to_set)
        gain_button_text = str(gain_to_set) + ': Update'
        self.buttonGain.setText(gain_button_text)

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
            self.buttonGratingState.setText('Turn Off')
            self.buttonGratingState.setStyleSheet('background: #121212')
            self.grating = True

        except pyvisa.errors.VisaIOError as error:
            self.buttonGratingUpdate.setDisabled(True)
            self.buttonGratingState.setDisabled(True)
            self.grating = False
            post.eventlog(self, 'Isoplane: Could not connect. Possibly being used in another process.')
            print(error)

    def gain_dial_change(self):
        dial_value = self.dialGain.value()
        gain_button_text = str(dial_value) + ': Update'
        self.buttonGain.setText(gain_button_text)

    def gain_update(self):
        dial_value = int(self.dialGain.value())
        self.andor.setemccdgain(dial_value)
        post.eventlog(self, 'Andor: Gain set to '+str(dial_value))

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

    def grating_state(self):
        if self.grating is True:
            self.isoplane.close()

            post.eventlog(self, 'Isoplane: Disconnected.')
            self.buttonGratingState.setText('Turn On')
            self.buttonGratingState.setStyleSheet('background: #121212')
            self.buttonGratingUpdate.setDisabled(True)
            self.grating = False

        elif self.grating is False:
            self.initialize_isoplane()

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
            acquirethread.stop()
            toggle.activate_buttons(self)
            post.status(self, '')
            self.buttonMainStartAcquisition.setText('Start Acquisition')

    def main_shutdown(self):
        toggle.deactivate_buttons(self)

        # Saving the event logger contents to a textfile
        now = datetime.datetime.now()
        newpath = 'F:\\SIPCARS\\Data\\Logs\\' + now.strftime('%Y-%m-%d') + '\\'
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
        if self.andor.coolerstatus == 0:  # and ui.andor.temperature > -20: # TODO Temp. whilst aligning
            self.andor.shutdown()
            # ui.isoplane.close()

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
            # ui.isoplane.close()

            post.eventlog(self, 'ScanCARS can now be safely closed.')
            post.status(self, 'ScanCARS can now be safely closed.')

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
        # Creating instance of the live ccd chip thread
        ccdacquire_thread = ccdacquire.CcdAcquireThread(self)

        # If there's no current live ccd view taking place, then start one
        if self.ccdacquiring is False:
            self.ccdacquiring = True
            self.dialog_ccd()
            self.andor.setshutter(1, 1, 0, 0)
            toggle.deactivate_buttons(self, cameraoptions_openimage_stat=True)
            post.status(self, 'Live CCD view...')
            # self.buttonCamtrackView.setText('Stop Live View')

            # Camera parameters for live ccd acquisition
            self.andor.freeinternalmemory()
            self.andor.setreadmode(4)
            self.andor.setacquisitionmode(1)
            self.andor.setexposuretime(self.exposuretime)

            time.sleep(1)

            # Starting live ccd acquisition thread and connecting to plot function
            self.threadpool.start(ccdacquire_thread)
            ccdacquire_thread.signals.dataLiveAcquire.connect(lambda: plot())

            def plot():
                self.winccdlive.ccdliveWin.setImage(self.andor.imagearray)
                QCoreApplication.processEvents()

        elif self.ccdacquiring is True:
            self.ccdacquiring = False
            ccdacquire_thread.stop()
            toggle.activate_buttons(self)
            post.status(self, '')

    def spectralacq_update(self):
        # Storing and setting the acquisition time
        self.exposuretime = float(self.spectralRequiredTime.text())
        self.andor.setexposuretime(self.exposuretime)

        # Updating the actual acquisition time that has been set
        self.andor.getacquisitiontimings()
        self.spectralActualTime.setText(str(round(self.andor.exposure, 3)))
        post.eventlog(self, 'Andor: Exposure time set to ' + str(self.exposuretime) + 's')

    def spectralacq_start(self):
        # Creating an instance of the spectral acquisition thread
        frames = int(self.spectralFrames.text())
        darkcount = int(self.spectralBackgroundFrames.text())
        spectralthread = spectralacquire.SpectralAcquireThread(self, frames, darkcount)

        # If there's no acquisition taking place, then start one
        if self.spectralacquiring is False:
            self.spectralacquiring = True
            self.andor.setshutter(1, 1, 0, 0)
            toggle.deactivate_buttons(self, spectralacq_start_stat=True)
            post.status(self, 'Spectral acquisition in progress...')
            self.buttonSpectralStart.setText('Stop Spectral Acquisition')

            # Camera parameters for spectral acquisition
            self.andor.freeinternalmemory()
            self.andor.setacquisitionmode(1)
            self.andor.setexposuretime(self.exposuretime)

            self.spectral_data = [0] * frames

            time.sleep(1)

            def plot_and_store(numscan):
                self.spectral_data[numscan] = self.andor.imagearray
                # TODO use spectra_data instead of imagearray following from here
                self.track1plot.setData(self.andor.imagearray[0:self.width - 1])
                self.track2plot.setData(self.andor.imagearray[self.width:(2 * self.width) - 1])
                self.diffplot.setData(
                    self.andor.imagearray[self.width:(2 * self.width) - 1] - self.andor.imagearray[0:self.width - 1])

                self.progressbar.setValue((darkcount + numscan + 1) / (darkcount + frames) * 100)

                QCoreApplication.processEvents()

            def finished_acquisition():
                if not self.acquisition_cancelled:
                    # Processing data
                    spectral_data = np.asarray(self.spectral_data)
                    spectral_data = np.transpose(spectral_data)

                    acquired_data = np.mean(spectral_data, 1)  # - np.mean(dark_data, 1)

                    # Plotting the mean spectrum
                    self.track1plot.setData(acquired_data[0:self.width - 1])
                    self.track2plot.setData(acquired_data[self.width:(2 * self.width) - 1])
                    self.diffplot.setData(
                        acquired_data[self.width:(2 * self.width) - 1] - acquired_data[0:self.width - 1])

                    self.previousplot.setData(
                        acquired_data[self.width:(2 * self.width) - 1] - acquired_data[0:self.width - 1])

                    # # Saving the data to file
                    now = datetime.datetime.now()
                    newpath = self.user_directory + '\\' + now.strftime('%Y-%m-%d') + '\\'
                    if not os.path.exists(newpath):
                        os.makedirs(newpath)
                    filename = QFileDialog.getSaveFileName(caption='File Name', filter='H5 (*.h5)',
                                                           directory=newpath)

                    if filename[0]:
                        acqproperties = savetofile.EmptyClass()
                        acqproperties.width = self.andor.width
                        acqproperties.time = self.exposuretime
                        acqproperties.number = frames

                        savetofile.save(spectral_data, str(filename[0]), acqproperties, acqtype='spectral')

                        self.progressbar.setValue(100)
                        post.eventlog(self, 'Spectral acquisition saved.')  # TODO Print file name saved to as well

                    else:
                        self.progressbar.setValue(100)
                        post.eventlog(self, 'Acquisition aborted.')

                    # Finishing up UI acquisition call
                    self.andor.setshutter(1, 2, 0, 0)
                    post.status(self, '')
                    self.buttonSpectralStart.setText('Start Spectral Acquisition')
                    self.progressbar.setValue(0)
                    toggle.activate_buttons(self)

                else:
                    # Finishing up UI acquisition call
                    self.andor.setshutter(1, 2, 0, 0)
                    post.status(self, '')
                    self.progressbar.setValue(0)
                    self.acquisition_cancelled = False
                    post.eventlog(self, 'Spectral acquisition aborted.')
                    self.buttonSpectralStart.setText('Start Spectral Acquisition')
                    toggle.activate_buttons(self)

            # Starting spectral acquisition thread and connecting to plot and store function
            self.threadpool.start(spectralthread)
            spectralthread.signals.dataSpectralAcquire.connect(plot_and_store)
            spectralthread.signals.finishedSpectralAcquire.connect(finished_acquisition)

        elif self.spectralacquiring is True:
            self.spectralacquiring = False
            spectralthread.stop()
            toggle.activate_buttons(self)
            post.status(self, '')
            self.buttonSpectralStart.setText('Start Spectral Acquisition')
        ##############

    def hyperacq_start(self):
        # Storing values for hyperspectral acquisition
        self.x_required = int(self.hyperspectralXPix.text())
        self.y_required = int(self.hyperspectralYPix.text())
        self.z_required = int(self.hyperspectralZPix.text())
        self.total_pixels = self.x_required * self.y_required * self.z_required

        xystep_voltage = float(self.hyperspectralXYStep.text()) / 20
        zstep_voltage = float(self.hyperspectralZStep.text()) / 2

        self.exposuretime = float(self.hyperspectralRequiredTime.text())
        self.background_frames = int(self.hyperspectralBackgroundFrames.text())

        # Creating an instance of the hyperspectral acquisition thread
        hyperthread = hyperacquire.HyperAcquireThread(self, self.x_required, self.y_required, self.z_required,
                                                      xystep_voltage, zstep_voltage,
                                                      self.exposuretime, self.background_frames)

        # If there's no acquisition taking place, then start one
        if self.hyperacquiring is False:
            self.hyperacquiring = True
            self.andor.setshutter(1, 1, 0, 0)
            toggle.deactivate_buttons(self, hyperacq_start_stat=True)
            post.status(self, 'Hyperspectral acquisition in progress...')
            self.buttonHyperspectralStart.setText('Stop Hyperspectral Acquisition')

            # Camera parameters for hyperspectral acquisition
            self.andor.freeinternalmemory()
            self.andor.setacquisitionmode(1)
            self.andor.setexposuretime(self.exposuretime)

            width = self.width
            self.hyperspectral_data = np.zeros((self.x_required, self.y_required, self.z_required, 2 * width))
            self.imageplot_data = np.zeros((self.x_required, self.y_required))

            time.sleep(1)

            # Starting hyperspectral acquisition thread and connecting to plot and store function
            self.start = time.time()
            self.threadpool.start(hyperthread)
            hyperthread.signals.dataHyperAcquire.connect(self.plot_and_store)
            hyperthread.signals.finishedHyperAcquire.connect(self.finished_acquisition)

        elif self.hyperacquiring is True:
            self.hyperacquiring = False
            hyperthread.stop()
            toggle.activate_buttons(self)
            post.status(self, '')
            self.buttonHyperspectralStart.setText('Start Hyperspectral Acquisition')
        ##############

    def hyperacq_update_time(self):
        x_required = int(self.hyperspectralXPix.text())
        y_required = int(self.hyperspectralYPix.text())
        z_required = int(self.hyperspectralZPix.text())

        exposuretime = float(self.hyperspectralRequiredTime.text())

        closed_multiplicative_factor = 12

        time_est_seconds = x_required * y_required * z_required * exposuretime * closed_multiplicative_factor
        self.hyperspectralEstTime.setText(str(time_est_seconds / 60))

    def plot_and_store(self, x_position, y_position, z_position):
        x_real = x_position + 1
        self.hyperspectral_data[x_position, y_position, z_position, :] = self.andor.imagearray
        self.imageplot_data[x_position, y_position] = np.mean(
            self.andor.imagearray[self.width:(2*self.width) - 1] - self.andor.imagearray[0:self.width - 1]
        )

        self.track1plot.setData(self.andor.imagearray[0:self.width - 1])
        self.track2plot.setData(self.andor.imagearray[self.width:(2*self.width) - 1])
        self.diffplot.setData(
            self.andor.imagearray[self.width:(2 * self.width) - 1] - self.andor.imagearray[0:self.width - 1]
        )
        self.imageplot.setImage(
            self.imageplot_data,
            autoDownsample=True
        )

        self.progressbar.setValue(
            (x_real + y_position * self.x_required + z_position * self.x_required * self.y_required) * 100 / self.total_pixels
        )

        QCoreApplication.processEvents()

        # TODO Implement image update as shown in google groups

    def finished_acquisition(self):
        if not self.acquisition_cancelled:
            finish = time.time()
            # Saving the data to file
            now = datetime.datetime.now()
            newpath = self.user_directory + '\\' + now.strftime('%Y-%m-%d') + '\\'
            if not os.path.exists(newpath):
                os.makedirs(newpath)
            filename = QFileDialog.getSaveFileName(caption='File Name', filter='H5 (*.h5)',
                                                   directory=newpath)

            if filename[0]:
                acqproperties = savetofile.EmptyClass()
                acqproperties.width = self.andor.width
                acqproperties.time = self.exposuretime
                acqproperties.xpixels = self.x_required
                acqproperties.ypixels = self.y_required
                acqproperties.zpixels = self.z_required
                acqproperties.xystep = float(self.hyperspectralXYStep.text())
                acqproperties.zstep = float(self.hyperspectralZStep.text())

                savetofile.save(self.hyperspectral_data, str(filename[0]), acqproperties,
                                acqtype='hyperspectral')

                # TODO progress bar
                post.eventlog(self, 'Hyperspectral acquisition saved')

            else:
                # TODO progress bar
                post.eventlog(self, 'Acquisition aborted.')

            # Finishing up UI acquisition call
            self.andor.setshutter(1, 2, 0, 0)
            post.status(self, '')
            self.buttonHyperspectralStart.setText('Start Hyperspectral Acquisition')
            self.progressbar.setValue(0)
            post.eventlog(self, 'Time taken: ' + str(round(finish - self.start, 1)) + 's')
            toggle.activate_buttons(self)

        else:
            # Finishing up UI acquisition call
            self.andor.setshutter(1, 2, 0, 0)
            post.status(self, '')
            self.progressbar.setValue(0)
            self.acquisition_cancelled = False
            post.eventlog(self, 'Hyperspectral acquisition aborted.')
            self.buttonHyperspectralStart.setText('Start Hyperspectral Acquisition')
            toggle.activate_buttons(self)


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
