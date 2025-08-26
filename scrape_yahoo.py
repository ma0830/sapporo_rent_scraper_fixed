"""
Yahoo不動産の賃貸物件情報をスクレイピングするプログラム

このファイルの主な機能：
1. Yahoo不動産のページから物件一覧を取得
2. 各物件の詳細情報（賃料、間取り、住所など）を抽出
3. 取得したデータをCSVファイルに保存

Created on 2025/08/02
@author: 81901
"""
#scrape_yahoo.py

# 必要なライブラリをインポート
from selenium.webdriver.common.by import By  # Seleniumでページ要素を指定する
from driver import create_driver  # ブラウザを起動するカスタム関数
import csv  # CSVファイル操作用
import time  # 待機時間設定用

def get_listings(url, driver):
    """
    指定されたURLから物件一覧ページを取得する関数
    
    Args:
        url (str): 取得したいページのURL
        driver: Seleniumのwebdriver（ブラウザ操作用）
    
    Returns:
        list: 物件要素のリスト
    """
    print(f"\n🔍 {url} を取得中...")
    driver.get(url)  # URLにアクセス
    time.sleep(2)  # ページ読み込み待ち（2秒）
    # 物件の部屋情報が含まれる要素をすべて取得
    return driver.find_elements(By.CSS_SELECTOR, ".ListCassetteRoom__inner")

def parse_cassette_item(item, parent_info=None):
    """
    個別の物件（部屋）の詳細情報を抽出する関数
    
    Args:
        item: Seleniumで取得した物件要素
        parent_info (dict): 建物全体の情報（建物名、住所など）
    
    Returns:
        dict: 物件の詳細情報の辞書（賃料、間取り、住所など）
    """
    try:
        # === 1. 物件名（建物名）の取得 ===
        title = ""
        # 建物情報が親から渡されている場合はそれを使用
        if parent_info and 'building_name' in parent_info:
            title = parent_info['building_name']
        else:
            # 渡されていない場合は、親要素を遡って建物名を探す
            try:
                parent_element = item
                # 最大10階層上まで探して建物名を見つける
                for _ in range(10):
                    try:
                        parent_element = parent_element.find_element(By.XPATH, "..")
                        title_elements = parent_element.find_elements(By.CSS_SELECTOR, ".ListCassette__ttl__link")
                        if title_elements:
                            title = title_elements[0].text.strip()
                            # プレースホルダーでなければ使用
                            if title and "物件名が入ります" not in title:
                                break
                    except:
                        continue
            except:
                pass
        
        # === 2. 物件名が取得できない場合のフォールバック処理 ===
        if not title or "物件名が入ります" in title:
            try:
                # 詳細ページのリンクから物件IDを取得して識別に使用
                detail_link = item.find_element(By.CSS_SELECTOR, "a[href*='/rent/detail/']").get_attribute("href")
                property_id = detail_link.split("/rent/detail/")[-1].split("/")[0]
                title = f"物件ID_{property_id}"
            except:
                # 最後の手段: 価格と階数を組み合わせて識別名を作成
                try:
                    floor = item.find_element(By.CSS_SELECTOR, ".ListCassetteRoom__block--floor").text.strip()
                    price = item.find_element(By.CSS_SELECTOR, ".ListCassetteRoom__dtl__price").text.strip().split()[0]
                    title = f"{price}_{floor}"
                except:
                    title = "物件名不明"
        
        # === 3. 基本的な部屋情報を取得 ===
        # 階数を取得（例: "10階"）
        floor = item.find_element(By.CSS_SELECTOR, ".ListCassetteRoom__block--floor").text.strip()
        
        # 賃料情報を取得（例: "6.2万円 管理費等 6,000円"）
        price_block = item.find_element(By.CSS_SELECTOR, ".ListCassetteRoom__dtl__price").text.strip()

        # === 4. 間取り・面積の情報を取得 ===
        layout_elements = item.find_elements(By.CSS_SELECTOR, ".ListCassetteRoom__dtl__layout")
        # 1つ目の要素: 間取り（例: "1LDK"）
        layout = layout_elements[0].text.strip() if len(layout_elements) > 0 else ""
        # 2つ目の要素: 面積（例: "40.34m²"）
        area = layout_elements[1].text.strip() if len(layout_elements) > 1 else ""

        # === 5. 敷金・礼金の情報を取得 ===
        shiki, rei = "不明", "不明"  # 初期値設定
        deposit_blocks = item.find_elements(By.CSS_SELECTOR, ".ListCassetteRoom__dtl__deposit")
        # 各敷金・礼金ブロックを確認
        for block in deposit_blocks:
            try:
                # ラベル（"敷"や"礼"）を取得
                label = block.find_element(By.CSS_SELECTOR, ".ListCassetteRoom__dtl__deposit__tag").text.strip()
                # 金額部分を取得（ラベルを除いた部分）
                value = block.text.replace(label, "").strip()
                if "敷" in label:
                    shiki = value  # 敷金
                elif "礼" in label:
                    rei = value    # 礼金
            except:
                continue

        # === 6. 物件詳細ページへのリンクを取得 ===
        try:
            # 「詳細を見る」リンクを探す
            link_elem = item.find_element(By.CSS_SELECTOR, "a.ListCassetteRoom__textLink")
            href = link_elem.get_attribute("href")
            # 相対URLの場合は絶対URLに変換
            link = href if href.startswith("http") else "https://realestate.yahoo.co.jp" + href
        except:
            try:
                # 代替方法: 詳細ページへのリンクを含む要素を探す
                all_links = item.find_elements(By.CSS_SELECTOR, "a[href*='/rent/detail/']")
                if all_links:
                    href = all_links[0].get_attribute("href")
                    link = href if href.startswith("http") else "https://realestate.yahoo.co.jp" + href
                else:
                    link = "リンクなし"
            except:
                link = "リンクなし"

        # === 7. 物件のスコア計算（お得度の指標） ===
        score = 0
        # 敷金なしの場合は+1点
        if "なし" in shiki:
            score += 1
        # 礼金なしの場合は+1点  
        if "なし" in rei:
            score += 1

        # === 8. 建物レベルの情報を取得（建物全体に共通の情報） ===
        # parent_infoから建物の共通情報を取得（効率的）
        location = parent_info.get('location', '不明') if parent_info else "不明"      # 所在地（区）
        address = parent_info.get('address', '不明') if parent_info else "不明"        # 完全な住所
        access = parent_info.get('access', '不明') if parent_info else "不明"          # アクセス（駅・徒歩時間）
        built_year = parent_info.get('built_year', '不明') if parent_info else "不明"  # 築年数・階数

        # === 9. すべての情報を辞書形式で返す ===
        return {
            "title": title,              # 物件名（建物名）
            "price_block": price_block,  # 賃料情報
            "floor": floor,              # 階数
            "layout": layout,            # 間取り（1LDK等）
            "area": area,                # 面積（㎡）
            "location": location,        # 所在地（区）
            "address": address,          # 完全な住所
            "access": access,            # アクセス（駅・徒歩時間）
            "built_year": built_year,    # 築年数・階数
            "shiki": shiki,              # 敷金
            "rei": rei,                  # 礼金
            "link": link,                # 詳細ページのURL
            "score": score               # お得度スコア
        }

    except Exception as e:
        # エラーが発生した場合はエラー内容を表示して None を返す
        print("❌ パースエラー:", e)
        return None

