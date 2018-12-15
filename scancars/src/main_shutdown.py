import os
import time
import datetime
from PyQt5.QtCore import QCoreApplication
from scancars.utils import toggle, post


def main_shutdown(ui):
    toggle.deactivate_buttons(ui)

    # Saving the event logger contents to a textfile
    now = datetime.datetime.now()
    newpath = 'C:\\Users\\CARS\\Documents\\SIPCARS\\Data\\' + now.strftime('%Y-%m-%d') + '\\'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    with open(newpath + 'eventlog--' + now.strftime('%H-%M-%S') + '.txt', 'w') as eventfile:
        eventfile.write(str(ui.eventLogger.toPlainText()))

    # Ensuring all acquiring and temperature loops have been stopped
    ui.acquiring = False
    ui.gettingtemp = False

    # Turning the shutter off and checking to see if the camera cooler is on
    ui.andor.setshutter(1, 2, 0, 0)
    ui.andor.iscooleron()
    ui.andor.gettemperature()

    # If the cooler is off, proceed to shutdown the camera
    if ui.andor.coolerstatus == 0:  # and ui.andor.temperature > -20: # TODO Temp. whilst aligning
        ui.andor.shutdown()
        # ui.isoplane.close()

        post.eventlog(ui, 'ScanCARS can now be safely closed.')
        post.status(ui, 'ScanCARS can now be safely closed.')

    # If the cooler is on, turn it off, wait for temp. to increase to -20C, and then shutdown camera
    else:
        ui.andor.gettemperature()
        if ui.andor.temperature < -20:
            post.eventlog(ui, 'Andor: Waiting for camera to return to normal temp...')
        ui.andor.cooleroff()
        ui.buttonCameratempCooler.setText('Cooler On')
        time.sleep(1)
        while ui.andor.temperature < -20:
            time.sleep(3)
            ui.andor.gettemperature()
            ui.cameratempActualTemp.setText(str(ui.andor.temperature))
            QCoreApplication.processEvents()

            ui.andor.shutdown()
        # ui.isoplane.close()

        post.eventlog(ui, 'ScanCARS can now be safely closed.')
        post.status(ui, 'ScanCARS can now be safely closed.')
