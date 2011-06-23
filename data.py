from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
class User(Base):
	__tablename__ = 'users'

	id = Column(Integer, primary_key = True)
	name = Column(String)
	fullname = Column(String)
	password = Column(String)

	def __init__(self, name, fullname, password):
		self.name = name
		self.fullname = fullname
		self.password = password

	def __repr__(self):
		return "<" + self.fullname + " with password " + self.password + ">"

engine = create_engine('mysql://localhost:1234/test', echo=True)

catalog = MetaData()
#catalog.create_all(engine)

session = sessionmaker(bind = engine)
ed = User('ed', 'Supa ed', 'password')
session.add(ed)
session.commit()

