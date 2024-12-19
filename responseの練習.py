import requests

url:str='https://news.yahoo.co.jp/'

response = requests.get(url)

#responseの中身を表示
#print(response.text[:200])

#responseのステータスコードを表示
print("ステータスコード")
print(response.status_code)

#responseのヘッダーを表示
print("ヘッダー")
print(response.headers)

#responseのエンコーディングを表示
print("エンコーディング")
print(response.encoding)

#responseのコンテンツを表示
print("コンテンツ")
print(response.content[:100])

#responseのテキストを表示
print("テキスト")
print(response.text[:100])


#responseのクッキーを表示
print("クッキー")
print(response.cookies[:100])

