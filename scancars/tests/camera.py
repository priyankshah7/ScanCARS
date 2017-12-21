import numpy as np
import ctypes
import matplotlib.pyplot as plt
import pyqtgraph as pg

from scancars.sdk.andor import Cam

andor = Cam()

randtrack = np.array([154, 187, 211, 244])

errorinitialize = andor.initialize()
if errorinitialize != 'DRV_SUCCESS':
    print('Andor: Initialize error. ' + errorinitialize)
andor.getdetector()
andor.setshutter(1, 2, 0, 0)
andor.setreadmode(2)
andor.setrandomtracks(2, randtrack)
andor.setadchannel(1)
andor.settriggermode(0)
andor.sethsspeed(1, 0)
andor.setvsspeed(4)

andor.dim = andor.width * andor.randomtracks

andor.setacquisitionmode(1)
andor.setshutter(1, 1, 0, 0)
andor.setexposuretime(0.1)
andor.startacquisition()
andor.waitforacquisition()
andor.getacquireddata()

track1 = andor.imagearray[0:andor.width-1]
track2 = andor.imagearray[andor.width:(2*andor.width)-1]
trackdiff = track2 - track1

# plt.figure()
# plt.plot(track1)
# plt.plot(track2)
# plt.plot(trackdiff)
# plt.show()


andor.freeinternalmemory()
andor.setshutter(1, 2, 0, 0)