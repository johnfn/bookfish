import tornado
#from module import Module

class AdminHandler(tornado.web.RequestHandler):
  def get(self):
    self.write("Hey")

class Admin:
  def get_handlers(self, namespace):
    return [('/%s' % namespace, AdminHandler)]
