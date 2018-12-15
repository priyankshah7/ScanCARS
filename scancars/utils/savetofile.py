import h5py
import time
import numpy as np

"""
INTERNAL
Note that saving to .h5 will increase the size of the file compared to the custom .cars binary file.
The increase is roughly a factor of x3.6 even with compression (worthwhile sacrifice for now).
"""


def save(data, path, acqproperties, acqtype='spectral'):
    if acqtype == 'spectral':
        raw_data1 = data[0:acqproperties.width-1, :]
        raw_data2 = data[acqproperties.width:(2*acqproperties.width)-1, :]

        # Data to store
        track1_min, track1_max = np.zeros(acqproperties.width), np.zeros(acqproperties.width)
        track2_min, track2_max = np.zeros(acqproperties.width), np.zeros(acqproperties.width)
        track1_std, track2_std = np.zeros(acqproperties.width), np.zeros(acqproperties.width)
        track1 = np.mean(raw_data1, 1)
        track2 = np.mean(raw_data2, 1)
        for spectral_point in range(acqproperties.width-1):
            track1_min[spectral_point] = np.min(raw_data1[spectral_point, :])
            track2_min[spectral_point] = np.min(raw_data2[spectral_point, :])
            track1_max[spectral_point] = np.max(raw_data1[spectral_point, :])
            track2_max[spectral_point] = np.max(raw_data2[spectral_point, :])
            track1_std[spectral_point] = np.std(raw_data1[spectral_point, :])
            track2_std[spectral_point] = np.std(raw_data2[spectral_point, :])

        with h5py.File(path, 'w') as datafile:
            filegroup = datafile.create_group('sipcars')
            # filegroup.create_dataset('track1', data=track1, compression='gzip', compression_opts=9)
            # filegroup.create_dataset('track2', data=track2, compression='gzip', compression_opts=9)

            filegroup.create_dataset('track1', data=track1)
            filegroup.create_dataset('track2', data=track2)
            filegroup.create_dataset('track1_min', data=track1_min)
            filegroup.create_dataset('track1_max', data=track1_max)
            filegroup.create_dataset('track2_min', data=track2_min)
            filegroup.create_dataset('track2_max', data=track2_max)
            filegroup.create_dataset('track1_std', data=track1_std)
            filegroup.create_dataset('track2_std', data=track2_std)

            filegroup.attrs['Acquisition Type'] = 'Spectral'
            filegroup.attrs['Exposure Time'] = acqproperties.time
            filegroup.attrs['Number of Acquisitions'] = acqproperties.number
            filegroup.attrs['Time and Date'] = str(
                time.strftime('%d/%m/%Y') + ':' + time.strftime("%H:%M:%S"))

    elif acqtype == 'hyperspectral':
        track1 = data[:, :, :, 0:acqproperties.width - 1]
        track2 = data[:, :, :, acqproperties.width:(2 * acqproperties.width) - 1]

        with h5py.File(path, 'w') as datafile:
            filegroup = datafile.create_group('sipcars')
            filegroup.create_dataset('track1', data=track1, compression='gzip', compression_opts=9)
            filegroup.create_dataset('track2', data=track2, compression='gzip', compression_opts=9)

            filegroup.attrs['Acquisition Type'] = 'Hyperspectral'
            filegroup.attrs['Exposure Time'] = acqproperties.time
            filegroup.attrs['X Pixels'] = acqproperties.xpixels
            filegroup.attrs['Y Pixels'] = acqproperties.ypixels
            filegroup.attrs['Z Pixels'] = acqproperties.zpixels
            filegroup.attrs['XY Step Size'] = acqproperties.xystep
            filegroup.attrs['Z Step Size'] = acqproperties.zstep
            filegroup.attrs['Time and Date'] = str(
                time.strftime('%d/%m/%Y') + ':' + time.strftime("%H:%M:%S"))


class EmptyClass:
    def __init__(self):
        pass

