# TODO: pages ending with / and those that don't should go to the same place.

import os

import tornado.ioloop
import tornado.httpserver
import tornado.web

from db import DBWrapper, Book
from admin import Admin

PORT = 8888

db = None

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    sess = db.get_session()
    all_books = [b for b in sess.query(Book)]
    self.render("index.html", all_books = all_books)

  def post(self):
    new_book = self.get_argument("book_name")
    db.add_book(new_book)
    self.redirect("/")

class TopTenHandler(tornado.web.RequestHandler):
  def get(self):
    sess = db.get_session()
    top_ten_books = sess.query(Book).order_by(Book.rating)[:10]
    self.render("top-10.html", top_ten_books = top_ten_books)

class BookDetailHandler(tornado.web.RequestHandler):
  def get(self, book_id):
    sess = db.get_session()
    book = sess.query(Book).filter(Book.id == book_id).one()

    self.render("book_detail.html", book = book)


class Application(tornado.web.Application):
  def __init__(self):
    admin = Admin()

    handlers  = [ (r"/", MainHandler)
                , (r"/top-10", TopTenHandler)
                , (r"/book/([\d]+)", BookDetailHandler)
                ]

    handlers.extend(admin.get_handlers('admin'))
    print handlers

    settings = dict(
      template_path = os.path.join(os.path.dirname(__file__), "templates"),
      static_path = os.path.join(os.path.dirname(__file__), "public"),
    )

    global db
    db = DBWrapper() #initialize DB

    tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == "__main__":
  print "http://localhost:%d" % (PORT)
  server = tornado.httpserver.HTTPServer(Application())
  server.listen(PORT)
  tornado.ioloop.IOLoop.instance().start()
