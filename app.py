'''
Created on 2025/08/08

@author: 81901
'''

# app.py

import streamlit as st
import pandas as pd
import os
import re
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

# CSS調整
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
  background-color: #e0f7f7;
  background-image: url('https://www.transparenttextures.com/patterns/waves.png');
  background-repeat: repeat;
  background-size: 200px 200px;
  background-position: center;
  min-height: 100vh;
  padding: 0 20px 40px 20px;
  box-sizing: border-box;
  position: relative;
}

/* ブラウザ上下に00b0aeのグラデーション枠 */
[data-testid="stAppViewContainer"]::before,
[data-testid="stAppViewContainer"]::after {
  content: "";
  position: fixed;
  left: 0;
  right: 0;
  height: 40px;
  pointer-events: none;
  z-index: 9999;
}
[data-testid="stAppViewContainer"]::before {
  top: 0;
  background: linear-gradient(to bottom, #00b0ae, transparent);
}
[data-testid="stAppViewContainer"]::after {
  bottom: 0;
  background: linear-gradient(to top, #00b0ae, transparent);
}

/* タイトル全体枠 */
h1, h2, h3 {
  font-family: "Yu Gothic UI", "游ゴシック体", "Yu Gothic", "ヒラギノ角ゴ Pro W3", "Hiragino Kaku Gothic Pro", sans-serif;
  color: #007f7d;
  text-align: center;
  margin-bottom: 0.2em;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-shadow:
    1px 1px 2px rgba(0, 176, 174, 0.4);
}

/* タイトル装飾（h1用）*/
h1 {

  
  border-bottom: 4px solid #00b0ae;
  padding-bottom: 0.3em;
  margin-bottom: 1rem;
}

/* サブタイトル枠（h2用） */
h2 {
  background: #e0f7f7;
  border-left: 6px solid #00b0ae;
  color: #006e6c;
  padding: 12px 20px;
  border-radius: 8px;
  box-shadow: 2px 2px 8px rgba(0,176,174,0.15);
  margin-top: 0.2rem;
  margin-bottom: 1rem;
  font-weight: 600;
  letter-spacing: 0.04em;
}

/* サブテキスト用の段落 */
.subtext {
  font-family: "Yu Gothic UI", "游ゴシック体", "Yu Gothic", sans-serif;
  font-size: 0.9rem;
  color: #005f5d;
  max-width: 720px;
  margin: 0 auto 2rem auto;
  line-height: 1.5;
  text-align: center;
  padding: 0 10px;
}

/* アコーディオンのタイトル（st.expanderのボタン風） */
[data-testid="stExpander"] > div > button {
  font-family: "Yu Gothic UI", "游ゴシック体", "Yu Gothic", sans-serif;
  background: #00b0ae;
  color: white;
  font-weight: 700;
  font-size: 1rem;
  border-radius: 8px;
  padding: 10px 18px;
  border: none;
  box-shadow: 0 3px 8px rgba(0, 176, 174, 0.5);
  cursor: pointer;
  transition: background-color 0.3s ease;
  width: 100%;
  text-align: left;
}

[data-testid="stExpander"] > div > button:hover {
  background-color: #00928f;
}

/* アコーディオン内テキスト */
[data-testid="stExpander"] > div > div {
  background-color: #e0f7f7;
  border-left: 5px solid #00b0ae;
  padding: 15px 25px;
  border-radius: 0 0 10px 10px;
  color: #004d4b;
  font-family: "Yu Gothic UI", "游ゴシック体", "Yu Gothic", sans-serif;
  line-height: 1.6;
  margin-top: 0;
  box-shadow: inset 2px 2px 8px rgba(0,176,174,0.1);
}

/* テーブルスタイル */
.stDataFrame table {
  border-collapse: collapse !important;
  width: 100% !important;
  font-family: "Yu Gothic UI", "游ゴシック体", "Yu Gothic", sans-serif;
  font-size: 0.95rem;
  color: #004d4b;
  box-shadow: 0 0 15px rgba(0,176,174,0.15);
  border-radius: 10px;
  overflow: hidden;
}

.stDataFrame thead tr {
  background: linear-gradient(90deg, #00b0ae, #00928f);
  color: #fff !important;
  font-weight: 700;
}

.stDataFrame tbody tr:nth-child(even) {
  background-color: #d9f0f0 !important;
}

.stDataFrame tbody tr:hover {
  background-color: #a0d9d9 !important;
}

/* リンク */
a, a:visited {
  color: #007f7d;
  text-decoration: underline;
}
a:hover {
  color: #004d4b;
}

/* スクロールバー（Webkit系） */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: #e0f7f7;
}
::-webkit-scrollbar-thumb {
  background: #00b0ae;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #00928f;
}
</style>
""", unsafe_allow_html=True)


# CSS調整ここまで


# 環境変数読み込み
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def parse_rent_to_manken(price_block: str):
    """価格表記から「万円」単位の数値（float）を返す。解析できない場合は None を返す。"""
    if not isinstance(price_block, str):
        return None
    s = price_block.replace('\u3000', ' ').replace(',', '')  # 全角スペースを半角に、カンマ削除

    m = re.search(r"(\d+(?:\.\d+)?)\s*万円", s)
    if m:
        try:
            return float(m.group(1))
        except Exception:
            return None

    m2 = re.search(r"(\d+(?:\.\d+)?)\s*円", s)
    if m2:
        try:
            yen = float(m2.group(1))
            return yen / 10000.0
        except Exception:
            return None

    m3 = re.search(r"(\d+(?:\.\d+)?)\s*万\b", s)
    if m3:
        try:
            return float(m3.group(1))
        except Exception:
            return None

    return None


def safe_get(row, key):
    return row.get(key, '') if key in row.index else ''


def calculate_score(row):
    try:
        score = 0

        layout = str(safe_get(row, 'layout')).upper()
        if any(ldk in layout for ldk in ['3LDK', '4LDK', '5LDK', '6LDK', '7LDK', '8LDK', '9LDK', '10LDK']):
            score += 3
        elif '2LDK' in layout:
            score += 2

        area_str = str(safe_get(row, 'area')).replace('m²', '').replace('㎡', '').strip()
        try:
            area = float(re.sub(r"[^0-9.]", "", area_str)) if area_str else 0
            if area >= 55:
                score += 3
            elif area >= 50:
                score += 2
        except Exception:
            pass

        rent_manken = parse_rent_to_manken(str(safe_get(row, 'price_block')))
        if rent_manken is not None:
            if rent_manken <= 6:
                score += 3
            elif rent_manken <= 8:
                score += 2

        access = str(safe_get(row, 'access')).strip()
        walk_time_match = re.search(r'徒歩\s*(\d+)分', access)
        if walk_time_match:
            try:
                walk_time = int(walk_time_match.group(1))
                if walk_time <= 5:
                    score += 3
                elif walk_time <= 10:
                    score += 2
            except Exception:
                pass

        built_year_str = str(safe_get(row, 'built_year')).strip()
        built_year_match = re.search(r'築\s*(\d+)年', built_year_str)
        if built_year_match:
            try:
                built_year = int(built_year_match.group(1))
                if built_year <= 5:
                    score += 3
                elif built_year <= 10:
                    score += 2
            except Exception:
                pass

        specified_stations_plus_3 = ['札幌', 'さっぽろ', '北12条', '北18条', '大通', 'すすきの', '中島公園', '幌平橋']
        specified_stations_plus_2 = ['西11丁目', '西18丁目', 'バスセンター駅', '菊水']
        matched_station_score = 0
        for station in specified_stations_plus_3:
            if station in access:
                matched_station_score = 3
                break
        if matched_station_score == 0:
            for station in specified_stations_plus_2:
                if station in access:
                    matched_station_score = 2
                    break
        score += matched_station_score

        if 'なし' in str(safe_get(row, 'shiki')):
            score += 1
        if 'なし' in str(safe_get(row, 'rei')):
            score += 1

        return score
    except Exception:
        return 0


async def generate_comment_async(property_info, semaphore=None):
    if client is None:
        return "(OpenAI APIキー未設定のためコメント生成スキップ)"

    if semaphore is None:
        semaphore = asyncio.Semaphore(1)

    async with semaphore:
        try:
            prompt = f"以下の物件情報について、魅力的な短いコメントを日本語で作成してください。\n\n{property_info}"
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "あなたは不動産アドバイザーです。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=60
            )
            try:
                text = response.choices[0].message.content.strip()
                return text
            except Exception:
                return "(生成結果の解析に失敗)"
        except Exception as e:
            return f"コメント生成エラー: {e}"


async def generate_comments_for_df(df, concurrency=1, delay_sec=0.6):
    semaphore = asyncio.Semaphore(concurrency)
    comments = []

    for _, row in df.iterrows():
        property_info = (
            f"タイトル: {safe_get(row, 'title')}\n"
            f"間取り: {safe_get(row, 'layout')}\n"
            f"面積: {safe_get(row, 'area')}\n"
            f"賃料: {safe_get(row, 'price_block')}\n"
            f"アクセス: {safe_get(row, 'access')}\n"
            f"築年数: {safe_get(row, 'built_year')}"
        )
        comment = await generate_comment_async(property_info, semaphore=semaphore)
        comments.append(comment)
        try:
            await asyncio.sleep(delay_sec)
        except Exception:
            pass

    return comments


st.set_page_config(page_title="札幌賃貸物件 スコアリング", layout="wide")

st.title("札幌賃貸物件 スコアリング")

csv_path = "results.csv"

if os.path.exists(csv_path):
    try:
        df = pd.read_csv(csv_path, dtype=str, encoding='utf-8', on_bad_lines='skip')

        required_cols = ['layout', 'area', 'price_block', 'access', 'built_year', 'shiki', 'rei']
        if 'price_block' not in df.columns:
            for alt in ['price', '賃料', '家賃']:
                if alt in df.columns:
                    df['price_block'] = df[alt].astype(str)
                    break
        for col in required_cols:
            if col not in df.columns:
                df[col] = ''

        df['score'] = df.apply(calculate_score, axis=1)
        df['extracted_rent'] = df['price_block'].apply(parse_rent_to_manken)

        excluded_layouts = ['ワンルーム', '1K', '1LDK', '1DK', '2K', '2DK']
        df_filtered = df[~df['layout'].isin(excluded_layouts) & df['extracted_rent'].notna() & (df['extracted_rent'] <= 8.5)].copy()

        need_relax = False
        if len(df_filtered) < 10:
            need_relax = True

            df_relax1 = df[~df['layout'].isin(excluded_layouts) & df['extracted_rent'].notna() & (df['extracted_rent'] <= 9.5)].copy()
            df_filtered = pd.concat([df_filtered, df_relax1]).drop_duplicates().head(10)

        if len(df_filtered) < 10:
            df_relax2 = df[df['extracted_rent'].notna() & (df['extracted_rent'] <= 9.5)].copy()
            df_filtered = pd.concat([df_filtered, df_relax2]).drop_duplicates().head(10)

        if len(df_filtered) < 10:
            df_relax3 = df[df['extracted_rent'].notna()].copy()
            df_relax3 = df_relax3.sort_values(by='score', ascending=False)
            df_filtered = pd.concat([df_filtered, df_relax3]).drop_duplicates().head(10)

        df_sorted = df_filtered.sort_values(by='score', ascending=False).reset_index(drop=True)
        df_sorted['順位'] = df_sorted.index + 1

        st.subheader("""スコア上位10件 (おすすめポイントコメント付き)
        情報取得に数分かかる場合があります...""")
        
        with st.expander("物件の条件は..."):
            st.markdown("""
            以下の方が希望する条件を想定しています。
            
            30代女性：  
            子供が一人、正社員でフルタイムで働く。  
            会社は札幌駅近郊にあり、通勤30分圏内に住みたい。  

            ・札幌市中央区か北区の物件  
            ・間取りはできれば２LDK以上、45㎡以上の広さであること  
            ・駅徒歩10分以内  
            ・築年数は10年以下  
            ・家賃は安いに越したことはない  
            ・敷金礼金もないに越したことはない  

            これらの項目を重視して独自にスコアリングした結果を表示します。  
            """)

        top10 = df_sorted.head(10).copy()

        display_cols = ['順位', 'title', 'price_block', 'floor', 'layout', 'area', 'access', 'built_year', 'shiki', 'rei', 'score', 'AIコメント', 'link']
        for col in display_cols:
            if col not in top10.columns:
                top10[col] = ''

        if OPENAI_API_KEY:
            try:
                try:
                    comments = asyncio.run(generate_comments_for_df(top10, concurrency=1, delay_sec=0.7))
                except RuntimeError:
                    st.warning("非同期実行が現在の環境で利用できないため、コメント生成をスキップします。")
                    comments = ["(実行環境の制約でコメント生成スキップ)" for _ in range(len(top10))]
                except Exception as e:
                    st.warning(f"コメント生成中にエラーが発生しました: {e}")
                    comments = [f"コメント生成エラー: {e}" for _ in range(len(top10))]
            except Exception as e:
                comments = [f"コメント生成エラー: {e}" for _ in range(len(top10))]
        else:
            comments = ["(OpenAI APIキー未設定)" for _ in range(len(top10))]

        top10['AIコメント'] = comments

        display_cols_present = [col for col in display_cols if col in top10.columns]
        st.dataframe(top10[display_cols_present], hide_index=True)

        if need_relax:
            st.warning(f"条件に合う物件は {len(df_filtered)} 件です。条件通りの物件が10件未満の場合は条件を段階的に緩和して10件表示しています。")

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")

else:
    st.error(f"CSVファイル '{csv_path}' が見つかりません。配置場所とファイル名を確認してください。")

# ---------- end of file ----------









