import numpy as np
import xlsxwriter
import datetime
def B(d):
    return ((360.0/365)*(d-81))*np.pi/180

def EOT(b):
    return 9.87*np.sin(2*b) - 7.53*np.cos(b) - 1.5*np.sin(b)

def LST(lt, day):
    return lt + day/60.0

now = datetime.datetime.now()

prefix = str(now.year)+ '-' +str(now.month)+ '-' +str(now.day)

workbook = xlsxwriter.Workbook(prefix+".xlsx")

def saveSunPathXLSX():
    pass 
    