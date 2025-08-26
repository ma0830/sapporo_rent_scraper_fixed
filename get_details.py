'''
Created on 2025/08/04

@author: 81901
'''
# get_details.py

import time
from selenium.webdriver.common.by import By

def get_detail_page_info(driver, url):
    detail_info = {}

    try:
        driver.get(url)
        time.sleep(2)

        try:
            built_year_element = driver.find_element(By.XPATH, '//th[text()="築年数"]/following-sibling::td')
            detail_info["築年"] = built_year_element.text.strip()
        except:
            detail_info["築年"] = "不明"

        try:
            location_element = driver.find_element(By.XPATH, '//th[text()="所在地"]/following-sibling::td')
            detail_info["所在地"] = location_element.text.strip()
        except:
            detail_info["所在地"] = "不明"

    except Exception as e:
        print(f"🔍 詳細ページの取得失敗: {e}")

    return detail_info

