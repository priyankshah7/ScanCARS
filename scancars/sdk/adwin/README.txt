========
ADwin.py
========
This is the python wrapper module for the ADwin API to communicate with ADwin-systems.
--------------------------------------------------------------------------------------

:Version: 0.16.0
:Date: November 2017
:Organisation: Jäger Computergesteuerte Messtechnik GmbH


Requirements, downloadable at www.adwin.de:

*    Linux / Mac: libadwin.so
*    Windows: adwin32.dll / adwin64.dll


**Changelog**

Version 0.16.0
    * Changed license to Apache V2
    * CODING cp1252 added in example*.py

Version 0.15
    * bugfixes
    * new functions: Set_FPar_Double, Get_FPar_Double, Get_FPar_Block_Double, Get_FPar_All_Double,
      SetData_Double, GetData_Double, SetFifo_Double, GetFifo_Double,
      Data_Type, Data2File, File2Data
    * renamed Get_Last_Error_Text() to Get_Error_Text()
    * changed returnvalue from Processor_Type to str (1010 -> "T10")
    * div pep8-style changes
    * several improvements
    * winreg-key
    * examples reworked

Version 0.14
    * bugfix GetData_String()

Version 0.13
    * new function: GD_Transsize

Version 0.12
    * bugfixes

Version 0.11
    * bugfixes

Version 0.10
    * bas_demo7: float() instead of QString.toDouble()
    * examples: c_int32 instead of c_long
    * new functions: Clear_Data(), Retry_Counter()

Version 0.9
    * adwin32.dll / adwin64.dll depending on the python-version
    * bas_demos: str() instead of QtCore.QString.number()
    * bas_dmo3: bugfix div/0

Version 0.8
    * ctypes.c_int32 instead of ctypes.c_long

Version 0.7
    * bugfix Windows-registry
    * python3-support for Windows

Version 0.6
    * bugfix GetData_String()

Version 0.5
    * removed Get- and Set_Globaldelay()
    * bugfixes Fifo_Count() and Fifo_Empty()

Version 0.4
    * new class-attribute ADwindir
    * bas_demos (1, 2, 3, 7) created
    * indenting fixed

Version 0.3
    * one file for booth python-versions (2/3)
    * no exception if Test_Version() fails

Version 0.2
    * usage of the module ctypes
    * class ADwin
    * python3-support for linux

Version 0.1
    * first issue
