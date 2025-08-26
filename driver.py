'''
Created on 2025/08/03

@author: 81901
'''
# driver.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from config import IMPLICIT_WAIT, HEADLESS

def get_driver():
    # オプション設定
    options = Options()
    if HEADLESS:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")

    # 必要に応じてオプション追加（ウィンドウサイズやUser-Agentなど）
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")

    # ChromeDriverのパス（パスが通っていれば省略可）
    service = Service()

    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(IMPLICIT_WAIT)
    return driver

def create_driver():
    options = webdriver.ChromeOptions()
    if HEADLESS:
        options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(IMPLICIT_WAIT)
    return driver

