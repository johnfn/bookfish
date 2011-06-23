from __future__ import division

import os

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

"""
Models
"""

Base = declarative_base()

class Book(Base):
	__tablename__ = "books"

	id = Column(Integer, primary_key = True)
	name = Column(String)
	stars = Column(Integer)
	votes = Column(Integer)
	rating = Column(Float)

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
	"""Run a loop to do some simple database commands"""

	db = DBWrapper()

	def get_command():
		print "Commands:" 
		print "[D]rop all tables"
		print "[P]opulate database"
		print "[I]nspect database"
		print "[Q]uit"
		print

		return raw_input()

	while True:
		command = get_command().upper()

		if command == "Q":
			print "Quit"
			break
		elif command == "P":
			print "Populating database...",
			db.populate()
			print "Done"
		elif command == "I":
			db.inspect()
		elif command == "D":
			print "Drop all tables. Are you sure? n/Y"
			result = raw_input()
			if result == "Y":
				db.destroy()

