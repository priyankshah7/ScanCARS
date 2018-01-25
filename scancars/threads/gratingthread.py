from PyQt5 import QtCore


class WorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()


class GratingThread(QtCore.QRunnable):
    def __init__(self, device, query=None, value=None):
        super(GratingThread, self).__init__()
        self.isoplane = device
        self.query = query
        self.value = value

        self.signals = WorkerSignals()

    @QtCore.pyqtSlot()
    def run(self):
        if self.query == 'grating':
            self.set_grating(self.value)

        elif self.query == 'wavelength':
            self.set_nm(self.value)

    def set_grating(self, grating):
        self.isoplane.clear()
        success = self.isoplane.ask(str(grating) + ' GRATING')

        if success == ' ':
            self.signals.finished.emit()

    def set_nm(self, nm):
        self.isoplane.clear()
        success = self.isoplane.ask(str(nm) + ' NM')

        if success == ' ':
            self.signals.finished.emit()
