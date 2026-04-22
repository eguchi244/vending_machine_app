"""
自販機アプリ
このアプリはStreamlitを使用した自販機アプリのフロントエンドとロジックを制御します。
"""

import streamlit as st
import time
from cash_manager import CashManager
from data_handler import add_transaction_log

# ==========================================
# 定数（Constants, Config）
# ==========================================
DRINK_MENU = {
    "Water": 100, "Tea": 120, "Coffee": 130, "Cider": 140,
    "Cola": 150, "Orange": 160, "Cocoa": 180, "Monster": 200
}
BILL_TYPES = [10000, 5000, 1000, 500, 100, 50, 10, 5, 1]
MAX_ITEM_STOCK = 5
MAX_BILL_COUNT = 100

# ==========================================
# 状態管理の初期化（session_state）
# ==========================================
# 金庫の在庫枚数
if "cash_inventory" not in st.session_state:
    st.session_state.cash_inventory = {
        10000: 10, 5000: 10, 1000: 10, 500: 10, 100: 10, 50: 10, 10: 10
    }

# 現在の各金種の投入枚数
if "current_bills_deposit" not in st.session_state:
    st.session_state.current_bills_deposit = {
        10000: 0, 5000: 0, 1000: 0, 500: 0, 100: 0, 50: 0, 10: 0
    }

# 合計金額
if "total_money" not in st.session_state:
    st.session_state.total_money = 0

# 商品在庫
if "drink_inventory" not in st.session_state:
    st.session_state.drink_inventory = {
        "Water": 5, "Tea": 5, "Coffee": 5, "Cider": 5,
        "Cola": 5, "Orange": 5, "Cocoa": 5, "Monster": 5
    }

