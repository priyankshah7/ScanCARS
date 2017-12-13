from PyQt5.QtCore import QRunnable, pyqtSlot, pyqtSignal, QObject


class Update(QRunnable):
    def __init__(self, gui):
        super(Update, self).__init__()
        self.gui = gui

    @pyqtSlot()
    def run(self):
        RandomTrackposition = [int(self.gui.CameraOptions_track1lower.text()),
                               int(self.gui.CameraOptions_track1upper.text()),
                               int(self.gui.CameraOptions_track2lower.text()),
                               int(self.gui.CameraOptions_track2upper.text())]

        messageSetRandomTrack = self.gui.cam.SetRandomTracks(2, RandomTrackposition)
        if messageSetRandomTrack is not None:
            self.gui.post.eventlog(self.gui, messageSetRandomTrack)
            return


class OpenImage(QRunnable):
    def __init__(self, gui):
        super(OpenImage, self).__init__()
        self.gui = gui
        self.acquiring = False

    @pyqtSlot()
    def run(self):
        messageSetAcquisitionMode = self.gui.cam.SetAcquisitionMode(1)
        if messageSetAcquisitionMode is not None:
            self.gui.post.eventlog(self.gui, messageSetAcquisitionMode)
            return

        nessageSetReadMode = self.gui.cam.SetReadMode(4)
        if nessageSetReadMode is not None:
            self.gui.post.eventlog(self.gui, nessageSetReadMode)
            return

        self.acquiring = self.gui.wincamera.isVisible()
        while self.acquiring:
            self.acquiring = self.gui.wincamera.isVisible()
            messageStartAcquisition = self.gui.cam.StartAcquisition()
            messageGetAcquiredData = self.gui.cam.GetAcquiredData()

