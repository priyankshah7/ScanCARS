import pyvisa
from scancars.utils import post


def initialize_isoplane(ui):
    rm = pyvisa.ResourceManager()
    try:
        # 'ASRL4::INSTR' is the port which the Isoplane is connected to. Change as required.
        ui.isoplane = rm.open_resource('ASRL4::INSTR')
        ui.isoplane.timeout = 300000
        ui.isoplane.baud_rate = 9600

        ui.isoplane.read_termination = ' ok\r\n'
        ui.isoplane.write_termination = '\r'

        ui.finished_grating_query()

        post.eventlog(ui, 'Isoplane: Connected.')
        ui.buttonGratingState.setText('Turn Off')
        ui.buttonGratingState.setStyleSheet('background: #121212')
        ui.grating = True

    except pyvisa.errors.VisaIOError as error:
        ui.buttonGratingUpdate.setDisabled(True)
        ui.buttonGratingState.setDisabled(True)
        ui.grating = False
        post.eventlog(ui, 'Isoplane: Could not connect. Possibly being used in another process.')
        print(error)
