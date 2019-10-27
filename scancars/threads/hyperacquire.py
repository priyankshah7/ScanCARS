import ctypes
import nidaqmx as daq
from PyQt5 import QtCore


class WorkerSignals(QtCore.QObject):
    dataHyperAcquire = QtCore.pyqtSignal(int, int, int)
    finishedHyperAcquire = QtCore.pyqtSignal()


class HyperAcquireThread(QtCore.QRunnable):
    def __init__(self, ui, x_required, y_required, z_required,
                 xystep_voltage, zstep_voltage,
                 exposuretime, background_frames):
        super(HyperAcquireThread, self).__init__()
        self.signals = WorkerSignals()
        self.ui = ui
        self.cimage = (ctypes.c_long * self.ui.andor.dim)()
        self.x_required = x_required
        self.y_required = y_required
        self.z_required = z_required
        self.xystep_voltage = xystep_voltage
        self.zstep_voltage = zstep_voltage
        self.exposuretime = exposuretime
        self.background_frames = background_frames

        self.mutex = QtCore.QMutex()

    @QtCore.pyqtSlot()
    def stop(self):
        self.mutex.lock()
        self.ui.hyperacquiring = False
        self.ui.acquisition_cancelled = True
        self.mutex.unlock()

    @QtCore.pyqtSlot(int, int, int)
    def run(self):
        # DAQ settings
        xVoltageChannel, yVoltageChannel, zVoltageChannel = daq.Task(), daq.Task(), daq.Task()
        xVoltageChannel.ao_channels.add_ao_voltage_chan('cDAQ1Mod1/ao0')
        yVoltageChannel.ao_channels.add_ao_voltage_chan('cDAQ1Mod1/ao1')
        zVoltageChannel.ao_channels.add_ao_voltage_chan('cDAQ1Mod1/ao2')

        x_voltage = 0#; x_voltage_final = self.xystep_voltage * self.x_required
        y_voltage = 0#; y_voltage_final = self.xystep_voltage * self.y_required
        z_voltage = 0#; z_voltage_final = self.zstep_voltage * self.z_required

        x_position = 0; x_position_final = self.x_required
        y_position = 0; y_position_final = self.y_required
        z_position = 0; z_position_final = self.z_required
        self.ui.hyperacquiring = True
        while z_position < z_position_final:
            zVoltageChannel.write(z_voltage)

            while y_position < y_position_final:
                yVoltageChannel.write(y_voltage)

                while x_position < x_position_final:
                    xVoltageChannel.write(x_voltage)

                    # Do acquisition... ###
                    self.ui.andor.startacquisition()
                    self.ui.andor.waitforacquisition()
                    self.ui.andor.getacquireddata(self.cimage, 1)

                    self.signals.dataHyperAcquire.emit(x_position, y_position, z_position)

                    x_voltage += self.xystep_voltage
                    x_position += 1

                    if not self.ui.hyperacquiring:
                        break

                x_voltage = 0
                x_position = 0
                y_voltage += self.xystep_voltage
                y_position += 1

                if not self.ui.hyperacquiring:
                    break

            y_voltage = 0
            y_position = 0
            z_voltage += self.zstep_voltage
            z_position += 1

            if not self.ui.hyperacquiring:
                break

        else:
            self.ui.andor.setshutter(1, 2, 0, 0)

        # Terminating link with DAQ channels after acquisition
        xVoltageChannel.close()
        yVoltageChannel.close()
        zVoltageChannel.close()

        self.ui.hyperacquiring = False
        self.signals.finishedHyperAcquire.emit()
