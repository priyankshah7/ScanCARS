from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow

from scancars.tests.ui import testui
from andorsdk.pyandor import Andor

import sys, time
import numpy as np
from ctypes import *

# TODO Consider replacing the classes style below with just def methods (and assigning pyqtSlot where needed


class TestUI(QMainWindow, testui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(TestUI, self).__init__(parent)
        self.setupUi(self)
        self.dll = cdll.LoadLibrary("C:\\Program Files\\Andor iXon\\Drivers\\atmcd64d")

        self.width = None

        self.threadpool = QtCore.QThreadPool()
        self.initialize()
        self.acquire = Acquire()

        # Connecting Start button to function
        self.startacq.clicked.connect(lambda: self.startplot())

    def initialize(self):
        self.dll.Initialize()
        self.dll.SetShutter(1, 2, 0, 0)
        self.dll.SetReadMode(2)

        trackposition = np.array([154, 187, 211, 244])

        self.dll.SetRandomTracks(2, trackposition.ctypes.data_as(POINTER(c_long)))
        self.dll.SetADChannel(1)
        self.dll.SetTriggerMode(0)

        cw = c_int()
        ch = c_int()

        self.dll.GetDetector(byref(cw), byref(ch))
        self.width = cw.value

        self.dll.SetHSSpeed(1, 0)
        self.dll.SetVSSpeed(3)

    def startplot(self):
        if self.acquire.condition is False:
            self.threadpool.start(self.acquire)
            print('starting acq...')

        elif self.acquire.condition is True:
            self.acquire.stop()
            print('stopping acq...')


class AcquireSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()


class Acquire(QtCore.QRunnable):
    def __init__(self):
        super(Acquire, self).__init__()
        self.dll = cdll.LoadLibrary("C:\\Program Files\\Andor iXon\\Drivers\\atmcd64d")
        self.condition = False
        self.signals = AcquireSignals()

        imagearray = c_int * 1024
        self.cimage = imagearray()

        # self.gui = TestUI()

    @QtCore.pyqtSlot()
    def stop(self):
        self.condition = False
        self.signals.finished.emit()

    @QtCore.pyqtSlot()
    def run(self):
        self.dll.SetAcquisitionMode(1)
        self.dll.SetShutter(1, 1, 0, 0)

        self.condition = True
        # while self.condition:
        #     self.dll.SetExposureTime(0.1)
        #     self.dll.StartAcquisition()
        #
        #     self.dll.WaitForAcquisition()
        #
        #     self.dll.GetAcquiredData(pointer(self.cimage), 1024)
        #
        #     image = np.asarray(self.cimage[:])
        #
        #     track1 = image[0:511]
        #     track2 = image[512:1023]
        #     trackdiff = track2 - track1
        #
        #     self.gui.specwin.clear()
        #     self.gui.specwin.plot(track1, pen='r', name='track1')
        #     self.gui.specwin.plot(track2, pen='r', name='track2')
        #     self.gui.specwin.plot(trackdiff, pen='r', name='trackdiff')
        #
        #     self.dll.FreeInternalMemory()

        self.signals.finished.emit()


def main():
    app = QApplication(sys.argv)
    form = TestUI()
    form.setWindowTitle('ScanCARS Test')
    form.show()
    sys.exit(app.exec_())


# If the file is run directly and not imported, this runs the main function
if __name__ == '__main__':
    main()