import pandas as pd 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Core.Database.Database import Settings


engine = create_engine('sqlite:///settings.sqlite', echo=False)

Session = sessionmaker(bind=engine)
session = Session()


def fit(fileName):
	for sett in session.query(Settings).filter(Settings.name==fileName):
		month = str(sett.date[5:7])
		day = str(sett.date[8:10])
	print(month,day)