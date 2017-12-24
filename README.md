# ScanCARS

*Author: Priyank Shah* <br />
*Author email: priyank.shah@kcl.ac.uk* <br />
*Institution: King's College London* <br />
*Description: Hyperspectral image acquisition software*

### Description
This interactive GUI-based software is built to acquire hyperspectral
data in a microscope-based experimental setup. It's original 
purpose is to acquire spectral interferometric polarized coherent 
anti-Stokes Raman spectroscopy (SIPCARS) hyperspectral data.

Hyperspectral acquisition using ScanCARS requires an Andor scientific camera
and an open-loop configured microscope stage controlled using a NI DAQ card 
(though an ADwin software development kit is also provided). ScanCARS is
currently only configured to work on Windows, however it can easily be modified
to work on Linux/Mac OS if the relevant Andor driver has been purchased.

### Requirements
ScanCARS is Qt based and written in python. An API to the Andor software development
kit written in python is provided *(scancars/sdk/andor)* and, for reference, it 
has been modified from [here](https://github.com/hamidohadi/pyandor). The openly
available **nidaqmx** package developed by NI is not provided but can be acquired 
from [here](https://github.com/ni/nidaqmx-python). 

The following python packages are also required:
+ numpy
+ pyqtgraph
+ PyQt5
+ h5py
+ nidaqmx

### Data output
File are stored in the hierarchical data format (HDF5), a format used to store
multidimensional data.  
+ Single-point spectroscopic data: *.h5 file*
+ Hyperspectral data: *.h5 file*


