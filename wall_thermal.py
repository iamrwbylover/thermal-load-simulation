# -*- coding: utf-8 -*-
"""
Created on Tue Apr 05 23:15:11 2016

@author: Neil
"""

import numpy as np
import matplotlib.pyplot as mp
from sympy import Symbol, diff, simplify, cos, 


#-----------------initialization-----------------------------------------------
N = 4000
delta = 8
LSTM = 15*delta
phi = np.pi/2

#longwave
I_l = np.zeros(N)
I_latm = np.zeros(N)
I_cloud = np.zeros(N) #sigma x dewTemp[i]^4
I_lterr = np.zeros(N)
I_lrefl = np.zeros(N)
T = np.zeros(N)

#shortwave
I_dni = np.zeros(N)
I_diff = np.zeros(N)
I_dir = np.zeros(N)
I_srefl = np.zeros(N)
I_sdirh = np.zeros(N)
I_s = np.zeros(N)


#emitted
I_e = np.zeros(N)

Temp1 = np.zeros(N)
Temp2 = np.zeros(N)
Temp3 = np.zeros(N)
Temp4 = np.zeros(N)

iTemp1 = np.zeros(N)
iTemp2 = np.zeros(N)
iTemp3 = np.zeros(N)
iTemp4 = np.zeros(N)

#room air
Tain = []

at = np.zeros(N)


T_a = Symbol('T_a')
#-------------------------first set of objects---------------------------------

class settings:
    def __init__(self, longitude = 121.072729, latitude = 14.649519, day = 141):
        self.longitude = longitude 
        self.latitude = latitude*np.pi/180
        self.day = day
   
sett = settings(day = 250) #pwedeng magpalit ng day dito saka position

class sunpath:
    def __init__(self, EoT = np.zeros(365), day = np.linspace(1,365,365), 
                 TC = np.zeros(365), HRA = np.zeros(N), hr = np.linspace(0,24,N)):
        self.EoT = EoT
        self.day = day
        self.TC  = TC
        self.HRA = HRA
        self.hr = hr        

sp = sunpath()
        
class angles:
    def __init__(self, elev = np.zeros(N), azi = np.zeros(N), 
                 hour = np.linspace(0,24,N)):
        self.elev = elev
        self.azi = azi        
        self.hour = hour

    def sunrise(self):
        ad = np.where(self.elev>0)
        self.elev = self.elev[ad]
        self.azi = self.azi[ad]
        sp.hr = sp.hr[ad]
        
    def inversion(self):
        ad = np.where(self.elev == max(self.elev))
        for i in np.linspace(ad[0][0],N-1,N-(ad[0][0])):
            self.azi[int(i)] = -self.azi[int(i)]
        
a = angles()


#------------------------------------------------------------------------------

#----------------------sunpath functions---------------------------------------
def B(d):
    return ((360.0/365)*(d-81))*np.pi/180

def EOT(b):
    return 9.87*np.sin(2*b) - 7.53*np.cos(b) - 1.5*np.sin(b)

def LST(lt):
    return lt + sp.TC[sett.day]/60.0
#------------------end---------------------------------------------------------
#------------------------sun path loops----------------------------------------    
    
for i in range(365):
    sp.EoT[i] = EOT(B(i))
    sp.TC[i] = 4*(sett.longitude-LSTM) + sp.EoT[i]

for i in range(N):
    sp.HRA[i] = (15*(LST(sp.hr[i])-12))*np.pi/180
#----------------------------end-----------------------------------------------

#--------------------------elevation and azimuthal angles----------------------
delta = (23.45*np.sin((((360.0/365)*(sett.day-81))*np.pi/180)))*np.pi/180

for i in range(N):
    a.elev[i] = np.arcsin(np.sin(delta)*np.sin(sett.latitude)
                + np.cos(delta)*np.cos(sett.latitude)*np.cos(sp.HRA[i])) 
    a.azi[i] = np.arccos((np.sin(delta)*np.cos(sett.latitude)
              -np.cos(delta)*np.sin(sett.latitude)*np.cos(sp.HRA[i]))
              /np.cos(a.elev[i]))
    

a.inversion()
#------------------------------------------------------------------------------

