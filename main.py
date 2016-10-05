import sys
from PyQt5 import QtCore, QtGui, uic, QtWidgets
import save
import sunpath


mainWindowUI = "thesisgui.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(mainWindowUI)


i = 0
class First(QtWidgets.QMainWindow, Ui_MainWindow):
	def __init__(self):

		QtWidgets.QMainWindow.__init__(self)
		Ui_MainWindow.__init__(self)
		self.setupUi(self)

		#see thesisgui.py for variable names
		self.oneNext.clicked.connect(self.goNextPage)
		self.twoBack.clicked.connect(self.goPreviousPage)
		self.oneNext_2.clicked.connect(self.goNextPage)
		self.twoBack_2.clicked.connect(self.goPreviousPage)

		
		self.statusBar = QtWidgets.QStatusBar()
		self.setStatusBar(self.statusBar)
		self.save.clicked.connect(self.saveButton)

		



	def goNextPage(self):
		global i
		i = i+1
		self.stackedWidget.setCurrentIndex(i)
	def goPreviousPage(self):
		global i
		i = i-1
		self.stackedWidget.setCurrentIndex(i)
	def saveButton(self):
		msg = QtWidgets.QMessageBox()
		msg.setIcon(QtWidgets.QMessageBox.Question)

		msg.setText("Are you sure you want to save changes?")
		msg.setWindowTitle("Save")
		msg.setStandardButtons(QtWidgets.QMessageBox.Ok| QtWidgets.QMessageBox.Cancel)

		retVal = msg.exec_()
		
		if retVal == QtWidgets.QMessageBox.Ok:
			self.statusBar.showMessage("Saving...", 2000)
			#data list
			self.locationSett = {'latitude':self.latitudeBox.value(), 'longitude':self.longitudeBox.value(),
							'altitude':self.altitudeBox.value()}
			self.dateSett = {'date':str(self.dateEdit.date().toPyDate())}
			self.envSett = {'swCoeff':self.swReflBox.value(), 'lwCoeff':self.lwReflBox.value(),
						'lwEmiss':self.lwEmissBox.value()}
			self.thermalSett = {'thickness':self.thicknessBox.value(), 'specific heat':self.spec_heatBox.value(), 'thermal conductance':self.thermal_conBox.value(),
							'convective coefficient':self.conv_coeffBox.value(), 'density':self.densityBox.value()}
			self.radConSett = {'shortwave absorptivity':self.short_absBox.value(), 'long wave emissivity':self.long_emissBox.value()}
			self.dimensionSett = {'length':self.lengthBox.value(), 'width':self.widthBox.value(), 'height':self.heightBox.value(),
								'direction':self.normVectorBox.value()}
			self.tempSett = {'initial temperature':self.initialTempBox.value(), 'comfortable temperature':self.comfTempBox.value()}


			self.dataset = {'location settings':self.locationSett, 'date settings':self.dateSett, 'environmental settings':self.envSett,
						'thermal properties':self.thermalSett, 'radiation constants':self.radConSett, 'dimension settings':self.dimensionSett,
						'temperature settings':self.tempSett}
			
			save.Save(self.dataset)
			self.statusBar.showMessage("Saved.", 2000)
		else:
			self.close()
			self.statusBar.showMessage("Cancelled.", 2000)




if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = First()
	window.show()
	sys.exit(app.exec_())