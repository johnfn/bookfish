# TODO: pages ending with / and those that don't should go to the same place.

import os

import tornado.ioloop
import tornado.httpserver
import tornado.web
import tornado.auth

from db import DBWrapper, Book, User
from admin import Admin

PORT = 8888

db = None

class BaseHandler(tornado.web.RequestHandler):
  def get_current_user(self):
    user_json = self.get_secure_cookie("user")
    if not user_json: return None
    user_object = tornado.escape.json_decode(user_json)

    # Add the user to the db if he isn't in there already.

    sess = db.get_session()
    user_db = sess.query(User).filter(User.full_name == user_object['name'])

    if user_db.count() == 0:
      sess.add(User(user_object['name']))
      sess.commit()
      user_db = sess.query(User).filter(User.full_name == user_object['name'])

    return user_db.one()

class MainHandler(BaseHandler):
  def get(self):
    print self.get_current_user()

    sess = db.get_session()
    all_books = [b for b in sess.query(Book)]
    
    self.render("index.html", all_books = all_books)

  def post(self):
    new_book = self.get_argument("book_name")
    db.add_book(new_book)
    self.redirect("/")

class AuthLoginHandler(BaseHandler, tornado.auth.GoogleMixin):
  @tornado.web.asynchronous
  def get(self):
    if self.get_argument("openid.mode", None):
      self.get_authenticated_user(self.async_callback(self._on_auth))
      return
    self.authenticate_redirect(ax_attrs=["name"])

  def _on_auth(self, user):
    if not user:
      raise tornado.web.HTTPError(500, "Google auth failed")

    self.set_secure_cookie("user", tornado.escape.json_encode(user))
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

class BookRatingHandler(tornado.web.RequestHandler):
  def get(self, book_id, rating):
    rating = float(rating)
    if not 0 <= rating <= 5:
      raise #TODO: More robust errors than just crashing.

    print "Rating book %s %s" % (book_id, rating)

    user = self.get_current_user()
    if not user:
      raise #TODO: Again...
      #TODO: Stuff like this is great for testing.


class Application(tornado.web.Application):
  def __init__(self):
    admin = Admin()

    handlers  = [ (r"/", MainHandler)
                , (r"/top-10", TopTenHandler)
                , (r"/book/([\d]+)", BookDetailHandler)
                , (r"/login", AuthLoginHandler)
                , (r'/book/([\d]+)/rate/([\d\.]+)', BookRatingHandler)
                ]

    handlers.extend(admin.get_handlers('admin'))

    # TODO: Change cookie_secret
    settings = dict(
      cookie_secret="43oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
      login_url="/auth/login",
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