#--------------------------functions-------------------------------------------
def air_temp(t):
    a0 =      29.17  
    a1 =     -2.297  
    a2 =     0.6056  
    b1 =      -1.764  
    b2 =     0.1449  
    w =    0.2683  
    temp =  a0 + a1*np.cos(w*t) + a2*np.cos(2*w*t) + b1*np.sin(w*t) + b2*np.sin(2*w*t)
    
    return temp+273.15
    
def vapor_pressure(T_a):
    return 6.11*10**((7.5*(T_a-273.15))/(237.3+(T_a-273.15)))
    #x is the absolute temperature


def airmass(z):
    return (1)/(np.cos(z) + 0.50572*(96.07995-z*(180/np.pi))**(-1.6364))
    #z is the zenith angle




def D_at(t2):
    a = 0.6162851*np.sin(0.2683*t2) - 0.32496496*np.sin(0.5366*t2) - 0.4732812*np.cos(0.2683*t2) + 0.07775334*np.cos(0.5366*t2)
    return a


hc = 4.5

#-------------------------second set of objects--------------------------------


class constants:
    def __init__(self, A = 1104, c = .121, C_n = 0.8):
        self.A = A
        self.c = c
        self.C_n = C_n

c = constants()



class radconstants:
    def __init__(self,alpha = 0.36, epsi = 0.95, sigma = 5.67*10**(-8),
                 g_atm = (np.cos(phi/2))**2):

        self.alpha = alpha
        self.epsi = epsi
        self.sigma = sigma
        self.g_atm = g_atm
        self.g_terr = 1 - g_atm

rc = radconstants()
        
class environment():
    def __init__(self,rho_soil = 0.17,rhol_soil = 0.05, epsi_soil = 0.95,):
        self.rho_soil = rho_soil
        self.rhol_soil = rhol_soil
        self.epsi_soil = epsi_soil
        
    
    def airtemp(self):
        for i in range(N):
            at[i] = air_temp(sp.hr[i])
            
env = environment()        
#----------------------direct normal and diffused irradianace------------------

env.airtemp()


for i in range(N):
    if a.elev[i] < 0:
        I_dni[i] = 0
    else:
        angle = np.pi/2 - a.elev[i]    
        am = airmass(angle)
        I_dni[i] = c.A*0.7**(am**.678)
    I_diff[i] = c.c*I_dni[i]

#------------------third set of objects----------------------------------------

l = 0.1
omega = 0.2683#(1/24.0)*2*np.pi*(1/3600.0)
k = 0.8
dens = 2400.0
speche = 880

R = l/k

diffu = k/(speche*dens)

H = (-1j*omega*((speche*dens*l**2)/k))**.5#(1j*omega/(diffu*l))**.5


a11 = np.cos(H)
a12 = -R*np.sin(H)/H
a21 = -H*np.sin(H)/R
a22 = np.cos(H)



#------------------beta-------------------------------------------------------

I = np.zeros(N)

class building():
    def __init__(self, front = 0.0, right = np.pi/2, back = np.pi,
                 left = 3*np.pi/2, T_0 = air_temp(sp.hr[0]), U_value = 11.11,
                 l = 6, w = 3, h = 3):
        self.T_o = T_0
        self.front = front
        self.right = right
        self.back = back
        self.left = left
        self.U = U_value
        self.l = l
        self.w = w
        self.h = h
        self.V = l*w*h
        self.C_air = 836.47
    def wall_temp(self,i,theta,wall):
        if i != 0:
            T_a = air_temp(sp.hr[i])
            T_0 = wall[i-1]
            T = (rc.alpha*I_s[i] + rc.epsi*I_l[i] + hc*T_a
            +3*rc.epsi*rc.sigma*T_0**4)/(4*rc.epsi*rc.sigma*T_0**3 + hc)
            return T
        else:
            return self.T_o
    
    def inwall_temp(self,i,wall_temp):
        I = rc.alpha*I_s[i] + rc.epsi*I_l[i] - rc.epsi*rc.sigma*wall_temp[i]**4
        return wall_temp[i] -(I)/self.U
