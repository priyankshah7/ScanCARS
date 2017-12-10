from PyQt5.QtCore import QRunnable, pyqtSlot, pyqtSignal, QObject


class UpdateTime(QRunnable):
    def __init__(self, gui):
        super(UpdateTime, self).__init__()
        self.gui = gui

    @pyqtSlot()
    def run(self):
        pass


class Start(QRunnable):
    def __init__(self, gui):
        super(Start, self).__init__()
        self.gui = gui

    @pyqtSlot()
    def run(self):
        time_req = float(self.gui.SpectralAcq_update_time.text())
        darkfield_req = int(self.gui.SpectralAcq_darkfield.text())
