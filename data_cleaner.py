'''
Created on 2025/08/05

@author: 81901
'''
#data_cleaner.py

import pandas as pd

def load_and_inspect_csv(csv_path="results.csv"):
    df = pd.read_csv(csv_path)
    
    print("▼ 先頭5件")
    print(df.head())

    print("\n▼ カラム一覧")
    print(df.columns)

    print("\n▼ データ型と件数")
    print(df.info())

    print("\n▼ 欠損値の件数")
    print(df.isnull().sum())

    return df

if __name__ == "__main__":
    load_and_inspect_csv()