#        return a11*wall_temp[i] + a12*I
build = building()         
#build = building(front = 0.0+np.pi/4, right = np.pi/2+np.pi/4, back = np.pi+np.pi/4,
#                 left = 3*np.pi/2+np.pi/4)

#------------------------------------------------------------------------------

t2 = Symbol('t2')

def Pw(T_a):
    return 0


#original
def Ilterr(t):
    return env.epsi_soil*rc.sigma*air_temp(t)**4
def Ilatm(t):
    return rc.sigma*(air_temp(t)**4)*(0.79-0.174*10**(-0.041*(6.11*10**((7.5*(air_temp(t)-273.15))/(237.3+(air_temp(t)-273.15))))))
def Ilrefl(t):
    return env.rhol_soil*Ilatm(t)

#derived
def DIlterr(t):
    return D_at(i)*4*env.epsi_soil*rc.sigma*air_temp(t)**3
def DIlatm(t):
    ans = D_at(i)*(2.471481558e-9*10**(-0.25051*10**((7.5*air_temp(t) - 2048.625)/(air_temp(t) - 35.85)))*10**((7.5*air_temp(t) - 2048.625)/(air_temp(t) - 35.85))*air_temp(t)**4*(7.5/(air_temp(t) - 35.85) - (7.5*air_temp(t) - 2048.625)/(air_temp(t) - 35.85)**2)*np.log(10)**2 + 2.268e-7*air_temp(t)**3*(-0.174*10**(-0.25051*10**((7.5*air_temp(t) - 2048.625)/(air_temp(t) - 35.85))) + 0.79))
    return ans
def DIlrefl(t):
    return env.rhol_soil*Ilatm(t)*DIlatm(t)




#------------------------------------------------------------------------------



class radiation():
    def __init__(self, C = 0):
        self.C = C
    def I_long(self,i):
        T[i] = air_temp(sp.hr[i])
        I_latm[i] = self.C*I_cloud[i] +(1-self.C)*(rc.sigma*T[i]**4)*(0.79 - 
        0.174*10**(-0.041*vapor_pressure(T[i])))
        I_lterr[i] = rc.sigma*T[i]**4
        I_lrefl[i] = env.rhol_soil*I_latm[i]
        I_l[i] = rc.g_atm*I_latm[i] + rc.g_terr*(I_lterr[i] + I_lrefl[i])
        
    def I_short(self, i, theta):
        I_dir[i] = I_dni[i]*np.cos(a.elev[i])*np.cos(theta-a.azi[i])
        if a.elev[i] < 0:
            I_s[i] = 0
        elif  I_dir[i] <0:
            I_dir[i] = 0
            I_sdirh[i] = I_dni[i]*np.sin(a.elev[i]) + I_diff[i]
            I_srefl[i] = env.rho_soil*(I_sdirh[i] + I_diff[i])
            I_s[i] = I_dir[i] + rc.g_atm*I_diff[i] + rc.g_terr*I_srefl[i]
        else:
            I_sdirh[i] = I_dni[i]*np.sin(a.elev[i]) + I_diff[i]
            I_srefl[i] = env.rho_soil*(I_sdirh[i] + I_diff[i])
            I_s[i] = I_dir[i] + rc.g_atm*I_diff[i] + rc.g_terr*I_srefl[i]
        return I_s[i]

rad = radiation()        
#---------------------------temperature calculations---------------------------
     
I1 = np.zeros(N)
I2 = np.zeros(N)
I3 = np.zeros(N)
I4 = np.zeros(N)
for i in range(N):
    rad.I_long(i)
    
    
        
    
    I1[i] = rad.I_short(i, build.front)
    Temp1[i] = build.wall_temp(i,build.front,Temp1)
    iTemp1[i] = build.inwall_temp(i,Temp1)
    
    
    I2[i] = rad.I_short(i, build.right)
    Temp2[i] = build.wall_temp(i,build.right,Temp2)
    iTemp2[i] = build.inwall_temp(i,Temp2)
    
    I3[i] = rad.I_short(i, build.back)
    Temp3[i] = build.wall_temp(i,build.back,Temp3)
    iTemp3[i] = build.inwall_temp(i,Temp3)
    
    I4[i] = rad.I_short(i, build.left)
    Temp4[i] = build.wall_temp(i,build.left,Temp4)
    iTemp4[i] = build.inwall_temp(i,Temp4)


