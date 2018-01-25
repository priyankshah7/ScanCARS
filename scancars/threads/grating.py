"""
Functions to control the isoplane. The instance of the isoplane must be passed through when calling
any of the functions below.
"""


def get_serial(device):
    device.clear()
    serial_no = device.query('SERIAL', delay=3)
    return serial_no


def get_model(device):
    device.clear()
    model_no = device.query('MODEL', delay=3)
    return model_no


def get_turret(device):
    device.clear()
    turret_no = device.query('?TURRET', delay=3)
    return turret_no


def get_grating(device):
    device.clear()
    grating_no = device.query('?GRATING', delay=3)
    grating_no = int(grating_no[1])
    return grating_no


def set_grating(device, grating):
    device.clear()
    device.write(str(grating) + ' GRATING', delay=3)


def get_nm(device):
    device.clear()
    nm_no = device.query('?NM')
    nm_no = float(nm_no[1:8])
    return nm_no


def set_nm(device, nm):
    device.clear()
    device.write(str(nm) + ' NM')
