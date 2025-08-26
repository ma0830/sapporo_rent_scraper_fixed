"""
Created on 2025/08/03
@author: 81901
"""
#main.py

from scrape_yahoo import scrape_yahoo_main, save_to_csv

if __name__ == "__main__":
    print("🚀 スクレイピング開始")
    results = scrape_yahoo_main()
    print(f"📊 取得件数: {len(results) if results else 0} 件")
    
    if results:
        save_to_csv(results)
        print("✅ 処理完了")
    else:
        print("⚠️ 取得できたデータがありません")
        
        
        