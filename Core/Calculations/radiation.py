from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Core.Database.Database import Settings
import Core.Calculations.Functions as fxn
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt


engine = create_engine('sqlite:///settings.sqlite', echo=False)

Session = sessionmaker(bind=engine)
session = Session()
N = 4000


hr = np.linspace(0,24,N)
I_cloud = np.zeros(N)
I_latm = np.empty(N)
I_lterr = np.empty(N)
I_lrefl = np.empty(N)
I_ltotal = np.empty(N)
I_l = np.empty(N)
airtemp = np.empty(N)
hr = np.linspace(0,24,N)
C = 0.0 #cloud cover
sigma = 5.67*10**(-8)
T = np.empty(N)

phi = np.pi/2
g_atm = (np.cos(phi/2))**2
g_terr = 1-g_atm

#temporary constants
A = 1104.0
c = .121
C_n = 0.8

#SW
I_dni = np.empty(N)
I_diff = np.empty(N)
I_dir = np.empty(N)
I_sdirh = np.empty(N)
I_srefl =np.empty(N)
I_s = np.empty(N)


#theta placeholder
I_1 = np.empty(N)
I_2 = np.empty(N)
I_3 = np.empty(N)
I_4 = np.empty(N)

azi = np.empty(N)
elev = np.empty(N)
epsi_soil = 0
rhol_soil = 0
rhos_soil = 0
theta = 0



def calculateRadiation(fileName):
    global epsi_soil, rhol_soil, rhos_soil, azi, elev, I_dni,I_diff
    excelFile = "./Data/SunPath/SunPath-"+fileName+'.xlsx'
    excel = pd.ExcelFile(excelFile)
    sheet = excel.parse(0)
    azi = sheet.iloc[:,0].real
    elev = sheet.iloc[:,1].real
    

    for sett in session.query(Settings).filter(Settings.name==fileName):
        epsi_soil = sett.lwE
        rhol_soil = sett.lwRC
        rhos_soil = sett.swRC
        theta = sett.direction*np.pi/180

    #long wave radiation
    # for i in range(N):
    #     T[i] = fxn.air_temp(hr[i])
    #     I_latm[i] = C*I_cloud[i] + (1-C)*sigma*(T[i]**4)*(0.79 - 
    #     0.174*10**(-0.041*fxn.vapor_pressure(T[i])))
    #     I_lterr[i] = sigma*T[i]**4
    #     I_lrefl[i] = rhol_soil*I_latm[i]
    #     I_l[i] = g_atm*I_latm[i] + g_terr*(I_lterr[i] + I_lrefl[i])    

    #direct normal irradiance plus diffused
    for i in range(N):
        if elev[i] < 0:
            I_dni[i] = 0
        else:
            angle = np.pi/2 - elev[i]
            am = fxn.airmass(angle)
            I_dni[i] = A*0.7**(am**0.678)
        I_diff[i] = c*I_dni[i]

    I_1 = np.empty(N)
    I_2 = np.empty(N)
    I_3 = np.empty(N)
    I_4 = np.empty(N)

    for i in range(N):
        I_1[i] = calculateSW(i, theta-np.pi/2)
        I_2[i] = calculateSW(i, theta)
        I_3[i] = calculateSW(i, theta+np.pi/2)
        I_4[i] = calculateSW(i, theta+np.pi)

    saveRadiation(fileName,I_1,I_2,I_3,I_4)

def calculateSW(i, angle):
    #short wave radiation
    global rhos_soil, elev, azi,I_dni, I_diff
    I_dir[i] = I_dni[i]*np.cos(elev[i])*np.cos(angle-azi[i])
    
    if elev[i] < 0:
        I_s[i] = 0
    elif I_dir[i] <0:
        I_dir[i] = 0
        I_sdirh[i] = I_dni[i]*np.sin(elev[i]) + I_diff[i]
        I_srefl[i] = rhos_soil*(I_sdirh[i] + I_diff[i])
        I_s[i] = I_dir[i] + g_atm*I_diff[i] + g_terr*I_srefl[i]
    else:
        I_sdirh[i] = I_dni[i]*np.sin(elev[i]) + I_diff[i]
        I_srefl[i] = rhos_soil*(I_sdirh[i] + I_diff[i])
        I_s[i]= I_dir[i] + g_atm*I_diff[i] + g_terr*I_srefl[i]
    return I_s[i]

    


def saveRadiation(fileName,I_1,I_2,I_3,I_4):
    file = "./Data/Radiation/ShortwaveRadiation-"+fileName+'.xlsx'
    writer = pd.ExcelWriter(file, engine='xlsxwriter')
    df = pd.DataFrame({'Northern':I_1,
                        'Eastern':I_2,
                        'Western':I_3,
                        'Southern':I_4,})
    df.to_excel(writer, sheet_name = 'SWRadiation')
    # plt.plot(I_1)
    # plt.plot(I_2)
    # plt.plot(I_3)
    # plt.plot(I_4)
    # plt.show()
    print("Shortwaved Radiation saved as excel file.")
    writer.save()
    writer.close()
    

