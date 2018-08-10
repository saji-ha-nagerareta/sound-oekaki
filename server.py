import tornado.ioloop
import tornado.web
import tornado.websocket
import json
import os

# 各ルーム接続者
ws_con = {}


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
    global ws_con

    # すべての通信を受け入れる設定
    def check_origin(self, origin):
        return True

    def open(self, *args, **kwargs):
        if (args[0] not in ws_con):
            ws_con[args[0]] = [self]
        else:
            ws_con[args[0]].append(self)
        print("[OPEN] room:" + args[0] + "   Member:" + str(len(ws_con[args[0]])))  # ルームID
        # Todo:過去キャンバス送信

    def on_message(self, message):
        print(message)
        print("roomID:" + self.path_args[0])
        for waiter in ws_con[self.path_args[0]]:
            if waiter == self:
                continue
            waiter.write_message(message)  # デフォルトでバイナリはfalseなのでbinaryを送るときは変える

    def on_close(self):
        ws_con[self.path_args[0]].remove(self)
        print("[CLOSE] room:" + self.path_args[0] + "   Member:" + str(len(ws_con[self.path_args[0]])))


# 部屋情報
class RoomHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(json.dumps(ws_con))

    def post(self):
        self.write("create room")


# テスト用ページ
class test(tornado.web.RequestHandler):
    def get(self, *args):
        #loader = tornado.web.template.Loader(b"templates")
        #self.render(loader.load(b"WStest.html").generate(roomname=args[0]))
        self.render("WStest.html",roomname=args[0])


def make_app():
    BASE_DIR = os.path.dirname(__file__)
    return tornado.web.Application([
        # ルーティング
        (r"/", MainHandler),
        (r"/pen", PenInfoHandler),
        (r'/soundOekaki/(.*)', broadcastDrawInfoHandler),
        (r'/room', RoomHandler),
        (r'/test/(.*)', test)
    ],
        template_path = os.path.join(BASE_DIR, "templates")
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
