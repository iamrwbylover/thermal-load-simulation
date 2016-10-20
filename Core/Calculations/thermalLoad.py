import pandas as pd
import numpy as np
from matplotlib.pyplot import plot, show
from scipy.linalg import expm, inv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Core.Database.Database import Settings

from Core.Calculations.Functions import air_temp



engine = create_engine('sqlite:///settings.sqlite', echo=True)

Session = sessionmaker(bind=engine)
session = Session()


N = 4000
hour = np.linspace(0,24,N)

alpha = 0
h_rc = 11.0 #radiation + convection
g_atm = 0.5
def T_sa(i, I):
    global alpha
    #consider dew point here !!!
    #!!!!!!!!!!!!!!!
    
    T = air_temp(hour[i])-273.15 + alpha*I[i]/h_rc - g_atm*6.5*(air_temp(hour[i]) - (25+273.15))/h_rc
    if i == 3900:
        print(T)
    return T

def T_io(i, sol_air, Ti):
    ans = np.mat([[sol_air[i]+273.15],[Ti]])
    return ans


def test():
    print('meron naman')

def thermalLoad(fileName):
    global alpha, N
    print(fileName, 'yow')
    for sett in session.query(Settings).filter(Settings.name==fileName):
        print('here')
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
        sigma = 5.67*(10)**(-8)

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

    A = np.mat([[a11,a12],[a21,a22]])
    B = np.mat([[b11,b12],[b21,b22]])
    C = np.mat([c11,c12])
    D = np.mat([d11,d12])

    print(A)
    print(B)
    print(C)
    print(D)


    I = np.mat([[1,0],[0,1]])
    
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
 

    #heat
    Qn = np.empty(N)
    Qe = np.empty(N)
    Qs = np.empty(N)
    Qw = np.empty(N)

    Qt = np.empty(N) # total heat
    T_i = np.empty(N) 
    T_initial = 273.15 + 25

    T_i[0] = T_initial

    Tn = np.empty(N)
    Te = np.empty(N)
    Ts = np.empty(N)
    Tw = np.empty(N)


    A_f = length*width
    V = A_f*height
    dens = 1.225 #density of air 
    c_a = 0.718*1000 #specific heat of air

    C_air = V*dens*c_a

    occ = 2 # number of occupants
    Q = 1 #volumetric flow rate 
    D = occ/A_f 
    mu = Q*D*height/V

    for i in range(N):
        Ti = T_i[i]
        if i == 1:
            Qn[i] = S0*T_io(1,sol_airn,Ti) + S1*T_io(1,sol_airn,Ti) + S2*T_io(1,sol_airn,Ti) - e1*Qn[1] - e2*Qn[1];
            Qe[i] = S0*T_io(1,sol_aire,Ti) + S1*T_io(1,sol_aire,Ti) + S2*T_io(1,sol_aire,Ti) - e1*Qe[1] - e2*Qe[1];
            Qs[i] = S0*T_io(1,sol_airs,Ti) + S1*T_io(1,sol_airs,Ti) + S2*T_io(1,sol_airs,Ti) - e1*Qs[1] - e2*Qs[1];
            Qw[i] = S0*T_io(1,sol_airw,Ti) + S1*T_io(1,sol_airw,Ti) + S2*T_io(1,sol_airw,Ti) - e1*Qw[1] - e2*Qw[1];
        elif i == 2:
            Qn[i] = S0*T_io(i,sol_airn,Ti) + S1*T_io(i-1,sol_airn,Ti) + S2*T_io(i-1,sol_airn,Ti) - e1*Qn[i-1] -e2*Qn[i-1];
            Qe[i] = S0*T_io(i,sol_aire,Ti) + S1*T_io(i-1,sol_aire,Ti) + S2*T_io(i-1,sol_aire,Ti) - e1*Qe[i-1] -e2*Qe[i-1];
            Qs[i] = S0*T_io(i,sol_airs,Ti) + S1*T_io(i-1,sol_airs,Ti) + S2*T_io(i-1,sol_airs,Ti) - e1*Qs[i-1] -e2*Qs[i-1];
            Qw[i] = S0*T_io(i,sol_airw,Ti) + S1*T_io(i-1,sol_airw,Ti) + S2*T_io(i-1,sol_airw,Ti) - e1*Qw[i-1] -e2*Qw[i-1];
        else:
            Qn[i] = S0*T_io(i,sol_airn,Ti) + S1*T_io(i-1,sol_airn,Ti) + S2*T_io(i-2,sol_airn,Ti) - e1*Qn[i-1] -e2*Qn[i-2];
            Qe[i] = S0*T_io(i,sol_aire,Ti) + S1*T_io(i-1,sol_aire,Ti) + S2*T_io(i-2,sol_aire,Ti) - e1*Qe[i-1] -e2*Qe[i-2];
            Qs[i] = S0*T_io(i,sol_airs,Ti) + S1*T_io(i-1,sol_airs,Ti) + S2*T_io(i-2,sol_airs,Ti) - e1*Qs[i-1] -e2*Qs[i-2];
            Qw[i] = S0*T_io(i,sol_airw,Ti) + S1*T_io(i-1,sol_airw,Ti) + S2*T_io(i-2,sol_airw,Ti) - e1*Qw[i-1] -e2*Qw[i-2];
                            
        Tn(i) = Qn(i)/.3 + sol_airn(i);
        Te(i) = Qe(i)/.3 + sol_aire(i);
        Ts(i) = Qs(i)/.3 + sol_airs(i);
        Tw(i) = Qw(i)/.3 + sol_airw(i);
    print('Success bui')

    plot(Tn)
    plot(Te)
    plot(Tw)
    plot(Ts)
    show()