#-------------------------differential equation--------------------------------  
l,w,h = build.l,build.w,build.h
V = build.V
C = build.C_air
answ = []



x = min(sp.hr)
y = max(sp.hr)
hz = 3600*(y-x)/N
Ts = 298.15#air_temp(x-hz/3600)
wit = np.zeros(N)


def Tx(T,i,a): 
    ans = 4.68* (l*h*((iTemp1[i] - T) + (iTemp3[i] - T)) + w*h*((iTemp2[i]-T)+
    (iTemp4[i]-T)) + 2*w*l*((300.0 - T)))/(C*V) + a*(293.15 - T)/(C*V)
    wit[i] = ans
    return ans
    
T1 = np.zeros(N)
T2 = np.zeros(N)
T3 = np.zeros(N)
T4 = np.zeros(N)



for i in range(N):
    Tain.append(Ts)
    Ts += hz*Tx(Ts,i,10)

    
Tain = np.array(Tain)


#plots
mp.figure(1)
mp.plot(sp.hr, Tain-273.15,label = 'room air temperature')
#mp.plot(sp.hr, T0-273.15,label = 'ventilation rate = 10')
#mp.plot(sp.hr, T1-273.15,label = 'ventilation rate = 30')
#mp.plot(sp.hr, T2-273.15,label = 'ventilation rate = 60')
#mp.plot(sp.hr, T3-273.15,label = 'ventilation rate = 90')
#mp.plot(sp.hr, T4-273.15,label = 'ventilation rate = 1000')
mp.plot(sp.hr, at-273.15,'--',label = 'outside air temperature')
mp.xticks(np.arange(0,25,1))
mp.xlabel('hour of the day')
mp.ylabel('C')
mp.legend(loc = 'best')
mp.show()


#----------------------------plots---------------------------------------------

class plots():
    def outside_wall(self, orientation = 0):
        t = sp.hr
        if orientation == 0:        
            mp.figure(2)
            mp.plot(t, iTemp1-273.15, '--', label = 'inside north wall temperature')
            mp.plot(t, Temp1-273.15, '-', label = 'outside north wall temperature')
            mp.xticks(np.arange(0,25,1))
            mp.xlabel('hour of the day')
            mp.ylabel('C')
            mp.legend(loc = 'best')
            mp.show()
            mp.figure(3)
            mp.plot(t, iTemp2-273.15, '--', label = 'inside east wall temperature')
            mp.plot(t, Temp2-273.15, '-', label = 'outside east wall temperature')
            mp.xticks(np.arange(0,25,1))
            mp.xlabel('hour of the day')
            mp.ylabel('C')
            mp.legend(loc = 'best')
            mp.show()
            mp.figure(4)
            mp.plot(t, iTemp3-273.15, '--', label = 'inside south wall temperature')
            mp.plot(t, Temp3-273.15, '-', label = 'outside south wall temperature')
            mp.xticks(np.arange(0,25,1))
            mp.xlabel('hour of the day')
            mp.ylabel('C')
            mp.legend(loc = 'best')
            mp.show()
            mp.figure(5)
            mp.plot(t, iTemp4-273.15, '--', label = 'inside west wall temperature')
            mp.plot(t, Temp4-273.15, '-', label = 'outside west wall temperature')
            mp.xticks(np.arange(0,25,1))
            mp.xlabel('hour of the day')
            mp.ylabel('C')
            mp.legend(loc = 'best')
            mp.show()
        else:
            mp.plot(t, at-273.15, '--', label = 'outside air temperature')
            mp.plot(t, orientation-273.15, '-', label = 'north outside wall temperature')
            mp.xticks(np.arange(0,25,1))
            mp.xlabel('hour of the day')
            mp.ylabel('C')
            mp.legend(loc = 'best')
            mp.show()
        
    def any(self, x, y):
        mp.plot(x,y)
        mp.xticks(np.arange(0,25,1))
        mp.show()
            
plot = plots()

plot.outside_wall()

#---------------------beta----------------------------------------------------

T = 300

a = 17*(at[i] - T) 




















