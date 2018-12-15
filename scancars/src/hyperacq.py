import os
import time
import datetime
import numpy as np
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QFileDialog

from scancars.utils import post, toggle, savetofile
from scancars.threads import hyperacquire


def hyperacq_start(ui):
    # Storing values for hyperspectral acquisition
    x_required = int(ui.hyperspectralXPix.text())
    y_required = int(ui.hyperspectralYPix.text())
    z_required = int(ui.hyperspectralZPix.text())

    xystep_voltage = float(ui.hyperspectralXYStep.text()) / 20
    zstep_voltage = float(ui.hyperspectralZStep.text()) / 2

    exposuretime = float(ui.hyperspectralRequiredTime.text())
    background_frames = int(ui.hyperspectralBackgroundFrames.text())

    # Creating an instance of the hyperspectral acquisition thread
    hyperthread = hyperacquire.HyperAcquireThread(ui, x_required, y_required, z_required,
                                                  xystep_voltage, zstep_voltage,
                                                  exposuretime, background_frames)

    # If there's no acquisition taking place, then start one
    if ui.hyperacquiring is False:
        ui.hyperacquiring = True
        ui.andor.setshutter(1, 1, 0, 0)
        toggle.deactivate_buttons(ui, hyperacq_start_stat=True)
        post.status(ui, 'Hyperspectral acquisition in progress...')
        ui.buttonHyperspectralStart.setText('Stop Hyperspectral Acquisition')

        # Camera parameters for hyperspectral acquisition
        ui.andor.freeinternalmemory()
        ui.andor.setacquisitionmode(1)
        ui.andor.setexposuretime(exposuretime)

        width = ui.width
        ui.hyperspectral_data = np.zeros((x_required, y_required, z_required, 2 * width))

        time.sleep(1)

        def plot_and_store(x_position, y_position, z_position):
            ui.hyperspectral_data[x_position, y_position, z_position, :] = ui.andor.imagearray

            ui.track1plot.setData(ui.andor.imagearray[0:ui.width - 1])
            ui.track2plot.setData(ui.andor.imagearray[ui.width:(2 * ui.width) - 1])
            ui.diffplot.setData(
                ui.andor.imagearray[ui.width:(2 * ui.width) - 1] - ui.andor.imagearray[0:ui.width - 1])

            ui.imagewinMain.setImage(np.squeeze(np.mean(
                ui.hyperspectral_data[:, :, z_position, ui.width:(2 * ui.width) - 1] - ui.hyperspectral_data[:, :, z_position, 0:ui.width - 1], 2)))

            # TODO Progress bar

            QCoreApplication.processEvents()

        def finished_acquisition():
            if not ui.acquisition_cancelled:
                finish = time.time()
                # Saving the data to file
                now = datetime.datetime.now()
                newpath = 'C:\\Users\\CARS\\Documents\\SIPCARS\\Data\\' + now.strftime('%Y-%m-%d') + '\\'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                filename = QFileDialog.getSaveFileName(caption='File Name', filter='H5 (*.h5)',
                                                       directory=newpath)

                if filename[0]:
                    acqproperties = savetofile.EmptyClass()
                    acqproperties.width = ui.andor.width
                    acqproperties.time = exposuretime
                    acqproperties.xpixels = x_required
                    acqproperties.ypixels = y_required
                    acqproperties.zpixels = z_required
                    acqproperties.xystep = float(ui.hyperspectralXYStep.text())
                    acqproperties.zstep = float(ui.hyperspectralZStep.text())

                    savetofile.save(ui.hyperspectral_data, str(filename[0]), acqproperties, acqtype='hyperspectral')

                    # TODO progress bar
                    post.eventlog(ui, 'Hyperspectral acquisition saved')

                else:
                    # TODO progress bar
                    post.eventlog(ui, 'Acquisition aborted.')

                # Finishing up UI acquisition call
                ui.andor.setshutter(1, 2, 0, 0)
                post.status(ui, '')
                ui.buttonHyperspectralStart.setText('Start Hyperspectral Acquisition')
                ui.progressbar.setValue(0)
                post.eventlog(ui, 'Time taken: ' + str(round(finish - ui.start, 1)) + 's')
                toggle.activate_buttons(ui)

            else:
                # Finishing up UI acquisition call
                ui.andor.setshutter(1, 2, 0, 0)
                post.status(ui, '')
                ui.progressbar.setValue(0)
                ui.acquisition_cancelled = False
                post.eventlog(ui, 'Hyperspectral acquisition aborted.')
                ui.buttonHyperspectralStart.setText('Start Hyperspectral Acquisition')
                toggle.activate_buttons(ui)

        # Starting hyperspectral acquisition thread and connecting to plot and store function
        ui.start = time.time()
        ui.threadpool.start(hyperthread)
        hyperthread.signals.dataHyperAcquire.connect(plot_and_store)
        hyperthread.signals.finishedHyperAcquire.connect(finished_acquisition)

    elif ui.hyperacquiring is True:
        ui.hyperacquiring = False
        hyperthread.stop()
        toggle.activate_buttons(ui)
        post.status(ui, '')
        ui.buttonHyperspectralStart.setText('Start Hyperspectral Acquisition')
    ##############


def hyperacq_update_time(ui):
    x_required = int(ui.hyperspectralXPix.text())
    y_required = int(ui.hyperspectralYPix.text())
    z_required = int(ui.hyperspectralZPix.text())

    exposuretime = float(ui.hyperspectralRequiredTime.text())

    closed_multiplicative_factor = 12

    time_est_seconds = x_required * y_required * z_required * exposuretime * closed_multiplicative_factor
    ui.hyperspectralEstTime.setText(str(time_est_seconds / 60))
