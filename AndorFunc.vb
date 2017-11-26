Imports Microsoft.VisualBasic
Imports ADwin.Driver

Public Class Andor
    Public Function sc_initialise()
        Dim errorValue_Initialize As String = Initialize("")
        Select Case (errorValue_Initialize)
            Case DRV_SUCCESS
                event_logger.AppendText("- Camera initialized." & Environment.NewLine)

                Dim detector_size As Integer = vbGetDetector()
                vbGetHardwareVersion()

                Exit Select

            Case DRV_VXDNOTINSTALLED
                event_logger.AppendText("- Camera initialization unsuccessful. VxD not loaded." & Environment.NewLine)

            Case DRV_INIERROR
                event_logger.AppendText("- Camera initialization unsuccessful. Unable to load 'DETECTOR.INI'." & Environment.NewLine)

            Case DRV_ERROR_ACK
                event_logger.AppendText("- Camera initialization unsuccessful. Unable to communicate with card." & Environment.NewLine)

            Case DRV_ERROR_PAGELOCK
                event_logger.AppendText("- Camera initialization unsuccessful. Unable to acquire lock on requested memory." & Environment.NewLine)

            Case DRV_USBERROR
                event_logger.AppendText("- Camera initialization unsuccessful. Unable to detect USB device or not USB2.0." & Environment.NewLine)

            Case DRV_ERROR_NOCAMERA
                event_logger.AppendText("- Camera initialization unsuccessful. No camera found." & Environment.NewLine)

            Case Else
                event_logger.AppendText("- Camera initialization unsuccessful. Unknown error." & Environment.NewLine)
        End Select
    
    End Function
    
    Function vbGetDetector()
        Dim xpixels As Integer
        Dim ypixels As Integer

        Dim errorValue_GetDetector As String = GetDetector(xpixels, ypixels)
        Select Case (errorValue_GetDetector)
            Case DRV_SUCCESS
                event_logger.AppendText("- Detector size returned." & Environment.NewLine)

                Return {xpixels, ypixels}

            Case DRV_NOT_INITIALIZED
                event_logger.AppendText("- System not initalized (GetDetector)." & Environment.NewLine)
        End Select

    End Function

    Function vbGetHardwareVersion()
        Dim PCB As Integer
        Dim Decode As Integer
        Dim dummy1 As Integer
        Dim dummy2 As Integer
        Dim CameraFirmwareVersion As Integer
        Dim CameraFirmwareBuild As Integer

        Dim errorValue_GetHardwareVersion As String = GetHardwareVersion(PCB, Decode, dummy1, dummy2, CameraFirmwareVersion, CameraFirmwareBuild)
        Select Case (errorValue_GetHardwareVersion)
            Case DRV_SUCCESS
                event_logger.AppendText("- Camera version information returned." & Environment.NewLine)

                Exit Select

            Case DRV_NOT_INITIALIZED
                event_logger.AppendText("- System not initalized (GetHardwareVersion)." & Environment.NewLine)

            Case DRV_ACQUIRING
                event_logger.AppendText("- Acquisition in progress (GetHardwareVersion)." & Environment.NewLine)

            Case DRV_ERROR_ACK
                event_logger.AppendText("- Unable to communicate with card (GetHardwareVersion)." & Environment.NewLine)
        End Select

    End Function
    
    Public Function sc_coolerON()
        Dim errorValue As String = GetTemperatureRange(mintemp, maxtemp)
        If errorValue <> DRV_SUCCESS Then
            Exit Sub
        End If
        
    End Function
    
    Public Function sc_coolerOFF()
    End Function
    
    Public Function sc_spec_acquire()
    End Function
    
    Public Function sc_hsi_acquire()
    End Function
    
    Public Function sc_updatetime_acq()
    End Function
    
    Public Function sc_updatetracks()
    End Function
    
    Public Function sc_displaytracks()
    End Function
    

End Class
