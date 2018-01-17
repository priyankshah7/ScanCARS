import sys
import time
import ctypes
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog

from scancars.gui import dialogs
from scancars.gui.forms import main
from scancars.gui.css import setstyle
from scancars.threads import uithreads
from scancars.utils import post, toggle, savetofile
from scancars.sdk.andor import pyandor


class ScanCARS(QMainWindow, main.Ui_MainWindow):
    def __init__(self, parent=None):
        super(ScanCARS, self).__init__(parent)
        self.setupUi(self)

        # TODO Add options to take individual pump/Stokes. Will depend on being able to code up some shutters.
        # TODO If speed becomes an issue, consider using numba package with jit decorator
            # Required to use maths functions instead of numpy

        # ------------------------------------------------------------------------------------------------------------
        # Importing relevant methods and classes
        self.threadpool = QtCore.QThreadPool()
        self.andor = pyandor.Cam()

        # Creating acquisition and CCD temperature loop conditions
        self.acquiring = False
        self.spectralacquiring = False
        self.hyperacquiring = False
        self.gettingtemp = False

        # Storing exposure times
        self.exposuretime = float(self.SpectralAcq_time_req.text())
        self.darkexposure = 0.1

        # Plot settings
        # self.Main_specwin.plotItem.addLegend()
        self.Main_specwin.plotItem.showGrid(x=True, y=True)
        self.Main_specwin.setXRange(-10, 520, padding=0)
        # self.Main_specwin.setYRange(-65000, 65000, padding=0)
        # self.Main_specwin.plotItem.

        # Setting the css-style file
        setstyle.main(self)

        # Creating variables to store instances of the camera and track/sum dialogs
        self.wincamera = None
        self.winspectracks = None
        self.winspecsum = None

        # Connecting buttons to methods
        self.Main_start_acq.clicked.connect(lambda: self.main_startacq())
        self.Main_shutdown.clicked.connect(lambda: self.main_shutdown())
        self.CameraTemp_cooler_on.clicked.connect(lambda: self.cameratemp_cooler())
        self.SpectraWin_single_track.clicked.connect(lambda: self.spectrawin_tracks())
        self.SpectraWin_sum_track.clicked.connect(lambda: self.spectrawin_sum())
        self.Grating_update.clicked.connect(lambda: self.grating_update())
        self.CameraOptions_update.clicked.connect(lambda: self.cameraoptions_update())
        self.CameraOptions_openimage.clicked.connect(lambda: self.cameraoptions_openimage())
        self.SpectralAcq_update_time.clicked.connect(lambda: self.spectralacq_updatetime())
        self.SpectralAcq_start.clicked.connect(lambda: self.spectralacq_start())
        self.HyperAcq_start.clicked.connect(lambda: self.hyperacq_start())

        # ------------------------------------------------------------------------------------------------------------

        # ------------------------------------------------------------------------------------------------------------
        # Startup Processes
        post.event_date(self)

        # Initializing the camera
        self.initialize_andor()
        self.width = self.andor.width
        # ------------------------------------------------------------------------------------------------------------

    def __del__(self):
        post.eventlog(self, 'An error has occurred. This program will exit after the Andor camera has shut down.')
        self.main_shutdown()

    # Initialize: defining functions
    def initialize_andor(self):
        toggle.deactivate_buttons(self)

        # Storing the positions of the random tracks in an array
        randtrack = np.array([int(self.CameraOptions_track1lower.text()),
                              int(self.CameraOptions_track1upper.text()),
                              int(self.CameraOptions_track2lower.text()),
                              int(self.CameraOptions_track2upper.text())])

        errorinitialize = self.andor.initialize()       # Initializing the detector
        if errorinitialize != 'DRV_SUCCESS':
            post.eventlog(self, 'Andor: Initialize error. ' + errorinitialize)
            return
        self.andor.getdetector()                        # Getting information from the detector
        self.andor.setshutter(1, 2, 0, 0)               # Ensuring the shutter is closed
        self.andor.setreadmode(2)                       # Setting the read mode to Random Tracks
        self.andor.setrandomtracks(2, randtrack)        # Setting the position of the random tracks
        self.andor.setadchannel(1)                      # Setting the AD channel
        self.andor.settriggermode(0)                    # Setting the trigger mode to 'internal'
        self.andor.sethsspeed(1, 0)                     # Setting the horiz. shift speed
        self.andor.setvsspeed(4)                        # Setting the verti. shift speed

        time.sleep(2)

        self.andor.dim = self.andor.width * self.andor.randomtracks

        toggle.activate_buttons(self)
        post.eventlog(self, 'Andor: Successfully initialized.')

        # Starting the temperature thread to monitor the temperature of the camera
        self.gettingtemp = True
        gettemperature = uithreads.TemperatureThread(self)
        self.threadpool.start(gettemperature)

    # Main: defining functions
    def main_startacq(self):
        # startacq = uithreads.AcquireThread(self)
        # if self.acquiring is False:
        #     self.acquiring = True
        #     self.threadpool.start(startacq)
        #
        # elif self.acquiring is True:
        #     self.acquiring = False
        #     toggle.activate_buttons(self)
        #     post.status(self, '')
        #     self.andor.setshutter(1, 2, 0, 0)
        #     self.Main_start_acq.setText('Start Acquisition')

        # NOTE The acquiring thread has been moved here (no thread)
        # This has solved the plot hanging after a certain number of plots
        # This needs to be moved into a multiprocessing process though

        if self.acquiring is False:
            self.acquiring = True
            toggle.deactivate_buttons(self, main_start_acq_stat=True)
            post.status(self, 'Acquiring...')
            self.Main_start_acq.setText('Stop Acquisition')

            self.Main_specwin.clear()
            track1plot = self.Main_specwin.plot(pen='r', name='track1')
            track2plot = self.Main_specwin.plot(pen='g', name='track2')
            diffplot = self.Main_specwin.plot(pen='w', name='trackdiff')

            cimage = (ctypes.c_int * self.andor.dim)()

            self.andor.freeinternalmemory()
            self.andor.setacquisitionmode(1)
            self.andor.setshutter(1, 1, 0, 0)
            self.andor.setexposuretime(self.exposuretime)

            # istracksvisisble = dialogs.SPECTRACKS.isVisible()
            # if istracksvisisble:
            #     print('true')

            while self.acquiring:
                self.andor.startacquisition()
                self.andor.waitforacquisition()
                self.andor.getacquireddata(cimage)

                track1plot.setData(self.andor.imagearray[0:self.andor.width - 1])
                track2plot.setData(self.andor.imagearray[self.andor.width:(2 * self.andor.width) - 1])
                diffplot.setData(
                    self.andor.imagearray[self.andor.width:(2 * self.andor.width) - 1] - self.andor.imagearray[
                                                                                0:self.andor.width - 1], )

                QtCore.QCoreApplication.processEvents()

        elif self.acquiring is True:
            self.acquiring = False
            toggle.activate_buttons(self)
            post.status(self, '')
            self.Main_start_acq.setText('Start Acquisition')
            self.andor.setshutter(1, 2, 0, 0)

    def main_shutdown(self):
        # Ensuring all acquiring and temperature loops have been stopped
        self.acquiring = False
        self.gettingtemp = False

        # Turning the shutter off and checking to see if the camera cooler is on
        self.andor.setshutter(1, 2, 0, 0)
        self.andor.iscooleron()

        # If the cooler is off, proceed to shutdown the camera
        if self.andor.coolerstatus == 0:
            self.andor.shutdown()

            post.eventlog(self, 'ScanCARS can now be safely closed.')
            toggle.deactivate_buttons(self)

        # If the cooler is on, turn it off, wait for temp. to increase to -20C, and then shutdown camera
        elif self.andor.coolerstatus == 1:
            self.andor.gettemperature()
            if self.andor.temperature < -20:
                post.eventlog(self, 'Andor: Waiting for camera to return to normal temp...')
            self.andor.cooleroff()
            self.CameraTemp_temp_actual.setStyleSheet("QLineEdit {background: #191919}")
            self.CameraTemp_cooler_on.setText('Cooler On')
            time.sleep(1)
            while self.andor.temperature < -20:
                time.sleep(3)
                self.andor.gettemperature()

            self.andor.shutdown()

            post.eventlog(self, 'ScanCARS can now be safely closed.')
            toggle.deactivate_buttons(self)

    # CameraTemp: defining functions
    def cameratemp_cooler(self):
        # Checking to see if the cooler is on or off
        messageIsCoolerOn = self.andor.iscooleron()
        if messageIsCoolerOn != 'DRV_SUCCESS':
            post.eventlog(self, 'Andor: IsCoolerOn error. ' + messageIsCoolerOn)

        else:
            if self.andor.coolerstatus == 0:
                # Turning the cooler on and checking to see if it has been turned on
                self.andor.settemperature(int(self.CameraTemp_temp_req.text()))
                self.andor.cooleron()
                self.andor.iscooleron()
                if self.andor.coolerstatus == 1:
                    post.eventlog(self, 'Andor: Cooler on.')
                    self.CameraTemp_temp_actual.setStyleSheet("QLineEdit {background: #323e30}")
                    self.CameraTemp_cooler_on.setText('Cooler Off')

            elif self.andor.coolerstatus == 1:
                # Turning the cooler off and checking to see if it has been turned off
                self.andor.cooleroff()
                self.andor.iscooleron()
                if self.andor.coolerstatus == 0:
                    post.eventlog(self, 'Andor: Cooler off.')
                    self.CameraTemp_temp_actual.setStyleSheet("QLineEdit {background: #191919}")
                    self.CameraTemp_cooler_on.setText('Cooler On')

            else:
                # Shouldn't expect this to be called, if it is then it's unlikely to be related to the Andor
                post.eventlog(self, 'An error has occured. Possibly related to the GUI itself?')

    # SpectraWin: defining functions
    def spectrawin_tracks(self):
        self.winspectracks = dialogs.SPECTRACKS()
        self.winspectracks.setWindowTitle('Individual Tracks Spectra')
        self.winspectracks.show()

    def spectrawin_sum(self):
        self.winspecsum = dialogs.SPECSUM()
        self.winspecsum.setWindowTitle('Sum Track Spectrum')
        self.winspecsum.show()

    # Grating: defining functions
    def grating_update(self):
        pass

    # CameraOptions: defining functions
    def cameraoptions_update(self):
        pass

    def cameraoptions_openimage(self):
        # openimage = CameraOptions.OpenImage(self)
        # self.threadpool.start(openimage)
        self.wincamera = dialogs.CAMERA()
        self.wincamera.setWindowTitle('Live CCD Video')
        self.wincamera.show()

        pass

    # SpectralAcq: defining functions
    def spectralacq_updatetime(self):
        # Storing and setting the acquisition time
        self.exposuretime = float(self.SpectralAcq_time_req.text())
        self.andor.setexposuretime(self.exposuretime)

        # Updating the actual acquisition time that has been set
        self.andor.getacquisitiontimings()
        self.SpectralAcq_actual_time.setText(str(round(self.andor.exposure, 3)))
        post.eventlog(self, 'Andor: Exposure time set to ' + str(self.exposuretime) + 's')

    def spectralacq_start(self):
        toggle.deactivate_buttons(self)
        self.spectralacquiring = True
        post.status(self, 'Spectral acquisition in progress...')
        self.Main_progress.setValue(0)

        exposuretime = float(self.SpectralAcq_time_req.text())
        frames = int(self.SpectralAcq_frames.text())
        # darkcount = int(self.SpectralAcq_darkfield.text())
        darkcount = 0

        # Expected time
        total = (darkcount * self.darkexposure) + (frames * exposuretime)
        # progress_darkcount = ((darkcount * self.ui.darkexposure) / total) * 100

        # Spectral acquisitions
        # self.andor.setshutter(1, 1, 0, 0)
        # self.andor.setexposuretime(exposuretime)
        # self.andor.setnumberkinetics(frames)
        # self.andor.setacquisitionmode(3)
        #
        # time.sleep(2)
        #
        # self.andor.startacquisition()
        # self.andor.getstatus()
        # while self.andor.getstatusval == 'DRV_ACQUIRING':
        #     time.sleep(exposuretime/10)
        #     self.andor.getstatus()
        #
        # cimage = (ctypes.c_long * frames * self.andor.dim)()
        # self.andor.getacquireddata(cimage, frames)
        # spectral_data = self.andor.imagearray

        # Converting the acquisition from using Kinetic series to Single scan
        self.andor.setshutter(1, 1, 0, 0)
        self.andor.setexposuretime(exposuretime)
        self.andor.setacquisitionmode(1)
        cimage = (ctypes.c_long * self.andor.dim)()

        time.sleep(2)
        spectral_data = [0]*frames

        numscan = 0
        while numscan < frames:
            self.andor.startacquisition()
            self.andor.waitforacquisition()
            self.andor.getacquireddata(cimage, 1)
            spectral_data[numscan] = self.andor.imagearray

            self.Main_progress.setValue((numscan+1)/frames * 100)
            numscan += 1

        spectral_data = np.asarray(spectral_data)
        spectral_data = np.transpose(spectral_data)

        # # Plotting the mean spectrum
        self.Main_specwin.clear()
        self.Main_specwin.plot(np.mean(spectral_data[0:511, :], 1), pen='r')
        self.Main_specwin.plot(np.mean(spectral_data[512:1023, :], 1), pen='g')
        self.Main_specwin.plot(np.mean(spectral_data[512:1023, :] - spectral_data[0:511, :], 1), pen='w')

        # # Saving the data to file
        filename = QFileDialog.getSaveFileName(caption='File Name', filter='H5 (*.h5)',
                                               directory='C:\\Users\\CARS\\Documents\\LabVIEW Data\\CARS data files\\priyank\\new software')

        if filename[0]:
            acqproperties = savetofile.EmptyClass()
            acqproperties.width = self.andor.width
            acqproperties.time = exposuretime
            acqproperties.number = frames

            savetofile.save(spectral_data, str(filename[0]), acqproperties, acqtype='spectral')

            post.eventlog(self, 'Spectral acquisition saved.')  # TODO Print file name saved to as well

        else:
            post.eventlog(self, 'Acquisition aborted.')

        # Finishing up UI acquisition call
        self.andor.setshutter(1, 2, 0, 0)
        post.status(self, '')
        self.spectralacquiring = False
        self.Main_progress.setValue(100)
        toggle.activate_buttons(self)


    # HyperAcq: defining functions
    def hyperacq_start(self):
        pass


def main():
    app = QApplication(sys.argv)
    form = ScanCARS()
    form.setWindowTitle('ScanCARS')
    form.show()
    sys.exit(app.exec_())


# If the file is run directly and not imported, this runs the main function
if __name__ == '__main__':
    main()
