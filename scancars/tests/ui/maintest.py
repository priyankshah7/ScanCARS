import sys, time
import numpy as np
from ctypes import *
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow

from scancars.tests.ui import testui
from scancars.sdk.andor import Cam
from scancars.threads import uithread

# TODO Consider replacing the classes style below with just def methods (and assigning pyqtSlot where needed
andor = Cam()


class TestUI(QMainWindow, testui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(TestUI, self).__init__(parent)
        self.setupUi(self)

        self.acquiring = False

        # Importing css style file
        stylefile = QtCore.QFile('./styletemp.css')
        stylefile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
        stylefile.open(QtCore.QFile.ReadOnly)
        self.setStyleSheet(str(stylefile.readAll(), 'utf-8'))
        stylefile.close()

        # Plot window settings
        self.specwin.enableAutoRange(x=False, y=True)
        self.specwin.setXRange(0, 512, padding=0)
        self.specwin.plotItem.addLegend()

        # Importing threads
        self.initializethread = Initialize()
        # self.startacqthread = Start(self)

        # TODO For sake of pyqtgraph plotting, need to move class initializations here.
        # TODO DO NOT DO THIS. Breaks plotting for some reason.

        # Connecting Start button to function
        self.startacq.clicked.connect(lambda: self.startplot())

        self.threadpool = QtCore.QThreadPool()
        self.initialize()

    def initialize(self):
        self.threadpool.start(self.initializethread)

    def startplot(self):
        startacqthread = Start(self)
        if self.acquiring is False:
            self.threadpool.start(startacqthread)
            self.acquiring = True

        elif self.acquiring is True:
            startacqthread.stop()
            self.acquiring = False


class Initialize(QtCore.QRunnable):
    def __init__(self):
        super(Initialize, self).__init__()

    @QtCore.pyqtSlot()
    def run(self):
        randtrack = np.array([153, 186, 211, 244])

        errorinitialize = andor.initialize()
        if errorinitialize != 'DRV_SUCCESS':
            print('Andor: Initialize error. ' + errorinitialize)
        andor.getdetector()
        andor.setshutter(1, 2, 0, 0)
        andor.setreadmode(2)
        andor.setrandomtracks(2, randtrack)
        andor.setadchannel(1)
        andor.settriggermode(0)
        andor.sethsspeed(1, 0)
        andor.setvsspeed(4)

        andor.dim = andor.width * andor.randomtracks

        print('finished initialization')


class Start(QtCore.QRunnable):
    def __init__(self, ui):
        super(Start, self).__init__()
        self.ui = ui
        self.condition = False
        self.width = andor.width

    def stop(self):
        self.condition = False
        andor.abortacquisition()

    @QtCore.pyqtSlot()
    def run(self):
        andor.setacquisitionmode(1)
        andor.setshutter(1, 1, 0, 0)
        andor.setexposuretime(0.2)

        self.ui.specwin.clear()
        track1plot = self.ui.specwin.plot()
        track2plot = self.ui.specwin.plot()
        trackdplot = self.ui.specwin.plot()

        self.condition = True
        while self.condition:
            andor.setexposuretime(0.2)
            andor.startacquisition()
            andor.waitforacquisition()
            andor.getacquireddata()

            imagearray = andor.imagearray

            track1plot.setData(imagearray[0:self.width - 1], pen='r', name='track1')
            track2plot.setData(imagearray[self.width:(2 * self.width) - 1], pen='g', name='track2')
            trackdplot.setData(imagearray[self.width:(2 * self.width) - 1] - imagearray[0:self.width - 1],
                               pen='w', name='trackdiff')

            andor.freeinternalmemory()


def main():
    app = QApplication(sys.argv)
    form = TestUI()
    form.setWindowTitle('ScanCARS Test')
    form.show()
    sys.exit(app.exec_())


# If the file is run directly and not imported, this runs the main function
if __name__ == '__main__':
    main()
