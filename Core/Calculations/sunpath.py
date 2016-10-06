# import matplotlib
# matplotlib.use('Qt5Agg')
import pandas as pd
import numpy as np
from matplotlib.pyplot import plot, show, legend
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from  ..Database.Database import Settings


engine = create_engine('sqlite:///settings.sqlite', echo=True)

Session = sessionmaker(bind=engine)
session = Session()


def B(d):
    return ((360.0/365)*(d-81))*np.pi/180

def EOT(b):
    return 9.87*np.sin(2*b) - 7.53*np.cos(b) - 1.5*np.sin(b)

def LST(lt, dummy):
    return lt + dummy/60.0

#function to assign values 
def calculateSunPath(fileName):
    N = 4000
    delta = 8
    LSTM = 15*delta
    phi = np.pi/2
    yearDays = 365


    for query in session.query(Settings).filter(Settings.name==fileName):
        alt = query.altitude
        lat = query.latitude*np.pi/180
        longi = query.longitude
        year = int(query.date[0:4])
        month = int(query.date[5:7])
        day = int(query.date[9:11])
        print(day,month,year)
    
    leap = 28
    if year/4.0 == 0:
        yearDays = 366
        leap = 29

    if month == 1:
        numDay = day
    elif month ==2:
        numDay = day + 31
    elif month ==3:
        numDay = day + 31 + leap
    elif month ==4:
        numDay = day + 31 + leap + 31
    elif month ==5:
        numDay = day + 31 + leap + 31 + 30
    elif month ==6:
        numDay = day + 31 + leap + 31 + 30 + 31
    elif month ==7:
        numDay = day + 31 + leap + 31 + 30 + 31 + 30
    elif month ==8:
        numDay = day + 31 + leap + 31 + 30 + 31 + 30 + 31
    elif month ==9:
        numDay = day + 31 + leap + 31 + 30 + 31 + 30 + 31 + 31
    elif month ==10:
        numDay = day + 31 + leap + 31 + 30 + 31 + 30 + 31 + 31 + 30
    elif month ==11:
        numDay = day + 31 + leap + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31
    elif month ==12:
        numDay = day + 31 + leap + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30
    
    EoT = np.zeros(yearDays)
    TC = np.zeros(yearDays)
    HRA = np.zeros(N)
    hr = np.linspace(0,24,N)

    for i in range(yearDays):
        EoT[i] = EOT(B(i));
        TC[i] = 4*(longi-LSTM) + EoT[i]
    for i in range(N):
        HRA[i] = (15*(LST(hr[i], TC[numDay])-12))*np.pi/180


    delta = (23.45*np.sin((((360.0/yearDays)*(numDay-81))*np.pi/180)))*np.pi/180

    elev = np.zeros(N)
    azi = np.zeros(N)

    for i in range(N):
        elev[i] = np.arcsin(np.sin(delta)*np.sin(lat)
                + np.cos(delta)*np.cos(lat)*np.cos(HRA[i])) 
        azi[i] = np.arccos((np.sin(delta)*np.cos(lat)
            -np.cos(delta)*np.sin(lat)*np.cos(HRA[i]))
            /np.cos(elev[i]))
    
    maxAd = np.where(elev == max(elev))
    for i in np.linspace(maxAd[0][0],N-1,N-(maxAd[0][0])):
        azi[int(i)] = -azi[int(i)]
    file = "./Data/SunPath/SunPath-"+fileName+'.xlsx'
    writer = pd.ExcelWriter(file, engine='xlsxwriter')
    df = pd.DataFrame({'Elevation Angles':elev,
                        'Azimuthal Angles':azi})
    df.to_excel(writer, sheet_name='Sun Path Angles')
    writer.save()
    writer.close()
    plot(azi*180/np.pi,label='azi')
    plot(elev*180/np.pi,label='elev')
    legend(loc = 'best')
    show()
    print("It got here")


#calculateSunPath('sam')
