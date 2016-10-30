import matplotlib
matplotlib.use('Qt5Agg')
import pandas as pd
import numpy as np
from matplotlib.pyplot import show, figure, rcParams
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Core.Database.Database import Settings
from Core.Calculations.fit import fit
from scipy.integrate import simps, odeint
from matplotlib.pyplot import show,plot
from Core.Calculations import radiation, sunpath


engine = create_engine('sqlite:///settings.sqlite', echo=False)

Session = sessionmaker(bind=engine)
session = Session()

noOfDays = 1
N = noOfDays*500





hour = np.linspace(0,noOfDays*24,N)

air_temp = 0
dew_point = 0
relHum = 0
cloudCover = 0 

h_r = 4.5
h_rc = 11.0 #radiation + convection
g_atm = 0.5
sigma = 5.67*10**(-8)
epsi = 0

def vapor_pressure(i):
    global air_temp, relHum
    A = 6.116441
    m = 7.591386
    Tn = 240.7263
    T = air_temp(hour[i])-273.15
    ps = A*10**(m*T/(T+Tn))
    RH = relHum(hour[i])
    p = RH*ps    
    return p

def I_cloud(i):
    global dew_point
    return sigma*(dew_point(hour[i]))**4

def cc(i):
    okta = cloudCover(hour[i])
    okta = int(okta)
    if okta == 1:
        return 0
    elif okta == 2:
        return .25
    elif okta == 3:
        return .30
    elif okta == 4:
        return .5
    elif okta == 5:
        return .60
    elif okta == 6:
        return .75
    elif okta == 7:
        return .8
    else:
        return 1.0


def skyTemp(i):
    global sigma, cloudCover, dew_point
    I = cc(i)*(I_cloud(i))+(1-cc(i))*sigma*(air_temp(hour[i])**4)*(0.79-0.174*10**(-0.041*vapor_pressure(i)))
    return (I/sigma)**.25
def T_sa(i, I):
    global h_rc, air_temp, dew_point, epsi, alpha
    T = air_temp(hour[i])-273.15 + alpha*I[i]/h_rc - g_atm*6.5*(air_temp(hour[i]) - skyTemp(i))/h_rc
    return T

