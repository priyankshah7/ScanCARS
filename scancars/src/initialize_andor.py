import time
import numpy as np

from scancars.utils import toggle, post
from scancars.threads import monitortemp


def initialize_andor(ui):
    toggle.deactivate_buttons(ui)

    # Storing the positions of the random tracks in an array
    randtrack = np.array([int(ui.camtrackLower1.text()),
                          int(ui.camtrackUpper1.text()),
                          int(ui.camtrackLower2.text()),
                          int(ui.camtrackUpper2.text())])

    errorinitialize = ui.andor.initialize()  # Initializing the detector
    if errorinitialize != 'DRV_SUCCESS':
        post.eventlog(ui, 'Andor: Initialize error. ' + errorinitialize)
        return
    ui.andor.getdetector()  # Getting information from the detector
    ui.andor.setshutter(1, 2, 0, 0)  # Ensuring the shutter is closed
    ui.andor.setreadmode(2)  # Setting the read mode to Random Tracks
    ui.andor.setrandomtracks(2, randtrack)  # Setting the position of the random tracks
    ui.andor.setadchannel(1)  # Setting the AD channel
    ui.andor.settriggermode(0)  # Setting the trigger mode to 'internal'
    ui.andor.sethsspeed(0, 0)  # Setting the horiz. shift speed
    ui.andor.setvsspeed(0)  # Setting the verti. shift speed

    ui.exposuretime = float(ui.spectralRequiredTime.text())
    ui.andor.setexposuretime(ui.exposuretime)

    time.sleep(2)

    ui.andor.dim = ui.andor.width * ui.andor.randomtracks

    ui.andor.getacquisitiontimings()
    ui.spectralActualTime.setText(str(round(ui.andor.exposure, 3)))

    toggle.activate_buttons(ui)
    post.eventlog(ui, 'Andor: Successfully initialized.')

    # Starting the temperature thread to monitor the temperature of the camera
    ui.gettingtemp = True
    gettemperature = monitortemp.MonitorTemperatureThread(ui)
    ui.threadpool.start(gettemperature)
