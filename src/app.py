"""
自販機アプリ
このアプリはStreamlitを使用した自販機アプリのフロントエンドとロジックを制御します。
"""

import streamlit as st
import time
from cash_manager import CashManager

# ==========================================
# 定数（Constants, Config）
# ==========================================
DRINK_MENU = {
    'Water': 100, 'Tea': 120, 'Coffee': 130, 'Cider': 140,
    'Cola': 150, 'Orange': 160, 'Cocoa': 180, 'Monster': 200
}
BILL_TYPES = [1, 5, 10, 50, 100, 500, 1000, 5000, 10000]

# ==========================================
# 状態管理の初期化（session_state）
# ==========================================
# 金庫の金種枚数
if 'cash_inventory' not in st.session_state:
    st.session_state.cash_inventory = {
        10: 10, 50: 10, 100: 10, 500: 10, 1000: 10, 5000: 10, 10000: 10
    }

# 現在の各金種の投入枚数
if 'current_bills_deposit' not in st.session_state:
    st.session_state.current_bills_deposit = {
        10: 0, 50: 0, 100: 0, 500: 0, 1000: 0, 5000: 0, 10000: 0
    }

# 合計金額
if 'total_money' not in st.session_state:
    st.session_state.total_money = 0

# CashManagerのインスタンス化
def get_cash_mgr():
    """
    常に最新の金庫データを持ったCashManagerを返す
    session_stateにインスタンスは持たせないようにする
    """
    return CashManager(
        st.session_state.cash_inventory,
        st.session_state.current_bills_deposit,
    )

# ==========================================
# メソッド定義
# ==========================================

# 
# ロジック関数（UIに依存しない計算）
# ==========================================
def process_purchase(name: str, current_money: int):
    """
    商品購入処理メソッド
    購入判定とお釣り計算のみを行う

    Args:
        name (int): 商品名
        current_money (int): 投入残金

    Returns:
        失敗：(bool), current_money(int): False, 投入残金
        成功：(bool), change_amount(int): True, 投入残金
    """
    # 商品の価格を取得
    price = DRINK_MENU[name]
    # 購入判定
    if current_money < price:
        return False, current_money
    
    change_amount = current_money - price 
    return True, change_amount

# 
# 表示用関数（UIを描写する）
# ==========================================
def display_drink_menu(row_size: int = 4) -> str | None:
    """
    商品一覧メソッド（多段表示）
    商品を「row_sizeの列数で一行」のチャンクとして
    チャンク毎の段に分けた多段の形で一覧表示する

    Args:
        row_size (int): チャンク（一つの段）に表示する商品のデフォルト数

    Returns:
        clicked_item(str | None):, ボタン押下：商品名 | ボタン押下なし：None
    """
    st.write('### 商品ラインナップ')

    # 商品選択を初期化
    clicked_item = None

    # 多段表示のためのスライスが使えるように「辞書->リスト」に変換
    items = list(DRINK_MENU.items())

    # 商品一覧を表示
    for i in range(0, len(items), row_size):
        cols = st.columns(row_size)
        # row_sizeで指定の列数でチャンクを作成
        chunk = items[i : i + row_size]
        
        # チャンク毎の段に分けて商品データを表示
        for j, (name, price) in enumerate(chunk):
            with cols[j]:
                st.markdown(f"### {name}\n{price}円")

                # 選択されたボタンの商品名を取得
                if st.button(f"購入", key=f"btn_{name}"):
                    clicked_item = name
    
    return clicked_item

# ==========================================
# メイン処理
# ==========================================

# 
# サイドバーUIエリア
# ==========================================
with st.sidebar:
    # --- メッセージエリア ---
    with st.container(border=True):
        st.write('📢 メッセージパネル')
        side_msg = st.empty() # サイドバー用の表示領域を配置
        side_msg.info('いらっしゃいませ')
        money_display = st.empty() # 金額表示用の表示領域を配置

    # --- コイン投入エリア ---
    with st.container(border=True):
        st.header('💰 コイン投入口')
        selected_money = st.selectbox('投入する金額を選択', BILL_TYPES)
        input_clicked = st.button('投入')
        return_clicked = st.button('返却')
        st.write("サポートセンター")
        st.write("TEL：XXX-XXXX-XXXX")

    # --- コイン返却エリア ---
    with st.container(border=True):
        st.header('💰 コイン返却口')
        return_money_msg = st.empty() # お釣り返却用の表示領域を配置