def save_to_csv(data):
    """
    取得した物件データをCSVファイルに保存する関数
    
    Args:
        data (list): 物件情報のリスト（辞書のリスト）
    
    Returns:
        None: CSVファイルを作成するだけ
    """
    # データが空の場合は保存しない
    if not data:
        print("⚠️ 保存するデータがありません。")
        return

    # スコアの高い順（お得な物件順）にソート
    sorted_data = sorted(data, key=lambda x: x.get("score", 0), reverse=True)
    
    # CSVファイルのカラム順を定義
    keys = ["title", "price_block", "floor", "layout", "area", "location", "address",
        "access", "built_year", "shiki", "rei", "link", "score"]

    # CSVファイルを作成してデータを書き込み
    with open("results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)  # CSVライターを作成
        writer.writeheader()  # ヘッダー行（カラム名）を書き込み
        # 各物件のデータを一行ずつ書き込み
        for row in sorted_data:
            writer.writerow(row)

    print(f"✅ CSVファイル results.csv に保存しました。（{len(data)} 件）")

def scrape_yahoo_main():
    """
    Yahoo不動産の物件情報をスクレイピングするメイン関数
    複数のURLを処理して、すべての物件情報を収集する
    
    Returns:
        list: すべての物件情報のリスト
    """
    # スクレイピングするページのURLリスト
    urls = [
        "https://realestate.yahoo.co.jp/rent/search/01/01/01101/",  # 中央区 1ページ目
        "https://realestate.yahoo.co.jp/rent/search/01/01/01102/",  # 北区 1ページ目
    ]
    all_results = []  # すべての物件情報を格納するリスト

    # Webブラウザを起動（Chromeブラウザを使用）
    driver = create_driver()

    # 各URLを順番に処理
    for url in urls:
        try:
            print(f"🔍 URL処理中: {url}")
            driver.get(url)  # 指定URLにアクセス
            time.sleep(2)    # ページ読み込み待ち
            
            print(f"✅ ページ読み込み完了")
            
            # === 建物グループごとに処理 ===
            # Yahoo不動産では同じ建物の部屋がグループ化されている
            building_groups = driver.find_elements(By.CSS_SELECTOR, ".ListBukken__item")
            print(f"🏢 建物数: {len(building_groups)} 件")
            
            processed_count = 0  # 処理した物件数のカウンター
            
            # 各建物を順番に処理
            for building in building_groups:
                try:
                    # === 建物名を取得 ===
                    building_name = ""
                    try:
                        building_name_elem = building.find_element(By.CSS_SELECTOR, ".ListCassette__ttl__link")
                        building_name = building_name_elem.text.strip()
                    except:
                        building_name = "建物名不明"
                    
                    # === 建物レベルの共通情報を取得（効率化のため） ===
                    # 初期値設定
                    building_address = "不明"      # 住所
                    building_location = "不明"     # 所在地（区）
                    building_access = "不明"       # アクセス情報
                    building_built_year = "不明"   # 築年数
                    
                    try:
                        # 建物の詳細情報を含むテキスト要素をすべて取得
                        location_elements = building.find_elements(By.CSS_SELECTOR, ".ListCassette__txt")
                        
                        # 住所情報を探す
                        for elem in location_elements:
                            text = elem.text.strip()
                            if "北海道札幌市" in text:
                                building_address = text
                                # 「北海道札幌市」を除いて区名だけ取得
                                building_location = text.replace("北海道札幌市", "").split()[0] if text else "不明"
                                break
                        
                        # アクセス情報（駅名・徒歩時間）を探す
                        access_parts = []
                        for elem in location_elements:
                            text = elem.text.strip()
                            # 「駅/」と「徒歩」を含むテキストをアクセス情報として収集
                            if "駅/" in text and "徒歩" in text:
                                access_parts.append(text)
                        # 最初の2つの駅情報を連結
                        building_access = " / ".join(access_parts[:2]) if access_parts else "不明"
                        
                        # 築年数・階建情報を探す
                        for elem in location_elements:
                            text = elem.text.strip()
                            if "築" in text and ("年" in text or "階建" in text):
                                building_built_year = text
                                break
                    except:
                        pass  # エラーが発生しても続行
                    
                    # === この建物の各部屋を処理 ===
                    rooms = building.find_elements(By.CSS_SELECTOR, ".ListCassetteRoom__item")
                    for room in rooms:
                        try:
                            # 「さらに物件を見る」ボタンはスキップ（物件情報ではないため）
                            if "さらに物件を見る" in room.text:
                                continue
                                
                            # 建物の共通情報を辞書形式でまとめる
                            parent_info = {
                                'building_name': building_name,       # 建物名
                                'address': building_address,          # 住所
                                'location': building_location,        # 所在地（区）
                                'access': building_access,            # アクセス情報
                                'built_year': building_built_year     # 築年数
                            }
                            
                            # 個別の部屋情報を解析
                            parsed = parse_cassette_item(room, parent_info)
                            if parsed:  # 解析が成功した場合
                                all_results.append(parsed)  # 結果リストに追加
                                processed_count += 1        # カウンターを増やす
                                
                            # 5件ごとに進捗を表示
                            if processed_count % 5 == 0:
                                print(f"  ▶️ 処理済み: {processed_count} 件")
                                
                        except Exception as e:
                            print(f"⚠️ 部屋の解析エラー: {e}")
                            continue  # エラーが発生しても次の部屋を処理
                            
                except Exception as e:
                    print(f"⚠️ 建物の解析エラー: {e}")
                    continue  # エラーが発生しても次の建物を処理
                    
            print(f"✅ 合計処理件数: {processed_count} 件")
                    
        except Exception as e:
            print(f"❌ URL処理エラー: {e}")
            continue  # エラーが発生しても次のURLを処理

    # ブラウザを閉じる
    driver.quit()
    print(f"🎉 全体で {len(all_results)} 件のデータを取得しました")
    return all_results  # 取得したすべての物件情報を返す



