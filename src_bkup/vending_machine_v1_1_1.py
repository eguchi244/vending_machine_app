"""
自販機アプリ

このアプリはStreamlitを使用した自販機シミュレーターの
フロントエンドとロジックを制御します。
"""

import streamlit as st
import time

# ==========================================
# 定数（Constants / Config）の初期化
# ==========================================
### 商品一覧の設定
DRINK_MENU = {"Water": 100, "Tea": 120, "Cola": 150, "Monster": 200}
### 金種のリスト（自販機で使えるものに限定）
BILL_TYPES = [10, 50, 100 ,500, 1000, 5000, 10000]

# ==========================================
# 状態管理（Session State）の初期化
# ==========================================
# 合計金額の状態の初期化（状態保持）
if "total_money" not in st.session_state:
    st.session_state.total_money = 0

# ==========================================
# メソッド定義
# ==========================================

# 
# 表示用メソッド（UI）
# ==========================================
def display_sidebar():
    """
    サイドバーのUIとロジックを処理する
    ロジック：お金の受け取り、お金の返却、残金の表示
    """
    st.sidebar.header("💰 コイン投入口")
    
    # --- お金の受け取り ---
    selected_money = st.sidebar.selectbox("投入する金額を選択", BILL_TYPES)
    if st.sidebar.button("投入"):
        st.session_state.total_money += selected_money
        st.rerun()

    # --- お金の返却 ---
    if st.sidebar.button("返却"):
        if st.session_state.total_money > 0:
            st.toast(f"💰 お釣りは {st.session_state.total_money} 円です。")
            st.session_state.total_money = 0
            st.rerun()
    
    st.sidebar.divider()

    # --- 残金の表示 ---
    st.sidebar.metric("現在の投入金額", f"{st.session_state.total_money}円")

def display_drink_menu(drinks: dict[str, int]):
    """ 
    メインUIの商品一覧をグリッド表示する
    
    Args:
        drinks (dict[str, int]): 商品の一覧の辞書
    """

    st.write("### 商品ラインナップ")

    # 商品一覧を表示
    cols = st.columns(len(drinks))
    for i, (name, price) in enumerate(drinks.items()):
        cols[i].metric(label=name, value=f"{price}円")   

     
    # # 上記はこの機能をPysonicな書き方でスマートに記述したもの
    # # 商品名のリストを作る
    # cols = st.columns(len(drinks))
    # names = list(drinks.keys())

    # # 商品名のリストを表示する
    # for i in range(len(names)):
    #     name = names[i]
    #     price = drinks[name]
    #     # 商品一覧をの名前と価格をstの指標形式（metric）形式で表示する
    #     cols[i].metric(label=name, value=f"{price}円") 
    
# 
# ロジック（計算・判定）
# ==========================================

def process_drinks_buy(selected: str, drinks: dict[str, int]):
    """
    商品の購入処理
    投入金額と商品金額の比較結果と商品選択状態を判定してメッセージを表示する
    お釣りの計算をする

    Args:
        selected (str): 選択された商品の名前
        drinks (dict[str, int]): 商品の一覧の辞書
    """
    # --- 投入金額の存在確認 ---
    current_money = st.session_state.total_money
    if current_money == 0:
        st.error("お金が投入されていません。サイドバーから投入してください。")
        return

    # --- 商品の存在確認 ---
    if selected == "-- 選択してください --":
    # if selected == "-- 選択してください --" and current_money > 0:
        # 商品が選択されてない場合 -> 警告メッセージ
        st.warning("商品を選択してください。")
        return
    
    # 商品価格を取得
    price = drinks[selected]

    # --- 購入判定とお釣り計算 ---
    # 金額が不足してる場合 -> エラーメッセージ
    if current_money < price:
        st.error(f"金額が不足しています。")
    # それ以外（購入成功処理）
    else:
        # --- お釣りを計算する ---
        change = current_money - price
        
        # 合計金額の状態を更新（お釣りの額にする）
        st.session_state.total_money = change
        
        # 購入結果の通知を表示
        st.toast(f"💰 お釣りは{change}円です。")
        st.toast(f"✅ {selected} を購入しました！", icon="🥤")
        time.sleep(1)
        st.rerun()

# ==========================================
# メイン処理
# ==========================================

# --- サイドバーUI ---
display_sidebar()

# --- メイン画面UI ---
# 自販機のタイトル
st.title("🥤 Streamlit 自販機")

### 商品一覧を表示
display_drink_menu(DRINK_MENU)

### 商品が選択される
selected = st.selectbox(
    "購入する商品を選んでください", 
    options=["-- 選択してください --"] + list(DRINK_MENU.keys())
)

### 購入ボタンで決定する
if st.button("購入する"):
    process_drinks_buy(selected, DRINK_MENU)