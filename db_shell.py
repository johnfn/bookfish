#!/usr/bin/python
from __future__ import division
import subprocess
import sys
import os

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from db import Book, User, Rating

if __name__ == '__main__':
  print "Don't run this file. Instead, run ./db_shell ."
  exit(0)

print "This is the database shell."
print "For a list of all commands, type 'commands()'"

"""
DB wrapper helper class
"""

Base = declarative_base()


class DBShell:
  def __init__(self, in_memory = False):
    self.__DB_NAME = "db"
    if in_memory: 
      self.__db = create_engine('sqlite:///:memory:') #create in memory database
    else:
      self.__db = create_engine('sqlite:///%s' % self.__DB_NAME)

    self.__db.echo = False #Don't spam SQL to console

    Base.metadata.bind = self.__db
    Base.metadata.create_all(self.__db) #Create all tables

    self.Session = sessionmaker(bind = self.__db) #Session object type

  def __get_session(self):
    return self.Session()

  def inspect(self):
    """Print out the entire database in human readable form."""
    session = self.__get_session()

    for subclass in Base.__subclasses__():
      print subclass.__name__ + "s"
      for item in session.query(subclass):
        if "nice_repr" in dir(item):
          print item.nice_repr(session)
        else:
          print item

      print ""

  def destroy(self):
    """Deletes the entire database. Be careful!"""
    os.unlink(self.__DB_NAME)

  def populate(self):
    """ Inserts sample data into the database."""

    def make_test_data(session, model_type, args_array):
      """ Helper method for creating many testing models on the fly. """
      new_data = [ model_type(*args) for args in args_array ]

      for item in new_data: session.add(item)
      session.commit()

      return new_data

    session = self.__get_session()

    new_users = make_test_data(session, User, 
      [ ("Herp Derper",) # (Trailing comma required to distinguish tuple)
      , ("Derpina Tester",)
      ])

    new_books = make_test_data(session, Book,
      [ ("Harry Potter and the Chamber of Derp", "J. K. Lol")
      , ("Harry Potter and the Goblet of Herp", "J. K. Lol")
      ])

    new_ratings = make_test_data(session, Rating,
      [ (4.5, new_users[0].id, new_books[0].id)
      , (2.5, new_users[0].id, new_books[1].id)
      ])

  # TODO: Take this out of here.
  def add_book(self, book_name):
    session = self.__get_session()
    session.add(Book(book_name))
    session.commit()

"""
if __name__ == "__main__":
  db = DBShell()

  if len(sys.argv) == 1:
    print "Usage: "
    print "./db.py [-option]"
    print 
    print "Options:"
    print "  -p : Populate database with data"
    print "  -i : Inspect database"
    print "  -d : Drop all tables"
    print 
  
  for arg in sys.argv[1:]:
    command = arg.upper()
    if command[0] == "-": command = command[1:]

    if command == "P":
      print "Populating database...",
      try:
        db.populate()
      except:
        print "Failed populating database. I recommend deleting all data and trying again."
        exit(0)
      print "Done"
    elif command == "I":
      db.inspect()
    elif command == "D":
      print "Drop all tables. Are you sure? Y/n"
      result = raw_input()
      if result == "Y":
        db.destroy()
"""

d = DBShell()

help_text = ""

# Get all public methods of DBShell
methods = [f for f in dir(DBShell) if "__" not in f] 

# Add all public methods to globals for shell convenience.
for method in methods:
  globals()[method] = getattr(d, method)

  help_text += "%s() : \n\t%s\n" % (method, (getattr(d, method).__doc__))

def commands():
  print help_text
