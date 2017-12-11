from PyQt5.QtCore import QRunnable, pyqtSlot, pyqtSignal, QObject


class UpdateTime(QRunnable):
    def __init__(self, gui):
        super(UpdateTime, self).__init__()
        self.gui = gui

    @pyqtSlot()
    def run(self):
        messageSetExposureTime = self.gui.cam.SetExposureTime(float(self.gui.SpectralAcq_time_req.text()))
        if messageSetExposureTime is not None:
            self.gui.post.eventlog(self, messageSetExposureTime)

        messageGetAcquisitionTimings = self.gui.cam.GetAcquisitionTimings()
        if messageGetAcquisitionTimings is not None:
            self.gui.post.eventlog(self.gui, messageGetAcquisitionTimings)
            return
        else:
            self.gui.SpectralAcq_actual_time.setText(str("%.4f" % round(self.gui.cam.exposure, 4)))


class StartSignals(QObject):
    finished = pyqtSignal()


class Start(QRunnable):
    def __init__(self, gui):
        super(Start, self).__init__()
        self.gui = gui
        self.signals = StartSignals()

    @pyqtSlot()
    def run(self):
        time_req = float(self.gui.SpectralAcq_update_time.text())
        darkfield_req = int(self.gui.SpectralAcq_darkfield.text())

        self.signals.finished.emit()
