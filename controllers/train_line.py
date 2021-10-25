import json
import requests
from  bs4 import BeautifulSoup

from config.config import db
from models.train import TrainLine


def fetch_all_names():
    URL = 'https://transit.yahoo.co.jp/traininfo/area/6/'
    html = requests.get(URL)
    soup = BeautifulSoup(html.content, 'html.parser')
    train_map = soup.find_all('div', class_='elmTblLstLine')
    train_name_list = []
    for train in train_map:
        train_names = train.find_all('a')
        for train_name in train_names:
            train_name_list.append(train_name.text)

    train_name_list = list(set(train_name_list))
    res_json = {'names': train_name_list}

    return json.dumps(res_json, indent=2, ensure_ascii=False)

def set_line_names():
    res = json.loads(fetch_all_names())
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