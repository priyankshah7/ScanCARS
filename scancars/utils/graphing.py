# Defining plot and image functions for the relevant pyqtgraph wins


def carsplot(self, spectrum):
    self.Main_specwin.clear()
    self.Main_specwin.plot(spectrum)


def carsimage(self, image):
    self.Main_imagewin.clear()
    self.Main_imagewin.setImage(image)
