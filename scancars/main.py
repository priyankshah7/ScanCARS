# ScanCARS v1
# Software to control the SIPCARS experimental setup
# Priyank Shah - King's College London

import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow

from scancars.gui.forms import WindowMAIN
from scancars.gui import gui_camera, gui_specsum, gui_spectracks
from scancars.gui.css.setstyle import main
from scancars.threads import uithread, tempthread, specthread
from scancars.utils import post


class ScanCARS(QMainWindow, WindowMAIN.Ui_MainWindow):
    def __init__(self, parent=None):
        super(ScanCARS, self).__init__(parent)
        self.setupUi(self)

        # TODO Add options to take individual pump/Stokes. Will depend on being able to code up some shutters.
        # TODO If speed becomes an issue, consider using numba package with jit decorator
            # Required to use maths functions instead of numpy

        # TODO Reconsidering separating main functions completely.......

        # ------------------------------------------------------------------------------------------------------------
        # Importing relevant methods and classes
        self.post = post
        self.threadpool = QtCore.QThreadPool()
        self.acquiring = False

        # Creating variables for tracks (perhaps create function here instead)
        self.track1 = None
        self.track2 = None
        self.trackdiff = None
        self.tracksum = None

        self.Main_specwin.plotItem.addLegend()

        # Setting the css-style file
        main(self)

        # Creating variables to store instances of the camera and track/sum dialogs
        self.wincamera = None
        self.winspectracks = None
        self.winspecsum = None

        # Main: connecting buttons to functions
        self.Main_start_acq.clicked.connect(lambda: self.main_startacq())
        self.Main_shutdown.clicked.connect(lambda: self.main_shutdown())

        # CameraTemp: connecting buttons to functions
        self.CameraTemp_cooler_on.clicked.connect(lambda: self.cameratemp_cooler())

        # SpectraWin: connecting buttons to functions
        self.SpectraWin_single_track.clicked.connect(lambda: self.spectrawin_tracks())
        self.SpectraWin_sum_track.clicked.connect(lambda: self.spectrawin_sum())

        # Grating: connecting buttons to functions
        self.Grating_update.clicked.connect(lambda: self.grating_update())

        # CameraOptions: connecting buttons to functions
        self.CameraOptions_update.clicked.connect(lambda: self.cameraoptions_update())
        self.CameraOptions_openimage.clicked.connect(lambda: self.cameraoptions_openimage())

        # SpectralAcq: connecting buttons to functions
        self.SpectralAcq_update_time.clicked.connect(lambda: self.spectralacq_updatetime())
        self.SpectralAcq_start.clicked.connect(lambda: self.spectralacq_start())

        # HyperAcq: connecting buttons to functions
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
        uithread.Shutdown(self)

    # Initialize: defining functions
    def initialize_andor(self):
        initialize = uithread.Initialize(self)
        self.threadpool.start(initialize)
        initialize.signals.finished.connect(lambda: self.initialize_gettemp())

    def initialize_gettemp(self):
        post.eventlog(self, 'Andor: Successfully initialized.')
        gettemperature = tempthread.AndorTemperature(self)
        self.threadpool.start(gettemperature)

    # Main: defining functions
    def main_startacq(self):
        startacq = specthread.Acquire(self)
        if self.acquiring is False:
            self.threadpool.start(startacq)
            self.acquiring = True
            post.eventlog(self, 'acq is true')

        elif self.acquiring is True:
            startacq.stop()
            self.acquiring = False
            post.eventlog(self, 'acq is false')

    def main_shutdown(self):
        shutdown = uithread.Shutdown(self)
        self.threadpool.start(shutdown)
        shutdown.signals.finished.connect(lambda: post.eventlog(self, 'ScanCARS can now be safely closed.'))

    # CameraTemp: defining functions
    def cameratemp_cooler(self):
        messageIsCoolerOn = self.cam.IsCoolerOn()
        if messageIsCoolerOn is not None:
            post.eventlog(self, messageIsCoolerOn)

        else:
            if self.cam.coolerstatus == 0:
                cooleron = tempthread.CoolerOn(self)
                self.threadpool.start(cooleron)
                cooleron.signals.finished.connect(lambda: post.eventlog(self, 'Andor: Cooler on.'))
                self.CameraTemp_temp_actual.setStyleSheet("QLineEdit {background: #323e30}")

            elif self.cam.coolerstatus == 1:
                cooleroff = tempthread.CoolerOff(self)
                self.threadpool.start(cooleroff)
                cooleroff.signals.finished.connect(lambda: post.eventlog(self, 'Andor: Cooler switched off.'))
                self.CameraTemp_temp_actual.setStyleSheet("QLineEdit {background: #191919}")

            else:
                post.eventlog(self, 'An error has occured. Possibly related to the GUI itself?')

    # SpectraWin: defining functions
    def spectrawin_tracks(self):
        self.winspectracks = gui_spectracks.SPECTRACKS()
        self.winspectracks.setWindowTitle('Individual Tracks Spectra')
        self.winspectracks.show()

    def spectrawin_sum(self):
        self.winspecsum = gui_specsum.SPECSUM()
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
        self.wincamera = gui_camera.CAMERA()
        self.wincamera.setWindowTitle('Live CCD Video')
        self.wincamera.show()

        pass

    # SpectralAcq: defining functions
    def spectralacq_updatetime(self):
        pass

    def spectralacq_start(self):
        pass

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
