#!/usr/bin/python
from __future__ import division
import subprocess
import sys
import os

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Book(Base):
  __tablename__ = "books"

  id = Column(Integer, primary_key = True) # Primary ID
  name = Column(String)   # Name of book
  stars = Column(Integer) # Sum of all votes
  votes = Column(Integer) # Total number of voters
  rating = Column(Float)  # Average rating
  author = Column(String) # Author

  def __init__(self, name, author):
    self.name = name
    self.stars = 0
    self.votes = 0
    self.rating = 0.0
    self.author = author

  def get_url(self):
    return "/book/%d" % (self.id)

  def get_rating_url(self, score):
    return "/book/%d/rate/%s" % (self.id, score)

  def add_rating(self, score):
    self.stars += vote
    self.votes += 1
    self.rating =  self.stars / self.votes
  
  def __repr__(self):
    return "%s \n\t[%d stars, %d votes, %f average rating]" % (self.name, self.stars, self.votes, self.rating)

class User(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key = True)
  full_name = Column(String)

  def __init__(self, name):
    self.full_name = name
  
  def first_name(self):
    return self.full_name.split(" ")[0]

  def __repr__(self):
    return "%s" % self.full_name

class Rating(Base):
  """A user gives a rating (0.0 to 5.0, in 0.5 increments) to a book."""
  __tablename__ = "ratings"

  id = Column(Integer, primary_key = True)
  value = Column(Float)
  creator = Column(Integer, ForeignKey('users.id'))
  book = Column(Integer, ForeignKey('books.id'))

  def __init__(self, value, creator, book):
    self.value = value
    self.creator = creator
    self.book = book

  def nice_repr(self, session):
    """A human readable representation of the Rating. We separate nice_repr and
    __repr because we may not want to keep hitting the db when we
    querying for __repr__."""
    
    creator_db = session.query(User).filter(User.id == self.creator).one()
    book_db = session.query(Book).filter(Book.id == self.book).one()

    return "User %s rated book %s a %f" % \
      (creator_db.full_name, book_db.name, self.value)
    print "Created by %s" % creator_db.full_name

  def __repr__(self):
    return "User %d rated book %d a %d." % (self.creator, self.book, self.value)

if __name__ == '__main__':
  print "Don't run this file. Instead, run ./db_shell ."
  exit(0)

print "This is the database shell."
print "For a list of all commands, type 'commands()'"

"""
DB wrapper helper class
"""

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
      for item in session.query(subclass):
        if id != None and item.id != id: continue
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
      os.unlink(self.__DB_NAME)
      print "Database destroyed."
    else:
      print "Database not destroyed."

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
      [ (4.5, new_users[0].id, new_books[0].id)
      , (2.5, new_users[0].id, new_books[1].id)
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
