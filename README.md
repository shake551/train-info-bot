# train-info

## 概要
電車の運行情報をスクレイピングして、LINEで通知してくれるボットです

こちらのQRコードから友達登録できます．IDは`@262hlvbr`です．

<img width="150" alt="スクリーンショット 2022-03-18 23 08 00" src="https://user-images.githubusercontent.com/73379887/159018370-cd1c307e-5059-4eee-ad4d-92f9519b6e91.png">

#### 詳細は[こちら](https://shake551.github.io/portfolio/train.html)からご確認ください

## 動機
電車の運行情報を通知してくれるアプリ等は存在しますが、「アプリのダウンロード」「通知のON」というハードルがあり、使いにくいと感じていました．
そこで、多くの人が通知をONにしているであろうLINEを使って通知しようと考え開発しました．

## 機能
* 通常運転でない路線の一覧表示(リッチメニューから選択できる)
* 送信された名前にヒットする路線の運行状況を通知する
* スクレイピング([こちらのサイト](https://transit.yahoo.co.jp/traininfo/area/6/)から運行状況をスクレイピングしています)

## 使用技術
* Python
* flask
* Postgresql
* heroku
* LINE Developers