# 
# メイン画面UIエリア
# ==========================================
main_view = st.container(border=True)

# 描画順序を Title -> Menu -> Exit に固定する
title_area = main_view.container()
menu_area = main_view.container()
exit_area = main_view.container()

# --- 自販機のタイトルエリア ---
with title_area:
    with st.container(border=True):
        st.title('🥤 Streamlit 自販機')

# --- 商品一覧エリア ---
with menu_area:
    with st.container(border=True):
        # 選択商品を取得
        buy_clicked = display_drink_menu()

# --- 商品取出口エリア ---
with exit_area:
    with st.container(border=True):
        st.write('📥 商品取出口')
        footer_msg = st.empty() # 購入結果用の表示領域だけ配置

# ==========================================
# イベントハンドラー（ロジックとUI操作の結合）
# ==========================================

# --- 金銭投入処理 ---
if input_clicked:
    try:
        cash_mgr = get_cash_mgr()
        cash_mgr.deposit(selected_money)
        st.session_state.total_money += selected_money
        st.rerun()
    except ValueError as e:
        side_msg.error(f"警告:{e}")

        with return_money_msg.container():
            st.write(f"返却内容: {{ {selected_money}: 1 }}")

        time.sleep(3)
        return_money_msg.empty()

# --- 金銭返却処理 ---
if return_clicked:
    if st.session_state.total_money > 0:
        # お釣り金額を確定
        current_money = st.session_state.total_money
        cash_mgr = get_cash_mgr()
        change_detail = cash_mgr.calc_change(current_money)

        # お釣り計算判定
        if change_detail:
            cash_mgr.update_inventory(change_detail)

            # TODO ここに後で履歴記録(add_transaction_log)を追加する

            # 投入制限枚数をリセット
            cash_mgr.reset_bills_deposit()

            with return_money_msg.container():
                st.info(f'💰 お釣りは{current_money}円です。')
                # 0枚以外の金種内訳を表示
                st.write(f"金種内訳:{ {k: v for k, v in change_detail.items() if v > 0 } }")

            # 合計金額の初期化
            st.session_state.total_money = 0
            time.sleep(5)
            return_money_msg.empty()
            st.rerun()
        else:
            side_msg.error('申し訳ありません。お釣り（金庫）が足りず返却できません。サポートセンターまでご連絡ください。')

# --- 商品購入処理 ---
if buy_clicked:
    success, change_amount= process_purchase(buy_clicked, st.session_state.total_money)
    
    # 商品購入成功時の処理
    if success:
        # お釣り金額を確定
        cash_mgr = get_cash_mgr()
        change_detail = cash_mgr.calc_change(change_amount)

        if change_detail or change_amount == 0:
            # 金庫を確定（減算）させる
            cash_mgr.update_inventory(change_detail)

            # TODO ここに後で履歴記録(add_transaction_log)を追加する

            # 投入制限枚数をリセット
            cash_mgr.reset_bills_deposit()

            # 投入金額を更新
            st.session_state.total_money = change_amount
            side_msg.info("ありがとうございました。")
            side_msg.info(f"💰 残金は{change_amount}円です。")
            footer_msg.success(f'✅ {buy_clicked} を購入しました！', icon='🥤')
            
            # メッセージの初期化
            time.sleep(5)
            footer_msg.empty()
            side_msg.empty()
            side_msg.info('いらっしゃいませ')
            st.rerun()
        else:
            # 計算はできるが、金庫の硬貨が足りない場合
            side_msg.error('申し訳ありません。お釣り切れのため購入できません。')
    else:
        # それ以外の処理（金額不足）
        side_msg.error('金額が不足しています。')

# 金額表示の更新（最後に実行して最新状態を反映）
money_display.write(f'現在の投入金額: **{st.session_state.total_money}円**')