import time
from PyQt5.QtCore import QCoreApplication
from scancars.utils import toggle, post
from scancars.threads import liveacquire


def main_startacq(ui):
    # Creating an instance of the live acquisition thread
    acquirethread = liveacquire.LiveAcquireThread(ui)

    # If there's no current live acquisition taking place, then start one
    if ui.acquiring is False:
        ui.acquiring = True
        ui.andor.setshutter(1, 1, 0, 0)
        toggle.deactivate_buttons(ui, main_start_acq_stat=True)
        post.status(ui, 'Acquiring...')
        ui.buttonMainStartAcquisition.setText('Stop Acquisition')

        # Camera parameters from live acquisition
        ui.andor.freeinternalmemory()
        ui.andor.setacquisitionmode(1)
        ui.andor.setexposuretime(ui.exposuretime)

        time.sleep(1)

        # Starting live acquisition thread and connecting to plot function
        ui.threadpool.start(acquirethread)
        acquirethread.signals.dataLiveAcquire.connect(lambda: plot())

        def plot():
            ui.track1plot.setData(ui.andor.imagearray[0:ui.width - 1])
            ui.track2plot.setData(ui.andor.imagearray[ui.width:(2 * ui.width) - 1])
            ui.diffplot.setData(ui.andor.imagearray[ui.andor.width:(2 * ui.andor.width) - 1] -
                                ui.andor.imagearray[0:ui.andor.width - 1])

            ui.sumdialogplot.setData(ui.andor.imagearray[ui.width:(2 * ui.width) - 1] +
                                     ui.andor.imagearray[0:ui.width - 1])

            ui.diffdialogplot.setData(ui.andor.imagearray[ui.width:(2 * ui.width) - 1] -
                                      ui.andor.imagearray[0:ui.width - 1])

            QCoreApplication.processEvents()

    # If there's a live acquisition taking place, then stop it
    elif ui.acquiring is True:
        ui.acquiring = False
        acquirethread.stop()
        toggle.activate_buttons(ui)
        post.status(ui, '')
        ui.buttonMainStartAcquisition.setText('Start Acquisition')
