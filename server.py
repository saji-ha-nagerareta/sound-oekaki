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
class PenInfoHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("test")

    def post(self):
        pass


# 描画情報ブロードキャスト
class broadcastDrawInfoHandler(tornado.websocket.WebSocketHandler):
    # 接続者
    waiters = set()

    # すべての通信を受け入れる設定
    def check_origin(self, origin):
        return True

    def open(self, *args, **kwargs):
        self.waiters.add(self)
        print(args[0])  # ルームID
        # Todo:過去キャンバス送信

    def on_message(self, message):
        print(message)
        print("roomID:" + self.path_args[0])
        for waiter in self.waiters:
            if waiter == self:
                continue
            waiter.write_message(message)  # デフォルトでバイナリはfalseなのでbinaryを送るときは変える

    def on_close(self):
        self.waiters.remove(self)


# 部屋情報
class RoomHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("room index")

    def post(self):
        self.write("create room")


# テスト用ページ
class test(tornado.web.RequestHandler):
    def get(self):
        self.render('WStest.html')


def make_app():
    return tornado.web.Application([
        # ルーティング
        (r"/", MainHandler),
        (r"/pen", PenInfoHandler),
        (r'/soundOekaki/(.*)', broadcastDrawInfoHandler),
        (r'/room', RoomHandler),
        (r'/test', test)
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
