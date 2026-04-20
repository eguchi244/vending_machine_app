from src.cash_manager import CashManager

def test_calc_change_success():
    """正常系：お釣りが正しく計算され、在庫が足りる場合"""
    # 各金種をセットしてテスト
    cash_manager = CashManager({
        10000:10, 5000:10, 1000:10, 500:10, 100:10, 50:10, 10:10
    })
    
    # 金銭投入
    cash_manager.deposit(1000)
    
    # お釣り計算
    change = cash_manager.calc_change(880)
    print(f"880円のお釣り内訳: {change}")
    # 期待値: {...500: 1, 100: 3, 50: 1, 10: 3}

    # 各金種の在庫枚数の計算
    cash_manager.update_inventory(change)
    print(f"金種の在庫枚数: {cash_manager.inventory}")
    # 期待値: {...1000:11, 500: 9, 100: 7, 50: 9, 10: 7}

    # 在庫金額の合計の計算
    print(cash_manager.total_inventory_value)
    # 期待値: 166,720円

def test_calc_change_stock():
    """異常系：金額的には払えるが、特定の硬貨在庫が足りない場合"""
    # 100円玉以降が0枚の状態
    cash_manager = CashManager({
        10000:10, 5000:10, 1000:10, 500:0, 100:0, 50:0, 10:0
    })
    
    # 200円のお釣り（100円玉以降が必要だが在庫なし）
    change = cash_manager.calc_change(200)
    
    # 在庫不足なら空の辞書を返す仕様の検証
    assert change == {}
    # 期待値: assertの期待通りのため何も表示されない

# メイン処理呼び出し
if __name__ == "__main__":
    test_calc_change_success()
    test_calc_change_stock()

