import h5py, time
import numpy as np
from PyQt5.QtWidgets import QFileDialog
"""
INTERNAL
Note that saving to .h5 will increase the size of the file compared to the custom .cars binary file.
The increase is roughly a factor of x3.6 even with compression (worthwhile sacrifice for now).
"""


def save(data, path, acqproperties, acqtype='spectral'):
    if acqtype == 'spectral':
        # TODO Note that the below assumes that data has the form data[track1+track2, number of acqs]
        track1 = data[0:acqproperties.width-1]
        track2 = data[acqproperties.width:(2*acqproperties.width)-1]

        with h5py.File(path, 'w') as datafile:
            filegroup = datafile.create_group('sipcars')
            # filegroup.create_dataset('track1', data=track1, compression='gzip', compression_opts=9)
            # filegroup.create_dataset('track2', data=track2, compression='gzip', compression_opts=9)

            filegroup.create_dataset('track1', data=track1)
            filegroup.create_dataset('track2', data=track2)

            filegroup.attrs['Acquisition Type'] = 'Spectral'
            filegroup.attrs['Exposure Time'] = acqproperties.time
            filegroup.attrs['Number of Acquisitions'] = acqproperties.number
            filegroup.attrs['Time and Date'] = str(
                time.strftime('%d/%m/%Y') + ':' + time.strftime("%H:%M:%S"))

    elif acqtype == 'hyperspectral':
        track1 = data[0:acqproperties.width - 1, :, :, :]
        track2 = data[acqproperties.width:(2 * acqproperties.width) - 1, :, :, :]

        with h5py.File(path, 'w') as datafile:
            filegroup = datafile.create_group('sipcars')
            filegroup.create_dataset('track1', data=track1, compression='gzip', compression_opts=9)
            filegroup.create_dataset('track2', data=track2, compression='gzip', compression_opts=9)

            filegroup.attrs['Acquisition Type'] = 'Hyperspectral'
            filegroup.attrs['Exposure Time'] = acqproperties.time
            filegroup.attrs['X Pixels'] = acqproperties.xpixels
            filegroup.attrs['Y Pixels'] = acqproperties.ypixels
            filegroup.attrs['Z Pixels'] = acqproperties.zpixels
            filegroup.attrs['Time and Date'] = str(
                time.strftime('%d/%m/%Y') + ':' + time.strftime("%H:%M:%S"))


class EmptyClass:
    def __init__(self):
        pass

