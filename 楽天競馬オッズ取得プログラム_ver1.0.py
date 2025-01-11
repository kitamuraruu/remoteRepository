#戻す
#概要：楽天競馬のオッズ情報を取得し、jsonファイルとして出力する。
#内容：楽天競馬のオッズページ（トップ）から競馬場のリンクを取得し、
#      競馬場のリンクからレースのリンクを取得し、
#      レースのリンクから馬の情報を1頭ずつ取得する。
#      取得した情報をjsonファイルとして出力する。

#補足：リンクが存在するURLのみ取得する。
#      取得する情報は、競馬場ID、場所名、レースNo、馬番号、馬、単勝オッズ
#      数値で取れるべき項目が数値でない場合は、Nullを返す。
#      例）馬番号が文字列の場合、Nullを返す。
#ver1.0
#2025/01/05

#ライブラリのインポート----------------------------------------------------------------------------------------------------------------------------
import requests
from bs4 import BeautifulSoup
import re
import json
import datetime


#関数------------------------------------------------------------------------------------------------------------------------------------------------
#int型に安全に変換できなければ、Nullを返す
def safe_int(value):
    try:
        return int(value)
    except ValueError:
        return None
    
#float型に安全に変換できなければ、Nullを返す
def safe_float(value):
    try:
        return float(value)
    except ValueError:
        return None


#定数定義----------------------------------------------------------------------------------------------------------------------------
#楽天競馬のオッズページ（トップ）URLの前半部分
urlOdsTop = 'https://keiba.rakuten.co.jp/odds/tanfuku/RACEID/'

#出力するファイル名の決定
outPath = "C:\\作業フォルダ\\"
fileType = ".json"
fileName = '楽天競馬'


#メイン処理----------------------------------------------------------------------------------------------------------------------------
#今日の日付を取得
today = datetime.datetime.now()
#yyyymmdd形式に変換
today = today.strftime('%Y%m%d')
#強制的に日付を指定する場合は、以下のコメントを外して日付を指定する
today = '20250105'

#レース情報を格納するリスト
raceDataAll = []

#末尾に本日の日付と固定値を追加
urlJoin = urlOdsTop + today + '0000000000'

# 情報を取得
responseOdsTop = requests.get(urlJoin)

# レスポンスのHTMLを解析
soupOdsTop = BeautifulSoup(responseOdsTop.text, 'html.parser')

# メインとなる情報を抽出
soupOdsMains = soupOdsTop.find(class_="raceTrack")

#soupOdsMainsの中から特定のhref属性を取得しsoupOdsUrlsに格納
soupOdsUrls = soupOdsMains.find_all(href=re.compile(urlOdsTop))

# 競馬場のリンクのテキスト情報を取得しリストに格納
raceTrackLinks = [soupOdsUrl.attrs['href'] for soupOdsUrl in soupOdsUrls]

#取得したリンクの数（=今日開催する競馬場の数）だけ繰り返し
for raceTrackLink in raceTrackLinks:

    #競馬場のリンク情報を取得する
    responseRaceTrack = requests.get(raceTrackLink)

    # レスポンスのHTMLを解析
    soupRaceTracks = BeautifulSoup(responseRaceTrack.text, 'html.parser')

    # メインとなる情報を抽出
    soupRaceTrackMains = soupRaceTracks.find("tbody",class_="raceState")

    #soupRaceTrackMainsの中からhref属性を取得しsoupRaceTrackUrlsに格納
    soupRaceTrackUrls = soupRaceTrackMains.find_all(href=re.compile(urlOdsTop))

    # レースのリンクのテキスト情報を取得しリストに格納
    raceCardLinks = [soupRaceTrackUrl.attrs['href'] for soupRaceTrackUrl in soupRaceTrackUrls]

    #取得したリンクの数（=レースの数だけ）繰り返し
    for raceCardLink in raceCardLinks:

        #レースのリンク情報を取得する
        responseRaceCard = requests.get(raceCardLink)

        # レスポンスのHTMLを解析
        soupRaceCards = BeautifulSoup(responseRaceCard.text, 'html.parser')

        # メインとなる情報を抽出
        soupRaceCardMains = soupRaceCards.find("table", {"class": "dataTable"})

        # main_table内のすべての行を取得
        main_rows = soupRaceCardMains.find_all("tr")

        #競馬場のIDを取得する　URLの後ろから２桁目から１０桁目までを取得
        raceId = raceCardLink[-10:-2]

        #競馬場の名前を取得する
        getValue = ""
        getValue=soupRaceCards.select('#raceInfomation > div > div.raceTitle > div > span.racePlace')
        racePlace=getValue[0].contents[0]

        #レースNumberを取得する
        #数値化するために文字列から数値に変換
        getValue = ""
        getValue=soupRaceCards.select('#raceInfomation > div > div.raceTitle > div > span.raceNumber > span')
        raceNumber=getValue[0].contents[0]
        raceNumber = safe_int(raceNumber)

        #取得した行の数（=走る馬の数だけ）繰り返し　※先頭行はヘッダー行のため、１からスタート
        for i,row in enumerate(main_rows[1:],start=1):
            #馬の名前を取得する
            getValue = ""
            getValue=row.find_all(class_='horse')
            horseName=getValue[0].text.strip()

            #馬の番号を取得する
            #数値化するために文字列から数値に変換
            getValue = ""
            getValue=row.find_all(class_='number')
            horseNumber=getValue[0].text.strip()
            horseNumber = safe_int(horseNumber)


            #単勝オッズを取得する
            #数値化するために文字列から数値に変換
            getValue = ""
            getValue=row.find_all(class_='oddsWin')
            odds=getValue[0].text.strip()
            odds = safe_float(odds)


            # レース情報を一時的に格納する辞書型リスト
            raceData=[]
            raceData = {
                        "競馬場ID":raceId,
                        "場所名":racePlace,
                        "レースNo":raceNumber,
                        "馬番号":horseNumber,
                        "馬":horseName,
                        "単勝オッズ":odds
                        }
            
            #raceDataをraceDataAllに追加
            raceDataAll.append(raceData)

#jsonファイルとして出力
with open(outPath + fileName + fileType, 'w') as f:
    json.dump(raceDataAll,f,indent=4,ensure_ascii=False)

print("終了")

