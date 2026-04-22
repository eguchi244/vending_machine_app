"""
実行コマンド
python -m pytest test/test_data_handler.py

pytestのコマンドはwiondowsPCにガードされる
"""

import os
import json
import pytest
import csv
from src.data_handler import add_transaction_log

def test_add_transaction_log_creates_file_and_header(tmp_path, monkeypatch):
    """
    ファイルが存在しない状態で実行し、ヘッダーと1行目が正しく作成されるか確認
    """
    # テスト用の一時ディレクトリにファイルを作成するように設定
    test_log = tmp_path / "test_vending_log.csv"
    monkeypatch.setattr("src.data_handler.LOG_FILE", str(test_log))

    # テストデータ
    add_transaction_log(
        type="deposit",
        amount=100,
        item="-",
        balance_before=0,
        balance_after=100
    )

    # 検証: ファイルが存在するか
    assert test_log.exists()

    # 検証: 内容の確認
    with open(test_log, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["type"] == "deposit"
        assert rows[0]["amount"] == "100"
        # 項目が足りない場合のデフォルト値チェック
        assert rows[0]["detail_str"] == "{}"
        assert rows[0]["inventory_str"] == "{}"

def test_add_transaction_log_append_mode(tmp_path, monkeypatch):
    """
    2回連続で呼び出した際、2行目が正しく追記され、ヘッダーが重複しないか確認
    """
    test_log = tmp_path / "test_append_log.csv"
    monkeypatch.setattr("src.data_handler.LOG_FILE", str(test_log))

    # 1行目: 投入
    add_transaction_log("deposit", 1000)
    # 2行目: 購入
    add_transaction_log("purchase", -150, item="Cola")

    with open(test_log, mode="r", encoding="utf-8-sig") as f:
        lines = f.readlines()
        # ヘッダー(1) + データ(2) で計3行であること
        assert len(lines) == 3
        
        # 2行目の内容をDictReaderで再検証
        f.seek(0)
        reader = csv.DictReader(f)
        rows = list(reader)
        assert rows[1]["type"] == "purchase"
        assert rows[1]["item"] == "Cola"

def test_add_transaction_log_json_serialization(tmp_path, monkeypatch):
    """
    辞書データが正しくJSON文字列として保存・復元できるか確認
    """
    test_log = tmp_path / "test_json_log.csv"
    monkeypatch.setattr("src.data_handler.LOG_FILE", str(test_log))

    change = {10: 5, 50: 1}
    inventory = {10: 100, 50: 50, 100: 20}

    add_transaction_log(
        "refund", -100, 
        change_detail=change, 
        inventory_after=inventory
    )

    with open(test_log, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        row = next(reader)
        
        # JSONから復元して中身を比較
        res_change = json.loads(row["detail_str"])
        res_inv = json.loads(row["inventory_str"])
        
        # JSON化によりキーが文字列に変換されることを考慮
        assert res_change["10"] == 5
        assert res_inv["100"] == 20