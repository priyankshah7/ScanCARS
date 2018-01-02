# ScanCARS v1
# Software to control the SIPCARS experimental setup
# Priyank Shah - King's College London

import sys, ctypes, time
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow

from scancars.gui import dialogs
from scancars.gui.forms import main
from scancars.gui.css import setstyle
from scancars.threads import uithreads
from scancars.utils import post, toggle, savetofile
from scancars.sdk.andor import pyandor

andor = pyandor.Cam()


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

        # Creating acquisition and CCD temperature loop conditions
        self.acquiring = False
        self.spectralacquiring = False
        self.hyperacquiring = False
        self.gettingtemp = False

        self.exposuretime = float(self.SpectralAcq_time_req.text())
        self.darkexposure = 0.1
        self.width = andor.width

        self.Main_specwin.plotItem.addLegend()

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
        # self.cam = Cam()
        self.initialize_andor()

        # ------------------------------------------------------------------------------------------------------------

    def __del__(self):
        post.eventlog(self, 'An error has occurred. This program will exit after the Andor camera has shut down.')
        andorthread = uithreads.AndorThread(self)
        andorthread.shutdown()

    # Initialize: defining functions
    def initialize_andor(self):
        toggle.deactivate_buttons(self)

        randtrack = np.array([int(self.CameraOptions_track1lower.text()),
                              int(self.CameraOptions_track1upper.text()),
                              int(self.CameraOptions_track2lower.text()),
                              int(self.CameraOptions_track2upper.text())])

        errorinitialize = andor.initialize()
        if errorinitialize != 'DRV_SUCCESS':
            post.eventlog(self, 'Andor: Initialize error. ' + errorinitialize)
            return
        andor.getdetector()
        andor.setshutter(1, 2, 0, 0)
        andor.setreadmode(2)
        andor.setrandomtracks(2, randtrack)
        andor.setadchannel(1)
        andor.settriggermode(0)
        andor.sethsspeed(1, 0)
        andor.setvsspeed(4)
        andor.dim = andor.width * andor.randomtracks

        toggle.activate_buttons(self)

        post.eventlog(self, 'Andor: Successfully initialized.')

        self.gettingtemp = True
        gettemperature = uithreads.TemperatureThread(self)
        self.threadpool.start(gettemperature)

    # Main: defining functions
    def main_startacq(self):
        # TODO Need to choose whether to use QThread or ORunnable
        startacq = uithreads.AcquireThread(self)
        if self.acquiring is False:
            self.acquiring = True
            self.threadpool.start(startacq)
        #
        # elif self.acquiring is True:
        #     startacq.stop()
        #     startacq.signals.finishedAcquireStop.connect(lambda: self.acquiring is False)
        #     # TODO Test the above lambda

        # startacq = uithreads.AcquireTest(self)
        # if self.acquiring is False:
        #     self.acquiring = True
        #     startacq.start()

        elif self.acquiring is True:
            self.acquiring = False
            toggle.activate_buttons(self)
            post.status(self, '')
            andor.setshutter(1, 2, 0, 0)
            self.Main_start_acq.setText('Start Acquisition')

    def main_shutdown(self):
        self.acquiring = False
        self.gettingtemp = False

        andor.setshutter(1, 2, 0, 0)
        andor.iscooleron()
        if andor.coolerstatus == 0:
            andor.shutdown()

            post.eventlog(self, 'ScanCARS can now be safely closed.')
            toggle.deactivate_buttons(self)

        elif andor.coolerstatus == 1:
            andor.cooleroff()
            self.CameraTemp_temp_actual.setStyleSheet("QLineEdit {background: #191919}")
            self.CameraTemp_cooler_on.setText('Cooler On')
            post.eventlog(self, 'Andor: Waiting for camera to return to normal temp...')
            andor.gettemperature()
            while andor.temperature < -20:
                time.sleep(2)
                andor.gettemperature()
            andor.shutdown()

            post.eventlog(self, 'ScanCARS can now be safely closed.')
            toggle.deactivate_buttons(self)

    # CameraTemp: defining functions
    def cameratemp_cooler(self):
        # Checking to see if the cooler is on or off
        messageIsCoolerOn = andor.iscooleron()
        if messageIsCoolerOn != 'DRV_SUCCESS':
            post.eventlog(self, 'Andor: IsCoolerOn error. ' + messageIsCoolerOn)

        else:
            if andor.coolerstatus == 0:
                # Turning the cooler on and checking to see if it has been turned on
                andor.cooleron()
                andor.iscooleron()
                if andor.coolerstatus == 1:
                    post.eventlog(self, 'Andor: Cooler on.')
                    self.CameraTemp_temp_actual.setStyleSheet("QLineEdit {background: #323e30}")
                    self.CameraTemp_cooler_on.setText('Cooler Off')

            elif andor.coolerstatus == 1:
                # Turning the cooler off and checking to see if it has been turned off
                andor.cooleroff()
                andor.iscooleron()
                if andor.coolerstatus == 0:
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
        # Storing the acquisition time
        self.exposuretime = float(self.SpectralAcq_time_req.text())
        post.eventlog(self, 'Andor: Exposure time set to ' + str(self.exposuretime) + 's')

    def spectralacq_start(self):
        spectralacqstart = uithreads.SpectralThread(self)
        self.threadpool.start(spectralacqstart)


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
