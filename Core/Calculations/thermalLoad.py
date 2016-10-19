import pandas as pd
import numpy as np
from scipy.linalg import expm, inv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Database import Settings

from Core.Calculations.Functions import air_temp



engine = create_engine('sqlite:///settings.sqlite', echo=True)

Session = sessionmaker(bind=engine)
session = Session()


N = 4000
hour = linspace(0,24,N)

alpha = 0
h_rc = 11.0 #radiation + convection
g_atm = 0.5
def T_sa(i, I):
    global alpha
    #consider dew point here !!!
    #!!!!!!!!!!!!!!!
    T = air_temp(hour[i])-273.15 + alpha*I(i)/h_rc - g_atm*6.5*(air_temp(hour[i]) - (25+273.15))/h_rc

def thermalLoad(fileName):
    global alpha
    for sett in session.query(Settings).filter(Settings.name=='fileName'):
        
        length = sett.length
        width = sett.width
        height = sett.height
        datemonth = sett.date[5:7]
        dateday = sett.date[8:10]


        a1 = width*height
        a2 = length*height
        a3 = width*height
        a4 = length*height
        
        thickness = sett.thickness
        h_c = sett.conv_coeff
        rho = sett.density
        c = sett.spec_heat
        k = sett.therm_cond
        R = thickness/k
        Cc = rho*c*thickness/2
        
        alpha = sett.swAbs
        epsi = sett.lwEWall
        sigma = 5.67*1)**(-8)

    a11 = -1/(R*Cc) - h_rc/(Cc);
    a12 = 1/(R*Cc);
    a21 = 1/(R*Cc);
    a22 = -1/(R*Cc) - h_c/(Cc);

    b11 = h_rc/(Cc);
    b12 = 0;
    b21 = 0;
    b22 = h_c/(Cc);

    c11 = 0;
    c12 = h_c;

    d11 = 0;
    d12 = -h_c;

    A = np.mat('a11 a12; a21 a22')
    B = np.mat('b11 b12; b21 b22')
    C = np.mat('c11 c12')
    D = np.mat('d11 d12')

    I = np.mat('1 0;0 1')
    
    delta = 3600*(24/N)
    
    phi = expm(A*delta)

    gamma1 = inv(A)*(phi-I)*B;
    gamma2 = inv(A)*(gamma1/delta - B);

    R0 = I
    e1 = -np.trace(phi*R0)/1
    R1 = phi*R0 + e1*I 
    e2 = -np.trace(phi*R1)/2

    S0 = C*R0*gamma2 + D;
    S1 = C*(R0*(gamma1-gamma2)+R1*gamma2) + e1*D;
    S2 = C*(R1*(gamma1-gamma2))+ e2*D;

    #call function of air and vapor pressure

    excel = "Core/Data/Radiation/ShortwaveRadiation-"+fileName+".xlsx"
    rad = pd.read_excel(excel, index_col=False)
    I_sn = rad['Northern']
    I_se = rad['Eastern']
    I_ss = rad['Southtern']
    I_sw = rad['Western']

    sol_airn = np.empty(N)
    sol_aire = np.empty(N)
    sol_airs = np.empty(N)
    sol_airw = np.empty(N)

    


        
                



