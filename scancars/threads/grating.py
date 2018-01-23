import pyvisa

rm = pyvisa.ResourceManager()

spec_device = rm.open_resource('ASRL4::INSTR')
spec_device.baud_rate = 9600
spec_device.timeout = 20

spec_device.read_termination = '\r'
spec_device.write_termination = '\r'


def get_serial(device):
    spec_device.clear()
    serial_no = device.query('SERIAL', delay=3)
    return serial_no


def get_model(device):
    spec_device.clear()
    model_no = device.query('MODEL', delay=3)
    return model_no


def get_turret(device):
    spec_device.clear()
    turret_no = device.query('?TURRET', delay=3)
    return turret_no


def get_grating(device):
    spec_device.clear()
    grating_no = device.query('?GRATING', delay=3)
    grating_no = int(grating_no[1])
    return grating_no


def set_grating(device, grating):
    spec_device.clear()
    device.write(str(grating) + ' GRATING', delay=3)


def get_nm(device):
    spec_device.clear()
    nm_no = device.query('?NM')
    nm_no = float(nm_no[1:8])
    return nm_no


def set_nm(device, nm):
    spec_device.clear()
    device.write(str(nm) + ' NM')
