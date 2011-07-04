from settings import *
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

class Util:
  @staticmethod
  def make_sessionmaker(base, in_memory = False):
    __DB_NAME = Settings.db_name
    if in_memory: 
      __db = create_engine('sqlite:///:memory:') #create in memory database
    else:
      __db = create_engine('sqlite:///%s' % __DB_NAME)

    __db.echo = False #Don't spam SQL to console

    base.metadata.bind = __db
    base.metadata.create_all(__db) #Create all tables

    Session = sessionmaker(bind = __db) #Session object type
    return Session
