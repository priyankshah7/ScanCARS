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

    self.buttonMainStartAcquisition.setEnabled(main_start_acq_stat)
    self.buttonMainShutdown.setEnabled(main_shutdown_stat)
    self.buttonCameratempCooler.setEnabled(cameratemp_cooler_stat)
    self.buttonDialogsSum.setEnabled(spectrawin_sum_stat)
    self.buttonDialogsDifference.setEnabled(spectrawin_single_stat)
    # self.buttonGratingUpdate.setEnabled(grating_update_stat)
    self.buttonCamtrackView.setEnabled(cameraoptions_openimage_stat)
    self.buttonCamtrackUpdate.setEnabled(cameraoptions_update_stat)
    self.buttonSpectralStart.setEnabled(spectralacq_start_stat)
    self.buttonSpectralUpdate.setEnabled(spectralacq_update_stat)
    self.buttonHyperspectralStart.setEnabled(hyperacq_start_stat)


def activate_buttons(self, main_start_acq_stat=True, main_shutdown_stat=True, cameratemp_cooler_stat=True,
                     spectrawin_sum_stat=True, spectrawin_single_stat=True, grating_update_stat=True,
                     cameraoptions_openimage_stat=True, cameraoptions_update_stat=True,
                     spectralacq_start_stat=True, spectralacq_update_stat=True, hyperacq_start_stat=True):

    self.buttonMainStartAcquisition.setEnabled(main_start_acq_stat)
    self.buttonMainShutdown.setEnabled(main_shutdown_stat)
    self.buttonCameratempCooler.setEnabled(cameratemp_cooler_stat)
    self.buttonDialogsSum.setEnabled(spectrawin_sum_stat)
    self.buttonDialogsDifference.setEnabled(spectrawin_single_stat)
    # self.buttonGratingUpdate.setEnabled(grating_update_stat)
    self.buttonCamtrackView.setEnabled(cameraoptions_openimage_stat)
    self.buttonCamtrackUpdate.setEnabled(cameraoptions_update_stat)
    self.buttonSpectralStart.setEnabled(spectralacq_start_stat)
    self.buttonSpectralUpdate.setEnabled(spectralacq_update_stat)
    self.buttonHyperspectralStart.setEnabled(hyperacq_start_stat)
