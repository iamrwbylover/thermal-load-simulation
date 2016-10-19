from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Database import Settings


engine = create_engine('sqlite:///home/bisgetti/Documents/Thesisit/settings.sqlite', echo=True)

Session = sessionmaker(bind=engine)
session = Session()

for sett in session.query(Settings).filter(Settings.name=='foo'):
    print(sett.date[5:])