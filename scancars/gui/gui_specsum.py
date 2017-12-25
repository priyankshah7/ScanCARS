from PyQt5.QtWidgets import QMainWindow

from gui.forms import WindowSPECSUM


class SPECSUM(QMainWindow, WindowSPECSUM.Ui_Dialog):
    def __init__(self, parent=None):
        super(SPECSUM, self).__init__(parent)
        self.setupUi(self)