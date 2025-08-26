'''
Created on 2025/08/03

@author: 81901
'''
# scraper/property_scraper.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_properties(driver):
    """全ページをめくりながら物件情報を取得する"""
    properties = []

    while True:
        # ページの読み込みを待つ（物件一覧が表示されるまで）
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cassetteitem"))
            )
        except:
            print("物件情報の読み込みに失敗しました。")
            break

        # 物件情報をすべて取得
        items = driver.find_elements(By.CLASS_NAME, "cassetteitem")
        for item in items:
            try:
                title = item.find_element(By.CLASS_NAME, "cassetteitem_content-title").text
                address = item.find_element(By.CLASS_NAME, "cassetteitem_detail-col1").text
                rent = item.find_element(By.CLASS_NAME, "cassetteitem_price--rent").text
                management_fee = item.find_element(By.CLASS_NAME, "cassetteitem_price--administration").text
                deposit = item.find_element(By.CLASS_NAME, "cassetteitem_price--deposit").text
                gratuity = item.find_element(By.CLASS_NAME, "cassetteitem_price--gratuity").text

                properties.append({
                    "title": title,
                    "address": address,
                    "rent": rent,
                    "management_fee": management_fee,
                    "deposit": deposit,
                    "gratuity": gratuity
                })

            except Exception as e:
                print(f"物件情報の抽出時にエラーが発生しました: {e}")
                continue

        # 「次へ」ボタンを探してクリック（なければ終了）
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "li.pagination__item--next > a")
            if next_button.is_enabled():
                next_button.click()
                time.sleep(2)  # ページ遷移を待つ
            else:
                break
        except:
            print("次のページが見つからなかったか、すべてのページを処理しました。")
            break

    return properties
