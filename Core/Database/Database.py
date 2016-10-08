from sqlalchemy import Column, Integer, String, Float, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine



    
Base = declarative_base()
engine = create_engine('sqlite:///settings.sqlite', echo=False)

class Settings(Base):
    __tablename__ = 'Settings'
    name = Column(String, primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    date = Column(String)
    swRC = Column(Float)
    lwRC = Column(Float)
    lwE = Column(Float)
    thickness = Column(Float)
    spec_heat = Column(Float)
    therm_cond = Column(Float)
    conv_coeff = Column(Float)
    density = Column(Float)
    swAbs = Column(Float)
    lwEWall = Column(Float)
    length = Column(Float)
    width = Column(Float)
    height = Column(Float)
    direction = Column(Float)
    initTemp = Column(Float)
    comfTemp = Column(Float)

    def __repr__(self):
        return "<Settings(name='%s', latitude = '%f', longitude = '%f',altitude = '%f',date = '%s',shortwave reflection coefficient = '%f',longwave reflection coefficient = '%f',longwave emissivity = '%f',)>" %(self.name,self.latitude, self.longitude, self.altitude,str(self.date), self.swRC, self.lwRC, self.lwE)







Settings.__table__
Base.metadata.create_all(engine)