def thermalLoad(fileName):
    global alpha, N, air_temp, dew_point, epsi, cloudCover, relHum, noOfDays,N, hour
    global sol_airn,sol_aire,sol_airs,sol_airw
    for sett in session.query(Settings).filter(Settings.name==fileName):

        length = sett.length
        width = sett.width
        height = sett.height

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
        noOfDays = int(sett.numDays)
    N = noOfDays*500
    hour = np.linspace(0,noOfDays*24,N)
    sol_airn = np.empty(N)
    sol_aire = np.empty(N)
    sol_airs = np.empty(N)
    sol_airw = np.empty(N)


    air_temp, dew_point, relHum, cloudCover, days = fit(fileName)
    R = thickness/k
    Cc = rho*c*thickness/2
    #call function of air and vapor pressure

    excel = "Data/Radiation/ShortwaveRadiation-"+fileName+".xlsx"
    
    try:
        rad = pd.read_excel(excel)
    except FileNotFoundError as error:
        sp = sunpath.calculateSunPath(fileName)
        r = radiation.calculateRadiation(fileName)
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
    sky = []
    for i in range(N):
        sol_airn[i] = T_sa(i, I_sn)
        sol_aire[i] = T_sa(i, I_se)
        sol_airs[i] = T_sa(i, I_ss)
        sol_airw[i] = T_sa(i, I_sw)
        at[i] = air_temp(hour[i])
        
    # plot(sol_airn)
    # plot(sol_aire)
    # plot(sol_airw)
    # plot(sol_airs)
    # show()
    # #heat
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
    T2n[0] = 273.15 + Ti+.001
    T1e[0] = 273.15 + Ti
    T2e[0] = 273.15 + Ti+.001
    T1s[0] = 273.15 + Ti
    T2s[0] = 273.15 + Ti+.001
    T1w[0] = 273.15 + Ti
    T2w[0] = 273.15 + Ti+.001

    T1nf = np.empty(N)
    T2nf = np.empty(N)
    T1ef = np.empty(N)
    T2ef = np.empty(N)
    T1sf = np.empty(N)
    T2sf = np.empty(N)
    T1wf = np.empty(N)
    T2wf = np.empty(N)

    T1nf[0] = 273.15 + Ti
    T2nf[0] = 273.15 + Ti+.001
    T1ef[0] = 273.15 + Ti
    T2ef[0] = 273.15 + Ti+.001
    T1sf[0] = 273.15 + Ti
    T2sf[0] = 273.15 + Ti+.001
    T1wf[0] = 273.15 + Ti
    T2wf[0] = 273.15 + Ti+.001


    Tair = np.empty(N)
    Tair[0] = 273.15 + Ti
    Tfree = np.empty(N)
    Tfree[0] = 273.15 + Ti

    s = (noOfDays*24*3600-0)/N

    an = width*height
    ae = length*height
    aS = width*height
    aw = length*width


    A_f = length*width
    V = A_f*height
    dens = 1.225 #density of air 
    c_a = 0.718*1000 #specific heat of air
    C_air = V*dens*c_a

    Q = np.zeros(N)

    Tc = np.empty(N)
    Tc[0] = Tair[0]

    

    Tcomfmin = Tcomf-3
    Tcomfmax = Tcomf+1


    for i in range(N-1):

        T1n[i+1] = T1n[i] + s*(h_rc*((sol_airn[i]+273.15) - T1n[i])/Cc + (T2n[i]-T1n[i])/(R*Cc))
        T1nf[i+1] = T1nf[i] + s*(h_rc*((sol_airn[i]+273.15) - T1nf[i])/Cc + (T2nf[i]-T1nf[i])/(R*Cc))

        T2n[i+1] = T2n[i] + s*(h_c*(Tfree[i]-T2n[i])/Cc-(T2n[i]-T1n[i])/(R*Cc))
        T2nf[i+1] = T2nf[i] + s*(h_c*(Tair[i]-T2nf[i])/Cc-(T2nf[i]-T1nf[i])/(R*Cc))

        T1e[i+1] = T1e[i] + s*(h_rc*((sol_aire[i]+273.15) - T1e[i])/Cc + (T2e[i]-T1e[i])/(R*Cc))
        T1ef[i+1] = T1ef[i] + s*(h_rc*((sol_aire[i]+273.15) - T1ef[i])/Cc + (T2ef[i]-T1ef[i])/(R*Cc))

        T2e[i+1] = T2e[i] + s*(h_c*(Tfree[i]-T2e[i])/Cc-(T2e[i]-T1e[i])/(R*Cc))
        T2ef[i+1] = T2ef[i] + s*(h_c*(Tair[i]-T2ef[i])/Cc-(T2ef[i]-T1ef[i])/(R*Cc))

        T1s[i+1] = T1s[i] + s*(h_rc*((sol_airs[i]+273.15) - T1s[i])/Cc + (T2s[i]-T1s[i])/(R*Cc))
        T1sf[i+1] = T1sf[i] + s*(h_rc*((sol_airs[i]+273.15) - T1sf[i])/Cc + (T2sf[i]-T1sf[i])/(R*Cc))

        T2s[i+1] = T2s[i] + s*(h_c*(Tfree[i]-T2s[i])/Cc-(T2s[i]-T1s[i])/(R*Cc))
        T2sf[i+1] = T2sf[i] + s*(h_c*(Tair[i]-T2sf[i])/Cc-(T2sf[i]-T1sf[i])/(R*Cc))

        T1w[i+1] = T1w[i] + s*(h_rc*((sol_airw[i]+273.15) - T1w[i])/Cc + (T2w[i]-T1w[i])/(R*Cc))
        T1wf[i+1] = T1wf[i] + s*(h_rc*((sol_airw[i]+273.15) - T1wf[i])/Cc + (T2wf[i]-T1wf[i])/(R*Cc));


        T2w[i+1] = T2w[i] + s*(h_c*(Tfree[i]-T2w[i])/Cc-(T2w[i]-T1w[i])/(R*Cc));
        T2wf[i+1] = T2wf[i] + s*(h_c*(Tair[i]-T2wf[i])/Cc-(T2wf[i]-T1wf[i])/(R*Cc));

        
        Q[i] = h_c*(an*(T2nf[i]-273.15-Tcomf)+ae*(T2ef[i]-273.15-Tcomf)+aS*(T2sf[i]-273.15-Tcomf)+aw*(T2wf[i]-273.15-Tcomf))

        if Q[i] < 0:
            Q[i] = 0

        Tfree[i+1] = Tfree[i] + s*(h_c*(an*(T2n[i]-Tfree[i])+ae*(T2e[i]-Tfree[i])+aS*(T2s[i]-Tfree[i])+aw*(T2w[i]-Tfree[i])))/(C_air)
        Tair[i+1] = Tair[i] + s*(h_c*(an*(T2nf[i]-Tair[i])+ae*(T2ef[i]-Tair[i])+aS*(T2sf[i]-Tair[i])+aw*(T2wf[i]-Tair[i])))/(C_air) - s*Q[i]/(C_air)
        
    
    
    days = dayNames(days)
    Q[N-1] = Q[N-2]

    #
    secs = np.linspace(0,noOfDays*24*3600,N)
    energy = simps(y=Q,x=secs,even='avg')

    show_plot(Tair,Tfree,at,Q, days,fileName)
    Tfreep = np.empty(N)
    np.copyto(Tfreep, Tfree)

    indexes_above_max_temp = np.where( Tfreep > (Tcomfmax+273.15))
    Tfreep[[indexes_above_max_temp]] = Tcomfmax+273.15
    
    discomfort = measureD(Tfree,secs,Tcomfmax)  
    comfort = measureC(Tfreep,secs,Tcomfmax)

    print(fileName)
    print('Required energy {} (days):{} kJ'.format(noOfDays,round((energy/1000),2)))
    print('Average power required: {} W'.format( round(Q.mean(),2) ) )
    print('Average temperature in free mode: {} C'.format(Tfree.mean()-273.15))
    print('Discomfort (D): {}'.format( round(discomfort/(comfort+discomfort),2) ))
    print('Comfort (C): {}'.format( round(comfort/(comfort+discomfort),2 )))


