# ScanCARS

ScanCARS is a hardware-control and data acquisition software program created to acquire 
hyperspectral data. More specifically, the software is used to acquire spectral 
interferometric polarisation coherent anti-Stokes Raman spectroscopy 
([SIPCARS](https://doi.org/10.1002/jrs.5576)) signals.

### Description
This GUI software is built to acquire hyperspectral
data in a microscope-based experimental setup. It's original 
purpose is to acquire spectral interferometric polarized coherent 
anti-Stokes Raman spectroscopy (SIPCARS) hyperspectral data.

Hyperspectral acquisition using ScanCARS requires an Andor scientific camera, an 
open-loop configured microscope stage controlled using a NI DAQ card and a Princeton
Instruments Isoplane spectrometer.

### Platform and instrument models 
ScanCARS is only configured to work with Windows, though the code can be modified
to work with linux/macOS provided that the relevant Andor driver has been purchased.
The software has been tested with the following instrument models:
+ Andor iXon 897 and Andor Newton DU920P <br />
Controlled using a custom python API to the Andor SDK <br />

+ Princeton Instruments Isoplane SCT-320 <br />
Controlled by treating the USB connection as a COM port

### Requirements
ScanCARS is Qt based and written in python. An API to the Andor software development
kit written in python is provided *(scancars/sdk/andor)* and, for reference, it 
has been modified from [here](https://github.com/hamidohadi/pyandor). The openly
available **nidaqmx** package developed by NI is not provided but can be acquired 
from [here](https://github.com/ni/nidaqmx-python). 

The following python packages are required:
+ numpy
+ pyqtgraph
+ PyQt5
+ h5py
+ pyvisa
+ nidaqmx

### Data output
File are stored in the hierarchical data format (HDF5), a format used to store
multidimensional data.  
+ Spectral data: *.h5 file*
+ Hyperspectral data: *.h5 file*

### Screenshot
![Screenshot](/scancars/resources/screenshot.png?raw=true)


