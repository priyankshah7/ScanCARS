import os
import time
import datetime
import numpy as np
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QFileDialog

from scancars.utils import post, toggle, savetofile
from scancars.threads import spectralacquire


def spectralacq_update(ui):
    # Storing and setting the acquisition time
    ui.exposuretime = float(ui.spectralRequiredTime.text())
    ui.andor.setexposuretime(ui.exposuretime)

    # Updating the actual acquisition time that has been set
    ui.andor.getacquisitiontimings()
    ui.spectralActualTime.setText(str(round(ui.andor.exposure, 3)))
    post.eventlog(ui, 'Andor: Exposure time set to ' + str(ui.exposuretime) + 's')


def spectralacq_start(ui):
    # Creating an instance of the spectral acquisition thread
    frames = int(ui.spectralFrames.text())
    darkcount = int(ui.spectralBackgroundFrames.text())
    spectralthread = spectralacquire.SpectralAcquireThread(ui, frames, darkcount)

    # If there's no acquisition taking place, then start one
    if ui.spectralacquiring is False:
        ui.spectralacquiring = True
        ui.andor.setshutter(1, 1, 0, 0)
        toggle.deactivate_buttons(ui, spectralacq_start_stat=True)
        post.status(ui, 'Spectral acquisition in progress...')
        ui.buttonSpectralStart.setText('Stop Spectral Acquisition')

        # Camera parameters for spectral acquisition
        ui.andor.freeinternalmemory()
        ui.andor.setacquisitionmode(1)
        ui.andor.setexposuretime(ui.exposuretime)

        ui.spectral_data = [0] * frames

        time.sleep(1)

        def plot_and_store(numscan):
            ui.spectral_data[numscan] = ui.andor.imagearray
            # TODO use spectra_data instead of imagearray following from here
            ui.track1plot.setData(ui.andor.imagearray[0:ui.width - 1])
            ui.track2plot.setData(ui.andor.imagearray[ui.width:(2 * ui.width) - 1])
            ui.diffplot.setData(
                ui.andor.imagearray[ui.width:(2 * ui.width) - 1] - ui.andor.imagearray[0:ui.width - 1])

            ui.progressbar.setValue((darkcount + numscan + 1) / (darkcount + frames) * 100)

            QCoreApplication.processEvents()

        def finished_acquisition():
            if not ui.acquisition_cancelled:
                # Processing data
                spectral_data = np.asarray(ui.spectral_data)
                spectral_data = np.transpose(spectral_data)

                acquired_data = np.mean(spectral_data, 1)  # - np.mean(dark_data, 1)

                # Plotting the mean spectrum
                ui.track1plot.setData(acquired_data[0:ui.width - 1])
                ui.track2plot.setData(acquired_data[ui.width:(2 * ui.width) - 1])
                ui.diffplot.setData(acquired_data[ui.width:(2 * ui.width) - 1] - acquired_data[0:ui.width - 1])

                ui.previousplot.setData(
                    acquired_data[ui.width:(2 * ui.width) - 1] - acquired_data[0:ui.width - 1])

                # # Saving the data to file
                now = datetime.datetime.now()
                newpath = 'C:\\Users\\CARS\\Documents\\SIPCARS\\Data\\' + now.strftime('%Y-%m-%d') + '\\'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                filename = QFileDialog.getSaveFileName(caption='File Name', filter='H5 (*.h5)',
                                                       directory=newpath)

                if filename[0]:
                    acqproperties = savetofile.EmptyClass()
                    acqproperties.width = ui.andor.width
                    acqproperties.time = ui.exposuretime
                    acqproperties.number = frames

                    savetofile.save(spectral_data, str(filename[0]), acqproperties, acqtype='spectral')

                    ui.progressbar.setValue(100)
                    post.eventlog(ui, 'Spectral acquisition saved.')  # TODO Print file name saved to as well

                else:
                    ui.progressbar.setValue(100)
                    post.eventlog(ui, 'Acquisition aborted.')

                # Finishing up UI acquisition call
                ui.andor.setshutter(1, 2, 0, 0)
                post.status(ui, '')
                ui.buttonSpectralStart.setText('Start Spectral Acquisition')
                ui.progressbar.setValue(0)
                toggle.activate_buttons(ui)

            else:
                # Finishing up UI acquisition call
                ui.andor.setshutter(1, 2, 0, 0)
                post.status(ui, '')
                ui.progressbar.setValue(0)
                ui.acquisition_cancelled = False
                post.eventlog(ui, 'Spectral acquisition aborted.')
                ui.buttonSpectralStart.setText('Start Spectral Acquisition')
                toggle.activate_buttons(ui)

        # Starting spectral acquisition thread and connecting to plot and store function
        ui.threadpool.start(spectralthread)
        spectralthread.signals.dataSpectralAcquire.connect(plot_and_store)
        spectralthread.signals.finishedSpectralAcquire.connect(finished_acquisition)

    elif ui.spectralacquiring is True:
        ui.spectralacquiring = False
        spectralthread.stop()
        toggle.activate_buttons(ui)
        post.status(ui, '')
        ui.buttonSpectralStart.setText('Start Spectral Acquisition')
    ##############