def measureC(Tairf, secs, Tcomfmax):
    C = simps(y=np.full(N,Tcomfmax+273.15), x=secs,even='avg') - simps(y=Tairf, x = secs, even='avg')
    if C < 0:
        C = 0
    return C

def measureD(Tairf,secs,Tcomfmax):
    indexes_below_max_temp = np.where(Tairf < (Tcomfmax+273.15))
    Tairf[indexes_below_max_temp] = Tcomfmax+273.15
    D = simps(y=Tairf, x=secs,even='avg') - simps(y=np.full(N,Tcomfmax+273.15), x=secs,even='avg')
    if D<0:
        D=0
    return D

def dayNames(days):
    names = []
    for d in days:
        month = d[0]
        day = d[1]
        if month == 1:
            monthName = 'Jan'
        elif month == 2:
            monthName = 'Feb'
        elif month == 3:
            monthName = 'Mar'
        elif month == 4:
            monthName = 'Apr'
        elif month == 5:
            monthName = 'May'
        elif month == 6:
            monthName = 'Jun'
        elif month == 7:
            monthName = 'July'
        elif month == 8:
            monthName = 'Aug'
        elif month == 9:
            monthName = 'Sept'
        elif month == 10:
            monthName = 'Oct'
        elif month == 11:
            monthName = 'Nov'
        elif month == 12:
            monthName = 'Dec'
        names.append(monthName+' '+str(day))
    return names

def show_plot(Tair, Tfree,at, Q, days,fileName):

    fig = figure(fileName)

    energy = fig.add_subplot(211,axisbg='black')
    temperature = fig.add_subplot(212,axisbg='black')
    energy.set_axisbelow(True)
    temperature.set_axisbelow(True)
    
    #minor grids
    energy.xaxis.grid(True,'minor', color='w',linestyle='-',linewidth=.2)
    energy.yaxis.grid(True,'minor', color='w',linestyle='-',linewidth=.2)
    #ticks    
    energy.xaxis.set_ticks(np.arange(0,24*noOfDays+1,24))
    energy.minorticks_on()
    energy.set_xticklabels(days)
    #major grids
    energy.xaxis.grid(True,'major',linewidth=.5,linestyle='-', color='w')
    energy.yaxis.grid(True,'major',linewidth=.5,linestyle='-', color='w')
    #labels
    energy.set_ylabel("Required Power (W)")



    #minor grids
    temperature.xaxis.grid(True,'minor', color='w',linestyle='-',linewidth=.2)
    temperature.yaxis.grid(True,'minor', color='w',linestyle='-',linewidth=.2)   
    #ticks
    temperature.xaxis.set_ticks(np.arange(0,24*noOfDays+1,24))
    temperature.minorticks_on()
    temperature.set_xticklabels(days)
    #major grids
    temperature.xaxis.grid(True,'major',linewidth=.5,linestyle='-', color='w')
    temperature.yaxis.grid(True,'major',linewidth=.5, linestyle='-',color='w')
    #labels
    temperature.set_ylabel("Temperature ($^{o}C$)")
    temperature.set_xlabel("day")
    
    #for mathematical fonts
    params = {'mathtext.default': 'regular' }          
    rcParams.update(params)
    energy.plot(hour, Q, linewidth='1.5', label='Energy requirements')

    temperature.plot(hour,Tair-273.15, linewidth='1.5', label='$T_{wAC}$')
    temperature.plot(hour, Tfree-273.15, linewidth='1.5',label='$T_{free}$',linestyle='--')
    temperature.plot(hour, at-273.15, linewidth='1.5',label='$T_{outside}$')
    temperature.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=0., fontsize='medium',
        fancybox=True, shadow=True)
    show()


    
