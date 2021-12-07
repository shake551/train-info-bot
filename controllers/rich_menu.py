from linebot import (
    LineBotApi,
)
from linebot.models import (
    RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds, MessageAction
)

import os
from dotenv import load_dotenv
load_dotenv()


class LineBotRichMenu():
    def __init__(self):
        self.line_bot_api = LineBotApi(os.environ.get('LINEAPI'))

    # リッチメニュー作成
    def create(self):
        rich_menu_to_create = RichMenu(
        size=RichMenuSize(width=800, height=500),
        selected=True,
        name="train",
        chat_bar_text="Tap here",
        areas=[RichMenuArea(
            bounds=RichMenuBounds(x=0, y=0, width=2500, height=1562),
            action=MessageAction(label='トラブル', text='トラブル'))]
        )
        rich_menu_id = self.line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

        # リッチメニューに画像を追加
        with open('img/trouble.png', 'rb') as f:
            self.line_bot_api.set_rich_menu_image(rich_menu_id, 'image/png', f)

        # リッチメニューをデフォルトに設定
        self.line_bot_api.set_default_rich_menu(rich_menu_id)
        
        print(rich_menu_id)

    # すでにあるリッチメニューをすべて削除
    def delete_all(self):
        rich_menu_list = self.line_bot_api.get_rich_menu_list()
        for rich_menu in rich_menu_list:
            print(rich_menu.rich_menu_id)
            self.line_bot_api.delete_rich_menu(rich_menu.rich_menu_id)