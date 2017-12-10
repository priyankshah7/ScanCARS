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

    @pyqtSlot()
    def run(self):
        pass
