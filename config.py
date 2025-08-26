'''
Created on 2025/08/03

@author: 81901
'''
# config.py

# 対象エリア（札幌市中央区と北区）に基づくURL（ページネーションあり）
TARGET_URLS = [
    "https://realestate.yahoo.co.jp/rent/search/?b=01&l=01&la=01&pf=01&md=01&sc=01101&page={}",  # 中央区
    "https://realestate.yahoo.co.jp/rent/search/?b=01&l=01&la=01&pf=01&md=01&sc=01102&page={}",  # 北区
]

# クロール対象の最大ページ数（仮に5ページまで）
MAX_PAGES = 5

# Seleniumでの待機時間設定（必要に応じて調整）
IMPLICIT_WAIT = 10
HEADLESS = False  # Trueにするとブラウザ非表示で動作します

SEARCH_URLS = [
   "https://realestate.yahoo.co.jp/rent/search/?b=01&l=01&la=01&pf=01&md=01&sc=01101&page={}",  # 中央区
   "https://realestate.yahoo.co.jp/rent/search/?b=01&l=01&la=01&pf=01&md=01&sc=01102&page={}",  # 北区
]

URLS = SEARCH_URLS  # または URLS = TARGET_URLS にしてもよい


