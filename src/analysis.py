"""
analysis.py: 売上分析ロジック
役割: CSVログデータを分析してグラフやチャートに加工して可視化する
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ファイルパス
LOG_FILE = "../log/vending_machine_log.csv"

def load_data(LOG_FILE):
    """分析用のデータフォーマットの下準備"""
    try:
        # ファイルを読み込み
        df = pd.read_csv(LOG_FILE)
        #　datetimeを日付形式に変換して分析用のデータフォーマットを作成
        df["datetime"] = pd.to_datetime(df["datetime"])
        # データフォーマットをを返す
        return df
    except Exception:
        return None

def get_sales_metrics(df):
    """購入金額・投入金額・返金の抽出と集計"""
    # 購入(purchase)を抽出して合計
    sales_array = np.where(df["log_type"] == "purchase", df["amount"], 0) * -1
    total_sales = np.sum(sales_array)
    
    # 投入金額(deposit)を抽出して合計
    deplogosit_array = np.where(df["log_type"] == "deposit", df["amount"], 0)
    total_deposit = np.sum(deplogosit_array)
    
    # 返金(refund)を抽出して合計
    refund_array = np.where(df["log_type"] == "refund", df["amount"], 0)
    total_refund = np.abs(np.sum(refund_array))
    
    # それぞれの合計を返す
    return total_sales, total_deposit, total_refund

def get_advanced_stats(df):
    """購入額の統計計算"""
    # 購入(purchase)を抽出してNumPyの配列に変換
    purchase_amounts = np.abs(df[df["log_type"] == "purchase"]["amount"].to_numpy())

    # 購入額が0の時は終了
    if len(purchase_amounts) == 0:
        return 0, 0, 0
    
    # 平均単価,最大単価,中央値を返す
    return np.mean(purchase_amounts), np.max(purchase_amounts), np.median(purchase_amounts)

def get_daily_sales_data(df):
    """時系列チャート用データの作成"""
    # 購入金額(purchase)の行だけ金額を抽出、それ以外を欠損値(np.nan)にして除外
    df["sales_cleaned"] = np.where(df["log_type"] == "purchase", np.abs(df["amount"]), np.nan)
    # 売上の折れ線グラフを作成
    sales_by_time = df.dropna(subset=["sales_cleaned"]).resample("D", on="datetime")["sales_cleaned"].sum()
    # 折れ線グラフを返す
    return sales_by_time

def get_item_sales_data(df):
    """商品別売上データの整形"""
    # 購入(purchase)を抽出
    purchase_only = df[df["log_type"] == "purchase"]
    # 商品別の合計額の棒グラフを作成
    sales_item = purchase_only.groupby("item")["amount"].sum().abs().sort_values(ascending=False)
    #　棒グラフを返す
    return sales_item

def create_pie_chart(sales_item):
    """売上構成比の円グラフの整形"""
    # ラベルと値を作成
    labels = sales_item.index.to_numpy()
    values = sales_item.to_numpy()
    
    # グラフの描画エリアを大きさを指定して作成
    fig, ax = plt.subplots(figsize=(5, 5))
    # ラベルと値を渡し、円グラフを作成
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    # 円グラフを返す
    return fig