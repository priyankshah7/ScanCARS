# Defining status and eventlog functions
import time


def status(self, message):
    self.mainStatus.setText(message)


def eventlog(self, message):
    self.eventLogger.appendPlainText('(' + time.strftime("%H:%M:%S") + ')' + ' - ' + message)
    self.eventLogger.ensureCursorVisible()
