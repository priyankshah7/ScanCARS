import time
import numpy as np
from PyQt5.QtCore import QCoreApplication

from scancars.utils import post, toggle
from scancars.threads import ccdacquire


def camtracks_update(ui):
    # Reading in the required track position values from the gui
    randtrack = np.array([int(float(ui.camtrackLower1.text())),
                          int(float(ui.camtrackUpper1.text())),
                          int(float(ui.camtrackLower2.text())),
                          int(float(ui.camtrackUpper2.text()))])

    # Setting the random track positions on the camera
    errormessage = ui.andor.setrandomtracks(2, randtrack)

    # Checking to make sure that the camera has successfully set the random tracks
    if errormessage != 'DRV_SUCCESS':
        post.eventlog(ui, 'Andor: SetRandomTracks error. ' + errormessage)

    else:
        post.eventlog(ui, 'Andor: Random track positions updated.')


def camtracks_view(ui):
    # Creating instance of the live ccd chip thread
    ccdacquire_thread = ccdacquire.CcdAcquireThread(ui)

    # If there's no current live ccd view taking place, then start one
    if ui.ccdacquiring is False:
        ui.ccdacquiring = True
        ui.dialog_ccd()
        ui.andor.setshutter(1, 1, 0, 0)
        toggle.deactivate_buttons(ui, cameraoptions_openimage_stat=True)
        post.status(ui, 'Live CCD view...')
        # self.buttonCamtrackView.setText('Stop Live View')

        # Camera parameters for live ccd acquisition
        ui.andor.freeinternalmemory()
        ui.andor.setreadmode(4)
        ui.andor.setacquisitionmode(1)
        ui.andor.setexposuretime(ui.exposuretime)

        time.sleep(1)

        # Starting live ccd acquisition thread and connecting to plot function
        ui.threadpool.start(ccdacquire_thread)
        ccdacquire_thread.signals.dataLiveAcquire.connect(lambda: plot())

        def plot():
            ui.winccdlive.ccdliveWin.setImage(ui.andor.imagearray)
            QCoreApplication.processEvents()

    elif ui.ccdacquiring is True:
        ui.ccdacquiring = False
        ccdacquire_thread.stop()
        toggle.activate_buttons(ui)
        post.status(ui, '')
