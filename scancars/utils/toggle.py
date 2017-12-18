# Functions to activate or deactivate all the buttons in the GUI
from scancars import main


class Toggle(main.ScanCARS):
    def __init__(self, parent=main.ScanCARS):
        super(Toggle, self).__init__(parent)

    def deactivate_buttons(self):
        self.Main_start_acq.setEnabled(False)
        self.Main_shutdown.setEnabled(False)
        self.CameraTemp_cooler_on.setEnabled(False)
        self.SpectraWin_sum_track.setEnabled(False)
        self.SpectraWin_single_track.setEnabled(False)
        self.Grating_update.setEnabled(False)
        self.CameraOptions_openimage.setEnabled(False)
        self.CameraOptions_update.setEnabled(False)
        self.SpectralAcq_start.setEnabled(False)
        self.SpectralAcq_update_time.setEnabled(False)
        self.HyperAcq_start.setEnabled(False)

    def activate_buttons(self):
        self.Main_start_acq.setEnabled(True)
        self.Main_shutdown.setEnabled(True)
        self.CameraTemp_cooler_on.setEnabled(True)
        self.SpectraWin_sum_track.setEnabled(True)
        self.SpectraWin_single_track.setEnabled(True)
        self.Grating_update.setEnabled(True)
        self.CameraOptions_openimage.setEnabled(True)
        self.CameraOptions_update.setEnabled(True)
        self.SpectralAcq_start.setEnabled(True)
        self.SpectralAcq_update_time.setEnabled(True)
        self.HyperAcq_start.setEnabled(True)
