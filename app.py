from flask import Flask, request, abort, render_template
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup

import os
import json
from dotenv import load_dotenv
load_dotenv()

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

from config.config import db, app
from models.train import TrainData
from controllers.train import TrainInfoAPI
from controllers.train import create_reply
from controllers.train import obtain_line_names


line_bot_api = LineBotApi(os.environ.get('LINEAPI'))
handler = WebhookHandler(os.environ.get('HANDLER'))

URL = 'https://transit.yahoo.co.jp/diainfo/area/6'
TRAIN_NAME = obtain_line_names()


def set_delay_data():
    train_info_api = TrainInfoAPI(URL)
    res = json.loads(train_info_api.fetch_delay_train())
    delay_info = res['delay_info']
    # 一旦データを全て消す
    db.session.query(TrainData).delete()
    
    for data in delay_info:
        new_info = TrainData()
        new_info.name = data['name']
        new_info.info = data['info']
        db.session.add(new_info)
    db.session.commit()
    
    return json.dumps({'message':'ok'}, indent=2, ensure_ascii=False)


@app.route('/')
def test():
    return 'hello flask'


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# LINEbotにメッセージが来たときの処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_name = event.message.text
    name_list = [x for x in TRAIN_NAME if line_name in x]
    if line_name == 'トラブル':
        query_data = TrainData.query.all()
        res = json.loads(create_reply(query_data))
        reply_text = res['reply_text']

    elif len(name_list) != 0:
        length = len(name_list)
        reply_text = '運行状況をお知らせします．\n'
        for i in range(length):
            data = db.session.query(TrainData).filter(TrainData.name == name_list[i]).first()
            if (data):
                reply_text += '\n<' + data.name + '>\n' + data.info + '\n'
            else:
                reply_text += '\n<' + str(name_list[i]) + '>\n   通常運転\n'
                
        reply_text += '\n\nお問い合わせの路線の運行状況は以上の通りです．'

    elif line_name == 'リスト':
        reply_text = '対応している路線の一覧\n'
        for name in TRAIN_NAME:
            reply_text += '\n' + str(name)

    else:
        reply_text = 'データにそのような路線はありません．\n運行情報が知りたい路線の名前を送信してください．\nどの路線に対応しているか知りたい場合は「リスト」と送信すると一覧が表示されます．\nまた、「トラブル」と送信すると通常運転ではない路線をお知らせします．'
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text))


if __name__ == "__main__":
    app.run()
