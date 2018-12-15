from scancars.utils import post


def cameratemp_cooler(ui):
    # Checking to see if the cooler is on or off
    message_iscooleron = ui.andor.iscooleron()
    if message_iscooleron != 'DRV_SUCCESS':
        post.eventlog(ui, 'Andor: IsCoolerOn error. ' + message_iscooleron)

    else:
        if ui.andor.coolerstatus == 0:
            # Turning the cooler on and checking to see if it has been turned on
            ui.andor.settemperature(int(ui.cameratempRequiredTemp.text()))
            ui.andor.cooleron()
            ui.andor.iscooleron()
            if ui.andor.coolerstatus == 1:
                post.eventlog(ui, 'Andor: Cooler on.')
                ui.cameratempActualTemp.setStyleSheet('background: #4e644e')
                ui.buttonCameratempCooler.setText('Cooler Off')

        elif ui.andor.coolerstatus == 1:
            # Turning the cooler off and checking to see if it has been turned off
            ui.andor.cooleroff()
            ui.andor.iscooleron()
            if ui.andor.coolerstatus == 0:
                post.eventlog(ui, 'Andor: Cooler off.')
                ui.cameratempActualTemp.setStyleSheet('background: #121212')
                ui.buttonCameratempCooler.setText('Cooler On')

        else:
            # Shouldn't expect this to be called, if it is then it's unlikely to be related to the Andor
            post.eventlog(ui, 'An error has occured. Possibly related to the GUI itself?')
