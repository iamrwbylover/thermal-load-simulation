import pandas as pd
import numpy as np



def B(d):
    return ((360.0/365)*(d-81))*np.pi/180

def EOT(b):
    return 9.87*np.sin(2*b) - 7.53*np.cos(b) - 1.5*np.sin(b)

def LST(lt, dummy):
    return lt + dummy/60.0

#function to assign values 
def assignValues(fileName):
    N = 4000;
    delta = 8;
    LSTM = 15*delta;
    phi = np.pi/2
    yearDays = 365


    file = pd.ExcelFile(fileName)
    parseDate = file.parse("date settings")
    parseLoc = file.parse("location settings")
    Date = parseDate.to_dict()
    Loc = parseLoc.to_dict()
    alt = Loc['Value'][0]
    lat = Loc['Value'][1]*np.pi/180
    longi = Loc['Value'][2]
    month = int(Date['Value'][0][5:7])
    day =  int(Date['Value'][0][9:11])
    
    leap = 28
    if float(Date['Value'][0][0:4])/4 == 0:
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


#----functions for sunpath calculation
    # def B(d):
    #     return ((360.0/365)*(d-81))*np.pi/180

    # def EOT(b):
    #     return 9.87*np.sin(2*b) - 7.53*np.cos(b) - 1.5*np.sin(b)

    # def LST(lt):
    #     return lt + dummy/60.0
    
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
    file = "SunPath"+fileName
    writer = pd.ExcelWriter(file, engine='xlsxwriter')
    df = pd.DataFrame({'Elevation Angles':elev,
                        'Azimuthal Angles':azi})
    df.to_excel(writer, sheet_name='Sun Path Angles')
    writer.save()
    writer.close()
    print("It got here")