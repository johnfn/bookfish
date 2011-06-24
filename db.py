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

	def __init__(self, name):
		self.name = name
		self.stars = 0
		self.votes = 0
		self.rating = 0.0
	
	def add_rating(self, score):
		self.stars += vote
		self.votes += 1
		self.rating =  self.stars / self.votes
	
	def __repr__(self):
		return self.name

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
		for book in session.query(Book).order_by(Book.id):
			print book

	def destroy(self):
		os.unlink(self.DB_NAME)

	def populate(self):
		""" Insert some stuff into the database """
		session = self.get_session()

		session.add(Book('Harry Potter and the Chamber of Derp'))
		session.add(Book('Harry Potter and the Goblet of Herp'))

		session.commit()
	
	def add_book(self, book_name):
		session = self.get_session()
		session.add(Book(book_name))
		session.commit()

if __name__ == "__main__":
	db = DBWrapper()

	if len(sys.argv) == 1:
		print "Usage: "
		print "./db.py [-options]"
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
			db.populate()
			print "Done"
		elif command == "I":
			db.inspect()
		elif command == "D":
			print "Drop all tables. Are you sure? Y/n"
			result = raw_input()
			if result == "Y":
				db.destroy()

