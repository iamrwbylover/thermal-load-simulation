import os
import pandas as pd 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Core.Database.Database import Settings
import numpy as np
from scipy import interpolate
import calendar 

cal = calendar.Calendar()



engine = create_engine('sqlite:///settings.sqlite', echo=False)

Session = sessionmaker(bind=engine)
session = Session()

noOfDays = 30
N = noOfDays*500

path = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','Data/Conditions/'))

def fit(fileName):
    global noOfDays
    for sett in session.query(Settings).filter(Settings.name==fileName):
        year = int(sett.date[:4])
        month = int(sett.date[5:7])
        day = int(sett.date[8:10])   
        noOfDays = int(sett.numDays)

    db = []
    dp = []
    rh = []
    cc = []
    dd = 0
    month2 = 0
    days = []

    count = 0
    nextmonth = 0

    while count < noOfDays:
        for day in cal.itermonthdays(year, month+nextmonth):
            if day != 0:
                filename = str(month+nextmonth)+'-'+str(day)
                start = pd.read_csv(path+'/'+filename+'.csv')
                drybulb = start['TemperatureC']
                dewpoint = start['Dew PointC']
                relHum = start['Humidity']
                cloudCover = start['Conditions']
                db.append(drybulb)
                dp.append(dewpoint)
                rh.append(relHum)
                cc.append(cloudCover)
                days.append([month+nextmonth,day])
                count += 1
                if count == noOfDays:
                    break
        nextmonth += 1



    # for i in range(noOfDays):
    #     try:
    #         d = day + i
    #         filename = str(month)+'-'+str(d)
    #         start = pd.read_csv(path+'/'+filename+'.csv')
    #         drybulb = start['TemperatureC']
    #         dewpoint = start['Dew PointC']
    #         relHum = start['Humidity']
    #         cloudCover = start['Conditions']
    #         db.append(drybulb)
    #         dp.append(dewpoint)
    #         rh.append(relHum)
    #         cc.append(cloudCover)
    #         days.append([month,d])
    #     except:
    #         dd += 1
    #         month2 = month + 1
    #         if month2 == 2 and dd == 30:
    #             month = month + 1
    #             dd = 1
    #         if month2 == 13:
    #             month2 = 1
    #         filename = str(month2)+'-'+str(dd)
    #         start = pd.read_csv(path+'/'+filename+'.csv')
    #         drybulb = start['TemperatureC']
    #         dewpoint = start['Dew PointC']
    #         relHum = start['Humidity']
    #         cloudCover = start['Conditions']
    #         db.append(drybulb)
    #         dp.append(dewpoint)
    #         rh.append(relHum)
    #         cc.append(cloudCover)
    #         days.append([month2,dd])

    curveDB = np.array(pd.concat(db))
    curveDP = np.array(pd.concat(dp))
    curveRH = np.array(pd.concat(rh))
    curveCC = np.array(pd.concat(cc))

    x = np.linspace(0,24*noOfDays,24*noOfDays)


    drybulb = interpolate.interp1d(x, curveDB+273.15)
    dewpoint = interpolate.interp1d(x,curveDP+273.15)
    relHum = interpolate.interp1d(x,curveRH/100)
    cloudCover = interpolate.interp1d(x,curveCC)
    

    return drybulb, dewpoint, relHum, cloudCover, days
	