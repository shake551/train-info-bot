from controller import obtain_train_data
import json
from models.train import TrainData
import requests
from  bs4 import BeautifulSoup



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

json_data = json.dumps(res_json, indent=2, ensure_ascii=False)
print(json_data)
