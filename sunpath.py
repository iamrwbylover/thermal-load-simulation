import pandas as pd
import numpy as np


N = 4000;
delta = 8;
LSTM = 15*delta;
phi = np.pi/2

alt = 0;
lat = 0;
longi = 0;
numDay = 1;



#function to assign values 
def assignValues(fileName):
    file = pd.ExcelFile(fileName)
    parseDate = file.parse("date settings")
    parseLoc = file.parse("location settings")
    Date = parseDate.to_dict()
    Loc = parseLoc.to_dict()
    alt = Loc['Value'][0]
    lat = Loc['Value'][1]
    longi = Loc['Value'][2]
    month = int(Date['Value'][0][5:7])
    day =  int(Date['Value'][0][9:11])
    if month == 1:
        numDay = day
    elif month ==2:
        numDay = day + 31
    elif month ==3:
        numDay = day + 31 + 28
    elif month ==4:
        numDay = day + 31 + 28 + 31
    elif month ==5:
        numDay = day + 31 + 28 + 31 + 30
    elif month ==6:
        numDay = day + 31 + 28 + 31 + 30 + 31
    elif month ==7:
        numDay = day + 31 + 28 + 31 + 30 + 31 + 30
    elif month ==8:
        numDay = day + 31 + 28 + 31 + 30 + 31 + 30 + 31
    elif month ==9:
        numDay = day + 31 + 28 + 31 + 30 + 31 + 30 + 31 + 31
    elif month ==10:
        numDay = day + 31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30
    elif month ==11:
        numDay = day + 31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31
    elif month ==12:
        numDay = day + 31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30



#----functions for sunpath calculation
def B(d):
    return ((360.0/365)*(d-81))*np.pi/180

def EOT(b):
    return 9.87*np.sin(2*b) - 7.53*np.cos(b) - 1.5*np.sin(b)

def LST(lt):
    return lt + day/60.0