import pandas as pd
import numpy as np
from matplotlib.pyplot import plot, show, figure
from scipy.linalg import expm, inv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Core.Database.Database import Settings

from Core.Calculations.Functions import air_temp



engine = create_engine('sqlite:///settings.sqlite', echo=False)

Session = sessionmaker(bind=engine)
session = Session()

noOfDays = 5


N = noOfDays*1000
hour = np.linspace(0,noOfDays*24,N)

h_rc = 11.0 #radiation + convection
g_atm = 0.5
def T_sa(i, I):
    global h_rc
    #consider dew point here !!!
    #!!!!!!!!!!!!!!!
    
    T = air_temp(hour[i])-273.15 + alpha*I[i]/h_rc - g_atm*6.5*(air_temp(hour[i]) - (25+273.15))/h_rc
    return T

def thermalLoad(fileName):
    global alpha, N
    for sett in session.query(Settings).filter(Settings.name==fileName):

        length = sett.length
        width = sett.width
        height = sett.height
        # datemonth = sett.date[5:7]
        # dateday = sett.date[8:10]


        #material properties
        thickness = sett.thickness
        h_c = sett.conv_coeff
        rho = sett.density
        c = sett.spec_heat
        k = sett.therm_cond
        
        Ti = sett.initTemp
        Tcomf = sett.comfTemp
            
        alpha = sett.swAbs
        epsi = sett.lwEWall
        sigma = 5.67*(10)**(-8)
    
    R = thickness/k
    Cc = rho*c*thickness/2
    #call function of air and vapor pressure

    excel = "Data/Radiation/ShortwaveRadiation-"+fileName+".xlsx"
    rad = pd.read_excel(excel)
    I_sn = rad['Northern']
    I_se = rad['Eastern']
    I_ss = rad['Southern']
    I_sw = rad['Western']

    

    sol_airn = np.empty(N)
    sol_aire = np.empty(N)
    sol_airs = np.empty(N)
    sol_airw = np.empty(N)

    
    at = np.empty(N)

    for i in range(N):
        sol_airn[i] = T_sa(i, I_sn)
        sol_aire[i] = T_sa(i, I_se)
        sol_airs[i] = T_sa(i, I_ss)
        sol_airw[i] = T_sa(i, I_sw)
        at[i] = air_temp(hour[i])

    #heat
    Qn = np.empty(N)
    Qe = np.empty(N)
    Qs = np.empty(N)
    Qw = np.empty(N)

    Qt = np.empty(N) # total heat

    T1n = np.empty(N)
    T2n = np.empty(N)
    T1e = np.empty(N)
    T2e = np.empty(N)
    T1s = np.empty(N)
    T2s = np.empty(N)
    T1w = np.empty(N)
    T2w = np.empty(N)

    T1n[0] = 273.15 + Ti
    T2n[0] = 273.15 + Ti
    T1e[0] = 273.15 + Ti
    T2e[0] = 273.15 + Ti
    T1s[0] = 273.15 + Ti
    T2s[0] = 273.15 + Ti
    T1w[0] = 273.15 + Ti
    T2w[0] = 273.15 + Ti

    Tair = np.empty(N)
    Tair[0] = 273.15 + Ti

    s = 3600*(24/N)

    an = width*height
    ae = length*height
    aS = width*height
    aw = length*width


    A_f = length*width
    V = A_f*height
    dens = 1.225 #density of air 
    c_a = 0.718*1000 #specific heat of air
    C_air = V*dens*c_a

    dv = 0.1 #m3/s
    dm1 = dens*dv #kg/s
    m1 = s*dm1 #kg

    dve = 0.05 #m3/s
    ve = s*dve #m3 
    me = dens*ve #kg

    Q = np.empty(N)
    Q[0] = 0

    Tc = np.empty(N)
    Tc[0] = Tair[0]

    dm1dt = np.empty(N)
    dm1dt[0] = dm1

    inputTemp = 25
    ac_min = 18

    shift = False


    for i in range(N-1):
        T1n[i+1] = T1n[i] + s*(h_rc*((sol_airn[i]+273.15) - T1n[i])/Cc + (T2n[i]-T1n[i])/(R*Cc));
        T2n[i+1] = T2n[i] + s*(h_c*(Tair[i]-T2n[i])/Cc-(T2n[i]-T1n[i])/(R*Cc));
        T1e[i+1] = T1e[i] + s*(h_rc*((sol_aire[i]+273.15) - T1e[i])/Cc + (T2e[i]-T1e[i])/(R*Cc));
        T2e[i+1] = T2e[i] + s*(h_c*(Tair[i]-T2n[i])/Cc-(T2e[i]-T1e[i])/(R*Cc));
        T1s[i+1] = T1s[i] + s*(h_rc*((sol_airs[i]+273.15) - T1s[i])/Cc + (T2s[i]-T1s[i])/(R*Cc));
        T2s[i+1] = T2s[i] + s*(h_c*(Tair[i]-T2n[i])/Cc-(T2s[i]-T1s[i])/(R*Cc));
        T1w[i+1] = T1w[i] + s*(h_rc*((sol_airw[i]+273.15) - T1w[i])/Cc + (T2w[i]-T1w[i])/(R*Cc));
        T2w[i+1] = T2w[i] + s*(h_c*(Tair[i]-T2n[i])/Cc-(T2w[i]-T1w[i])/(R*Cc));

        # if dm1 != 0 and shift == False:
        #     Tc[i+1] = Tair[i] - h_c*(an*(T2n[i]-Tair[i])+ae*(T2e[i]-Tair[i])+aS*(T2s[i]-Tair[i])+aw*(T2w[i]-Tair[i]))/(c_a*dm1);
        #     if Tc[i+1] < (273.15+ac_min):
        #         Tc[i+1] = 273.15+ac_min;
        #     dm1 = h_c*(an*(T2n[i]-Tair[i])+ae*(T2e[i]-Tair[i])+aS*(T2s[i]-Tair[i])+aw*(T2w[i]-Tair[i]))/(c_a*(Tair[i]-Tc[i+1]));

        Tair[i+1] = Tair[i] + s*(h_c*(an*(T2n[i]-Tair[i])+ae*(T2e[i]-Tair[i])+aS*(T2s[i]-Tair[i])+aw*(T2w[i]-Tair[i]))/(C_air + m1*c_a-me*c_a)) + s*100*(290.15-Tair[i])/C_air# - s*(c_a*dm1*(Tair[i]-Tc[i+1])/(C_air + m1*c_a-me*c_a))# + s*10*(290.15-Tair[i])/C_air #+ s*1.4*A_w*((at[i]+273.15)-Tair[i])/C_air - s*800/C_air ;
        Q[i+1] = c_a*dm1*(Tair[i]-Tc[i+1]) + m1*c_a*(Tair[i+1]-Tair[i])/s;                

    


    figure(1)
    plot(Tair-273.15)
    
    plot(at-273.15)
    show()

    
