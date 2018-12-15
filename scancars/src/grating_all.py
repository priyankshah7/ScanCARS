from scancars.utils import post
from scancars.threads import grating


def grating_update(ui):
    post.eventlog(ui, 'Isoplane: Updating...')
    ui.isoplane.clear()
    grating_no = ui.isoplane.ask('?GRATING')
    grating_no = int(grating_no[1])

    ui.isoplane.clear()
    wavelength_no = ui.isoplane.ask('?NM')
    wavelength_no = round(float(wavelength_no[0:-3]))

    if ui.grating150.isChecked() and grating_no == 2:
        setgrating = grating.GratingThread(ui.isoplane, query='grating', value=3)
        ui.threadpool.start(setgrating)
        message = 'Isoplane: Grating set to 150 lines/mm'
        setgrating.signals.finished.connect(lambda: ui.finished_grating_query(message))

    elif ui.grating600.isChecked() and grating_no == 3:
        setgrating = grating.GratingThread(ui.isoplane, query='grating', value=2)
        ui.threadpool.start(setgrating)
        message = 'Isoplane: Grating set to 600 lines/mm'
        setgrating.signals.finished.connect(lambda: ui.finished_grating_query(message))

    if int(ui.gratingRequiredWavelength.text()) != wavelength_no:
        reqwavelength = int(ui.gratingRequiredWavelength.text())
        setwavelength = grating.GratingThread(ui.isoplane, query='wavelength', value=reqwavelength)
        ui.threadpool.start(setwavelength)
        message = 'Isoplane: Wavelength set to ' + str(reqwavelength) + ' nm'
        setwavelength.signals.finished.connect(lambda: finished_grating_query(ui, message))


def finished_grating_query(ui, message=None):
    ui.isoplane.clear()
    grating_no = ui.isoplane.ask('?GRATING')
    grating_no = int(grating_no[1])

    ui.isoplane.clear()
    wavelength_no = ui.isoplane.ask('?NM')
    wavelength_no = round(float(wavelength_no[0:-3]))

    if ui.grating150.isChecked() and grating_no == 2:
        ui.grating600.setChecked(True)

    elif ui.grating600.isChecked() and grating_no == 3:
        ui.grating150.setChecked(True)

    ui.gratingActualWavelength.setText(str(wavelength_no))

    if message is not None:
        post.eventlog(ui, message)


def grating_state(ui):
    if ui.grating is True:
        ui.isoplane.close()

        post.eventlog(ui, 'Isoplane: Disconnected.')
        ui.buttonGratingState.setText('Turn On')
        ui.buttonGratingState.setStyleSheet('background: #121212')
        ui.buttonGratingUpdate.setDisabled(True)
        ui.grating = False

    elif ui.grating is False:
        ui.initialize_isoplane()
