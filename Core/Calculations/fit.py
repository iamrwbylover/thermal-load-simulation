import pandas as pd 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Core.Database.Database import Settings
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
engine = create_engine('sqlite:///settings.sqlite', echo=False)

Session = sessionmaker(bind=engine)
session = Session()



path = '/home/bisgetti/Documents/Thesisit/Data/MeanTemps/Dewpoint/'

def fit(fileName):
	for sett in session.query(Settings).filter(Settings.name==fileName):
		month = int(sett.date[5:7])
		day = int(sett.date[8:10])
	
	db = []
	dp = []

	for i in range(5):
		d = day + i
		filename = str(month)+'-'+str(d)
		start = pd.read_csv(path+filename+'.csv')
		drybulb = start['TemperatureC']
		dewpoint = start['Dew PointC']
		db.append(drybulb)
		dp.append(dewpoint)

	curveDB = np.array(pd.concat(db))
	curveDP = np.array(pd.concat(dp))

	x = np.linspace(0,120,120)


	drybulb = interpolate.interp1d(x, curveDB)
	dewpoint = interpolate.interp1d(x,curveDP)
	
	
	return drybulb, dewpoint
	

	