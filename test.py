
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine



    
Base = declarative_base()
engine = create_engine('sqlite:///users.sqlite', echo=True)

class User(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullName = Column(String)
    password = Column(String)

    def __repr__(self):
        return "<User(name='%s', fullName = '%s', password='%s')>" %(self.name, self.fullName, self.password)


User.__table__
Base.metadata.create_all(engine)