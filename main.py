import sys
import sunpath
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from Database import Settings
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
engine = create_engine('sqlite:///settings.sqlite', echo = True)
Session = sessionmaker(bind=engine)
session = Session()




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
			fileName = self.datasetName.text()
			entry = Settings(name = fileName,
							latitude = self.latitudeBox.value(),
							longitude = self.longitudeBox.value(),
							altitude = self.altitudeBox.value(),
							date = str(self.dateEdit.date().toPyDate()),
							swRC = self.swReflBox.value(),
							lwRC = self.lwReflBox.value(),
							lwE = self.lwEmissBox.value(),
							thickness = self.thicknessBox.value(),
							spec_heat = self.spec_heatBox.value(),
							therm_cond = self.thermal_conBox.value(),
							conv_coeff = self.conv_coeffBox.value(),
							density = self.densityBox.value(),
							swAbs = self.short_absBox.value(),
							lwEWall = self.long_emissBox.value(),
							length = self.lengthBox.value(),
							width = self.widthBox.value(),
							height = self.heightBox.value(),
							direction = self.normVectorBox.value(),
							initTemp = self.initialTempBox.value(),
							comfTemp = self.comfTempBox.value()
							)
			
			
			session.add(entry)
			session.commit()
			sunpath.calculateSunPath(fileName)
			self.statusBar.showMessage("Saved.", 2000)
		else:
			self.close()
			self.statusBar.showMessage("Cancelled.", 2000)




if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = First()
	window.show()
	sys.exit(app.exec_())