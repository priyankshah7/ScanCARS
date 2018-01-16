# Functions to activate/deactivate pushbuttons in the main GUI
"""
All pushbuttons are, by default, set to be activated/deactivated depending on which method is called.
However individual buttons can be set to be countered to the main call (e.g. activated despite call
for deactivate_buttons() by doing the following:

e.g. deactivate all buttons apart from the main Shutdown pushbutton:

    deactivate_buttons(self, main_shutdown_stat=True)
"""

# (TODO) Set stylefiles to change here when activating/deactivating buttons


def deactivate_buttons(self, main_start_acq_stat=False, main_shutdown_stat=False, cameratemp_cooler_stat=False,
                       spectrawin_sum_stat=False, spectrawin_single_stat=False, grating_update_stat=False,
                       cameraoptions_openimage_stat=False, cameraoptions_update_stat=False,
                       spectralacq_start_stat=False, spectralacq_update_stat=False, hyperacq_start_stat=False):

    self.Main_start_acq.setEnabled(main_start_acq_stat)
    self.Main_shutdown.setEnabled(main_shutdown_stat)
    self.CameraTemp_cooler_on.setEnabled(cameratemp_cooler_stat)
    self.SpectraWin_sum_track.setEnabled(spectrawin_sum_stat)
    self.SpectraWin_single_track.setEnabled(spectrawin_single_stat)
    self.Grating_update.setEnabled(grating_update_stat)
    self.CameraOptions_openimage.setEnabled(cameraoptions_openimage_stat)
    self.CameraOptions_update.setEnabled(cameraoptions_update_stat)
    self.SpectralAcq_start.setEnabled(spectralacq_start_stat)
    self.SpectralAcq_update_time.setEnabled(spectralacq_update_stat)
    self.HyperAcq_start.setEnabled(hyperacq_start_stat)


def activate_buttons(self, main_start_acq_stat=True, main_shutdown_stat=True, cameratemp_cooler_stat=True,
                     spectrawin_sum_stat=True, spectrawin_single_stat=True, grating_update_stat=True,
                     cameraoptions_openimage_stat=True, cameraoptions_update_stat=True,
                     spectralacq_start_stat=True, spectralacq_update_stat=True, hyperacq_start_stat=True):

    self.Main_start_acq.setEnabled(main_start_acq_stat)
    self.Main_shutdown.setEnabled(main_shutdown_stat)
    self.CameraTemp_cooler_on.setEnabled(cameratemp_cooler_stat)
    self.SpectraWin_sum_track.setEnabled(spectrawin_sum_stat)
    self.SpectraWin_single_track.setEnabled(spectrawin_single_stat)
    self.Grating_update.setEnabled(grating_update_stat)
    self.CameraOptions_openimage.setEnabled(cameraoptions_openimage_stat)
    self.CameraOptions_update.setEnabled(cameraoptions_update_stat)
    self.SpectralAcq_start.setEnabled(spectralacq_start_stat)
    self.SpectralAcq_update_time.setEnabled(spectralacq_update_stat)
    self.HyperAcq_start.setEnabled(hyperacq_start_stat)
