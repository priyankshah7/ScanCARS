# ScanCARS
*Author: Priyank Shah* <br />
*Author email: priyank.shah@kcl.ac.uk* <br />
*Institution: King's College London* <br />
*Description: Hyperspectral image acquisition software*

This interactive GUI-based software is built to acquire hyperspectral
data in a microscope-based experimental setup. It's original 
development is to acquire spectral interferometric polarized coherent 
anti-Stokes Raman spectroscopy (SIPCARS) hyperspectral data.

### Requirements
The two software development kits (SDKs) included are the Andor SDK and 
the ADwin SDK. The Andor SDK controls Andor's range of CCD cameras and its
use is dependent on the installation of the drivers provided by Andor. The Andor
SDK is modified from [here](https://github.com/hamidohadi/pyandor). The
ADwin SDK is used to drive the microscope stage and its use is also
dependent on the installation of the drivers provided by ADwin.

The following python packages are also required:
+ numpy
+ pyqtgraph
+ pyqt5

### Data file type
+ Single-point spectroscopic data: .txt file
+ Hyperspectral data: .txt file

[![Build Status](https://travis-ci.org/priyankshah7/ScanCARS.svg?branch=master)](https://travis-ci.org/priyankshah7/ScanCARS)
[![Test Coverage](https://api.codeclimate.com/v1/badges/033308ac957b0d2608ca/test_coverage)](https://codeclimate.com/github/priyankshah7/ScanCARS/test_coverage)
[![NSP Status](https://nodesecurity.io/orgs/cars/projects/1189321f-476c-4347-b365-3a6e6f8acc86/badge)](https://nodesecurity.io/orgs/cars/projects/1189321f-476c-4347-b365-3a6e6f8acc86)
