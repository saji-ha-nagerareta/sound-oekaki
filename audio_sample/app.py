import tornado.ioloop
import tornado.web
import tornado.websocket
import json
import os


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        arg = self.request.arguments
        self.render('main.html')
        print(arg)


# ペン情報取得
class PenInfoHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("test")

    def post(self):
        print(self.request.headers)
        
        dump = open("tmp.webm", 'wb')
        dump.write(self.request.body)
        dump.close()
    #   print(self.request.body)


def make_app():
    BASE_DIR = os.path.dirname(__file__)
    return tornado.web.Application([
        (r"/pen", PenInfoHandler),
    ],
        template_path=os.path.join(BASE_DIR, "templates")
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("server running")
    tornado.ioloop.IOLoop.current().start()
