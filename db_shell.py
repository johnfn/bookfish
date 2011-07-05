#!/usr/bin/python
from __future__ import division
import subprocess
import sys
import os

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from models import *
from settings import *
from util import *

if __name__ == '__main__':
  print "Don't run this file. Instead, run ./db_shell ."
  exit(0)

print "This is the database shell."
print "For a list of all commands, type 'commands()'"

"""
DB wrapper helper class
"""

class DBShell:
  def __init__(self):
    self.Session = Util.make_sessionmaker(Base)

  def __get_session(self):
    return self.Session()

  def inspect(self, inspect_class = None, id = None):
    """([type, [id]]) 
    Inspect the database.
    If type is given, only inspect elements of that type. 
    If id is also given, only inspect the element of provided type with 
    given ID."""
    session = self.__get_session()

    for subclass in Base.__subclasses__():
      if inspect_class != None and subclass != inspect_class: continue
      print subclass.__name__
      for item in session.query(subclass).order_by(subclass.id):
        if id != None and item.id != id: continue
        print "[%d]" % item.id,
        if "nice_repr" in dir(item):
          print item.nice_repr(session)
        else:
          print item

      print ""

  def destroy(self):
    """()
    Deletes the entire database. Be careful!"""
    print "Destroy the database. Are you sure? Y/n"
    result = raw_input()
    if result == "Y":
      os.unlink(Settings.db_name)
      print "Database destroyed."
    else:
      print "Database not destroyed."

  def get(self, obj_type, obj_id):
    """(obj_type, obj_id)
    Gets the unique object with specified id and type."""
    session = self.__get_session()

    return session.query(obj_type).filter(obj_type.id == obj_id).one()

  def populate(self):
    """()
    Inserts sample data into the database."""

    def make_test_data(session, model_type, args_array):
      """ Helper method for creating many testing models on the fly. """
      new_data = [ model_type(*args) for args in args_array ]

      print "Adding %ss to the database" % model_type.__name__,
      for item in new_data: 
        sys.stdout.write(".") # Only way to not write trailing space
        session.add(item)
      print " Done"
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
      [ (session, 4.5, new_users[0].id, new_books[0].id)
      , (session, 2.5, new_users[0].id, new_books[1].id)
      ])

  # TODO: Take this out of here.
  def add_book(self, book_name):
    """ TODO: Remove this method"""
    session = self.__get_session()
    session.add(Book(book_name))
    session.commit()

d = DBShell()

help_text = ""

# Get all public methods of DBShell
methods = [f for f in dir(DBShell) if "__" not in f] 

def make_bold(s):
  return "\033[1m" + s + "\033[0;0m"

# Add all public methods to globals for shell convenience.
for method in methods:
  globals()[method] = getattr(d, method)

  help_text += make_bold(method) + "%s\n" % ((getattr(d, method).__doc__))

def commands():
  print help_text
