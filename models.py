#!/usr/bin/python

#TODO: rename to models.py

from __future__ import division

import os
import sys

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, relationship, backref
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
  ratings = relationship("Rating", backref='book') #TODO

  def __init__(self, name, author):
    self.name = name
    self.stars = 0
    self.votes = 0
    self.rating = 0.0
    self.author = author

  # Assume that someone is going to call commit afterwards...
  def calculate_rating(self):
    self.rating = self.stars / self.votes

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
  ratings = relationship("Rating", backref='user')

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
  creator_id = Column(Integer, ForeignKey('users.id'))
  book_id = Column(Integer, ForeignKey('books.id'))

  def __init__(self, session, value, creator, book):
    book_db = session.query(Book).filter(Book.id == book).one()

    # Check to see if user has rated this book already.
    # TODO fix
    old_rating = session.query(Rating).filter(Rating.creator_id == creator).filter(Rating.book_id == book)

    if old_rating.count() > 0:
      old_rating = old_rating.one()
      book_db.stars -= old_rating.value
      old_rating.value = value
      book_db.stars += value
      book_db.calculate_rating()
      session.commit()
      return

    self.value = value
    self.creator_id = creator
    self.book_id = book
    book_db.stars += value
    book_db.votes += 1
    book_db.calculate_rating()

  def book_name(self):
    return self.book.name

  def nice_repr(self, session):
    """A human readable representation of the Rating. We separate nice_repr and
    __repr because we may not want to keep hitting the db when we
    querying for __repr__."""
    
    creator_db = session.query(User).filter(User.id == self.creator_id).one()
    book_db = session.query(Book).filter(Book.id == self.book.id).one()

    return "User %s rated book %s a %f" % \
      (creator_db.full_name, book_db.name, self.value)
    print "Created by %s" % creator_db.full_name

  def __repr__(self):
    return "User %d rated book %d a %d." % (self.creator_id, self.book, self.value)
