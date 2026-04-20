"""
実行コマンド
pytest
または
python -m pytest test/test_cash_manager.py
"""
from src.cash_manager import CashManager
from streamlit.testing.v1 import AppTest

def test_calc_change_success():
    """正常系：お釣りが正しく計算され、在庫が足りる場合"""
    # 1. 初期在庫の設定
    cash_manager = CashManager({
        10000:10, 5000:10, 1000:10, 500:10, 100:10, 50:10, 10:10
    })
    
    # 2. 金銭投入（1000円札が1枚増えるはず）
    cash_manager.deposit(1000)
    
    # 3. お釣り計算の検証
    change = cash_manager.calc_change(880)
    # 期待値: 500円x1, 100円x3, 50円x1, 10円x3
    assert change[500] == 1
    assert change[100] == 3
    assert change[50] == 1
    assert change[10] == 3

    # 4. 在庫更新後の枚数検証
    cash_manager.update_inventory(change)
    # 1000円は投入で+1、他は計算通り減っているか
    assert cash_manager.inventory[1000] == 11
    assert cash_manager.inventory[500] == 9
    assert cash_manager.inventory[100] == 7
    assert cash_manager.inventory[50] == 9
    assert cash_manager.inventory[10] == 7

    # 5. 合計金額の検証
    # 166,720円（初期 166,600 + 投入 1000 - お釣り 880）
    assert cash_manager.total_inventory_value == 166720

def test_calc_change_stock():
    """異常系：特定の硬貨在庫が足りず、お釣りが払えない場合"""
    # 500円玉以下が0枚の状態
    cash_manager = CashManager({
        10000:10, 5000:10, 1000:10, 500:0, 100:0, 50:0, 10:0
    })
    
    # 200円のお釣り（100円玉等が必要だが在庫なし）
    change = cash_manager.calc_change(200)
    
    # 空の辞書が返ってくることを検証
    assert change == {}