# CashManagerのインスタンス化
def get_cash_mgr():
    """
    常に最新の在庫データを持ったCashManagerを返す
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

def handle_deposit() -> None:
    try:
        #各パラメータを取得
        cash_mgr = get_cash_mgr()
        before_cash = cash_mgr.total_inventory_value

        # 投入金額を金庫に加算
        cash_mgr.deposit(selected_money)

        # 合計金額に投入金額を加算
        st.session_state.total_money += selected_money

        # 処理後の金庫金額を取得
        after_cash = cash_mgr.total_inventory_value

        # ログ記録メソッドを呼び出し
        add_transaction_log(
            log_type="deposit", # 投入処理
            amount=selected_money, # 投入金額（選択貨幣）
            balance_before=before_cash, # 処理前の金庫総額
            balance_after=after_cash, # 処理後の金庫総額
            inventory_after=st.session_state.cash_inventory # 処理後の金庫各金種の枚数
        )

        st.rerun()

    except ValueError as e:
        # 警告メッセージ
        side_msg.error(f"警告:{e}")

        # 返却金額を表示
        with return_money_msg.container():
            st.write(f"返却内容: {{ {selected_money}: 1 }}")

        # メッセージを初期化
        clear_message()

def handle_refund() -> None:
    """
    返却処理（イベントハンドラー）
    """

    # 投入金額のマイナス判定
    if st.session_state.total_money < 0:
        return

    # 各パラメータを取得
    current_money = st.session_state.total_money
    cash_mgr = get_cash_mgr()
    before_cash  = cash_mgr.total_inventory_value
    change_detail = cash_mgr.calc_change(current_money)

    # お釣り計算判定
    if change_detail is None:
        # ログ記録メソッドを呼び出し
        add_transaction_log(
            log_type="refund_failed", # 返金処理
            amount=0, # 現在の合計金額
            change_detail={}, # お釣り内訳
            balance_before=before_cash, # 処理前の金庫総額
            balance_after=before_cash, # 失敗のため処理前の金庫総額を設定
            inventory_after=st.session_state.cash_inventory # 処理後の金庫各金種の枚数
        )

        side_msg.error("お釣りが足りず返却できません。サポートセンターまでご連絡ください。")
        # エラーを出し続けるためclear_message()は使用しない
        time.sleep(5)
        st.rerun()

    # --- 正常系処理 ---
    # 返却処理
    # 金庫残高を更新
    cash_mgr.update_inventory(change_detail)

    # 処理後の金庫残高を取得
    after_cash  = cash_mgr.total_inventory_value

    # ログ記録メソッドを呼び出し
    add_transaction_log(
        log_type="refund", # 返金処理
        amount=-current_money, # 現在の合計金額
        change_detail=change_detail, # お釣り内訳
        balance_before=before_cash, # 処理前の金庫総額
        balance_after=after_cash, # 処理後の金庫総額
        inventory_after=st.session_state.cash_inventory # 処理後の金庫各金種の枚数
    )

    # 投入制限枚数をリセット
    cash_mgr.reset_bills_deposit()

    # 返却メッセージを表示
    with return_money_msg.container():
        st.info(f"💰 お釣りは{current_money}円です。")
        st.write(f"金種内訳:{ {k: v for k, v in change_detail.items() if v > 0 } }")

    # 合計金額の初期化
    st.session_state.total_money = 0
    clear_message()

def handle_purchase(buy_clicked: str) -> None:
    """
    商品購入処理（イベントハンドラー）

    Args:
        buy_clicked (str): 購入された商品名
    """

    # 商品在庫判定
    if st.session_state.drink_inventory[buy_clicked] <= 0:
        side_msg.error(f"申し訳ありません。{buy_clicked} は売り切れです。")
        clear_message()
        return

    # 金額不足判定
    if st.session_state.total_money < DRINK_MENU[buy_clicked]:
        side_msg.error("金額が不足しています。")
        clear_message()
        return

    # お釣り返却の事前判定
    price = DRINK_MENU[buy_clicked]
    potential_change = st.session_state.total_money - price

    cash_mgr = get_cash_mgr()

    if potential_change > 0 and not cash_mgr.calc_change(potential_change):
        side_msg.error("お釣りが不足しているため、この商品は購入できません。")
        clear_message()
        return

    # --- 正常系処理 ---
    # 購入処理 
    success, change_amount = process_purchase(
        buy_clicked,
        st.session_state.total_money
    )

    # 商品購入成功時の処理
    if success:
        # 現在の金庫残高を取得(金庫は変化しない:balance_before = balance_after)
        cash_mgr = get_cash_mgr()
        current_cash = cash_mgr.total_inventory_value

        # 商品在庫を減算
        st.session_state.drink_inventory[buy_clicked] -= 1

        # ログ記録メソッドを呼び出し
        add_transaction_log(
            log_type="purchase", # 購入処理
            amount=-DRINK_MENU[buy_clicked], # 商品金額
            item=buy_clicked, # 選択商品
            change_detail={}, # 購入時はお釣りを払い出さない
            balance_before=current_cash, # 処理前の金庫総額
            balance_after=current_cash, # 処理後の金庫総額
            inventory_after=st.session_state.cash_inventory # 処理後の金庫各金種の枚数(お釣りが確定するまで金種は増減させない)
        )

        # 購入結果を表示
        st.session_state.total_money = change_amount
        side_msg.info("ありがとうございました。")
        side_msg.info(f"💰 残金は{change_amount}円です。")
        footer_msg.success(f"✅ {buy_clicked} を購入しました！", icon="🥤")

        # メッセージの初期化
        clear_message()
        side_msg.info("いらっしゃいませ")
        st.rerun()

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
    st.write("### 商品ラインナップ")

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

                # 在庫表示（追加）
                stock = st.session_state.drink_inventory[name]
                st.caption(f"在庫: {stock}")

                # 在庫0ならボタン無効化
                disabled = stock <= 0

                # 選択されたボタンの商品名を取得
                if st.button(f"購入", key=f"btn_{name}", disabled=disabled):
                    clicked_item = name
    
    return clicked_item

def clear_message() -> None:
    """メッセージ消去"""
    time.sleep(3)
    footer_msg.empty()
    side_msg.empty()
    return_money_msg.empty()
    stock_msg.empty()
    st.rerun()

# ==========================================
# メイン処理
# ==========================================

# --- タブの定義 ---
tab_purchase, tab_sales, tab_item, tab_cash = st.tabs([
    "自販機",
    "売上管理",
    "商品管理",
    "金庫管理"
])

# 
# サイドバーUIエリア
# ==========================================
with st.sidebar:
    # --- メッセージエリア ---
    with st.container(border=True):
        st.write("📢 メッセージパネル")
        side_msg = st.empty()
        side_msg.info("いらっしゃいませ")
        money_display = st.empty()

    # --- コイン投入エリア ---
    with st.container(border=True):
        st.header("💰 コイン投入口")
        selected_money = st.selectbox("投入する金額を選択", BILL_TYPES)
        input_clicked = st.button("投入")
        refund_clicked = st.button("返却")
        st.write("サポートセンター")
        st.write("TEL：XXX-XXXX-XXXX")

    # --- コイン返却エリア ---
    with st.container(border=True):
        st.header("💰 コイン返却口")
        return_money_msg = st.empty()

# 
# メイン画面UIエリア
# ==========================================

# --- 購入タブ ---
with tab_purchase:
    main_view = st.container(border=True)

    title_area = main_view.container()
    menu_area = main_view.container()
    exit_area = main_view.container()

    # --- タイトル ---
    with title_area:
        with st.container(border=True):
            st.title("🥤 Streamlit 自販機")

    # --- 商品一覧 ---
    with menu_area:
        with st.container(border=True):
            buy_clicked = display_drink_menu()

    # --- 商品取出口 ---
    with exit_area:
        with st.container(border=True):
            st.write("📥 商品取出口")
            footer_msg = st.empty()

# --- 売上管理タブ ---
with tab_sales:
    st.header("売上分析レポート")
    st.info("※ここは後ほど analysis.py と連携してグラフを表示します")
    # 簡易表示（テスト用）
    st.metric("現在のセッション売上", f"{st.session_state.total_money} 円")

# --- 商品管理タブ ---
with tab_item:
    # タイトル
    st.header("在庫補充・設定")
    st.subheader("在庫一覧")

    stock_msg = st.empty()

    # テーブル
    for name, price in DRINK_MENU.items():
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])

        with col1:
            st.write(f"**{name}**({price}円)")
        with col2:
            stock = st.session_state.drink_inventory[name]
            # 在庫が少ない場合に色を変えて警告
            if stock <= 0:
                st.markdown(f":red[在庫: {stock}]") 
            elif stock <= 2:
                st.markdown(f":orange[在庫: {stock}]")  
            else:
                st.markdown(f":blue[在庫: {stock}]")  
        with col3:
            if st.button("+1", key=f"add_{name}"):
                if st.session_state.drink_inventory[name] < MAX_ITEM_STOCK:
                    st.session_state.drink_inventory[name] += 1
                    st.rerun()
                else:
                    stock_msg.error("すでに最大補充数です。") 
                    clear_message()
        with col4:
            if st.button("-1", key=f"sub_{name}"):
                if st.session_state.drink_inventory[name] > 0:
                    st.session_state.drink_inventory[name] -= 1
                    st.rerun()
                else:
                    stock_msg.error("これ以上は減らすことはできません。(0個)") 
                    clear_message()
        with col5:
            if st.button(f"満タン補充", key=f"full_{name}"):
                st.session_state.drink_inventory[name] = MAX_ITEM_STOCK
                st.rerun()

    st.divider()

    # 全商品一括補充機能
    if st.button("全商品一括補充", use_container_width=True):
        for name in DRINK_MENU.keys():
            st.session_state.drink_inventory[name] = MAX_ITEM_STOCK
        stock_msg.success("全ての商品の在庫を補充しました！")
        clear_message()

# --- ④ 金庫管理タブ ---
with tab_cash:
    # タイトル
    st.header("💰 金庫残高・金種内訳")

    # 最新の金庫状況を取得
    cash_mgr = get_cash_mgr()

    # 金庫総額（カンマ区切り表示）
    st.metric(f"金庫総額", f"{cash_mgr.total_inventory_value:,}円")
    st.divider()

    # 金種別在庫
    st.subheader("金種別在庫")

    # --- コールバック関数の定義 ---
    # Streamlitの仕様上、ウィジェット表示後に値を書き換えるとエラーになるため、
    # 描画前に実行されるコールバックを使用して状態を更新します。

    def sync_inv_callback(b):
        """ナンバーインプットが手動変更された際に在庫データを同期する"""
        st.session_state.cash_inventory[b] = st.session_state[f"input_{b}"]

    def handle_full_click(b):
        """「満タン」ボタン押下時に在庫と入力欄の両方を更新する"""
        st.session_state.cash_inventory[b] = MAX_BILL_COUNT
        st.session_state[f"input_{b}"] = MAX_BILL_COUNT

    def handle_bulk_click():
        """「一括補充」ボタン押下時に全ての金種を更新する"""
        for b in BILL_TYPES[:-2]:
            st.session_state.cash_inventory[b] = MAX_BILL_COUNT
            st.session_state[f"input_{b}"] = MAX_BILL_COUNT
    # ----------------------------

    # テーブル形式で金種ごとに表示（10円〜10000円）
    for bill in BILL_TYPES[:-2]:
        col1, col2, col3, col4 = st.columns([1, 1, 2, 1])

        with col1:
            st.write(f"**{bill:,}円**")

        with col2:
            # 現在の在庫数を取得
            count = st.session_state.cash_inventory[bill]
            
            # 在庫数に応じた色の警告表示
            if count <= 3:
                st.markdown(f":red[{count} 枚]")
            elif count <= 5:
                st.markdown(f":orange[{count} 枚]")
            else:
                st.markdown(f":blue[{count} 枚]")    

        with col3:
            # 【重要】keyで状態を保持し、変更時はコールバックで在庫へ反映
            # valueには在庫データを指定し、ボタン側からの変更も即座に反映されるようにします
            st.number_input(
                "枚数設定",
                min_value=0,
                max_value=MAX_BILL_COUNT,
                value=st.session_state.cash_inventory[bill],
                key=f"input_{bill}",
                on_change=sync_inv_callback,
                args=(bill,),
                label_visibility="collapsed"
            )

        with col4:
            # 個別補充ボタン：on_clickを使用してウィジェット生成前に値を書き換える
            st.button("満タン", key=f"full_{bill}", on_click=handle_full_click, args=(bill,))

    st.divider()

    # 釣り銭準備金（金庫）の一括補充ボタン
    # こちらもon_clickで処理を行うことでAPIエラーを回避します
    if st.button("📦 釣り銭準備金を一括補充", use_container_width=True, on_click=handle_bulk_click):
        st.success(f"全ての金種を {MAX_BILL_COUNT} 枚に補充しました。")

# ==========================================
# イベントハンドラー
# ==========================================

# --- 金銭投入処理 ---
if input_clicked:
    handle_deposit()

# --- 金銭返却処理 ---
if refund_clicked:
    handle_refund()

# --- 商品購入処理 ---
if buy_clicked:
    handle_purchase(buy_clicked)

# --- 金額金額表示の更新（最後に実行して最新状態を反映） ---
money_display.write(f"現在の投入金額: **{st.session_state.total_money}円**")