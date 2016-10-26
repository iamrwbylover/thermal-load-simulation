import sys
from Core.Calculations import sunpath
from PyQt5 import uic, QtWidgets
from Core.Database.Database import Settings
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from Core.Calculations import radiation, thermalLoad, fit
engine = create_engine('sqlite:///settings.sqlite', echo = False)
Session = sessionmaker(bind=engine)
session = Session()




items = []

mainWindowUI = "./GUI/thesisgui.ui"
loader = "./GUI/load.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(mainWindowUI)
load, QtBaseClass2 = uic.loadUiType(loader)

i = 0
class Load(QtWidgets.QDialog, load):
	def __init__(self):
		QtWidgets.QDialog.__init__(self)
		load.__init__(self)
		self.setupUi(self)
		self.cb = self.load

		self.cb.activated.connect(self.loadIt)
		self.populate()
		
	def loadIt(self,i):
		fileName = self.cb.currentText()
		msg = QtWidgets.QMessageBox()
		msg.setIcon(QtWidgets.QMessageBox.Question)

		msg.setText("Load dataset {}?".format(fileName))
		msg.setWindowTitle("Load")
		msg.setStandardButtons(QtWidgets.QMessageBox.Ok| QtWidgets.QMessageBox.Cancel)

		retVal = msg.exec_()
		
		if retVal == QtWidgets.QMessageBox.Ok:
			self.close()
			print(fileName)
			thermalLoad.thermalLoad(fileName)		
		else:
			msg.close()
		
	def populate(self):
		global items
		for sett in session.query(Settings).filter():
			if sett.name not in items:
				self.cb.addItem(sett.name)
				items.append(sett.name)

class Main(QtWidgets.QMainWindow, Ui_MainWindow):
	def __init__(self, parent=None):

		QtWidgets.QMainWindow.__init__(self)
		Ui_MainWindow.__init__(self)
		self.setupUi(self)

		#see thesisgui.py for variable names
		self.oneNext.clicked.connect(self.goNextPage)
		self.twoBack.clicked.connect(self.goPreviousPage)
		self.oneNext_2.clicked.connect(self.goNextPage)
		self.twoBack_2.clicked.connect(self.goPreviousPage)



		home = self.Home
		home.triggered.connect(self.Home1)
		
		self.statusBar = QtWidgets.QStatusBar()
		self.setStatusBar(self.statusBar)
		self.save.clicked.connect(self.saveButton)

		self.load = Load()


	def Home1(self):
		self.load.show()
		

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
			radiation.calculateRadiation(fileName)
			self.statusBar.showMessage("Saved.", 2000)
			thermalLoad.thermalLoad(fileName)
			self.load.populate()
		else:

			self.statusBar.showMessage("Cancelled.", 2000)


if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = Main()
	window.show()
	sys.exit(app.exec_())
