import tornado.ioloop
import tornado.web
import tornado.websocket

# ルート
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        arg = self.request.arguments
        self.render('main.html')
        print(arg)


# ペン情報取得
class PenInfo(tornado.web.RequestHandler):
    def get(self):
        self.write("test")

    def post(self):
        pass


def make_app():
    return tornado.web.Application([
        # ルーティング
        (r"/", MainHandler),
        (r"/penInfo", PenInfo)
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
