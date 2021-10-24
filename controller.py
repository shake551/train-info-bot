import requests
from bs4 import BeautifulSoup
import json


# 遅延している路線の名前と詳細のデータを取得する
def obtain_train_data():
    URL = 'https://transit.yahoo.co.jp/traininfo/area/6/'
    html = requests.get(URL)
    soup = BeautifulSoup(html.content, 'html.parser')
    train_map = soup.find('div', class_='elmTblLstLine')
    info_map = train_map.find_all('td')
    delay_info = []
    res_json = {}
    
    for i, info in enumerate(info_map):
        print(i, info)
        if i % 3 == 0:
            insert_info = {}
            line_url = info.find('a').get('href')
            line_html = requests.get(line_url)
            line_soup = BeautifulSoup(line_html.content, 'html.parser')
            line_info = line_soup.find('dd', class_='trouble')
            print('[路線情報]', line_info.text)
            insert_info['name'] = info.text
            insert_info['info'] = line_info.text[:-18].strip()
            delay_info.append(insert_info)
    
    res_json['delay_info'] = delay_info
    
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
    
    res_json = {'res':return_text}

    return json.dumps(res_json, indent=2, ensure_ascii=False)
