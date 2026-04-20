import pandas as pd
from datetime import datetime
import streamlit as st

def add_transaction_log(log_type: str, amount: int, item_name: str = "-", change_detail: dict = None):
    """
    取引履歴を st.session_state.history に追加する
    """
    if "history" not in st.session_state:
        st.session_state.history = []

    new_log = {
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": log_type,      # 'deposit', 'purchase', 'refund'
        "item": item_name,
        "amount": amount,
        "change_detail": str(change_detail) if change_detail else "-"
    }
    st.session_state.history.append(new_log)

def get_history_df():
    """
    履歴リストを Pandas DataFrame に変換して返す
    """
    if "history" not in st.session_state or not st.session_state.history:
        return pd.DataFrame()
    return pd.DataFrame(st.session_state.history)