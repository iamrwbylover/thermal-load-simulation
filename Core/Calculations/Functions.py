import numpy as np

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

sigma = 5.67*10**(-8)

def Ilterr(epsi_soil,t):
    return epsi_soil*sigma*air_temp(t)**4

def Ilatm(t):
    return sigma*(air_temp(t)**4)*(0.79-0.174*10**(-0.041*(6.11*10**((7.5*(air_temp(t)-273.15))/(237.3+(air_temp(t)-273.15))))))

def Ilrefl(rhol_soil,t):
    return rhol_soil*Ilatm(t)
