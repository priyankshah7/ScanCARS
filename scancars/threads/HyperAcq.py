from PyQt5.QtCore import QRunnable, pyqtSlot, pyqtSignal, QObject


class StartSignals(QObject):
    finished = pyqtSignal()


class Start(QRunnable):
    def __init__(self, gui):
        super(Start, self).__init__()
        self.gui = gui
        self.signals = StartSignals()

    @pyqtSlot()
    def run(self):
        xpixel = int(self.gui.HyperAcq_xpixel.text())
        ypixel = int(self.gui.HyperAcq_ypixel.text())
        zpixel = int(self.gui.HyperAcq_zpixel.text())

        xystep = float(self.gui.HyperAcq_xystep.text())
        zstep = float(self.gui.HyperAcq_zstep.text())

        time_req = float(self.gui.HyperAcq_time_req.text())
        darkfield_req = int(self.gui.HyperAcq_darkfield.text())

        # do stuff ............

        self.signals.finished.emit()
