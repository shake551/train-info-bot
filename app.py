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
from controller import obtain_train_data


line_bot_api = LineBotApi(os.environ.get('LINEAPI'))
handler = WebhookHandler(os.environ.get('HANDLER'))


TRAIN_NAME = [
    # JR西日本
    '大阪環状線', 'JRゆめ咲線', 'JR宝塚線', '琵琶湖線', 'JR京都線', '湖西線', '草津線', '嵯峨野線', '学研都市線', 'JR東西線', 'JR神戸線', '阪和線', '紀勢本線', '羽衣線', '大和路線', '関西本線', '奈良線', '桜井線', '和歌山線', '関西空港線', '和田岬線', 'きのくに線', '加古川線', '播但線', '舞鶴線', '小浜線', '福知山線', '山陰本線', 'おおさか東線',
    # 近畿日本鉄道
    '近鉄大阪線', '近鉄奈良線', '近鉄けいはんな線', '近鉄京都線', '近鉄橿原線', '近鉄天理線', '近鉄信貴線', '近鉄生駒線', '近鉄田原本線', '近鉄南大阪線', '近鉄道明寺線', '近鉄御所線', '近鉄吉野線', '近鉄長野線',
    # 阪急電鉄
    '阪急京都本線', '阪急伊丹線', '阪急今津線', '阪急甲陽線', '阪急神戸本線', '阪急宝塚本線', '阪急箕面線', '阪急千里線', '阪急嵐山線',
    # 大阪メトロ
    'ニュートラム', '大阪メトロ御堂筋線', '大阪メトロ谷町線', '大阪メトロ四つ橋線', '大阪メトロ中央線', '大阪メトロ千日前線', '大阪メトロ堺筋線', '大阪メトロ長堀鶴見緑地線', '大阪メトロ今里筋線',
    # 南海電鉄
    '南海本線', '南海空港線', '南海高師浜線', '南海多奈川線', '南海加太線', '南海和歌山港線', '南海高野線', '南海汐見橋線',
    # 京阪電鉄
    '京阪本線・中之島線', '京阪交野線', '京阪宇治線', '京阪京津線', '京阪石山坂本線',
    # 阪神電鉄
    '阪神本線', '阪神なんば線', '阪神武庫川線', '阪神高速線',
    # 神戸電鉄
    '神戸電鉄有馬・三田線', '神戸電鉄公園都市線', '神戸電鉄栗生線',
    # 山陽電鉄
    '山陽電鉄本線', '山陽電鉄網干線',
    # ウィーラートレインズ
    '京都丹後鉄道宮福線', '京都丹後鉄道宮舞線・宮豊線',
    # 神戸新交通
    'ポートライナー', '六甲ライナー',
    # 神戸市交通局
    '神戸市営西神・山手線・北神線', '神戸市営海岸線',
    # 京都市交通局
    '京都市営烏丸線', '京都市営東西線',
    # 能勢電鉄
    '能勢電鉄線',
    # 大阪モノレール
    '大阪モノレール線',
    # 北条鉄道
    '北条鉄道線',
    # 信楽高原鐵道
    '信楽高原鐵道線',
    # 和歌山電鐵
    '和歌山電鐵貴志川線',
    # 京福電鉄
    '嵐電',
    # 紀州鉄道
    '紀州鉄道線',
    # 水間鉄道
    '水間鉄道線',
    # 近江鉄道
    '近江鉄道線',
    # 阪堺電気軌道
    '阪堺電気軌道線',
    # 叡山電鉄
    '叡山電鉄線',
    # 北大阪急行電鉄
    '北大阪急行線',
    # 泉北高速鉄道
    '泉北高速鉄道線',
    # 伊賀鉄道
    '伊賀鉄道線']


def set_delay_data():
    res = json.loads(obtain_train_data())
    delay_info = res['delay_info']
    # 一旦データを全て消す
    db.session.query(TrainData).delete()
    
    for i in range(len(delay_info)):
        new_info = TrainData()
        new_info.name = delay_info['name']
        new_info.info = delay_info['info']
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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_name = event.message.text
    name_list = [x for x in TRAIN_NAME if line_name in x]
    if line_name == 'トラブル':
        all_data = TrainData.query.all()
        if len(all_data) == 0:
            return_text = '現在通常運転でない路線はありません．'
        else:
            return_text = '現在通常運転ではない路線の情報をお知らせします．\n'
            for data in all_data:
                return_text += '\n<' + data.name + '>\n' + data.info + '\n'
            return_text += '\n\n通常運転でない路線は以上です．'
    elif len(name_list) != 0:
        length = len(name_list)
        return_text = '運行状況をお知らせします．\n'
        for i in range(length):
            data = db.session.query(TrainData).filter(TrainData.name == name_list[i]).first()
            if (data):
                return_text += '\n<' + data.name + '>\n' + data.info + '\n'
            else:
                return_text += '\n<' + str(name_list[i]) + '>\n   通常運転\n'
                
        return_text += '\n\nお問い合わせの路線の運行状況は以上の通りです．'
    else:
        if line_name == 'リスト':
            return_text = '対応している路線の一覧\n'
            for name in TRAIN_NAME:
                return_text += '\n' + str(name)
        else:
            return_text = 'データにそのような路線はありません．\n運行情報が知りたい路線の名前を送信してください．\nどの路線に対応しているか知りたい場合は「リスト」と送信すると一覧が表示されます．\nまた、「トラブル」と送信すると通常運転ではない路線をお知らせします．'
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=return_text))


if __name__ == "__main__":
    app.run()
