from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Core.Database.Database import Settings
import Core.Calculations.Functions as fxn
import numpy as np
engine = create_engine('sqlite:///settings.sqlite', echo=True)

Session = sessionmaker(bind=engine)
session = Session()
N = 4000


hr = np.linspace(0,24,N)
I_latm = np.empty(N)
I_lterr = np.empty(N)
I_lrefl = np.empty(N)
I_ltotal = np.empty(N)
airtemp = np.empty(N)


def calculateOutsideWallTemp(fileName):
    for sett in session.query(Settings).filter(Settings.name==fileName):
        epsi_soil = sett.lwE
        rhol_soil = sett.lwRC
        rhos_soil = sett.swRC
    print(epsi_soil, rhol_soil, rhos_soil)

calculateOutsideWallTemp('foo')