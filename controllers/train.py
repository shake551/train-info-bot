import requests
from bs4 import BeautifulSoup
import json

from config.config import db
from models.train import TrainLine


class TrainInfoAPI():
    def __init__(self):
        print('init')

    def fetch_train_data(self, option=0):
        URL = 'https://transit.yahoo.co.jp/diainfo/area/6'
        html = requests.get(URL)
        soup = BeautifulSoup(html.content, 'html.parser')
        train_map = soup.find_all('dd')
        
        if option:
            return train_map[0]
        
        train_map.pop(0)
        return train_map

    def fetch_delay_train(self):
        delay_data = self.fetch_train_data(1).find_all('a')
        delay_info = []
        res_json = {}

        for info in delay_data:
            insert_info = {}
            line_url = 'https://transit.yahoo.co.jp' + info.get('href')
            line_html = requests.get(line_url)
            line_soup = BeautifulSoup(line_html.content, 'html.parser')
            line_info = line_soup.find('dd', class_='trouble')
            print('[路線情報]', line_info.text)
            insert_info['name'] = info.find('dt').text
            insert_info['info'] = line_info.text
            delay_info.append(insert_info)
        
        res_json['delay_info'] = delay_info
        
        return json.dumps(res_json, indent=2, ensure_ascii=False)
    
    def fetch_all_names(self):
        train_data = self.fetch_train_data()
        train_name_list = []
        for train in train_data:
            train_names = train.find_all('dt')
            for train_name in train_names:
                train_name_list.append(train_name.text)

        train_name_list = list(set(train_name_list))
        res_json = {'names': train_name_list}

        return json.dumps(res_json, indent=2, ensure_ascii=False)


# クエリデータからリプライメッセージを生成する
def create_reply(query_data):
    if len(query_data) == 0:
        return_text = '現在通常運転でない路線はありません．'
    else:
        return_text = '現在通常運転ではない路線の情報をお知らせします．\n'
        for data in query_data:
            return_text += '\n<' + data.name + '>\n' + data.info + '\n'
        return_text += '\n\n通常運転でない路線は以上です．'
    
    res_json = {'reply_text':return_text}

    return json.dumps(res_json, indent=2, ensure_ascii=False)


def set_line_names():
    train_info_api = TrainInfoAPI()
    res = json.loads(train_info_api.fetch_all_names())
    line_names = res['names']

    db.session.query(TrainLine).delete()
    
    for line in line_names:
        line_data = TrainLine()
        line_data.name = line
        db.session.add(line_data)
    db.session.commit()
    
    print('[set_line_names]', res)
    
    return json.dumps({'message':'ok'}, indent=2, ensure_ascii=False)


def obtain_line_names():
    name_query = db.session.query(TrainLine).all()
    train_names = []
    for name in name_query:
        train_names.append(name.name)
    print(train_names)

    return train_names