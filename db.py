#!/usr/bin/python

from __future__ import division

import os
import sys

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

"""
Models
"""

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

"""
DB wrapper helper class
"""

class DBWrapper:
  def __init__(self, in_memory = False):
    self.DB_NAME = "db"
    if in_memory: 
      self.db = create_engine('sqlite:///:memory:') #create in memory database
    else:
      self.db = create_engine('sqlite:///%s' % self.DB_NAME)

    self.db.echo = False #Don't spam SQL to console

    Base.metadata.bind = self.db
    Base.metadata.create_all(self.db) #Create all tables

    self.Session = sessionmaker(bind = self.db) #Session object type

  def get_session(self):
    return self.Session()

  def inspect(self):
    session = self.get_session()

    for subclass in Base.__subclasses__():
      print subclass.__name__ + "s"
      for item in session.query(subclass):
        if "nice_repr" in dir(item):
          print item.nice_repr(session)
        else:
          print item

      print ""

  def destroy(self):
    os.unlink(self.DB_NAME)

  def populate(self):
    """ Insert some stuff into the database """

    def make_test_data(session, model_type, args_array):
      """ Helper method for creating many testing models on the fly. """
      new_data = [ model_type(*args) for args in args_array ]

      for item in new_data: session.add(item)
      session.commit()

      return new_data

    session = self.get_session()

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

  def add_book(self, book_name):
    session = self.get_session()
    session.add(Book(book_name))
    session.commit()

if __name__ == "__main__":
  db = DBWrapper()

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

