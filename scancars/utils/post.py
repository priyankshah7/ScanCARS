# Defining status and eventlog functions
import time


def status(self, message):
    self.Main_status.setText(message)


def eventlog(self, message):
    self.EventLogger_box.appendPlainText('(' + time.strftime("%H:%M:%S") + ')' + ' - ' + message)


def event_date(self):
    self.EventLogger_box.appendPlainText(
        '------------------------------------------------------------------------------------')
    self.EventLogger_box.appendPlainText(
        ' ScanCARS Software                                    Date: ' + time.strftime('%d/%m/%Y'))
    self.EventLogger_box.appendPlainText(
        '------------------------------------------------------------------------------------')
