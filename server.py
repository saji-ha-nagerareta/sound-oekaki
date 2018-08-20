#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import tornado.websocket
import json
import os
import uuid
import cv2
import base64

from audio2pen import acoustic_feature, generatePen

from time import sleep

# CONST
TEMP_DIR = "./tmp/"

# 各ルーム接続者
ws_con = {}

defaultRoomID = "room1234"
userNum = 0

def getRoomList():
    RoomInfo = {}
    for roomName, connections in ws_con.items():
        RoomInfo[roomName] = len(connections)
    return RoomInfo

# ルート
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        global userNum
        arg = self.request.arguments
        userNum += 1
        self.render('index.html',PeopleNum = userNum)
        print(arg)

# ペン情報取得
class PenInfoHandler(tornado.web.RequestHandler):
    def get(self):
        img = cv2.imread("./static/brush2.png", cv2.IMREAD_UNCHANGED)
       # cv2.imshow("test",img)
        #cv2.waitKey(0)
        result, img_png = cv2.imencode(".png", img)
        self.write({"data":base64.b64encode(img_png).decode('utf-8')})

    def post(self):
        print(self.request.headers)
        print(self.request.body)

        # 仮実装。Ajaxで送られてきていることを想定

        # 音声のファイル出力
        if not os.path.exists(TEMP_DIR):
            os.mkdir(TEMP_DIR)

        dump_path = TEMP_DIR + uuid.uuid4().hex
        print(dump_path)

        with open(dump_path, "wb") as f:
            f.write(self.request.body)
        print("Audio File Output.")

        # ブラシ生成
        brush_path = dump_path + '.png'
        feature = acoustic_feature.extract(dump_path)
        img = generatePen.generateBrush(feature)
        cv2.imwrite(brush_path, img)

        # 生成されたブラシ画像の返却
        with open(brush_path, "rb") as f:
            mime_type = "image/png"
            b64_data = base64.b64encode(f.read()).decode('utf-8')

            self.write(
                {
                    "data": "data:{}; base64, {}".format(mime_type, b64_data)
                }
            )



# 描画情報ブロードキャスト
class broadcastDrawInfoHandler(tornado.websocket.WebSocketHandler):
    # 接続者
    global ws_con

    # すべての通信を受け入れる設定
    def check_origin(self, origin):
        return True

    def open(self, *args, **kwargs):
        global userNum
        if (args[0] not in ws_con):
            ws_con[args[0]] = [self]
        else:
            ws_con[args[0]].append(self)
        print("[OPEN] room:" + args[0] + "   Member:" + str(userNum))  # ルームID
        initMessage = {"action": "ID",
                       "payload": {"id": uuid.uuid4().hex}
                       }
        self.write_message(initMessage)

        #人数変化
        enterNumMessage = {"action": "ENTER_USER",
                           "payload": {
                               "num": userNum
                           }}
        for waiter in ws_con[self.path_args[0]]:
            if waiter == self:
                continue
            waiter.write_message(enterNumMessage)
        # Todo:過去キャンバス送信

    def on_message(self, message):
        if "SEND_BRUSH" in message:
            print("roomID:" + self.path_args[0] + "    msg:" + message)

        for waiter in ws_con[self.path_args[0]]:
            if waiter == self:
                continue
            waiter.write_message(message)  # デフォルトでバイナリはfalseなのでbinaryを送るときは変える

    def on_close(self):
        global userNum
        userNum -= 1
        ws_con[self.path_args[0]].remove(self)
        print("[CLOSE] room:" + self.path_args[0] + "   Member:" + str(userNum))

        # 人数変化
        enterNumMessage = {"action": "ENTER_USER",
                           "payload": {
                               "num": userNum
                           }}
        for waiter in ws_con[self.path_args[0]]:
            if waiter == self:
                continue
            waiter.write_message(enterNumMessage)



# 部屋情報
class RoomHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(getRoomList())

    def post(self):
        self.write("create room")


# テスト用ページ
class test(tornado.web.RequestHandler):
    def get(self, *args):
        self.render("WStest.html", roomname=args[0])


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
        template_path=os.path.join(BASE_DIR, "templates"),
        static_path=os.path.join(BASE_DIR, "static")
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("server running")
    tornado.ioloop.IOLoop.current().start()
