'''
Created on 2025/08/10

@author: 81901
'''
# generate_comments.py

import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# .envの読み込み
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEYが.envに設定されていません")

client = OpenAI(api_key=api_key)

# スコアリング定義
def score_listing(row):
    score = 0

    # 間取り
    if "3LDK" in row["間取り"] or "4LDK" in row["間取り"] or "5LDK" in row["間取り"]:
        score += 3
    elif "2LDK" in row["間取り"]:
        score += 2

    # 面積（数値抽出して㎡比較）
    try:
        m2 = float(str(row["面積"]).replace("m2", "").replace("㎡", "").strip())
        if m2 >= 50:
            score += 3
        elif m2 >= 45:
            score += 2
    except:
        pass

    # 賃料（管理費込みでなく賃料部分だけで判定）
    try:
        rent_str = str(row["賃料"]).replace("万円", "").strip()
        rent_val = float(rent_str)
        if rent_val <= 6:
            score += 3
        elif rent_val <= 8:
            score += 2
    except:
        pass

    # 徒歩（最短時間）
    try:
        if "徒歩" in row["アクセス"]:
            times = []
            parts = str(row["アクセス"]).split("/")
            for p in parts:
                if "徒歩" in p:
                    t = p.split("徒歩")[1].replace("分", "").strip()
                    times.append(int(t))
            if times:
                min_time = min(times)
                if min_time <= 5:
                    score += 3
                elif min_time <= 10:
                    score += 2
    except:
        pass

    return score


# コメント生成
def generate_comment(row):
    prompt = f"""
あなたは不動産アドバイザーです。
以下の物件情報をもとに短いコメントを作成してください。
ユーザーは物件を探している一般の人です。
過剰な営業トークではなく、魅力や注意点を簡潔に述べてください。

物件名: {row['物件名']}
間取り: {row['間取り']}
面積: {row['面積']}
賃料: {row['賃料']}
アクセス: {row['アクセス']}
築年数など: {row['築年数・階数']}
総合スコア: {row['スコア']}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    # 講師添削コードで出力されたCSVを読み込み
    input_csv = "output.csv"  # ファイル名は講師コードの出力名に合わせて変更
    df = pd.read_csv(input_csv)

    # スコア計算
    df["スコア"] = df.apply(score_listing, axis=1)

    # コメント生成
    df["コメント"] = df.apply(generate_comment, axis=1)

    # 保存
    output_csv = "scored_with_comments.csv"
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"✅ コメント付きCSVを保存しました: {output_csv}")
