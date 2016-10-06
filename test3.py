from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from test import User


engine = create_engine('sqlite:///users.sqlite', echo=True)

Session = sessionmaker(bind=engine)
session = Session()

for user in session.query(User).order_by(User.id):
    print(user.fullName)